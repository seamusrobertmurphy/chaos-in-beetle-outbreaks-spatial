#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md.
#
# Pass 1 (identification): deduplicate by DOI, falling back to normalised title.
# Pass 2 (mechanical screen): apply the protocol's vocabulary criteria by script
# and record the decision and reason code per record, so a reader can see which
# decisions a script made rather than a person.
#
# Reads  02.inputs/derived/review-search.jsonl
# Writes 02.inputs/derived/review-records.csv
#        02.inputs/derived/review-screen-counts.csv

import collections
import csv
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
DERIVED = ROOT / "02.inputs" / "derived"
IN_JSONL = DERIVED / "review-search.jsonl"
OUT_RECORDS = DERIVED / "review-records.csv"
OUT_COUNTS = DERIVED / "review-screen-counts.csv"

YEAR_MIN, YEAR_MAX = 1950, 2026

# Vocabulary. Matched case-insensitively against title plus abstract.
BEETLE = r"(mountain pine beetle|dendroctonus|bark beetle|scolytid|ips typographus|" \
         r"spruce beetle|budworm|choristoneura|defoliator|forest insect|forest pest|" \
         r"lymantria|gypsy moth|spongy moth|pine beetle|engraver beetle)"
SPREAD = r"(spread|dispersal|dispersing|invasion|invasive|range expansion|expansion|" \
         r"spreading|colonis|coloniz|diffusion|wave[- ]?front|invasion front|" \
         r"travell?ing wave|spread rate|rate of spread|invasion speed|front velocity|" \
         r"range shift|migration)"
SYNC = r"(synchron|moran effect|spatial correlation|spatial autocorrelation|" \
       r"cross[- ]correlation|semivariogram|variogram|correlogram|spatial dependence|" \
       r"spatial covariance|correlation function)"
SURVEY = r"(aerial overview survey|aerial detection survey|aerial survey|sketch[- ]?map|" \
         r"overview survey|aerial sketch|forest health survey|damage survey)"
RS = r"(landsat|sentinel-2|remote sensing|satellite|landtrendr|ccdc|bfast|" \
     r"vegetation change tracker|time series segmentation|disturbance detection|" \
     r"change detection|disturbance mapping|surface reflectance)"
REGIME = r"(bifurcation|period[- ]doubling|period doubling|chaos|chaotic|attractor|" \
         r"regime shift|dynamical regime|feigenbaum|pulsed front|patchy invasion|" \
         r"pulsating|nonlinear dynamic|limit cycle)"
METHOD = r"(estimat|method|model|rate|velocity|speed|regression|likelihood|bayesian|" \
         r"simulat|statistic|inference|algorithm)"
BIO = r"(population|ecolog|species|insect|forest|tree|beetle|moth|host|organism|" \
      r"epidemi|outbreak|biolog|invasion)"
DISPERSAL = r"(dispersal|flight|flying|above[- ]canopy|long[- ]distance|mark[- ]release|" \
            r"recapture|trap catch|pheromone trap|wind[- ]assisted|atmospheric transport)"
GRADIENT = r"(gradient|elevation|latitud|temperature gradient|environmental gradient|" \
           r"climatic gradient|thermal gradient)"

NOT_RESEARCH_TITLE = r"^(editorial|erratum|corrigendum|correction|retraction|" \
                     r"book review|comment on|reply to|introduction to the special|" \
                     r"in memoriam|obituary|preface|foreword|announcement|index to)"
NOT_RESEARCH_TYPE = {"editorial", "erratum", "letter", "paratext", "peer-review",
                     "retraction", "grant", "other", "supplementary-materials"}


def has(pattern, text):
    return re.search(pattern, text, re.I) is not None


