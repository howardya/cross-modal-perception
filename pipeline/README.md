# Pipeline

Persona scoring, divergence metrics, calibration. Emits the JSON the
visualization consumes. Knows nothing about rendering.

## Setup

```bash
cd pipeline
uv sync
uv run pytest            # 156 tests, no network required
```

## Running the calibration

Needs Anthropic API credentials. Either:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

or, if the `ant` CLI is installed, `ant auth login` — the SDK picks up the stored
profile with no environment variable.

Then:

```bash
uv run python -m cmp list                                # available stimuli
uv run python -m cmp calibrate meridian-q4   --k 5       # hero,     ~20 calls
uv run python -m cmp calibrate aldercroft-h1 --k 5       # held-out, ~20 calls
```

Each run writes two files into `../fixtures/`:

- `<stimulus>.json` — the perceptual field set the visualization reads
- `<stimulus>-calibration.md` — the published calibration report

**The command exits non-zero if the run fails the acceptance checks.** The fixture
is still written so the failure can be inspected, but a failing run must not be
shipped as calibrated. Do not tune the personas until it passes — a failure is a
result, and `docs/calibration.md` is where it gets reported.

Cost is roughly 20 Opus calls per stimulus at `--k 5`. Lower `--k` for a cheap
smoke test, but `--k 1` is rejected: a single sample has no measurable reliability.

## Layout

| Module | Purpose |
|---|---|
| `metrics.py` | Divergence, overlap, valence conflict, concentration, chunk agreement |
| `targets.py` | Published effect sizes as executable acceptance constraints |
| `personas.py` | Four finance personas, defined as mandates |
| `stimuli.py` | Stimulus loading and author-assigned relevance masks |
| `scoring.py` | k-sample loop, median aggregation. Client is injected |
| `anthropic_client.py` | Claude Opus 5 with a constrained output schema |
| `reliability.py` | Krippendorff's alpha, plus the diffuse/erratic diagnosis |
| `calibrate.py` | Runs a stimulus and builds the report |
| `human.py` | Ranks a person's markup against the personas |
| `field.py` | The perceptual field and the JSON contract |

## Two things that will bite you

**Relevance masks mean "would fixate on", not "bears on the mandate."** Salience is
normalised to a fixed budget, so if a mask marks a majority of clauses relevant,
enhancement and suppression become algebraically the same statement and the
asymmetry constraint silently stops testing anything. Masks are held to a minority
of clauses by `tests/test_stimuli.py`.

**A low alpha is not automatically a failure.** For a persona attending
near-uniformly — the correct shape for a lay reader — alpha's denominator
collapses and the statistic stops being informative. `diagnose_reliability`
separates that case from a genuinely erratic persona by reading alpha alongside
concentration.
