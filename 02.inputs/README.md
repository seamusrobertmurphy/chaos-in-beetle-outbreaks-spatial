# Input data manifest

Every dataset entering `02.inputs/` is recorded here on the day it is downloaded, with
integrity hashes appended to `SHA256SUMS.txt`. Raw data are gitignored; this manifest and
the retrieval code are the reproducible record.

The licence column carries what was read from the source on the date given, quoted where
the wording matters. A dataset whose licence page has not been opened is recorded as
unread, never as public domain by assumption. Service metadata counts as the source: a
licence sitting in a service's own metadata is binding even when the endpoint is open.

No outcome analysis is run on any file here until the pre-registration is frozen.

## Availability check

Run 2026-08-18, after the framing gate opened and **before** the pre-registration, so it is
a confirmation of existence and structure and **not** a retrieval. Nothing was copied except
the small province boundary recorded under Derived below, which the resolution analysis needs
in order to define the sample. No beetle outcome value has been read.

| Dataset | Where it is | Confirmed | State |
|---|---|---|---|
| Pest Infestation Polygons, multi-year archive | `/Volumes/PortableSSD/Github/chaos-in-beetle-outbreaks/02.inputs/survey/pest_infestation_poly.zip`, 769,472,357 bytes, and the unpacked File Geodatabase beside it | Present 2026-08-18 | **Not copied.** Copy enters this repository only after the pre-registration locks the design, and is recorded then with the sibling named and its hash compared, as Study 1 recorded its own copy. |
| Mountain pine beetle polygons extracted from that archive | `/Volumes/PortableSSD/Github/chaos-in-beetle-outbreaks/02.inputs/derived/agent-polys.gpkg`, 1.8 GB | Read-only structural check 2026-08-18 with `ogrinfo -so`: layer `pest_infestation_poly`, **682,902 multipolygons**, EPSG:3005, fields `PEST_SEVERITY_CODE`, `CAPTURE_YEAR`, `AREA_HA`. Extent 524,699 to 1,870,505 m easting and 448,468 to 1,695,215 m northing, so 1,346 by 1,247 km. A single aggregate query returned **capture years 1959 to 2025 across 65 distinct years**. | **Not copied.** Study 1 is read-only from here; this was a metadata query, not an extraction. |
| WorldClim 2.1 bio1 projected to BC | `/Volumes/PortableSSD/Github/chaos-in-beetle-outbreaks/02.inputs/derived/bc-temperature.tif` | Present 2026-08-18 | Not copied. Enters after pre-registration if the design keeps temperature as the control axis. |

Two calendar years between 1959 and 2025 carry no polygons for this agent. **Which two has
not been determined**, because doing so is a question about the outcome record and waits for
the pre-registration. The design treats the record as 65 observed years, not 67.

## Downloaded

Nothing retrieved. The framing gate opened on 2026-08-18 and retrieval waits for the
pre-registration.

| Folder | Dataset | Source | Licence | Notes |
|---|---|---|---|---|
| none | none | | | |

## Derived

Intermediate products, each regenerable from the raw inputs and gitignored unless it is a
small table the manuscript cites.

| File | Built by | Contents |
|---|---|---|
| `bc-nr-regions.geojson` | Copied 2026-08-18 from `/Volumes/PortableSSD/Github/chaos-in-beetle-outbreaks/02.inputs/derived/` | BC natural resource regions, 8 features, EPSG 3005, simplified at 500 m. SHA-256 compared against the sibling's copy on the day and identical: `69627a2b...1cb62c1`. Original source: BC openmaps WFS layer `WHSE_ADMIN_BOUNDARIES.ADM_NR_REGIONS_SPG`, Open Government Licence - British Columbia, licence recorded in the sibling chain rather than re-read here, and marked as such. **This is a boundary, not an outcome**, and it is copied now because the resolution analysis must define the sample before an estimator is chosen. |
| `03.outputs/tables/landsat-availability.csv` | `05.scripts/pipe-ee-availability.R`, generated from the manuscript | Growing-season Landsat scene counts over British Columbia, per mission and year, 1984 to 2025, queried from the Earth Engine catalogue 2026-08-18. Metadata about the archive, not an outcome. Establishes that 2012 carries 611 Landsat 7 scenes and none from any other mission, so excluding Landsat 7 leaves that year without coverage. |
| `review-search.jsonl`, `review-records.csv`, `review-reading-list.csv` and the other review tables | `05.scripts/05-` through `10-` | The prior-work survey's search, screening, prioritisation and citation-verification ledgers. Every count in `docs/science-superpowers/prior-work/2026-08-18-survey.md` is reproducible from them. The 29 MB raw search file is gitignored; the small tables are committed. |

## Planned

Named in the draft framing document and **not retrieved**. Every licence below is recorded
as it will have to be read, from the source, on the retrieval date, before the dataset is
used.

| Dataset | Intended role | Source | Licence status |
|---|---|---|---|
| Landsat Collection 2 Level-2 surface reflectance, Tier 1 | Spread-front observation tier: dated, spatially explicit damage signal independent of the survey sketch polygons | USGS EROS, via the STAC catalogue or Microsoft Planetary Computer; collection, tier, path/row footprint and temporal coverage fixed in the framing document | **Unread.** USGS Landsat is customarily unrestricted, but the statement must be read from the USGS page on the retrieval date and quoted here. Never recorded from memory. |
| Pest Infestation Polygons, multi-year archive | Reference tier: dated polygons giving outbreak extent per year, the same archive Study 1 used | BC Data Catalogue record `450b67bb-02d5-4526-8bc0-ac7924125a1e` | Open Government Licence - British Columbia, read from the catalogue API 2026-08-16 in the Study 1 manifest. Re-read on retrieval into this repository. |
| Natural resource region boundaries | Cartography and any regional stratification | BC openmaps WFS layer `WHSE_ADMIN_BOUNDARIES.ADM_NR_REGIONS_SPG` | Open Government Licence - British Columbia, per the Study 1 manifest. Re-read on retrieval. |
| Host distribution layer, source not yet chosen | Confound: lodgepole pine availability bounds where the front can travel | To be named at design | Unread |

A copy taken from a sibling repository is recorded as copied, with the sibling named and
its recorded hash compared, exactly as Study 1 recorded its copy of the survey archive.

## Streaming or on-demand

Sources used without a local copy: web services, cloud archives, and anything whose licence
forbids bulk download. Record the endpoint, the terms read from the live page, and the date.

- None yet. Landsat is expected to be read this way, scene-windowed rather than bulk
  downloaded, given the 8 GB machine.
