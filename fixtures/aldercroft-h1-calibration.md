# Calibration report — Aldercroft Software — H1 trading update

**Verdict: PASS**

Stimulus `aldercroft-h1`, 20 clauses, 4 personas. Novice baseline: `retail-investor`.

## Reliability (agreement of each persona with itself)

Alpha is read alongside concentration. Krippendorff's alpha divides by the
spread of scores across clauses, so a persona attending near-uniformly can
score near zero even when its runs agree — which is the expected shape for a
lay reader, not a defect. A low alpha with *concentrated* attention is the
real failure: the persona is picking different clauses each run.

| Persona | alpha | Concentration | Reading |
|---|---|---|---|
| `credit-analyst` | 0.940 | 0.060 | reliable |
| `equity-pm` | 0.953 | 0.072 | reliable |
| `retail-investor` | 0.961 | 0.028 | reliable |
| `risk-officer` | 0.826 | 0.045 | reliable |

## Literature acceptance (L1)

Target asymmetry from the research note: 1.70 (reported, not gated — see docs/calibration.md section 2).

| Persona | Enhancement | Suppression | Asymmetry | Concentration vs novice | Result |
|---|---|---|---|---|---|
| `credit-analyst` | 1.48x | 0.61x | 1.26 | 0.060 vs 0.028 | pass |
| `equity-pm` | 1.55x | 0.60x | 1.15 | 0.072 vs 0.028 | pass |
| `risk-officer` | 1.47x | 0.67x | 1.06 | 0.045 vs 0.028 | pass |

## Pairwise divergence

`Top-k shared` is the headline: of the clauses each reader attends to most,
how many are the same. `1 - JSD` is the continuous measure and is retained,
but it compresses badly over a long document — see cmp.metrics.top_k_overlap.

| Persona A | Persona B | Top-k shared | 1 - JSD | Valence conflicts | Chunk agreement |
|---|---|---|---|---|---|
| `credit-analyst` | `equity-pm` | **4/8** (50%) | 86.9% | 0 | 0.83 |
| `credit-analyst` | `risk-officer` | **5/8** (62%) | 91.3% | 0 | 0.54 |
| `credit-analyst` | `retail-investor` | **4/8** (50%) | 92.2% | 0 | 0.61 |
| `equity-pm` | `risk-officer` | **3/8** (38%) | 82.4% | 0 | 0.59 |
| `equity-pm` | `retail-investor` | **4/8** (50%) | 88.1% | 0 | 0.55 |
| `risk-officer` | `retail-investor` | **4/8** (50%) | 92.8% | 1 | 0.34 |
