#!/usr/bin/env python3
"""Build both pages from the fixtures.

    python3 viz/build.py

Two pages, same principle: neither holds any scores of its own, so re-scoring
and rebuilding is the entire update path and a page can never drift from the
data it claims to show.

    template.html        + fixtures/meridian-q4.json     -> dist/index.html
    report.template.html + cmp.report_data (all fixtures) -> dist/report.html
    acts/chorus.template.html    + all five fixtures  -> dist/chorus.html
    acts/blindspot.template.html + meridian-q4.json   -> dist/blindspot.html
    acts/eighth.template.html    + meridian-q4.json   -> dist/eighth.html
    acts/collision.template.html + meridian-q4.json   -> dist/collision.html
    lens.template.html   + cmp.lens_data (all fixtures) -> dist/lens.html

Adding a reader or a document means scoring it, listing it in
`cmp.report_data.READERS` or `DOCUMENTS`, and running this. Nothing in either
page needs hand-editing — which matters most for a new reader, since lift is
measured against the reader average and one more reader shifts every existing
number in the study.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIZ = ROOT / "viz"
OUT = VIZ / "dist"
SITE = VIZ / "site"
FIXTURE = ROOT / "fixtures" / "meridian-q4.json"

DEMO_PLACEHOLDER = "/*__FIELD_DATA__*/"
REPORT_PLACEHOLDER = "/*__REPORT_DATA__*/"
ACTS = VIZ / "acts"

# The three single-idea pages. Each takes the same fixtures the demo takes,
# so none of them can drift from the study either.
CHORUS_PLACEHOLDER = "/*__CHORUS_DATA__*/"
BLINDSPOT_PLACEHOLDER = "/*__BLINDSPOT_DATA__*/"
EIGHTH_PLACEHOLDER = "/*__EIGHTH_DATA__*/"
COLLISION_PLACEHOLDER = "/*__COLLISION_DATA__*/"

# The lens is the one page that is also served live, so it needs the persona
# definitions themselves rather than only their scores.
LENS_PLACEHOLDER = "/*__LENS_DATA__*/"

# Document order for the chorus switcher: the constructed hero note first,
# then the real filings, which show a weaker effect (findings.md 2.5).
CHORUS_DOCS = [
    "meridian-q4",
    "aldercroft-h1",
    "whirlpool-q2",
    "alamo-q2",
    "jazz-q2",
]


def _inject(template: Path, placeholder: str, payload: dict, out: Path) -> None:
    text = template.read_text()
    if placeholder not in text:
        raise SystemExit(f"{template.name} has no {placeholder} placeholder")
    blob = json.dumps(payload, separators=(",", ":"))
    # </script> inside a string literal would close the block early.
    blob = blob.replace("</", "<\\/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text.replace(placeholder, blob))


def _load(fixture: Path) -> dict:
    """Read one fixture and refuse it if it cannot be rendered honestly."""
    if not fixture.exists():
        raise SystemExit(f"missing fixture: {fixture}\nsee pipeline/README.md")

    data = json.loads(fixture.read_text())
    n = len(data["stimulus"]["texts"])
    for field in data["fields"]:
        if len(field["units"]) != n:
            raise SystemExit(
                f"{fixture.name} is inconsistent: {field['persona_id']} has "
                f"{len(field['units'])} units for {n} clauses"
            )
        # The pages sort by `order` to recover a reading sequence, so it has to
        # be a real permutation. A duplicate rank would silently drop a clause.
        ranks = sorted(u["order"] for u in field["units"])
        if ranks != list(range(n)):
            raise SystemExit(
                f"{fixture.name}: {field['persona_id']} has a broken order field"
            )
    return data


def build_acts() -> None:
    docs = {d: _load(ROOT / "fixtures" / f"{d}.json") for d in CHORUS_DOCS}
    hero = docs["meridian-q4"]

    _inject(
        ACTS / "chorus.template.html",
        CHORUS_PLACEHOLDER,
        {"docs": docs, "order": CHORUS_DOCS, "default_doc": "meridian-q4"},
        OUT / "chorus.html",
    )
    _inject(ACTS / "blindspot.template.html", BLINDSPOT_PLACEHOLDER, hero,
            OUT / "blindspot.html")
    _inject(ACTS / "eighth.template.html", EIGHTH_PLACEHOLDER, hero,
            OUT / "eighth.html")
    _inject(ACTS / "collision.template.html", COLLISION_PLACEHOLDER, hero,
            OUT / "collision.html")

    for name, extra in (
        ("chorus.html", f"{len(docs)} documents"),
        ("blindspot.html", f"{len(hero['stimulus']['texts'])} clauses"),
        ("eighth.html", f"{len(hero['stimulus']['texts'])} clauses"),
        ("collision.html", f"{len(hero['stimulus']['texts'])} clauses"),
    ):
        kb = (OUT / name).stat().st_size / 1024
        print(f"built viz/dist/{name:<14} ({kb:.0f} KB, {extra}, "
              f"{len(hero['fields'])} readers)")


def build_demo() -> None:
    if not FIXTURE.exists():
        raise SystemExit(f"missing fixture: {FIXTURE}\nsee pipeline/README.md")

    data = json.loads(FIXTURE.read_text())
    n = len(data["stimulus"]["texts"])
    for field in data["fields"]:
        if len(field["units"]) != n:
            raise SystemExit(
                f"fixture is inconsistent: {field['persona_id']} has "
                f"{len(field['units'])} units for {n} clauses"
            )
    if not data["comparisons"]:
        raise SystemExit("fixture has no comparisons; the readout would be empty")

    _inject(VIZ / "template.html", DEMO_PLACEHOLDER, data, OUT / "index.html")
    kb = (OUT / "index.html").stat().st_size / 1024
    print(f"built viz/dist/index.html   ({kb:.0f} KB, {n} clauses, "
          f"{len(data['fields'])} readers)")


def build_report() -> None:
    """The report's figures come from the pipeline, so it is built in the
    pipeline's environment rather than importing cmp from here."""
    result = subprocess.run(
        ["uv", "run", "--quiet", "python", "-m", "cmp.report_data"],
        cwd=ROOT / "pipeline",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"could not build report data:\n{result.stderr.strip()}")

    payload = json.loads(result.stdout)
    _inject(VIZ / "report.template.html", REPORT_PLACEHOLDER, payload, OUT / "report.html")
    kb = (OUT / "report.html").stat().st_size / 1024
    print(f"built viz/dist/report.html  ({kb:.0f} KB, "
          f"{len(payload['readers'])} readers, {len(payload['documents'])} documents, "
          f"{len(payload['topics'])} topics)")


