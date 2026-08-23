"""Top-k attention overlap — the headline statistic.

Jensen-Shannon divergence is the right *continuous* measure of how two attention
distributions differ, but it is a poor headline. Over thirty clauses, two readers
with genuinely different priorities still score 85-94% overlap, because almost
every clause receives some attention and JSD only approaches 1 for near-disjoint
support. Quoting "they overlap on 94%" would tell the audience these people
broadly agree, which is the opposite of what the field shows.

Top-k overlap asks the question a heat-map comparison actually answers: of the k
clauses each reader spends most of their attention on, how many are the same?
It discriminates sharply and needs no explanation.
"""

import pytest

from cmp.metrics import top_attention, top_k_overlap


def test_identical_attention_shares_every_top_clause():
    a = [0.9, 0.8, 0.1, 0.2, 0.3]
    assert top_k_overlap(a, a, k=2) == pytest.approx(1.0)


def test_disjoint_priorities_share_nothing():
    a = [0.9, 0.8, 0.1, 0.1, 0.1]
    b = [0.1, 0.1, 0.9, 0.8, 0.1]
    assert top_k_overlap(a, b, k=2) == pytest.approx(0.0)


def test_partial_agreement_is_a_proportion_of_k():
    a = [0.9, 0.8, 0.1, 0.1]
    b = [0.9, 0.1, 0.8, 0.1]
    assert top_k_overlap(a, b, k=2) == pytest.approx(0.5)


def test_top_attention_returns_indices_most_attended_first():
    assert top_attention([0.2, 0.9, 0.5], k=3) == [1, 2, 0]


def test_ties_are_broken_by_index_so_results_are_deterministic():
    assert top_attention([0.5, 0.5, 0.5], k=2) == [0, 1]


def test_k_larger_than_the_vector_is_rejected():
    with pytest.raises(ValueError, match="k"):
        top_attention([0.1, 0.2], k=5)


def test_k_must_be_positive():
    with pytest.raises(ValueError, match="k"):
        top_attention([0.1, 0.2], k=0)


def test_overlap_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="same length"):
        top_k_overlap([0.1, 0.2], [0.1, 0.2, 0.3], k=1)


def test_top_k_discriminates_where_divergence_does_not():
    """The whole reason this metric exists.

    Two readers attending to opposite halves of a long document still score high
    on 1 - JSD because every clause carries some weight. Top-k separates them.
    """
    from cmp.metrics import perceptual_overlap

    n = 30
    a = [0.9 if i < 8 else 0.3 for i in range(n)]
    b = [0.9 if i >= 22 else 0.3 for i in range(n)]

    assert perceptual_overlap(a, b) > 0.80
    assert top_k_overlap(a, b, k=8) == pytest.approx(0.0)


def test_shared_clauses_can_be_listed_for_the_visualisation():
    from cmp.metrics import shared_top_attention

    a = [0.9, 0.8, 0.1, 0.1]
    b = [0.9, 0.1, 0.8, 0.1]
    assert shared_top_attention(a, b, k=2) == [0]
