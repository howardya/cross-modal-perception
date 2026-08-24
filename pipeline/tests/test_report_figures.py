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
from cmp.report_data import DOCUMENTS, READERS, THEMES, build_report_data
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
    ("meridian-q4", "credit-analyst", "Net leverage stands at 4.1x", 2.2),
    ("aldercroft-h1", "credit-analyst", "holds $420m of cash", 4.8),
    ("meridian-q4", "equity-pm", "Gross margin declined 240", 1.9),
    ("aldercroft-h1", "equity-pm", "Diluted share count increased", 5.6),
    ("meridian-q4", "risk-officer", "three largest customers", 2.0),
    ("aldercroft-h1", "risk-officer", "No customer data was exfiltrated", 5.1),
    ("aldercroft-h1", "risk-officer", "first positive operating income", -4.1),
    ("meridian-q4", "retail-investor", "eighth consecutive quarter", 3.1),
    ("meridian-q4", "retail-investor", "agreed an amendment with its lending", -4.1),
]


@pytest.mark.parametrize("doc,persona,needle,printed", QUOTED)
def test_figures_quoted_in_prose_still_match_the_fixtures(doc, persona, needle, printed):
    assert _lift_of(doc, persona, needle) == pytest.approx(printed, abs=0.06)


def test_the_mirror_the_caption_claims_is_real(template):
    hero = topic_lift(_fixture("meridian-q4")["fields"], labels_for("meridian-q4"))
    debt, perform = "debt", "perform"
    credit, retail = hero["credit-analyst"], hero["retail-investor"]
    assert max(credit, key=credit.get) == debt
    assert min(credit, key=credit.get) == perform
    assert max(retail, key=retail.get) == perform
    assert min(retail, key=retail.get) == debt
    assert "photographic negatives" in template


def test_the_risk_officer_dips_on_performance_in_both_documents(template):
    for sid, _ in DOCUMENTS:
        lift = topic_lift(_fixture(sid)["fields"], labels_for(sid))["risk-officer"]
        assert min(lift, key=lift.get) == "perform", sid
    assert "signature is an absence" in template


def test_the_page_names_the_weakest_profile_as_weakest(data, template):
    rs = {p["id"]: p["correlation"] for p in data["profiles"]}
    weakest = min(rs, key=rs.get)
    assert weakest == "equity-pm"
    assert THEMES[weakest]["gloss"] == "least settled of the four"
    assert "not yet established" in template


def test_the_risk_officer_really_does_stop_at_the_reassurance():
    """The page's boldest claim. It lives in THEMES rather than the template,
    because the card prose travels with the data now."""
    d = _fixture("aldercroft-h1")
    top = [d["stimulus"]["texts"][m.index]
           for m in signatures(d["fields"], "risk-officer", k=2)]
    assert any("No customer data was exfiltrated" in t for t in top)
    assert "treats a denial as information" in THEMES["risk-officer"]["stops"]


def test_the_covenant_amendment_is_the_untrained_readers_deepest_blind_spot(template):
    worst = None
    for sid, _ in DOCUMENTS:
        d = _fixture(sid)
        for i, v in enumerate(attention_lift(d["fields"])["retail-investor"]):
            if worst is None or v < worst[0]:
                worst = (v, d["stimulus"]["texts"][i])
    assert "amendment with its lending syndicate" in worst[1]
    assert "deepest blind spot anywhere in this" in template


def test_the_profile_correlations_quoted_in_prose_are_right(data, template):
    rs = sorted((p["correlation"] for p in data["profiles"]), reverse=True)
    for r in rs:
        assert f"{r:+.2f}".replace("+", "") in template, r


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
