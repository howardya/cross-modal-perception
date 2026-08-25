# Findings

What this project actually found, as opposed to what it set out to find.

Three companion documents: [`OBJECTIVE.md`](OBJECTIVE.md) is what we meant to
build, [`research-note.md`](research-note.md) is what the literature says, and
[`calibration.md`](calibration.md) is the argument written for someone trying to
disbelieve the result. This file is the record of conclusions.

---

## 1. In one paragraph

Seven reading mandates — credit analyst, distressed debt investor, risk officer,
short seller, equity portfolio manager, financial journalist, retail investor —
were applied to five financial documents by a language model, five independent
times each: **175 runs in one sweep**. Two documents were written for this
project; three are real SEC filings nobody here wrote. Every reading is checked
against constraints derived from the perceptual-expertise literature, and three of
the five documents fail one of those checks for one reader each — reported, not
tuned (§2.7). The readings are reproducible (Krippendorff's α 0.79–0.98).

The central result was never the one the project set out to show, and it has now
been sharpened twice. At four readers it looked like this: **the experts do not
disagree about what is good or bad news, only about what to look at.** That
survives a fresh sweep exactly — the credit analyst, equity PM and risk officer
produce **zero** valence conflicts with each other on all five documents, and they
are the *only* three pairs in the study that do. But adding a short seller and a
distressed investor showed what was really holding it up: **not expertise, but a
shared payoff direction.** All three original experts are on the same side of the
trade. Put a reader on the other side and disagreement appears everywhere — 158
conflicts across the seven readers. The valence conflicts with the untrained
reader still
on the one real filing in the study there are no valence conflicts at all, which
turns out to say more about constructed documents than about readers.

---

## 2. The headline results

### 2.1 Experts diverge in attention, not judgement

Of the eight clauses each reader dwells on most, how many are shared. With seven
readers there are 21 pairs per document; these are the six lowest and the rest of
the top on the hero note:

| Pair | Shared, hero note |
|---|---|
| equity PM vs retail investor | **1 / 8** |
| credit analyst vs retail investor | 2 / 8 |
| risk officer vs retail investor | 2 / 8 |
| distressed investor vs retail investor | 2 / 8 |
| short seller vs retail investor | 2 / 8 |
| financial journalist vs retail investor | 2 / 8 |
| … every professional pair | 4 / 8 – 7 / 8 |

**The six lowest-overlap pairs in the document are the six that contain the
untrained reader.** That is a stronger version of the original result, not a
weaker one: adding three more professionals — including two whose payoff is
inverted and one who is not a financial professional at all — did not produce a
single professional pair that reads the page as differently as any professional
reads it from an amateur.

The full 21-pair comparison is in the report's reader × reader matrix rather than
here; a table of 21 rows per document is not a finding, it is a data dump.

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

**Two corrections, in opposite directions.**

*First:* scored on the real filings, the original four readers produce almost no
valence conflicts at all — zero, one and zero. The sentences above were written by
this project, and a debt-funded buyback set beside collapsing cash conversion is a
constructed juxtaposition. The professional-versus-lay divide is real wherever a
document contains such a sentence; how often real documents do is not established.
See §2.6.

*Second, and larger:* the claim that the divide is **professional versus lay** was
an artefact of which professionals were in the room. All three were on the same
side of the trade. The seven-reader sweep gives:

| | Valence conflicts |
|---|---|
| credit analyst / equity PM / risk officer, among themselves, all five documents | **0** |
| every other pair, across the study | **158** |
| pairs with zero conflicts anywhere | **exactly those three** |

A short seller disagrees with everyone (75 conflicts); so does the journalist (62),
which has no position at all and is answering a different question — *is this a
story* rather than *is this good for me*. The distressed investor, whose inversion
is structural rather than stipulated, disagrees least of the added readers (23).

So: **experts who share a payoff direction agree about good and bad news.
Expertise as such does not produce that agreement.** The original finding was
right about the data and wrong about the cause. `calibration.md` §7.9.

### 2.3 Expertise concentrates attention, as predicted

| Persona | Hero | Held-out | Whirlpool | Alamo | Jazz |
|---|---|---|---|---|---|
| distressed investor | 0.065 | 0.074 | 0.089 | 0.099 | 0.091 |
| credit analyst | 0.059 | 0.062 | 0.082 | 0.084 | 0.063 |
| risk officer | 0.045 | 0.048 | 0.068 | 0.054 | 0.066 |
| short seller | 0.049 | 0.055 | 0.062 | 0.058 | 0.055 |
| equity PM | 0.041 | 0.059 | 0.065 | 0.056 | 0.049 |
| financial journalist | 0.043 | 0.069 | 0.056 | 0.057 | 0.042 |
| retail investor (baseline) | 0.025 | 0.028 | 0.019 | 0.017 | 0.024 |

**Every expert is more concentrated than the lay reader on every one of the five
documents — thirty out of thirty.** This is the one place the literature's
prediction reproduces cleanly, and it is the only claim in this file that has
survived every extension without qualification.

It also survives the hardest case available: the **financial journalist** is a
trained reader who is not a financial professional, added specifically to test
whether the concentration effect was measuring expertise or merely numeracy. It
concentrates 1.7× to 2.5× the lay reader on all five documents, on a completely
different set of topics. Information reduction is not a property of reading
numbers.

### 2.4 It is reproducible

Krippendorff's α across five independent runs per persona — each a fresh model
context, blind to the others:

Across the 175-run sweep the range is **0.79 – 0.98**. On the hero note:

| Persona | Hero |
|---|---|
| credit analyst | 0.983 |
| distressed investor | 0.971 |
| retail investor | 0.964 |
| risk officer | 0.931 |
| short seller | 0.929 |
| financial journalist | 0.921 |
| equity PM | 0.901 |

Thirty-four of the thirty-five reader-document pairs clear the 0.80 convention.
The exception is the distressed investor on `jazz-q2` at 0.79 — and because its
attention there is *concentrated* (0.091) rather than diffuse, that is the
**erratic** reading rather than the harmless one, and it fails L1 accordingly
(§2.7). **This measures consistency, not correctness** — a reader could be
reproducibly wrong and score exactly as well.

### 2.5 The constructed note inflates the effect by about a third

*Measured at four readers. The figures below are the four-reader values and are
kept as the record of that stage; §2.7 gives the seven-reader numbers, which are
higher on almost every document because more readers means more pairs that
resemble each other.*

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

*Also measured at four readers.*

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

### 2.7 Seven readers: what a shared payoff was really doing

Three readers were added — a **distressed debt investor** and a **short seller**,
both with payoffs that run against the original three, and a **financial
journalist**, a trained reader who is not a financial professional — and
everything was re-scored in one 175-run sweep so that the reader average every
lift is measured against comes from a single model generation. Method, mask
discipline and the full accounting in `calibration.md` §7.9.

**The result the inverted readers were added to test is in §2.2 and it is the
main finding of this stage.** Three more things came with it.

**The seven-reader overlap numbers are higher, and that is arithmetic, not
signal.** More readers means more pairs, and the added pairs are mostly
professional-to-professional:

| | Hero | Held-out | Whirlpool | Alamo | Jazz |
|---|---|---|---|---|---|
| Mean top-k overlap, 7 readers | 55.4% | 47.6% | 61.9% | 33.9% | 52.4% |
| (at 4 readers) | 37.5% | 50.0% | 52.1% | 31.2% | 47.9% |

The ordering across documents barely moves — Alamo lowest, Whirlpool highest,
both times. The level is not comparable across reader counts and should never be
quoted without one.

**Three documents now fail L1**, kept and reported rather than tuned:

| Document | Reader | Why |
|---|---|---|
| hero note | financial journalist | attends no harder than the untrained reader to what its mandate predicts |
| Whirlpool | risk officer | reproduces the §2.6 failure against the same signature-derived mask |
| Jazz | distressed investor | α 0.79 with concentrated attention — *erratic*, the genuine failure mode |

The journalist's failure is the informative one: it fails on the **constructed**
note and passes on all four others. `meridian-q4` was written by someone thinking
about lenders and shareholders, so there is little in it for a journalist's
mandate to grip. That is a fact about the stimulus.

**The re-base moved published numbers, and they were corrected rather than
defended.** The photographic-negative mirror is now half true (§5b); the risk
officer's absence holds on four of five documents, not five; the weakest profile
is the short seller, not the equity PM; and the six statistical traits of §5b no
longer reproduce across sweeps at all — recorded as not reproducing rather than
refitted, which is what §7.7 of `calibration.md` promised when it committed to
reporting between-sweep disagreement.

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

Can the readers be reduced to something compact that *means* something?

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
looked at, seven categories used identically on all five documents — and a reader's
attention becomes a profile over **topics** rather than over one document's
layout. That is the fix for the trait that failed earlier: reading position was
document-specific because its axis was position. Topic is not; "what is owed"
exists in any filing.

The profiles travel:

| Reader | 2 docs | 4 docs | 5 docs | **5 docs, 7 readers** |
|---|---|---|---|---|
| risk officer | +0.79 | +0.80 | +0.74 | **+0.72** |
| equity PM | +0.54 | +0.54 | +0.50 | **+0.60** |
| retail investor | +0.78 | +0.81 | +0.58 | **+0.59** |
| distressed investor | — | — | — | **+0.57** |
| credit analyst | **+0.90** | +0.92 | +0.52 | **+0.56** |
| financial journalist | — | — | — | **+0.48** |
| short seller | — | — | — | **+0.37** |

Two things move these: adding documents, and adding readers. The fifth document
(`jazz-q2`, which contains nothing about debt or cash) is what dropped the credit
analyst from +0.92 to +0.52; the three new readers then re-based every figure
again. The **risk officer is now the most stable profile in the study**, and it is
the one defined by an absence — which is the same result as before, arrived at
from a different direction.

And they are readable as shapes. Mean lift in points of attention above or below
the seven-reader average, across all five documents:

| Reader | debt | cash | perform | share | depend | language | events |
|---|---|---|---|---|---|---|---|
| credit analyst | **+9.5** | +2.0 | −2.5 | −0.2 | −1.5 | −3.5 | −3.8 |
| distressed investor | **+12.0** | +1.1 | −4.6 | +0.4 | −2.8 | −1.7 | −4.3 |
| risk officer | +2.4 | +0.2 | **−8.0** | −1.6 | +1.2 | +1.3 | +4.5 |
| short seller | −5.8 | **+2.6** | +0.4 | −0.2 | +2.0 | +1.6 | −0.5 |
| equity PM | −5.9 | −0.5 | **+5.4** | +3.6 | +2.0 | −2.1 | −2.5 |
| financial journalist | −6.2 | −2.6 | +2.2 | −1.5 | −0.1 | +2.4 | **+5.7** |
| retail investor | −6.0 | −2.8 | **+7.1** | −0.5 | −0.9 | +2.1 | +1.0 |

Read a column and the readers sort themselves. *What is owed* is positive for
exactly two of seven — and they are the two whose job is being repaid.

**The credit analyst and the untrained reader are photographic negatives — but
only half of that survived the seven-reader re-base.** The credit analyst's
tallest topic is still *what is owed* and the untrained reader's deepest is still
*what is owed*. But the credit analyst's own deepest topic is no longer *how it
did*: three readers who ignore corporate events lifted the average there and took
its floor down with them. Nothing about the reader changed; the thing it is
measured against did. That is what "more theirs than anyone's" costs.

**The risk officer's signature is an absence.** *How it did* is its deepest bar on
four of the five documents, and by a wide margin — it is the only reader defined
chiefly by what it refuses to look at, which is exactly what the
information-reduction hypothesis predicts an expert would look like. It is also
the most stable profile here, and those two facts are probably the same fact: an
absence needs nothing from the document, whereas a reader looking for covenants
needs a document that has some.

The short seller is the weakest of the seven and its shape should not be treated as
established. The taxonomy is an author judgment, recorded in
`pipeline/stimuli/topics.json` with its two most arguable calls named; the check
that it is not simply encoding the answer is that the profiles survive a change
of document, which an arbitrary labelling would not.

### Every blind spot is somebody else's specialism

The gaps are not random. Line each reader's over-attended sentence up against the
reader who most walks past it, and the same sentences appear on both sides:

| Sentence | Caught by | Missed by |
|---|---|---|
| "A $150m convertible note matures in September 2027." | distressed investor **+6.7** | financial journalist **−4.9** |
| "The company holds $420m of cash and has no drawn debt." | distressed investor **+7.2** | short seller **−4.2** |
| "The company disclosed a security incident affecting a single-tenant deployment…" | financial journalist **+5.9** | equity PM **−4.0** |
| "The company continues to actively evaluate additional value-enhancing corporate development." | distressed investor **+4.8** | financial journalist **−3.9** |
| "Generated GAAP / non-GAAP adjusted earnings per share of $2.78 / $5.71…" | distressed investor **+4.7** | risk officer **−3.2** |

At four readers this table was mostly *professional catches it, amateur misses
it*. At seven the untrained reader has dropped out of it entirely, and every row
is one professional against another. The sharpest gaps in the study are no longer
between training and its absence — they are between two trained readers looking
for different things, which is a harder claim and a more interesting one.

The untrained reader's deepest blind spot anywhere is still a sentence from a real
filing: Alamo Group reporting that six months of operations threw off $22.7m of
cash while investing consumed $171.6m, with $37.3m borrowed to bridge the gap
(**−4.9**). A company spending seven times what it earned, funded from outside.
*The one person who most needs the warning is the one person built not to see it*
— and that holds whether or not anyone intended the sentence to warn them.

### What this is and is not

It is a **signature**, not a genome: enough to say what kind of sentence each
reader stops at, and the themes hold across four documents sharing no subject
matter — but not across the fifth, which cannot express two of the seven topics
and on which most correlations fall sharply (§2.6). It is not evidence that these resemble real professionals — every reader
here is a language model given a mandate, and five documents is a small basis.
What would settle it is the thing still missing from the whole project: a real
credit analyst, marking up the same page.

---

## 6. What is still unknown

1. **No human has validated any of it.** `pipeline/src/cmp/human.py` ranks a real
   person's markup against the seven personas. It has never been run against a real
   person. Three practitioners and one afternoon would close it, and a *mismatch*
   would be the most informative result this project could produce.

2. **No published study measures these roles.** Nothing compares a credit analyst,
   a distressed investor, a risk officer, a short seller, an equity PM, a financial
   journalist and a retail investor reading the same document. It appears not to
   exist. Everything here is argued from mandates.

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

7. **The payoff finding rests on two inverted readers.** §2.2 concludes that a
   shared payoff direction, not expertise, is what produces valence agreement. That
   rests on a short seller and a distressed investor — both written here, both
   sharing the same author and the same prompt scaffolding as the readers they
   disagree with. A real short seller might disagree differently, or less. The
   control that would settle it is the same one every other open item points at: a
   human doing the same markup.

---

## 7. Reproducing it

```bash
cd pipeline && uv sync && uv run pytest        # 326 tests, no network

# the study of record: seven readers, one sweep
uv run python -m cmp.from_samples scored/sweep-meridian-q4    meridian-q4   # exits 1: see 2.7
uv run python -m cmp.from_samples scored/sweep-aldercroft-h1  aldercroft-h1
uv run python -m cmp.from_samples scored/sweep-whirlpool-q2   whirlpool-q2  # exits 1: see 2.7
uv run python -m cmp.from_samples scored/sweep-alamo-q2       alamo-q2
uv run python -m cmp.from_samples scored/sweep-jazz-q2        jazz-q2       # exits 1: see 2.7
python3 ../viz/build.py && open ../viz/dist/report.html
```

Every sample from every scoring run is committed under `pipeline/scored/`. The
`sweep-*` directories are the current study of record — seven readers × five
documents × five samples, 175 runs, one model generation. The earlier runs are
kept and were not consulted while building the current fixtures:
`subagent-run1` (the failed untightened run), `subagent-run2` and
`subagent-heldout` (the original four-reader pair), and `subagent-whirlpool`,
`subagent-alamo` and `subagent-jazz` (the four-reader real filings). The failures
are kept deliberately, so the before-and-after in §4.3 and the between-sweep
disagreement in §2.7 are auditable rather than asserted.

With API credentials, `python -m cmp calibrate <stimulus> --k 5` does the same
thing through the Anthropic API instead of subagents.
