# Findings

What this project actually found, as opposed to what it set out to find.

Three companion documents: [`OBJECTIVE.md`](OBJECTIVE.md) is what we meant to
build, [`research-note.md`](research-note.md) is what the literature says, and
[`calibration.md`](calibration.md) is the argument written for someone trying to
disbelieve the result. This file is the record of conclusions.

---

## 1. In one paragraph

Four professional mandates — credit analyst, equity portfolio manager, risk
officer, retail investor — were applied to the same 30-clause financial note by a
language model, five independent times each, and checked against constraints
derived from the perceptual-expertise literature. The readings are reproducible
(Krippendorff's α 0.83–0.97) and the method transfers unchanged to a note held
back from every tuning decision. The central result is not the one the project
was designed to show. **The three experts do not disagree with each other about
what is good or bad news. They disagree about what to look at.** The only genuine
valence conflicts are between professionals and the untrained reader, and they
land on the two sentences an ordinary investor would find most reassuring.

---

## 2. The headline results

### 2.1 Experts diverge in attention, not judgement

Of the eight clauses each reader dwells on most, how many are shared:

| Pair | Hero note | Held-out note |
|---|---|---|
| equity PM vs retail investor | **0 / 8** | 4 / 8 |
| credit analyst vs retail investor | 1 / 8 | 4 / 8 |
| risk officer vs retail investor | 1 / 8 | 4 / 8 |
| equity PM vs risk officer | 5 / 8 | 3 / 8 |
| credit analyst vs equity PM | 5 / 8 | 4 / 8 |
| credit analyst vs risk officer | 6 / 8 | 5 / 8 |

On the hero note, an equity PM and a retail investor read the same thirty
sentences and share **nothing at all** in what they dwell on. Meanwhile the three
professionals overlap with each other at 5/8 and 6/8 — they are reading the same
document in a way an untrained person simply is not.

### 2.2 The valence divide is professional versus lay

Valence conflicts (both readers confident, opposite signs) across the whole hero
note: **5 in total, every one of them expert-versus-retail.** Between the three
experts: **zero.**

| Clause | Credit | Equity | Risk | Retail |
|---|---|---|---|---|
| "$300m share repurchase … funded from the revolving credit facility" | −0.90 | −0.70 | −0.85 | **+0.60** |
| "The quarterly dividend was raised 8% to 27 cents" | −0.50 | −0.20 | −0.50 | **+0.90** |

**The two sentences an untrained reader likes most are the two every professional
treats as a warning.** Not because the untrained reader is careless — those
sentences are written to sound like generosity. Knowing where the money comes
from is what inverts them, and that knowledge is invisible from outside.

### 2.3 Expertise concentrates attention, as predicted

| Persona | Hero | Held-out |
|---|---|---|
| credit analyst | 0.062 | 0.060 |
| equity PM | 0.042 | 0.072 |
| risk officer | 0.043 | 0.045 |
| retail investor (baseline) | 0.023 | 0.028 |

Every expert is more concentrated than the lay reader on both notes, in the
direction the information-reduction hypothesis predicts. This is the one place
the literature's prediction was reproduced cleanly.

### 2.4 It is reproducible

Krippendorff's α across five independent runs per persona — each a fresh model
context, blind to the others:

| Persona | Hero | Held-out |
|---|---|---|
| credit analyst | 0.972 | 0.940 |
| equity PM | 0.880 | 0.953 |
| risk officer | 0.936 | 0.826 |
| retail investor | 0.944 | 0.961 |

All eight figures clear the 0.80 convention. **This measures consistency, not
correctness** — a reader could be reproducibly wrong and score exactly as well.

### 2.5 The constructed note inflates the effect by about a third

| | Hero (tuning done here) | Held-out (never seen) |
|---|---|---|
| L1 acceptance | pass | pass |
| Reliability α | 0.88 – 0.97 | 0.83 – 0.96 |
| Top-8 shared, range | 0/8 – 6/8 | 3/8 – 5/8 |
| **Mean overlap** | **37.5%** | **50.0%** |
| Valence conflicts | 5 | 1 |

The hero note was written to divide these readers. The held-out note was not.
The phenomenon survives — reliably, in the predicted direction, on a document the
method had never seen — but **the dramatic 0/8 is a property of the hero note,
not of the four mandates.** On ordinary prose the separation is real and about a
third smaller.

---

## 3. Four things the literature corrected

Found during the research phase, before any code was written. Each contradicted
an assumption in the approved plan.

1. **Bouba/kiki is 72%, not the ~95% usually quoted.** Ćwiek et al. (2022), 917
   participants, 25 languages, 10 writing systems: 72% congruent [56–82%]. It is
   asymmetric (*bouba* reliable in 22 of 25 languages, *kiki* in 11) and it falls
   *below chance* in Romanian, Mandarin and Turkish.

2. **The synaesthete "pop-out" is not pop-out.** Ward et al. (2010), 36
   synaesthetes: 41.4% correct against 31.5%. The authors concluded synaesthetic
   colour does not guide attention the way real colour does; Rothen & Meier (2009)
   found no advantage at all. A head start, not magic — which turns out to be a
   better analogy for expertise anyway.

3. **The classic expert-gaze signature is not reliable.** Klostermann & Moeinirad
   (2020), 101 studies: more null than significant results for fixation duration
   and count, and the sport literature's *direction* is the opposite of the
   visualization meta-analysis's. What does hold is gaze **location** — which is
   fortunate, since location is what this project renders.

4. **Attention is zero-sum and dilutes.** Sirois et al. (2018) measured it in a
   real financial document: highlighting one audit matter pulled readers to the
   related note ~207 seconds faster, highlighting three worked measurably less
   well per matter, and attention to highlighted sections came out of attention to
   everything else. This is why salience is normalised throughout.

---

## 4. Five things building it corrected

These are errors in the project's own design, found only by running it.

### 4.1 A constraint that could not be satisfied

The literature-acceptance layer originally *failed* any field whose suppression
of the irrelevant did not dominate its enhancement of the relevant. Under a fixed
attention budget the totals must balance across unequal counts, so with a
minority relevant mask each irrelevant clause necessarily loses less share than
each relevant clause gains. Passing required roughly a **45:1** salience ratio.
It was testing an artefact of the normalisation, not a finding. Demoted to a
reported diagnostic.

### 4.2 The headline metric was the wrong statistic

"Perceptual overlap" as 1 − Jensen-Shannon divergence scored every persona pair
at **83–94%** on real data. Arithmetically correct, rhetorically fatal: it reads
as *these people broadly agree*, the opposite of the finding. JSD only approaches
1 for near-disjoint support, so it compresses everything into a narrow high band.
Replaced with **top-k attention overlap**, which is the comparison a heat-map
overlay actually makes and which separates the personas properly.

### 4.3 Prose does not constrain a model; arithmetic does

Told in words that "your attention is a finite budget", the model marked almost
every clause salient. The equity PM came out at concentration **0.017** —
essentially uniform, and *flatter than the untrained reader*, inverting the
finding the project rests on. Replacing the prose with a countable quota (at most
8 of 30 clauses above 0.55, at least 12 below 0.25) fixed it immediately; agents
reported hitting the quota exactly. **This is the single most transferable lesson
here.** A model's default is to be comprehensive, and comprehensiveness is the
precise opposite of expertise.

### 4.4 The novice needs a different quota, or the contrast collapses

Applying the expert quota to the lay reader would have made the novice as
concentrated as the expert and erased the very thing being measured. The lay
persona gets a deliberately looser bound (at most 15 above, only 4 below),
because the literature's claim *is* that experts concentrate and novices do not.

### 4.5 Reliability statistics mislead on diffuse readers

Krippendorff's α divides by the spread of scores across clauses. A reader
attending near-uniformly — which is correct behaviour for a novice — can score
near zero even when its runs agree closely. Reading that as unreliability would
fail a good run for the wrong reason; ignoring it would hide a genuinely erratic
persona. The code therefore reads α alongside concentration and distinguishes
**diffuse** (uninformative) from **erratic** (a real failure).

---

## 5. The reversal

The project was designed around a credit-analyst-versus-equity-PM conflict, and
the hero note was constructed to produce one. **Scored independently, that
conflict did not appear.**

An earlier hand-scored fixture had the equity PM at **+0.70** on the debt-funded
buyback, on the conventional "capital returned to shareholders" reading. Scored
cold, the model put it at **−0.70**: borrowing at 4.1x leverage to repurchase
stock while cash conversion collapses is bad capital allocation for the residual
claimant too. That is the better reading. The hand-scored version — written by
the author of this project — was simply wrong, and the independent runs caught it.

So the stimulus failed at the thing it was built for, and the finding that
replaced it is stronger:

> Professionals are not divided from each other by judgement. They are divided
> from the untrained by *what they can see*, and divided from each other by
> *where they look*.

That is closer to the information-reduction hypothesis the project is built on
than the symmetric conflict it set out to show, and unlike the original it was
not authored by hand.

---

## 5b. Is there a "DNA" for each role?

Asked directly: can the four readers be reduced to a compact profile that means
something, rather than a 30-clause fingerprint of one document?

The question has a sharp test in it. **A fingerprint identifies; DNA generates.**
A trait is only a property of the *role* if it survives changing the document —
and with two independently-scored notes that is falsifiable. Six traits were
computed on both (`pipeline/src/cmp/signature.py`, report via
`python -m cmp.dna`).

| Trait | Asks | Spread ÷ drift | Ordering holds? |
|---|---|---|---|
| **Threat pull** | Does bad news pull the eye, or good news? | 3.98 | **yes** |
| Chunking | How many sentences read as one idea? | 6.32 | no |
| Focus | How narrowly is attention spent? | 4.09 | no |
| Baseline mood | What does this reader expect to find? | 3.37 | no |
| Alarm | How much unease does the document raise? | 1.95 | no |
| Reading position | Where in the document does attention land? | 1.35 | no |

### The one that works

**Threat pull** — the correlation between how much a clause pulls the eye and how
*bad* it is — is the only trait whose ordering across all four readers survives
the change of document. It also flips sign, which is what makes it interpretable
rather than merely different:

| | Hero note | Held-out note |
|---|---|---|
| risk officer | +0.83 | +0.68 |
| equity PM | +0.83 | +0.65 |
| credit analyst | +0.78 | **−0.07** |
| retail investor | **−0.56** | **−0.35** |

Positive means attention is dragged toward bad news; negative means toward good
news. **The untrained reader is negative on both documents; two of the three
professionals are strongly positive on both.** That is the mechanism underneath
§2.2 — it is *why* the two sentences a layperson likes best are the two every
professional flags. Their attention is wired to opposite signs.

It is also the trait the prompt did **not** specify. The mandates say what each
role reads *for* — covenants, tail events, headline numbers — never which
direction of news should attract attention. Meanwhile alarm, which the risk
officer's mandate does imply, failed the stability test. So the signature is not
simply recovering its own instructions, which was the obvious objection.

### Three honest limits

**The credit analyst breaks it.** Its threat pull collapses from +0.78 to −0.07 on
the unseen note. The professional/lay separation rests on two roles out of three.

**On the held-out note the axis inverts.** There, the three professionals differ
from *each other* (spread 0.75) more than the least threat-driven of them differs
from the layperson (gap 0.28). On the tuned note the group split dominates; on the
unseen one it does not. This is the strongest single caution against treating
these six numbers as settled.

**Two documents cannot establish a fine structure.** Several traits order the
three professionals identically on both — threat, alarm and reading position all
put the risk officer at one end, most alarmed and reading latest in the document,
which is a satisfying story about a role that hunts for governance items buried at
the end. But with two documents, "consistent twice" is a coin landing the same way
twice, and on the hero note the credit/equity gaps are 0.78 vs 0.83 and 0.40 vs
0.41 — noise. Direction only; no magnitude claimed.

### What can be said

> There is **one axis with real support: trained versus untrained**, carried by
> which direction of news captures attention. Within the professionals the
> differences are consistent in direction and slight in size, and two documents
> is not enough to call them role identities. There is no evidence here for four
> distinct genomes.

That is a smaller claim than "each role has a DNA", and it is the one the data
carries. The fix is cheap and obvious: more documents. Each additional stimulus
scored the same way turns a coin-flip into a trend, and the machinery to do it is
already built.

Also worth noting against §2.1: **reading position is the weakest trait of the
six.** The "professionals in the middle, untrained at the ends" pattern visible in
the lead figure is a property of the hero note, not of the roles. The figure is
labelled with its document for that reason.

---

## 6. What is still unknown

1. **No human has validated any of it.** `pipeline/src/cmp/human.py` ranks a real
   person's markup against the four personas. It has never been run against a real
   person. Three practitioners and one afternoon would close it, and a *mismatch*
   would be the most informative result this project could produce.

2. **No published study measures these roles.** Nothing compares a credit analyst,
   an equity PM, a risk officer and a retail investor reading the same document. It
   appears not to exist. Everything here is argued from mandates.

3. **Two calibration constants are unverified** (r = 0.27, r = −0.43), taken from
   secondary sources because the paper is paywalled.

4. **Cross-domain transfer is assumed.** The effect sizes come from medicine,
   sport, aviation and music, applied to financial prose.

5. **A language model is not an expert.** Sampling bounds the variance. Nothing
   here bounds the bias.

---

## 7. Reproducing it

```bash
cd pipeline && uv sync && uv run pytest        # 198 tests, no network
uv run python -m cmp.from_samples scored/subagent-run2   meridian-q4
uv run python -m cmp.from_samples scored/subagent-heldout aldercroft-h1
python3 ../viz/build.py && open ../viz/dist/index.html
```

Every sample from all three scoring runs is committed under `pipeline/scored/`:
`subagent-run1` (the failed untightened run), `subagent-run2` (the hero note), and
`subagent-heldout` (the validation). The failure is kept deliberately, so the
before-and-after in §4.3 is auditable rather than asserted.

With API credentials, `python -m cmp calibrate <stimulus> --k 5` does the same
thing through the Anthropic API instead of subagents.
