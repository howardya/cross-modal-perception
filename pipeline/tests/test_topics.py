"""Attention by topic — the shape that turned out to travel between documents.

Reading position failed as a role trait because its axis was position in one
particular document. Topic is document-independent: "what is owed" exists in any
filing, so a profile built over topics can be computed on a page the reader has
never seen and compared with one it has.

That is the whole reason this module exists, and the test that matters is
`test_profiles_hold_across_documents`.
"""

import pytest

from cmp.topics import (
    CATEGORIES,
    labels_for,
    profile_shape,
    topic_lift,
    topic_share,
)


def _field(persona_id, salience):
    return {"persona_id": persona_id, "salience": salience}


# --- the labelling -------------------------------------------------------------------


def test_every_sentence_of_every_stimulus_is_labelled():
    for name, n in (("meridian-q4", 30), ("aldercroft-h1", 20)):
        assert len(labels_for(name)) == n


def test_labels_only_use_declared_categories():
    for name in ("meridian-q4", "aldercroft-h1"):
        assert set(labels_for(name)) <= set(CATEGORIES)


def test_every_category_appears_in_both_documents():
    """A category present in only one document cannot be compared across them."""
    a, b = set(labels_for("meridian-q4")), set(labels_for("aldercroft-h1"))
    assert a == set(CATEGORIES)
    assert b == set(CATEGORIES)


def test_an_unknown_stimulus_is_reported_clearly():
    with pytest.raises(KeyError, match="nonexistent"):
        labels_for("nonexistent")


# --- shares and lift -----------------------------------------------------------------


def test_share_of_attention_sums_to_one_across_topics():
    readers = [_field("a", [1, 1, 1, 1])]
    labels = ["debt", "debt", "cash", "perform"]
    share = topic_share(readers, labels)["a"]
    assert sum(share.values()) == pytest.approx(1.0)


def test_a_reader_attending_only_to_debt_puts_all_its_share_there():
    readers = [_field("a", [1.0, 0.0, 0.0])]
    labels = ["debt", "cash", "perform"]
    share = topic_share(readers, labels)["a"]
    assert share["debt"] == pytest.approx(1.0)
    assert share["cash"] == pytest.approx(0.0)


def test_share_needs_a_label_for_every_sentence():
    with pytest.raises(ValueError, match="one label per sentence"):
        topic_share([_field("a", [1, 1, 1])], ["debt", "cash"])


def test_lift_is_share_minus_the_reader_average():
    readers = [_field("a", [1.0, 0.0]), _field("b", [0.0, 1.0])]
    labels = ["debt", "cash"]
    lift = topic_lift(readers, labels)
    assert lift["a"]["debt"] == pytest.approx(50.0)
    assert lift["b"]["debt"] == pytest.approx(-50.0)


def test_lift_sums_to_zero_across_readers_for_every_topic():
    readers = [_field("a", [0.9, 0.1]), _field("b", [0.2, 0.8]), _field("c", [0.5, 0.5])]
    labels = ["debt", "cash"]
    lift = topic_lift(readers, labels)
    for c in ("debt", "cash"):
        assert sum(lift[p][c] for p in "abc") == pytest.approx(0.0)


def test_lift_is_reported_in_percentage_points():
    """The page prints these, so the unit has to be the page's unit."""
    readers = [_field("a", [1.0, 0.0]), _field("b", [0.0, 1.0])]
    lift = topic_lift(readers, ["debt", "cash"])
    assert abs(lift["a"]["debt"]) > 1


# --- the finding ---------------------------------------------------------------------


def test_profile_shape_is_ordered_by_the_declared_categories():
    readers = [_field("a", [1.0, 0.0]), _field("b", [0.0, 1.0])]
    shape = profile_shape(topic_lift(readers, ["debt", "cash"])["a"])
    assert len(shape) == len(CATEGORIES)


def test_profiles_hold_across_documents():
    """The claim the whole visual rests on: a reader's topic shape on a page it
    has never seen resembles its shape on the page it was tuned to."""
    import json
    from pathlib import Path

    import numpy as np

    root = Path(__file__).resolve().parents[2]

    def lift_of(name):
        raw = json.loads((root / "fixtures" / f"{name}.json").read_text())
        return topic_lift(raw["fields"], labels_for(name))

    hero, held = lift_of("meridian-q4"), lift_of("aldercroft-h1")
    for pid in hero:
        a = np.array(profile_shape(hero[pid]))
        b = np.array(profile_shape(held[pid]))
        r = float(np.corrcoef(a, b)[0, 1])
        assert r > 0.4, f"{pid} profile does not travel between documents ({r:+.2f})"


def test_the_credit_analyst_and_the_untrained_reader_are_opposites(fixtures_lift):
    """Credit's strongest topic is the untrained reader's weakest, and the
    reverse — the mirror the figure is built around."""
    hero = fixtures_lift("meridian-q4")
    credit, retail = hero["credit-analyst"], hero["retail-investor"]
    assert max(credit, key=credit.get) == "debt"
    assert min(retail, key=retail.get) == "debt"
    assert max(retail, key=retail.get) == "perform"
    assert min(credit, key=credit.get) == "perform"


def test_the_risk_officer_avoids_performance_on_both_documents(fixtures_lift):
    for name in ("meridian-q4", "aldercroft-h1"):
        lift = fixtures_lift(name)["risk-officer"]
        assert min(lift, key=lift.get) == "perform", name


@pytest.fixture
def fixtures_lift():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]

    def _load(name):
        raw = json.loads((root / "fixtures" / f"{name}.json").read_text())
        return topic_lift(raw["fields"], labels_for(name))

    return _load
