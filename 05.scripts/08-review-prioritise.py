#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md and by the
# dated prioritisation deviation recorded in it.
#
# The mechanical screen passed 5990 records, which no single reviewer reads.
# This stage scores each passing record against the question it matched, marks
# records hit by a question's decisive pattern, and writes a reading list with
# an explicit per-question budget. What the budget drops is counted per question
# and written out, so the cap is visible rather than silent.
#
# Reads  02.inputs/derived/review-records.csv
#        02.inputs/derived/review-search.jsonl   (for abstracts)
# Writes 02.inputs/derived/review-reading-list.csv
#        02.inputs/derived/review-priority-counts.csv

import collections
import csv
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DERIVED = ROOT / "02.inputs" / "derived"

BUDGET = 60  # abstracts read per question, on top of every decisive-pattern hit

# Scored terms per question. Weight reflects how directly a term bears on the
# question, not how common it is.
SCORES = {
    "q1": [(r"mountain pine beetle", 3), (r"british columbia", 3), (r"synchron", 2),
           (r"spatiotemporal|spatio-temporal", 2), (r"epicent", 3), (r"landscape", 1),
           (r"aerial survey|aerial overview", 2), (r"spread", 2)],
    "q2": [(r"spread rate|rate of spread|invasion speed|spreading speed", 4),
           (r"estimat\w* (the )?(spread|invasion|expansion)", 3),
           (r"skellam|reaction[- ]diffusion|kolmogorov", 3),
           (r"travell?ing wave", 2), (r"wave speed|front speed|front velocity", 4),
           (r"first detection|year of (first )?detection|time of arrival", 4),
           (r"boundary displacement|distance regression|regression of distance", 4),
           (r"stratified dispersal|long[- ]distance dispersal", 2),
           (r"failure|bias|assumption|sensitiv", 1)],
    "q3": [(r"mountain pine beetle", 3), (r"km\s*(per|/)\s*(yr|year)|kilomet\w+ per year", 4),
           (r"spread rate|rate of spread|expansion rate", 4),
           (r"range expansion", 3), (r"alberta|british columbia", 2),
           (r"\bkm\b", 1), (r"aerial survey|aerial overview", 1)],
    "q4": [(r"mountain pine beetle|dendroctonus ponderosae", 3),
           (r"long[- ]distance dispersal", 4), (r"above[- ]canopy|above the canopy", 4),
           (r"flight|flying|dispersal distance", 3),
           (r"mark[- ]release|recapture|trap|radar", 2),
           (r"wind|atmospheric transport|convect", 2), (r"\bkm\b|metre|meter", 1)],
    "q5": [(r"spatial synchrony|population synchrony", 4), (r"moran effect", 4),
           (r"synchrony scale|scale of synchrony|spatial scale of", 4),
           (r"correlation function|nonparametric covariance|spline correlogram", 4),
           (r"dispersal (versus|vs|and) (environment|climate|moran)", 4),
           (r"bootstrap|confidence (interval|envelope)", 2), (r"variogram|correlogram", 2)],
    "q6": [(r"aerial overview survey|aerial detection survey", 4),
           (r"sketch[- ]?map", 4), (r"positional (accuracy|error)|locational accuracy", 4),
           (r"accuracy|omission|commission|agreement|validation", 2),
           (r"british columbia|canada", 2), (r"survey\w* bias|observer|effort", 3),
           (r"polygon", 2)],
    "q7": [(r"landtrendr|ccdc|bfast|vegetation change tracker|vct", 4),
           (r"temporal accuracy|timing error|dating|year of disturbance|detection delay", 4),
           (r"disturbance", 2), (r"landsat", 2), (r"bark beetle|mountain pine beetle", 3),
           (r"accuracy assess|validation|reference (data|plots)", 2),
           (r"annual|time series", 1)],
    "q8": [(r"bifurcation", 3), (r"invasion front|spread front|range front", 3),
           (r"pulsed|pulsating|patchy invasion|oscillat", 3),
           (r"environmental gradient|climatic gradient|latitudinal gradient", 4),
           (r"regime", 2), (r"empirical|field|observed", 2)],
    "q9": [(r"feigenbaum", 4), (r"period[- ]doubling", 3), (r"cascade", 2),
           (r"empirical|field|observed|experiment", 2), (r"4\.669", 4)],
}

