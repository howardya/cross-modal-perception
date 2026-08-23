"""Loading stimuli and their author-assigned relevance masks.

The relevance masks are the independent half of the L1 check: they encode each
persona's mandate applied to each clause by hand, so the acceptance test in
cmp.targets compares model output against an external judgment rather than
against a restatement of itself.
"""

import pytest

from cmp.personas import FINANCE_PERSONAS
from cmp.stimuli import available_stimuli, load_stimulus


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


def test_every_persona_has_a_relevance_mask():
    loaded = load_stimulus("meridian-q4")
    for persona in FINANCE_PERSONAS:
        assert persona.id in loaded.relevance


def test_relevance_masks_cover_every_clause():
    loaded = load_stimulus("meridian-q4")
    n = len(loaded.stimulus.texts)
    for persona_id, mask in loaded.relevance.items():
        assert len(mask) == n, f"{persona_id} mask is the wrong length"


def test_no_persona_finds_everything_relevant():
    """A mandate that admits everything is not a mandate."""
    loaded = load_stimulus("meridian-q4")
    for persona_id, mask in loaded.relevance.items():
        assert not all(mask), f"{persona_id} marks every clause relevant"


def test_no_persona_finds_nothing_relevant():
    loaded = load_stimulus("meridian-q4")
    for persona_id, mask in loaded.relevance.items():
        assert any(mask), f"{persona_id} marks no clause relevant"


def test_irrelevant_clauses_outnumber_relevant_ones_for_the_experts():
    """The asymmetry constraint only carries information under this shape.

    See docs/calibration.md section 2 — with a balanced split, enhancement and
    suppression are algebraically the same statement.
    """
    loaded = load_stimulus("meridian-q4")
    for persona in FINANCE_PERSONAS:
        if not persona.expert:
            continue
        mask = loaded.relevance[persona.id]
        assert sum(mask) < len(mask) / 2, f"{persona.id} finds too much relevant"


def test_credit_and_equity_disagree_about_what_matters():
    """If the two mandates selected the same clauses there would be no demo."""
    loaded = load_stimulus("meridian-q4")
    credit = loaded.relevance["credit-analyst"]
    equity = loaded.relevance["equity-pm"]
    disagreements = sum(1 for c, e in zip(credit, equity) if c != e)
    assert disagreements >= 8


def test_the_held_out_note_is_a_different_shape_from_the_hero():
    """Transfer is only a real test if the second stimulus is not a rehearsal."""
    hero = load_stimulus("meridian-q4").stimulus
    held = load_stimulus("aldercroft-h1").stimulus
    assert len(hero.texts) != len(held.texts)


def test_stimuli_record_that_they_are_constructed():
    for name in ("meridian-q4", "aldercroft-h1"):
        assert load_stimulus(name).note
