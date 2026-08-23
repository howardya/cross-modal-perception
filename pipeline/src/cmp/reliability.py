"""How much a persona agrees with itself across repeated samples.

An LLM persona scored once is an anecdote. The project's claim to have
*quantified* anything rests on scoring each persona k times and publishing how
well those runs agree. That number belongs in the demo, whatever it turns out
to be — a low alpha is a finding, not a bug to hide.

Krippendorff's alpha, interval metric:

    alpha = 1 - Do / De

where Do is the observed disagreement within units across runs and De is the
disagreement expected if all the values were shuffled freely. 1.0 is perfect
agreement, 0.0 is chance, and negative values mean the runs contradict each
other more than random pairing would.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

__all__ = [
    "DIFFUSE_CONCENTRATION",
    "RELIABILITY_TENTATIVE",
    "RELIABILITY_THRESHOLD",
    "ReliabilityDiagnosis",
    "ReliabilityVerdict",
    "diagnose_reliability",
    "krippendorff_alpha_interval",
    "reliability_verdict",
]

#: Below this concentration a persona is attending near-uniformly, and alpha's
#: denominator is too small for the statistic to mean much either way.
DIFFUSE_CONCENTRATION = 0.05

#: Krippendorff's own convention for drawing firm conclusions.
RELIABILITY_THRESHOLD = 0.80

#: Below this, data is not usable even tentatively.
RELIABILITY_TENTATIVE = 0.667


def krippendorff_alpha_interval(runs: Sequence[Sequence[float]]) -> float:
    """Agreement across repeated scoring runs over the same units.

    `runs` is a list of runs; each run is one score per unit, in unit order.
    Assumes complete data — every run scores every unit, which is what the
    scoring layer guarantees.
    """
    if len(runs) < 2:
        raise ValueError("reliability needs at least two runs to compare")

    widths = {len(r) for r in runs}
    if len(widths) != 1:
        raise ValueError("all runs must have the same length")

    matrix = np.asarray(runs, dtype=float)  # (m runs, n units)
    m, n = matrix.shape
    if n < 2:
        raise ValueError("reliability needs at least two units")

    # Observed disagreement: squared differences between runs, within each unit.
    # Uses the identity  sum_{i,j} (x_i - x_j)^2 == 2 * m^2 * var(x).
    pair_sums = 2.0 * (m**2) * matrix.var(axis=0, ddof=0)
    observed = pair_sums.sum() / (n * m * (m - 1))

    # Expected disagreement: the same statistic over every value pooled together.
    pooled = matrix.ravel()
    total = pooled.size
    expected = 2.0 * total * pooled.var(ddof=0) / (total - 1)

    if expected <= 0:
        raise ValueError(
            "no variation between units; agreement is undefined when every unit "
            "receives the same score"
        )

    return float(1.0 - observed / expected)


@dataclass(frozen=True)
class ReliabilityVerdict:
    alpha: float
    usable: bool
    tentative: bool
    summary: str


def reliability_verdict(alpha: float) -> ReliabilityVerdict:
    """Turn an alpha into something quotable in the demo's honesty panel."""
    usable = alpha >= RELIABILITY_THRESHOLD
    tentative = RELIABILITY_TENTATIVE <= alpha < RELIABILITY_THRESHOLD

    if usable:
        body = (
            f"Repeated runs of the same persona agree at alpha = {alpha:.2f}, above the "
            f"conventional {RELIABILITY_THRESHOLD:.2f} threshold, so these scores are "
            f"stable enough to draw conclusions from."
        )
    elif tentative:
        body = (
            f"Repeated runs agree at alpha = {alpha:.2f}. That is below the "
            f"{RELIABILITY_THRESHOLD:.2f} convention, so these scores support tentative "
            f"conclusions only."
        )
    else:
        body = (
            f"Repeated runs agree at only alpha = {alpha:.2f}. The persona does not score "
            f"this stimulus consistently, so any single reading of it should not be "
            f"trusted."
        )

    return ReliabilityVerdict(alpha=alpha, usable=usable, tentative=tentative, summary=body)


@dataclass(frozen=True)
class ReliabilityDiagnosis:
    """Alpha read alongside concentration, so a low score can be interpreted."""

    alpha: float
    concentration: float
    diffuse: bool
    erratic: bool
    summary: str

    @property
    def reliable(self) -> bool:
        """True unless the persona genuinely contradicts itself between runs.

        A diffuse persona is not marked unreliable: attending evenly is the
        correct behaviour for a novice reader, and alpha cannot measure
        agreement when there is almost no between-unit signal to agree about.
        """
        return not self.erratic


def diagnose_reliability(alpha: float, concentration: float) -> ReliabilityDiagnosis:
    """Separate "attends uniformly" from "picks different clauses each run"."""
    if not 0.0 <= concentration <= 1.0:
        raise ValueError(f"concentration must lie in [0, 1], got {concentration}")

    weak = alpha < RELIABILITY_THRESHOLD
    diffuse = weak and concentration < DIFFUSE_CONCENTRATION
    erratic = weak and not diffuse

    if not weak:
        summary = (
            f"Runs agree at alpha = {alpha:.2f}, above the "
            f"{RELIABILITY_THRESHOLD:.2f} convention."
        )
    elif diffuse:
        summary = (
            f"Alpha is {alpha:.2f}, but attention is near-uniform "
            f"(concentration {concentration:.3f}). Alpha is unstable when there is "
            f"little between-clause variation to agree about, so this reads as a "
            f"diffuse reader rather than an inconsistent one. Treat the low alpha "
            f"as uninformative here, not as a failure."
        )
    else:
        summary = (
            f"Alpha is {alpha:.2f} while attention is concentrated "
            f"(concentration {concentration:.3f}). The persona is focusing on "
            f"different clauses on different runs, which is erratic rather than "
            f"diffuse. This is a real reliability failure."
        )

    return ReliabilityDiagnosis(
        alpha=alpha,
        concentration=concentration,
        diffuse=diffuse,
        erratic=erratic,
        summary=summary,
    )
