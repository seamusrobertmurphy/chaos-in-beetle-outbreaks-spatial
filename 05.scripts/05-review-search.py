#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md, not by the
# pipe-purl do-not-edit rule.
#
# Runs the two independent search strands the protocol fixes, Semantic Scholar
# bulk search and OpenAlex, plus round-one citation chasing from the three seeds
# verified against CrossRef in 04.references/README.md. Writes incrementally so
# an interruption costs one query and not the run.
#
# Outputs:
#   02.inputs/derived/review-search.jsonl      raw records, one per line, with strand and route
#   02.inputs/derived/review-search-log.csv    per-query counts, cap status, errors

import csv
import json
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DERIVED = ROOT / "02.inputs" / "derived"
OUT_JSONL = DERIVED / "review-search.jsonl"
OUT_LOG = DERIVED / "review-search-log.csv"

S2 = "https://api.semanticscholar.org/graph/v1"
S2_FIELDS = "title,abstract,year,venue,externalIds,citationCount"
OA = "https://api.openalex.org/works"
OA_FIELDS = ("id,doi,title,publication_year,type,cited_by_count,"
             "primary_location,abstract_inverted_index")

CAP = 3000          # protocol deviation of 2026-08-18, logged per query
S2_SLEEP = 2.0      # unauthenticated shared rate limit
OA_SLEEP = 0.2

# Nine review questions from the frozen protocol. Keys carry the question number.
S2_QUERIES = {
    "q1-aukema-mpb-spatiotemporal":
        '"mountain pine beetle" (spatiotemporal | "spatial synchrony" | "spatial dynamics" | "outbreak development")',
    "q2-spread-rate-methods":
        '("spread rate" | "invasion speed" | "rate of spread" | "range expansion") (estimat* | method* | model*) (insect | invasion | population)',
    "q2b-kpp-skellam":
        '(Skellam | "reaction-diffusion" | "Kolmogorov-Petrovsky-Piskunov" | "travelling wave" | "traveling wave") (invasion | "population spread" | "biological invasion")',
    "q3-mpb-spread-rate":
        '"mountain pine beetle" (spread | expansion | "range expansion" | "km per year" | "kilometres per year")',
    "q4-mpb-dispersal":
        '("mountain pine beetle" | Dendroctonus) (dispersal | flight | "long-distance" | "long distance dispersal" | "above canopy")',
    "q5-synchrony-methods":
        '("spatial synchrony" | "Moran effect" | "population synchrony") (scale | distance | method* | estimat*)',
    "q6-aerial-survey":
        '("aerial overview survey" | "aerial detection survey" | "sketch mapping" | "aerial survey") (forest | insect | defoliation | accuracy | mapping)',
    "q7-landsat-dating":
        '(Landsat) ("disturbance" | "forest change") (LandTrendr | CCDC | "time series" | "dating" | "detection accuracy" | "temporal accuracy")',
    "q8-spatial-regimes":
        '("pulsed" | "pulsating" | "patchy") ("invasion front" | "spread front" | "range expansion") | ("bifurcation" (spatial | "spreading population" | "invasion front"))',
    "q9-feigenbaum-eco":
        'Feigenbaum (ecology | ecological | population | insect | outbreak)',
}

OA_QUERIES = {
    "q1-aukema-mpb-spatiotemporal":
        '"mountain pine beetle" AND (spatiotemporal OR "spatial synchrony")',
    "q2-spread-rate-methods":
        '("spread rate" OR "invasion speed" OR "rate of spread") AND (insect OR invasion)',
    "q2b-kpp-skellam":
        '("reaction-diffusion" OR "travelling wave" OR "traveling wave") AND ("population spread" OR "biological invasion")',
    "q3-mpb-spread-rate":
        '"mountain pine beetle" AND (spread OR "range expansion")',
    "q4-mpb-dispersal":
        '("mountain pine beetle" OR Dendroctonus) AND dispersal',
    "q5-synchrony-methods":
        '("spatial synchrony" OR "Moran effect") AND (scale OR distance)',
    "q6-aerial-survey":
        '("aerial overview survey" OR "aerial detection survey" OR "sketch mapping") AND forest',
    "q7-landsat-dating":
        'Landsat AND disturbance AND ("time series" OR LandTrendr OR CCDC)',
    "q8-spatial-regimes":
        '("invasion front" OR "spread front") AND (pulsed OR pulsating OR patchy OR bifurcation)',
    "q9-feigenbaum-eco":
        'Feigenbaum AND (ecology OR population OR insect)',
}

SEEDS = {
    "10.1111/j.2006.0906-7590.04445.x": "Aukema_2006",
    "10.1134/S0006350916020147": "Perevaryukha_2016",
    "10.1007/s10559-019-00119-6": "Perevaryukha_2019",
}


def get(url, tries=5):
    req = urllib.request.Request(url, headers={"User-Agent": "prior-work-survey"})
    last = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except Exception as e:
            last = e
            wait = 5 * (attempt + 1)
            print(f"  retry after {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}: {last}")


