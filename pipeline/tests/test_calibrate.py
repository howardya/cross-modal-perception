"""Assembling a calibration report from scored fields.

The report is what gets published: per-persona reliability, the L1 acceptance
verdict against the author-assigned relevance masks, and the pairwise
divergences. Failures are recorded, not suppressed — a field set that misses the
literature's shape produces a report saying so.
"""

import pytest

from cmp.calibrate import CalibrationReport, build_report
from cmp.field import PerceptualField, Unit
from cmp.reliability import reliability_verdict
from cmp.stimuli import load_stimulus


def _field(persona_id, salience):
    return PerceptualField(
        persona_id=persona_id,
        units=[
            Unit(salience=s, valence=0.0, chunk=i // 3, arousal=0.0, order=i)
            for i, s in enumerate(salience)
        ],
    )


HERO = load_stimulus("meridian-q4")
N = len(HERO.stimulus.texts)


def _expertish(mask):
    """A field that attends to the masked clauses and suppresses the rest."""
    return [0.9 if m else 0.03 for m in mask]


def _flat():
    return [0.5] * N


def _fields():
    return [
        _field("credit-analyst", _expertish(HERO.relevance["credit-analyst"])),
        _field("equity-pm", _expertish(HERO.relevance["equity-pm"])),
        _field("risk-officer", _expertish(HERO.relevance["risk-officer"])),
        _field("retail-investor", _flat()),
    ]


def _reliabilities():
    return {p: reliability_verdict(0.9) for p in
            ("credit-analyst", "equity-pm", "risk-officer", "retail-investor")}


def test_report_is_produced_for_a_well_shaped_field_set():
    report = build_report(HERO, _fields(), _reliabilities())
    assert isinstance(report, CalibrationReport)


def test_expert_fields_pass_the_literature_check():
    """Suppressing everything outside the mask is the shape the literature predicts."""
    report = build_report(HERO, _fields(), _reliabilities())
    for persona_id, check in report.signature_checks.items():
        assert check.passed, f"{persona_id}: {check.reasons}"


def test_the_lay_reader_is_used_as_the_novice_baseline_not_checked_itself():
    report = build_report(HERO, _fields(), _reliabilities())
    assert "retail-investor" not in report.signature_checks


def test_a_flat_expert_field_fails_the_check():
    fields = _fields()
    fields[0] = _field("credit-analyst", _flat())
    report = build_report(HERO, fields, _reliabilities())
    assert not report.signature_checks["credit-analyst"].passed


def test_report_records_every_pairwise_overlap():
    report = build_report(HERO, _fields(), _reliabilities())
    assert len(report.comparisons) == 6  # 4 personas choose 2


def test_report_carries_reliability_for_each_persona():
    report = build_report(HERO, _fields(), _reliabilities())
    assert set(report.reliabilities) == {
        "credit-analyst", "equity-pm", "risk-officer", "retail-investor"
    }


def test_report_overall_pass_requires_every_check_to_pass():
    fields = _fields()
    fields[0] = _field("credit-analyst", _flat())
    assert not build_report(HERO, fields, _reliabilities()).passed


def test_report_overall_pass_requires_usable_reliability():
    weak = {p: reliability_verdict(0.2) for p in
            ("credit-analyst", "equity-pm", "risk-officer", "retail-investor")}
    assert not build_report(HERO, _fields(), weak).passed


def test_report_needs_a_lay_persona_to_serve_as_baseline():
    fields = [f for f in _fields() if f.persona_id != "retail-investor"]
    with pytest.raises(ValueError, match="baseline"):
        build_report(HERO, fields, _reliabilities())


def test_report_renders_as_readable_markdown():
    text = build_report(HERO, _fields(), _reliabilities()).to_markdown()
    assert "credit-analyst" in text
    assert "overlap" in text.lower()


def test_report_markdown_states_the_verdict_plainly():
    fields = _fields()
    fields[0] = _field("credit-analyst", _flat())
    text = build_report(HERO, fields, _reliabilities()).to_markdown()
    assert "FAIL" in text


# --- reliability diagnosis is applied per persona -----------------------------------


def test_a_diffuse_lay_persona_with_low_alpha_does_not_fail_the_run():
    """A novice attending uniformly is correct behaviour, and alpha cannot see it.

    See tests/test_reliability_diagnosis.py for why alpha is uninformative there.
    """
    reliabilities = dict(_reliabilities())
    reliabilities["retail-investor"] = reliability_verdict(0.06)
    assert build_report(HERO, _fields(), reliabilities).passed


def test_a_focused_persona_with_low_alpha_does_fail_the_run():
    """Concentrated attention landing differently each run is genuinely erratic."""
    reliabilities = dict(_reliabilities())
    reliabilities["credit-analyst"] = reliability_verdict(0.06)
    assert not build_report(HERO, _fields(), reliabilities).passed


def test_report_exposes_the_diagnosis_for_each_persona():
    report = build_report(HERO, _fields(), _reliabilities())
    assert set(report.diagnoses) == {
        "credit-analyst", "equity-pm", "risk-officer", "retail-investor"
    }


def test_markdown_explains_a_diffuse_low_alpha_rather_than_just_failing_it():
    reliabilities = dict(_reliabilities())
    reliabilities["retail-investor"] = reliability_verdict(0.06)
    text = build_report(HERO, _fields(), reliabilities).to_markdown()
    assert "diffuse" in text.lower()
