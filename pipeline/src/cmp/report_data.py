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
SAMPLES = ROOT / "pipeline" / "scored"

#: Document order matters: the first is the one the method was tuned on.
DOCUMENTS = [
    ("meridian-q4", "Meridian Logistics"),
    ("aldercroft-h1", "Aldercroft Software"),
    ("whirlpool-q2", "Whirlpool Corporation"),
    ("alamo-q2", "Alamo Group"),
    ("jazz-q2", "Jazz Pharmaceuticals"),
]

#: Documents that did not pass the L1 acceptance check, and for which reader.
#: They stay in the study -- the failure is the result, see docs/calibration.md
#: section 7.6 -- but every figure drawing on them has to say so.
L1_FAILURES = {
    "meridian-q4": ["financial-journalist"],
    "whirlpool-q2": ["risk-officer"],
    "jazz-q2": ["distressed-investor"],
}

#: Display order for readers, and the short label the figures use. Adding a
#: reader means adding it here and re-running; nothing else is hard-coded.
READERS = [
    ("credit-analyst", "credit analyst"),
    ("distressed-investor", "distressed investor"),
    ("risk-officer", "risk officer"),
    ("short-seller", "short seller"),
    ("equity-pm", "equity PM"),
    ("financial-journalist", "financial journalist"),
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
        "gloss": "reads what a share is worth",
        "stops": "Stops at what a single share is worth — margin, dilution, and "
                 "what has been excluded from the adjusted number.",
        "walks": "Walks past the balance sheet, and past anything that is not a number.",
    },
    "distressed-investor": {
        "gloss": "the credit analyst's twin",
        "stops": "Stops at the maturity wall and the collateral — when the money "
                 "falls due, what is left to pay it with, and who gets paid first.",
        "walks": "Walks past how the business is actually trading.",
    },
    "short-seller": {
        "gloss": "least settled of the seven",
        "stops": "Stops where the reported number and the cash part company — "
                 "receivables stretching, spend cut to manufacture a margin, a "
                 "one-off gain holding one up.",
        "walks": "Walks past what is owed and when. The only expert here that does.",
    },
    "financial-journalist": {
        "gloss": "reads what is missing",
        "stops": "Stops at people, incidents and what was said out loud — and at "
                 "the sentence admitting something has not happened yet.",
        "walks": "Walks past the balance sheet entirely.",
    },
    "retail-investor": {
        "gloss": "reads how it did",
        "stops": "Stops at headline numbers, firsts and streaks — and at things "
                 "you can picture.",
        "walks": "Walks past the machinery — debt terms, accounting adjustments, "
                 "retention.",
    },
}


#: The clause the worked example follows from five raw scores to one cell of
#: the DNA table, and the two readers it contrasts. Nothing about the example
#: is special-cased: it is the ordinary pipeline, printed with its working
#: shown. Chosen because the two readers disagree about it as widely as any
#: sentence in the study, and because its topic is the one each of them is
#: defined by -- one for reading it, one for skipping it.
WORKED = {
    "document": "meridian-q4",
    "clause": 12,
    "readers": ["credit-analyst", "retail-investor"],
}


def _load(stimulus_id: str) -> dict:
    return json.loads((FIXTURES / f"{stimulus_id}.json").read_text())


def _runs(stimulus_id: str, persona_id: str, index: int) -> list[float]:
    """What the five blind runs scored one clause, before aggregation.

    The samples are the audit trail behind every median in the fixtures, so
    the worked example reads them rather than restating the aggregate as if
    it were raw.
    """
    directory = SAMPLES / f"sweep-{stimulus_id}"
    paths = sorted(directory.glob(f"{persona_id}-*.json"))
    if not paths:
        raise FileNotFoundError(
            f"no samples for {persona_id} in {directory}; the worked example "
            f"shows the runs behind a median and cannot invent them"
        )
    return [json.loads(p.read_text())["units"][index]["salience"] for p in paths]


