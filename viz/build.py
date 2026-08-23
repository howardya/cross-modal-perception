#!/usr/bin/env python3
"""Inject the calibrated fixture into the page template.

    python3 viz/build.py

The visualization holds no scores of its own — it renders whatever the pipeline
emitted. Keeping the fixture as the single source means re-running the
calibration and rebuilding is the whole update path, and the page can never
drift away from the data it claims to show.

Output is one self-contained file: no build step, no bundler, no network beyond
the Google Fonts stylesheet.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "viz" / "template.html"
FIXTURE = ROOT / "fixtures" / "meridian-q4.json"
OUTPUT = ROOT / "viz" / "dist" / "index.html"

PLACEHOLDER = "/*__FIELD_DATA__*/"


def main() -> int:
    if not FIXTURE.exists():
        print(f"missing fixture: {FIXTURE}", file=sys.stderr)
        print("run the calibration first — see pipeline/README.md", file=sys.stderr)
        return 1

    template = TEMPLATE.read_text()
    if PLACEHOLDER not in template:
        print(f"template has no {PLACEHOLDER} placeholder", file=sys.stderr)
        return 1

    data = json.loads(FIXTURE.read_text())

    # Fail loudly rather than shipping a page that renders half a note.
    n = len(data["stimulus"]["texts"])
    for field in data["fields"]:
        if len(field["units"]) != n:
            print(
                f"fixture is inconsistent: {field['persona_id']} has "
                f"{len(field['units'])} units for {n} clauses",
                file=sys.stderr,
            )
            return 1
    if not data["comparisons"]:
        print("fixture has no comparisons; the readout would be empty", file=sys.stderr)
        return 1

    # separators without spaces keeps the payload compact; the page is one file.
    payload = json.dumps(data, separators=(",", ":"))
    # </script> inside a string literal would close the block early.
    payload = payload.replace("</", "<\\/")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(template.replace(PLACEHOLDER, payload))

    kb = OUTPUT.stat().st_size / 1024
    print(f"built {OUTPUT.relative_to(ROOT)}  ({kb:.0f} KB, {n} clauses, "
          f"{len(data['fields'])} personas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
