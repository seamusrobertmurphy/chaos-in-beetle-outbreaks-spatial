# Input data manifest

Every dataset entering `02.inputs/` is recorded here on the day it is downloaded, with
integrity hashes appended to `SHA256SUMS.txt`. Raw data are gitignored; this manifest and
the retrieval code are the reproducible record.

The licence column carries what was read from the source on the date given, quoted where
the wording matters. A dataset whose licence page has not been opened is recorded as
unread, never as public domain by assumption. Service metadata counts as the source: a
licence sitting in a service's own metadata is binding even when the endpoint is open.

No outcome analysis is run on any file here until the pre-registration is frozen.

## Downloaded

Nothing. The framing gate is open and blocking, and no retrieval runs before it is
approved.

| Folder | Dataset | Source | Licence | Notes |
|---|---|---|---|---|
| none | none | | | |

## Derived

Intermediate products, each regenerable from the raw inputs and gitignored unless it is a
small table the manuscript cites.

| File | Built by | Contents |
|---|---|---|
| none | | |

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
