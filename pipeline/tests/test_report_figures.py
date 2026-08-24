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


# --- the lead figure ----------------------------------------------------------------


def _strip_rows(html: str) -> list[list[int]]:
    """The data-top index lists driving the attention strip, in page order."""
    return [
        [int(n) for n in m.split(",") if n]
        for m in re.findall(r'class="strip-cells"[^>]*data-top="([^"]*)"', html)
    ]


def _consensus(hero: dict) -> set:
    by_id = {f["persona_id"]: set(f["top_attention"]) for f in hero["fields"]}
    return by_id["credit-analyst"] & by_id["equity-pm"] & by_id["risk-officer"]


def test_the_figure_marks_come_from_the_fixture(html, hero):
    """Every filled square must be a real top-8 index, not a typed one."""
    by_id = {f["persona_id"]: f for f in hero["fields"]}
    order = ["credit-analyst", "equity-pm", "risk-officer", "retail-investor"]
    rows = _strip_rows(html)
    assert len(rows) == 4, f"expected four reader rows, found {len(rows)}"
    for pid, marks in zip(order, rows):
        assert sorted(marks) == sorted(by_id[pid]["top_attention"]), pid


def test_every_row_marks_exactly_eight_sentences(html):
    for marks in _strip_rows(html):
        assert len(marks) == 8


def test_the_caret_row_is_the_real_expert_consensus(html, hero):
    m = re.search(r'strip-cells--caret"[^>]*data-top="([^"]*)"', html)
    assert m, "caret row missing"
    assert sorted(int(n) for n in m.group(1).split(",")) == sorted(_consensus(hero))


def test_the_untrained_reader_shares_none_of_the_consensus(hero):
    """The claim the figure is built to make."""
    by_id = {f["persona_id"]: set(f["top_attention"]) for f in hero["fields"]}
    consensus = _consensus(hero)
    assert consensus, "experts share nothing, so the figure has no claim to make"
    assert not (consensus & by_id["retail-investor"])


def test_the_two_ticked_sentences_are_real_conflicts(html, hero):
    cold = int(re.search(r'data-cold="(\d+)"', html).group(1))
    warm = int(re.search(r'data-warm="(\d+)"', html).group(1))
    conflicts = {i for c in hero["comparisons"] for i in c["valence_conflicts"]}
    assert cold in conflicts, f"clause {cold} is not a valence conflict"
    assert warm in conflicts, f"clause {warm} is not a valence conflict"


def test_the_cold_tick_is_where_every_professional_dwells(html, hero):
    cold = int(re.search(r'data-cold="(\d+)"', html).group(1))
    by_id = {f["persona_id"]: set(f["top_attention"]) for f in hero["fields"]}
    for pid in ("credit-analyst", "equity-pm", "risk-officer"):
        assert cold in by_id[pid], pid
    assert cold not in by_id["retail-investor"]


def test_the_warm_tick_is_where_the_untrained_reader_dwells(html, hero):
    warm = int(re.search(r'data-warm="(\d+)"', html).group(1))
    by_id = {f["persona_id"]: set(f["top_attention"]) for f in hero["fields"]}
    assert warm in by_id["retail-investor"]


def test_the_two_ticked_sentences_are_adjacent(html):
    """The caption says 'adjacent sentences'; it must stay true."""
    cold = int(re.search(r'data-cold="(\d+)"', html).group(1))
    warm = int(re.search(r'data-warm="(\d+)"', html).group(1))
    assert abs(cold - warm) == 1


def test_the_ticked_sentences_read_in_opposite_directions(html, hero):
    cold = int(re.search(r'data-cold="(\d+)"', html).group(1))
    warm = int(re.search(r'data-warm="(\d+)"', html).group(1))
    by_id = {f["persona_id"]: f for f in hero["fields"]}
    for pid in ("credit-analyst", "equity-pm", "risk-officer"):
        assert by_id[pid]["units"][cold]["valence"] < 0, pid
    assert by_id["retail-investor"]["units"][warm]["valence"] > 0


def test_the_ghost_cells_mark_the_consensus_the_lay_reader_misses(html, hero):
    """The figure draws the absence, so the absence must be the real one."""
    m = re.search(r'data-ghost="([^"]*)"', html)
    assert m, "ghost cells missing from the untrained reader's row"
    ghost = sorted(int(n) for n in m.group(1).split(",") if n)
    assert ghost == sorted(_consensus(hero))
    by_id = {f["persona_id"]: set(f["top_attention"]) for f in hero["fields"]}
    assert not (set(ghost) & by_id["retail-investor"]), (
        "a ghost cell would be drawn over a filled one"
    )


# --- the signature section ------------------------------------------------------------


