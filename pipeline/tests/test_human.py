"""Comparing a human's markup against the modelled personas.

Used twice. In the demo it is Act 2's closing move — the viewer highlights the
note themselves, then finds out whose perceptual field theirs most resembles. In
the pipeline it is the face-validity check: real finance people mark up the hero
note, and their markup is compared to the persona claiming to represent them.

The second use is the more important one. If a real credit analyst's markup does
not resemble the credit-analyst persona, that is a finding to publish, not a bug
to tune away.
"""

import pytest

from cmp.field import PerceptualField, Unit
from cmp.metrics import perceptual_overlap
from cmp.human import (
    HumanMarkup,
    closest_persona,
    rank_personas,
    salience_from_highlights,
)


def _field(persona_id, salience):
    return PerceptualField(
        persona_id=persona_id,
        units=[
            Unit(salience=s, valence=0.0, chunk=0, arousal=0.0, order=i)
            for i, s in enumerate(salience)
        ],
    )


FOCUSED = _field("credit-analyst", [0.9, 0.9, 0.05, 0.05])
OPPOSITE = _field("equity-pm", [0.05, 0.05, 0.9, 0.9])
FIELDS = [FOCUSED, OPPOSITE]


# --- turning highlights into a salience vector --------------------------------------


def test_highlighted_units_carry_most_of_the_attention():
    salience = salience_from_highlights({0, 1}, n_units=4)
    assert salience[0] > salience[2]
    assert salience[1] > salience[3]


def test_unhighlighted_units_keep_a_small_baseline():
    """A reader still saw the words they did not mark; they just did not dwell."""
    salience = salience_from_highlights({0}, n_units=3)
    assert all(s > 0 for s in salience)


def test_highlighting_everything_is_the_same_as_highlighting_nothing():
    """Both are uniform attention — neither says anything about what mattered.

    The two vectors differ in scale but are identical as distributions, which is
    the only level at which salience is meaningful (note claim 9).
    """
    everything = salience_from_highlights({0, 1, 2}, n_units=3)
    nothing = salience_from_highlights(set(), n_units=3)
    assert perceptual_overlap(everything, nothing) == pytest.approx(1.0)


def test_highlight_index_must_be_in_range():
    with pytest.raises(ValueError, match="out of range"):
        salience_from_highlights({7}, n_units=3)


def test_n_units_must_be_positive():
    with pytest.raises(ValueError, match="at least two"):
        salience_from_highlights(set(), n_units=1)


# --- ranking ------------------------------------------------------------------------


def test_a_reader_is_ranked_closest_to_the_persona_they_match():
    markup = HumanMarkup(person_id="p1", highlights={0, 1})
    assert closest_persona(markup, FIELDS, n_units=4) == "credit-analyst"


def test_a_reader_matching_the_other_persona_ranks_that_way():
    markup = HumanMarkup(person_id="p2", highlights={2, 3})
    assert closest_persona(markup, FIELDS, n_units=4) == "equity-pm"


def test_ranking_covers_every_persona():
    markup = HumanMarkup(person_id="p1", highlights={0})
    ranked = rank_personas(markup, FIELDS, n_units=4)
    assert {r.persona_id for r in ranked} == {"credit-analyst", "equity-pm"}


def test_ranking_is_ordered_by_descending_overlap():
    markup = HumanMarkup(person_id="p1", highlights={0, 1})
    ranked = rank_personas(markup, FIELDS, n_units=4)
    assert ranked[0].overlap >= ranked[1].overlap


def test_every_overlap_is_a_proportion():
    markup = HumanMarkup(person_id="p1", highlights={0, 2})
    for result in rank_personas(markup, FIELDS, n_units=4):
        assert 0.0 <= result.overlap <= 1.0


def test_ranking_needs_at_least_one_persona():
    markup = HumanMarkup(person_id="p1", highlights={0})
    with pytest.raises(ValueError, match="at least one persona"):
        rank_personas(markup, [], n_units=4)


def test_markup_must_match_the_stimulus_length():
    markup = HumanMarkup(person_id="p1", highlights={0})
    with pytest.raises(ValueError, match="4 units"):
        rank_personas(markup, FIELDS, n_units=9)


def test_a_reader_who_marked_nothing_is_still_ranked():
    """Uniform attention resembles the least concentrated persona most."""
    markup = HumanMarkup(person_id="p1", highlights=set())
    ranked = rank_personas(markup, FIELDS, n_units=4)
    assert len(ranked) == 2


def test_markup_records_who_it_came_from_for_the_validity_check():
    markup = HumanMarkup(person_id="analyst-3", highlights={1}, role="credit analyst")
    assert markup.role == "credit analyst"
