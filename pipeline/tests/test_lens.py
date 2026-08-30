"""One live reading of one document by one reader.

The study aggregates five samples per persona and measures the agreement between
them. The lens cannot: the viewer is waiting. So the thing these tests guard
hardest is that borrowing the study's prompt does not let the lens quietly
change the study's contract — `SCORING_SCHEMA` must come out of this module
untouched.
"""

import pytest

from cmp.anthropic_client import SCORING_SCHEMA, build_scoring_prompt
from cmp.field import Stimulus
from cmp.ingest import Ingested
from cmp.lens import (
    LENS_SCHEMA,
    MAX_NOTES,
    LensField,
    attend,
    build_lens_prompt,
    parse_lens,
    stimulus_of,
)
from cmp.personas import persona_by_id

CREDIT = persona_by_id("credit-analyst")
RETAIL = persona_by_id("retail-investor")

DOC = Ingested(
    doc_id="abc123",
    title="Q4 results",
    clauses=[
        "Revenue rose 19%.",
        "Gross margin fell 240 basis points.",
        "Leverage reached 4.1 turns.",
        "The buyback was funded from the revolver.",
        "The dividend was raised 8%.",
        "Free cash flow was negative.",
    ],
    source="text",
)


def payload(n=6, notes=None):
    units = []
    for i in range(n):
        unit = {
            "salience": round(0.1 + 0.1 * i, 2),
            "valence": -0.5,
            "chunk": i // 2,
            "arousal": 0.3,
        }
        if notes and i in notes:
            unit["note"] = notes[i]
        units.append(unit)
    return {"units": units}


class StubClient:
    """Returns a canned payload; records what it was asked."""

    def __init__(self, response=None):
        self.response = response if response is not None else payload()
        self.calls = []

    def raw_attend(self, persona, stimulus):
        self.calls.append((persona.id, stimulus))
        return self.response


# --- the study's contract is not touched --------------------------------------------


def test_the_study_schema_still_has_exactly_its_four_fields():
    props = SCORING_SCHEMA["properties"]["units"]["items"]["properties"]
    assert set(props) == {"salience", "valence", "chunk", "arousal"}


def test_the_study_schema_still_requires_exactly_those_four():
    required = SCORING_SCHEMA["properties"]["units"]["items"]["required"]
    assert set(required) == {"salience", "valence", "chunk", "arousal"}


def test_the_lens_schema_is_a_superset():
    study = SCORING_SCHEMA["properties"]["units"]["items"]["properties"]
    lens = LENS_SCHEMA["properties"]["units"]["items"]["properties"]
    assert set(study) < set(lens)
    assert set(lens) - set(study) == {"note"}


def test_the_note_is_not_required():
    assert "note" not in LENS_SCHEMA["properties"]["units"]["items"]["required"]


def test_the_lens_schema_is_a_copy_not_an_alias():
    LENS_SCHEMA["properties"]["units"]["items"]["properties"]["scratch"] = {}
    try:
        study = SCORING_SCHEMA["properties"]["units"]["items"]["properties"]
        assert "scratch" not in study
    finally:
        del LENS_SCHEMA["properties"]["units"]["items"]["properties"]["scratch"]


# --- prompt -------------------------------------------------------------------------


def test_the_lens_prompt_contains_the_study_prompt_unchanged():
    stim = stimulus_of(DOC)
    assert build_scoring_prompt(CREDIT, stim) in build_lens_prompt(CREDIT, stim)


def test_the_lens_prompt_asks_for_notes():
    assert "note" in build_lens_prompt(CREDIT, stimulus_of(DOC)).lower()


def test_the_lens_prompt_bounds_how_many_notes():
    assert str(MAX_NOTES) in build_lens_prompt(CREDIT, stimulus_of(DOC))


# --- parsing ------------------------------------------------------------------------


def test_scores_parse_without_any_notes():
    scores, notes = parse_lens(payload(), n_units=6)
    assert len(scores) == 6
    assert notes == {}


def test_notes_are_returned_against_their_clause_index():
    scores, notes = parse_lens(payload(notes={2: "That is the covenant."}), n_units=6)
    assert notes == {2: "That is the covenant."}


def test_blank_notes_are_dropped():
    _, notes = parse_lens(payload(notes={1: "   "}), n_units=6)
    assert notes == {}


def test_more_notes_than_allowed_keeps_the_most_salient_clauses():
    given = {i: f"note {i}" for i in range(6)}
    _, notes = parse_lens(payload(notes=given), n_units=6)
    assert len(notes) == MAX_NOTES
    # salience rises with index in the stub payload, so the tail survives.
    assert set(notes) == {5, 4, 3, 2}


def test_a_wrong_unit_count_is_still_refused():
    with pytest.raises(ValueError, match="6"):
        parse_lens(payload(n=4), n_units=6)


def test_an_out_of_range_score_is_still_refused():
    bad = payload()
    bad["units"][0]["salience"] = 1.4
    with pytest.raises(ValueError):
        parse_lens(bad, n_units=6)


# --- attend -------------------------------------------------------------------------


def test_attend_returns_a_field_over_every_clause():
    got = attend(StubClient(), CREDIT, DOC)
    assert isinstance(got, LensField)
    assert len(got.field.units) == len(DOC.clauses)


def test_attend_labels_the_field_with_the_persona():
    assert attend(StubClient(), RETAIL, DOC).field.persona_id == "retail-investor"


def test_reading_order_ranks_by_salience_most_salient_first():
    got = attend(StubClient(), CREDIT, DOC)
    orders = [u.order for u in got.field.units]
    # salience rises with index, so the last clause is reached first.
    assert orders[-1] == 0
    assert orders[0] == len(DOC.clauses) - 1


def test_attend_passes_the_document_title_to_the_model():
    stub = StubClient()
    attend(stub, CREDIT, DOC)
    assert stub.calls[0][1].title == "Q4 results"


def test_attend_reports_one_sample_and_no_measured_reliability():
    got = attend(StubClient(), CREDIT, DOC)
    blob = got.to_dict()
    assert blob["samples"] == 1
    assert blob["reliability_measured"] is False


def test_the_serialised_field_carries_its_notes():
    stub = StubClient(payload(notes={3: "Borrowing to buy stock."}))
    blob = attend(stub, CREDIT, DOC).to_dict()
    assert blob["notes"] == {"3": "Borrowing to buy stock."}


def test_a_field_that_attended_to_nothing_is_refused():
    flat = {"units": [{"salience": 0.0, "valence": 0.0, "chunk": 0, "arousal": 0.0}] * 6}
    with pytest.raises(ValueError):
        attend(StubClient(flat), CREDIT, DOC)


def test_stimulus_of_uses_the_doc_id_so_scores_can_be_traced_back():
    assert stimulus_of(DOC).id == "abc123"
