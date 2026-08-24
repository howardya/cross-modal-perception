# Extending the study

How to add a reader or a document without breaking anything, and which of the
two is worth more.

Both pages are generated from `fixtures/`, so nothing on either is hand-edited:

```
viz/template.html        + fixtures/meridian-q4.json      → viz/dist/index.html
viz/report.template.html + cmp.report_data (all fixtures) → viz/dist/report.html
```

`python3 viz/build.py` rebuilds both.

---

## Which should you add first?

**A document, and it should be a real one.**

The signature claim rests on five documents, three of them real SEC filings. The
correlations rose as the documents became less like each other — right up to the
fifth, a pharmaceutical release that never mentions borrowings, where three of the
four fell hard (+0.92 to +0.52 for the credit analyst). They now read +0.74, +0.58,
+0.52 and +0.50. The claim that survives is narrower: **the signatures travel
across documents that talk about money owed, and not to one that does not.**

**Everything else is less settled than three documents made it look.** §7.6 of
[`calibration.md`](calibration.md) drew a conclusion from one real filing —
attention overlap of 52.1%, "the constructed notes inflate by a third,
confirmed" — and §7.7 withdrew it, because the second real filing came in at
31.2%, *below* the note built to divide readers. Four documents span 31% to 52%,
and the constructed pair sits inside that range rather than to one side of it.

Take the lesson rather than the number: **two points look like a trend, three
points look like a confirmed trend, and the fourth is where you find out.** If a
new document moves a headline figure, suspect the figure before you suspect the
document.

Pick it the way `whirlpool-q2` was picked: **write the selection rule down before
you read any candidates**, and record the rule and the rejections in the
stimulus's `note`. Choosing a filing after reading it reintroduces exactly the
construction bias the real filing exists to measure. A rule that enumerates
EDGAR in a fixed order costs nothing and makes the result defensible.

Adding a reader is worth doing too, but it is a smaller gain and it carries a
cost the next section explains.

---

## Adding a document

1. **Write or obtain the text** and split it into clauses, one sentence each.
   Save as `pipeline/stimuli/<id>.json` following the shape of
   `meridian-q4.json`: `id`, `title`, `role`, `note`, `texts`, and a
   `relevance` mask per reader.

   The `note` field is not decoration — record there whether the text is
   constructed or real, and whether it was written to divide readers. That
   caveat has to travel with the data. For a real filing it also has to carry
   the provenance (accession number, URL, date) and the selection rule, since
   neither is recoverable from the text. See `whirlpool-q2.json` for the shape.

2. **Label every sentence by topic** in `pipeline/stimuli/topics.json`, using the
   same seven categories. This is the step people skip and it is the one that
   matters: **a document without topic labels cannot appear in the signature
   figures at all**, because the whole point of the topic axis is that it is
   comparable across documents.

   If a new text does not fit the seven categories, that is a real finding about
   the taxonomy, not a licence to invent an eighth quietly. Widening the taxonomy
   changes every profile in the study, so it is the same kind of decision as
   adding a reader.

   Real filings strain the seven in ways constructed notes do not. `alamo-q2` has
   **no clauses at all** in one category, which yields a lift of zero for every
   reader — a flat bar that reads as "everyone attended equally" and means "there
   was nothing there". `topics.json` also records three strains from `whirlpool-q2` — section
   headers that are structural labels rather than statements, a tax rate with no
   home, and a distribution so lopsided (13 of 31 clauses on performance, one
   each on cash, per share and dependency) that three of the seven bars rest on a
   single clause. **Record the strain and file the clause under its nearest
   category.** The lopsidedness is itself a result: the even spread the
   constructed notes have across the taxonomy is a property of documents written
   by someone who knew what the readers were for.

3. **Score it.** Either through the API:

   ```bash
   cd pipeline
   uv run python -m cmp calibrate <id> --k 5
   ```

   or, without credentials, by dispatching one subagent per sample and dropping
   the JSON into `pipeline/scored/<run>/<reader>-<n>.json`, then:

   ```bash
   uv run python -m cmp.from_samples scored/<run> <id>
   ```

   Five samples per reader is the floor; `--k 1` is rejected because a single
   sample has no measurable reliability.

