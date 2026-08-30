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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIZ = ROOT / "viz"
OUT = VIZ / "dist"
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


def main() -> int:
    build_demo()
    build_acts()
    build_report()
    build_lens()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
