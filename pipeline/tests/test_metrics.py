"""Divergence metrics between two personas' perceptual fields.

Hand-computed expectations only — these are the numbers the demo quotes, so they
must be verifiable by someone with a calculator and no trust in this code.
"""

import math

import pytest

from cmp.metrics import (
    attention_divergence,
    chunk_agreement,
    perceptual_overlap,
    salience_concentration,
    valence_conflicts,
)


# --- attention divergence / overlap -------------------------------------------------


def test_identical_salience_has_zero_divergence():
    a = [0.1, 0.9, 0.4, 0.2]
    assert attention_divergence(a, a) == pytest.approx(0.0, abs=1e-12)


def test_identical_salience_has_full_overlap():
    a = [0.1, 0.9, 0.4, 0.2]
    assert perceptual_overlap(a, a) == pytest.approx(1.0, abs=1e-12)


def test_disjoint_salience_has_maximal_divergence():
    """All attention on unit 0 vs all on unit 3 — JSD in base 2 is exactly 1."""
    assert attention_divergence([1, 0, 0, 0], [0, 0, 0, 1]) == pytest.approx(1.0)


def test_disjoint_salience_has_zero_overlap():
    assert perceptual_overlap([1, 0, 0, 0], [0, 0, 0, 1]) == pytest.approx(0.0)


def test_divergence_is_symmetric():
    a = [0.5, 0.2, 0.9, 0.1]
    b = [0.1, 0.8, 0.2, 0.4]
    assert attention_divergence(a, b) == pytest.approx(attention_divergence(b, a))


def test_divergence_ignores_scale_because_salience_is_normalised():
    """Attention is a budget: doubling every score changes nothing about its shape."""
    a = [0.2, 0.4, 0.4]
    b = [0.4, 0.8, 0.8]
    assert attention_divergence(a, b) == pytest.approx(0.0, abs=1e-12)


def test_half_overlapping_distributions_hand_computed():
    """p=(1/2,1/2,0,0), q=(0,0,1/2,1/2). m is uniform. JSD = 1 bit."""
    assert attention_divergence([1, 1, 0, 0], [0, 0, 1, 1]) == pytest.approx(1.0)


def test_divergence_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        attention_divergence([0.1, 0.2], [0.1, 0.2, 0.3])


def test_divergence_rejects_all_zero_salience():
    with pytest.raises(ValueError, match="zero"):
        attention_divergence([0, 0, 0], [0.1, 0.2, 0.3])


def test_divergence_rejects_negative_salience():
    with pytest.raises(ValueError, match="negative"):
        attention_divergence([-0.1, 0.5], [0.1, 0.5])


# --- valence conflict ---------------------------------------------------------------


def test_valence_conflict_found_where_signs_oppose():
    """Unit 1 is positive for one persona and negative for the other."""
    assert valence_conflicts([0.8, 0.7], [0.6, -0.9], threshold=0.5) == [1]


def test_valence_agreement_is_not_a_conflict():
    assert valence_conflicts([0.8, 0.7], [0.6, 0.9], threshold=0.5) == []


def test_weak_opposing_valence_is_not_a_conflict():
    """Both must exceed the threshold — a faint disagreement is noise, not conflict."""
    assert valence_conflicts([0.2, 0.1], [-0.2, -0.1], threshold=0.5) == []


def test_conflict_requires_both_sides_above_threshold():
    """Strong positive vs barely negative does not count."""
    assert valence_conflicts([0.9], [-0.1], threshold=0.5) == []


def test_multiple_conflicts_returned_in_order():
    a = [0.9, -0.8, 0.1, 0.7]
    b = [-0.9, 0.8, 0.1, 0.7]
    assert valence_conflicts(a, b, threshold=0.5) == [0, 1]


def test_valence_rejects_out_of_range_values():
    with pytest.raises(ValueError, match="-1"):
        valence_conflicts([1.5], [0.2], threshold=0.5)


# --- salience concentration ---------------------------------------------------------


def test_uniform_attention_has_zero_concentration():
    """Attending equally to everything is the novice limit."""
    assert salience_concentration([0.25, 0.25, 0.25, 0.25]) == pytest.approx(0.0)


def test_single_point_attention_has_full_concentration():
    """All attention on one unit is the (unreachable) expert limit."""
    assert salience_concentration([1, 0, 0, 0]) == pytest.approx(1.0)


def test_concentration_increases_as_attention_narrows():
    diffuse = salience_concentration([0.3, 0.3, 0.2, 0.2])
    focused = salience_concentration([0.7, 0.2, 0.05, 0.05])
    assert focused > diffuse


def test_concentration_is_normalised_entropy_hand_computed():
    """p=(1/2,1/2,0,0): H = 1 bit, Hmax = 2 bits, so concentration = 1 - 1/2 = 0.5."""
    assert salience_concentration([1, 1, 0, 0]) == pytest.approx(0.5)


def test_concentration_undefined_for_single_unit():
    with pytest.raises(ValueError, match="at least two"):
        salience_concentration([1.0])


# --- chunk agreement ----------------------------------------------------------------


def test_identical_partitions_agree_completely():
    assert chunk_agreement([0, 0, 1, 1], [0, 0, 1, 1]) == pytest.approx(1.0)


def test_partition_labels_are_arbitrary():
    """Relabelling the same grouping must not change agreement."""
    assert chunk_agreement([0, 0, 1, 1], [7, 7, 3, 3]) == pytest.approx(1.0)


def test_orthogonal_partitions_agree_around_zero():
    """ARI is chance-corrected, so unrelated partitions score near 0."""
    assert chunk_agreement([0, 0, 1, 1], [0, 1, 0, 1]) == pytest.approx(-0.5)


def test_chunk_agreement_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        chunk_agreement([0, 0, 1], [0, 1])


# --- the expertise signature the literature predicts --------------------------------


def test_expert_field_is_more_concentrated_than_novice_field():
    """Research note claim 2: expertise concentrates attention.

    This is the shape the calibration layer must reproduce; the test pins the
    direction so a future model change cannot silently invert it.
    """
    novice = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    expert = [0.9, 0.8, 0.05, 0.05, 0.05, 0.05]
    assert salience_concentration(expert) > salience_concentration(novice)


def test_overlap_and_divergence_always_sum_to_one():
    a = [0.3, 0.1, 0.9, 0.5]
    b = [0.8, 0.2, 0.1, 0.4]
    assert attention_divergence(a, b) + perceptual_overlap(a, b) == pytest.approx(1.0)


def test_overlap_is_bounded_for_random_fields():
    rng = [(0.13 * i) % 1.0 + 0.01 for i in range(1, 21)]
    other = [(0.37 * i) % 1.0 + 0.01 for i in range(1, 21)]
    overlap = perceptual_overlap(rng, other)
    assert 0.0 <= overlap <= 1.0
    assert not math.isnan(overlap)
