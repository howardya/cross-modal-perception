"""The report is generated; these tests hold it to the fixtures.

Three seams, tested separately:

1. **The data** (`cmp.report_data`) — every number the figures draw must be
   derivable from `fixtures/`, not typed.
2. **The template** (`viz/report.template.html`) — its prose makes claims with
   numbers in them. Prose cannot be generated, so each claim is asserted here
   and a stale one fails loudly rather than quietly misleading.
3. **The build** (`viz/dist/report.html`) — the placeholder is really filled and
   the page is publishable as an artifact.

The report used to have its figures hand-written. It stopped being safe to do
that the moment the study could grow: adding a reader re-bases every lift in the
study, because lift is measured against the reader average.
"""

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pytest

from cmp.lift import attention_lift, blind_spots, signatures
from cmp.report_data import (
    DOCUMENTS,
    READERS,
    THEMES,
    WORKED,
    _profile_stability,
    build_report_data,
)
from cmp.topics import CATEGORIES, labels_for, topic_lift

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "viz" / "report.template.html"
BUILT = ROOT / "viz" / "dist" / "report.html"
FIXTURES = ROOT / "fixtures"


@pytest.fixture(scope="module")
def data():
    return build_report_data()


@pytest.fixture(scope="module")
def template() -> str:
    return TEMPLATE.read_text()


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text())


def _lift_of(name: str, persona: str, needle: str) -> float:
    d = _fixture(name)
    matches = [i for i, t in enumerate(d["stimulus"]["texts"]) if needle in t]
    assert len(matches) == 1, f"{needle!r} matched {len(matches)} sentences in {name}"
    return attention_lift(d["fields"])[persona][matches[0]] * 100


# ── 1. the data ──────────────────────────────────────────────────────────────


def test_every_reader_has_a_profile(data):
    assert [p["id"] for p in data["profiles"]] == [r for r, _ in READERS]


def test_every_profile_covers_every_topic_on_every_document(data):
    for p in data["profiles"]:
        assert len(p["series"]) == len(DOCUMENTS)
        for series in p["series"]:
            assert len(series) == len(CATEGORIES)


def test_plotted_profile_values_come_from_the_fixtures(data):
    for doc_i, (sid, _) in enumerate(DOCUMENTS):
        d = _fixture(sid)
        lift = topic_lift(d["fields"], labels_for(sid))
        for p in data["profiles"]:
            expected = [lift[p["id"]][c] for c in CATEGORIES]
            assert p["series"][doc_i] == pytest.approx(expected), (p["id"], sid)


def test_no_profile_bar_overflows_the_figure_scale(data):
    limit = data["scale"]["profile_max"]
    for p in data["profiles"]:
        for series in p["series"]:
            assert max(abs(v) for v in series) <= limit, p["id"]


def test_no_mirror_bar_overflows_the_figure_scale(data):
    limit = data["scale"]["mirror_max"]
    for m in data["mirrors"]:
        assert abs(m["seen"]) <= limit and abs(m["missed"]) <= limit, m["text"][:40]


def test_signature_quotes_are_the_real_extremes(data):
    for card in data["cards"]:
        for doc_i, (sid, _) in enumerate(DOCUMENTS):
            d = _fixture(sid)
            texts = d["stimulus"]["texts"]
            top = signatures(d["fields"], card["id"], k=1)[0]
            bot = blind_spots(d["fields"], card["id"], k=1)[0]
            assert card["stops"][doc_i]["text"] == texts[top.index]
            assert card["walks"][doc_i]["text"] == texts[bot.index]


def test_every_mirror_is_caught_by_one_reader_and_missed_by_another(data):
    for m in data["mirrors"]:
        assert m["seen"] > 0 > m["missed"]
        assert m["seen_by"] != m["missed_by"]


def test_pair_table_covers_every_combination(data):
    n = len(READERS)
    assert len(data["pairs"]) == n * (n - 1) // 2


def test_adding_a_reader_to_the_fixtures_without_listing_it_fails_loudly():
    """The trap this whole refactor exists to prevent."""
    from cmp import report_data

    original = report_data.READERS
    try:
        report_data.READERS = [r for r in original if r[0] != "risk-officer"]
        with pytest.raises(ValueError, match="not listed in READERS"):
            report_data.build_report_data()
    finally:
        report_data.READERS = original


