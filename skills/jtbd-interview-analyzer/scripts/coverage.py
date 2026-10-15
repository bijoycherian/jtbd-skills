#!/usr/bin/env python3
"""Coverage report for an evidence file (card 3).

Usage:
    python coverage.py evidence.csv RESEARCH_DIR [--product-terms "upgrade,TV offers"]

Reports quotes per source and type, sources with no quotes (listed, never dropped),
the spread by speaker role, and the share of quotes that mention your own products
(a high share can mean the interview guide was leading).
"""
import argparse, csv, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from size_plan import scan  # noqa: E402

SID = re.compile(r"\b([A-Z]{2,5}-[\w]+)")


def source_ids(research):
    """Source IDs present in the research: from file names and from IDs written inside files."""
    ids = {}
    readable, _ = scan([research])
    for f, _ in readable:
        base = os.path.splitext(os.path.basename(f))[0].upper()
        found = set(SID.findall(open(f, encoding="utf-8", errors="replace").read()))
        if re.fullmatch(r"[A-Z]{2,5}-\w+", base):
            found.add(base)
        for s in found:
            ids.setdefault(s, os.path.basename(f))
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence"); ap.add_argument("research")
    ap.add_argument("--product-terms", default="")
    a = ap.parse_args()
    rows = [{k.strip().lower(): (v or "").strip() for k, v in r.items() if k}
            for r in csv.DictReader(open(a.evidence, newline="", encoding="utf-8-sig"))]
    by_src, by_type, by_role = {}, {}, {}
    for r in rows:
        by_src[r["source_id"]] = by_src.get(r["source_id"], 0) + 1
        by_type[r.get("type") or "?"] = by_type.get(r.get("type") or "?", 0) + 1
        by_role[r.get("speaker_role") or "?"] = by_role.get(r.get("speaker_role") or "?", 0) + 1
    ids = source_ids(a.research)
    # file-level IDs (INT-01) vs item IDs inside a file (SUP-118): a file counts as covered if any of its IDs has quotes
    files = {}
    for s, f in ids.items():
        files.setdefault(f, set()).add(s)
    empty = sorted(f for f, s in files.items() if not any(by_src.get(x) for x in s))
    print(f"Coverage: {len(rows)} quotes from {sum(1 for f, s in files.items() if any(by_src.get(x) for x in s))} "
          f"of {len(files)} sources.")
    print("By source: " + ", ".join(f"{k} {v}" for k, v in sorted(by_src.items())))
    print("By type: " + ", ".join(f"{k} {v}" for k, v in sorted(by_type.items(), key=lambda kv: -kv[1])))
    print("By speaker role: " + ", ".join(f"{k} {v}" for k, v in sorted(by_role.items(), key=lambda kv: -kv[1])))
    for f in empty:
        print(f"No relevant quotes: {f} (listed, so it won't silently shape the results)")
    terms = [t.strip().lower() for t in a.product_terms.split(",") if t.strip()]
    if terms and rows:
        hit = sum(any(t in r["quote"].lower() for t in terms) for r in rows)
        share = round(100 * hit / len(rows))
        print(f"Quotes mentioning your own products: {hit} of {len(rows)} ({share}%)"
              + (". High: check the interview guide didn't lead people to your offers." if share >= 30 else "."))


if __name__ == "__main__":
    main()
