"""Everything the report's figures need, computed from the fixtures.

The report began with its figures hand-written, which was fine while the study
had four readers and two documents and would stop being fine the moment either
changed. Adding a fifth reader in particular **re-bases every number in the
study**: lift is measured against the reader average, so one more reader shifts
every existing value. Hand-editing thirty numbers after that is not a plan.

So the figures are generated. `viz/build.py` injects this into
`viz/report.template.html`, exactly as the demo is built from its own fixture,
and adding a reader or a document becomes: score it, rebuild, done.

Prose numbers are still written by hand — they sit inside sentences — but
`tests/test_report_figures.py` asserts them against the fixtures, so a stale one
fails loudly rather than quietly misleading.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from cmp.lift import blind_spots, mirrored_pairs, signatures
from cmp.topics import CATEGORIES, CATEGORY_BLURB, labels_for, topic_lift

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "fixtures"

#: Document order matters: the first is the one the method was tuned on.
DOCUMENTS = [
    ("meridian-q4", "Meridian Logistics"),
    ("aldercroft-h1", "Aldercroft Software"),
    ("whirlpool-q2", "Whirlpool Corporation"),
    ("alamo-q2", "Alamo Group"),
]

#: Documents that did not pass the L1 acceptance check, and for which reader.
#: They stay in the study -- the failure is the result, see docs/calibration.md
#: section 7.6 -- but every figure drawing on them has to say so.
L1_FAILURES = {"whirlpool-q2": ["risk-officer"]}

#: Display order for readers, and the short label the figures use. Adding a
#: reader means adding it here and re-running; nothing else is hard-coded.
READERS = [
    ("credit-analyst", "credit analyst"),
    ("risk-officer", "risk officer"),
    ("equity-pm", "equity PM"),
    ("retail-investor", "retail investor"),
]

TOPIC_LABELS = {
    "debt": "what is owed",
    "cash": "cash & working capital",
    "perform": "how it did",
    "share": "per share",
    "depend": "who it depends on",
    "language": "how it is described",
    "events": "what happened",
}

#: Author prose. Everything else in this module is computed; these four pairs
#: are a human reading of the quotes underneath them, and they live here so that
#: adding a reader is one edit rather than a hunt through the page. A new reader
#: needs an entry here or the build fails loudly.
THEMES = {
    "credit-analyst": {
        "gloss": "reads what is owed",
        "stops": "Stops at anything that is a claim on cash — what is owed, "
                 "when it falls due, what it costs.",
        "walks": "Walks past the story being told about the business.",
    },
    "risk-officer": {
        "gloss": "refuses to read the results",
        "stops": "Stops at reassurance. The only reader that treats a denial as "
                 "information.",
        "walks": "Walks past how the business actually performed.",
    },
    "equity-pm": {
        "gloss": "least settled of the four",
        "stops": "Stops at what a single share is worth — margin, dilution, and "
                 "what has been excluded from the adjusted number.",
        "walks": "Walks past the balance sheet, and past anything that is not a number.",
    },
    "retail-investor": {
        "gloss": "reads how it did",
        "stops": "Stops at headline numbers, firsts and streaks — and at things "
                 "you can picture.",
        "walks": "Walks past the machinery — debt terms, accounting adjustments, "
                 "retention.",
    },
}


def _load(stimulus_id: str) -> dict:
    return json.loads((FIXTURES / f"{stimulus_id}.json").read_text())


def _profile_stability(series: list[list[float]]) -> float | None:
    """How well a reader's topic profile travels across documents.

    The mean Pearson correlation over every pair of documents. With two
    documents that is just the correlation between them, which is what the
    study shipped with and what its published figures quote; with more, it is
    the average agreement between any two readings of the same reader, so one
    document that disagrees with the rest pulls it down rather than being
    silently dropped.

    None below two documents: a profile cannot be shown to travel on the
    strength of the only place it has been seen.
    """
    if len(series) < 2:
        return None
    rs = [
        float(np.corrcoef(series[i], series[j])[0, 1])
        for i in range(len(series))
        for j in range(i + 1, len(series))
    ]
    return float(np.mean(rs))


def build_report_data() -> dict[str, Any]:
    docs = {sid: _load(sid) for sid, _ in DOCUMENTS}
    reader_ids = [pid for pid, _ in READERS]

    present = {f["persona_id"] for f in docs[DOCUMENTS[0][0]]["fields"]}
    missing = set(reader_ids) - present
    if missing:
        raise ValueError(f"fixtures have no field for {sorted(missing)}")
    extra = present - set(reader_ids)
    if extra:
        raise ValueError(
            f"fixtures contain readers not listed in READERS: {sorted(extra)}. "
            f"Add them there so the figures include them."
        )
    unthemed = set(reader_ids) - set(THEMES)
    if unthemed:
        raise ValueError(
            f"no THEMES entry for {sorted(unthemed)}. Every reader needs a prose "
            f"reading of its own signature; see the note above THEMES."
        )

    lifts = {sid: topic_lift(docs[sid]["fields"], labels_for(sid)) for sid, _ in DOCUMENTS}

    # ── the topic profiles ───────────────────────────────────────────────
    profiles = []
    for pid, label in READERS:
        series = [[lifts[sid][pid][c] for c in CATEGORIES] for sid, _ in DOCUMENTS]
        r = _profile_stability(series)
        strongest = CATEGORIES[int(np.argmax(series[0]))]
        weakest = CATEGORIES[int(np.argmin(series[0]))]
        profiles.append(
            {
                "id": pid,
                "label": label,
                "series": series,
                "correlation": r,
                "gloss": THEMES[pid]["gloss"],
                "strongest": TOPIC_LABELS[strongest],
                "weakest": TOPIC_LABELS[weakest],
            }
        )

    # ── signature and blind-spot quotes, one per document ────────────────
    cards = []
    for pid, label in READERS:
        stops, walks = [], []
        for sid, _ in DOCUMENTS:
            texts = docs[sid]["stimulus"]["texts"]
            fields = docs[sid]["fields"]
            top = signatures(fields, pid, k=1)[0]
            bot = blind_spots(fields, pid, k=1)[0]
            stops.append({"lift": round(top.lift * 100, 1), "text": texts[top.index]})
            walks.append({"lift": round(bot.lift * 100, 1), "text": texts[bot.index]})
        cards.append(
            {
                "id": pid,
                "label": label,
                "stops_theme": THEMES[pid]["stops"],
                "walks_theme": THEMES[pid]["walks"],
                "stops": stops,
                "walks": walks,
            }
        )

    # ── sentences one reader owns and another walks past ─────────────────
    mirrors = []
    for sid, title in DOCUMENTS:
        texts = docs[sid]["stimulus"]["texts"]
        for p in mirrored_pairs(docs[sid]["fields"], k=3):
            mirrors.append(
                {
                    "document": title,
                    "text": texts[p.index],
                    "seen_by": dict(READERS)[p.seen_by],
                    "seen": round(p.seen_lift * 100, 1),
                    "missed_by": dict(READERS)[p.missed_by],
                    "missed": round(p.missed_lift * 100, 1),
                }
            )
    mirrors.sort(key=lambda m: m["seen"] - m["missed"], reverse=True)
    mirrors = mirrors[:5]

    # ── pairwise attention, which is O(n^2) in readers ───────────────────
    pairs = []
    hero = docs[DOCUMENTS[0][0]]
    names = dict(READERS)
    for c in hero["comparisons"]:
        a, b = c["personas"]
        pairs.append(
            {
                "a": names.get(a, a),
                "b": names.get(b, b),
                "shared": len(c["shared_top"]),
                "of": c["top_k"],
                "conflicts": len(c["valence_conflicts"]),
            }
        )
    pairs.sort(key=lambda p: p["shared"])

    return {
        "readers": [{"id": p, "label": l} for p, l in READERS],
        "documents": [{"id": s, "title": t} for s, t in DOCUMENTS],
        "topics": [
            {"key": c, "label": TOPIC_LABELS[c], "blurb": CATEGORY_BLURB[c]}
            for c in CATEGORIES
        ],
        "profiles": profiles,
        "cards": cards,
        "mirrors": mirrors,
        "pairs": pairs,
        "scale": {
            "profile_max": 16,
            "mirror_max": 6,
        },
    }


def main() -> int:
    print(json.dumps(build_report_data(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
