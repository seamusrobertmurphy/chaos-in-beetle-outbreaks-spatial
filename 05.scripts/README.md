# Scripts

**Everything in this directory is generated.** All code that derives data lives in
`01.manuscript/manuscript.qmd`, in the `Analysis pipeline` section, and is written out here
by the `pipe-purl` chunk so that long jobs can be run from a terminal without rendering the
whole document.

Edit the chunk in the manuscript and regenerate. Edits made here are lost on the next
regeneration, and the two copies would otherwise drift with the paper reporting numbers
produced by code that is not the code in the repository.

`04-build-readme.R` is the exception: it is repository tooling rather than analysis, and it
extracts the title, abstract, figures and tables from the rendered manuscript to build the
root README.

Any phase that must run before the framing gate, and so before the manuscript it would
otherwise be generated from, is hand-written in its own numbered block with a distinct
prefix, documented in the table below, and never carried into the manuscript by copying: it
is rewritten into the pipeline or it is reported as preliminary work and left here.

## Hand-written blocks

| File | Phase | What it does |
|---|---|---|
| `04-build-readme.R` | tooling | Builds the root README from the rendered manuscript. Inherited from Study 1 unchanged. |
| `05-review-search.py` | survey | Runs the two search strands the review protocol fixes, Semantic Scholar bulk and OpenAlex, plus forward citation chasing from three seeds. Writes `02.inputs/derived/review-search.jsonl` and `review-search-log.csv`. |
| `06-review-chase-backward.py` | survey | Recovers the protocol's backward citation chase from OpenAlex `referenced_works`, because Semantic Scholar returned zero references for all three seeds. Appends to the same two files. |
| `07-review-screen.py` | survey | Deduplicates by DOI then normalised title, applies the protocol's vocabulary criteria by script, and records a decision and reason code per record. Writes `review-records.csv` and `review-screen-counts.csv`. |
| `08-review-prioritise.py` | survey | Scores each passing record against the question it matched, keeps every decisive-pattern hit, and reads down to a declared per-question budget. Writes `review-reading-list.csv` and `review-priority-counts.csv`, including what the budget dropped. |
| `09-verify-citations.py` | survey | Checks candidate DOIs against CrossRef before any entry is written. Caught four DOIs resolving to the wrong paper. Writes `citation-verification.csv`. |
| `10-build-bibliography.py` | survey | Fetches BibTeX by DOI content negotiation from CrossRef and writes `04.references/references.bib`. Nothing enters the bibliography by any other route. Writes `bibliography-build-log.csv`. |

| `11-resolution-analysis.R` | design | Resolution analysis on the real province geometry, run before any estimator was chosen and touching no beetle data. Plants waves of known speed on grids of 1, 2, 5 and 12 km under modelled positional error and omission, and plants a simultaneous eruption as the null. Writes `03.outputs/tables/resolution-analysis.csv` and `resolution-null-case.csv`. |
| `12-blocked-inference-check.R` | design | Second stage: plants a stochastic front with a spatially correlated arrival anomaly, compares the naive standard error against a spatial block bootstrap at 50, 100 and 200 km, and reruns the null case under blocked inference. Writes `blocked-inference.csv` and `blocked-null-case.csv`. Source of the design effect and the chosen block size. |

All six survey scripts are governed by
`docs/science-superpowers/prior-work/2026-08-18-review-protocol.md`, not by the `pipe-purl`
do-not-edit rule, and every count in the survey synthesis is reproducible by running them in
numeric order. The two design scripts are governed by
`docs/science-superpowers/plans/2026-08-18-spatial-spread-plan.md` and read no outcome data;
their only input is the province boundary.
