"""Score a stimulus as a persona, using Claude with a constrained output schema.

Kept separate from `cmp.scoring` so the aggregation logic has no dependency on
any model provider. The SDK import is deferred to construction time, so the rest
of the pipeline works without the optional `scoring` extra installed.

The prompt deliberately encodes the two constraints the research note derived
from Sirois et al. (2018): attention is a finite budget (claim 9), and salience
dilutes as more is highlighted (claim 10). Without those, personas mark
everything important and the fields stop being distinguishable.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from cmp.field import Stimulus
from cmp.personas import Persona
from cmp.scoring import RawScores

__all__ = [
    "SCORING_SCHEMA",
    "AnthropicScoringClient",
    "SalienceQuota",
    "build_scoring_prompt",
    "parse_scores",
    "salience_quota",
]

DEFAULT_MODEL = "claude-opus-5"

HIGH = 0.55
LOW = 0.25

#: Share of clauses an expert may mark strongly salient, and the share it must
#: actively ignore. Derived from the shape of the literature's task-relevant
#: areas of interest, which are always a minority of the display.
EXPERT_HIGH_SHARE, EXPERT_LOW_SHARE = 0.27, 0.40

#: A lay reader spreads attention: it may mark more things salient and is not
#: required to ignore much. Applying the expert quota here would make the novice
#: as concentrated as the expert and erase the contrast being measured.
LAY_HIGH_SHARE, LAY_LOW_SHARE = 0.50, 0.15


@dataclass(frozen=True)
class SalienceQuota:
    """An arithmetic constraint the model can check its own output against."""

    max_high: int
    min_low: int
    high: float = HIGH
    low: float = LOW


def salience_quota(persona: Persona, n_units: int) -> SalienceQuota:
    """How concentrated this persona's attention is permitted to be.

    Prose alone did not hold. Run 1 of the independent scoring told the model
    that attention was a finite budget and it marked nearly every clause
    salient anyway — the equity PM came out at concentration 0.017, flatter
    than the lay reader. A number the model can count against does hold.
    """
    if n_units < 2:
        raise ValueError(f"a quota needs at least two clauses, got {n_units}")

    high_share, low_share = (
        (EXPERT_HIGH_SHARE, EXPERT_LOW_SHARE) if persona.expert
        else (LAY_HIGH_SHARE, LAY_LOW_SHARE)
    )
    max_high = max(1, math.floor(n_units * high_share))
    min_low = math.floor(n_units * low_share)
    # Leave the two bounds room to coexist.
    min_low = min(min_low, n_units - max_high)
    return SalienceQuota(max_high=max_high, min_low=min_low)

SCORING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "units": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "salience": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "How strongly this clause pulls your attention.",
                    },
                    "valence": {
                        "type": "number",
                        "minimum": -1,
                        "maximum": 1,
                        "description": "Good news (+) or bad news (-) for your mandate.",
                    },
                    "chunk": {
                        "type": "integer",
                        "minimum": 0,
                        "description": (
                            "Group id. Clauses you read as one idea share a chunk id."
                        ),
                    },
                    "arousal": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "How much alarm or uncertainty this raises in you.",
                    },
                },
                "required": ["salience", "valence", "chunk", "arousal"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["units"],
    "additionalProperties": False,
}


def _quota_text(persona: Persona, n_units: int) -> str:
    """The salience constraint, stated as arithmetic rather than as advice."""
    q = salience_quota(persona, n_units)

    if persona.expert:
        return f"""  HARD CONSTRAINT, and the one most often got wrong: **at most {q.max_high}**
  of the {n_units} clauses may score above {q.high}, and **at least {q.min_low}**
  must score below {q.low}. Count them before you answer. If you are over the
  ceiling, you are describing what a careful generalist would find interesting
  rather than what your role would actually stop on.

  The second number matters more than the first. Expertise is mostly learned
  neglect: years of practice have taught you to ignore whole categories of
  true, interesting, well-written material because it does not bear on your
  mandate. A low score does not mean the clause is unimportant to anyone — it
  means you would skim straight past it."""

    return f"""  You have no filter, so your attention is broad and shallow rather than
  targeted. Most clauses land somewhere in the middle: you read them, none of
  them tells you much. At most {q.max_high} of the {n_units} clauses should score
  above {q.high} — reserve those for the few that genuinely grab you, usually
  the big round numbers and anything that sounds like good or bad news in plain
  language. Only about {q.min_low} should fall below {q.low}, and those are the
  ones so technical that your eye slides off them entirely.

  Do not impose an expert's discipline on this. Reading everything a bit is the
  point."""


def build_scoring_prompt(persona: Persona, stimulus: Stimulus) -> str:
    """The instruction handed to the model for one scoring sample."""
    numbered = "\n".join(f"[{i}] {text}" for i, text in enumerate(stimulus.texts))
    quota_text = _quota_text(persona, len(stimulus.texts))

    return f"""{persona.brief()}

