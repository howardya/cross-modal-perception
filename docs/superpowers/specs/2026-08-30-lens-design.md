# The Lens — design

A tool, not a page. You give it a URL or a block of text, choose one of the seven
readers, and the document is re-rendered as that reader perceives it: what they
dwell on grows and sharpens, what they skim past shrinks and blurs, good news and
bad news for *their* mandate take opposite colours, and the sentences they read as
one idea close up into a single block. Switching readers morphs continuously
between two renderings of the same unchanged words.

Companion documents: [`../../OBJECTIVE.md`](../../OBJECTIVE.md) states what the
project is for; [`../../findings.md`](../../findings.md) records what the study
found; [`../../calibration.md`](../../calibration.md) is the argument for a
skeptic, and gains a section on this tool's weaker provenance.

---

## 1. Why this is a new thing rather than a sixth act

The five pages in `viz/dist` are *records*. Each shows a finding on documents that
were scored five times each, aggregated by median, and checked for reliability.
They cannot show you a document they have never seen.

The lens is an *instrument*. Its subject is whatever the viewer brings, which
means it can never have the study's provenance: one live sample, no median, no
measurable α. That is a real and permanent difference in evidential weight, and
the design's job is to make the tool vivid without letting it borrow authority it
does not have. §7 is how.

The two coexist. Nothing in `viz/acts/` or `viz/template.html` changes.

---

## 2. What the viewer does

1. Lands on `dist/lens.html`. It opens on the hero note with the credit analyst's
   reading already applied, from the inlined study fixtures — the instrument is
   never blank, and never requires a server to demonstrate itself.
2. Pastes a URL or text. The page posts it to the local server, which fetches,
   strips and splits it into clauses, and returns them.
3. Picks an eye. That persona is scored first and appears in roughly ten seconds.
   The other six are requested in parallel behind it and light up in the switcher
   as each lands.
4. Switches between readers. Once warm, every switch is instant and animated.

Steps 2–4 need `pipeline/src/cmp/server.py` running with an API key. Step 1 does
not, and the page states which mode it is in at all times.

---

## 3. Server

Three new modules under `pipeline/src/cmp/`. No new dependency: `urllib` and
`http.server` from the standard library, plus the existing optional `anthropic`
extra, which is already how the study's API path is gated.

### 3.1 `ingest.py`

The study's stimuli are hand-authored `texts` lists; nothing in the pipeline
splits prose today. This module is that, and nothing else.

```
fetch(url) -> tuple[str, str]        # (title, plain text)
to_clauses(text) -> list[str]        # prose -> numbered clause list
ingest(*, url=None, text=None) -> Ingested
```

`Ingested` carries `doc_id` (sha256 of the normalised source, so the same input is
never scored twice), `title`, `clauses`, and `source` (`"url"` or `"text"`).

Rules, all of them testable without network:

- HTML is reduced by stripping `script`, `style`, `nav`, `header`, `footer` and
  then tags, collapsing whitespace, and dropping lines under 40 characters that
  contain no sentence-ending punctuation — the usual navigation debris.
- Clause splitting is sentence-level on `.`, `?`, `!` followed by whitespace and a
  capital or digit, with an abbreviation guard (`Inc.`, `Corp.`, `Q4.`, `U.S.`,
  `Mr.`, and single initials). A sentence over 400 characters is split further at
  `;` and at ` — `.
- **Cap: 120 clauses.** Beyond that the render stops being legible and the cost
  stops being trivial. Over the cap, `ingest` truncates and sets
  `truncated_from`, which the page reports to the viewer rather than hiding.
- **Floor: 6 clauses.** Below that the salience quota is meaningless
  (`salience_quota` already refuses fewer than two) and the divergence between
  readers has nothing to land on. Rejected with a message saying so.
- Fetching is restricted to `http` and `https`, follows at most three redirects,
  caps the response at 2 MB, and times out at 15 seconds. It sends a plain
  identifying user-agent. It does not execute JavaScript, so a page that renders
  its text client-side will come back thin — the page says "that URL gave us only
  N clauses" rather than pretending.

