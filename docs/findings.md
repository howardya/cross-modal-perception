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
back from every tuning decision, and then to a real SEC filing nobody here wrote,
which it partly fails — informatively (§2.6). The central result is not the one the project
was designed to show. **The three experts do not disagree with each other about
what is good or bad news. They disagree about what to look at.** The only genuine
valence conflicts are between professionals and the untrained reader, and they
land on the two sentences an ordinary investor would find most reassuring — and
on the one real filing in the study there are no valence conflicts at all, which
turns out to say more about constructed documents than about readers.

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

**This does not reproduce on a real document.** Scored on a genuine SEC filing,
the four readers produce **zero** valence conflicts, between any pair. The
sentences above were written by this project, and a debt-funded buyback set beside
collapsing cash conversion is a constructed juxtaposition. The divide is real
whenever a document contains such a sentence; what is not established is how often
real documents do. See §2.6 and `calibration.md` §7.6.

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
third smaller. A real filing later put the number at 52.1% — see §2.6.

### 2.6 A real filing closes the bracket, and costs the risk officer half its signature

Every document above was written by the author of this project. The third was
not: **Whirlpool Corporation's Q2 2026 results release**, verbatim from EDGAR, 31
clauses, picked by a rule fixed before reading it so that no filing could be
chosen for being interesting. Full method and audit trail in `calibration.md`
§7.6.

| | Hero (built to divide) | Held-out (not) | **Real filing** |
|---|---|---|---|
| L1 acceptance | pass | pass | **fail — risk officer** |
| Mean top-k overlap | 37.5% | 50.0% | **52.1%** |
| Valence conflicts | 5 | 1 | **0** |

**The run fails, and the failure is the finding.** The risk officer attends no
more than the untrained reader to the clauses its mandate predicts. Its mask was
built from its own signature in §5b — *stops at reassurance* — so this was an
out-of-sample test of that claim, and the four reassurance sentences came out
ranked 23rd to 26th of 31. It read the balance sheet instead. Eight of the 31
clauses are management framing: when everything is reassurance, reassurance stops
being a signal, and what looked like a reader's instinct may have been a property
of documents where comfort was rare.

**Two headline claims weaken. The load-bearing one strengthens.** The topic
profiles travel to the third document nearly unchanged — credit analyst +0.90 to
+0.91, risk officer +0.79 to +0.78, retail investor +0.78 to +0.76, equity PM
+0.54 unmoved. Two documents was a coin landing twice; three, one of them written
by strangers for another purpose, is the first real evidence that the signatures
belong to the readers.

Note *which* half of the risk officer's signature broke. *Stops at reassurance* is
a claim about particular sentences and it failed. *Refuses to read the results* is
a claim about a whole topic and it held — performance is still its deepest bar on
all three documents. That is exactly the difference the topic axis was introduced
to draw, and this is the first run where the two came apart.

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

## 5b. A signature for each reader

Can the four readers be reduced to something compact that *means* something?

**A first attempt failed and is worth recording.** Six statistical traits were
computed — threat pull, baseline mood, focus, chunking, alarm, reading position —
and checked for stability across both documents. One survived. It was accurate
and useless: "threat pull is the negative correlation of salience with valence"
is a number about a number, and the thing it showed was one the attention tables
already showed better. A signature made of distribution shapes says nothing you
can act on.

The question a signature should answer is concrete: **what kind of sentence makes
this reader look up, and what do they walk straight past while everyone else
stops?** Both halves come from one number — a reader's share of attention on a
sentence, minus the average share across all four. Implemented in
`pipeline/src/cmp/lift.py`; report via `python -m cmp.profile`.

### The four signatures

Two sentences per reader from each document, so a theme appearing on both is a
property of the reader rather than of the page.

| Reader | Stops at | Walks past |
|---|---|---|
| **Credit analyst** | Anything that is a claim on cash — what is owed, when it falls due, what it costs | The story being told about the business |
| **Equity PM** | What a single share is worth — margin, dilution, what was excluded from the adjusted number | The balance sheet, and anything that is not a number |
| **Risk officer** | Reassurance | How the business actually performed |
| **Retail investor** | Headline numbers, firsts and streaks, and things you can picture | The machinery — debt terms, accounting adjustments, retention |

### The risk officer stops at being told not to worry

Its two strongest sentences on the held-out note are the disclosure of a security
incident and the sentence saying nobody was harmed by it — *"No customer data was
exfiltrated, according to a third-party forensic review"* (+5.1). On the hero note
one of its signatures is *"Management described the renewal pipeline as
constructive"* (+1.4).

Three reassurances, two documents, one reader. **It is the only reader that treats
a denial as information.**

**Refuted out of sample.** On the real filing added later (§2.6) this reader
walked past every reassurance sentence in the document — ranks 23 to 26 of 31 —
and read the balance sheet instead. This claim should now be read as holding on
constructed prose and not established generally. Nothing in its mandate says to attend to hedged
comfort; it says to look for what could go wrong. Reassurance is where it went
looking.

