# Calibration report — Jazz Pharmaceuticals plc — Q2 2026 results release

**Verdict: PASS**

Stimulus `jazz-q2`, 33 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.891 | 0.061 | reliable |
| `equity-pm` | 0.870 | 0.057 | reliable |
| `retail-investor` | 0.953 | 0.024 | reliable |
| `risk-officer` | 0.897 | 0.064 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.67x | 0.80x | 0.43 | 0.061 vs 0.024 | pass |
| `equity-pm` | 1.24x | 0.89x | 0.52 | 0.057 vs 0.024 | pass |
| `risk-officer` | 2.07x | 0.71x | 0.47 | 0.064 vs 0.024 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **5/8** (62%) | 97.7% | 0 | 0.71 |
| `credit-analyst` | `risk-officer` | **3/8** (38%) | 91.3% | 0 | 0.78 |
| `credit-analyst` | `retail-investor` | **5/8** (62%) | 95.9% | 0 | 0.75 |
| `equity-pm` | `risk-officer` | **4/8** (50%) | 93.4% | 0 | 0.83 |
| `equity-pm` | `retail-investor` | **4/8** (50%) | 94.2% | 0 | 0.87 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 88.3% | 0 | 0.96 |
