# Calibration report — Jazz Pharmaceuticals plc — Q2 2026 results release

**Verdict: FAIL**

Stimulus `jazz-q2`, 33 clauses, 7 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.900 | 0.063 | reliable |
| `distressed-investor` | 0.791 | 0.091 | **erratic** |
| `equity-pm` | 0.903 | 0.049 | reliable |
| `financial-journalist` | 0.857 | 0.042 | reliable |
| `retail-investor` | 0.970 | 0.024 | reliable |
| `risk-officer` | 0.902 | 0.066 | reliable |
| `short-seller` | 0.848 | 0.055 | reliable |

### Reliability notes

- `distressed-investor`: Alpha is 0.79 while attention is concentrated (concentration 0.091). The persona is focusing on different clauses on different runs, which is erratic rather than diffuse. This is a real reliability failure.

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.77x | 0.78x | 0.45 | 0.063 vs 0.024 | pass |
| `distressed-investor` | 1.69x | 0.81x | 0.39 | 0.091 vs 0.024 | pass |
| `equity-pm` | 1.18x | 0.92x | 0.51 | 0.049 vs 0.024 | pass |
| `financial-journalist` | 1.56x | 0.85x | 0.36 | 0.042 vs 0.024 | pass |
| `risk-officer` | 2.07x | 0.71x | 0.47 | 0.066 vs 0.024 | pass |
| `short-seller` | 1.54x | 0.85x | 0.39 | 0.055 vs 0.024 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **6/8** (75%) | 98.1% | 0 | 0.86 |
| `credit-analyst` | `risk-officer` | **4/8** (50%) | 90.4% | 0 | 0.80 |
| `credit-analyst` | `distressed-investor` | **6/8** (75%) | 97.1% | 3 | 0.67 |
| `credit-analyst` | `short-seller` | **4/8** (50%) | 95.5% | 1 | 0.92 |
| `credit-analyst` | `financial-journalist` | **4/8** (50%) | 94.0% | 0 | 0.82 |
| `credit-analyst` | `retail-investor` | **4/8** (50%) | 94.3% | 0 | 1.00 |
| `equity-pm` | `risk-officer` | **4/8** (50%) | 92.8% | 0 | 0.86 |
| `equity-pm` | `distressed-investor` | **5/8** (62%) | 93.8% | 3 | 0.73 |
| `equity-pm` | `short-seller` | **5/8** (62%) | 97.8% | 3 | 0.79 |
| `equity-pm` | `financial-journalist` | **2/8** (25%) | 95.3% | 0 | 0.89 |
| `equity-pm` | `retail-investor` | **3/8** (38%) | 94.4% | 0 | 0.86 |
| `risk-officer` | `distressed-investor` | **3/8** (38%) | 87.7% | 1 | 0.73 |
| `risk-officer` | `short-seller` | **5/8** (62%) | 94.2% | 1 | 0.79 |
| `risk-officer` | `financial-journalist` | **4/8** (50%) | 90.4% | 1 | 0.89 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 86.5% | 0 | 0.80 |
| `distressed-investor` | `short-seller` | **4/8** (50%) | 92.4% | 0 | 0.65 |
| `distressed-investor` | `financial-journalist` | **4/8** (50%) | 90.4% | 2 | 0.75 |
| `distressed-investor` | `retail-investor` | **6/8** (75%) | 92.8% | 3 | 0.67 |
| `short-seller` | `financial-journalist` | **4/8** (50%) | 93.9% | 3 | 0.81 |
| `short-seller` | `retail-investor` | **4/8** (50%) | 92.9% | 4 | 0.92 |
| `financial-journalist` | `retail-investor` | **5/8** (62%) | 95.8% | 2 | 0.82 |
