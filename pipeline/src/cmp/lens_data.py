"""Everything the lens page needs, as one JSON blob on stdout.

    uv run python -m cmp.lens_data

Same arrangement as `cmp.report_data`: the page holds no scores of its own, and
`viz/build.py` stays free of any dependency on `cmp`. The lens needs one thing
the other pages do not — the persona definitions themselves, because it shows
the viewer whose eyes they are wearing and what that reader is for.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from cmp.personas import FINANCE_PERSONAS

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "fixtures"

#: The constructed hero note first, then the real filings, which show a weaker
#: effect (findings.md 2.5). Same order the chorus uses.
DOCUMENTS = [
    "meridian-q4",
    "aldercroft-h1",
    "whirlpool-q2",
    "alamo-q2",
    "jazz-q2",
]

DEFAULT_DOC = "meridian-q4"
DEFAULT_PERSONA = "credit-analyst"


def persona_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": p.id,
            "label": p.label,
            "mandate": p.mandate,
            "time_horizon": p.time_horizon,
            "loss_function": p.loss_function,
            "reads_for": list(p.reads_for),
            "expert": p.expert,
        }
        for p in FINANCE_PERSONAS
    ]


def build() -> dict[str, Any]:
    documents: dict[str, Any] = {}
    for name in DOCUMENTS:
        raw = json.loads((FIXTURES / f"{name}.json").read_text())
        documents[name] = {
            "id": name,
            "title": raw["stimulus"]["title"],
            "texts": raw["stimulus"]["texts"],
            "fields": raw["fields"],
            # The page marks the clauses where two readers are confidently
            # opposed. Those are measured, not asserted, so they come from the
            # fixture rather than from anything the page decides.
            "comparisons": raw["comparisons"],
            "provenance": raw["provenance"],
        }

    return {
        "personas": persona_payload(),
        "documents": documents,
        "order": DOCUMENTS,
        "default_doc": DEFAULT_DOC,
        "default_persona": DEFAULT_PERSONA,
    }


def main() -> int:
    json.dump(build(), sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
