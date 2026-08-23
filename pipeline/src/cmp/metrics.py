"""Divergence metrics between two personas' perceptual fields.

These produce the numbers the demo quotes out loud, so every one of them is a
standard, citable statistic rather than something invented here:

    attention_divergence   Jensen-Shannon divergence (base 2, so bounded [0, 1])
    perceptual_overlap     1 - JSD, the headline "they attend to the same X%"
    valence_conflicts      units read in opposite directions by two personas
    salience_concentration 1 - normalised Shannon entropy
    chunk_agreement        adjusted Rand index between two chunk partitions

Salience is always normalised to a probability distribution before comparison.
That is not a convenience: `docs/research-note.md` claim 9 records that attention
is zero-sum within a document, so only the *shape* of a salience vector is
meaningful, never its scale.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np

__all__ = [
    "attention_divergence",
    "chunk_agreement",
    "perceptual_overlap",
    "salience_concentration",
    "valence_conflicts",
]


def _as_distribution(salience: Sequence[float], name: str) -> np.ndarray:
    arr = np.asarray(salience, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"{name} must be a one-dimensional sequence")
    if np.any(arr < 0):
        raise ValueError(f"{name} contains negative salience; salience is non-negative")
    total = arr.sum()
    if total <= 0:
        raise ValueError(f"{name} sums to zero; a persona must attend to something")
    return arr / total


def _entropy_bits(p: np.ndarray) -> float:
    """Shannon entropy in bits, treating 0 log 0 as 0."""
    nonzero = p[p > 0]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def attention_divergence(a: Sequence[float], b: Sequence[float]) -> float:
    """Jensen-Shannon divergence between two salience distributions.

    Base 2, so the result is bounded [0, 1]: 0 when two personas attend
    identically, 1 when their attention is completely disjoint.
    """
    if len(a) != len(b):
        raise ValueError("salience vectors must have the same length")
    p = _as_distribution(a, "first salience vector")
    q = _as_distribution(b, "second salience vector")
    m = (p + q) / 2.0
    jsd = _entropy_bits(m) - (_entropy_bits(p) + _entropy_bits(q)) / 2.0
    return float(np.clip(jsd, 0.0, 1.0))


def perceptual_overlap(a: Sequence[float], b: Sequence[float]) -> float:
    """Share of attention two personas hold in common. The headline number."""
    return 1.0 - attention_divergence(a, b)


def valence_conflicts(
    a: Sequence[float],
    b: Sequence[float],
    threshold: float = 0.5,
) -> list[int]:
    """Indices where two personas read the same unit in opposite directions.

    Both readings must be at least `threshold` strong. A faint disagreement is
    noise; a conflict means each persona is confident and they disagree — the
    same clause being good news to one and bad news to the other.
    """
    if len(a) != len(b):
        raise ValueError("valence vectors must have the same length")
    x = np.asarray(a, dtype=float)
    y = np.asarray(b, dtype=float)
    for arr, name in ((x, "first"), (y, "second")):
        if np.any(np.abs(arr) > 1.0):
            raise ValueError(f"{name} valence vector has values outside [-1, 1]")
    strong = (np.abs(x) >= threshold) & (np.abs(y) >= threshold)
    opposed = np.sign(x) != np.sign(y)
    return [int(i) for i in np.flatnonzero(strong & opposed)]


def salience_concentration(salience: Sequence[float]) -> float:
    """How focused a persona's attention is, on [0, 1].

    0 means attention spread perfectly evenly (the novice limit); 1 means all
    attention on a single unit. This is the primary calibration target: the
    research note records that expertise concentrates attention, and that it
    does so mainly by *suppressing* the irrelevant.
    """
    p = _as_distribution(salience, "salience vector")
    if p.size < 2:
        raise ValueError("concentration needs at least two units to be meaningful")
    return 1.0 - _entropy_bits(p) / np.log2(p.size)


def chunk_agreement(a: Sequence[int], b: Sequence[int]) -> float:
    """Adjusted Rand index between two chunk partitions.

    Chance-corrected, so unrelated partitions score near 0 and identical ones
    score 1, whatever labels each side happened to use.
    """
    if len(a) != len(b):
        raise ValueError("chunk partitions must have the same length")
    n = len(a)
    if n < 2:
        raise ValueError("chunk agreement needs at least two units")

    pairs = Counter(zip(a, b))
    rows = Counter(a)
    cols = Counter(b)

    def choose2(k: int) -> float:
        return k * (k - 1) / 2.0

    index = sum(choose2(v) for v in pairs.values())
    row_sum = sum(choose2(v) for v in rows.values())
    col_sum = sum(choose2(v) for v in cols.values())
    total = choose2(n)

    expected = row_sum * col_sum / total
    maximum = (row_sum + col_sum) / 2.0
    if maximum == expected:
        return 1.0
    return float((index - expected) / (maximum - expected))