Below is a document, split into numbered clauses. Score every clause exactly as
this role would perceive it on a first read — not as a neutral analyst would, and
not as a summary of what the clause says.

Document: {stimulus.title}

{numbered}

For each clause give four numbers.

salience (0-1): how strongly the clause pulls your attention.
{quota_text}

valence (-1 to +1): whether this is good news or bad news *for you*, given your
  mandate. This is the score most likely to differ from another role's. The same
  clause can be genuinely positive for one mandate and negative for another
  because they hold different claims on the same company. Do not hedge toward
  zero to seem balanced.

chunk (integer): which clauses you read as a single idea. Clauses you would take
  in together share a chunk id. Reading in larger groups is a mark of fluency in
  your domain; reading clause by clause is what someone unfamiliar does.

arousal (0-1): how much alarm or uncertainty the clause raises in you,
  independent of whether it is good or bad news.

Return exactly {len(stimulus.texts)} unit objects, in document order."""


def parse_scores(payload: dict[str, Any], n_units: int) -> RawScores:
    """Validate a model response and turn it into score vectors."""
    units = payload["units"]
    if len(units) != n_units:
        raise ValueError(
            f"model returned {len(units)} scores but the stimulus has {n_units} units"
        )

    salience: list[float] = []
    valence: list[float] = []
    chunks: list[int] = []
    arousal: list[float] = []

    for i, unit in enumerate(units):
        s = float(unit["salience"])
        v = float(unit["valence"])
        a = float(unit["arousal"])
        if not 0.0 <= s <= 1.0:
            raise ValueError(f"unit {i}: salience {s} outside [0, 1]")
        if not -1.0 <= v <= 1.0:
            raise ValueError(f"unit {i}: valence {v} outside [-1, 1]")
        if not 0.0 <= a <= 1.0:
            raise ValueError(f"unit {i}: arousal {a} outside [0, 1]")
        salience.append(s)
        valence.append(v)
        arousal.append(a)
        chunks.append(int(unit["chunk"]))

    if sum(salience) <= 0:
        raise ValueError("salience is zero everywhere; the persona attended to nothing")

    order = [int(o) for o in np.argsort(np.argsort([-s for s in salience]))]

    return RawScores(
        salience=salience, valence=valence, chunks=chunks, arousal=arousal, order=order
    )


class AnthropicScoringClient:
    """Scores one persona-stimulus pair per call, via the Messages API."""

    def __init__(
        self,
        client: Any | None = None,
        model: str = DEFAULT_MODEL,
        effort: str = "high",
        max_tokens: int = 16000,
    ) -> None:
        if client is None:
            import anthropic  # deferred: optional dependency

            client = anthropic.Anthropic()
        self._client = client
        self._model = model
        self._effort = effort
        self._max_tokens = max_tokens

    def score(self, persona: Persona, stimulus: Stimulus) -> RawScores:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            thinking={"type": "adaptive"},
            output_config={
                "effort": self._effort,
                "format": {"type": "json_schema", "schema": SCORING_SCHEMA},
            },
            messages=[
                {"role": "user", "content": build_scoring_prompt(persona, stimulus)}
            ],
        )
        text = next(b.text for b in response.content if b.type == "text")
        return parse_scores(json.loads(text), n_units=len(stimulus.texts))