# A record matching its question's decisive pattern is read whatever its rank.
DECISIVE = {
    "q1": r"(mountain pine beetle|dendroctonus).{0,200}(british columbia).{0,400}(synchron|epicent|spread)",
    "q2": r"(wave speed|front speed|front velocity|spread rate|invasion speed).{0,200}(estimat|method|model|fit)",
    "q3": r"\d+(\.\d+)?\s*(km|kilomet\w+)\s*(per|/|\s+a\s+|\s+)(yr|year|annum)",
    "q4": r"(dispersal|flight|flew|transport).{0,200}\d+(\.\d+)?\s*(km|kilomet\w+)",
    "q5": r"(synchrony|correlation).{0,200}(declin|decay|scale).{0,200}(distance|km)",
    "q6": r"(sketch[- ]?map|aerial (overview|detection) survey).{0,300}(accuracy|error|agreement|bias|precision)",
    "q7": r"(disturbance|change).{0,200}(year|timing|temporal).{0,120}(accuracy|error|agreement|offset)",
    "q8": r"(bifurcation|regime).{0,300}(gradient|along a|across a).{0,120}(temperature|climat|elevation|environment)",
    "q9": r"feigenbaum",
}


def score(text, terms):
    s = 0
    for pat, w in terms:
        if re.search(pat, text, re.I):
            s += w
    return s


def main():
    abstracts = {}
    with open(DERIVED / "review-search.jsonl") as f:
        for line in f:
            p = json.loads(line)
            doi = ((p.get("externalIds") or {}).get("DOI") or "").strip().lower() or None
            key = f"doi:{doi}" if doi else None
            if key and p.get("abstract") and key not in abstracts:
                abstracts[key] = p["abstract"]

    rows = [r for r in csv.DictReader(open(DERIVED / "review-records.csv"))
            if r["decision"] == "pass"]
    for r in rows:
        r["abstract"] = abstracts.get(r["key"], "")

    by_q = collections.defaultdict(list)
    for r in rows:
        text = f"{r['title']} {r['abstract']}"
        for q in r["questions"].split():
            sc = score(text, SCORES[q])
            cites = int(r["citations"]) if r["citations"] else 0
            dec = bool(re.search(DECISIVE[q], text, re.I | re.S))
            by_q[q].append((sc + (4 if dec else 0) + math.log1p(cites) / 10, dec, r))

    chosen, counts = {}, []
    for q in sorted(by_q):
        ranked = sorted(by_q[q], key=lambda t: -t[0])
        keep, dropped, decisive_kept = [], 0, 0
        for i, (sc, dec, r) in enumerate(ranked):
            if i < BUDGET or dec:
                keep.append((q, i + 1, round(sc, 2), dec, r))
                decisive_kept += int(dec)
            else:
                dropped += 1
        counts.append({"question": q, "passed_screen": len(ranked),
                       "budget": BUDGET, "decisive_hits": sum(1 for t in ranked if t[1]),
                       "selected_for_reading": len(keep), "dropped_unread": dropped})
        for item in keep:
            k = item[4]["key"]
            chosen.setdefault(k, {"row": item[4], "questions": [], "ranks": []})
            chosen[k]["questions"].append(q)
            chosen[k]["ranks"].append(f"{q}:{item[1]}:{item[2]}{'*' if item[3] else ''}")

    out = []
    for k, v in chosen.items():
        r = v["row"]
        out.append({
            "key": k, "doi": r["doi"], "year": r["year"], "venue": r["venue"],
            "citations": r["citations"], "questions": " ".join(v["questions"]),
            "ranks": " ".join(v["ranks"]), "title": r["title"],
            "abstract": re.sub(r"\s+", " ", r["abstract"])[:1500],
        })
    out.sort(key=lambda r: (r["questions"], r["ranks"]))
    with open(DERIVED / "review-reading-list.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    with open(DERIVED / "review-priority-counts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(counts[0].keys()))
        w.writeheader()
        w.writerows(counts)

    print(f"reading list: {len(out)} unique records")
    for c in counts:
        print(f"  {c['question']}: passed {c['passed_screen']:>4}  "
              f"decisive {c['decisive_hits']:>3}  read {c['selected_for_reading']:>3}  "
              f"dropped unread {c['dropped_unread']:>4}")


if __name__ == "__main__":
    main()
