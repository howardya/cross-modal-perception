"""The literature, expressed as constraints the model output must satisfy.

This is layer L1 of the calibration described in `docs/research-note.md` §8. It
answers one question: does a generated perceptual field have the *shape* that
published research says expert attention has?

The central claim being enforced is the suppression asymmetry — expertise is
learned neglect of the irrelevant more than it is sharper attention to the
relevant (note claims 1, 2 and 4).

**What is gated** is direction only, which is what the evidence supports:

1. the expert attends more than the novice to task-relevant units (r = +0.27),
2. the expert attends less than the novice to task-redundant units (r = -0.43),
3. the expert's attention is more concentrated (information reduction).

**What is reported but NOT gated** is the suppression asymmetry. Gating it was a
mis-specification, found by scoring a real 30-clause note and watching a
well-formed field fail. Two reasons it does not work:

- The published numbers are standardised mean differences (d). Re-expressing
  them as a ratio of normalised attention shares is not a faithful translation,
  and the result is sensitive to the novice baseline's own tilt in a way the
  d values are not.
- Under a fixed attention budget the totals must balance: the attention moved
  *into* relevant clauses equals the attention moved *out of* irrelevant ones.
  When irrelevant clauses outnumber relevant ones — the realistic case — each
  irrelevant clause therefore loses less share than each relevant clause gains.
  Making |log suppression| exceed |log enhancement| then requires driving
  irrelevant clauses to near zero: for the hero note, roughly a 45:1 salience
  ratio. No real reader is that extreme, so the constraint was demanding an
  artefact rather than testing a finding.

The asymmetry is still computed and displayed, because its *value* is
informative when read against the relevant/irrelevant balance. It is simply no
longer allowed to fail a run.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from cmp.metrics import salience_concentration

__all__ = [
    "SUPPRESSION_ASYMMETRY",
    "ExpertiseSignature",
    "SignatureCheck",
    "check_expertise_signature",
    "expertise_signature",
]


def _d_from_r(r: float) -> float:
    """Cohen's d from a point-biserial correlation."""
    return 2 * r / math.sqrt(1 - r * r)


# Gegenfurtner, Lehtinen & Saljo (2011), via note §2.1. Both flagged unverified.
R_RELEVANT = 0.27
R_REDUNDANT = -0.43

D_RELEVANT = _d_from_r(R_RELEVANT)  # ~ +0.56
D_REDUNDANT = _d_from_r(R_REDUNDANT)  # ~ -0.95

#: How much harder expertise suppresses the irrelevant than it enhances the
#: relevant. Reported as a diagnostic; not a pass/fail threshold.
SUPPRESSION_ASYMMETRY = abs(D_REDUNDANT) / abs(D_RELEVANT)


@dataclass(frozen=True)
class ExpertiseSignature:
    """How an expert field differs from a novice field on the same stimulus.

    Both ratios are computed on normalised salience, so they describe how
    attention was *reallocated* within a fixed budget.
    """

    enhancement: float
    """Expert attention to relevant units, as a multiple of novice attention."""

    suppression: float
    """Expert attention to irrelevant units, as a multiple of novice attention."""

    asymmetry: float
    """|log suppression| / |log enhancement|. Above 1 means suppression dominates."""

    expert_concentration: float
    novice_concentration: float


@dataclass(frozen=True)
class SignatureCheck:
    signature: ExpertiseSignature
    reasons: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.reasons


def _normalise(values: Sequence[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    total = arr.sum()
    if total <= 0:
        raise ValueError("salience sums to zero; a persona must attend to something")
    return arr / total


def expertise_signature(
    expert: Sequence[float],
    novice: Sequence[float],
    relevant: Sequence[bool],
) -> ExpertiseSignature:
    """Measure how an expert field reallocates attention relative to a novice field."""
    if not (len(expert) == len(novice) == len(relevant)):
        raise ValueError("expert, novice and relevant mask must have the same length")

    mask = np.asarray(relevant, dtype=bool)
    if not mask.any():
        raise ValueError("at least one unit must be marked relevant")
    if mask.all():
        raise ValueError("at least one unit must be irrelevant, or there is nothing to suppress")

    e = _normalise(expert)
    n = _normalise(novice)

    enhancement = float(e[mask].mean() / n[mask].mean())
    suppression = float(e[~mask].mean() / n[~mask].mean())

    log_enh = abs(math.log(enhancement)) if enhancement > 0 else math.inf
    log_sup = abs(math.log(suppression)) if suppression > 0 else math.inf
    asymmetry = math.inf if log_enh == 0 else log_sup / log_enh

    return ExpertiseSignature(
        enhancement=enhancement,
        suppression=suppression,
        asymmetry=asymmetry,
        expert_concentration=salience_concentration(expert),
        novice_concentration=salience_concentration(novice),
    )


def check_expertise_signature(
    expert: Sequence[float],
    novice: Sequence[float],
    relevant: Sequence[bool],
) -> SignatureCheck:
    """Test a field pair against the shape the literature predicts.

    Gated on direction and ordering only — see the module docstring for why the
    magnitude is reported rather than enforced.
    """
    sig = expertise_signature(expert, novice, relevant)
    reasons: list[str] = []

    if sig.enhancement <= 1.0:
        reasons.append(
            f"Expert attends no more to task-relevant units than the novice does "
            f"(enhancement {sig.enhancement:.2f}, expected above 1.0)."
        )
    if sig.suppression >= 1.0:
        reasons.append(
            f"Expert fails to suppress task-irrelevant units "
            f"(suppression {sig.suppression:.2f}, expected below 1.0)."
        )
    if sig.expert_concentration <= sig.novice_concentration:
        reasons.append(
            f"Expert attention is no more concentrated than novice attention "
            f"({sig.expert_concentration:.3f} vs {sig.novice_concentration:.3f})."
        )

    return SignatureCheck(signature=sig, reasons=reasons)
