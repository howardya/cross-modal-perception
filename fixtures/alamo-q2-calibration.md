# Calibration report — Alamo Group Inc. — Q2 2026 results release

**Verdict: PASS**

Stimulus `alamo-q2`, 35 clauses, 7 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.965 | 0.084 | reliable |
| `distressed-investor` | 0.916 | 0.099 | reliable |
| `equity-pm` | 0.853 | 0.056 | reliable |
| `financial-journalist` | 0.853 | 0.057 | reliable |
| `retail-investor` | 0.937 | 0.017 | reliable |
| `risk-officer` | 0.821 | 0.054 | reliable |
| `short-seller` | 0.862 | 0.058 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 3.03x | 0.58x | 0.50 | 0.084 vs 0.017 | pass |
| `distressed-investor` | 3.98x | 0.62x | 0.34 | 0.099 vs 0.017 | pass |
| `equity-pm` | 1.58x | 0.83x | 0.41 | 0.056 vs 0.017 | pass |
| `financial-journalist` | 1.14x | 0.96x | 0.27 | 0.057 vs 0.017 | pass |
| `risk-officer` | 1.79x | 0.81x | 0.37 | 0.054 vs 0.017 | pass |
| `short-seller` | 1.91x | 0.82x | 0.31 | 0.058 vs 0.017 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **3/8** (38%) | 84.8% | 0 | 0.95 |
| `credit-analyst` | `risk-officer` | **4/8** (50%) | 90.6% | 0 | 0.92 |
| `credit-analyst` | `distressed-investor` | **7/8** (88%) | 99.2% | 4 | 0.74 |
| `credit-analyst` | `short-seller` | **1/8** (12%) | 80.5% | 1 | 0.85 |
| `credit-analyst` | `financial-journalist` | **1/8** (12%) | 78.6% | 1 | 0.92 |
| `credit-analyst` | `retail-investor` | **1/8** (12%) | 84.1% | 0 | 0.65 |
| `equity-pm` | `risk-officer` | **3/8** (38%) | 89.9% | 0 | 0.97 |
| `equity-pm` | `distressed-investor` | **2/8** (25%) | 82.2% | 0 | 0.78 |
| `equity-pm` | `short-seller` | **3/8** (38%) | 95.0% | 3 | 0.91 |
| `equity-pm` | `financial-journalist` | **4/8** (50%) | 92.0% | 3 | 0.97 |
| `equity-pm` | `retail-investor` | **2/8** (25%) | 91.1% | 0 | 0.61 |
| `risk-officer` | `distressed-investor` | **4/8** (50%) | 91.1% | 0 | 0.81 |
| `risk-officer` | `short-seller` | **4/8** (50%) | 92.2% | 2 | 0.94 |
| `risk-officer` | `financial-journalist` | **4/8** (50%) | 89.0% | 2 | 1.00 |
| `risk-officer` | `retail-investor` | **1/8** (12%) | 89.5% | 0 | 0.66 |
| `distressed-investor` | `short-seller` | **1/8** (12%) | 79.1% | 0 | 0.75 |
| `distressed-investor` | `financial-journalist` | **1/8** (12%) | 77.3% | 0 | 0.81 |
| `distressed-investor` | `retail-investor` | **0/8** (0%) | 81.8% | 1 | 0.56 |
| `short-seller` | `financial-journalist` | **4/8** (50%) | 96.1% | 0 | 0.94 |
| `short-seller` | `retail-investor` | **3/8** (38%) | 92.6% | 0 | 0.60 |
| `financial-journalist` | `retail-investor` | **4/8** (50%) | 94.2% | 0 | 0.66 |