def s2_bulk(query, out):
    n, token, total, capped = 0, None, None, False
    while True:
        url = f"{S2}/paper/search/bulk?query={urllib.parse.quote(query)}&fields={S2_FIELDS}"
        if token:
            url += f"&token={urllib.parse.quote(token)}"
        r = get(url)
        if total is None:
            total = r.get("total")
        for p in (r.get("data") or []):
            if n >= CAP:
                capped = True
                break
            p["strand"] = "semantic_scholar"
            out.write(json.dumps(p) + "\n")
            n += 1
        token = r.get("token")
        time.sleep(S2_SLEEP)
        if capped or not token:
            out.flush()
            return n, total, capped


def oa_abstract(inv):
    if not inv:
        return None
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def oa_search(query, out):
    n, cursor, total, capped = 0, "*", None, False
    while True:
        params = urllib.parse.urlencode({
            "filter": f"title_and_abstract.search:{query}",
            "select": OA_FIELDS,
            "per-page": 200,
            "cursor": cursor,
        })
        r = get(f"{OA}?{params}")
        if total is None:
            total = (r.get("meta") or {}).get("count")
        results = r.get("results") or []
        for p in results:
            if n >= CAP:
                capped = True
                break
            loc = p.get("primary_location") or {}
            src = (loc.get("source") or {}) if isinstance(loc, dict) else {}
            out.write(json.dumps({
                "strand": "openalex",
                "openalexId": p.get("id"),
                "title": p.get("title"),
                "abstract": oa_abstract(p.get("abstract_inverted_index")),
                "year": p.get("publication_year"),
                "venue": src.get("display_name"),
                "type": p.get("type"),
                "citationCount": p.get("cited_by_count"),
                "externalIds": {"DOI": (p.get("doi") or "").replace("https://doi.org/", "") or None},
            }) + "\n")
            n += 1
        cursor = (r.get("meta") or {}).get("next_cursor")
        time.sleep(OA_SLEEP)
        if capped or not cursor or not results:
            out.flush()
            return n, total, capped


def s2_chase(doi, direction, out):
    key = "citedPaper" if direction == "references" else "citingPaper"
    n, offset, capped = 0, 0, False
    while True:
        url = (f"{S2}/paper/DOI:{doi}/{direction}"
               f"?fields={S2_FIELDS}&limit=500&offset={offset}")
        r = get(url)
        batch = [row.get(key) for row in (r.get("data") or [])]
        for p in batch:
            if not p:
                continue
            if n >= CAP:
                capped = True
                break
            p["strand"] = "semantic_scholar"
            out.write(json.dumps(p) + "\n")
            n += 1
        time.sleep(S2_SLEEP)
        nxt = r.get("next")
        if capped or nxt is None or not batch:
            out.flush()
            return n, n, capped
        offset = nxt


def main():
    DERIVED.mkdir(parents=True, exist_ok=True)
    rows = []
    with open(OUT_JSONL, "w") as out:
        for name, q in S2_QUERIES.items():
            route = f"search-{name}"
            try:
                n, total, capped = s2_bulk(q, out)
                err = ""
            except Exception as e:
                n, total, capped, err = 0, None, False, str(e)[:200]
            rows.append({"strand": "semantic_scholar", "route": route, "query": q,
                         "retrieved": n, "reported_total": total,
                         "cap": CAP, "capped": capped, "error": err})
            print(f"S2 {route}: {n} (reported {total}) capped={capped} {err}")
        for name, q in OA_QUERIES.items():
            route = f"search-{name}"
            try:
                n, total, capped = oa_search(q, out)
                err = ""
            except Exception as e:
                n, total, capped, err = 0, None, False, str(e)[:200]
            rows.append({"strand": "openalex", "route": route, "query": q,
                         "retrieved": n, "reported_total": total,
                         "cap": CAP, "capped": capped, "error": err})
            print(f"OA {route}: {n} (reported {total}) capped={capped} {err}")
        for doi, label in SEEDS.items():
            for direction in ("references", "citations"):
                route = f"chase1-{direction}-{label}"
                try:
                    n, total, capped = s2_chase(doi, direction, out)
                    err = ""
                except Exception as e:
                    n, total, capped, err = 0, None, False, str(e)[:200]
                rows.append({"strand": "semantic_scholar", "route": route,
                             "query": f"DOI:{doi}", "retrieved": n,
                             "reported_total": total, "cap": CAP,
                             "capped": capped, "error": err})
                print(f"S2 {route}: {n} capped={capped} {err}")
    with open(OUT_LOG, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["strand", "route", "query", "retrieved",
                                          "reported_total", "cap", "capped", "error"])
        w.writeheader()
        w.writerows(rows)
    total = sum(r["retrieved"] for r in rows)
    print(f"wrote {total} raw records to {OUT_JSONL}")


if __name__ == "__main__":
    main()
