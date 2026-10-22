---
description: Raw research in a folder; the analyzer lists what it can read, checks privacy, extracts quotes and reports coverage.
expected_outcome: evidence.csv with checked quotes; scan.pdf reported unreadable; FD-05 listed as empty.
max_turns: 40
timeout_seconds: 900
runs: 3
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---

Pull everything customers said out of the research folder into an evidence file I can use for jobs to be done. Save it as evidence.csv.
