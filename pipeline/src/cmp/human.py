"""Placing a human reader among the modelled personas.

Two uses, one mechanism.

In the demo: the viewer highlights the note as themselves before seeing any
persona, then learns whose field theirs most resembles. Their own baseline is
what makes the comparison personal rather than an abstraction about other people.

In the pipeline: real practitioners mark up the hero note and their markup is
compared with the persona that claims to represent them. A mismatch there is a
result worth publishing, not a parameter to tune away.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field as dataclass_field

from cmp.field import PerceptualField
from cmp.metrics import perceptual_overlap

__all__ = [
    "HumanMarkup",
    "PersonaMatch",
    "closest_persona",
    "rank_personas",
    "salience_from_highlights",
]

#: Attention retained by a clause the reader did not mark. They still read the
#: words; they just did not dwell. Zero would claim they never saw them.
BASELINE_SALIENCE = 0.15


@dataclass(frozen=True)
class HumanMarkup:
    """What one person marked as mattering, on one stimulus."""

    person_id: str
    highlights: set[int]
    role: str | None = None
    notes: str = ""


@dataclass(frozen=True)
class PersonaMatch:
    persona_id: str
    overlap: float


def salience_from_highlights(
    highlights: set[int],
    n_units: int,
    baseline: float = BASELINE_SALIENCE,
) -> list[float]:
    """Turn a set of highlighted clause indices into a salience vector.

    Highlighting everything and highlighting nothing both produce uniform
    attention, which is correct: neither tells us what mattered to the reader.
    """
    if n_units < 2:
        raise ValueError("comparison needs at least two units")
    for index in highlights:
        if not 0 <= index < n_units:
            raise ValueError(f"highlight index {index} is out of range for {n_units} units")

    return [1.0 if i in highlights else baseline for i in range(n_units)]


def rank_personas(
    markup: HumanMarkup,
    fields: Sequence[PerceptualField],
    n_units: int,
) -> list[PersonaMatch]:
    """Rank personas by how closely their attention resembles this reader's."""
    if not fields:
        raise ValueError("ranking needs at least one persona to compare against")

    for f in fields:
        if len(f.units) != n_units:
            raise ValueError(
                f"persona {f.persona_id!r} has {len(f.units)} units but the "
                f"comparison expects {n_units} units"
            )

    human = salience_from_highlights(markup.highlights, n_units)
    matches = [
        PersonaMatch(persona_id=f.persona_id, overlap=perceptual_overlap(human, f.salience()))
        for f in fields
    ]
    return sorted(matches, key=lambda m: m.overlap, reverse=True)


def closest_persona(
    markup: HumanMarkup,
    fields: Sequence[PerceptualField],
    n_units: int,
) -> str:
    """The persona this reader most resembles."""
    return rank_personas(markup, fields, n_units)[0].persona_id
