"""Loading stimuli and their author-assigned relevance masks.

A stimulus ships with a per-persona relevance mask: which clauses that mandate
would treat as task-relevant. The masks are assigned by hand, before any scoring
runs, which is what makes the L1 acceptance test an external check rather than a
tautology. They are a judgment, and `docs/calibration.md` says so.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from cmp.field import Stimulus

__all__ = ["LoadedStimulus", "STIMULI_DIR", "available_stimuli", "load_stimulus"]

STIMULI_DIR = Path(__file__).resolve().parents[2] / "stimuli"


@dataclass(frozen=True)
class LoadedStimulus:
    stimulus: Stimulus
    relevance: dict[str, list[bool]]
    role: str
    note: str


def available_stimuli() -> list[str]:
    return sorted(p.stem for p in STIMULI_DIR.glob("*.json"))


def load_stimulus(name: str) -> LoadedStimulus:
    path = STIMULI_DIR / f"{name}.json"
    if not path.exists():
        raise KeyError(f"unknown stimulus {name!r}; available: {available_stimuli()}")

    raw = json.loads(path.read_text())
    stimulus = Stimulus(id=raw["id"], title=raw["title"], texts=list(raw["texts"]))

    relevance = {k: [bool(v) for v in mask] for k, mask in raw["relevance"].items()}
    n = len(stimulus.texts)
    for persona_id, mask in relevance.items():
        if len(mask) != n:
            raise ValueError(
                f"{name}: relevance mask for {persona_id!r} has {len(mask)} entries "
                f"but the stimulus has {n} clauses"
            )

    return LoadedStimulus(
        stimulus=stimulus,
        relevance=relevance,
        role=raw.get("role", "unknown"),
        note=raw.get("note", ""),
    )
