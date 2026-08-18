# Reference manifest

One row per source, recording what it is, whether it may be cited, and whether it has been
read. PDFs are not committed.

Every entry in `references.bib` was fetched from CrossRef by DOI content negotiation on
2026-08-18 by `05.scripts/10-build-bibliography.py`, and rekeyed to
`FirstAuthorFamily_Year`. No entry was written from memory and none was copied from another
repository's manifest on trust. Thirty-six entries were requested and thirty-six returned;
the build log is `02.inputs/derived/bibliography-build-log.csv`.

A preprint is distinguished from the peer-reviewed version. **A claim about another paper
that carries weight in the manuscript requires the paper to have been opened and the
quotation checked against it.** The read column below is the honest state of that, not an
aspiration.

## Read status

Four levels, used exactly:

1. **Full text**, opened and read in this repository on the date given.
2. **Full text elsewhere**, read in Study 1 and not re-read here.
3. **Abstract**, the abstract retrieved and read; nothing is claimed beyond it.
4. **Secondary**, not opened at all; any figure attributed to it is quoted from a source
   that quotes it, and that source is named in the row.

## Blocking gap

**`Aukema_2006` is closed access and no open version exists.** OpenAlex reports
`oa_status: closed` with no best open location, and Semantic Scholar returns
`openAccessPdf.status: CLOSED`. The prior-work protocol's adjudication rule 1 requires that
any claim about what that paper did or did not do be made from its full text and never from
its abstract. **That rule cannot currently be satisfied**, so the novelty judgement in the
survey is recorded as provisional and the manuscript may not assert what Aukema et al. did
not measure until the full text is read. The same applies to `Aukema_2008`. Resolving this
needs institutional access, which is Seamus's to supply.

## Entries

