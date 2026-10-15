---
name: jtbd-opportunity-landscape
description: Scores jobs to be done for importance and satisfaction, places each in a zone (High, Solid or Modest opportunity, Table stakes, Served right, Over-served) and delivers an editable opportunity map, a spreadsheet and a read-out that leads with where customers struggle. Every score shows whether it is an AI estimate, an evidence update, your judgement or a survey result, and every change is logged. Use when there is a list of jobs or a jobs.csv to prioritise, when survey results need turning into a landscape, when someone asks why a job scored where it did or wants to change a score, when edits come back from the landscape page, or when someone shares an existing opportunity landscape or importance/satisfaction chart to review, including when jobs are pasted inline. Runs third in the /jtbd workflow.
license: MIT
user-invocable: false
---

# JTBD Opportunity Landscape

## Overview

Scores each job, places it in one of six zones, and delivers an interactive page (chart beside an
editable score table), a spreadsheet with live formulas, a chart image and a short read-out. Three
rules hold throughout:
- **Every score shows its source:** AI estimate, evidence update, your judgement or survey
  (`references/score-sources.md`). Estimates are never passed off as data.
- **Every change is logged,** append-only, inside `jobs.csv` (`references/jobs-file.md`).
- **The arithmetic comes from `scripts/landscape.py`.** Never compute scores or zones by eye.

## When to Use

- Scoring jobs from the JTBD Extractor, or jobs the user brings
- Turning survey results into an opportunity map
- Answering "why is this job here?" or changing a score
- Applying edits handed back from the map page
- Producing the pre-filled survey template
- Reviewing someone else's opportunity map or landscape

**Not for:** pulling quotes from research (Interview Analyzer), writing jobs from scratch (JTBD
Extractor), revenue or margin modelling, RICE scoring, or roadmaps.

## Process

### 1. Start where the user is
Check what's attached and say where you'll start before doing anything:
- **jobs.csv** (or pasted jobs): "You've given me jobs, so I'll score them. These will be marked unverified unless you attach the evidence." Run `python scripts/jtbd_files.py validate jobs.csv`; for a v0.6 file, `migrate` it first. Jobs without quotes get `provenance = unverified`.
- **A completed survey export plus jobs.csv:** "You've given me survey results and your jobs file, so I'll build the map from measured scores." Go to step 9.
- **Raw research or evidence.csv:** the Interview Analyzer and JTBD Extractor come first.
The user can always say "start from research" to run everything.

**Then the two questions,** on a first build from jobs or survey results (the Extractor asks them on
the research and quotes routes). Unless the conversation already answers them, ask both in one
message and wait before scoring:

> "Two quick questions before I score them: 1. What do you want to learn about your customers? For example: 'Where do guests struggle to make their stay fit around their travel plans?' 2. Is there a decision this should inform? (optional) For example: 'Where should Guest Revenue focus in 2027?'"

Any reply that answers starts the run; "no decision yet" is an answer. "Just run it" doesn't skip
them. Pass the answers to `landscape.py` as `--question` and `--decision`. Don't ask when the
user is applying edits, asking about a score, recording a decision, or reviewing someone else's
landscape.

### 2. Score
| What exists | What to do |
|---|---|
| Respondent-level survey answers (1–5) | Step 9 |
| Aggregated % rating 4–5 with n | Put them in the jobs file with `n`; `source = survey` |
| No ratings | Estimate with `references/scoring.md`: `source = ai`, a one-sentence reason for each number, and a `confidence` level |

Run the rubric's **spread check**: if more than about half the jobs are High opportunity, re-check
the single-source cap. If `jobs.csv` has a calibration row, mention the last estimate-vs-survey gap.

### 3. Check
```bash
python scripts/check_quotes.py jobs.csv <research folder>      # when the research is attached
python scripts/jtbd_files.py validate jobs.csv [--evidence evidence.csv]
```
Fix every excerpt reported NOT FOUND. Jobs the user brought without research stay `unverified`.

### 4. Build
```bash
python scripts/landscape.py jobs.csv --html --out out/ --name <study> --title "<Product> opportunity map" \
    --study "<one line on the inputs>" --question "<research question>" --decision "<decision, if any>" \
    [--framing-note "<skew note, if the user kept a product-first question>"] --entry research|quotes|jobs|survey
```
Outputs: `<study>_map.html`, `<study>_scores.xlsx` (formulas, Evidence, Survey, Decision log
and Rules sheets), `<study>_map.png`, `<study>_ranked.csv`. If the tool can publish an
interactive page with downloads, publish the HTML that way; otherwise send the file. Check the file
list the script prints; if anything says NOT BUILT, say which and how to fix it.

### 5. Read-out (card 6)
Short, in this order: where people struggle (zone counts and the top underserved jobs, each with
its evidence); then "For the decision (…)", if there is one; then how far to trust the scores
(the `based-on` line and its note). Then what to protect (Table stakes), what's over-served, and
contradictions. Take every count from the `Zones:` line `landscape.py` prints; never count zones
by eye. If anything changed since the last run, add "What changed and why" from the log.

