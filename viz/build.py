#!/usr/bin/env python3
"""Build both pages from the fixtures.

    python3 viz/build.py

Two pages, same principle: neither holds any scores of its own, so re-scoring
and rebuilding is the entire update path and a page can never drift from the
data it claims to show.

    template.html        + fixtures/meridian-q4.json     -> dist/index.html
    report.template.html + cmp.report_data (all fixtures) -> dist/report.html

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


def _inject(template: Path, placeholder: str, payload: dict, out: Path) -> None:
    text = template.read_text()
    if placeholder not in text:
        raise SystemExit(f"{template.name} has no {placeholder} placeholder")
    blob = json.dumps(payload, separators=(",", ":"))
    # </script> inside a string literal would close the block early.
    blob = blob.replace("</", "<\\/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text.replace(placeholder, blob))


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


def main() -> int:
    build_demo()
    build_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
