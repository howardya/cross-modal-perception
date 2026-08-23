"""Command line entry point for the calibration run.

    uv run python -m cmp calibrate meridian-q4 --k 5
    uv run python -m cmp calibrate aldercroft-h1 --k 5 --out ../fixtures

Writes the perceptual field JSON that the visualization consumes, plus a
markdown calibration report. Exits non-zero if the run fails the literature
acceptance checks or the reliability threshold, so a bad run cannot quietly
become the fixture the demo ships.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cmp.calibrate import run_calibration
from cmp.stimuli import available_stimuli, load_stimulus


def _calibrate(args: argparse.Namespace) -> int:
    from cmp.anthropic_client import AnthropicScoringClient

    loaded = load_stimulus(args.stimulus)
    n_calls = 4 * args.k
    print(
        f"Scoring {len(loaded.stimulus.texts)} clauses of {loaded.stimulus.title!r} "
        f"as 4 personas, {args.k} samples each ({n_calls} API calls).",
        file=sys.stderr,
    )

    client = AnthropicScoringClient(model=args.model, effort=args.effort)
    report = run_calibration(client, loaded, k=args.k)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    field_path = out / f"{loaded.stimulus.id}.json"
    field_path.write_text(json.dumps(report.field_set.to_dict(), indent=2) + "\n")

    report_path = out / f"{loaded.stimulus.id}-calibration.md"
    report_path.write_text(report.to_markdown())

    print(report.to_markdown())
    print(f"Wrote {field_path}", file=sys.stderr)
    print(f"Wrote {report_path}", file=sys.stderr)

    if not report.passed:
        print(
            "\nRun FAILED the acceptance checks. The fixture was still written so the "
            "failure can be inspected, but it must not be shipped as calibrated.",
            file=sys.stderr,
        )
        return 1
    return 0


def _list(_: argparse.Namespace) -> int:
    for name in available_stimuli():
        loaded = load_stimulus(name)
        print(f"{name:20s} {len(loaded.stimulus.texts):3d} clauses  [{loaded.role}]")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cmp", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("calibrate", help="score a stimulus and check the result")
    run.add_argument("stimulus", help="stimulus id, e.g. meridian-q4")
    run.add_argument("--k", type=int, default=5, help="samples per persona (default 5)")
    run.add_argument("--model", default="claude-opus-5")
    run.add_argument("--effort", default="high")
    run.add_argument("--out", default="../fixtures", help="output directory")
    run.set_defaults(func=_calibrate)

    listing = sub.add_parser("list", help="list available stimuli")
    listing.set_defaults(func=_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
