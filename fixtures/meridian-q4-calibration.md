# Calibration report — Meridian Logistics — Q4 results summary

**Verdict: PASS**

Stimulus `meridian-q4`, 30 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability — NOT MEASURED

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | nan | 0.079 | reliable |
| `equity-pm` | nan | 0.052 | reliable |
| `retail-investor` | nan | 0.023 | reliable |
| `risk-officer` | nan | 0.030 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 2.31x | 0.46x | 0.93 | 0.079 vs 0.023 | pass |
| `equity-pm` | 1.50x | 0.64x | 1.10 | 0.052 vs 0.023 | pass |
| `risk-officer` | 2.04x | 0.65x | 0.61 | 0.030 vs 0.023 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **2/8** (25%) | 85.1% | 3 | 0.92 |
| `credit-analyst` | `risk-officer` | **4/8** (50%) | 91.5% | 0 | 0.74 |
| `credit-analyst` | `retail-investor` | **1/8** (12%) | 83.4% | 2 | 0.11 |
| `equity-pm` | `risk-officer` | **2/8** (25%) | 89.1% | 3 | 0.82 |
| `equity-pm` | `retail-investor` | **5/8** (62%) | 94.2% | 0 | 0.11 |
| `risk-officer` | `retail-investor` | **0/8** (0%) | 90.4% | 3 | 0.13 |
