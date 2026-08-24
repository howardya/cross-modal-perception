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
  build.py              Injects the fixtures into both. Neither page holds
                        scores of its own, so re-scoring and rebuilding is the
                        whole update path.
fixtures/     The contract between pipeline and pages.
docs/         The four documents above.
```

## Running it

```bash
cd pipeline && uv sync && uv run pytest     # 297 tests, no network needed
cd .. && python3 viz/build.py               # fixtures → both pages
open viz/dist/report.html
```

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
