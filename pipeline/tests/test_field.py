"""The perceptual field and its JSON contract.

`fixtures/perceptual_field.json` is the only thing shared between the scoring
pipeline and the visualization. The pipeline must not know how anything is
rendered; the visualization must not know that language models exist. These
tests pin the contract so either half can be rebuilt without the other.
"""

import json

import pytest

from cmp.field import PerceptualField, Stimulus, StimulusFieldSet, Unit


def _units(salience, valence=None, chunk=None, arousal=None, order=None):
    n = len(salience)
    valence = valence if valence is not None else [0.0] * n
    chunk = chunk if chunk is not None else list(range(n))
    arousal = arousal if arousal is not None else [0.0] * n
    order = order if order is not None else list(range(n))
    return [
        Unit(salience=s, valence=v, chunk=c, arousal=a, order=o)
        for s, v, c, a, o in zip(salience, valence, chunk, arousal, order)
    ]


def _stimulus(n=4):
    return Stimulus(
        id="test-note",
        title="Test note",
        texts=[f"clause {i}" for i in range(n)],
    )


# --- validation ---------------------------------------------------------------------


def test_salience_must_lie_in_the_unit_interval():
    with pytest.raises(ValueError, match="salience"):
        Unit(salience=1.4, valence=0.0, chunk=0, arousal=0.0, order=0)


def test_valence_must_lie_between_minus_one_and_one():
    with pytest.raises(ValueError, match="valence"):
        Unit(salience=0.5, valence=-2.0, chunk=0, arousal=0.0, order=0)


def test_arousal_must_lie_in_the_unit_interval():
    with pytest.raises(ValueError, match="arousal"):
        Unit(salience=0.5, valence=0.0, chunk=0, arousal=1.1, order=0)


def test_field_must_score_every_unit_of_its_stimulus():
    stim = _stimulus(4)
    complete = PerceptualField(persona_id="equity-pm", units=_units([0.1, 0.2, 0.3, 0.4]))
    short = PerceptualField(persona_id="credit-analyst", units=_units([0.1, 0.2, 0.3]))
    with pytest.raises(ValueError, match="every unit"):
        StimulusFieldSet(stimulus=stim, fields=[complete, short])


def test_field_set_requires_at_least_two_personas_to_compare():
    stim = _stimulus(3)
    one = PerceptualField(persona_id="solo", units=_units([0.1, 0.2, 0.3]))
    with pytest.raises(ValueError, match="two personas"):
        StimulusFieldSet(stimulus=stim, fields=[one])


def test_persona_ids_must_be_unique():
    stim = _stimulus(3)
    a = PerceptualField(persona_id="same", units=_units([0.1, 0.2, 0.3]))
    b = PerceptualField(persona_id="same", units=_units([0.3, 0.2, 0.1]))
    with pytest.raises(ValueError, match="unique"):
        StimulusFieldSet(stimulus=stim, fields=[a, b])


# --- the JSON contract --------------------------------------------------------------


def _two_persona_set():
    stim = _stimulus(4)
    a = PerceptualField(
        persona_id="credit-analyst",
        units=_units([0.9, 0.1, 0.8, 0.1], valence=[-0.9, 0.2, -0.7, 0.0]),
    )
    b = PerceptualField(
        persona_id="equity-pm",
        units=_units([0.1, 0.9, 0.2, 0.8], valence=[0.8, 0.3, 0.6, 0.1]),
    )
    return StimulusFieldSet(stimulus=stim, fields=[a, b])


def test_export_round_trips_through_json():
    original = _two_persona_set()
    restored = StimulusFieldSet.from_dict(json.loads(json.dumps(original.to_dict())))
    assert restored.stimulus.id == original.stimulus.id
    assert [f.persona_id for f in restored.fields] == [f.persona_id for f in original.fields]
    assert restored.fields[0].salience() == original.fields[0].salience()


def test_export_carries_the_stimulus_text():
    """The visualization renders the real words, so they travel with the scores."""
    payload = _two_persona_set().to_dict()
    assert payload["stimulus"]["texts"][0] == "clause 0"


def test_export_includes_a_comparison_for_every_persona_pair():
    payload = _two_persona_set().to_dict()
    pairs = {tuple(sorted(c["personas"])) for c in payload["comparisons"]}
    assert pairs == {("credit-analyst", "equity-pm")}


def test_comparison_reports_perceptual_overlap():
    comparison = _two_persona_set().to_dict()["comparisons"][0]
    assert 0.0 <= comparison["overlap"] <= 1.0


def test_comparison_reports_valence_conflicts_as_unit_indices():
    """Units 0 and 2 are negative for the credit analyst, positive for the PM."""
    comparison = _two_persona_set().to_dict()["comparisons"][0]
    assert comparison["valence_conflicts"] == [0, 2]


def test_comparison_reports_chunk_agreement():
    comparison = _two_persona_set().to_dict()["comparisons"][0]
    assert -1.0 <= comparison["chunk_agreement"] <= 1.0


def test_export_records_each_persona_concentration():
    payload = _two_persona_set().to_dict()
    by_id = {f["persona_id"]: f for f in payload["fields"]}
    assert 0.0 <= by_id["credit-analyst"]["concentration"] <= 1.0


def test_export_declares_provenance_so_the_demo_can_be_honest():
    """The honesty panel reads this, rather than having it retyped by hand."""
    payload = _two_persona_set().to_dict()
    assert payload["provenance"]["measured"] is False
    assert "modelled" in payload["provenance"]["summary"].lower()


def test_export_records_how_the_scores_were_produced():
    """A fixture must carry its own method, so the panel cannot drift from the truth."""
    payload = _two_persona_set().to_dict()
    assert payload["provenance"]["method"]


def test_provenance_method_can_be_set_per_field_set():
    stim = _stimulus(3)
    a = PerceptualField(persona_id="a", units=_units([0.1, 0.2, 0.3]))
    b = PerceptualField(persona_id="b", units=_units([0.3, 0.2, 0.1]))
    field_set = StimulusFieldSet(
        stimulus=stim, fields=[a, b], method="scored by hand for a unit test"
    )
    assert field_set.to_dict()["provenance"]["method"] == "scored by hand for a unit test"


def test_provenance_records_whether_reliability_was_measurable():
    payload = _two_persona_set().to_dict()
    assert "reliability_measured" in payload["provenance"]


def test_export_is_json_serialisable_without_custom_encoders():
    json.dumps(_two_persona_set().to_dict())


def test_schema_version_is_present():
    assert _two_persona_set().to_dict()["schema_version"] == 1