| Key | Source | Read | Citable | Notes |
|---|---|---|---|---|
| Aukema_2006 | Ecography 29(3):427-441, 2006 | Abstract, 2026-08-18 | Yes, bounded | The closest prior work. Measures epicentre against simultaneous eruption on 12 by 12 km cells from the aerial survey, 1990-2003, and synchrony against distance. **Novelty of this study turns on its full text, which is unavailable.** |
| Aukema_2008 | Ecography 31(3):348-358, 2008 | Abstract, 2026-08-18 | Yes, bounded | Chilcotin Plateau, 800 thousand ha, 1970s to early 1980s. Reports landscape-level synchrony in eruption onsets. Second-closest prior work. |
| Bjornstad_2001 | Environmental and Ecological Statistics 8(1):53-70 | Abstract, 2026-08-18 | Yes | Nonparametric spatial covariance function with bootstrap intervals. The adopted estimator for the synchrony scale in H3. |
| Bright_2020 | Forests 11(5):529 | **Full text, 2026-08-18** | Yes | Satellite evaluation of aerial survey bark beetle mortality, northern Idaho. Source of the severity accuracies 71.3 to 78.1 percent and of the quotation of Johnson_2008b's spatial accuracy figures. |
| Chen_2011 | Ecosphere 2(6):art66 | Abstract, 2026-08-18 | Yes | Short and long distance dispersal partitioned from the **British Columbia aerial overview survey**. Same archive as this study. |
| Chen_2014 | Ecography 37(4):344-356, CrossRef records the year as 2013 for the online version | Abstract, 2026-08-18 | Yes | Spatiotemporal pattern analysis of the same archive, **1960 to 2010**, by morphological spatial pattern analysis. Closest overlap with this study's window. |
| Clark_2001 | American Naturalist 157(5):537-554 | Abstract, 2026-08-18 | Yes | Fat-tailed dispersal kernels give accelerating spread with no asymptotic wave speed. Bears directly on whether H2's constant speed is well posed. |
| Coggins_2008 | The Forestry Chronicle 84(6):900-909 | Abstract, 2026-08-18 | Yes | Survey detection accuracy across field, aerial and satellite scales for this beetle in British Columbia. |
| Coleman_2018 | Forest Ecology and Management 430:321-336 | Abstract, 2026-08-18 | Yes | The largest formal accuracy assessment of aerial detection surveys. Full text needed before its numbers are used. |
| Cooke_2017 | Forest Ecology and Management 396:11-25 | Secondary, via the arXiv preprint of Johnson_2026 | Context only | Cited there for a 250 km eastward jump in one year. Not opened; the figure is not used as a prior effect size until it is. |
| Fox_2011 | Ecology Letters 14(2):163-168, CrossRef records the year as 2010 | Abstract, 2026-08-18 | Yes | Experimental separation of the Moran effect from short-distance dispersal and phase locking. |
| Franklin_2003 | Photogrammetric Engineering and Remote Sensing 69(3):283-288 | Abstract, 2026-08-18 | Yes | Landsat TM red-attack classification in British Columbia. |
| Gamarra_2008 | Journal of Animal Ecology 77(4):796-801 | Abstract, 2026-08-18 | Yes | Occupancy and fractal dimension of infestations in British Columbia, scale-invariant in 24 of 37 years. |
| Gilbert_2010 | Ecography 33(5):809-817 | Abstract, 2026-08-18 | Yes | Comparison of spread-rate estimators. The method paper for H1 and H2. Full text needed before an estimator is fixed. |
| Giroday_2012 | Journal of Biogeography 39(6):1112-1123 | Abstract, 2026-08-18 | Yes | The Rocky Mountain breach, comparing consecutive-year spread patterns against dispersal hypotheses. |
| Jackson_2008 | Canadian Journal of Forest Research 38(8):2313-2327 | Abstract, 2026-08-18 | Yes | Weather radar and aerial capture of beetles flying above the canopy. The long-distance dispersal mechanism. |
| Johnson_2008a | Australian Forestry 71(3):216-222 area | Abstract, 2026-08-18 | Yes | Aerial detection surveys in the United States, method description. |
| Johnson_2008b | Australian Forestry 71, Quantifying error in aerial survey data | **Secondary**, quoted by Bright_2020 | Bounded | Spatial accuracy 61, 68 and 79 percent at tolerances of 0, 50 and 500 m, in 233 plots. **Not opened.** Any use states that it is quoted from Bright_2020. |
| Johnson_2026 | Ecology, Modeling stratified dispersal in forest pests | **Full text of the arXiv preprint (2409.05320), 2026-08-18**; journal version not opened | Yes, preprint flagged | Student's t kernel, median dispersal 60 m, 95th percentile near 5 km, prior estimates spanning 10 m to 18 km. The preprint and the journal version are distinguished wherever cited. |
| Koenig_2002 | Ecography 25(3):283-288 area | Abstract, 2026-08-18 | Yes | Spatial autocorrelation of climate as the scale of the Moran effect. |
| Lande_1999 | American Naturalist 153(2) | Abstract, 2026-08-18 | Yes | The theory that makes H3 decidable: synchrony scale under environmental correlation against dispersal. |
| MacLean_1996 | Canadian Journal of Forest Research 26 | Abstract, 2026-08-18 | Yes | Accuracy of aerial sketch-mapping for spruce budworm defoliation, 1984-1993, 222 to 325 plots. |
| MaciasFauria_2009 | Journal of Geophysical Research Biogeosciences | Abstract, 2026-08-18 | Yes | **High spatial synchrony across large distances in British Columbia, 1959-2002, related to the Pacific Decadal and Arctic Oscillations.** A published Moran-effect reading of this study's own archive. |
| Meddens_2014 | Forest Ecology and Management, Landsat detection of beetle-caused mortality, Colorado | Abstract, 2026-08-18 | Yes | Candidate source for Landsat detection lag. Full text needed before a timing error is quoted. |
| Peltonen_2002 | Ecology 83(11):3120-3129 | Abstract, 2026-08-18 | Yes | Dispersal against regional stochasticity across six forest insects. The canonical design for H3. |
| Perbet_2025 | Scientific Data 12:2012 | **Full text, 2026-08-18** | Yes | 30 m annual insect disturbance maps for all Canada, 1985-2024, from Landsat. Area-adjusted overall accuracy 90.0 ± 1.8 percent, commission 6.7 ± 3.5, **omission 41.0 ± 6.2**; start-year agreement R squared 0.96. CC BY 4.0. |
| Perevaryukha_2016 | Biophysics 61(2):334-341 | Full text elsewhere, 2026-08-17 in Study 1 | Yes | Threshold equilibria and a backward tangent bifurcation, explicitly not the Feigenbaum scenario. |
| Perevaryukha_2019 | Cybernetics and Systems Analysis 55(1):141-152 | Full text elsewhere, 2026-08-17 in Study 1 | Yes | Argues a travelling-wave spread model of the KPP kind is unrealistic for a forest moth. |
| Robertson_2009 | Journal of Biogeography 36 | Abstract, 2026-08-18 | Yes | Fine-scale movement patterns at three Rocky Mountain passes during range expansion. |
| Safranyik_1992 | Journal of Applied Entomology 113 | Abstract, 2026-08-18 | Yes | Mark-release-recapture under the canopy; over 80 percent of recaptures within three days. Routine dispersal. |
| Safranyik_2010 | The Canadian Entomologist 142(5) | Abstract, 2026-08-18 | Yes | Potential for range expansion into the boreal forest. |
| Senf_2017 | International Journal of Applied Earth Observation and Geoinformation 60 | Abstract, 2026-08-18 | Yes | Review of remote sensing of forest insect disturbance. |
| Shegelski_2019 | Agricultural and Forest Entomology 21(1) | Abstract, 2026-08-18 | Yes | Flight mill morphology; beetles flying over 11 km against under 1 km. |
| Skellam_1951 | Biometrika 38(1-2):196-218 | Abstract, 2026-08-18 | Yes | The origin of the diffusion spread-rate result the H1 estimator descends from. |
| Tobin_2015 | Book chapter, CABI | Abstract, 2026-08-18 | Yes | Square-root area regression, distance regression and boundary displacement, demonstrated on gypsy moth. |
| Ye_2021 | Remote Sensing of Environment 264:112560 | Abstract, 2026-08-18 | Yes | Detecting subtle change from dense Landsat series for mountain pine beetle and spruce beetle. Candidate Landsat tier method. |

## Counts

Thirty-six entries. **Three read in full in this repository** (Bright_2020, Perbet_2025, and
the arXiv preprint of Johnson_2026), two read in full in Study 1, **twenty-nine read at
abstract only**, and two held as secondary. The fraction of the bibliography actually opened
is therefore 5 of 36, and the survey states that rather than implying wider reading.