### 3.2 `lens.py`

One live sample of one persona over one ingested document.

The prompt is `anthropic_client.build_scoring_prompt` **unchanged**, including the
salience quota, plus one appended paragraph requesting notes. The response schema
is `SCORING_SCHEMA` extended with one optional per-clause string:

```
note: str | None   # <= 12 words, first person, this reader's own voice
```

`SCORING_SCHEMA` itself is not modified. `LENS_SCHEMA` is built from it by
deep-copy in `lens.py`, so the study's contract cannot drift by accident, and a
test pins that the study schema is byte-identical to what it was.

Notes are requested only for the clauses the reader scores highest — the model is
asked for at most four, and if it returns more, the four on the highest-salience
clauses are kept and the rest dropped server-side. They are the
annotation layer; a note on every clause would be a summary, which is the opposite
of what the tool is for.

```
attend(client, persona, ingested) -> LensField
```

`LensField` is a `PerceptualField` plus `notes: dict[int, str]`. `order` is derived
by rank on salience, exactly as `inline.py` already does it, so the reading-order
mode is consistent with the study pages.

Failure is explicit. A malformed response, a refused quota, or a unit-count
mismatch raises through the existing `parse_scores` validation; the server turns
it into a 502 naming the persona, and the page marks that eye as failed with a
retry rather than showing a silently degraded reading.

### 3.3 `server.py`

`python -m cmp.server` on port 8420, stdlib `ThreadingHTTPServer`.

| Route | Body | Returns |
|---|---|---|
| `POST /api/ingest` | `{url}` or `{text}` | `{doc_id, title, clauses, truncated_from?}` |
| `POST /api/attend` | `{doc_id, persona_id}` | one `LensField` as JSON |
| `GET /api/personas` | — | the seven, as id/label/mandate/reads_for |
| `GET /` and `/lens.html` | — | `viz/dist/lens.html` |
| `GET /fixtures/*.json` | — | the study fixtures |

Concurrency is the browser's. It issues one `POST /api/attend` for the selected
persona and six more in parallel; the server is threaded and the calls are
independent. No streaming, no polling, no job ids — seven ordinary requests, each
of which either returns a reading or an error.

Cache is a directory, `pipeline/.lenscache/{doc_id}/{persona_id}.json`, with the
ingested clauses at `{doc_id}/doc.json`. Keyed by content hash, so re-attending a
document already scored is free and instant, and closing the browser loses
nothing. `.gitignore` gains the directory.

Missing `ANTHROPIC_API_KEY`: the server still starts and still serves the page and
the fixtures. `/api/attend` returns 503 with a message the page displays as
"reading live needs an API key — here are the five documents from the study".
The instrument degrades to the record rather than to an error.

Bound to `127.0.0.1` only. It fetches URLs the viewer supplies and holds an API
key; it is a local tool and the README says so rather than leaving it implied.

---

## 4. The render

`viz/lens.template.html` -> `dist/lens.html`, built by `build.py` with the five
study fixtures inlined at `/*__LENS_DATA__*/`.

Each clause is a `<span class="clause">` carrying custom properties computed from
its unit. Nothing about the styling is in the markup, which is what makes the
morph possible: switching reader rewrites the properties and CSS interpolates.

| Channel | Driven by | Effect |
|---|---|---|
| size, weight | salience | `0.72rem` → `1.9rem`, weight 300 → 620 |
| opacity | 1 − salience | 1.0 → 0.12 |
| blur | 1 − salience | 0 → 3px, applied only below the median so the top half stays crisp |
| hue | valence | cold blue (bad for this mandate) ↔ warm amber (good for it) |
| saturation | salience × \|valence\| | ignored text desaturates to grey, so colour never shouts from a clause the reader skimmed |
| left rule, grain | arousal | a marginal rule and a faint texture — unease, kept deliberately separate from valence, because a reader can be alarmed by news that is good for them |
| grouping | chunk | clauses sharing a chunk id render gapless in one block; whitespace falls only at chunk boundaries |
| position | order | opt-in reading-order mode, §4.2 |
| margin note | `note` | short annotation, hairline-connected to its clause |