def test_a_reader_without_a_prose_theme_fails_loudly():
    from cmp import report_data

    original = report_data.THEMES
    try:
        report_data.THEMES = {k: v for k, v in original.items() if k != "equity-pm"}
        with pytest.raises(ValueError, match="no THEMES entry"):
            report_data.build_report_data()
    finally:
        report_data.THEMES = original


# ── 2. the template's prose claims ───────────────────────────────────────────


QUOTED = [
    ("meridian-q4", "credit-analyst", "Net leverage stands at 4.1x", 1.9),
    ("aldercroft-h1", "credit-analyst", "holds $420m of cash", 5.2),
    ("meridian-q4", "equity-pm", "Gross margin declined 240", 2.3),
    ("aldercroft-h1", "equity-pm", "Diluted share count increased", 6.5),
    ("meridian-q4", "risk-officer", "three largest customers", 1.9),
    ("aldercroft-h1", "risk-officer", "No customer data was exfiltrated", 4.5),
    ("aldercroft-h1", "risk-officer", "first positive operating income", -5.1),
    ("meridian-q4", "retail-investor", "eighth consecutive quarter", 3.6),
    ("meridian-q4", "retail-investor", "agreed an amendment with its lending", -4.6),
]


@pytest.mark.parametrize("doc,persona,needle,printed", QUOTED)
def test_figures_quoted_in_prose_still_match_the_fixtures(doc, persona, needle, printed):
    assert _lift_of(doc, persona, needle) == pytest.approx(printed, abs=0.06)


def test_the_mirror_the_caption_claims_is_real(template):
    """Three of the four legs survived the seven-reader re-base; the fourth
    did not, and the caption now says which. The credit analyst's own deepest
    topic on the hero note is `events`, not `perform` -- adding three readers
    who ignore what happened lifted the average there and took the credit
    analyst's floor with it."""
    hero = topic_lift(_fixture("meridian-q4")["fields"], labels_for("meridian-q4"))
    credit, retail = hero["credit-analyst"], hero["retail-investor"]
    assert max(credit, key=credit.get) == "debt"
    assert max(retail, key=retail.get) == "perform"
    assert min(retail, key=retail.get) == "debt"
    assert min(credit, key=credit.get) != "perform"
    assert "half of that mirror" in template


def test_the_risk_officer_dips_on_performance_on_most_documents(template):
    """Held on all documents at four readers. At seven it holds on four of the
    five -- whirlpool-q2 is the exception, where its deepest topic is `share`.
    The claim is kept and the count is stated rather than rounded up."""
    dips = [sid for sid, _ in DOCUMENTS
            if min(l := topic_lift(_fixture(sid)["fields"], labels_for(sid))["risk-officer"],
                   key=l.get) == "perform"]
    assert len(dips) == 4, dips
    assert "four of the five" in template
    assert "signature is an absence" in template


def test_the_page_names_the_weakest_profile_as_weakest(data, template):
    rs = {p["id"]: p["correlation"] for p in data["profiles"]}
    weakest = min(rs, key=rs.get)
    assert weakest == "short-seller"
    assert THEMES[weakest]["gloss"] == "least settled of the seven"
    assert "not yet established" in template


def test_the_risk_officer_really_does_stop_at_the_reassurance():
    """The page's boldest claim. It lives in THEMES rather than the template,
    because the card prose travels with the data now."""
    d = _fixture("aldercroft-h1")
    top = [d["stimulus"]["texts"][m.index]
           for m in signatures(d["fields"], "risk-officer", k=2)]
    assert any("No customer data was exfiltrated" in t for t in top)
    assert "treats a denial as information" in THEMES["risk-officer"]["stops"]


def test_the_cash_flow_line_is_the_untrained_readers_deepest_blind_spot(template):
    worst = None
    for sid, _ in DOCUMENTS:
        d = _fixture(sid)
        for i, v in enumerate(attention_lift(d["fields"])["retail-investor"]):
            if worst is None or v < worst[0]:
                worst = (v, d["stimulus"]["texts"][i])
    assert "cash flow provided by operations was $22.7 million" in worst[1]
    assert "deepest blind spot anywhere in this" in template


