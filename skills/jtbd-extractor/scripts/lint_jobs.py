#!/usr/bin/env python3
"""Automatic statement checks for draft or final jobs (SKILL.md step 5, checks marked ⚙).

Usage:
    python lint_jobs.py jobs.csv

Checks: no solution in the goal (1), one need per statement (2), customer voice (3),
distinct outcome (4), barrier consistent with satisfaction (5, when scored), exactly one
persona (9), evidence attached (11). The rest need judgement; see SKILL.md.
Exit 1 if any job fails.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jtbd_files as jf  # noqa: E402

SOLUTION = re.compile(r"\b(app|feature|button|chat|dashboard|portal|integration|notification|reminders?|"
                      r"automatic(ally)?|real[- ]time|documentation|api|plugin|widget|screen|tab|upgrade|tv channel)\b", re.I)
COMPANY = re.compile(r"\b(because (we|the company|our product) (is|are)n?'?t|our platform|marketplace|PDP|SKU|e2e|upsell|ancillar(y|ies))\b", re.I)
NOT_EXIST = re.compile(r"\b(don'?t|do not|can'?t|cannot|no) (have )?(the )?(option|way|ability|access)\b|\bcan'?t\b|\bcannot\b", re.I)
TWO_NEEDS = re.compile(r"\b(and|&)\b.*\b(also|chat|communicat)|\band\b.*\band\b", re.I)


def lint(jobs):
    out = {}
    outcomes = {}
    for j in jobs:
        outcomes.setdefault((j.get("outcome") or "").strip().lower(), []).append(j["label"])
    for j in jobs:
        f = []
        goal = j.get("goal", "")
        if SOLUTION.search(goal):
            f.append("1 the goal names a product or mechanism; describe the need")
        if TWO_NEEDS.search(goal):
            f.append("2 the goal may hold two needs; split them")
        if COMPANY.search(" ".join(j.get(k, "") for k in ("context", "barrier", "goal", "outcome"))):
            f.append("3 company language; use the customer's words")
        same = [x for x in outcomes.get((j.get("outcome") or "").strip().lower(), []) if x != j["label"]]
        if same and j.get("outcome"):
            f.append(f"4 the 'so' part matches job {', '.join(same)}; make the outcome specific")
        sat = jf.num(j.get("satisfaction"))
        if sat is not None and sat >= 80 and NOT_EXIST.search(j.get("barrier", "")):
            f.append("5 the barrier says it can't be done, yet satisfaction is 80 or more")
        if not j.get("persona") or re.search(r"/|,|\band\b", j.get("persona", "")):
            f.append("9 needs exactly one persona")
        if not (j.get("evidence") or j.get("evidence_ids")) and (j.get("provenance") or "").lower() != "unverified":
            f.append("11 no evidence attached")
        for k in ("context", "barrier", "goal", "outcome"):
            if not j.get(k):
                f.append(f"format: {k} is blank (When / but / help me / so)")
        out[j["label"]] = f
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    jobs = jf.read_jobs(sys.argv[1])[0]
    res = lint(jobs)
    bad = {k: v for k, v in res.items() if v}
    print(f"{len(jobs)} jobs checked; {len(bad)} with issues")
    for k, v in bad.items():
        for x in v:
            print(f"  job {k}: check {x}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
