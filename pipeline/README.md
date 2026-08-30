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


## The lens: reading a document the study never saw

`cmp.server` is a local, loopback-only server that lets `viz/dist/lens.html` read
arbitrary prose.

```bash
export ANTHROPIC_API_KEY=...
uv run --extra scoring python -m cmp.server      # http://127.0.0.1:8420/
```

| Module | What it does |
|---|---|
| `cmp.ingest` | URL or pasted text → clauses. Sentence-level, with an abbreviation guard. Capped at 120 clauses, floored at 6. |
| `cmp.lens` | One sample of one persona over one document, plus up to four marginal notes in that reader's voice. |
| `cmp.server` | `POST /api/ingest`, `POST /api/attend`, `GET /api/personas`. Caches per document and persona under `.lenscache/`. |
| `cmp.lens_data` | The build-time payload for the page: the personas plus all five scored documents. |

Three things worth knowing before trusting anything it shows.

**One sample, not five.** `score_persona` refuses fewer than two runs — one sample
is an anecdote and inter-run reliability cannot be measured from it. `cmp.lens`
takes exactly one, because a viewer is waiting, and every artefact it writes
carries `samples: 1` and `reliability_measured: false`. `docs/calibration.md` §8.

**The study's contract is not touched.** `LENS_SCHEMA` is a deep copy of
`SCORING_SCHEMA` with one optional field added, and `build_lens_prompt` is
`build_scoring_prompt` verbatim plus a paragraph. Tests pin both. A schema shared
between the record and the instrument would let the instrument redefine the
record.

**Loopback only.** It holds an API key and fetches URLs it is handed. Run it on
your own machine while you look at a document; do not deploy it.
