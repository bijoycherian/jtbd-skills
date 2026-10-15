---
name: jtbd-extractor
description: Turns customer evidence into jobs to be done in When / But / Help me / So form, each linked to the quotes behind it. Checks that the research question is about people rather than your product, proposes the main goal, who and when for the user to confirm, then drafts the job list for the user to merge, split, rename or drop. Use when there are quotes or an evidence.csv and the team needs the jobs customers are trying to get done, including when quotes are pasted inline, or when job statements need checking for solution words or links back to evidence. Runs second in the /jtbd workflow.
license: MIT
user-invocable: false
---

# JTBD Extractor

## Overview

Reads `evidence.csv` and writes `jobs.csv`: one row per job, in the customer's voice, linked to
the quotes that support it and the quotes that point the other way. Two checkpoints keep the
user in charge of the framing and the job list. A framing check runs first, so a
product-first question doesn't quietly steer which needs get noticed. This skill doesn't
score; it hands `jobs.csv` to the Opportunity Landscape. Wording and examples for every
message are in `references/framing.md`; the file spec is `references/jobs-file.md`.

## When to Use

- Quotes or `evidence.csv` need turning into jobs
- A research question needs checking before analysis
- Job statements need checking for solution words, company language or broken evidence links
- The second step of `/jtbd`, or its start when the user attaches `evidence.csv`

**Not for:** reading raw transcripts (Interview Analyzer first), scoring or charting jobs
(Opportunity Landscape), solution ideas or roadmaps.

## Process

### 1. Two questions (card 2)
If the user hasn't given them, ask both in one message, each with an example:

> "Two quick questions before I start: 1. What do you want to learn about your customers? For example: 'Where do guests struggle to make their stay fit around their travel plans?' 2. Is there a decision this should inform? (optional) For example: 'Where should Guest Revenue focus in 2027?' Then I'll read everything and check back with you twice: once on the framing, once on the job list."

If the files already contain a research question, show it for confirmation instead of asking
question 1. Any reply that answers starts the run; no keyword is needed.

### 2. Framing check (card 2a)
Run the four checks in `references/framing.md` on the question and any interview guide. If one
fails, file the question as the decision and offer the three options exactly as written there:
yes (recommended), your own wording, or keep mine. Never block. On "keep mine", record the skew
note for the read-out, page header and run report.

### 3. Checkpoint 1: main goal, who, when (card 4)
From `evidence.csv`, propose the main goal, who and when, each with quote counts, plus one
example correction. Wait for the reply. Skip only on "just run it".

### 4. Group quotes into draft jobs
Group quotes by **underlying need**, not keyword or feature. Write one draft job per need:
`When [context], but [barrier], help me [goal], so [outcome]`, with exactly one `persona`, a
`stage`, `evidence_ids`, the same quotes inline in `evidence`, and any `contradicts`. Label
drafts `D1`, `D2`… A feature request is a clue to a need: write the need. Funnel data shows
where, not why: mark any cause you infer `[inference]`.

### 5. Check every statement
```bash
python scripts/lint_jobs.py drafts.csv
python scripts/check_links.py drafts.csv evidence.csv
```
Rewrite every statement that fails. Also check by judgement: the barrier is a struggle, not a
missing feature (6); one situation, not a process (7); the outcome would still be true if your
product didn't exist (8); the survey wording reads naturally (10). Record each rewrite as
`before → after (check #)`.

### 6. Checkpoint 2: the job list (card 5)
Show the drafts by stage, one line each, and wait. Apply merges, splits, renames and drops,
re-run step 5, then:
```bash
python scripts/jtbd_files.py renumber drafts.csv --out jobs.csv
python scripts/jtbd_files.py validate jobs.csv --evidence evidence.csv
```
Confirm with the counts and what changed ("Done: 9 jobs, numbered 1 to 9…").

### 7. Hand over
Jobs without quotes (the user brought them) get `provenance = unverified`. End with: "Next: the
Opportunity Landscape scores these jobs. In /jtbd that happens now; on its own, attach
`jobs.csv` and ask for the opportunity map."

## Common Rationalizations

| Excuse | Reply |
|---|---|
| "The question looks fine; skip the framing check." | It runs every time, including on "just run it". It costs one message when it passes. |
| "They said just run it, so skip the lint." | "Just run it" skips checkpoints, never checks. |
| "This feature is what they asked for; write it as a job." | Solution words fail check 1. Write the struggle behind the request. |
| "The user's product question is what they want; use it." | Offer the three options. The product question isn't lost: it becomes the decision. |
| "Renumbering is busywork; keep D-labels." | Final numbers appear on the map. Draft labels are never reused, so edits can't be confused with jobs. |
| "This quote points the other way; leave it out." | Attach it as `contradicts`. Dropping it hides a real disagreement. |
| "Front desk staff are a persona." | Staff are a speaker role. They report on customers, they aren't the customer. |

## Red Flags

- A job with no `evidence_ids`, or a link `check_links.py` reports broken
- A goal containing a product noun (app, upgrade, TV channel, integration, dashboard)
- Jobs written before checkpoint 1 was confirmed, unless the user said "just run it"
- Draft labels in the final `jobs.csv`, or a dropped job's number reused
- The framing check skipped, or the user's choice made for them
- Company language or internal acronyms in a customer statement
- Personas mixed inside one job

## Verification

- [ ] Both questions answered (or confirmed from the files); decision recorded separately
- [ ] Framing check run; any failure offered as three options, and the reply applied
- [ ] Checkpoint 1 and 2 replies in the transcript, or "just run it" recorded
- [ ] `lint_jobs.py` shows 0 issues, or each remaining one is listed with a reason
- [ ] `check_links.py` shows 0 broken
- [ ] `jtbd_files.py validate jobs.csv --evidence evidence.csv` shows 0 errors
- [ ] Next step given in one line
