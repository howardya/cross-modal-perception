# Calibration report — Whirlpool Corporation — Q2 2026 results release

**Verdict: FAIL**

Stimulus `whirlpool-q2`, 31 clauses, 7 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.948 | 0.082 | reliable |
| `distressed-investor` | 0.956 | 0.089 | reliable |
| `equity-pm` | 0.951 | 0.065 | reliable |
| `financial-journalist` | 0.895 | 0.056 | reliable |
| `retail-investor` | 0.956 | 0.019 | reliable |
| `risk-officer` | 0.913 | 0.068 | reliable |
| `short-seller` | 0.915 | 0.062 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.82x | 0.69x | 0.61 | 0.082 vs 0.019 | pass |
| `distressed-investor` | 1.90x | 0.72x | 0.51 | 0.089 vs 0.019 | pass |
| `equity-pm` | 1.21x | 0.89x | 0.62 | 0.065 vs 0.019 | pass |
| `financial-journalist` | 1.34x | 0.91x | 0.32 | 0.056 vs 0.019 | pass |
| `risk-officer` | 0.98x | 1.01x | 0.39 | 0.068 vs 0.019 | **FAIL** |
| `short-seller` | 1.33x | 0.91x | 0.35 | 0.062 vs 0.019 | pass |

### Why these failed

- `risk-officer`: Expert attends no more to task-relevant units than the novice does (enhancement 0.98, expected above 1.0).
- `risk-officer`: Expert fails to suppress task-irrelevant units (suppression 1.01, expected below 1.0).

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **5/8** (62%) | 95.1% | 0 | 0.93 |
| `credit-analyst` | `risk-officer` | **6/8** (75%) | 97.5% | 0 | 1.00 |
| `credit-analyst` | `distressed-investor` | **7/8** (88%) | 99.5% | 0 | 0.84 |
| `credit-analyst` | `short-seller` | **6/8** (75%) | 97.1% | 3 | 1.00 |
| `credit-analyst` | `financial-journalist` | **5/8** (62%) | 93.1% | 2 | 0.82 |
| `credit-analyst` | `retail-investor` | **3/8** (38%) | 92.9% | 0 | 0.93 |
| `equity-pm` | `risk-officer` | **5/8** (62%) | 96.2% | 0 | 0.93 |
| `equity-pm` | `distressed-investor` | **5/8** (62%) | 94.4% | 0 | 0.77 |
| `equity-pm` | `short-seller` | **5/8** (62%) | 96.9% | 3 | 0.93 |
| `equity-pm` | `financial-journalist` | **4/8** (50%) | 93.9% | 2 | 0.88 |
| `equity-pm` | `retail-investor` | **4/8** (50%) | 95.6% | 0 | 1.00 |
| `risk-officer` | `distressed-investor` | **6/8** (75%) | 95.9% | 0 | 0.84 |
| `risk-officer` | `short-seller` | **6/8** (75%) | 98.8% | 7 | 1.00 |
| `risk-officer` | `financial-journalist` | **4/8** (50%) | 93.3% | 4 | 0.82 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 92.8% | 0 | 0.93 |
| `distressed-investor` | `short-seller` | **7/8** (88%) | 95.6% | 0 | 0.84 |
| `distressed-investor` | `financial-journalist` | **6/8** (75%) | 93.1% | 0 | 0.68 |
| `distressed-investor` | `retail-investor` | **4/8** (50%) | 92.8% | 0 | 0.77 |
| `short-seller` | `financial-journalist` | **5/8** (62%) | 94.3% | 0 | 0.82 |
| `short-seller` | `retail-investor` | **4/8** (50%) | 94.4% | 2 | 0.93 |
| `financial-journalist` | `retail-investor` | **5/8** (62%) | 96.7% | 1 | 0.88 |
