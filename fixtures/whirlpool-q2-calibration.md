# Calibration report — Whirlpool Corporation — Q2 2026 results release

**Verdict: FAIL**

Stimulus `whirlpool-q2`, 31 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.944 | 0.080 | reliable |
| `equity-pm` | 0.940 | 0.060 | reliable |
| `retail-investor` | 0.921 | 0.018 | reliable |
| `risk-officer` | 0.922 | 0.061 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.87x | 0.68x | 0.61 | 0.080 vs 0.018 | pass |
| `equity-pm` | 1.18x | 0.91x | 0.59 | 0.060 vs 0.018 | pass |
| `risk-officer` | 0.95x | 1.02x | 0.40 | 0.061 vs 0.018 | **FAIL** |

### Why these failed

- `risk-officer`: Expert attends no more to task-relevant units than the novice does (enhancement 0.95, expected above 1.0).
- `risk-officer`: Expert fails to suppress task-irrelevant units (suppression 1.02, expected below 1.0).

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **5/8** (62%) | 97.2% | 0 | 0.93 |
| `credit-analyst` | `risk-officer` | **6/8** (75%) | 98.0% | 0 | 0.77 |
| `credit-analyst` | `retail-investor` | **3/8** (38%) | 92.9% | 0 | 0.75 |
| `equity-pm` | `risk-officer` | **5/8** (62%) | 97.0% | 0 | 0.73 |
| `equity-pm` | `retail-investor` | **4/8** (50%) | 95.9% | 0 | 0.80 |
| `risk-officer` | `retail-investor` | **2/8** (25%) | 93.3% | 0 | 0.71 |
