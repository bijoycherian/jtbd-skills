---
description: "/jtbd with a bare website and the opening answers given, with public reviews already saved in sources/: no framing card, quotes are checked, \"Evidence is in\" reports the bias and keeps company and third-party pages out of customer voice, then checkpoint 1 before any jobs are drafted."
expected_outcome: "No framing card for a bare website; quotes checked by script; an Evidence is in paragraph with source types, quotes matched to their pages, product share and the skew caveat, DOC sources not counted as customer voice; checkpoint 1 with counts as numbered options; no jobs yet."
max_turns: 40
timeout_seconds: 900
runs: 3
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

/jtbd https://www.keyharbor.example There's no web access here, so I've already saved the public reviews and pages in sources/; work from those. Customers: buyers. Decision: product roadmap priorities.
