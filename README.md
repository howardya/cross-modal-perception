# Cross-Modal Perception

*Seeing through someone else's eyes.*

An interactive visual experience that lets you briefly perceive a familiar stimulus the way
someone else perceives it — and notice that your own way of seeing is one option among many
rather than the neutral default.

Read **[docs/OBJECTIVE.md](docs/OBJECTIVE.md)** first.

## Structure

```
pipeline/     Python (uv). Research → persona scoring → calibration → JSON.
viz/          TypeScript + Vite. Consumes JSON, renders. Knows nothing about LLMs.
fixtures/     perceptual_field.json — the contract between the two halves.
docs/         Objective, research note, calibration note.
```

The two halves are decoupled by `fixtures/perceptual_field.json`. Either can be rebuilt without
touching the other, and the visualization can be developed against a hand-written fixture before
scoring exists.

## Status

| Phase | Deliverable | State |
|---|---|---|
| 0 | Repo + objective | done |
| 1 | `docs/research-note.md` — 16 sourced claims | done |
| 2 | Quantification model + `docs/calibration.md` | done |
| 3 | Calibrated hero fixture + `fixtures/meridian-q4.json` | done (scored inline; no reliability figure) |
| 4 | `viz/` — the visualization | done |

185 tests, `cd pipeline && uv run pytest`.

## Two things still open

**No reliability figure.** The hero note was scored inside a single Claude session
because no API credentials were available. Samples drawn in one conversation are
not independent, so Krippendorff's alpha could not be computed and the fixture
carries `reliability_measured: false`. Closing this is one command:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd pipeline
uv run python -m cmp calibrate meridian-q4   --k 5
uv run python -m cmp calibrate aldercroft-h1 --k 5   # held-out validation
python3 ../viz/build.py
```

**No human validation.** `pipeline/src/cmp/human.py` ranks a real person's markup
against the personas. It has never been run against a real person. Even n = 3
would move this from a plausible model to a checked one, and a mismatch would be
the strongest result in the project.

## Rebuilding the page

```bash
python3 viz/build.py     # injects fixtures/meridian-q4.json into viz/template.html
open viz/dist/index.html
```

The page holds no scores of its own. Re-running the calibration and rebuilding is
the whole update path.
