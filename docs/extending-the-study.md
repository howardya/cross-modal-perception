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

**A document, and preferably a real one.**

The signature claim currently rests on two documents. With two, "the profile held
both times" is a coin landing the same way twice — the correlations of +0.90,
+0.79 and +0.78 in [`findings.md`](findings.md) are suggestive and not much more.
A third and fourth document is the cheapest thing that turns them into a trend.

More specifically, the single most valuable text you could add is **a real
filing**. Every document so far is constructed, and §7.5 of
[`calibration.md`](calibration.md) already measures what that costs: readers
share 37.5% of their attention on the note built to divide them against 50% on
the one that was not. A genuine filing is the only way to find out where the true
number sits.

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
   caveat has to travel with the data.

2. **Label every sentence by topic** in `pipeline/stimuli/topics.json`, using the
   same seven categories. This is the step people skip and it is the one that
   matters: **a document without topic labels cannot appear in the signature
   figures at all**, because the whole point of the topic axis is that it is
   comparable across documents.

   If a new text does not fit the seven categories, that is a real finding about
   the taxonomy, not a licence to invent an eighth quietly. Widening the taxonomy
   changes every profile in the study, so it is the same kind of decision as
   adding a reader.

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

4. **Check it passed.** The command exits non-zero if the run fails the
   literature checks. Do not tune the personas until it passes — a failure is a
   result, and §7.3 of `calibration.md` is where the last one is written up.

5. **List it** in `cmp.report_data.DOCUMENTS` and run `python3 viz/build.py`.

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
cd pipeline && uv sync && uv run pytest     # 297 tests, no network
cd .. && python3 viz/build.py               # both pages
open viz/dist/report.html
```