def _visible(html: str) -> str:
    """The page's prose, with style and script blocks removed.

    Searching the whole file for a bare "0.50" matches CSS font sizes, unrelated
    statistics and negative valences -- which is how this test passed unchanged
    while every correlation it checks had moved. Correlations are written signed
    in the prose, so the signed form is what gets asserted.
    """
    return re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S | re.I)


def test_the_profile_correlations_quoted_in_prose_are_right(data, template):
    prose = _visible(template)
    for p in data["profiles"]:
        assert f"{p['correlation']:+.2f}" in prose, (p["id"], p["correlation"])


def test_the_correlation_guard_would_notice_a_stale_figure(data, template):
    """The guard above is only worth having if it fails when the prose is
    wrong. A value no profile has must not be found."""
    prose = _visible(template)
    absent = {f"{p['correlation']:+.2f}" for p in data["profiles"]}
    assert "+0.99" not in absent
    assert "+0.99" not in prose


# ── 2b. the worked example ───────────────────────────────────────────────────
# The example on the page exists to let a reader check the arithmetic by hand.
# It is only worth having if the numbers printed beside each step are the ones
# the pipeline actually used, so each rung is asserted against the function
# that computes that same quantity for the figures.


def _worked(data):
    return data["worked"]


def test_worked_example_quotes_the_real_sentence(data):
    w = _worked(data)
    d = _fixture(WORKED["document"])
    assert w["text"] == d["stimulus"]["texts"][WORKED["clause"]]
    assert w["n"] == WORKED["clause"] + 1
    assert w["of"] == len(d["stimulus"]["texts"])
    assert w["topic_count"] == labels_for(WORKED["document"]).count(
        labels_for(WORKED["document"])[WORKED["clause"]]
    )


def test_worked_example_median_is_the_score_in_the_fixture(data):
    """Step a shows five raw runs and a median. If that median were not the
    number the fixture carries, every step below it would be a fiction."""
    w = _worked(data)
    units = {f["persona_id"]: f["units"] for f in _fixture(WORKED["document"])["fields"]}
    for r in w["readers"]:
        assert r["median"] == pytest.approx(np.median(r["runs"]))
        assert r["median"] == pytest.approx(units[r["id"]][WORKED["clause"]]["salience"])


def test_worked_example_share_and_lift_are_the_pipelines_own(data):
    w = _worked(data)
    d = _fixture(WORKED["document"])
    lift = attention_lift(d["fields"])
    totals = {
        f["persona_id"]: sum(u["salience"] for u in f["units"]) for f in d["fields"]
    }
    for r in w["readers"]:
        assert r["total"] == pytest.approx(totals[r["id"]], abs=5e-3)
        assert r["share"] == pytest.approx(r["median"] / totals[r["id"]] * 100)
        assert r["lift"] == pytest.approx(lift[r["id"]][WORKED["clause"]] * 100)


def test_worked_example_topic_step_matches_topic_lift(data):
    w = _worked(data)
    sid = WORKED["document"]
    topic = labels_for(sid)[WORKED["clause"]]
    expected = topic_lift(_fixture(sid)["fields"], labels_for(sid))
    for r in w["readers"]:
        assert r["topic_lift"] == pytest.approx(expected[r["id"]][topic])
        assert r["topic_share"] - w["mean_topic_share"] == pytest.approx(r["topic_lift"])


def test_worked_example_lands_on_the_cell_of_the_dna_table_it_claims(data):
    """The last arithmetic step says the average of the five documents *is* a
    cell of the table further down the page. That is the claim to protect."""
    w = _worked(data)
    sid = WORKED["document"]
    topic = labels_for(sid)[WORKED["clause"]]
    column = CATEGORIES.index(topic)
    rows = {r["id"]: r["row"] for r in data["dna"]}
    for r in w["readers"]:
        assert len(r["series"]) == len(DOCUMENTS)
        assert r["dna"] == pytest.approx(np.mean(r["series"]))
        assert r["dna"] == pytest.approx(rows[r["id"]][column])


