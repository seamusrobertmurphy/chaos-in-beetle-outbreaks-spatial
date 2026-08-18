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
