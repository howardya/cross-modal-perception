"""The inline-scored hero fixture, checked against the same constraints as any other.

Scores produced by a Claude session get no easier a ride than scores produced by
the API loop. If the hero fixture fails the literature checks, these tests fail.
"""

import pytest

from cmp.inline import load_inline_scores
from cmp.personas import FINANCE_PERSONAS
from cmp.targets import check_expertise_signature

LOADED, FIELDS = load_inline_scores("meridian-q4-inline")
BY_ID = {f.persona_id: f for f in FIELDS.fields}
BASELINE = BY_ID["retail-investor"]


def test_every_persona_scored_the_hero_note():
    assert set(BY_ID) == {p.id for p in FINANCE_PERSONAS}


def test_scores_cover_every_clause():
    n = len(LOADED.stimulus.texts)
    for field in FIELDS.fields:
        assert len(field.units) == n


@pytest.mark.parametrize(
    "persona_id", [p.id for p in FINANCE_PERSONAS if p.expert]
)
def test_expert_fields_pass_the_literature_checks(persona_id):
    check = check_expertise_signature(
        expert=BY_ID[persona_id].salience(),
        novice=BASELINE.salience(),
        relevant=LOADED.relevance[persona_id],
    )
    assert check.passed, f"{persona_id}: {check.reasons}"


@pytest.mark.parametrize(
    "persona_id", [p.id for p in FINANCE_PERSONAS if p.expert]
)
def test_experts_are_more_concentrated_than_the_lay_reader(persona_id):
    assert BY_ID[persona_id].concentration() > BASELINE.concentration()


def test_experts_chunk_more_coarsely_than_the_lay_reader():
    """The chunking literature, made visible: novices read clause by clause."""
    lay_chunks = len(set(BASELINE.chunks()))
    for persona in FINANCE_PERSONAS:
        if persona.expert:
            assert len(set(BY_ID[persona.id].chunks())) < lay_chunks


def test_the_credit_analyst_and_equity_pm_genuinely_conflict():
    """The demo's central claim needs real inversions, not near-misses."""
    comparison = next(
        c for c in FIELDS.comparisons()
        if set(c["personas"]) == {"credit-analyst", "equity-pm"}
    )
    assert len(comparison["valence_conflicts"]) >= 3


def test_the_covenant_amendment_is_a_conflict():
    """Clause 12 is the clause the demo is built around."""
    comparison = next(
        c for c in FIELDS.comparisons()
        if set(c["personas"]) == {"credit-analyst", "equity-pm"}
    )
    assert 12 in comparison["valence_conflicts"]


def test_the_buyback_is_a_conflict():
    comparison = next(
        c for c in FIELDS.comparisons()
        if set(c["personas"]) == {"credit-analyst", "equity-pm"}
    )
    assert 14 in comparison["valence_conflicts"]


def test_no_two_personas_perceive_the_note_identically():
    for comparison in FIELDS.comparisons():
        assert comparison["overlap"] < 0.95, comparison["personas"]


def test_the_fixture_declares_it_was_scored_inline():
    provenance = FIELDS.to_dict()["provenance"]
    assert "Claude Opus 5" in provenance["method"]
    assert provenance["reliability_measured"] is False


def test_the_fixture_does_not_claim_to_be_measured():
    assert FIELDS.to_dict()["provenance"]["measured"] is False
