"""Report which role traits survive changing the document, and which do not.

    uv run python -m cmp.dna

Prints the six traits for every role on both stimuli, and the drift verdict for
each. The verdicts are the point: this decides whether the project has role DNA
or only per-document fingerprints, and it is designed to be able to say no.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cmp.field import PerceptualField
from cmp.signature import TRAITS, signature, trait_drift

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "fixtures"

DOCS = [("hero", "meridian-q4"), ("held-out", "aldercroft-h1")]
SHORT = {
    "credit-analyst": "credit",
    "equity-pm": "equity",
    "risk-officer": "risk",
    "retail-investor": "retail",
}


def _load(name: str) -> dict[str, PerceptualField]:
    raw = json.loads((FIXTURES / f"{name}.json").read_text())
    return {f["persona_id"]: PerceptualField.from_dict(f) for f in raw["fields"]}


def collect() -> dict[str, dict[str, dict[str, float]]]:
    """{doc tag: {trait key: {role: value}}}"""
    out: dict[str, dict[str, dict[str, float]]] = {}
    for tag, name in DOCS:
        fields = _load(name)
        sigs = {pid: signature(f) for pid, f in fields.items()}
        out[tag] = {t.key: {pid: getattr(s, t.key) for pid, s in sigs.items()} for t in TRAITS}
    return out


def main() -> int:
    data = collect()
    a, b = DOCS[0][0], DOCS[1][0]
    roles = list(data[a]["threat"])

    print("ROLE SIGNATURES\n")
    header = f"{'trait':18s}" + "".join(f"{SHORT[r]:>18s}" for r in roles)
    print(header)
    print(f"{'':18s}" + "".join(f"{'hero   held':>18s}" for _ in roles))
    print("-" * len(header))
    for t in TRAITS:
        row = f"{t.label:18s}"
        for r in roles:
            row += f"{data[a][t.key][r]:>10.2f}{data[b][t.key][r]:>8.2f}"
        print(row)

    print("\n\nDOES IT SURVIVE CHANGING THE DOCUMENT?\n")
    print(f"{'trait':18s} {'spread':>7s} {'drift':>7s} {'ratio':>7s}  {'ordering':9s}  verdict")
    print("-" * 76)
    failures = 0
    for t in TRAITS:
        d = trait_drift(data[a][t.key], data[b][t.key])
        order = "holds" if d.same_ordering else "changes"
        if not d.stable:
            failures += 1
        print(
            f"{t.label:18s} {d.spread:7.2f} {d.drift:7.2f} {d.ratio:7.2f}  "
            f"{order:9s}  {d.verdict}"
        )

    print(f"\n{len(TRAITS) - failures} of {len(TRAITS)} traits carry role signal.")
    print()
    print("THE ONE AXIS THAT HOLDS — threat pull, by group")
    for tag, _ in DOCS:
        vals = data[tag]["threat"]
        experts = {r: v for r, v in vals.items() if r != "retail-investor"}
        lay = vals["retail-investor"]
        gap = min(experts.values()) - lay
        print(f"  {tag:9s} professionals {min(experts.values()):+.2f} to "
              f"{max(experts.values()):+.2f}   untrained {lay:+.2f}   gap {gap:+.2f}")
    print("Traits marked prompted=True are dictated by the instructions and are")
    print("a check that they were followed, not a finding:",
          ", ".join(t.label for t in TRAITS if t.prompted))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
