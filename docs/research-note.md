# Research Note — Perceptual Expertise and Cross-Modal Correspondence

**Phase 1 deliverable.** Evidence base for the quantification model (Phase 2) and the source
for the demo's own "how much should you trust this" panel.

Scope: what the published literature actually supports about (a) how expertise changes what a
person perceives in a stimulus, and (b) how the senses map onto each other — plus, explicitly,
what it does **not** support. Section 9 lists the gaps; they are as load-bearing as the findings.

---

## 1. Headline

Four things came out of this survey, two of which contradict what the project assumed at the
outset and have already changed the design.

1. **The robust expertise signature is *where* attention goes, not *how* the eye moves.**
   The popular "experts make fewer, longer fixations" story is not reliably supported. A
   101-study review found more null than significant results for fixation duration and count,
   while gaze *location* differences held up (§2.3). This is good news: location is precisely
   what this project renders.

2. **Expertise suppresses the irrelevant roughly twice as strongly as it enhances the relevant.**
   The meta-analytic correlations are r = 0.27 for fixation duration on task-relevant areas
   versus r = −0.43 on task-redundant areas — about d ≈ 0.56 against d ≈ −0.95 (§2.1). The
   headline of expertise is *learned blindness*, not sharper sight. This asymmetry becomes the
   model's primary calibration target.

3. **Attention is a finite, zero-sum budget — measured, in a financial document.** In the one
   good finance-domain eye-tracking study, directing readers to one audit matter pulled them to
   the related note ~207 seconds faster; directing them to *three* matters worked measurably
   *less* well per matter, and attention to highlighted sections came out of attention to
   everything else (§3). Salience in the model must therefore be normalised, not free.

4. **Two claims the project planned to make are wrong as stated.** The bouba/kiki effect is
   **72%**, not the ~95% often quoted, and it inverts in some languages (§4.1). The synaesthetic
   "pop-out" is **not** pop-out — the advantage is real but modest and not pre-attentive (§4.2).
   Both are corrected below, and both corrections make the piece *better*, because the honest
   versions map more accurately onto expertise, which is also partial and also fallible.

---

## 2. Perceptual expertise

### 2.1 The core meta-analysis

Gegenfurtner, Lehtinen & Säljö (2011) pooled **296 effect sizes** from eye-tracking studies of
expertise in visualization comprehension, across **819 experts, 187 intermediates and 893
novices** in professional domains including medicine, transport and sport.

Direction of findings — experts, relative to non-experts:

| Measure | Direction in experts |
|---|---|
| Fixation duration | Shorter |
| Fixations on task-relevant areas | More |
| Fixations on task-redundant areas | Fewer |
| Saccade length | Longer |
| Time to first fixation on relevant information | Shorter |

The reported correlations for fixation duration by area type are **r_relevant = 0.27** and
**r_redundant = −0.43**. Converting with *d* = 2*r*/√(1−*r*²):

- relevant areas: **d ≈ 0.56** (moderate)
- redundant areas: **d ≈ −0.95** (large)

> ⚠️ **Verification status.** These two *r* values were obtained from secondary sources
> summarising the paper; the article itself is paywalled and was not read in full. The
> *direction* of all findings is confirmed by the abstract and by the author's open-access
> habilitation. The two numeric values should be checked against the original before they are
> quoted publicly. They are used here as approximate targets, not as precise constants.

The authors' explanation is superiority in **parafoveal processing** (a wider effective visual
span, hence longer saccades) and **selective attention allocation**.

### 2.2 Information reduction

Haider & Frensch's **information-reduction hypothesis** (1996; 1999) holds that with practice,
information not logically required for the task is progressively *discarded from processing*.
Skill acquisition changes not only how information is processed but **what** information is
processed at all.

Two properties matter for this project:

- It predicts the r_relevant / r_redundant asymmetry above, and is the mechanism behind it.
- It is **partially under voluntary control** — the amount of reduction varies with task
  instruction. Expertise is therefore not a fixed lens; it is a lens plus a current task. The
  model's personas must accordingly encode a *mandate*, not merely an identity.

