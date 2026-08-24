# Calibration report — Alamo Group Inc. — Q2 2026 results release

**Verdict: PASS**

Stimulus `alamo-q2`, 35 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.971 | 0.087 | reliable |
| `equity-pm` | 0.905 | 0.066 | reliable |
| `retail-investor` | 0.946 | 0.018 | reliable |
| `risk-officer` | 0.915 | 0.064 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 2.92x | 0.58x | 0.50 | 0.087 vs 0.018 | pass |
| `equity-pm` | 1.54x | 0.84x | 0.40 | 0.066 vs 0.018 | pass |
| `risk-officer` | 1.78x | 0.80x | 0.39 | 0.064 vs 0.018 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **3/8** (38%) | 83.9% | 0 | 0.80 |
| `credit-analyst` | `risk-officer` | **5/8** (62%) | 91.6% | 0 | 0.83 |
| `credit-analyst` | `retail-investor` | **1/8** (12%) | 84.3% | 0 | 0.80 |
| `equity-pm` | `risk-officer` | **3/8** (38%) | 87.0% | 0 | 0.97 |
| `equity-pm` | `retail-investor` | **3/8** (38%) | 90.9% | 0 | 0.85 |
| `risk-officer` | `retail-investor` | **0/8** (0%) | 88.5% | 1 | 0.83 |
