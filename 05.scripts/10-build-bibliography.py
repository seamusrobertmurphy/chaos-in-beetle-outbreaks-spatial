#!/usr/bin/env python3
# HAND-WRITTEN review tooling, not generated from the manuscript. Governed by
# docs/science-superpowers/prior-work/2026-08-18-review-protocol.md, which makes
# CrossRef the registry of record.
#
# Fetches BibTeX by DOI content negotiation from CrossRef, rekeys each entry to
# FirstAuthorFamily_Year, and writes 04.references/references.bib. Every entry in
# the output came from a CrossRef response, never from memory. Keys that fail are
# reported and are not written.

import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "04.references" / "references.bib"
LOG = ROOT / "02.inputs" / "derived" / "bibliography-build-log.csv"

ENTRIES = [
    ("Aukema_2006", "10.1111/j.2006.0906-7590.04445.x"),
    ("Aukema_2008", "10.1111/j.0906-7590.2007.05453.x"),
    ("Bjornstad_2001", "10.1023/a:1009601932481"),
    ("Bright_2020", "10.3390/f11050529"),
    ("Chen_2011", "10.1890/es10-00172.1"),
    ("Chen_2014", "10.1111/j.1600-0587.2013.00470.x"),
    ("Clark_2001", "10.1086/319934"),
    ("Coggins_2008", "10.5558/tfc84900-6"),
    ("Coleman_2018", "10.1016/j.foreco.2018.08.020"),
    ("Cooke_2017", "10.1016/j.foreco.2017.04.008"),
    ("Fox_2011", "10.1111/j.1461-0248.2010.01567.x"),
    ("Franklin_2003", "10.14358/pers.69.3.283"),
    ("Gamarra_2008", "10.1111/j.1365-2656.2008.01389.x"),
    ("Gilbert_2010", "10.1111/j.1600-0587.2009.06018.x"),
    ("Giroday_2012", "10.1111/j.1365-2699.2011.02673.x"),
    ("Jackson_2008", "10.1139/x08-066"),
    ("Johnson_2008a", "10.1080/00049158.2008.10675037"),
    ("Johnson_2008b", "10.1080/00049158.2008.10675038"),
    ("Johnson_2026", "10.1002/ecy.70305"),
    ("Koenig_2002", "10.1034/j.1600-0587.2002.250304.x"),
    ("Lande_1999", "10.1086/303240"),
    ("MacLean_1996", "10.1139/x26-238"),
    ("MaciasFauria_2009", "10.1029/2008jg000760"),
    ("Meddens_2014", "10.1016/j.foreco.2014.02.037"),
    ("Peltonen_2002", "10.1890/0012-9658(2002)083[3120:SSIFIO]2.0.CO;2"),
    ("Perbet_2025", "10.1038/s41597-025-06269-x"),
    ("Perevaryukha_2016", "10.1134/S0006350916020147"),
    ("Perevaryukha_2019", "10.1007/s10559-019-00119-6"),
    ("Robertson_2009", "10.1111/j.1365-2699.2009.02100.x"),
    ("Safranyik_1992", "10.1111/j.1439-0418.1992.tb00687.x"),
    ("Safranyik_2010", "10.4039/n08-cpa01"),
    ("Senf_2017", "10.1016/j.jag.2017.04.004"),
    ("Shegelski_2019", "10.1111/afe.12305"),
    ("Skellam_1951", "10.2307/2332328"),
    ("Tobin_2015", "10.1079/9781780643946.0131"),
    ("Ye_2021", "10.1016/j.rse.2021.112560"),
]

HEADER = """% Every entry below was fetched from CrossRef by DOI content negotiation on
% 2026-08-18 by 05.scripts/10-build-bibliography.py and rekeyed to
% FirstAuthorFamily_Year. No entry was written from memory, and no entry was
% copied from another repository's manifest on trust.
%
% Read status and citability are recorded per entry in 04.references/README.md.
% A claim resting on an abstract is marked there as resting on an abstract.
"""


def fetch_bibtex(doi):
    url = f"https://doi.org/{urllib.parse.quote(doi, safe='/:')}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/x-bibtex", "User-Agent": "prior-work-survey"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def rekey(bib, key):
    return re.sub(r"^@(\w+)\{[^,]*,", lambda m: f"@{m.group(1)}{{{key},", bib.strip(),
                  count=1, flags=re.M)


def main():
    written, failed = [], []
    chunks = []
    for key, doi in ENTRIES:
        for attempt in range(4):
            try:
                bib = rekey(fetch_bibtex(doi), key)
                chunks.append(bib)
                written.append((key, doi))
                print(f"OK   {key}")
                break
            except Exception as e:
                if attempt == 3:
                    failed.append((key, doi, str(e)[:120]))
                    print(f"FAIL {key} {doi}: {e}", file=sys.stderr)
                else:
                    time.sleep(4 * (attempt + 1))
        time.sleep(1.0)
    OUT.write_text(HEADER + "\n" + "\n\n".join(chunks) + "\n")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "w") as f:
        f.write("key,doi,status,note\n")
        for k, d in written:
            f.write(f"{k},{d},written,\n")
        for k, d, e in failed:
            f.write(f'{k},{d},failed,"{e}"\n')
    print(f"\nwrote {len(written)} entries, {len(failed)} failed")


if __name__ == "__main__":
    main()