def _worked_example(docs: dict, lifts: dict) -> dict[str, Any]:
    """One clause traced end to end: five runs -> median -> share -> lift ->
    topic -> the reader's DNA cell.

    Every value here is recomputed from the fixtures by the same code paths
    the figures use, so the arithmetic on the page cannot drift from the
    arithmetic in the pipeline. Where a step is a one-line calculation the
    reader can check by eye, both operands travel with the result.
    """
    sid = WORKED["document"]
    index = WORKED["clause"]
    doc = docs[sid]
    labels = labels_for(sid)
    topic = labels[index]
    fields = {f["persona_id"]: f for f in doc["fields"]}

    salience = {
        pid: [u["salience"] for u in f["units"]] for pid, f in fields.items()
    }
    totals = {pid: float(sum(v)) for pid, v in salience.items()}
    shares = {pid: salience[pid][index] / totals[pid] for pid in salience}
    mean_share = float(np.mean(list(shares.values())))

    in_topic = [i for i, lab in enumerate(labels) if lab == topic]
    topic_totals = {pid: float(sum(salience[pid][i] for i in in_topic)) for pid in salience}
    topic_shares = {pid: topic_totals[pid] / totals[pid] for pid in salience}
    mean_topic_share = float(np.mean(list(topic_shares.values())))

    names = dict(READERS)
    readers = []
    for pid in WORKED["readers"]:
        runs = _runs(sid, pid, index)
        median = float(np.median(runs))
        if abs(median - salience[pid][index]) > 1e-9:
            raise ValueError(
                f"{pid}: the samples median to {median} but the fixture says "
                f"{salience[pid][index]}; one of the two is stale"
            )
        series = [lifts[s][pid][topic] for s, _ in DOCUMENTS]
        readers.append(
            {
                "id": pid,
                "label": names[pid],
                "runs": runs,
                "median": median,
                "total": round(totals[pid], 2),
                "share": shares[pid] * 100,
                "lift": (shares[pid] - mean_share) * 100,
                "topic_total": round(topic_totals[pid], 2),
                "topic_share": topic_shares[pid] * 100,
                "topic_lift": (topic_shares[pid] - mean_topic_share) * 100,
                "series": series,
                "dna": float(np.mean(series)),
            }
        )

    return {
        "document": dict(DOCUMENTS)[sid],
        "index": index,
        "n": index + 1,
        "of": len(labels),
        "text": doc["stimulus"]["texts"][index],
        "topic": TOPIC_LABELS[topic],
        "topic_count": len(in_topic),
        "mean_share": mean_share * 100,
        "mean_topic_share": mean_topic_share * 100,
        "readers": readers,
    }


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

    # ── reader x topic: every reader's DNA in one figure ─────────────────
    # Mean lift across documents. The per-document bars stay in `profiles`;
    # this is the view that lets seven readers be compared with each other
    # rather than each against itself.
    dna = []
    for pid, label in READERS:
        row = [float(np.mean([lifts[sid][pid][c] for sid, _ in DOCUMENTS]))
               for c in CATEGORIES]
        dna.append({"id": pid, "label": label, "row": row,
                    "strongest": TOPIC_LABELS[CATEGORIES[int(np.argmax(row))]],
                    "weakest": TOPIC_LABELS[CATEGORIES[int(np.argmin(row))]]})

    # ── reader x reader: whose DNA resembles whose ───────────────────────
    # Correlation between the mean topic profiles above. 1.0 means the two
    # readers spend their attention on the same topics in the same
    # proportions; negative means one reads what the other skips.
    order = [d["id"] for d in dna]
    vecs = {d["id"]: d["row"] for d in dna}
    similarity = [
        [1.0 if a == b else round(float(np.corrcoef(vecs[a], vecs[b])[0, 1]), 3)
         for b in order]
        for a in order
    ]
    twins = max(
        ((a, b, similarity[i][j])
         for i, a in enumerate(order) for j, b in enumerate(order) if i < j),
        key=lambda t: t[2])
    opposites = min(
        ((a, b, similarity[i][j])
         for i, a in enumerate(order) for j, b in enumerate(order) if i < j),
        key=lambda t: t[2])

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
        "worked": _worked_example(docs, lifts),
        "documents": [{"id": s, "title": t} for s, t in DOCUMENTS],
        "topics": [
            {"key": c, "label": TOPIC_LABELS[c], "blurb": CATEGORY_BLURB[c]}
            for c in CATEGORIES
        ],
        "profiles": profiles,
        "dna": dna,
        "similarity": {
            "order": order,
            "labels": [dict(READERS)[p] for p in order],
            "matrix": similarity,
            "twins": {"a": dict(READERS)[twins[0]], "b": dict(READERS)[twins[1]],
                      "r": round(twins[2], 2)},
            "opposites": {"a": dict(READERS)[opposites[0]],
                          "b": dict(READERS)[opposites[1]],
                          "r": round(opposites[2], 2)},
        },
        "l1_failures": [
            {"document": dict(DOCUMENTS)[sid], "readers":
             [dict(READERS)[r] for r in rs]}
            for sid, rs in L1_FAILURES.items()
        ],
        "cards": cards,
        "mirrors": mirrors,
        "pairs": pairs,
        "scale": {
            "profile_max": 20,
            "mirror_max": 8,
        },
    }


def main() -> int:
    print(json.dumps(build_report_data(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