3b. **Write the masks from the mandate, not from the reader's write-up.** The
   risk officer's mask on `whirlpool-q2` was built from its signature in
   `findings.md` §5b — *stops at reassurance* — and failed L1. On `alamo-q2` the
   same reader's mask was built from its `FINANCE_PERSONAS` mandate instead, and
   it passed comfortably. A mask copied from the study's own prose tests whether
   that prose is right, which is worth doing deliberately and disastrous by
   accident.

4. **Check it passed.** The command exits non-zero if the run fails the
   literature checks. Do not tune the personas until it passes — a failure is a
   result. §7.3 of `calibration.md` writes up the first one and §7.6 the latest,
   where a real filing failed on the risk officer and the failure turned out to be
   the most informative thing in the run — §7.7 is what identified the cause.

   A failing document can still go into the study, as `whirlpool-q2` did, but
   then `cmp.report_data.L1_FAILURES` has to name it and the page has to say so
   beside every figure that draws on it.

5. **List it** in `cmp.report_data.DOCUMENTS` and run `python3 viz/build.py`.

6. **Give it a bar style.** The topic figure draws one bar per document per topic,
   and the classes are listed in `DNA_SERIES` in `viz/report.template.html` with
   `.dna-bar--a` through `--e` beside them in the CSS. A sixth document needs a
   sixth style or it silently reuses the fifth. Past four, reach for texture rather
   than another shade — at 9px wide a fifth tint is indistinguishable from the
   third and fourth, which is why `--e` is hatched. The legend builds itself from
   `DATA.documents`, so it needs nothing. **Render the page and look at it** —
   the figure was hard-coded to two documents for a long time and drew the third
   nowhere, without erroring, without failing a test, and without any hint on the
   page that a document was missing.

The salience quota rescales itself for document length, so nothing needs tuning
for a shorter or longer text.

---

## Adding a reader

**Read this first: a new reader re-bases every number in the study.**

Lift is measured against the average across readers. The credit analyst's +9.6 on
*what is owed* means +9.6 relative to *these three colleagues*. Add a fifth
reader and every lift in every figure shifts, including ones already quoted in
`findings.md` and in the report's prose. This is not a bug — it is what "more
theirs than anyone's" means — but it does mean the write-ups need re-reading
after the rebuild, and the tests will tell you which sentences went stale.

The steps:

1. **Define the mandate** in `cmp.personas.FINANCE_PERSONAS`: objective, time
   horizon, loss function, what it reads for. No temperament — the research note
   (claim 5) records that information reduction is instruction-sensitive, so the
   mandate is the whole persona.

2. **Decide whether it is an expert.** The `expert` flag drives the salience
   quota, and the lay quota is deliberately looser. Giving a novice the expert
   quota erases the contrast the study exists to measure.

3. **Add a relevance mask** for it to every stimulus. "Relevant" means the
   minority of clauses it would actually fixate on, not everything bearing on the
   mandate — `tests/test_stimuli.py` enforces the minority shape, and
   `calibration.md` §2 explains why a majority mask makes the acceptance check
   vacuous.

4. **Re-score every document.** All of them, not just new ones: the fixtures need
   the new reader present everywhere or `build_report_data` refuses to run.

5. **Add a prose theme** in `cmp.report_data.THEMES` — a human reading of what
   the new reader stops at and walks past. The build fails without one, on
   purpose: a figure of quotes with no interpretation beside it is the thing that
   made the first attempt at a signature useless.

6. **Rebuild and re-read the prose.** `python3 viz/build.py`, then
   `uv run pytest`. Failures in `test_report_figures.py` are the sentences whose
   numbers moved.

---

## What stays hand-written

Prose. Numbers inside sentences cannot be generated without turning the writing
into a template, so they are asserted against the fixtures instead —
`test_figures_quoted_in_prose_still_match_the_fixtures` and the claim tests
beside it. A stale figure fails the suite rather than quietly misleading a reader.

The four prose themes and the topic taxonomy are also judgments rather than
computations, and both say so where they live.

---

## Full rebuild

```bash
cd pipeline && uv sync && uv run pytest     # 326 tests, no network
cd .. && python3 viz/build.py               # both pages
open viz/dist/report.html
```
