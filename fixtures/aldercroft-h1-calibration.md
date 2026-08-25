# Calibration report — Aldercroft Software — H1 trading update

**Verdict: PASS**

Stimulus `aldercroft-h1`, 20 clauses, 7 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.967 | 0.062 | reliable |
| `distressed-investor` | 0.951 | 0.074 | reliable |
| `equity-pm` | 0.958 | 0.059 | reliable |
| `financial-journalist` | 0.959 | 0.069 | reliable |
| `retail-investor` | 0.951 | 0.028 | reliable |
| `risk-officer` | 0.874 | 0.048 | reliable |
| `short-seller` | 0.901 | 0.055 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.50x | 0.61x | 1.21 | 0.062 vs 0.028 | pass |
| `distressed-investor` | 2.16x | 0.64x | 0.58 | 0.074 vs 0.028 | pass |
| `equity-pm` | 1.54x | 0.60x | 1.18 | 0.059 vs 0.028 | pass |
| `financial-journalist` | 1.24x | 0.85x | 0.78 | 0.069 vs 0.028 | pass |
| `risk-officer` | 1.51x | 0.63x | 1.11 | 0.048 vs 0.028 | pass |
| `short-seller` | 1.97x | 0.71x | 0.51 | 0.055 vs 0.028 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **3/8** (38%) | 86.8% | 0 | 0.83 |
| `credit-analyst` | `risk-officer` | **4/8** (50%) | 90.8% | 0 | 1.00 |
| `credit-analyst` | `distressed-investor` | **8/8** (100%) | 99.2% | 1 | 0.95 |
| `credit-analyst` | `short-seller` | **4/8** (50%) | 88.4% | 2 | 0.66 |
| `credit-analyst` | `financial-journalist` | **3/8** (38%) | 82.1% | 1 | 1.00 |
| `credit-analyst` | `retail-investor` | **4/8** (50%) | 91.6% | 0 | 0.77 |
| `equity-pm` | `risk-officer` | **1/8** (12%) | 83.4% | 0 | 0.83 |
| `equity-pm` | `distressed-investor` | **3/8** (38%) | 85.1% | 0 | 0.79 |
| `equity-pm` | `short-seller` | **5/8** (62%) | 95.1% | 4 | 0.66 |
| `equity-pm` | `financial-journalist` | **5/8** (62%) | 89.6% | 4 | 0.83 |
| `equity-pm` | `retail-investor` | **4/8** (50%) | 89.0% | 0 | 0.70 |
| `risk-officer` | `distressed-investor` | **4/8** (50%) | 89.6% | 1 | 0.95 |
| `risk-officer` | `short-seller` | **2/8** (25%) | 86.3% | 2 | 0.66 |
| `risk-officer` | `financial-journalist` | **4/8** (50%) | 87.6% | 2 | 1.00 |
| `risk-officer` | `retail-investor` | **3/8** (38%) | 91.3% | 0 | 0.77 |
| `distressed-investor` | `short-seller` | **4/8** (50%) | 85.5% | 0 | 0.63 |
| `distressed-investor` | `financial-journalist` | **3/8** (38%) | 79.1% | 0 | 0.95 |
| `distressed-investor` | `retail-investor` | **4/8** (50%) | 90.1% | 1 | 0.72 |
| `short-seller` | `financial-journalist` | **3/8** (38%) | 89.5% | 0 | 0.66 |
| `short-seller` | `retail-investor` | **3/8** (38%) | 89.4% | 2 | 0.50 |
| `financial-journalist` | `retail-investor` | **6/8** (75%) | 94.6% | 2 | 0.77 |
