# Reference manifest

One row per source, recording what it is, whether it may be cited, and whether it has been
read. PDFs are not committed.

Every entry in `references.bib` is verified against CrossRef by DOI content negotiation
before it is added; entries are taken from the registry, not from memory. Hand-entered
entries, where no DOI exists, are flagged as such in a comment.

A preprint is distinguished from a peer-reviewed version. A claim about another paper that
carries weight in the manuscript requires the paper to have been opened and the quotation
checked against it.

Study 1's manifest at
`/Volumes/PortableSSD/Github/chaos-in-beetle-outbreaks/04.references/README.md` carries
seventeen entries with their verification dates and read status. Entries are **re-verified
on entry here**, not copied on trust, because a manifest row is a claim about a registry
and this repository must be able to stand alone.

Three entries only, the works the manuscript shell already names. Each was re-verified
against CrossRef in this repository on 2026-08-17. The prior-work survey has not run and
every other citation waits for it.

| Key | Source | Read | Citable | Notes |
|---|---|---|---|---|
| Aukema_2006 | Ecography 29(3):427-441, DOI 10.1111/j.2006.0906-7590.04445.x, verified via CrossRef 2026-08-17 | Not read | General attribution only | The travelling-wave and spatial-synchrony study this one is positioned against, by its title claim. **Must be read in full before the framing gate closes**, because the novelty of this study depends on exactly what it did and did not measure. |
| Perevaryukha_2016 | Biophysics 61(2):334-341, DOI 10.1134/S0006350916020147, verified via CrossRef 2026-08-17 | Read in full 2026-08-17 (in Study 1) | Yes | Hybrid continuous-event psyllid outbreak model. Threshold equilibria and a backward tangent bifurcation; explicitly not the Feigenbaum scenario. Relevant here because it models outbreak spread as a threshold phenomenon rather than a travelling front. |
| Perevaryukha_2019 | Cybernetics and Systems Analysis 55(1):141-152, DOI 10.1007/s10559-019-00119-6, verified via CrossRef 2026-08-17 | Read in full 2026-08-17 (in Study 1) | Yes | Delay-equation models of spruce budworm sawtooth outbreaks in eastern Canada. Directly relevant: it argues a KPP travelling-wave spread model is unrealistic for moths, and reports interprovincial asynchrony against the Moran effect. |