def _lift_of(name: str, persona: str, needle: str) -> float:
    """Recompute the lift the page quotes, from the fixture, in points."""
    from cmp.lift import attention_lift
    from cmp.profile import load

    texts, fields = load(name)
    matches = [i for i, t in enumerate(texts) if needle in t]
    assert len(matches) == 1, f"{needle!r} matched {len(matches)} sentences in {name}"
    return attention_lift(fields)[persona][matches[0]] * 100


QUOTED = [
    # (document, reader, sentence fragment, figure printed on the page)
    ("meridian-q4", "credit-analyst", "Net leverage stands at 4.1x", 2.2),
    ("aldercroft-h1", "credit-analyst", "holds $420m of cash", 4.8),
    ("meridian-q4", "credit-analyst", "renewal pipeline as constructive", -1.4),
    ("meridian-q4", "equity-pm", "Gross margin declined 240", 1.9),
    ("aldercroft-h1", "equity-pm", "Diluted share count increased", 5.6),
    ("aldercroft-h1", "equity-pm", "disclosed a security incident", -4.3),
    ("meridian-q4", "risk-officer", "three largest customers", 2.0),
    ("aldercroft-h1", "risk-officer", "No customer data was exfiltrated", 5.1),
    ("aldercroft-h1", "risk-officer", "first positive operating income", -4.1),
    ("meridian-q4", "retail-investor", "eighth consecutive quarter", 3.1),
    ("aldercroft-h1", "retail-investor", "first positive operating income", 3.3),
    ("meridian-q4", "retail-investor", "agreed an amendment with its lending", -4.1),
    ("aldercroft-h1", "retail-investor", "Share-based compensation", -3.0),
]


@pytest.mark.parametrize("doc,persona,needle,printed", QUOTED)
def test_every_quoted_lift_matches_the_fixture(doc, persona, needle, printed):
    assert _lift_of(doc, persona, needle) == pytest.approx(printed, abs=0.06)


@pytest.mark.parametrize("doc,persona,needle,printed", QUOTED)
def test_every_quoted_sentence_appears_on_the_page(html, doc, persona, needle, printed):
    assert needle in html, needle


def test_the_risk_officer_really_does_stop_at_the_reassurance(html):
    """The page's boldest claim, so it is the one most worth pinning."""
    from cmp.lift import signatures
    from cmp.profile import load

    texts, fields = load("aldercroft-h1")
    top = [texts[m.index] for m in signatures(fields, "risk-officer", k=2)]
    assert any("No customer data was exfiltrated" in t for t in top)
    assert "treats a denial as information" in html


def test_the_risk_officer_is_blind_to_performance(html):
    from cmp.lift import blind_spots
    from cmp.profile import load

    for doc, needle in (
        ("meridian-q4", "EBITDA"),
        ("aldercroft-h1", "operating income"),
    ):
        texts, fields = load(doc)
        worst = [texts[m.index] for m in blind_spots(fields, "risk-officer", k=2)]
        assert any(needle in t for t in worst), doc


def test_the_covenant_amendment_is_the_untrained_readers_deepest_blind_spot(html):
    """The claim the mirrored figure is built around.

    Written first as "deepest in the entire dataset", which was wrong — the
    equity PM misses the security incident by 4.3 points against this 4.1. The
    true and still striking claim is scoped to the untrained reader.
    """
    from cmp.lift import attention_lift
    from cmp.profile import load

    worst = None
    for name in ("meridian-q4", "aldercroft-h1"):
        texts, fields = load(name)
        for i, v in enumerate(attention_lift(fields)["retail-investor"]):
            if worst is None or v < worst[0]:
                worst = (v, texts[i])
    value, text = worst
    assert "amendment with its lending syndicate" in text
    assert "deepest blind spot anywhere in this" in html


# --- the mirrored-sentence figure ----------------------------------------------------


def _mirror_rows(html: str):
    return re.findall(
        r'data-seen="(-?[\d.]+)" data-missed="(-?[\d.]+)"\s+'
        r'data-seen-by="([^"]+)" data-missed-by="([^"]+)"',
        html,
    )


def test_the_mirror_figure_has_rows(html):
    assert len(_mirror_rows(html)) == 5


def test_every_mirror_row_is_caught_by_one_and_missed_by_another(html):
    for seen, missed, seen_by, missed_by in _mirror_rows(html):
        assert float(seen) > 0 > float(missed)
        assert seen_by != missed_by


def test_no_mirror_bar_overflows_its_scale(html):
    """MIRROR_MAX in the page is 6; a larger value would silently clip."""
    for seen, missed, _, _ in _mirror_rows(html):
        assert abs(float(seen)) <= 6
        assert abs(float(missed)) <= 6
