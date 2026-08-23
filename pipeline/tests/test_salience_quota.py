"""The salience quota in the scoring prompt.

Run 1 of the independent subagent scoring produced excellent reliability
(alpha 0.94-0.98) and failed every expertise check, because the model marked
nearly every clause salient — the equity PM's attention came out at
concentration 0.017, essentially uniform, *less* focused than the lay reader's.

Telling the model in prose that "attention is a finite budget" was not enough.
The prompt now carries an arithmetic quota it can check itself against.

The quota is deliberately persona-dependent. Imposing the expert quota on the
lay reader would make the novice as concentrated as the expert and erase the
contrast the whole project is measuring — the literature's claim is precisely
that experts concentrate and novices do not.
"""

import math

import pytest

from cmp.anthropic_client import build_scoring_prompt, salience_quota
from cmp.field import Stimulus
from cmp.personas import persona_by_id

STIM = Stimulus(id="s", title="S", texts=[f"clause {i}." for i in range(30)])
CREDIT = persona_by_id("credit-analyst")
RETAIL = persona_by_id("retail-investor")


# --- the quota itself ---------------------------------------------------------------


def test_an_expert_may_mark_only_a_minority_strongly_salient():
    q = salience_quota(CREDIT, n_units=30)
    assert q.max_high < 30 / 2


def test_an_expert_must_actively_ignore_a_large_share():
    """Information reduction: the headline of expertise is learned neglect."""
    q = salience_quota(CREDIT, n_units=30)
    assert q.min_low >= 12


def test_the_quota_scales_with_document_length():
    short = salience_quota(CREDIT, n_units=20)
    long = salience_quota(CREDIT, n_units=60)
    assert long.max_high > short.max_high


def test_the_lay_reader_gets_a_looser_ceiling_than_the_expert():
    assert salience_quota(RETAIL, n_units=30).max_high > salience_quota(CREDIT, n_units=30).max_high


def test_the_lay_reader_is_not_required_to_ignore_much():
    """A novice reads everything at middling attention; that is the finding."""
    assert salience_quota(RETAIL, n_units=30).min_low < salience_quota(CREDIT, n_units=30).min_low


def test_the_quota_is_satisfiable():
    """max_high and min_low must leave room for each other."""
    for persona in (CREDIT, RETAIL):
        for n in (10, 20, 30, 60):
            q = salience_quota(persona, n_units=n)
            assert q.max_high + q.min_low <= n, (persona.id, n)


def test_a_very_short_document_still_permits_at_least_one_focus():
    assert salience_quota(CREDIT, n_units=4).max_high >= 1


# --- the prompt carries it ----------------------------------------------------------


def test_the_expert_prompt_states_both_numbers():
    q = salience_quota(CREDIT, n_units=30)
    prompt = build_scoring_prompt(CREDIT, STIM)
    assert str(q.max_high) in prompt
    assert str(q.min_low) in prompt


def test_the_expert_prompt_asks_the_model_to_check_itself():
    prompt = build_scoring_prompt(CREDIT, STIM).lower()
    assert "count" in prompt


def test_the_prompt_explains_why_rather_than_only_commanding():
    prompt = build_scoring_prompt(CREDIT, STIM).lower()
    assert "ignore" in prompt or "neglect" in prompt


def test_the_lay_prompt_does_not_demand_expert_focus():
    """The novice prompt must not smuggle in the expert's discipline."""
    expert_q = salience_quota(CREDIT, n_units=30)
    lay_prompt = build_scoring_prompt(RETAIL, STIM)
    assert f"more than {expert_q.max_high} " not in lay_prompt


def test_both_prompts_still_carry_the_persona_mandate():
    for persona in (CREDIT, RETAIL):
        assert persona.mandate.split(".")[0] in build_scoring_prompt(persona, STIM)


def test_quota_rejects_a_document_too_short_to_have_a_minority():
    with pytest.raises(ValueError, match="at least"):
        salience_quota(CREDIT, n_units=1)