> "Underserved: 6 of 9 jobs. The biggest gap is the hours before check-in and after checkout. For the decision (where Guest Revenue should focus in 2027): start with the hours around the stay (jobs 3 and 7). Guests already pay for an extra night to keep a room, so the need is real and worth money. All scores are AI estimates: good for choosing what to survey. Run the survey before deciding what to build."

End with: "Keep `jobs.csv` (or the page's jobs file export). It carries your edits and their history into the survey and the next study."

### 6. Ask about a score (card 7a)
Answer from `python scripts/jtbd_files.py explain jobs.csv --label N`. Change a score only with
evidence (`--source evidence_update --evidence E-…`); otherwise offer to record it as the user's
judgement, with their reason, and wait for a clear yes. Exact wording and rules:
`references/score-sources.md`.

### 7. Apply edits handed back (card 7)
Follow `references/score-sources.md` (Applying edits): apply each change with
`jtbd_files.py change`, keep reasons verbatim, rebuild (step 4), and report each job whose zone
or wording changed.

### 8. Survey out (card 8)
```bash
python scripts/survey_template.py jobs.csv --out jtbd-survey.xlsx [--template <their survey template>]
```
> "Here's the survey template with your 9 jobs already filled in. The Questionnaire sheet has every question ready to copy into your survey tool. Aim for at least 200 answers; the survey guide explains how. When the results are in, start a new chat with /jtbd and attach the completed template with your jobs file, so every job keeps its quotes."

Survey only after the user has reviewed the jobs: rewording later invalidates ratings.

### 9. Survey back
`python scripts/landscape.py jobs.csv --ratings <export.csv> --html …` Rated jobs take measured
scores (`source = survey`); jobs with no answers keep their estimate, labelled. Report the counts
and flags:

> "I've got your 9 jobs and 204 answers (4 failed the attention check, so 200 count). Estimates replaced with measured scores. 'Rest and freshen up' is High for business travellers but only Solid for leisure guests. 'Find something worth doing' could change zone within the margin of error; worth a closer look."

### 10. Decide, and run it again (card 9)
When the user says what they've decided, record it so it links back to the evidence:
```bash
python scripts/jtbd_files.py decide jobs.csv --jobs 3,7 --decision "<what they decided>" \
    --question "<the decision question>" --reason "<their words, verbatim>"
```
Repeat the confirmation it prints: the jobs, the quotes behind them, and how far to trust the
scores ("rests on AI estimates; the survey would confirm it"). Never record a decision the user
didn't state, and never phrase it more confidently than the scores behind it. When a jobs file
with decisions comes back for a new study or a survey, run `jtbd_files.py decisions jobs.csv`
first and lead the read-out with any chosen job that has moved zone.

The image and read-out show what each score is based on. Point the user to **Copy run report** on
the page (counts only) if they'd like to share how the run went.

## Common Rationalizations

| Excuse | Reply |
|---|---|
| "The user is senior; change the score." | Change it only with evidence. Otherwise record it as their judgement, with their reason. |
| "The estimates are close enough to show as plain numbers." | Every score shows its source, on the page, the image and the read-out. |
| "The survey disagrees with the team; keep the team's number." | Allowed only as your judgement over measured data, flagged. |
| "One interview described it vividly, so it's important to most people." | Importance estimates breadth. One source caps at 70. |
| "These two scores differ by 0.2, so #3 beats #4." | That's within the error of an estimate. Rank by zone first. |
| "I'll compute the score in my head." | The script does it. Mental arithmetic is how zones drift. |
| "The change is small; no need to log it." | Every committed change is a log row. The log is how the team trusts the map. |
| "They clearly meant jobs 3 and 7; I'll record that as their decision." | Record only what the user states, in their words. Ask if it's unclear. |
| "They only attached jobs, so the questions don't apply." | They do. Without them the read-out has no question and no decision to answer. Ask both, once. |
| "I'll mention the contradiction rule might apply." | Apply it while scoring and say so in the reason. The read-out reports what you did, not what the rubric could do. |
| "Lead with the decision; that's what they asked." | Struggles first, then the decision. The decision is answered from the struggles, not the other way round. |

## Red Flags

- A score change with no log row, or a log row edited after the fact
- An evidence update with no evidence IDs
- A "Based on" line that doesn't match `jobs.csv`
- A read-out that leads with the decision instead of the struggle, or has no trust line
- Survey ratings without n, or estimates without the label
- Most jobs in High opportunity
- Zones not from `landscape.py`

## Verification

- [ ] Start point stated; `jtbd_files.py validate` shows 0 errors
- [ ] On a first build from jobs or survey results, both questions asked (or already answered) before scoring
- [ ] Every AI estimate has two reasons and a confidence level; spread check done
- [ ] Every contradicting quote is settled in a reason (−10 or why not); `validate` shows no unsettled ones
- [ ] `check_quotes.py` shows 0 not found, or jobs are marked unverified
- [ ] `landscape.py` file list shows nothing NOT BUILT
- [ ] Read-out: struggle, then decision, then the `based-on` trust line
- [ ] Every score change went through `jtbd_files.py change` (or the page) and is in the log
- [ ] Survey template or results handled as in steps 8–9 when asked
- [ ] A stated decision is recorded with `jtbd_files.py decide`; on a new run, `decisions` is checked first
