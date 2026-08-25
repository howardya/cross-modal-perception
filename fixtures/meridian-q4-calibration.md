# Calibration report — Meridian Logistics — Q4 results summary

**Verdict: FAIL**

Stimulus `meridian-q4`, 30 clauses, 7 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.983 | 0.059 | reliable |
| `distressed-investor` | 0.971 | 0.065 | reliable |
| `equity-pm` | 0.901 | 0.041 | reliable |
| `financial-journalist` | 0.921 | 0.043 | reliable |
| `retail-investor` | 0.964 | 0.025 | reliable |
| `risk-officer` | 0.931 | 0.045 | reliable |
| `short-seller` | 0.929 | 0.049 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 2.30x | 0.54x | 0.74 | 0.059 vs 0.025 | pass |
| `distressed-investor` | 2.50x | 0.69x | 0.41 | 0.065 vs 0.025 | pass |
| `equity-pm` | 1.29x | 0.82x | 0.77 | 0.041 vs 0.025 | pass |
| `financial-journalist` | 0.95x | 1.02x | 0.37 | 0.043 vs 0.025 | **FAIL** |
| `risk-officer` | 1.89x | 0.68x | 0.61 | 0.045 vs 0.025 | pass |
| `short-seller` | 1.89x | 0.76x | 0.42 | 0.049 vs 0.025 | pass |

### Why these failed

- `financial-journalist`: Expert attends no more to task-relevant units than the novice does (enhancement 0.95, expected above 1.0).
- `financial-journalist`: Expert fails to suppress task-irrelevant units (suppression 1.02, expected below 1.0).

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **6/8** (75%) | 96.0% | 0 | 0.92 |
| `credit-analyst` | `risk-officer` | **5/8** (62%) | 96.7% | 0 | 0.92 |
| `credit-analyst` | `distressed-investor` | **7/8** (88%) | 98.9% | 0 | 0.91 |
| `credit-analyst` | `short-seller` | **6/8** (75%) | 95.3% | 8 | 0.91 |
| `credit-analyst` | `financial-journalist` | **5/8** (62%) | 93.9% | 8 | 0.94 |
| `credit-analyst` | `retail-investor` | **2/8** (25%) | 85.9% | 2 | 0.91 |
| `equity-pm` | `risk-officer` | **5/8** (62%) | 95.5% | 0 | 1.00 |
| `equity-pm` | `distressed-investor` | **5/8** (62%) | 93.6% | 0 | 0.84 |
| `equity-pm` | `short-seller` | **6/8** (75%) | 97.1% | 10 | 0.84 |
| `equity-pm` | `financial-journalist` | **6/8** (75%) | 96.0% | 8 | 0.94 |
| `equity-pm` | `retail-investor` | **1/8** (12%) | 90.3% | 1 | 0.84 |
| `risk-officer` | `distressed-investor` | **4/8** (50%) | 96.5% | 0 | 0.84 |
| `risk-officer` | `short-seller` | **6/8** (75%) | 96.7% | 10 | 0.84 |
| `risk-officer` | `financial-journalist` | **5/8** (62%) | 95.8% | 10 | 0.94 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 87.6% | 2 | 0.84 |
| `distressed-investor` | `short-seller` | **5/8** (62%) | 93.6% | 1 | 1.00 |
| `distressed-investor` | `financial-journalist` | **5/8** (62%) | 93.3% | 1 | 0.85 |
| `distressed-investor` | `retail-investor` | **2/8** (25%) | 85.1% | 1 | 1.00 |
| `short-seller` | `financial-journalist` | **6/8** (75%) | 97.1% | 0 | 0.85 |
| `short-seller` | `retail-investor` | **2/8** (25%) | 88.6% | 3 | 1.00 |
| `financial-journalist` | `retail-investor` | **2/8** (25%) | 91.7% | 3 | 0.85 |
