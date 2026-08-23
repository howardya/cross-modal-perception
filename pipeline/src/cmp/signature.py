"""Role signatures: the traits that might belong to a reader rather than to a page.

A per-clause perceptual field is a *fingerprint* — it says how one reader met one
document. The question this module exists to answer is whether anything in it is
*DNA*: a property of the role that survives changing the document.

That is a falsifiable question, and `trait_drift` is how it gets decided. Every
trait is computable on any stimulus of any length, so the same six numbers can be
produced for a second document and compared. A trait whose between-role spread is
large relative to how much it moves between documents is carrying role signal. A
trait that moves as much as it spreads was describing the document.

`docs/findings.md` records how each trait actually fared. Two caveats belong with
the numbers wherever they are shown:

1. **Some traits are dictated by the prompt.** Focus is imposed almost directly by
   the salience quota, and chunking is mentioned in the instructions. Recovering
   those is not a discovery, so `Trait.prompted` marks them and the honest reading
   foregrounds the traits nothing specified.
2. **Two documents is a very small basis** for calling anything stable.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

import numpy as np

from cmp.field import PerceptualField

__all__ = ["TRAITS", "Signature", "Trait", "TraitDrift", "signature", "trait_drift"]

#: A trait is judged to carry role signal when the spread between roles is at
#: least this many times the amount it drifts between documents.
STABLE_RATIO = 2.0


@dataclass(frozen=True)
class Trait:
    key: str
    label: str
    question: str
    low: str
    high: str
    prompted: bool
    """True when the scoring prompt effectively dictates this trait, so
    reproducing it is a check that the instruction was followed rather than a
    finding about the role."""


TRAITS: list[Trait] = [
    Trait(
        key="threat",
        label="Threat pull",
        question="Does bad news pull the eye, or good news?",
        low="drawn to good news",
        high="drawn to bad news",
        prompted=False,
    ),
    Trait(
        key="mood",
        label="Baseline mood",
        question="What does this reader expect to find?",
        low="expects trouble",
        high="expects reassurance",
        prompted=False,
    ),
    Trait(
        key="focus",
        label="Focus",
        question="How narrowly is attention spent?",
        low="reads everything a little",
        high="reads a few things hard",
        prompted=True,
    ),
    Trait(
        key="chunk_size",
        label="Chunking",
        question="How many sentences are read as one idea?",
        low="sentence by sentence",
        high="in groups",
        prompted=True,
    ),
    Trait(
        key="alarm",
        label="Alarm",
        question="How much unease does the document raise?",
        low="untroubled",
        high="on edge",
        prompted=True,
    ),
    Trait(
        key="position",
        label="Reading position",
        question="Where in the document does attention land?",
        low="the opening",
        high="the closing",
        prompted=False,
    ),
]


@dataclass(frozen=True)
class Signature:
    threat: float
    mood: float
    focus: float
    chunk_size: float
    alarm: float
    position: float


def signature(field: PerceptualField) -> Signature:
    """Reduce one reader's field to six document-independent traits."""
    s = np.array(field.salience(), dtype=float)
    v = np.array(field.valence(), dtype=float)
    a = np.array([u.arousal for u in field.units], dtype=float)
    chunks = field.chunks()
    n = len(s)

    # Threat pull: does salience track *negative* valence? Undefined when either
    # side is flat, and a flat vector means the question has no answer rather
    # than an answer of zero correlation — report 0.0 and move on.
    if n < 2 or s.std() == 0 or v.std() == 0:
        threat = 0.0
    else:
        threat = float(-np.corrcoef(s, v)[0, 1])

    # Where attention lands, as a fraction of the way through the document.
    if n < 2:
        position = 0.5
    else:
        weights = s / s.sum() if s.sum() > 0 else np.full(n, 1 / n)
        position = float((weights * (np.arange(n) / (n - 1))).sum())

    return Signature(
        threat=threat,
        mood=float(v.mean()),
        focus=field.concentration(),
        chunk_size=n / len(set(chunks)),
        alarm=float(a.mean()),
        position=position,
    )


@dataclass(frozen=True)
class TraitDrift:
    """How one trait behaved when the document changed underneath it."""

    spread: float
    """Range of the trait across roles, on the first document."""

    drift: float
    """Mean absolute movement per role between the two documents."""

    ratio: float
    """spread / drift. Above STABLE_RATIO the trait is carrying role signal."""

    same_ordering: bool
    """Whether the roles rank identically on both documents."""

    @property
    def stable(self) -> bool:
        return self.ratio >= STABLE_RATIO

    @property
    def verdict(self) -> str:
        if self.same_ordering and self.stable:
            return "role signal"
        if self.stable:
            return "partial"
        return "document-specific"


def trait_drift(first: Mapping[str, float], second: Mapping[str, float]) -> TraitDrift:
    """Compare one trait across two documents to see whether it belongs to the role.

    `first` and `second` map role id to that trait's value on each document.
    """
    if set(first) != set(second):
        raise ValueError("both documents must cover the same roles")
    if len(first) < 2:
        raise ValueError("comparing roles needs at least two of them")

    roles = list(first)
    values = [first[r] for r in roles]
    spread = max(values) - min(values)
    drift = float(np.mean([abs(first[r] - second[r]) for r in roles]))
    ratio = float("inf") if drift == 0 else spread / drift

    order_first = sorted(roles, key=lambda r: first[r])
    order_second = sorted(roles, key=lambda r: second[r])

    return TraitDrift(
        spread=spread,
        drift=drift,
        ratio=ratio,
        same_ordering=order_first == order_second,
    )
