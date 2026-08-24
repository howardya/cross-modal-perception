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

### 2.6 Three real filings: the bracket does not close, and the signatures meet their limit

Every document above was written by the author of this project. Two more were
not: **Whirlpool Corporation's** and **Alamo Group's** Q2 2026 results releases,
verbatim from EDGAR, 31 and 35 clauses, both picked by a rule fixed before
reading them so that no filing could be chosen for being interesting. Full method
and audit trail in `calibration.md` §7.6 and §7.7.

| | Hero (built to divide) | Held-out (not) | **Whirlpool** | **Alamo** | **Jazz** |
|---|---|---|---|---|---|
| L1 acceptance | pass | pass | **fail — risk officer** | pass | pass |
| Mean top-k overlap | 37.5% | 50.0% | **52.1%** | **31.2%** | **47.9%** |
| Valence conflicts | 5 | 1 | **0** | 1 | 0 |

**With one real filing this section claimed the true overlap was 52.1% and that
§2.5's "constructed notes inflate by a third" had held. The second came in at
31.2%, below the hero note, and that claim was withdrawn; the third at 47.9%.**
Across five documents the overlap runs 31% to 52%; the two constructed notes sit
inside the range the three real ones span, not to one side of it. What survives is weaker and
more useful: **how much two readers share is mostly a property of the document,
and no single percentage is a property of the four mandates.**

The valence result mostly holds — five conflicts on the hero note against one,
one and zero elsewhere — but the honest version is about how rarely a document
contains a sentence like a debt-funded buyback, not that professionals and
amateurs never disagree.

**Whirlpool fails, and the failure is the most useful thing here.** The risk
officer attended no more than the untrained reader to the clauses its mask
predicted. That mask was built from this reader's own signature in §5b — *stops at
reassurance* — so it was an out-of-sample test of that claim, and the four
reassurance sentences came out ranked 23rd to 26th of 31. It read the balance
sheet instead.

**Alamo says which thing was wrong.** Its risk-officer mask was written from the
*mandate* rather than from that signature, and on it the reader passes every
check, attending 1.78x harder than the novice to what the mandate predicts. So
the persona was never mis-specified. **The sentence in this document was.** A
description written by reading two documents we wrote did not survive a document
we did not.

**The load-bearing claim strengthened three times and then met its limit.**

| Reader | 2 documents | 3 | 4 | **5** |
|---|---|---|---|---|
| risk officer | +0.79 | +0.78 | +0.80 | **+0.74** |
| retail investor | +0.78 | +0.76 | +0.81 | **+0.58** |
| credit analyst | +0.90 | +0.91 | +0.92 | **+0.52** |
| equity PM | +0.54 | +0.54 | +0.54 | **+0.50** |

The fifth document is a pharmaceutical release that never mentions borrowings,
despite the issuer carrying $3.34bn of long-term debt. Two of the seven topics —
*what is owed* and *cash* — have no clauses in it at all. **The signatures travel
across documents that talk about money owed, and do not travel to one that does
not.** That is a smaller claim than "they strengthen every time", and it is the
one the evidence supports.

**Which reader falls is the interesting part.** The credit analyst is defined by
the two absent topics; on this document its tallest bar becomes *how it did* — the
topic it is otherwise defined by skipping — and it shares five of its top eight
clauses with the untrained reader, more than with any professional. *Deprived of
its subject matter, the specialist reads like an amateur.*

The risk officer barely moves, and *how it did* is its deepest bar here by the
widest margin anywhere in the study. Its signature is an **absence**, and an
absence needs nothing from the document: a reader can refuse to read the results
of any company, whereas a reader looking for covenants needs a document that has
some. **Signatures built from an absence travel further than signatures built from
a presence** — not designed, not predicted, and invisible until a document arrived
that could not express half the taxonomy. How much of the fall is mechanical (two
topics pinned at zero compress the correlation on their own) cannot be separated
from how much is a real limit, with one such filing. See `calibration.md` §7.8.

Note *which* half of the risk officer's signature broke. *Stops at reassurance* is
a claim about particular sentences and it failed. *Refuses to read the results* is
a claim about a whole topic and it held — performance is its deepest bar on all
four documents. That is exactly the difference the topic axis was introduced to
draw.

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

**Refuted out of sample.** On the first real filing (§2.6) this reader walked past
every reassurance sentence in the document — ranks 23 to 26 of 31 — and read the
balance sheet instead. On the second it was scored against its mandate rather than
against this description, and passed comfortably. **This sentence, not the reader,
is what failed.** It holds on constructed prose and is not established generally. Nothing in its mandate says to attend to hedged
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

| Reader | Two documents | Four | **Five, three of them real** |
|---|---|---|---|
| credit analyst | **+0.90** | +0.92 | **+0.52** |
| risk officer | +0.79 | +0.80 | **+0.74** |
| retail investor | +0.78 | +0.81 | **+0.58** |
| equity PM | +0.54 | +0.54 | **+0.50** |

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

The untrained reader's deepest blind spot anywhere in the study is now a sentence
from a real filing: Alamo Group reporting that six months of operations threw off
$22.7m of cash while investing consumed $171.6m, with $37.3m borrowed to bridge
the gap (−4.3). A company spending seven times what it earned, funded from
outside. The covenant-amendment row above (−4.1) is the constructed equivalent,
and it is the weaker example precisely because somebody wrote it to be one. *The
one person who most needs the warning is the one person built not to see it* — and
that holds whether or not anyone intended the sentence to warn them.

### What this is and is not

It is a **signature**, not a genome: enough to say what kind of sentence each
reader stops at, and the themes hold across four documents sharing no subject
matter — but not across the fifth, which cannot express two of the seven topics
and on which three of the four correlations fall sharply (§2.6). It is not evidence that these resemble real professionals — every reader
here is a language model given a mandate, and five documents is a small basis.
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

4. **Three real filings show a range, not a value, and a boundary.** Overlap came
   out at 52.1%, 31.2% and 47.9%, so the honest answer to "how much do these
   readers share" is "it depends on the page". The fifth document also showed where
   the reader signatures stop travelling — to a filing that never mentions
   borrowings. A second such filing is the specific thing needed next, to separate
   mechanical compression from a real limit on the taxonomy (`calibration.md` §7.8).

5. **Cross-domain transfer is assumed.** The effect sizes come from medicine,
   sport, aviation and music, applied to financial prose.

6. **A language model is not an expert.** Sampling bounds the variance. Nothing
   here bounds the bias.

---

## 7. Reproducing it

```bash
cd pipeline && uv sync && uv run pytest        # 326 tests, no network
uv run python -m cmp.from_samples scored/subagent-run2   meridian-q4
uv run python -m cmp.from_samples scored/subagent-heldout aldercroft-h1
uv run python -m cmp.from_samples scored/subagent-whirlpool  whirlpool-q2   # exits 1: see 2.6
uv run python -m cmp.from_samples scored/subagent-alamo      alamo-q2
uv run python -m cmp.from_samples scored/subagent-jazz       jazz-q2
python3 ../viz/build.py && open ../viz/dist/index.html
```

Every sample from all three scoring runs is committed under `pipeline/scored/`:
`subagent-run1` (the failed untightened run), `subagent-run2` (the hero note), and
`subagent-heldout` (the validation). The failure is kept deliberately, so the
before-and-after in §4.3 is auditable rather than asserted.

With API credentials, `python -m cmp calibrate <stimulus> --k 5` does the same
thing through the Anthropic API instead of subagents.
