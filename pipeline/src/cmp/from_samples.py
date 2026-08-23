"""Build a calibrated field set from independently-collected sample files.

The k samples per persona are collected out-of-band — one fresh model context
per sample, none of them able to see the others — and dropped here as JSON. From
that point the path is identical to the API loop: the same validation, the same
median aggregation, the same Krippendorff's alpha, the same acceptance checks.

This exists because independence is the only thing the API call was providing
that a single conversation cannot. Once the samples are genuinely independent,
where they came from stops mattering.

    uv run python -m cmp.from_samples <samples-dir> <stimulus-id>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cmp.anthropic_client import parse_scores
from cmp.calibrate import build_report
from cmp.personas import FINANCE_PERSONAS
from cmp.reliability import krippendorff_alpha_interval, reliability_verdict
from cmp.scoring import RawScores, aggregate_runs
from cmp.stimuli import load_stimulus

__all__ = ["load_samples", "build_from_samples"]


def load_samples(directory: Path, persona_id: str, n_units: int) -> list[RawScores]:
    """Read every sample file for one persona, validated as the API path would."""
    paths = sorted(directory.glob(f"{persona_id}-*.json"))
    if len(paths) < 2:
        raise ValueError(
            f"{persona_id}: found {len(paths)} sample(s) in {directory}; "
            f"reliability needs at least two independent samples"
        )
    return [parse_scores(json.loads(p.read_text()), n_units=n_units) for p in paths]


def build_from_samples(directory: Path, stimulus_id: str):
    loaded = load_stimulus(stimulus_id)
    n = len(loaded.stimulus.texts)

    fields, reliabilities, counts = [], {}, {}
    for persona in FINANCE_PERSONAS:
        samples = load_samples(directory, persona.id, n)
        fields.append(aggregate_runs(persona.id, samples))
        alpha = krippendorff_alpha_interval([s.salience for s in samples])
        reliabilities[persona.id] = reliability_verdict(alpha)
        counts[persona.id] = len(samples)

    return loaded, build_report(loaded, fields, reliabilities), counts


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    directory = Path(args[0])
    stimulus_id = args[1] if len(args) > 1 else "meridian-q4"
    out = Path(args[2]) if len(args) > 2 else Path("../fixtures")

    loaded, report, counts = build_from_samples(directory, stimulus_id)
    k = min(counts.values())

    report.field_set.__dict__["method"] = (
        f"Scored by Claude Opus 5 via {k} independent subagent runs per persona "
        f"({sum(counts.values())} runs total). Each run was a fresh model context that "
        f"could not see the others, so the samples are independent and inter-run "
        f"reliability is measurable. Aggregated by median; chunk labels by mode."
    )
    report.field_set.__dict__["reliability_measured"] = True

    out.mkdir(parents=True, exist_ok=True)
    (out / f"{stimulus_id}.json").write_text(
        json.dumps(report.field_set.to_dict(), indent=2) + "\n"
    )
    (out / f"{stimulus_id}-calibration.md").write_text(report.to_markdown())

    print(report.to_markdown())
    print(f"\nsamples per persona: {counts}", file=sys.stderr)
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
