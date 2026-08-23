"""L1 acceptance tests: the literature as executable constraints.

`docs/research-note.md` §8 turns published effect sizes into targets the model
output must satisfy. These tests pin those targets so a change to the scoring
layer cannot silently produce a "perceptual field" contradicting the evidence it
claims to rest on.

A note on fixtures. Salience is normalised to a fixed budget (note claim 9), so
with an equal split of relevant and irrelevant units, enhancement and suppression
sum to 2 — each is then just a restatement of the other and the asymmetry
constraint is vacuous. It only bites when irrelevant units outnumber relevant
ones, which is also the realistic shape of a document. Fixtures below therefore
use 2 relevant units out of 10.
"""

import pytest

from cmp.targets import (
    SUPPRESSION_ASYMMETRY,
    ExpertiseSignature,
    check_expertise_signature,
    expertise_signature,
)

# 2 relevant units in 10 — a realistic document shape.
MASK = [True, True] + [False] * 8
UNIFORM = [1.0] * 10

# Suppresses the irrelevant hard: 0.46 each on the two relevant units, 0.01 elsewhere.
EXPERT_LIKE = [46, 46, 1, 1, 1, 1, 1, 1, 1, 1]

# Enhances the relevant but leaves the irrelevant nearly intact.
ENHANCES_ONLY = [3, 3, 1, 1, 1, 1, 1, 1, 1, 1]


def test_asymmetry_constant_matches_the_research_note():
    """d_redundant / d_relevant, from r = -0.43 and r = 0.27 (note §2.1)."""
    assert SUPPRESSION_ASYMMETRY == pytest.approx(1.70, abs=0.02)


# --- measuring the signature --------------------------------------------------------


def test_expert_enhances_relevant_units():
    sig = expertise_signature(EXPERT_LIKE, UNIFORM, relevant=MASK)
    assert sig.enhancement > 1.0


def test_expert_suppresses_irrelevant_units():
    sig = expertise_signature(EXPERT_LIKE, UNIFORM, relevant=MASK)
    assert sig.suppression < 1.0


def test_suppression_dominates_in_an_expert_like_field():
    sig = expertise_signature(EXPERT_LIKE, UNIFORM, relevant=MASK)
    assert sig.asymmetry > 1.0


def test_enhancement_dominates_when_the_irrelevant_is_left_alone():
    """The failure mode: sharper sight without learned blindness."""
    sig = expertise_signature(ENHANCES_ONLY, UNIFORM, relevant=MASK)
    assert sig.asymmetry < 1.0


def test_a_flat_expert_field_shows_no_signature():
    sig = expertise_signature(UNIFORM, UNIFORM, relevant=MASK)
    assert sig.enhancement == pytest.approx(1.0)
    assert sig.suppression == pytest.approx(1.0)


def test_signature_requires_at_least_one_relevant_unit():
    with pytest.raises(ValueError, match="relevant"):
        expertise_signature([1, 1], [1, 1], relevant=[False, False])


def test_signature_requires_at_least_one_irrelevant_unit():
    with pytest.raises(ValueError, match="irrelevant"):
        expertise_signature([1, 1], [1, 1], relevant=[True, True])


def test_signature_rejects_mismatched_mask_length():
    with pytest.raises(ValueError, match="same length"):
        expertise_signature([1, 1, 1], [1, 1, 1], relevant=[True, False])


# --- the acceptance check -----------------------------------------------------------


def test_expert_like_field_is_accepted():
    result = check_expertise_signature(EXPERT_LIKE, UNIFORM, MASK)
    assert result.passed, result.reasons


def test_a_passing_check_reports_no_reasons():
    assert check_expertise_signature(EXPERT_LIKE, UNIFORM, MASK).reasons == []


def test_field_that_enhances_without_suppressing_is_rejected():
    result = check_expertise_signature(ENHANCES_ONLY, UNIFORM, MASK)
    assert not result.passed
    assert any("suppress" in r.lower() for r in result.reasons)


def test_field_less_concentrated_than_novice_is_rejected():
    result = check_expertise_signature(UNIFORM, EXPERT_LIKE, MASK)
    assert not result.passed
    assert any("concentrat" in r.lower() for r in result.reasons)


def test_field_ignoring_relevant_units_is_rejected():
    """Attending less to what matters than a novice does is disqualifying."""
    inattentive = [1, 1, 9, 9, 9, 9, 9, 9, 9, 9]
    result = check_expertise_signature(inattentive, UNIFORM, MASK)
    assert not result.passed
    assert any("relevant" in r.lower() for r in result.reasons)


def test_rejection_reasons_are_human_readable():
    result = check_expertise_signature(UNIFORM, EXPERT_LIKE, MASK)
    assert result.reasons
    for reason in result.reasons:
        assert len(reason) > 20
        assert reason[0].isupper()


def test_signature_is_reported_alongside_the_verdict():
    """A failing check must show its working, not merely say no."""
    result = check_expertise_signature(ENHANCES_ONLY, UNIFORM, MASK)
    assert isinstance(result.signature, ExpertiseSignature)
    assert result.signature.enhancement > 1.0


def test_check_reports_distance_from_the_literature_ratio():
    """The 1.70 target is a reported diagnostic, not a pass/fail gate.

    Two of the three numbers behind it are unverified (note §2.1), so gating on
    it would claim more precision than the evidence supports.
    """
    result = check_expertise_signature(EXPERT_LIKE, UNIFORM, MASK)
    assert result.passed
    assert result.signature.asymmetry != pytest.approx(SUPPRESSION_ASYMMETRY, abs=0.01)