Two of these do the heavy lifting and are worth naming. **Blur plus opacity is the
whole point** — the viewer must fail to read a sentence, notice that they failed,
and then be able to recover it by hovering. A highlight layer does not produce
that. **Chunking is what makes an expert's page look like fewer things**, which is
the visual form of information reduction and the study's cleanest result (§2.3 of
findings: thirty out of thirty).

### 4.1 The morph

Switching persona sets the new custom-property values on every clause at once and
lets a 700ms transition carry size, opacity, blur and colour. Chunk regrouping
animates by margin, so blocks visibly close up or come apart.

This is the deliverable. `OBJECTIVE.md` §1 names the static side-by-side as the
failure mode, because it invites analysis and analysis is the mode being bypassed.
A switch that cuts rather than morphs is that failure mode.

### 4.2 Reading order, off by default

A toggle reflows the clauses into the order the reader reaches them, animated with
FLIP so each sentence visibly travels to its new position.

This is the one effect that changes what the document *says* rather than how it
looks — a reordered document can imply a sequence its author did not write. The
`order` values are real scored data, so showing them is honest; making it the
default would not be. Off by default, labelled "reading order, not document
order" whenever on.

### 4.3 Legibility guarantees

- Hovering any clause returns it to full size, full opacity, zero blur, for as
  long as the pointer is on it. Nothing is ever unrecoverable.
- A "plain text" control drops every effect instantly, so a viewer can prove to
  themselves the words never changed. This is the answer to the only objection
  the render invites, and it needs to be one keystroke away, not in a menu.
- `prefers-reduced-motion` disables the morph and the FLIP; the readings still
  switch, they just cut. Blur is reduced but not removed — it carries data.
- Every clause keeps its true text in the DOM, unblurred, for screen readers and
  for select-and-copy.

---

## 5. Build

`build.py` gains `lens.template.html` -> `dist/lens.html` with `/*__LENS_DATA__*/`,
carrying all five documents' fields plus the persona definitions. Same rule as
every other page: no scores in the template, so the page cannot drift from the
study.

---

## 6. Tests

New files under `pipeline/tests/`, all offline, matching the existing suite's
no-network rule:

- `test_ingest.py` — sentence splitting including the abbreviation guard; HTML
  stripping; the 120 cap sets `truncated_from`; under-6 is refused; a
  `file://` or `javascript:` URL is refused.
- `test_lens.py` — `LENS_SCHEMA` is a superset of `SCORING_SCHEMA` and the latter
  is unchanged; `note` is optional and absent notes parse; more than four notes
  are dropped; order is the salience rank; a bad unit count still raises.
- `test_server.py` — routing, the doc/persona cache round-trip, 503 with no key,
  502 on a scoring failure naming the persona. Client is stubbed.

---

## 7. Provenance

A permanent strip on the page, not a footnote, saying which of two things is on
screen:

- **Study documents** — five independent samples per reader, aggregated by
  median, Krippendorff's α 0.90–0.98 on the hero note.
- **Live reading** — one sample, no median, **α unmeasurable**, scored just now
  by Claude Opus 5.

Both link to `calibration.md`, which gains a section stating plainly that the live
path trades the study's reliability for reach, that a single sample can be an
outlier, and that the honest use of the tool is to feel the shift rather than to
cite the numbers. `README.md` and `pipeline/README.md` gain the run instructions
and the local-only warning.

The existing sentence in `provenance.summary` — that these are modelled, not
measured recordings of real experts — applies to the live path unchanged and is
shown alongside.

---

## 8. Out of scope

- Deployment. It is a local tool; the API key makes it one.
- PDF ingestion.
- JavaScript-rendered pages.
- Saving or sharing a live reading. The cache is a cache, not a library.
- Comparing two readers side by side. The morph is the comparison; a split view
  is the failure mode §4.1 names.