def norm_title(t):
    t = unicodedata.normalize("NFKD", (t or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", t.lower())


def questions_matched(text):
    """Which review questions a record bears on. Empty means none."""
    q = []
    b, sp, sy = has(BEETLE, text), has(SPREAD, text), has(SYNC, text)
    if b and (sy or sp):
        q.append("q1")
    if sp and has(METHOD, text) and has(BIO, text):
        q.append("q2")
    if b and sp and has(r"(rate|speed|velocity|km|kilomet|per year|yr-1|annual)", text):
        q.append("q3")
    if b and has(DISPERSAL, text):
        q.append("q4")
    if sy and has(BIO, text):
        q.append("q5")
    if has(SURVEY, text) and has(r"(forest|insect|defoliat|damage|mortality|pest)", text):
        q.append("q6")
    if has(RS, text) and has(r"(disturbance|forest|mortality|damage|change)", text):
        q.append("q7")
    if has(REGIME, text) and (sp or sy or has(GRADIENT, text)):
        q.append("q8")
    if has(r"feigenbaum", text):
        q.append("q9")
    return q


def main():
    seen, records = {}, []
    n_raw = 0
    with open(IN_JSONL) as f:
        for line in f:
            n_raw += 1
            p = json.loads(line)
            doi = ((p.get("externalIds") or {}).get("DOI") or "").strip().lower() or None
            title = (p.get("title") or "").strip()
            key = f"doi:{doi}" if doi else f"ttl:{norm_title(title)}"
            if not title:
                continue
            if key in seen:
                r = seen[key]
                r["strands"].add(p.get("strand", ""))
                if not r["abstract"] and p.get("abstract"):
                    r["abstract"] = p["abstract"]
                r["n_dup"] += 1
                continue
            r = {"key": key, "doi": doi, "title": title,
                 "abstract": p.get("abstract") or "",
                 "year": p.get("year"), "venue": p.get("venue") or "",
                 "type": (p.get("type") or ""),
                 "citations": p.get("citationCount"),
                 "strands": {p.get("strand", "")}, "n_dup": 0}
            seen[key] = r
            records.append(r)

    counts = collections.Counter()
    rows = []
    for r in records:
        text = f"{r['title']} {r['abstract']}"
        title_only = not r["abstract"]
        decision, reason = "pass", ""
        yr = r["year"]
        if r["type"] in NOT_RESEARCH_TYPE or has(NOT_RESEARCH_TITLE, r["title"]):
            decision, reason = "exclude", "not-research"
        elif yr is None or not (YEAR_MIN <= int(yr) <= YEAR_MAX):
            decision, reason = "exclude", "out-of-window"
        elif len(re.findall(r"[a-zA-Z]", r["title"])) < 0.5 * max(1, len(r["title"])):
            decision, reason = "exclude", "not-english"
        else:
            qs = questions_matched(text)
            if not qs:
                topical = any(has(p, text) for p in (BEETLE, SPREAD, SYNC, SURVEY, RS, REGIME))
                decision = "exclude"
                reason = "off-topic" if topical else "no-spread"
            elif qs == ["q8"] and not has(BIO, text):
                decision, reason = "exclude", "not-ecology"
            else:
                r["questions"] = qs
        counts[reason or "pass"] += 1
        rows.append({
            "key": r["key"], "doi": r["doi"] or "", "title": r["title"],
            "year": yr if yr is not None else "", "venue": r["venue"],
            "type": r["type"], "citations": r["citations"] if r["citations"] is not None else "",
            "strands": "+".join(sorted(s for s in r["strands"] if s)),
            "duplicates_merged": r["n_dup"],
            "title_only": int(title_only),
            "questions": " ".join(r.get("questions", [])),
            "decision": decision, "reason": reason,
        })

    with open(OUT_RECORDS, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n_unique = len(rows)
    n_pass = sum(1 for r in rows if r["decision"] == "pass")
    with open(OUT_COUNTS, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["stage", "count"])
        w.writerow(["raw records retrieved", n_raw])
        w.writerow(["unique after deduplication", n_unique])
        w.writerow(["duplicates removed", n_raw - n_unique])
        for reason, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            w.writerow([f"mechanical screen: {reason}", n])
        w.writerow(["passed to reading screen", n_pass])
        w.writerow(["passed but title only, no abstract",
                    sum(1 for r in rows if r["decision"] == "pass" and r["title_only"])])
        w.writerow(["records in both strands",
                    sum(1 for r in rows if "+" in r["strands"])])

    print(f"raw {n_raw} -> unique {n_unique} -> pass {n_pass}")
    for reason, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {reason}: {n}")


if __name__ == "__main__":
    main()