def test_worked_example_contrasts_two_different_readers(data):
    w = _worked(data)
    ids = [r["id"] for r in w["readers"]]
    assert len(set(ids)) == len(ids) == 2
    listed = {pid for pid, _ in READERS}
    assert set(ids) <= listed


def test_a_stale_sample_directory_fails_loudly(monkeypatch):
    """The samples and the fixtures are two files that can disagree. If they
    ever do, the page must not quietly print a median nothing produced."""
    from cmp import report_data

    monkeypatch.setattr(report_data, "_runs", lambda *a, **k: [0.01, 0.02, 0.03])
    with pytest.raises(ValueError, match="stale"):
        report_data.build_report_data()


def test_the_page_asks_for_every_worked_value_it_is_given(data, template):
    """Each rung of the ladder is filled by the script from the payload. A
    step present in the markup with no calculation behind it would render as
    an empty box."""
    for key in re.findall(r'data-wk-calc="([a-z]+)"', template):
        assert key in ("runs", "share", "lift", "topic", "dna", "corr"), key
    for key in re.findall(r'data-wk="([a-z_]+)"', template):
        assert key in _worked(data), key
    assert re.search(r'data-wk-calc="runs"', template)


# ── 3. page hygiene and the build ────────────────────────────────────────────


def test_template_carries_the_data_placeholder(template):
    assert "/*__REPORT_DATA__*/" in template


def test_template_has_no_wrapper_tags(template):
    for tag in ("<!doctype", "<html", "<head>", "<body>"):
        assert tag not in template.lower()


def test_template_has_a_title_in_the_first_8kb(template):
    assert re.search(r"<title>.+</title>", template[:8192])


def test_template_defines_both_theme_palettes(template):
    assert "prefers-color-scheme: dark" in template
    assert ':root[data-theme="dark"]' in template
    assert ':root:not([data-theme="light"])' in template


def test_template_uses_no_external_resources_beyond_google_fonts(template):
    for u in re.findall(r'https?://[^\s"\'<>)]+', template):
        assert "fonts.googleapis.com" in u or "fonts.gstatic.com" in u, u


def test_the_build_fills_the_placeholder():
    subprocess.run(
        ["python3", str(ROOT / "viz" / "build.py")], cwd=ROOT, check=True,
        capture_output=True,
    )
    built = BUILT.read_text()
    assert "/*__REPORT_DATA__*/" not in built
    assert '"profiles"' in built


def test_the_built_page_carries_every_reader():
    built = BUILT.read_text()
    for _, label in READERS:
        assert label in built, label


# ── 4. profile stability generalises past two documents ──────────────────────


def test_profile_stability_over_two_documents_is_plain_correlation():
    """The study shipped with two documents and quotes four correlations. The
    N-document form must not move them, or Phase 0 has silently rewritten
    published numbers."""
    a = [1.0, -2.0, 3.0, 0.5, -1.5, 2.0, -0.5]
    b = [1.2, -1.8, 2.5, 0.1, -1.0, 2.4, -0.2]
    assert _profile_stability([a, b]) == pytest.approx(float(np.corrcoef(a, b)[0, 1]))


def test_profile_stability_is_the_mean_over_every_document_pair():
    a = [1.0, -2.0, 3.0, 0.5, -1.5, 2.0, -0.5]
    b = [1.2, -1.8, 2.5, 0.1, -1.0, 2.4, -0.2]
    c = [-1.0, 2.0, -3.0, -0.5, 1.5, -2.0, 0.5]
    expected = np.mean([
        np.corrcoef(a, b)[0, 1],
        np.corrcoef(a, c)[0, 1],
        np.corrcoef(b, c)[0, 1],
    ])
    assert _profile_stability([a, b, c]) == pytest.approx(float(expected))


def test_profile_stability_of_a_single_document_is_undefined():
    """One document cannot evidence that a profile travels."""
    assert _profile_stability([[1.0, -2.0, 3.0, 0.5, -1.5, 2.0, -0.5]]) is None
