#!/usr/bin/env python3
"""Count the words in a study and plan how to read it (card 1 and card 3b).

Usage:
    python size_plan.py RESEARCH_DIR_OR_FILES ... [--json]

Prints what can be read, anything that can't (no text), the total size and the plan:
one pass, batches, or a suggestion to split. Limits come from limits.json next to this
script, which the size test (evals) updates; until it passes, large studies are reported
as not fully tested.
"""
import json, math, os, sys

TEXT_EXT = (".md", ".txt", ".csv", ".vtt", ".srt", ".json", ".tsv")
HERE = os.path.dirname(os.path.abspath(__file__))


def limits():
    p = os.path.join(HERE, "limits.json")
    d = {"one_pass_words": 75000, "batch_words": 75000, "split_above_words": 300000, "tested": False}
    if os.path.exists(p):
        d.update(json.load(open(p, encoding="utf-8")))
    return d


def kind(name):
    n = os.path.basename(name).upper()
    for pre, what in (("INT", "interview"), ("FD", "front desk interview"), ("SUP", "ticket export"),
                      ("FUN", "funnel note"), ("DOC", "document"), ("SUR", "survey file")):
        if n.startswith(pre):
            return what
    return "file"


def scan(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for r, _, fs in os.walk(p):
                files += [os.path.join(r, f) for f in sorted(fs) if not f.startswith(".")]
        else:
            files.append(p)
    readable, unreadable = [], []
    for f in sorted(files):
        if f.lower().endswith(TEXT_EXT):
            txt = open(f, encoding="utf-8", errors="replace").read()
            readable.append((f, len(txt.split())))
        else:
            unreadable.append(f)
    return readable, unreadable


def plan(total, L):
    if total <= L["one_pass_words"]:
        return {"mode": "one pass", "batches": 1}
    b = math.ceil(total / L["batch_words"])
    if total > L["split_above_words"]:
        return {"mode": "split suggested", "batches": b}
    return {"mode": "batches", "batches": b}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(2)
    L = limits()
    readable, unreadable = scan(args)
    total = sum(w for _, w in readable)
    p = plan(total, L)
    if "--json" in sys.argv:
        print(json.dumps({"readable": len(readable), "unreadable": [os.path.basename(u) for u in unreadable],
                          "words": total, "plan": p, "limits": L}, indent=2))
        return
    counts = {}
    for f, _ in readable:
        counts[kind(f)] = counts.get(kind(f), 0) + 1
    n_all = len(readable) + len(unreadable)
    parts = ", ".join(f"{v} {k}{'s' if v != 1 and not k.endswith('export') else ''}" for k, v in counts.items())
    print(f"I can read {len(readable)} of your {n_all} files: {parts}.")
    for u in unreadable:
        print(f"I can't read {os.path.basename(u)} (no text); add a text version if it matters.")
    words = f"about {round(total / 1000)}k words" if total >= 1000 else f"{total} words"
    if p["mode"] == "one pass":
        print(f"Size: {words}. I'll read it in one go.")
    else:
        msg = (f"This study is {words} across {len(readable)} sources, so I'll read it in batches and show "
               "progress as each one finishes; it will take longer than a small study.")
        if not L.get("tested") and total > L["one_pass_words"]:
            msg += " Studies this large haven't been fully tested yet, so splitting it into two will give more reliable results."
        elif p["mode"] == "split suggested":
            msg += " Anything this big, I'd suggest splitting into two studies."
        print(msg)
        print("Shall I start? You can also remove some sources first.")
        print(f"(plan: {p['batches']} batches of up to {L['batch_words']:,} words)")


if __name__ == "__main__":
    main()
