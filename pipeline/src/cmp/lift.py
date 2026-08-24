"""What each reader over-attends to, and what they walk past.

This replaces an earlier attempt at a role signature built from six statistical
traits — threat pull, baseline mood and so on. That version was accurate and
useless: it described the shape of a distribution rather than saying anything a
person could act on, and its one surviving trait re-derived a finding the
attention tables already made plainly.

The question a signature should answer is concrete: **what kind of sentence
makes this reader look up, and what do they walk straight past while everyone
else stops?** Both halves come from the same number.

    lift(reader, sentence) = reader's share of attention − mean share

Positive means the sentence is more theirs than anyone's. Negative means the
others stopped and they did not. Shares rather than raw salience, so a reader
who scores generously across the board does not win every sentence.

The negative tail is the more interesting one. The project's thesis is that
expertise is learned neglect, and `mirrored_pairs` is where that becomes
visible: the sentences one reader owns and another is blind to, which turn out
not to be random gaps but the mirror image of somebody else's training.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

__all__ = [
    "Marked",
    "MirroredPair",
    "attention_lift",
    "blind_spots",
    "mirrored_pairs",
    "signatures",
]


@dataclass(frozen=True)
class Marked:
    """One sentence, as it stands out for (or vanishes from) one reader."""

    index: int
    lift: float


@dataclass(frozen=True)
class MirroredPair:
    """A sentence one reader owns and another walks past."""

    index: int
    seen_by: str
    seen_lift: float
    missed_by: str
    missed_lift: float

    @property
    def gap(self) -> float:
        return self.seen_lift - self.missed_lift


def _salience(reader: Mapping) -> list[float]:
    if "salience" in reader:
        return list(reader["salience"])
    return [u["salience"] for u in reader["units"]]


def attention_lift(readers: Sequence[Mapping]) -> dict[str, list[float]]:
    """Each reader's share of attention per sentence, minus the average share."""
    if len(readers) < 2:
        raise ValueError("lift is a comparison and needs at least two readers")

    widths = {len(_salience(r)) for r in readers}
    if len(widths) != 1:
        raise ValueError("all readers must cover the same length of document")

    shares = {}
    for r in readers:
        v = np.asarray(_salience(r), dtype=float)
        total = v.sum()
        if total <= 0:
            raise ValueError(f"reader {r['persona_id']!r} attends to nothing")
        shares[r["persona_id"]] = v / total

    mean = np.mean(list(shares.values()), axis=0)
    return {pid: (s - mean).tolist() for pid, s in shares.items()}


def _ranked(readers: Sequence[Mapping], persona_id: str, k: int, *, best: bool):
    lift = attention_lift(readers)
    if persona_id not in lift:
        raise KeyError(f"no reader named {persona_id!r}")
    v = lift[persona_id]
    order = sorted(range(len(v)), key=lambda i: -v[i] if best else v[i])
    return [Marked(index=i, lift=v[i]) for i in order[:k]]


def signatures(readers: Sequence[Mapping], persona_id: str, k: int = 3) -> list[Marked]:
    """The sentences that are more this reader's than anyone else's."""
    return _ranked(readers, persona_id, k, best=True)


def blind_spots(readers: Sequence[Mapping], persona_id: str, k: int = 3) -> list[Marked]:
    """The sentences everyone else stopped at and this reader did not."""
    return _ranked(readers, persona_id, k, best=False)


def mirrored_pairs(readers: Sequence[Mapping], k: int = 5) -> list[MirroredPair]:
    """Sentences that one reader owns and another is blind to.

    The widest gaps first. A document nobody disagrees about produces none,
    which is the correct answer rather than an empty-handed one.
    """
    lift = attention_lift(readers)
    ids = list(lift)
    n = len(next(iter(lift.values())))

    out: list[MirroredPair] = []
    for i in range(n):
        col = {pid: lift[pid][i] for pid in ids}
        seen = max(col, key=lambda p: col[p])
        missed = min(col, key=lambda p: col[p])
        if col[seen] <= 0 or col[missed] >= 0:
            continue
        out.append(
            MirroredPair(
                index=i,
                seen_by=seen,
                seen_lift=col[seen],
                missed_by=missed,
                missed_lift=col[missed],
            )
        )

    out.sort(key=lambda p: p.gap, reverse=True)
    return out[:k]
