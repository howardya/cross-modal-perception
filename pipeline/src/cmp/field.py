"""The perceptual field and the JSON contract between pipeline and visualization.

One stimulus, several personas, one scored field per persona. The exported
document carries the stimulus text, every persona's field, the pairwise
comparisons, and a provenance block the demo's honesty panel reads directly
rather than having the caveats retyped by hand.

Attribute meanings and their rendering channels are set out in
`docs/research-note.md` §8.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from cmp.metrics import (
    DEFAULT_TOP_K,
    chunk_agreement,
    perceptual_overlap,
    salience_concentration,
    shared_top_attention,
    top_attention,
    top_k_overlap,
    valence_conflicts,
)

__all__ = ["PerceptualField", "Stimulus", "StimulusFieldSet", "Unit"]

SCHEMA_VERSION = 1

#: Read by the demo's honesty panel. Kept here so the caveat travels with the data.
PROVENANCE_SUMMARY = (
    "Persona differences are modelled from role mandates and calibrated against "
    "published effect sizes. They are not measured recordings of real experts' "
    "attention. No eye-tracking study compares these roles on the same document."
)

#: Overridden per field set. A fixture must be able to state its own method, so
#: the demo's honesty panel cannot drift away from how the data was actually made.
DEFAULT_METHOD = "unspecified"


def _check_range(value: float, low: float, high: float, name: str) -> float:
    if not low <= value <= high:
        raise ValueError(f"{name} must lie in [{low}, {high}], got {value}")
    return value


@dataclass(frozen=True)
class Unit:
    """One clause of a stimulus, as one persona perceives it."""

    salience: float
    valence: float
    chunk: int
    arousal: float
    order: int

    def __post_init__(self) -> None:
        _check_range(self.salience, 0.0, 1.0, "salience")
        _check_range(self.valence, -1.0, 1.0, "valence")
        _check_range(self.arousal, 0.0, 1.0, "arousal")

    def to_dict(self) -> dict[str, Any]:
        return {
            "salience": self.salience,
            "valence": self.valence,
            "chunk": self.chunk,
            "arousal": self.arousal,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Unit:
        return cls(
            salience=float(raw["salience"]),
            valence=float(raw["valence"]),
            chunk=int(raw["chunk"]),
            arousal=float(raw["arousal"]),
            order=int(raw["order"]),
        )


@dataclass(frozen=True)
class Stimulus:
    """The thing being read, split into the units personas score."""

    id: str
    title: str
    texts: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "texts": list(self.texts)}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Stimulus:
        return cls(id=raw["id"], title=raw["title"], texts=list(raw["texts"]))


@dataclass(frozen=True)
class PerceptualField:
    """How one persona perceives one stimulus."""

    persona_id: str
    units: list[Unit]

    def salience(self) -> list[float]:
        return [u.salience for u in self.units]

    def valence(self) -> list[float]:
        return [u.valence for u in self.units]

    def chunks(self) -> list[int]:
        return [u.chunk for u in self.units]

    def concentration(self) -> float:
        return salience_concentration(self.salience())

    def to_dict(self) -> dict[str, Any]:
        k = min(DEFAULT_TOP_K, len(self.units))
        return {
            "persona_id": self.persona_id,
            "concentration": self.concentration(),
            "top_attention": top_attention(self.salience(), k),
            "units": [u.to_dict() for u in self.units],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PerceptualField:
        return cls(
            persona_id=raw["persona_id"],
            units=[Unit.from_dict(u) for u in raw["units"]],
        )


@dataclass(frozen=True)
class StimulusFieldSet:
    """One stimulus as seen by several personas, plus their pairwise comparisons."""

    stimulus: Stimulus
    fields: list[PerceptualField]
    valence_threshold: float = 0.5
    method: str = DEFAULT_METHOD
    reliability_measured: bool = False

    def __post_init__(self) -> None:
        if len(self.fields) < 2:
            raise ValueError("a field set needs at least two personas to compare")

        ids = [f.persona_id for f in self.fields]
        if len(set(ids)) != len(ids):
            raise ValueError(f"persona ids must be unique, got {ids}")

        expected = len(self.stimulus.texts)
        for f in self.fields:
            if len(f.units) != expected:
                raise ValueError(
                    f"persona {f.persona_id!r} scored {len(f.units)} units but the "
                    f"stimulus has {expected}; every unit must be scored"
                )

    def comparisons(self) -> list[dict[str, Any]]:
        out = []
        for a, b in combinations(self.fields, 2):
            k = min(DEFAULT_TOP_K, len(self.stimulus.texts))
            out.append(
                {
                    "personas": [a.persona_id, b.persona_id],
                    # The headline. See cmp.metrics.top_k_overlap for why this,
                    # and not 1 - JSD, is what the demo quotes.
                    "top_k": k,
                    "top_k_overlap": top_k_overlap(a.salience(), b.salience(), k),
                    "shared_top": shared_top_attention(a.salience(), b.salience(), k),
                    # Retained as the continuous measure; poor as a headline.
                    "overlap": perceptual_overlap(a.salience(), b.salience()),
                    "valence_conflicts": valence_conflicts(
                        a.valence(), b.valence(), threshold=self.valence_threshold
                    ),
                    "chunk_agreement": chunk_agreement(a.chunks(), b.chunks()),
                }
            )
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "stimulus": self.stimulus.to_dict(),
            "fields": [f.to_dict() for f in self.fields],
            "comparisons": self.comparisons(),
            "provenance": {
                "measured": False,
                "summary": PROVENANCE_SUMMARY,
                "method": self.method,
                "reliability_measured": self.reliability_measured,
            },
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> StimulusFieldSet:
        provenance = raw.get("provenance", {})
        return cls(
            stimulus=Stimulus.from_dict(raw["stimulus"]),
            fields=[PerceptualField.from_dict(f) for f in raw["fields"]],
            method=provenance.get("method", DEFAULT_METHOD),
            reliability_measured=provenance.get("reliability_measured", False),
        )


def field_from_scores(
    persona_id: str,
    salience: Sequence[float],
    valence: Sequence[float],
    chunks: Sequence[int],
    arousal: Sequence[float],
    order: Sequence[int],
) -> PerceptualField:
    """Assemble a field from parallel score vectors."""
    lengths = {len(salience), len(valence), len(chunks), len(arousal), len(order)}
    if len(lengths) != 1:
        raise ValueError("all score vectors must have the same length")
    return PerceptualField(
        persona_id=persona_id,
        units=[
            Unit(salience=s, valence=v, chunk=c, arousal=a, order=o)
            for s, v, c, a, o in zip(salience, valence, chunks, arousal, order)
        ],
    )
