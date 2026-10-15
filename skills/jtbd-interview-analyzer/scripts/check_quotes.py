#!/usr/bin/env python3
"""Check that every quote appears word for word in the research.

Usage:
    python check_quotes.py evidence.csv RESEARCH_DIR [RESEARCH_DIR ...]
    python check_quotes.py jobs.csv RESEARCH_DIR [RESEARCH_DIR ...]

Every skill carries an identical copy of this file.
evidence.csv rows are checked by source_id and quote; jobs.csv rows by the excerpts in
evidence and contradicts.

An excerpt passes when its words appear, in order and uninterrupted, in a research file
that also mentions its source ID (INT-01, SUP-04 ...). Comparison ignores case,
punctuation, curly vs straight quotes and whitespace. Text in [square brackets] after
the excerpt is treated as an annotation and skipped. "..." splits an excerpt into parts
that must each be found, in order.

Exit code 0 when every excerpt is found, 1 otherwise. Text files only (.md, .txt, .csv,
.vtt, .srt); convert other formats to text first.
"""
import csv, os, re, sys

TEXT_EXT = (".md", ".txt", ".csv", ".vtt", ".srt", ".json")


def words(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"(?<=\w)'(?=\w)", "", s)  # don't -> dont
    return re.findall(r"[a-z0-9%≥≤–\-]+", s.lower())


def load(dirs):
    files = []
    for d in dirs:
        for root, _, names in os.walk(d):
            for n in names:
                if n.lower().endswith(TEXT_EXT):
                    p = os.path.join(root, n)
                    txt = open(p, encoding="utf-8", errors="replace").read()
                    files.append((p, txt, " ".join(words(txt))))
    return files


def split(field):
    for part in (field or "").split("||"):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^([A-Z]{2,5}-[\w-]+)\s*:\s*(.*)$", part, re.S)
        if m:
            yield m.group(1), m.group(2).strip()


def found(excerpt, files, sid):
    text = re.sub(r"\[[^\]]*\]\s*$", "", excerpt).strip()
    parts = [p for p in re.split(r"\.\.\.|…", text) if words(p)]
    for path, raw, norm in files:
        if sid not in raw and sid not in os.path.basename(path):
            continue
        pos, ok = 0, True
        for p in parts:
            needle = " ".join(words(p))
            i = norm.find(needle, pos)
            if i < 0:
                ok = False
                break
            pos = i + len(needle)
        if ok:
            return path
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    files = load(sys.argv[2:])
    if not files:
        print("No text files found in", sys.argv[2:])
        sys.exit(2)
    rows = list(csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8-sig")))
    rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in r.items() if k} for r in rows]
    total, missing, no_evidence = 0, [], []
    if rows and "quote" in rows[0] and "source_id" in rows[0]:   # evidence.csv
        for r in rows:
            total += 1
            if not found(r["quote"], files, r["source_id"]):
                missing.append((r.get("evidence_id"), "quote", r["source_id"], r["quote"]))
        print(f"{total} quotes checked; {len(missing)} not found")
        for eid, kind, sid, ex in missing:
            print(f"  NOT FOUND  {eid} {sid}: {ex}")
        sys.exit(1 if missing else 0)
    rows = [r for r in rows if (r.get("record_type") or "job") == "job"]
    for r in rows:
        label = r.get("label") or r.get("id")
        ev = list(split(r.get("evidence", "")))
        if not ev and (r.get("provenance") or "").lower() != "unverified":
            no_evidence.append(label)
        for kind in ("evidence", "contradicts"):
            for sid, ex in split(r.get(kind, "")):
                total += 1
                if not found(ex, files, sid):
                    missing.append((label, kind, sid, ex))
    print(f"{total} excerpts checked across {len(rows)} jobs; {len(missing)} not found; "
          f"{len(no_evidence)} jobs without evidence")
    for label, kind, sid, ex in missing:
        print(f"  NOT FOUND  job {label} ({kind}) {sid}: {ex}")
    for label in no_evidence:
        print(f"  NO EVIDENCE  job {label}")
    sys.exit(1 if missing or no_evidence else 0)


if __name__ == "__main__":
    main()
