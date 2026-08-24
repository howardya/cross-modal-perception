"""Attention by topic: the reader profile that travels between documents.

An earlier trait, *reading position*, failed the stability test — and failed it
for an instructive reason. Its axis was position in one particular document, so
"the professionals read the middle" was a fact about that page's layout, not
about the readers.

Topic fixes the axis. "What is owed" exists in any filing, so a profile built
over topics can be computed on a page a reader has never seen and lined up
against one it has. Three of the four readers keep their shape when that is done
(correlations +0.90, +0.79, +0.78; the equity PM is weaker at +0.54).

Labels live in `stimuli/topics.json`, assigned from each sentence alone before
any score was consulted. They are an author taxonomy and the file says so. The
check on whether the taxonomy is doing real work rather than encoding the answer
is that the profiles survive a change of document — an arbitrary labelling would
not.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

import numpy as np

__all__ = [
    "CATEGORIES",
    "CATEGORY_BLURB",
    "labels_for",
    "profile_shape",
    "topic_lift",
    "topic_share",
]

TOPICS_FILE = Path(__file__).resolve().parents[2] / "stimuli" / "topics.json"

#: Fixed order. Every profile is reported in it, so shapes can be compared by eye.
CATEGORIES = ["debt", "cash", "perform", "share", "depend", "language", "events"]


@lru_cache(maxsize=1)
def _raw() -> dict:
    return json.loads(TOPICS_FILE.read_text())


CATEGORY_BLURB: dict[str, str] = _raw()["categories"]


def labels_for(stimulus_id: str) -> list[str]:
    """The per-sentence topic labels for one stimulus."""
    stimuli = _raw()["stimuli"]
    if stimulus_id not in stimuli:
        raise KeyError(f"no topic labels for {stimulus_id!r}; have {sorted(stimuli)}")
    return list(stimuli[stimulus_id])


def _salience(reader: Mapping) -> list[float]:
    if "salience" in reader:
        return list(reader["salience"])
    return [u["salience"] for u in reader["units"]]


def topic_share(
    readers: Sequence[Mapping], labels: Sequence[str]
) -> dict[str, dict[str, float]]:
    """Each reader's attention as a share, grouped by what the sentence is about."""
    out: dict[str, dict[str, float]] = {}
    for r in readers:
        s = np.asarray(_salience(r), dtype=float)
        if len(s) != len(labels):
            raise ValueError(
                f"need one label per sentence: {len(labels)} labels for {len(s)} sentences"
            )
        total = s.sum()
        if total <= 0:
            raise ValueError(f"reader {r['persona_id']!r} attends to nothing")
        s = s / total
        out[r["persona_id"]] = {
            c: float(sum(s[i] for i, lab in enumerate(labels) if lab == c))
            for c in CATEGORIES
        }
    return out


def topic_lift(
    readers: Sequence[Mapping], labels: Sequence[str]
) -> dict[str, dict[str, float]]:
    """Share minus the average share across readers, in percentage points.

    Positive means this reader spends more of their attention on that topic than
    the others do — which is the readable version of a signature, since raw share
    is dominated by how many sentences a document happens to devote to each topic.
    """
    share = topic_share(readers, labels)
    ids = list(share)
    mean = {c: float(np.mean([share[p][c] for p in ids])) for c in CATEGORIES}
    return {
        p: {c: (share[p][c] - mean[c]) * 100 for c in CATEGORIES} for p in ids
    }


def profile_shape(lift: Mapping[str, float]) -> list[float]:
    """One reader's lift as a vector in the fixed category order."""
    return [lift[c] for c in CATEGORIES]
