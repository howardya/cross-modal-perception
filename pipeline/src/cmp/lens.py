"""One live reading, by one reader, of a document nobody scored in advance.

The study's path scores each persona five times in independent contexts and
reports the agreement between those samples. This path cannot: a viewer is
waiting, and five samples across seven readers is thirty-five calls. So the lens
takes **one sample**, and every artefact it produces says so — `samples: 1`,
`reliability_measured: false`. `docs/calibration.md` §8 is the long version.

What the lens does *not* do is change the study's instrument to suit itself. The
prompt is `build_scoring_prompt` verbatim with a paragraph appended, and
`LENS_SCHEMA` is a deep copy of `SCORING_SCHEMA` with one optional field added.
Tests pin both, because a schema shared by the record and the instrument would
let the instrument silently redefine the record.

The added field is `note`: a handful of words in the reader's own voice, on the
few clauses it stops hardest on. Notes are the annotation layer of the render.
They are capped at four because a note on every clause is a summary, and a
summary is the thing the project exists to get underneath.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from cmp.anthropic_client import (
    DEFAULT_MODEL,
    SCORING_SCHEMA,
    build_scoring_prompt,
    parse_scores,
)
from cmp.field import PerceptualField, Stimulus, field_from_scores
from cmp.ingest import Ingested
from cmp.personas import Persona
from cmp.scoring import RawScores

__all__ = [
    "LENS_SCHEMA",
    "MAX_NOTES",
    "AnthropicLensClient",
    "LensClient",
    "LensField",
    "attend",
    "build_lens_prompt",
    "parse_lens",
    "stimulus_of",
]

#: Beyond this the annotations stop being what caught the eye and become a
#: running commentary, which is a summary by another name.
MAX_NOTES = 4

NOTE_WORDS = 12


def _lens_schema() -> dict[str, Any]:
    """The study schema plus one optional field, by copy so it cannot alias."""
    schema = copy.deepcopy(SCORING_SCHEMA)
    schema["properties"]["units"]["items"]["properties"]["note"] = {
        "type": "string",
        "description": (
            f"Optional. At most {NOTE_WORDS} words, first person, in your own "
            "voice — what this clause made you think. Only on the few clauses "
            "you stopped hardest on."
        ),
    }
    return schema


LENS_SCHEMA: dict[str, Any] = _lens_schema()


class LensClient(Protocol):
    """Anything that can produce one raw lens payload for a persona."""

    def raw_attend(self, persona: Persona, stimulus: Stimulus) -> dict[str, Any]: ...


@dataclass(frozen=True)
class LensField:
    """One live reading: the field, plus the reader's own marginal notes."""

    field: PerceptualField
    notes: dict[int, str]
    model: str = DEFAULT_MODEL

    def to_dict(self) -> dict[str, Any]:
        blob = self.field.to_dict()
        blob["notes"] = {str(i): text for i, text in sorted(self.notes.items())}
        # Stated on every live reading, so a page cannot show one without it.
        blob["samples"] = 1
        blob["reliability_measured"] = False
        blob["model"] = self.model
        return blob


def stimulus_of(doc: Ingested) -> Stimulus:
    """The ingested document, in the form the scoring prompt expects."""
    return Stimulus(id=doc.doc_id, title=doc.title, texts=list(doc.clauses))


def build_lens_prompt(persona: Persona, stimulus: Stimulus) -> str:
    """The study's instruction, plus a request for marginal notes."""
    return build_scoring_prompt(persona, stimulus) + f"""

One more thing, which the four numbers cannot carry.

note (optional string): on **at most {MAX_NOTES}** of the clauses — the ones you
  stopped hardest on — add at most {NOTE_WORDS} words in your own voice saying
  what stopped you. Not a summary of the clause; the reader can see the clause.
  The thought underneath it: what it tells you, what it makes you go and check,
  what it contradicts. Write it the way you would say it to a colleague, not the
  way you would write it in a memo. Leave `note` off every other clause."""


def _pick_notes(raw_notes: dict[int, str], salience: list[float]) -> dict[int, str]:
    """Keep the notes on the clauses this reader actually stopped on."""
    if len(raw_notes) <= MAX_NOTES:
        return dict(raw_notes)
    keep = sorted(raw_notes, key=lambda i: -salience[i])[:MAX_NOTES]
    return {i: raw_notes[i] for i in sorted(keep)}


def parse_lens(
    payload: dict[str, Any], n_units: int
) -> tuple[RawScores, dict[int, str]]:
    """Validate a lens response into scores and notes.

    Validation is `parse_scores` — the same range checks, the same unit-count
    check, the same refusal of a field that attended to nothing. The lens gets no
    softer contract than the study just because a viewer is watching.
    """
    scores = parse_scores(payload, n_units=n_units)

    raw_notes: dict[int, str] = {}
    for i, unit in enumerate(payload["units"]):
        note = unit.get("note")
        if isinstance(note, str) and note.strip():
            raw_notes[i] = note.strip()

    return scores, _pick_notes(raw_notes, scores.salience)


def attend(client: LensClient, persona: Persona, doc: Ingested) -> LensField:
    """Read one document as one persona, once."""
    stimulus = stimulus_of(doc)
    payload = client.raw_attend(persona, stimulus)
    scores, notes = parse_lens(payload, n_units=len(doc.clauses))

    # Most salient clause is reached first, matching how the study derives order
    # from an aggregated field. One sample needs no median to rank.
    order = [int(o) for o in np.argsort(np.argsort([-s for s in scores.salience]))]

    field = field_from_scores(
        persona_id=persona.id,
        salience=scores.salience,
        valence=scores.valence,
        chunks=scores.chunks,
        arousal=scores.arousal,
        order=order,
    )
    return LensField(field=field, notes=notes)


class AnthropicLensClient:
    """One call per persona-document pair. No retries, no aggregation."""

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

    def raw_attend(self, persona: Persona, stimulus: Stimulus) -> dict[str, Any]:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            thinking={"type": "adaptive"},
            output_config={
                "effort": self._effort,
                "format": {"type": "json_schema", "schema": LENS_SCHEMA},
            },
            messages=[
                {"role": "user", "content": build_lens_prompt(persona, stimulus)}
            ],
        )
        text = next(b.text for b in response.content if b.type == "text")
        return json.loads(text)
