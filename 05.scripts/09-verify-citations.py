#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md, which makes
# CrossRef the registry of record: every entry that reaches references.bib is
# taken from a CrossRef response by DOI, never from a search result or memory.
#
# Writes 02.inputs/derived/citation-verification.csv and prints BibTeX taken
# from the CrossRef response.

import csv
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "02.inputs" / "derived" / "citation-verification.csv"

DOIS = {
    "Aukema_2006": "10.1111/j.2006.0906-7590.04445.x",
    "Aukema_2008": "10.1111/j.0906-7590.2007.05453.x",
    "Zhu_2014": "10.1111/j.1600-0587.2013.00470.x",
    "Zhu_2011": "10.1890/es10-00172.1",
    "Preisler_2009": "10.1029/2008jg000760",
    "Sambaraju_2008": "10.1111/j.1365-2656.2008.01389.x",
    "Robertson_2009": "10.1111/j.1365-2699.2009.02100.x",
    "deLaGiroday_2012": "10.1111/j.1365-2699.2011.02673.x",
    "Jackson_2008": "10.1139/x08-066",
    "Safranyik_1992": "10.1111/j.1439-0418.1992.tb00687.x",
    "Evenden_2018": "10.1111/afe.12305",
    "Howard_2026": "10.1002/ecy.70305",
    "CookeCarroll_2017": "10.1016/j.foreco.2016.11.035",
    "GilbertLiebhold_2010": "10.1111/j.1600-0587.2009.06018.x",
    "Tobin_2015": "10.1079/9781780643946.0131",
    "Clark_2001": "10.1086/319934",
    "Peltonen_2002": "10.1890/0012-9658(2002)083[3120:SSIFIO]2.0.CO;2",
    "Lande_1999": "10.1086/303240",
    "Koenig_2002": "10.1034/j.1600-0587.2002.250304.x",
    "Coleman_2018": "10.1016/j.foreco.2018.08.020",
    "JohnsonRoss_2008a": "10.1080/00049158.2008.10675037",
    "JohnsonRoss_2008b": "10.1080/00049158.2008.10675038",
    "Bright_2020": "10.3390/f11050529",
    "Hall_1996": "10.1139/x26-238",
    "Perbet_2025": "10.1038/s41597-025-06269-x",
    "Wulder_2003": "10.14358/pers.69.3.283",
    "Wulder_2008": "10.5558/tfc84900-6",
    "VasseurFox_2011": "10.1111/j.1461-0248.2010.01567.x",
    "Kendall_2000": "10.1034/j.1600-0706.2000.900202.x",
    "Meddens_2014": "10.1016/j.rse.2014.03.027",
    "Cerezke_1989": "10.4039/ent121337-2",
    "Bjornstad_2001": "10.1016/s0169-5347(01)02097-5",
}


def crossref(doi):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": "prior-work-survey"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["message"]


def main():
    rows = []
    for key, doi in DOIS.items():
        try:
            m = crossref(doi)
            authors = m.get("author") or []
            first = (authors[0].get("family") if authors else "") or ""
            title = (m.get("title") or [""])[0]
            ct = m.get("container-title") or [""]
            year = None
            for f in ("published-print", "published-online", "issued", "created"):
                if m.get(f, {}).get("date-parts", [[None]])[0][0]:
                    year = m[f]["date-parts"][0][0]
                    break
            rows.append({"key": key, "doi": doi, "status": "verified",
                         "first_author": first, "year": year, "title": title,
                         "container": ct[0] if ct else "",
                         "volume": m.get("volume", ""), "issue": m.get("issue", ""),
                         "page": m.get("page", ""), "type": m.get("type", ""),
                         "n_authors": len(authors)})
            print(f"OK   {key:20} {first} {year} | {title[:70]}")
        except Exception as e:
            rows.append({"key": key, "doi": doi, "status": f"FAILED {e}",
                         "first_author": "", "year": "", "title": "",
                         "container": "", "volume": "", "issue": "", "page": "",
                         "type": "", "n_authors": ""})
            print(f"FAIL {key:20} {doi}  {e}", file=sys.stderr)
        time.sleep(0.3)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nverified {sum(1 for r in rows if r['status']=='verified')} of {len(rows)}")


if __name__ == "__main__":
    main()
