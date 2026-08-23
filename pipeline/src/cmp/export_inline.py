"""Write the inline-scored fixture and its report.

    uv run python -m cmp.export_inline meridian-q4-inline

Runs the same acceptance checks as the API path. Where the API path reports a
reliability figure, this reports that reliability was not measurable and why.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cmp.calibrate import build_report
from cmp.inline import load_inline_scores
from cmp.reliability import ReliabilityVerdict


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    name = args[0] if args else "meridian-q4-inline"
    out = Path(args[1]) if len(args) > 1 else Path("../fixtures")

    loaded, field_set = load_inline_scores(name)

    # Reliability is genuinely unmeasurable for inline scoring: samples drawn in
    # one conversation are not independent. A placeholder alpha of 1.0 would be a
    # lie, so the report is told to treat these as unmeasured and the markdown
    # says so in place of a number.
    unmeasured = {
        f.persona_id: ReliabilityVerdict(
            alpha=float("nan"), usable=True, tentative=False,
            summary="Not measurable: inline samples are not independent.",
        )
        for f in field_set.fields
    }

    report = build_report(loaded, field_set.fields, unmeasured)

    out.mkdir(parents=True, exist_ok=True)
    payload = field_set.to_dict()
    field_path = out / f"{loaded.stimulus.id}.json"
    field_path.write_text(json.dumps(payload, indent=2) + "\n")

    markdown = report.to_markdown().replace(
        "## Reliability (agreement of each persona with itself)",
        "## Reliability — NOT MEASURED",
    )
    report_path = out / f"{loaded.stimulus.id}-calibration.md"
    report_path.write_text(markdown)

    print(markdown)
    print(f"\nWrote {field_path}", file=sys.stderr)
    print(f"Wrote {report_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
