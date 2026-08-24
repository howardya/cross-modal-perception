"""Loading stimuli and their author-assigned relevance masks.

The relevance masks are the independent half of the L1 check: they encode each
persona's mandate applied to each clause by hand, so the acceptance test in
cmp.targets compares model output against an external judgment rather than
against a restatement of itself.
"""

import pytest

from cmp.personas import FINANCE_PERSONAS
from cmp.stimuli import available_stimuli, load_stimulus

#: Every stimulus in the study. The mask-shape rules below are properties of
#: any stimulus, not of the hero note -- they were written when only one
#: existed, so a later document that quietly broke them could not be caught.
STIMULI = ("meridian-q4", "aldercroft-h1", "whirlpool-q2")


def test_the_hero_stimulus_loads():
    loaded = load_stimulus("meridian-q4")
    assert loaded.stimulus.id == "meridian-q4"


def test_the_held_out_stimulus_loads():
    assert load_stimulus("aldercroft-h1").stimulus.id == "aldercroft-h1"


def test_both_stimuli_are_discoverable():
    assert {"meridian-q4", "aldercroft-h1"} <= set(available_stimuli())


def test_an_unknown_stimulus_is_reported_clearly():
    with pytest.raises(KeyError, match="nonexistent"):
        load_stimulus("nonexistent")


def test_the_hero_note_is_long_enough_to_be_worth_reading():
    assert len(load_stimulus("meridian-q4").stimulus.texts) >= 20


@pytest.mark.parametrize("sid", STIMULI)
def test_every_persona_has_a_relevance_mask(sid):
    loaded = load_stimulus(sid)
    for persona in FINANCE_PERSONAS:
        assert persona.id in loaded.relevance


@pytest.mark.parametrize("sid", STIMULI)
def test_relevance_masks_cover_every_clause(sid):
    loaded = load_stimulus(sid)
    n = len(loaded.stimulus.texts)
    for persona_id, mask in loaded.relevance.items():
        assert len(mask) == n, f"{persona_id} mask is the wrong length"


@pytest.mark.parametrize("sid", STIMULI)
def test_no_persona_finds_everything_relevant(sid):
    """A mandate that admits everything is not a mandate."""
    loaded = load_stimulus(sid)
    for persona_id, mask in loaded.relevance.items():
        assert not all(mask), f"{persona_id} marks every clause relevant"


@pytest.mark.parametrize("sid", STIMULI)
def test_no_persona_finds_nothing_relevant(sid):
    loaded = load_stimulus(sid)
    for persona_id, mask in loaded.relevance.items():
        assert any(mask), f"{persona_id} marks no clause relevant"


@pytest.mark.parametrize("sid", STIMULI)
def test_irrelevant_clauses_outnumber_relevant_ones_for_the_experts(sid):
    """The asymmetry constraint only carries information under this shape.

    See docs/calibration.md section 2 — with a balanced split, enhancement and
    suppression are algebraically the same statement.
    """
    loaded = load_stimulus(sid)
    for persona in FINANCE_PERSONAS:
        if not persona.expert:
            continue
        mask = loaded.relevance[persona.id]
        assert sum(mask) < len(mask) / 2, f"{persona.id} finds too much relevant"


@pytest.mark.parametrize("sid", STIMULI)
def test_credit_and_equity_disagree_about_what_matters(sid):
    """If the two mandates selected the same clauses there would be no demo."""
    loaded = load_stimulus(sid)
    credit = loaded.relevance["credit-analyst"]
    equity = loaded.relevance["equity-pm"]
    disagreements = sum(1 for c, e in zip(credit, equity) if c != e)
    assert disagreements >= len(credit) / 4, sid


def test_the_held_out_note_is_a_different_shape_from_the_hero():
    """Transfer is only a real test if the second stimulus is not a rehearsal."""
    hero = load_stimulus("meridian-q4").stimulus
    held = load_stimulus("aldercroft-h1").stimulus
    assert len(hero.texts) != len(held.texts)


def test_every_stimulus_records_its_provenance():
    for name in STIMULI:
        assert load_stimulus(name).note


def test_the_study_contains_a_document_nobody_here_wrote():
    """The construction bias measured in docs/calibration.md 7.5 can only be
    checked against a text that was not written for these readers."""
    assert [n for n in STIMULI if load_stimulus(n).role == "real"]
