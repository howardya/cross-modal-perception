"""Load scores produced inline by a Claude session rather than by the API loop.

Same validation, same metrics, same acceptance checks as the API path — the only
difference is where the numbers came from, and that difference is recorded in the
exported provenance block rather than left implicit.

The important limitation: scores produced in one conversation are not
independent samples, so inter-run reliability cannot be measured. Fields loaded
this way carry `reliability_measured: false`, and the calibration report says so
instead of printing an alpha that would mean nothing.
"""

from __future__ import annotations

import json
from pathlib import Path

from cmp.field import PerceptualField, StimulusFieldSet, field_from_scores
from cmp.stimuli import LoadedStimulus, load_stimulus

__all__ = ["SCORED_DIR", "load_inline_scores"]

SCORED_DIR = Path(__file__).resolve().parents[2] / "scored"


def _rank_by_salience(salience: list[float]) -> list[int]:
    """Most salient clause is reached first."""
    order = sorted(range(len(salience)), key=lambda i: -salience[i])
    rank = [0] * len(salience)
    for position, index in enumerate(order):
        rank[index] = position
    return rank


def load_inline_scores(name: str) -> tuple[LoadedStimulus, StimulusFieldSet]:
    """Read an inline-scored file and build a validated field set from it."""
    path = SCORED_DIR / f"{name}.json"
    if not path.exists():
        available = sorted(p.stem for p in SCORED_DIR.glob("*.json"))
        raise KeyError(f"unknown scored file {name!r}; available: {available}")

    raw = json.loads(path.read_text())
    loaded = load_stimulus(raw["stimulus_id"])
    n = len(loaded.stimulus.texts)

    fields: list[PerceptualField] = []
    for persona_id, scores in raw["scores"].items():
        for key in ("salience", "valence", "chunk", "arousal"):
            if len(scores[key]) != n:
                raise ValueError(
                    f"{name}: {persona_id} has {len(scores[key])} {key} values "
                    f"but the stimulus has {n} clauses"
                )
        fields.append(
            field_from_scores(
                persona_id=persona_id,
                salience=scores["salience"],
                valence=scores["valence"],
                chunks=scores["chunk"],
                arousal=scores["arousal"],
                order=_rank_by_salience(scores["salience"]),
            )
        )

    field_set = StimulusFieldSet(
        stimulus=loaded.stimulus,
        fields=fields,
        method=raw["method"],
        reliability_measured=bool(raw.get("reliability_measured", False)),
    )
    return loaded, field_set
