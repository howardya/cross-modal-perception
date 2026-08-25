"""What the role signatures actually showed, pinned against the fixtures.

These encode findings rather than behaviour, negative ones included. If a
re-scoring run overturns any of them, the test fails and the write-up gets
corrected — which is the point. A claim in `docs/findings.md` that no longer
matches the data is worse than no claim.
"""

import pytest

#: These pin the *first*, failed attempt at a signature — the six statistical
#: traits of docs/findings.md 5b. Re-scoring every reader on every document in
#: one sweep overturned their specific orderings. Restricting the computation to
#: the original four readers does not restore them, so the cause is the
#: re-score rather than the three new readers.
#:
#: They are marked xfail rather than rewritten. Rewriting the assertions to
#: match whatever the new sweep says would be fitting a claim to data, which is
#: the one thing this project keeps refusing to do; deleting them would erase a
#: recorded negative result. Marked, they still run, and pytest will say so if a
#: future sweep brings any of them back.
_SUPERSEDED = pytest.mark.xfail(reason=(
    "superseded by the seven-reader sweep: the trait orderings this pins do not reproduce across independent sweeps, which is itself the finding — see docs/calibration.md 7.9. The conclusion of findings.md 5b, that the statistical-trait signature was not usable, is unaffected and reinforced."
), strict=False)

from cmp.dna import collect
from cmp.signature import TRAITS, trait_drift

EXPERTS = ("credit-analyst", "equity-pm", "risk-officer")
LAY = "retail-investor"

#: The trait experiment in docs/findings.md 5b was run on these four readers,
#: before the distressed investor, short seller and journalist existed. Its
#: findings — including the negative ones — are claims about this population.
#: Recomputing them over seven readers would be a new experiment whose result
#: nobody has written up, so these tests keep the original four. Everything
#: about the *topic* signature, which is what the study actually rests on, is
#: computed over all seven elsewhere.
ORIGINAL_FOUR = EXPERTS + (LAY,)


@pytest.fixture(scope="module")
def data():
    return collect(only=ORIGINAL_FOUR)


@pytest.fixture(scope="module")
def drifts(data):
    return {
        t.key: trait_drift(data["hero"][t.key], data["held-out"][t.key])
        for t in TRAITS
    }


# --- the trait that works ------------------------------------------------------------


@_SUPERSEDED
def test_threat_pull_is_the_only_trait_whose_ordering_survives(drifts):
    holds = [k for k, d in drifts.items() if d.same_ordering]
    assert holds == ["threat"], holds


@_SUPERSEDED
def test_threat_pull_carries_role_signal(drifts):
    assert drifts["threat"].stable
    assert drifts["threat"].verdict == "role signal"


def test_the_untrained_reader_is_drawn_to_good_news_on_both_documents(data):
    """The sign flip is the finding: attention pulled the opposite way."""
    for doc in ("hero", "held-out"):
        assert data[doc]["threat"][LAY] < 0, doc


def test_two_of_three_professionals_are_drawn_to_bad_news_on_both(data):
    for pid in ("equity-pm", "risk-officer"):
        for doc in ("hero", "held-out"):
            assert data[doc]["threat"][pid] > 0.5, (pid, doc)


# --- the honest negatives ------------------------------------------------------------


def test_the_credit_analyst_does_not_hold_the_pattern(data):
    """Recorded deliberately. On the held-out note its threat pull collapses,
    so the professional/lay separation rests on two roles, not three."""
    assert data["hero"]["threat"]["credit-analyst"] > 0.5
    assert abs(data["held-out"]["threat"]["credit-analyst"]) < 0.2


def test_the_group_gap_narrows_sharply_on_the_unseen_document(data):
    def gap(doc):
        vals = data[doc]["threat"]
        return min(vals[p] for p in EXPERTS) - vals[LAY]

    assert gap("hero") > 1.0
    assert gap("held-out") < 0.5


@_SUPERSEDED
def test_reading_position_is_a_property_of_the_document_not_the_role(drifts):
    """The lead figure's 'professionals in the middle' does not generalise."""
    assert not drifts["position"].stable


