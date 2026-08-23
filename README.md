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
| 1 | `docs/research-note.md` | in progress |
| 2 | Quantification model + `docs/calibration.md` | not started |
| 3 | Calibrated hero stimulus + fixtures | not started |
| 4 | Visualization | not started |