This is the theoretical spine of the whole project and should be named explicitly in the demo:
**an expert is someone who has learned what to ignore.**

### 2.3 The important counter-evidence

Klostermann & Moeinirad (2020), *German Journal of Exercise and Sport Research* — a PRISMA
review of **101 studies** of expert gaze in sport — directly challenges the standard account:

- For **fixation duration** and **number of fixations**: results were unclear, with *more
  studies reporting non-significant than significant* effects.
- For **gaze location** and **quiet-eye duration**: expert/novice differences did hold.

Note also that this contradicts Gegenfurtner's *direction* as well as its reliability: the sport
literature's classic claim is that experts fixate *longer*, while the visualization meta-analysis
finds *shorter*. The measure is evidently task-dependent, and neither direction generalises.

**Design consequence (already applied):** the model treats micro-timing measures as weakly
supported and builds on **salience/location**, which survives both literatures. Any
fixation-duration-style channel is illustrative only and must be labelled as such.

### 2.4 Chunking

The Chase & Simon lineage establishes that experts perceive larger meaningful units. In music
this is directly measured as the **eye-hand span** — the number of notes the eye leads the hand
by: **0.52–3.69 notes for novices versus 1.73–6.8 for skilled musicians** (see §5). Note the
overlap between the ranges: a skilled musician's floor sits below a novice's ceiling. Expertise
shifts a distribution; it does not create two separate species. The demo should not imply
otherwise.

---

## 3. Finance-domain evidence

### 3.1 The one good study

Sirois, Bédard & Bera, *The Informational Value of Key Audit Matters in the Auditor's Report:
Evidence from an Eye-Tracking Study* (**Accounting Horizons** 32(2), 2018).

**Method.** 98 post-graduate accounting students at a large Canadian university, randomly
assigned to four groups differing in the Key Audit Matters (KAM) section of the auditor's
report: group A (control, no matters), group B (one matter, referring to note 5), groups C and D
(three matters). Participants navigated a full set of financial statements while eye movements
were recorded. Measures included time to first fixation (TTFF), fixation count, fixation count
per word, and pages visited before reaching a note.

**Results.**

| Finding | Value |
|---|---|
| TTFF on note 5, vs control | **163.4 s (C), 187.0 s (D), 206.9 s (B) faster** |
| Pages visited before note 5, vs control | 5.7 (C), 5.8 (D), 8.3 (B) fewer |
| Note 1k, per unit of attention to its audit matter | 3.2 fewer pages, **138 s faster** TTFF |
| One matter vs three (B vs C, D) | B significantly stronger on both measures, *p* < .05 |
| Model fit | R² between 22% and 25% |

**Three usable conclusions.**

1. **Directed salience produces enormous shifts in attention** — over three minutes of
   difference in when a reader first looks at a specific note, in a realistic document.
2. **Attention is zero-sum.** Readers exposed to KAMs devote less attention to the remaining
   parts of the financial statements. Highlighting is not additive; it reallocates.
3. **Salience dilutes.** Highlighting three things directed attention *less* effectively than
   highlighting one. This is a quantitative constraint on how concentrated a persona's salience
   distribution can plausibly be, and it argues against a model that lets every persona mark
   many things as maximally important.

### 3.2 Supporting accounting work

- An eye-tracking study of non-explanatory **photographs** in an annual report's management
  summary, and their effect on performance judgments of non-professional investors and auditors
  — evidence that presentation, not only content, moves attention in financial documents.
- An eye-tracking experiment on **nudges and professional skepticism**, in which participants
  assessed 14 pieces of audit evidence.

### 3.3 The gap — stated plainly

**No published eye-tracking study was found comparing a credit analyst, an equity portfolio
manager, a risk officer and a retail investor reading the same document.** The finance case
study therefore cannot be calibrated role-by-role against measured data. It inherits:

- its **expert-vs-novice** structure from §2 (a cross-domain meta-analysis), and
- its **role differentiation** from an argument about mandates, not from measurement.

Further, Sirois et al.'s participants were **accounting students used as a proxy for
non-professional investors**, not practising professionals. Even the best finance-domain anchor
is not an expert sample.

This is the project's single largest limitation and it must appear in the demo, not only here.

---

## 4. Cross-modal correspondence

### 4.1 Bouba/kiki

Ćwiek et al. (2022), *Philosophical Transactions of the Royal Society B* 377(1841),
DOI 10.1098/rstb.2020.0390 — the definitive cross-cultural test.

**Method.** 917 participants, **25 languages**, 9 language families, **10 writing systems**.

**Results.**

| Quantity | Value |
|---|---|
| Overall congruent matches | **72%** (95% CrI 56–82%) |
| Logit intercept | +0.93 (SE 0.31), p(β₀>0) = 0.99 |
| Languages with reliable above-chance effect | 17 of 25 |
| *Bouba* → round, reliable in | 22 of 25 languages |
| *Kiki* → spiky, reliable in | **only 11 of 25 languages** |
| Roman vs non-Roman script | 75% vs 63% (weak; CI crosses zero) |
| Below 50% | Romanian (36%, lowest), Mandarin Chinese, Turkish |

**Corrections to the project's assumptions.** The commonly cited "~95%" figure is wrong; the
correct headline is **72%**. The effect is **asymmetric** — *bouba* carries it, *kiki* is far
weaker. And it is **not universal**: it reverses in at least three languages.

**Design consequence.** The demo must report 72%, and should treat a viewer who answers
"incongruently" as a genuine data point rather than an error. This is in fact a gift: roughly
one viewer in four will *not* match, which stages the project's thesis in the first ten seconds
of Act 1 — *even here, at the most basic sensory level, you and the person beside you differ.*

### 4.2 Grapheme–colour synaesthesia and the "pop-out" claim

The embedded-figures paradigm: a field of `5`s contains a shape made of `2`s. Because 2 and 5 are
near mirror images sharing features, non-synaesthetes must search serially. Grapheme–colour
synaesthetes report seeing the digits in different colours.

**Replication record — mixed, and weaker than the popular account.**

| Study | n | Result |
|---|---|---|
| Ramachandran & Hubbard (2001) | 2 synaesthetes | Advantage over controls; termed "pop-out" |
| Hubbard et al. (2005) | 6 | 5 of 6 outperformed controls |
| Rothen & Meier (2009) | 13 | **Failed to replicate** |
| Ward, Jonas, Dienes & Seth (2010) | 36 | Group advantage: **41.4% vs 31.5% correct** |
| Rich & Karstoft (2013) | — | At set-size 64: **1.87% vs 11.56% errors** |

**The correction.** Ward et al. concluded the effect is *not* pre-attentive pop-out: synaesthetic
colours do not guide attention the way real colours do, and the accuracy gain is far smaller
than genuine pop-out would predict. At the individual level much of the embedded-figures data
reflected synaesthetes being *slower* than matched controls.