@_SUPERSEDED
def test_alarm_does_not_survive_either(drifts):
    assert not drifts["alarm"].stable


def test_no_trait_gives_all_four_roles_a_stable_distinct_ranking(drifts):
    """The claim the write-up must not overreach: there is one axis, not four
    separate genomes."""
    fully = [k for k, d in drifts.items() if d.same_ordering and d.stable]
    assert len(fully) <= 1, fully


def _untied_expert_orderings(data) -> set[str]:
    """Traits that rank the three professionals identically on both documents.

    Ties are excluded: on the held-out note chunking is 2.50 for all three, so
    any ordering it appears to have is an artefact of the sort, not a finding.
    """
    out = set()
    for t in TRAITS:
        vals = [(data[d][t.key], d) for d in ("hero", "held-out")]
        if any(len({v[p] for p in EXPERTS}) < len(EXPERTS) for v, _ in vals):
            continue
        orders = [sorted(EXPERTS, key=lambda p: v[p]) for v, _ in vals]
        if orders[0] == orders[1]:
            out.add(t.key)
    return out


@_SUPERSEDED
def test_only_a_few_traits_rank_the_professionals_consistently(data):
    """Three of six, once ties are excluded — and with two documents and six
    traits that is suggestive rather than established."""
    assert _untied_expert_orderings(data) == {"threat", "alarm", "position"}


def test_the_risk_officer_is_the_separable_professional(data):
    """Both surviving within-expert orderings put the risk officer at one end:
    most alarmed, and reading latest in the document."""
    for doc in ("hero", "held-out"):
        assert data[doc]["alarm"]["risk-officer"] == max(
            data[doc]["alarm"][p] for p in EXPERTS
        ), doc
        assert data[doc]["position"]["risk-officer"] == max(
            data[doc]["position"][p] for p in EXPERTS
        ), doc


def test_the_within_expert_differences_are_small(data):
    """They are consistent in direction and slight in size. The write-up must
    not inflate them into distinct genomes."""
    for key in ("alarm", "position"):
        for doc in ("hero", "held-out"):
            vals = [data[doc][key][p] for p in EXPERTS]
            assert max(vals) - min(vals) < 0.2, (key, doc)


def test_the_professional_lay_split_dominates_on_the_hero_note(data):
    """On the note the method was tuned to, the group gap is bigger than the
    spread inside the group — one axis, as the write-up says."""
    vals = data["hero"]["threat"]
    within = max(vals[p] for p in EXPERTS) - min(vals[p] for p in EXPERTS)
    between = min(vals[p] for p in EXPERTS) - vals[LAY]
    assert between > within * 3


def test_that_dominance_does_not_hold_on_the_unseen_note(data):
    """And on the held-out note it inverts: the professionals differ from each
    other more than they differ from the layperson. Recorded because it is the
    strongest caution against reading these six numbers as settled DNA."""
    vals = data["held-out"]["threat"]
    within = max(vals[p] for p in EXPERTS) - min(vals[p] for p in EXPERTS)
    between = min(vals[p] for p in EXPERTS) - vals[LAY]
    assert within > between


@_SUPERSEDED
def test_within_professional_differences_are_consistent_but_slight(data):
    """Several traits order the professionals the same way twice. With two
    documents that is a coin landing the same way twice, and on the hero note
    the gaps are at noise level, so the write-up reports direction only."""
    for key in ("threat", "alarm"):
        gap = abs(data["hero"][key]["credit-analyst"] - data["hero"][key]["equity-pm"])
        assert gap < 0.1, (key, gap)


# --- provenance of the traits --------------------------------------------------------


@_SUPERSEDED
def test_the_strongest_trait_was_not_one_the_prompt_dictated(drifts):
    """Guards against the obvious objection that the signature just recovers
    the instructions."""
    threat = next(t for t in TRAITS if t.key == "threat")
    assert not threat.prompted
    assert drifts["threat"].verdict == "role signal"


@_SUPERSEDED
def test_a_prompted_trait_failed(drifts):
    """The same objection, from the other side: being in the prompt did not
    guarantee the trait would hold."""
    prompted = [t.key for t in TRAITS if t.prompted]
    assert any(not drifts[k].stable for k in prompted)
