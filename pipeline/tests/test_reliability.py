"""Inter-run agreement across repeated persona samples.

A single LLM sample is an anecdote. Scoring each persona k times and publishing
the agreement between runs is the one number that distinguishes a quantified
claim from an asserted one, so it is computed here and shown in the demo.

Krippendorff's alpha for interval data: 1.0 is perfect agreement, 0.0 is what
chance would produce, and negative values mean the runs disagree more than
random pairing would.
"""

import pytest

from cmp.reliability import krippendorff_alpha_interval, reliability_verdict


def test_identical_runs_have_perfect_agreement():
    runs = [[0.1, 0.5, 0.9], [0.1, 0.5, 0.9], [0.1, 0.5, 0.9]]
    assert krippendorff_alpha_interval(runs) == pytest.approx(1.0)


def test_two_identical_runs_have_perfect_agreement():
    assert krippendorff_alpha_interval([[0.2, 0.8], [0.2, 0.8]]) == pytest.approx(1.0)


def test_near_identical_runs_have_high_agreement():
    runs = [[0.10, 0.50, 0.90, 0.30], [0.12, 0.48, 0.88, 0.32]]
    assert krippendorff_alpha_interval(runs) > 0.95


def test_noisy_runs_have_lower_agreement_than_clean_runs():
    clean = [[0.1, 0.5, 0.9, 0.3], [0.12, 0.52, 0.88, 0.31]]
    noisy = [[0.1, 0.5, 0.9, 0.3], [0.7, 0.2, 0.4, 0.9]]
    assert krippendorff_alpha_interval(clean) > krippendorff_alpha_interval(noisy)


def test_runs_with_no_variation_between_units_are_undefined():
    """If every unit scores the same, there is no signal to agree about."""
    with pytest.raises(ValueError, match="variation"):
        krippendorff_alpha_interval([[0.5, 0.5, 0.5], [0.5, 0.5, 0.5]])


def test_a_single_run_cannot_be_assessed():
    with pytest.raises(ValueError, match="at least two"):
        krippendorff_alpha_interval([[0.1, 0.2, 0.3]])


def test_runs_must_be_the_same_length():
    with pytest.raises(ValueError, match="same length"):
        krippendorff_alpha_interval([[0.1, 0.2], [0.1, 0.2, 0.3]])


def test_systematically_disagreeing_runs_score_below_zero():
    """One run's ordering inverted against the other is worse than chance."""
    runs = [[0.0, 0.25, 0.75, 1.0], [1.0, 0.75, 0.25, 0.0]]
    assert krippendorff_alpha_interval(runs) < 0.0


def test_alpha_is_order_independent_across_runs():
    a = [[0.1, 0.9, 0.4], [0.2, 0.8, 0.5], [0.15, 0.85, 0.45]]
    b = [a[2], a[0], a[1]]
    assert krippendorff_alpha_interval(a) == pytest.approx(krippendorff_alpha_interval(b))


# --- reporting ----------------------------------------------------------------------


def test_high_agreement_is_reported_as_usable():
    verdict = reliability_verdict(0.85)
    assert verdict.usable
    assert "0.85" in verdict.summary


def test_low_agreement_is_reported_as_not_usable():
    verdict = reliability_verdict(0.32)
    assert not verdict.usable
    assert "0.32" in verdict.summary


def test_the_conventional_threshold_is_eight_tenths():
    """Krippendorff's own convention: 0.80 for firm conclusions."""
    assert reliability_verdict(0.80).usable
    assert not reliability_verdict(0.79).usable


def test_tentative_band_is_flagged_between_point_667_and_point_8():
    verdict = reliability_verdict(0.70)
    assert not verdict.usable
    assert verdict.tentative


def test_verdict_summary_is_quotable_in_the_demo():
    summary = reliability_verdict(0.91).summary
    assert len(summary) > 30
    assert summary[0].isupper()
    assert summary.rstrip().endswith(".")
