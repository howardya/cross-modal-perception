# Calibration report — Meridian Logistics — Q4 results summary

**Verdict: FAIL**

Stimulus `meridian-q4`, 30 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.983 | 0.039 | reliable |
| `equity-pm` | 0.935 | 0.017 | reliable |
| `retail-investor` | 0.977 | 0.049 | reliable |
| `risk-officer` | 0.972 | 0.027 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 2.29x | 0.60x | 0.61 | 0.039 vs 0.049 | **FAIL** |
| `equity-pm` | 1.04x | 0.97x | 0.73 | 0.017 vs 0.049 | **FAIL** |
| `risk-officer` | 1.88x | 0.72x | 0.52 | 0.027 vs 0.049 | **FAIL** |

### Why these failed

- `credit-analyst`: Expert attention is no more concentrated than novice attention (0.039 vs 0.049).
- `equity-pm`: Expert attention is no more concentrated than novice attention (0.017 vs 0.049).
- `risk-officer`: Expert attention is no more concentrated than novice attention (0.027 vs 0.049).

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **5/8** (62%) | 96.8% | 0 | 0.74 |
| `credit-analyst` | `risk-officer` | **4/8** (50%) | 98.6% | 0 | 0.91 |
| `credit-analyst` | `retail-investor` | **1/8** (12%) | 85.3% | 2 | 0.91 |
| `equity-pm` | `risk-officer` | **3/8** (38%) | 96.8% | 0 | 0.83 |
| `equity-pm` | `retail-investor` | **1/8** (12%) | 91.8% | 1 | 0.83 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 86.7% | 2 | 1.00 |
