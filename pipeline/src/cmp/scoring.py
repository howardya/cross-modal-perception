"""Sample each persona k times, aggregate, and report how well the runs agreed.

The client is injected. This module contains no knowledge of any particular
model provider, which keeps the aggregation logic testable against a fake and
keeps the API dependency optional.

Aggregation uses the **median** across runs, not the mean, so a single wild
sample cannot drag a unit's score. Chunk labels are aggregated by mode instead,
because they are labels rather than magnitudes and averaging them is meaningless.
Reading order is recomputed from the aggregated salience rather than averaged,
so it stays consistent with the field it ships beside.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from cmp.field import PerceptualField, Stimulus, field_from_scores
from cmp.personas import Persona
from cmp.reliability import ReliabilityVerdict, krippendorff_alpha_interval, reliability_verdict

__all__ = [
    "RawScores",
    "ScoringClient",
    "ScoringRun",
    "aggregate_runs",
    "score_persona",
]


@dataclass(frozen=True)
class RawScores:
    """One model sample: parallel score vectors over a stimulus's units."""

    salience: list[float]
    valence: list[float]
    chunks: list[int]
    arousal: list[float]
    order: list[int]

    def __len__(self) -> int:
        return len(self.salience)


class ScoringClient(Protocol):
    """Anything that can score a stimulus as a persona, once."""

    def score(self, persona: Persona, stimulus: Stimulus) -> RawScores: ...


@dataclass(frozen=True)
class ScoringRun:
    """The aggregated field, its reliability, and the samples behind it."""

    field: PerceptualField
    reliability: ReliabilityVerdict
    samples: list[RawScores]


def _modal_chunks(runs: Sequence[RawScores]) -> list[int]:
    columns = zip(*(r.chunks for r in runs))
    return [Counter(col).most_common(1)[0][0] for col in columns]


def aggregate_runs(persona_id: str, runs: Sequence[RawScores]) -> PerceptualField:
    """Combine k samples into one field, median per unit."""
    if len(runs) < 2:
        raise ValueError("aggregation needs at least two runs to be meaningful")

    widths = {len(r) for r in runs}
    if len(widths) != 1:
        raise ValueError("all runs must have the same length")

    salience = np.median([r.salience for r in runs], axis=0)
    valence = np.median([r.valence for r in runs], axis=0)
    arousal = np.median([r.arousal for r in runs], axis=0)

    # Reading order follows the aggregated salience: the most salient unit is
    # reached first. Averaging the sampled orders would let order drift out of
    # step with the salience it is displayed alongside.
    order = list(np.argsort(np.argsort(-salience)).astype(int))

    return field_from_scores(
        persona_id=persona_id,
        salience=[float(v) for v in salience],
        valence=[float(v) for v in valence],
        chunks=_modal_chunks(runs),
        arousal=[float(v) for v in arousal],
        order=[int(v) for v in order],
    )


def score_persona(
    client: ScoringClient,
    persona: Persona,
    stimulus: Stimulus,
    k: int = 5,
) -> ScoringRun:
    """Score one persona k times and report the agreement between those runs."""
    if k < 2:
        raise ValueError("scoring needs at least two samples; one sample is an anecdote")

    expected = len(stimulus.texts)
    samples: list[RawScores] = []
    for _ in range(k):
        raw = client.score(persona, stimulus)
        if len(raw) != expected:
            raise ValueError(
                f"persona {persona.id!r} returned {len(raw)} scores but the stimulus "
                f"has {expected} units; every unit must be scored"
            )
        samples.append(raw)

    field = aggregate_runs(persona.id, samples)
    alpha = krippendorff_alpha_interval([s.salience for s in samples])
    return ScoringRun(field=field, reliability=reliability_verdict(alpha), samples=samples)
