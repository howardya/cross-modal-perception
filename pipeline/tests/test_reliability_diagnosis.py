"""Distinguishing "diffuse" from "inconsistent" in a low reliability score.

Krippendorff's alpha divides observed disagreement by the disagreement expected
from the pooled spread of values. When a persona attends near-uniformly, that
denominator collapses and alpha becomes unstable — it can read near zero even
when the runs agree closely in absolute terms.

That matters here because a *novice reader attending uniformly is the correct
behaviour*, not a defect. Reading a low alpha as unreliability would fail a good
run for the wrong reason. Reading it as fine would hide a genuinely erratic
persona. Alpha alone cannot tell those apart; alpha plus concentration can.
"""

import pytest

from cmp.reliability import diagnose_reliability


def test_high_alpha_is_simply_reliable():
    d = diagnose_reliability(alpha=0.92, concentration=0.30)
    assert d.reliable
    assert not d.diffuse


def test_low_alpha_with_uniform_attention_is_diagnosed_as_diffuse():
    """The novice case: agreement is unmeasurable, not absent."""
    d = diagnose_reliability(alpha=0.05, concentration=0.004)
    assert d.diffuse
    assert not d.erratic


def test_low_alpha_with_focused_attention_is_genuinely_erratic():
    """This one is a real problem: the persona picks different clauses each run."""
    d = diagnose_reliability(alpha=0.05, concentration=0.40)
    assert d.erratic
    assert not d.diffuse


def test_an_erratic_persona_is_not_reliable():
    assert not diagnose_reliability(alpha=0.05, concentration=0.40).reliable


def test_a_diffuse_persona_is_not_marked_unreliable():
    """Its attention carries little information, but it is not contradicting itself."""
    assert diagnose_reliability(alpha=0.05, concentration=0.004).reliable


def test_the_diagnosis_explains_itself():
    d = diagnose_reliability(alpha=0.05, concentration=0.004)
    assert "uniform" in d.summary.lower() or "diffuse" in d.summary.lower()
    assert d.summary.rstrip().endswith(".")


def test_the_erratic_diagnosis_says_so_plainly():
    d = diagnose_reliability(alpha=0.05, concentration=0.40)
    assert "erratic" in d.summary.lower() or "different" in d.summary.lower()


def test_concentration_must_be_a_proportion():
    with pytest.raises(ValueError, match="concentration"):
        diagnose_reliability(alpha=0.5, concentration=1.4)
