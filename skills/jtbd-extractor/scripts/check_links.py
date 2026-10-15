#!/usr/bin/env python3
"""Check that every job's evidence links resolve to quotes in evidence.csv.

Usage:
    python check_links.py jobs.csv evidence.csv

For each job: every ID in evidence_ids exists in evidence.csv, the job has at least one
(unless its provenance is 'unverified'), and every excerpt quoted inline in `evidence`
matches one of those quotes word for word. Exit 1 on any broken link.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jtbd_files as jf  # noqa: E402


def words(s):
    s = re.sub(r"\[[^\]]*\]\s*$", "", s or "")
    return " ".join(re.findall(r"[a-z0-9%]+", s.lower().replace("’", "'").replace("'", "")))


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    jobs = jf.read_jobs(sys.argv[1])[0]
    ev = {r["evidence_id"]: r for r in jf.read_rows(sys.argv[2])[0]}
    broken, n = [], 0
    for j in jobs:
        L = j["label"]
        ids = [e for e in re.split(r"[;,|\s]+", j.get("evidence_ids", "")) if e]
        if not ids and (j.get("provenance") or "").lower() != "unverified":
            broken.append(f"job {L}: no evidence_ids")
        for e in ids:
            n += 1
            if e not in ev:
                broken.append(f"job {L}: {e} is not in evidence.csv")
        quotes = {words(ev[e]["quote"]) for e in ids if e in ev}
        for part in (j.get("evidence") or "").split("||"):
            part = part.strip()
            if not part:
                continue
            excerpt = part.split(":", 1)[1] if re.match(r"^[A-Z]{2,5}-[\w-]+\s*:", part) else part
            if quotes and words(excerpt) not in quotes:
                broken.append(f"job {L}: inline excerpt isn't one of its linked quotes: {excerpt.strip()[:60]}")
    print(f"{n} links checked across {len(jobs)} jobs; {len(broken)} broken")
    for b in broken:
        print("  " + b)
    sys.exit(1 if broken else 0)


if __name__ == "__main__":
    main()