**Design consequence — this changes Act 1.** The planned framing ("the 2s are simply *there*,
instantly") is not supported and must be dropped. The replacement is more interesting anyway:

> A synaesthete's advantage on this task is real but *partial* — roughly 41% correct against
> 31%. They are not magic. They have a head start.

That is a far better bridge to expertise, because expertise is also partial, also fallible, and
also merely a head start. The colourised rendering stays in the demo, clearly labelled as an
**illustration of reported experience**, not as a simulation of measured performance.

### 4.3 Other correspondences

Well-attested mappings, usable as the rendering vocabulary:

- **Pitch ↔ size**: large ↔ low pitch, small ↔ high pitch.
- **Pitch ↔ elevation**: high pitch ↔ high spatial position.
- **Pitch ↔ brightness**: high pitch ↔ brighter.

The **environmental-statistics account** holds that these track real-world regularities rather
than arbitrary convention — large objects genuinely do resonate lower. This matters for the
project: it licenses using these mappings as a shared visual language rather than an invented
code the viewer must be taught.

Evidence on origin is mixed and worth noting: pitch–size and pitch–weight are indistinguishable
between blind and sighted adults, while pitch–texture and pitch–softness appear in blind but not
sighted adults; and bouba/kiki plus the size–weight illusion are shaped by visual experience,
per studies of sight restoration after congenital blindness.

---

## 5. Music reading (case study b)

Perra, Latimier, Poulin-Charronnat, Baccino & Drai-Zerbib (2022), *Journal of Eye Movement
Research* 15(4):1. **12 studies, 512 participants, 61 comparisons** in four subsets.

| Subset | k | Hedges *g* [95% CI] | p | I² | Verdict |
|---|---|---|---|---|---|
| Fixation duration | 24 | **−0.72 [−1.15, −0.30]** | < .01 | **0%** | Robust; experts shorter |
| Number of fixations | 11 | −0.42 [−2.10, 1.26] | .548 | 84.4% | Not significant |
| Saccade amplitude | 8 | 0.061 [−0.27, 0.39] | .594 | — | Null, underpowered |
| Gaze duration | 11 | −1.20 [−2.39, −0.008] | .049 | — | Underpowered, unreliable |

No publication bias detected in subsets 1 and 2 (Egger's z = −0.96, p = .34; z = −0.27, p = .79).
**Moderator analyses yielded no reliable results** (df < 4). The authors conclude only subsets 1
and 2 were interpretable.

**Eye-hand span** (excluded from the meta-analysis as sight-reading-specific): novices
0.52–3.69 notes, skilled musicians 1.73–6.8 notes.

**Assessment.** This is the cleanest single number in the entire survey — *g* = −0.72 with
I² = 0% — but it is a *fixation duration* effect, which §2.3 says is the least trustworthy family
of measures generally. The music case study should therefore lean on **eye-hand span** (a
chunking measure, directly interpretable, and visually renderable as "how far ahead they are
reading") rather than on fixation duration, despite the latter having the better statistics.

---

## 6. Visual encoding

Cleveland & McGill (1984), *Graphical Perception* — the accuracy ranking of elementary encodings:

**position (common scale) > position (non-aligned) > length > direction/angle/slope > area >
volume > curvature > shading > colour saturation**

with position **1.4–2.5× more accurate than length** and **1.96× more accurate than angle**.

Bertin's visual variables (position, size, shape, value, colour, orientation, texture) supply the
vocabulary; pre-attentive processing research supplies the set of features detectable in parallel
without serial search — the mechanism the demo is trading on throughout.

**Design consequence — a deliberate inversion.** This project's needs are the *opposite* of a
statistical chart's. A chart wants the viewer to read magnitudes accurately, so it uses
high-accuracy channels. This project wants the viewer to *feel* a difference pre-verbally
without reading off values, so the low-accuracy, high-immediacy channels — colour, texture,
value — are the right choice, and using them is a justified decision rather than sloppiness.

The one place the ranking must be obeyed: **the quantitative panel** (perceptual overlap %,
conflict counts). Those are meant to be read precisely and must use position/length encodings.

---

## 7. Claim table

| # | Claim | Source | Quantity | Used for |
|---|---|---|---|---|
| 1 | Experts fixate task-relevant areas more | Gegenfurtner et al. 2011 | r = 0.27 (d ≈ 0.56) ⚠️ | L1 target: salience concentration |
| 2 | Experts fixate redundant areas less | Gegenfurtner et al. 2011 | r = −0.43 (d ≈ −0.95) ⚠️ | L1 target: **primary** — suppression asymmetry |
| 3 | Experts reach relevant info sooner | Gegenfurtner et al. 2011 | direction only | Reveal-order channel |
| 4 | Irrelevant information is discarded with practice | Haider & Frensch 1996/99 | qualitative | Model's core mechanism |
| 5 | Reduction is partly voluntary, instruction-sensitive | Haider & Frensch 1999 | qualitative | Personas encode a *mandate*, not an identity |
| 6 | Fixation duration/count are NOT reliable expertise markers | Klostermann & Moeinirad 2020 | 101 studies, mostly null | Constrains model to location-based channels |
| 7 | Gaze location IS a reliable expertise marker | Klostermann & Moeinirad 2020 | qualitative | Justifies salience as the primary channel |
| 8 | Directed salience massively accelerates access | Sirois et al. 2018 | 163–207 s faster TTFF | Order channel magnitude |
| 9 | Attention is zero-sum across a document | Sirois et al. 2018 | crowd-out observed | Salience must be normalised |
| 10 | Salience dilutes as more is highlighted | Sirois et al. 2018 | B > C,D at p < .05 | Caps per-persona salience concentration |
| 11 | Bouba/kiki holds at 72%, not universally | Ćwiek et al. 2022 | 72% [56–82], 917 pp | Act 1 opener + honest framing |
| 12 | Bouba is stronger than kiki | Ćwiek et al. 2022 | 22/25 vs 11/25 languages | Asymmetric texture mapping |
| 13 | Synaesthetic advantage is real but not pop-out | Ward et al. 2010; Rothen & Meier 2009 | 41.4% vs 31.5% | Act 1 hinge, reframed |
| 14 | Expert musicians have shorter fixations | Perra et al. 2022 | g = −0.72, I² = 0% | Music case (secondary) |
| 15 | Eye-hand span grows with expertise | Perra et al. 2022 / review | 0.52–3.69 → 1.73–6.8 notes | Music case (**primary**) |
| 16 | Encoding channels differ in accuracy | Cleveland & McGill 1984 | position 1.4–2.5× length | Quantitative panel only |

⚠️ = numeric value not verified against the primary source; see §2.1.

---

## 8. What this means for the model (Phase 2 inputs)

1. **Salience is the primary channel** and the only one with support in both the expertise and
   the counter-evidence literature. Everything else is secondary.
2. **Calibrate on the suppression asymmetry, not on overall attention.** The target is that
   expert personas suppress task-irrelevant units about twice as strongly (|d| ≈ 0.95) as they
   enhance task-relevant ones (d ≈ 0.56).
3. **Salience must be normalised to a fixed budget per persona.** Justified by claims 9 and 10:
   attention is zero-sum and dilutes. A persona may not mark everything as important.
4. **Cap salience concentration.** Claim 10 gives an empirical reason to bound how peaked a
   persona's distribution may be.
5. **Personas are mandates, not identities** (claim 5). Each definition states an objective,
   time horizon and loss function — not a personality.
6. **Expert and novice distributions must overlap** (§2.4). Rendering them as disjoint would
   misrepresent the evidence.
7. **Treat timing channels as illustrative,** and label them so (claim 6).
8. **Use low-accuracy/high-immediacy channels for the felt layer, high-accuracy channels for
   the numeric panel** (§6).

---

## 9. Gaps and limitations

Carried forward verbatim into `docs/calibration.md` and the demo's honesty panel.

1. **No role-differentiated finance eye-tracking exists.** Credit analyst vs equity PM vs risk
   officer vs retail investor on the same note has not been measured. The role differences shown
   are **modelled from mandates, not measured**. Largest limitation in the project.
2. **The best finance anchor used students, not professionals** (Sirois et al., n = 98
   post-graduate accounting students as non-professional-investor proxies).
3. **Two key effect sizes are unverified** against the paywalled primary source (§2.1).
4. **The expertise literature contradicts itself** on fixation duration direction, and its
   reliability is challenged by a 101-study review (§2.3).
5. **Cross-domain transfer is assumed.** Effect sizes from medicine, sport and music are being
   applied to financial prose. No study licenses this.
6. **LLM personas are not experts.** Any persona output is a language model's model of a role.
   Multi-sample aggregation and a published reliability figure bound the noise, but not the bias.
7. **Music moderators are unresolved** — Perra et al. could not explain their heterogeneity.
8. **Poetry has no comparable evidence base** and, if built, must be presented as frankly
   interpretive rather than calibrated.

---

## 10. References

Bibliographic details marked ⚠️ were assembled from secondary sources and should be confirmed
before publication.

- Chase, W. G. & Simon, H. A. (1973). Perception in chess. *Cognitive Psychology* 4(1), 55–81.
- Cleveland, W. S. & McGill, R. (1984). Graphical perception: theory, experimentation, and
  application to the development of graphical methods. *JASA* 79(387), 531–554.
- Ćwiek, A., Fuchs, S., Draxler, C., Asu, E. L., Dediu, D., Hiovain, K., Kawahara, S.,
  Koutalidis, S., Krifka, M., Lippus, P., Lupyan, G., Oh, G. E., Paul, J., Petrone, C.,
  Ridouane, R., Reiter, S., Schümchen, N., Szalontai, Á., Ünal-Logacev, Ö., Zeller, J.,
  Perlman, M. & Winter, B. (2022). The bouba/kiki effect is robust across cultures and writing
  systems. *Phil. Trans. R. Soc. B* 377(1841). DOI 10.1098/rstb.2020.0390
- Gegenfurtner, A. (2020). *Professional Vision and Visual Expertise* (habilitation).
  University of Regensburg. epub.uni-regensburg.de/51267
- Gegenfurtner, A., Lehtinen, E. & Säljö, R. (2011). Expertise differences in the comprehension
  of visualizations: a meta-analysis of eye-tracking research in professional domains.
  *Educational Psychology Review* 23(4), 523–552. DOI 10.1007/s10648-011-9174-7
- Haider, H. & Frensch, P. A. (1996). The role of information reduction in skill acquisition.
  *Cognitive Psychology* 30(3), 304–337. ⚠️
- Haider, H. & Frensch, P. A. (1999). Information reduction during skill acquisition: the
  influence of task instruction. ⚠️
- Hubbard, E. M., Arman, A. C., Ramachandran, V. S. & Boynton, G. M. (2005). Individual
  differences among grapheme-color synesthetes. *Neuron* 45(6), 975–985. ⚠️
- Klostermann, A. & Moeinirad, S. (2020). Fewer fixations of longer duration? Expert gaze
  behavior revisited. *German Journal of Exercise and Sport Research*.
  DOI 10.1007/s12662-019-00616-y
- Perra, J., Latimier, A., Poulin-Charronnat, B., Baccino, T. & Drai-Zerbib, V. (2022). A
  meta-analysis on the effect of expertise on eye movements during music reading. *Journal of
  Eye Movement Research* 15(4):1. DOI 10.16910/jemr.15.4.1
- Ramachandran, V. S. & Hubbard, E. M. (2001). Synaesthesia — a window into perception, thought
  and language. *Journal of Consciousness Studies* 8(12), 3–34.
- Rich, A. N. & Karstoft, K.-I. (2013). Exploring the benefit of synaesthetic colours: testing
  for "pop-out" in individuals with grapheme–colour synaesthesia. *Cognitive Neuropsychology*.
  DOI 10.1080/02643294.2013.805686 ⚠️
- Rothen, N. & Meier, B. (2009). Do synesthetes have a general advantage in visual search and
  episodic memory? *Frontiers in Human Neuroscience* 3. ⚠️
- Sirois, L.-P., Bédard, J. & Bera, P. (2018). The informational value of key audit matters in
  the auditor's report: evidence from an eye-tracking study. *Accounting Horizons* 32(2),
  141–162.
- Ward, J., Jonas, C., Dienes, Z. & Seth, A. (2010). Grapheme-colour synaesthesia improves
  detection of embedded shapes, but without pre-attentive "pop-out" of synaesthetic colour.
  *Proc. R. Soc. B* 277(1684), 1021–1026. ⚠️
