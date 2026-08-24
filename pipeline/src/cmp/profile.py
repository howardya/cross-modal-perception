"""Print each reader's signature and blind spots, on both documents.

    uv run python -m cmp.profile

Two documents side by side is the point: a theme that appears on only one is a
fact about that document, and a theme that appears on both is a fact about the
reader.
"""

from __future__ import annotations

import json
from pathlib import Path

from cmp.lift import blind_spots, mirrored_pairs, signatures

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "fixtures"
DOCS = [("Meridian Logistics", "meridian-q4"), ("Aldercroft Software", "aldercroft-h1")]
ORDER = ["credit-analyst", "equity-pm", "risk-officer", "retail-investor"]
LABEL = {
    "credit-analyst": "CREDIT ANALYST",
    "equity-pm": "EQUITY PM",
    "risk-officer": "RISK OFFICER",
    "retail-investor": "RETAIL INVESTOR",
}


def load(name: str):
    raw = json.loads((FIXTURES / f"{name}.json").read_text())
    return raw["stimulus"]["texts"], raw["fields"]


def _clip(s: str, n: int = 72) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> int:
    for pid in ORDER:
        print("=" * 92)
        print(LABEL[pid])
        print("=" * 92)
        for title, name in DOCS:
            texts, fields = load(name)
            print(f"\n  {title}")
            print("    stops at:")
            for m in signatures(fields, pid, k=3):
                print(f"      +{m.lift * 100:4.1f}  {_clip(texts[m.index])}")
            print("    walks past:")
            for m in blind_spots(fields, pid, k=3):
                print(f"      {m.lift * 100:5.1f}  {_clip(texts[m.index])}")
        print()

    print("=" * 92)
    print("EVERY BLIND SPOT IS SOMEONE ELSE'S SPECIALISM")
    print("=" * 92)
    for title, name in DOCS:
        texts, fields = load(name)
        print(f"\n  {title}")
        for p in mirrored_pairs(fields, k=4):
            print(f"    {_clip(texts[p.index], 66)}")
            print(
                f"        caught by {LABEL[p.seen_by]:16s} +{p.seen_lift * 100:4.1f}"
                f"   missed by {LABEL[p.missed_by]:16s} {p.missed_lift * 100:5.1f}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
