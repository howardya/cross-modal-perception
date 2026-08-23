"""Role signatures — the traits that might be properties of a role rather than
of the document it was reading.

A fingerprint identifies; DNA generates. A per-clause field is a fingerprint: it
describes how one reader met one document. A signature is only worth the name if
it survives changing the document, so every trait here is designed to be
computable on any stimulus and is checked against both.
"""

import pytest

from cmp.field import PerceptualField, Unit
from cmp.signature import TRAITS, signature, trait_drift


def _field(persona_id="x", salience=None, valence=None, arousal=None, chunks=None):
    n = len(salience)
    valence = valence if valence is not None else [0.0] * n
    arousal = arousal if arousal is not None else [0.0] * n
    chunks = chunks if chunks is not None else list(range(n))
    return PerceptualField(
        persona_id=persona_id,
        units=[
            Unit(salience=s, valence=v, chunk=c, arousal=a, order=i)
            for i, (s, v, c, a) in enumerate(zip(salience, valence, chunks, arousal))
        ],
    )


# --- threat orientation: the trait that turned out to matter --------------------------


def test_attention_pulled_by_bad_news_scores_positive_threat():
    """The expert pattern: the worse a clause is, the harder you look at it."""
    f = _field(salience=[0.9, 0.7, 0.3, 0.1], valence=[-0.9, -0.6, 0.4, 0.8])
    assert signature(f).threat > 0.8


def test_attention_pulled_by_good_news_scores_negative_threat():
    """The untrained pattern: the eye goes to what sounds encouraging."""
    f = _field(salience=[0.9, 0.7, 0.3, 0.1], valence=[0.9, 0.6, -0.4, -0.8])
    assert signature(f).threat < -0.8


def test_attention_indifferent_to_valence_scores_near_zero():
    f = _field(salience=[0.9, 0.1, 0.9, 0.1], valence=[0.8, 0.8, -0.8, -0.8])
    assert abs(signature(f).threat) < 0.2


def test_threat_is_undefined_without_variation_in_valence():
    """Flat valence means there is no direction for attention to prefer."""
    f = _field(salience=[0.9, 0.5, 0.2, 0.1], valence=[0.3, 0.3, 0.3, 0.3])
    assert signature(f).threat == 0.0


# --- the other traits ----------------------------------------------------------------


def test_mood_is_the_average_valence():
    f = _field(salience=[0.5] * 4, valence=[-0.4, -0.2, 0.2, 0.0])
    assert signature(f).mood == pytest.approx(-0.1)


def test_alarm_is_the_average_arousal():
    f = _field(salience=[0.5] * 3, arousal=[0.2, 0.5, 0.8])
    assert signature(f).alarm == pytest.approx(0.5)


def test_chunk_size_counts_clauses_per_group():
    f = _field(salience=[0.5] * 6, chunks=[0, 0, 0, 1, 1, 1])
    assert signature(f).chunk_size == pytest.approx(3.0)


def test_reading_clause_by_clause_gives_a_chunk_size_of_one():
    f = _field(salience=[0.5] * 5, chunks=[0, 1, 2, 3, 4])
    assert signature(f).chunk_size == pytest.approx(1.0)


def test_focus_matches_the_field_concentration():
    f = _field(salience=[0.9, 0.1, 0.1, 0.1])
    assert signature(f).focus == pytest.approx(f.concentration())


def test_position_is_zero_when_all_attention_is_at_the_start():
    f = _field(salience=[1.0, 0.0, 0.0, 0.0])
    assert signature(f).position == pytest.approx(0.0)


def test_position_is_one_when_all_attention_is_at_the_end():
    f = _field(salience=[0.0, 0.0, 0.0, 1.0])
    assert signature(f).position == pytest.approx(1.0)


def test_position_is_a_half_for_evenly_spread_attention():
    f = _field(salience=[0.5] * 5)
    assert signature(f).position == pytest.approx(0.5)


# --- the trait catalogue -------------------------------------------------------------


def test_every_trait_declares_what_it_asks_in_plain_english():
    for t in TRAITS:
        assert t.question.endswith("?"), t.key
        assert len(t.question) > 15


def test_every_trait_names_its_two_poles():
    """A number without both ends labelled cannot be read."""
    for t in TRAITS:
        assert t.low and t.high, t.key


def test_every_trait_declares_whether_the_prompt_specified_it():
    """The traits the mandate already dictates are not discoveries."""
    for t in TRAITS:
        assert isinstance(t.prompted, bool)
    assert any(t.prompted for t in TRAITS)
    assert any(not t.prompted for t in TRAITS)


def test_the_catalogue_covers_exactly_the_signature_fields():
    f = _field(salience=[0.4, 0.6, 0.2])
    sig = signature(f)
    assert {t.key for t in TRAITS} == set(vars(sig))


# --- stability: the test that decides whether this is DNA at all ---------------------


def test_a_trait_that_does_not_move_between_documents_is_stable():
    a = {"credit": 0.8, "retail": -0.5}
    b = {"credit": 0.75, "retail": -0.45}
    assert trait_drift(a, b).stable


def test_a_trait_that_moves_as_much_as_it_spreads_is_not_stable():
    a = {"credit": 0.8, "retail": -0.5}
    b = {"credit": -0.4, "retail": 0.7}
    assert not trait_drift(a, b).stable


def test_drift_reports_the_signal_to_noise_it_judged_on():
    a = {"credit": 1.0, "retail": 0.0}
    b = {"credit": 0.9, "retail": 0.1}
    d = trait_drift(a, b)
    assert d.spread == pytest.approx(1.0)
    assert d.drift == pytest.approx(0.1)
    assert d.ratio == pytest.approx(10.0)


def test_drift_reports_whether_the_role_ordering_survived():
    same = trait_drift({"a": 1.0, "b": 2.0, "c": 3.0}, {"a": 1.1, "b": 2.2, "c": 3.3})
    flipped = trait_drift({"a": 1.0, "b": 2.0, "c": 3.0}, {"a": 3.0, "b": 2.0, "c": 1.0})
    assert same.same_ordering
    assert not flipped.same_ordering


def test_drift_needs_the_same_roles_on_both_sides():
    with pytest.raises(ValueError, match="same roles"):
        trait_drift({"a": 1.0}, {"b": 2.0})