Its blind spots are the mirror of that: adjusted EBITDA (−1.6), revenue (−1.5),
the company's first-ever positive operating income (−4.1). **It does not care how
the business did.**

### The reader drawn as a shape

Give every sentence a topic — what it is *about*, assigned before any score was
looked at, seven categories used identically on both documents — and a reader's
attention becomes a profile over **topics** rather than over one document's
layout. That is the fix for the trait that failed earlier: reading position was
document-specific because its axis was position. Topic is not; "what is owed"
exists in any filing.

The profiles travel:

| Reader | Two documents | **Three, incl. a real filing** |
|---|---|---|
| credit analyst | **+0.90** | **+0.91** |
| risk officer | +0.79 | +0.78 |
| retail investor | +0.78 | +0.76 |
| equity PM | +0.54 | +0.54 |

And they are readable as shapes. Lift in points of attention above or below the
four-reader average, hero note first:

| Reader | Strongest topic | Weakest topic |
|---|---|---|
| credit analyst | **what is owed** (+9.6, +13.8) | how it did (−5.4, −3.4) |
| retail investor | **how it did** (+10.6, +5.0) | what is owed (−11.2, −4.2) |
| risk officer | what happened / how it is described | **how it did (−7.9, −9.7)** |
| equity PM | how it did, per share | what happened |

**The credit analyst and the untrained reader are photographic negatives.** One
reads what the company owes and skips how it did; the other reads how it did and
skips what it owes. Their strongest and weakest topics are each other's, on both
documents.

**The risk officer's signature is an absence.** *How it did* is its deepest bar on
both documents — it is the only reader defined chiefly by what it refuses to look
at, which is exactly what the information-reduction hypothesis predicts an expert
would look like.

The equity PM is the weakest of the four and its shape should not be treated as
established. The taxonomy is an author judgment, recorded in
`pipeline/stimuli/topics.json` with its two most arguable calls named; the check
that it is not simply encoding the answer is that the profiles survive a change
of document, which an arbitrary labelling would not.

### Every blind spot is somebody else's specialism

The gaps are not random. Line each reader's over-attended sentence up against the
reader who most walks past it, and the same sentences appear on both sides:

| Sentence | Caught by | Missed by |
|---|---|---|
| "…agreed an amendment with its lending syndicate, raising the maximum permitted leverage covenant…" | credit analyst **+2.0** | retail investor **−4.1** |
| "Net leverage stands at 4.1x adjusted EBITDA, against 2.9x a year ago." | credit analyst **+2.2** | retail investor **−3.4** |
| "…reported fourth-quarter revenue of $1.42bn, up 19% year on year." | retail investor **+3.3** | risk officer **−1.5** |
| "No customer data was exfiltrated, according to a third-party forensic review." | risk officer **+5.1** | equity PM **−3.8** |
| "The company holds $420m of cash and has no drawn debt." | credit analyst **+4.8** | equity PM **−3.7** |

The first row is the sharpest result in the study. The sentence saying the company
went to its lenders for permission to carry more debt is the **untrained reader's
deepest blind spot anywhere here** — and one of the credit analyst's strongest
signals. *The one person who most needs that warning is the one person built not
to see it.*

### What this is and is not

It is a **signature**, not a genome: enough to say what kind of sentence each
reader stops at, and the themes hold across three documents sharing no subject
matter — one of them a real SEC filing, on which one reader's signature was
half refuted (§2.6). It is not evidence that these resemble real professionals — every reader
here is a language model given a mandate, and three documents is a small basis.
What would settle it is the thing still missing from the whole project: a real
credit analyst, marking up the same page.

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

4. **One real filing is a data point, not a distribution.** §2.6 rests on a single
   genuine document. Whether 52.1% overlap and zero valence conflicts are typical
   of real filings, or a property of this one, needs more of them — and that is
   now the cheapest useful thing left to do besides the human check.

5. **Cross-domain transfer is assumed.** The effect sizes come from medicine,
   sport, aviation and music, applied to financial prose.

6. **A language model is not an expert.** Sampling bounds the variance. Nothing
   here bounds the bias.

---

## 7. Reproducing it

```bash
cd pipeline && uv sync && uv run pytest        # 313 tests, no network
uv run python -m cmp.from_samples scored/subagent-run2   meridian-q4
uv run python -m cmp.from_samples scored/subagent-heldout aldercroft-h1
uv run python -m cmp.from_samples scored/subagent-whirlpool  whirlpool-q2   # exits 1: see 2.6
python3 ../viz/build.py && open ../viz/dist/index.html
```

Every sample from all three scoring runs is committed under `pipeline/scored/`:
`subagent-run1` (the failed untightened run), `subagent-run2` (the hero note), and
`subagent-heldout` (the validation). The failure is kept deliberately, so the
before-and-after in §4.3 is auditable rather than asserted.

With API credentials, `python -m cmp calibrate <stimulus> --k 5` does the same
thing through the Anthropic API instead of subagents.
