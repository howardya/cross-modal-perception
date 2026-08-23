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
from typing import Any

import numpy as np

from cmp.field import Stimulus
from cmp.personas import Persona
from cmp.scoring import RawScores

__all__ = [
    "SCORING_SCHEMA",
    "AnthropicScoringClient",
    "build_scoring_prompt",
    "parse_scores",
]

DEFAULT_MODEL = "claude-opus-5"

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


def build_scoring_prompt(persona: Persona, stimulus: Stimulus) -> str:
    """The instruction handed to the model for one scoring sample."""
    numbered = "\n".join(f"[{i}] {text}" for i, text in enumerate(stimulus.texts))

    return f"""{persona.brief()}

Below is a document, split into numbered clauses. Score every clause exactly as
this role would perceive it on a first read — not as a neutral analyst would, and
not as a summary of what the clause says.

Document: {stimulus.title}

{numbered}

For each clause give four numbers.

salience (0-1): how strongly the clause pulls your attention.
  Your attention is a finite budget. You cannot mark everything important — if
  most clauses score high, you have not done the task. Real readers of your role
  fixate on a small number of clauses and skim the rest, including clauses that
  are objectively interesting but irrelevant to your mandate. Scoring something
  low means you would genuinely skim past it, not that it does not matter to
  anyone.

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
