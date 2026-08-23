# Paper drop

Put the full-text PDF of **Gegenfurtner, Lehtinen & Säljö (2011)**, "Expertise differences in the
comprehension of visualizations: a meta-analysis of eye-tracking research in professional
domains", *Educational Psychology Review* 23(4), 523–552, DOI `10.1007/s10648-011-9174-7`
here, named:

    papers/gegenfurtner_2011.pdf

It is needed to verify the two calibration constants currently flagged ⚠️ in
`docs/research-note.md` §2.1 and in `pipeline/src/cmp/targets.py`:

| Constant | Current value | Status |
|---|---|---|
| `r_relevant` | 0.27 | from a secondary source |
| `r_redundant` | −0.43 | from a secondary source |

Once the PDF is here, the exact per-measure effect sizes can be extracted, the constants
updated, and the ⚠️ flags removed from the research note, the calibration doc and the demo's
honesty panel.

PDFs are gitignored; this directory holds only this README.
