"""The Anthropic-backed scoring client.

Only the pure parts are tested here — prompt construction and response parsing.
The network call itself is three lines of SDK glue and is exercised by the
Phase 3 calibration run, not by unit tests.
"""

import pytest

from cmp.anthropic_client import (
    SCORING_SCHEMA,
    build_scoring_prompt,
    parse_scores,
)
from cmp.field import Stimulus
from cmp.personas import persona_by_id

STIM = Stimulus(id="s", title="S", texts=["Revenue rose 20%.", "Leverage reached 4.1x."])
CREDIT = persona_by_id("credit-analyst")


# --- prompt -------------------------------------------------------------------------


def test_prompt_states_the_persona_mandate():
    prompt = build_scoring_prompt(CREDIT, STIM)
    assert CREDIT.mandate.split(".")[0] in prompt


def test_prompt_numbers_every_unit_so_scores_can_be_aligned():
    prompt = build_scoring_prompt(CREDIT, STIM)
    assert "[0]" in prompt
    assert "[1]" in prompt


def test_prompt_includes_the_actual_stimulus_text():
    prompt = build_scoring_prompt(CREDIT, STIM)
    assert "Leverage reached 4.1x." in prompt


def test_prompt_bounds_attention_arithmetically_not_just_in_prose():
    """Research note claims 9 and 10: attention is zero-sum and dilutes.

    This was originally asserted as prose about a "finite budget". Run 1 of the
    independent scoring showed prose does not hold — the model marked nearly
    every clause salient regardless. The prompt now carries a countable quota,
    so the test checks for that instead. See tests/test_salience_quota.py.
    """
    from cmp.anthropic_client import salience_quota

    q = salience_quota(CREDIT, n_units=len(STIM.texts))
    prompt = build_scoring_prompt(CREDIT, STIM)
    assert str(q.max_high) in prompt
    assert str(q.min_low) in prompt


def test_prompt_asks_for_valence_from_the_persona_point_of_view():
    prompt = build_scoring_prompt(CREDIT, STIM).lower()
    assert "for you" in prompt or "to you" in prompt


# --- schema -------------------------------------------------------------------------


def test_schema_forbids_extra_properties():
    assert SCORING_SCHEMA["additionalProperties"] is False


def test_schema_requires_every_attribute_on_each_unit():
    unit = SCORING_SCHEMA["properties"]["units"]["items"]
    assert set(unit["required"]) == {"salience", "valence", "chunk", "arousal"}


def test_schema_bounds_salience_to_the_unit_interval():
    unit = SCORING_SCHEMA["properties"]["units"]["items"]["properties"]
    assert unit["salience"]["minimum"] == 0
    assert unit["salience"]["maximum"] == 1


def test_schema_allows_negative_valence():
    unit = SCORING_SCHEMA["properties"]["units"]["items"]["properties"]
    assert unit["valence"]["minimum"] == -1


# --- parsing ------------------------------------------------------------------------


def _payload(*units):
    return {"units": list(units)}


def test_parses_a_well_formed_payload():
    raw = parse_scores(
        _payload(
            {"salience": 0.2, "valence": 0.9, "chunk": 0, "arousal": 0.1},
            {"salience": 0.8, "valence": -0.7, "chunk": 1, "arousal": 0.6},
        ),
        n_units=2,
    )
    assert raw.salience == [0.2, 0.8]
    assert raw.valence == [0.9, -0.7]
    assert raw.chunks == [0, 1]
    assert raw.arousal == [0.1, 0.6]


def test_parsed_order_ranks_the_most_salient_unit_first():
    raw = parse_scores(
        _payload(
            {"salience": 0.2, "valence": 0.0, "chunk": 0, "arousal": 0.0},
            {"salience": 0.8, "valence": 0.0, "chunk": 0, "arousal": 0.0},
        ),
        n_units=2,
    )
    assert raw.order == [1, 0]


def test_parsing_rejects_the_wrong_number_of_units():
    with pytest.raises(ValueError, match="2 units"):
        parse_scores(_payload({"salience": 0.2, "valence": 0, "chunk": 0, "arousal": 0}), n_units=2)


def test_parsing_rejects_out_of_range_salience():
    with pytest.raises(ValueError, match="salience"):
        parse_scores(
            _payload({"salience": 1.7, "valence": 0, "chunk": 0, "arousal": 0}),
            n_units=1,
        )


def test_parsing_rejects_a_missing_attribute():
    with pytest.raises((KeyError, ValueError)):
        parse_scores(_payload({"salience": 0.5, "valence": 0.0}), n_units=1)


def test_parsing_rejects_an_all_zero_salience_vector():
    """A persona that attends to nothing has not done the task."""
    with pytest.raises(ValueError, match="zero"):
        parse_scores(
            _payload(
                {"salience": 0.0, "valence": 0, "chunk": 0, "arousal": 0},
                {"salience": 0.0, "valence": 0, "chunk": 0, "arousal": 0},
            ),
            n_units=2,
        )
