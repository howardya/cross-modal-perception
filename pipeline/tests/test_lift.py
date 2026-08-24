"""Attention lift: what a reader over-attends to, and what they walk past.

The first attempt at a role signature produced six statistical traits and no
insight — "threat pull is the negative correlation of salience with valence" is
a number about a number, and it re-derived something the top-k table already
showed.

This is the replacement, and it answers the question a signature should answer:
*what kind of sentence makes this reader look up, and what do they walk past
while everyone else stops?* Lift compares one reader's share of attention on a
sentence against the average of all readers. The negative tail is the more
interesting half, because the project's own thesis is that expertise is learned
neglect.
"""

import pytest

from cmp.lift import attention_lift, blind_spots, mirrored_pairs, signatures


def _field(persona_id, salience):
    return {"persona_id": persona_id, "salience": salience}


FOUR = [
    _field("a", [0.9, 0.1, 0.1, 0.1]),
    _field("b", [0.1, 0.9, 0.1, 0.1]),
    _field("c", [0.1, 0.1, 0.9, 0.1]),
    _field("d", [0.1, 0.1, 0.1, 0.9]),
]


# --- lift ----------------------------------------------------------------------------


def test_a_reader_lifts_the_sentence_only_they_attend_to():
    lift = attention_lift(FOUR)
    assert lift["a"][0] > 0
    assert lift["b"][0] < 0


def test_lift_is_zero_when_every_reader_attends_identically():
    same = [_field(p, [0.4, 0.3, 0.2, 0.1]) for p in "abcd"]
    lift = attention_lift(same)
    for p in "abcd":
        assert all(abs(v) < 1e-12 for v in lift[p])


def test_lift_sums_to_zero_across_readers_on_every_sentence():
    """It is a share of attention redistributed, so it must balance."""
    lift = attention_lift(FOUR)
    for i in range(4):
        assert sum(lift[p][i] for p in "abcd") == pytest.approx(0.0)


def test_lift_is_scale_free():
    """A reader who scores everything high must not dominate every sentence."""
    loud = [
        _field("a", [0.9, 0.1, 0.1, 0.1]),
        _field("b", [9.0, 1.0, 1.0, 1.0]),
    ]
    lift = attention_lift(loud)
    for i in range(4):
        assert abs(lift["a"][i]) < 1e-12


def test_lift_needs_at_least_two_readers():
    with pytest.raises(ValueError, match="two readers"):
        attention_lift([_field("a", [0.5, 0.5])])


def test_lift_rejects_readers_of_differing_length():
    with pytest.raises(ValueError, match="same length"):
        attention_lift([_field("a", [0.5, 0.5]), _field("b", [0.5])])


# --- signatures and blind spots ------------------------------------------------------


def test_a_signature_is_what_is_more_this_readers_than_anyones():
    sig = signatures(FOUR, "a", k=1)
    assert [s.index for s in sig] == [0]


def test_a_blind_spot_is_where_everyone_else_stopped():
    blind = blind_spots(FOUR, "a", k=3)
    assert 0 not in [b.index for b in blind]
    assert all(b.lift < 0 for b in blind)


def test_signatures_are_ordered_strongest_first():
    sig = signatures(FOUR, "a", k=4)
    assert [s.lift for s in sig] == sorted([s.lift for s in sig], reverse=True)


def test_blind_spots_are_ordered_deepest_first():
    blind = blind_spots(FOUR, "a", k=3)
    assert [b.lift for b in blind] == sorted([b.lift for b in blind])


def test_an_unknown_reader_is_reported_clearly():
    with pytest.raises(KeyError, match="zzz"):
        signatures(FOUR, "zzz", k=1)


# --- the finding: blind spots are other people's specialisms -------------------------


def test_a_sentence_one_reader_owns_and_another_misses_is_a_mirrored_pair():
    pairs = mirrored_pairs(FOUR, k=1)
    assert pairs, "the fixture has an obvious mirror and none was found"
    p = pairs[0]
    assert p.seen_by != p.missed_by
    assert p.seen_lift > 0 > p.missed_lift


def test_mirrored_pairs_are_ordered_by_how_wide_the_gap_is():
    pairs = mirrored_pairs(FOUR, k=4)
    gaps = [p.seen_lift - p.missed_lift for p in pairs]
    assert gaps == sorted(gaps, reverse=True)


def test_each_sentence_appears_at_most_once_in_the_pairs():
    """One row per sentence, or the figure repeats itself."""
    pairs = mirrored_pairs(FOUR, k=4)
    idx = [p.index for p in pairs]
    assert len(idx) == len(set(idx))


def test_a_document_nobody_disagrees_about_yields_no_pairs():
    same = [_field(p, [0.4, 0.3, 0.2, 0.1]) for p in "abcd"]
    assert mirrored_pairs(same, k=3) == []
