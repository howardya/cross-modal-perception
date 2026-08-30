# Cross-Modal Perception

*Seeing through someone else's eyes.*

An interactive page that lets you read one document as four different
professionals, and watch which sentences you can and cannot see change with each.

**Start here → [docs/findings.md](docs/findings.md)** — what the project found,
including the two results that contradicted what it set out to show.

## The four documents

| | |
|---|---|
| [`docs/OBJECTIVE.md`](docs/OBJECTIVE.md) | What we set out to build, and why |
| [`docs/research-note.md`](docs/research-note.md) | What the literature says — 16 sourced claims |
| [`docs/findings.md`](docs/findings.md) | **What we found** |
| [`docs/calibration.md`](docs/calibration.md) | What is measured vs modelled, written for a skeptic |
| [`docs/extending-the-study.md`](docs/extending-the-study.md) | How to add a reader or a document — and why a document is worth more |

## The result in three lines

- Three professionals reading the same note **agree about good and bad news** and
  differ in *where they look* — 0/8 to 6/8 shared among the clauses each dwells on.
- The only real valence conflicts are **professional versus lay**, and they land on
  the two sentences an untrained investor finds most reassuring: the buyback and
  the dividend rise.
- The readings are reproducible (α 0.83–0.97) and transfer to a held-out note,
  where the effect is real but about **a third weaker** than on the constructed one.

## Structure

```
pipeline/     Python (uv). Persona scoring → calibration → JSON. No rendering.
  scored/     Every sample from all three runs, including the failed one.
viz/
  template.html         The demo.    → dist/index.html
  report.template.html  The summary. → dist/report.html
  acts/                 Three single-idea pages, one finding each:
    chorus.template.html      Seven readers reaching for the same filing in
                              six different places.   → dist/chorus.html
    blindspot.template.html   The filing with everything one reader walked
                              past taken out.          → dist/blindspot.html
    eighth.template.html      You read it; the page puts you beside the
                              seven.                   → dist/eighth.html
    collision.template.html   You judge three sentences first, then meet the
                              seven who disagree with you.
                                                       → dist/collision.html
  lens.template.html    The instrument. Give it a URL or paste text and read
                        it behind any of the seven pairs of eyes, live.
                                                       → dist/lens.html
  build.py              Injects the fixtures into all six. No page holds
                        scores of its own, so re-scoring and rebuilding is the
                        whole update path.
fixtures/     The contract between pipeline and pages.
docs/         The four documents above.
```

## Running it

```bash
cd pipeline && uv sync && uv run pytest     # 411 tests, no network needed
cd .. && python3 viz/build.py               # fixtures → all six pages
open viz/dist/report.html
```

## Reading something the study never saw

The five pages above are records of what the study found. `dist/lens.html` is the
instrument: hand it a URL or paste text, choose one of the seven readers, and the
document is re-rendered as that reader perceives it — what they dwell on grows
and sharpens, what they skim past blurs out, good and bad news *for their
mandate* take opposite colours, and the sentences they take in as one idea close
into a single block. Switching readers morphs between the two renderings.

```bash
cd pipeline
export ANTHROPIC_API_KEY=...
uv run --extra scoring python -m cmp.server   # http://127.0.0.1:8420/
```

It binds to loopback only. It holds your key and will fetch any URL you give it,
so it is a tool you run on your own machine, not a service you deploy.

Without a key the page still opens and the five scored documents still work; live
readings return a 503 the page turns into an offer of those documents.

**A live reading is one sample, where the study takes five.** No median, no
second opinion, and Krippendorff's α cannot be computed from one run — so the
page carries that on screen for as long as a live reading is up.
[`docs/calibration.md` §8](docs/calibration.md) is the long version.

Re-scoring, either through subagents (samples already committed) or the Anthropic
API, is documented in [`docs/findings.md` §7](docs/findings.md) and
[`pipeline/README.md`](pipeline/README.md).

## Status

| Phase | Deliverable | State |
|---|---|---|
| 0 | Repo + objective | done |
| 1 | Literature study → research note | done |
| 2 | Quantification model + calibration layer | done |
| 3 | Calibrated hero fixture, reliability, held-out validation | done |
| 4 | The visualization | done |

## The one thing still open

**No human has validated any of it.** `pipeline/src/cmp/human.py` ranks a real
person's markup against the four personas, and has never been run against a real
person. Three practitioners and one afternoon would close it — and a *mismatch*
would be the most informative result the project could produce.
