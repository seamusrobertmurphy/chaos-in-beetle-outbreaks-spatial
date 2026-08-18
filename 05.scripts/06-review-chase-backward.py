#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md.
#
# The protocol requires backward and forward citation chasing from three seeds.
# Semantic Scholar returned zero references for all three, so its reference
# lists do not cover them. This recovers the backward chase from OpenAlex
# referenced_works, which fulfils the protocol's stated chase by another route.
# Appends to review-search.jsonl and review-search-log.csv.

import csv
import json
import pathlib
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DERIVED = ROOT / "02.inputs" / "derived"
OUT_JSONL = DERIVED / "review-search.jsonl"
OUT_LOG = DERIVED / "review-search-log.csv"

OA = "https://api.openalex.org"
FIELDS = ("id,doi,title,publication_year,type,cited_by_count,"
          "primary_location,abstract_inverted_index")

SEEDS = {
    "10.1111/j.2006.0906-7590.04445.x": "Aukema_2006",
    "10.1134/S0006350916020147": "Perevaryukha_2016",
    "10.1007/s10559-019-00119-6": "Perevaryukha_2019",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "prior-work-survey"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def abstract(inv):
    if not inv:
        return None
    pos = {}
    for w, ix in inv.items():
        for i in ix:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def flatten(p):
    loc = p.get("primary_location") or {}
    src = (loc.get("source") or {}) if isinstance(loc, dict) else {}
    return {
        "strand": "openalex",
        "openalexId": p.get("id"),
        "title": p.get("title"),
        "abstract": abstract(p.get("abstract_inverted_index")),
        "year": p.get("publication_year"),
        "venue": src.get("display_name"),
        "type": p.get("type"),
        "citationCount": p.get("cited_by_count"),
        "externalIds": {"DOI": (p.get("doi") or "").replace("https://doi.org/", "") or None},
    }


def main():
    rows = []
    with open(OUT_JSONL, "a") as out:
        for doi, label in SEEDS.items():
            work = get(f"{OA}/works/doi:{urllib.parse.quote(doi)}?select=referenced_works")
            refs = work.get("referenced_works") or []
            time.sleep(0.2)
            n = 0
            for i in range(0, len(refs), 50):
                ids = "|".join(w.rsplit("/", 1)[-1] for w in refs[i:i + 50])
                params = urllib.parse.urlencode(
                    {"filter": f"openalex_id:{ids}", "select": FIELDS, "per-page": 200})
                r = get(f"{OA}/works?{params}")
                for p in (r.get("results") or []):
                    out.write(json.dumps(flatten(p)) + "\n")
                    n += 1
                time.sleep(0.2)
            out.flush()
            rows.append({"strand": "openalex", "route": f"chase1-references-{label}",
                         "query": f"DOI:{doi}", "retrieved": n,
                         "reported_total": len(refs), "cap": 3000,
                         "capped": False, "error": ""})
            print(f"chase1-references-{label}: {n} of {len(refs)} referenced works")
    with open(OUT_LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["strand", "route", "query", "retrieved",
                                          "reported_total", "cap", "capped", "error"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
