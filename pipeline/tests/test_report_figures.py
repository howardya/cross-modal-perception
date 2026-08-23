"""The published report quotes figures; these check it still tells the truth.

`viz/report.html` is the results summary. Unlike `viz/template.html`, its numbers
are written into the prose rather than injected from the fixture, because they
appear inside sentences. That makes it the one artefact in the project that can
silently drift away from the data it describes — exactly the failure the
pipeline/viz split was built to prevent everywhere else.

So the figures are asserted against the fixtures here. If a re-scoring run
changes a number, these fail and the report gets updated with it. A quoted
statistic that no longer matches the data is worse than no statistic.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "viz" / "report.html"
HERO = ROOT / "fixtures" / "meridian-q4.json"
HELD = ROOT / "fixtures" / "aldercroft-h1.json"


@pytest.fixture(scope="module")
def html() -> str:
    return REPORT.read_text()


@pytest.fixture(scope="module")
def hero() -> dict:
    return json.loads(HERO.read_text())


@pytest.fixture(scope="module")
def held() -> dict:
    return json.loads(HELD.read_text())


def _pair(data: dict, a: str, b: str) -> dict:
    for c in data["comparisons"]:
        if {a, b} == set(c["personas"]):
            return c
    raise AssertionError(f"no comparison for {a} and {b}")


def _mean_overlap(data: dict) -> float:
    ov = [c["top_k_overlap"] for c in data["comparisons"]]
    return sum(ov) / len(ov)


def test_the_report_exists():
    assert REPORT.exists(), "viz/report.html is the published results summary"


# --- headline claims ----------------------------------------------------------------


def test_the_zero_of_eight_pair_is_named_correctly(html, hero):
    """The one figure most likely to go stale, and it already did once."""
    zero = [c for c in hero["comparisons"] if not c["shared_top"]]
    assert len(zero) == 1, "expected exactly one pair sharing nothing"
    a, b = zero[0]["personas"]
    assert {a, b} == {"equity-pm", "retail-investor"}
    assert "equity PM · retail investor" in html


def test_every_hero_pair_figure_appears_in_the_report(html, hero):
    for c in hero["comparisons"]:
        shared = len(c["shared_top"])
        assert f"{shared} / {c['top_k']}" in html, f"{c['personas']} -> {shared}"


def test_experts_have_no_valence_conflicts_between_them(html, hero):
    experts = {"credit-analyst", "equity-pm", "risk-officer"}
    for c in hero["comparisons"]:
        if set(c["personas"]) <= experts:
            assert not c["valence_conflicts"], c["personas"]
    assert "Conflicts among experts" in html


def test_reported_alpha_range_matches_both_fixtures(html):
    """0.83–0.97 is quoted in the summary cards."""
    assert "0.83–0.97" in html


def test_mean_overlap_figures_match(html, hero, held):
    assert f"{_mean_overlap(hero):.1%}" == "37.5%"
    assert f"{_mean_overlap(held):.1%}" == "50.0%"
    assert "37.5%" in html
    assert "50.0%" in html


def test_conflict_totals_match(html, hero, held):
    assert sum(len(c["valence_conflicts"]) for c in hero["comparisons"]) == 5
    assert sum(len(c["valence_conflicts"]) for c in held["comparisons"]) == 1


def test_held_out_range_matches(html, held):
    shared = [len(c["shared_top"]) for c in held["comparisons"]]
    assert min(shared) == 3 and max(shared) == 5
    assert "3/8 – 5/8" in html


def test_hero_concentration_figures_match(html, hero):
    by_id = {f["persona_id"]: f for f in hero["fields"]}
    for pid in ("credit-analyst", "risk-officer", "equity-pm", "retail-investor"):
        assert f'{by_id[pid]["concentration"]:.3f}' in html, pid


def test_experts_are_more_concentrated_than_the_lay_reader_in_both(hero, held):
    """The claim the report makes in prose, checked against both fixtures."""
    for data in (hero, held):
        by_id = {f["persona_id"]: f["concentration"] for f in data["fields"]}
        lay = by_id["retail-investor"]
        for pid in ("credit-analyst", "equity-pm", "risk-officer"):
            assert by_id[pid] > lay, (pid, data["stimulus"]["id"])


# --- page hygiene -------------------------------------------------------------------


def test_report_declares_the_human_validation_gap(html):
    """The limits section must survive edits; it is the honest part."""
    assert "No human has validated any of it" in html


def test_report_carries_no_wrapper_tags(html):
    """Artifact publishing supplies doctype, head and body."""
    for tag in ("<!doctype", "<html", "<head>", "<body>"):
        assert tag not in html.lower()


def test_report_has_a_title_in_the_first_8kb(html):
    assert re.search(r"<title>.+</title>", html[:8192])


def test_report_defines_both_theme_palettes(html):
    assert 'prefers-color-scheme: dark' in html
    assert ':root[data-theme="dark"]' in html
    assert ':root:not([data-theme="light"])' in html


def test_report_uses_no_external_resources_beyond_google_fonts(html):
    urls = re.findall(r'https?://[^\s"\'<>)]+', html)
    for u in urls:
        assert "fonts.googleapis.com" in u or "fonts.gstatic.com" in u, u
