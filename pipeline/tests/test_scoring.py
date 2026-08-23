"""Persona scoring: k samples, aggregated, with reliability reported.

The scoring client is injected, so these tests exercise the real aggregation
logic against a deterministic fake rather than mocking out the thing under test.
No network, no API key.
"""

import pytest

from cmp.field import Stimulus
from cmp.personas import FINANCE_PERSONAS, Persona
from cmp.scoring import RawScores, ScoringRun, aggregate_runs, score_persona


class FakeClient:
    """Returns a canned sequence of raw scores, one per requested sample."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def score(self, persona, stimulus):
        self.calls.append((persona.id, stimulus.id))
        if not self._responses:
            raise AssertionError("FakeClient ran out of canned responses")
        return self._responses.pop(0)


def _raw(salience, valence=None, chunks=None, arousal=None, order=None):
    n = len(salience)
    return RawScores(
        salience=salience,
        valence=valence if valence is not None else [0.0] * n,
        chunks=chunks if chunks is not None else list(range(n)),
        arousal=arousal if arousal is not None else [0.0] * n,
        order=order if order is not None else list(range(n)),
    )


STIM = Stimulus(id="s", title="S", texts=["a", "b", "c", "d"])
PERSONA = Persona(
    id="test",
    label="Test",
    mandate="test the aggregation",
    time_horizon="none",
    loss_function="none",
    reads_for=["nothing"],
    expert=True,
)


# --- personas are mandates, not personalities ---------------------------------------


def test_every_finance_persona_declares_a_mandate():
    """Research note claim 5: information reduction is instruction-sensitive."""
    for persona in FINANCE_PERSONAS:
        assert persona.mandate
        assert persona.loss_function
        assert persona.time_horizon


def test_finance_personas_have_unique_ids():
    ids = [p.id for p in FINANCE_PERSONAS]
    assert len(set(ids)) == len(ids)


def test_the_lay_reader_is_present():
    """The retail investor is the seat most viewers actually occupy."""
    lay = [p for p in FINANCE_PERSONAS if not p.expert]
    assert len(lay) == 1
    assert lay[0].id == "retail-investor"


def test_there_are_experts_to_contrast_with_the_lay_reader():
    assert sum(1 for p in FINANCE_PERSONAS if p.expert) >= 2


# --- aggregation --------------------------------------------------------------------


def test_aggregating_identical_runs_returns_those_scores():
    runs = [_raw([0.2, 0.4, 0.6, 0.8])] * 3
    field = aggregate_runs("test", runs)
    assert field.salience() == pytest.approx([0.2, 0.4, 0.6, 0.8])


def test_aggregation_takes_the_median_so_one_wild_run_cannot_dominate():
    runs = [
        _raw([0.2, 0.4, 0.6, 0.8]),
        _raw([0.2, 0.4, 0.6, 0.8]),
        _raw([1.0, 0.0, 0.0, 0.0]),
    ]
    field = aggregate_runs("test", runs)
    assert field.salience() == pytest.approx([0.2, 0.4, 0.6, 0.8])


def test_aggregation_needs_at_least_two_runs():
    with pytest.raises(ValueError, match="at least two"):
        aggregate_runs("test", [_raw([0.1, 0.2])])


def test_aggregation_rejects_runs_of_differing_length():
    with pytest.raises(ValueError, match="same length"):
        aggregate_runs("test", [_raw([0.1, 0.2]), _raw([0.1, 0.2, 0.3])])


def test_aggregated_chunks_take_the_modal_grouping():
    """Chunks are labels, not magnitudes, so a median would be meaningless."""
    runs = [
        _raw([0.5, 0.5], chunks=[0, 0]),
        _raw([0.5, 0.5], chunks=[0, 0]),
        _raw([0.5, 0.5], chunks=[0, 1]),
    ]
    assert aggregate_runs("test", runs).chunks() == [0, 0]


def test_aggregated_order_is_recomputed_from_aggregated_salience():
    """Order must stay consistent with the salience it is aggregated alongside."""
    runs = [_raw([0.1, 0.9, 0.5], order=[0, 1, 2])] * 2
    field = aggregate_runs("test", runs)
    orders = [u.order for u in field.units]
    assert orders[1] < orders[2] < orders[0]


# --- the k-sample loop --------------------------------------------------------------


def test_score_persona_samples_the_client_k_times():
    client = FakeClient([_raw([0.1, 0.2, 0.3, 0.4]) for _ in range(5)])
    run = score_persona(client, PERSONA, STIM, k=5)
    assert len(client.calls) == 5
    assert isinstance(run, ScoringRun)


def test_score_persona_reports_reliability_across_its_samples():
    client = FakeClient([_raw([0.1, 0.2, 0.3, 0.9]) for _ in range(3)])
    run = score_persona(client, PERSONA, STIM, k=3)
    assert run.reliability.alpha == pytest.approx(1.0)


def test_score_persona_returns_an_aggregated_field():
    client = FakeClient([_raw([0.1, 0.2, 0.3, 0.4]) for _ in range(3)])
    run = score_persona(client, PERSONA, STIM, k=3)
    assert run.field.persona_id == "test"
    assert len(run.field.units) == 4


def test_score_persona_keeps_the_individual_samples_for_audit():
    client = FakeClient([_raw([0.1, 0.2, 0.3, 0.4]) for _ in range(3)])
    run = score_persona(client, PERSONA, STIM, k=3)
    assert len(run.samples) == 3


def test_score_persona_refuses_a_single_sample():
    """One sample is an anecdote and has no measurable reliability."""
    client = FakeClient([_raw([0.1, 0.2, 0.3, 0.4])])
    with pytest.raises(ValueError, match="at least two"):
        score_persona(client, PERSONA, STIM, k=1)


def test_scores_must_cover_every_unit_of_the_stimulus():
    client = FakeClient([_raw([0.1, 0.2]) for _ in range(2)])
    with pytest.raises(ValueError, match="4 units"):
        score_persona(client, PERSONA, STIM, k=2)