def build_lens() -> None:
    """The lens needs the personas as well as the fixtures, so like the report it
    is built in the pipeline's environment rather than importing cmp from here."""
    result = subprocess.run(
        ["uv", "run", "--quiet", "python", "-m", "cmp.lens_data"],
        cwd=ROOT / "pipeline",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"could not build lens data:\n{result.stderr.strip()}")

    payload = json.loads(result.stdout)
    _inject(VIZ / "lens.template.html", LENS_PLACEHOLDER, payload, OUT / "lens.html")
    kb = (OUT / "lens.html").stat().st_size / 1024
    print(f"built viz/dist/lens.html    ({kb:.0f} KB, "
          f"{len(payload['documents'])} documents, {len(payload['personas'])} readers)")




# ── the hosted copy ──────────────────────────────────────────────────────
# Every page in dist/ is a Claude Artifact *fragment*: no doctype, no <html>,
# <head> or <body>, because the artifact runtime injects that skeleton at
# publish time. That is required there and wrong everywhere else — served raw
# from a web server the pages parse in quirks mode, and with no viewport meta
# every phone lays them out at ~980px and zooms out, so none of the responsive
# breakpoints ever fire.
#
# site/ is the same pages wrapped in the skeleton the artifact runtime would
# have supplied, byte for byte, so the hosted copy renders identically to the
# published one. dist/ stays unwrapped and remains what gets published as an
# artifact. Neither is committed; both are rebuilt from the fixtures.
RESET = (
    ":root{color-scheme:light}"
    "body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;"
    "background:#faf9f5;color:#141413}"
    "img{max-width:100%}"
    "[hidden]:not([hidden=until-found]){display:none!important}"
)


def _wrap(title: str, fragment: str) -> str:
    """Wrap one fragment in a standalone document.

    The fragment keeps its own <title>, which is inert in <body> once the head
    carries one; its <link rel=stylesheet> and <style> work in body in every
    browser. Splitting the fragment instead would need a head/body boundary,
    and report.html has no <main> to split on.
    """
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{title}</title>\n"
        f"<style>{RESET}</style>\n"
        "</head>\n"
        "<body>\n" + fragment + "\n</body>\n</html>\n"
    )


def build_site() -> None:
    pages = sorted(OUT.glob("*.html"))
    if not pages:
        raise SystemExit("no pages in viz/dist; run the builders first")
    SITE.mkdir(parents=True, exist_ok=True)
    for src in pages:
        html = src.read_text()
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        if not m:
            raise SystemExit(f"{src.name} has no <title>; the hosted copy needs one")
        (SITE / src.name).write_text(_wrap(m.group(1).strip(), html))
    # Stop GitHub Pages running the built pages through Jekyll.
    (SITE / ".nojekyll").write_text("")
    kb = sum((SITE / p.name).stat().st_size for p in pages) / 1024
    print(f"wrapped viz/site/      ({len(pages)} pages, {kb:.0f} KB total)")


def main() -> int:
    build_demo()
    build_acts()
    build_report()
    build_lens()
    build_site()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
