# Score sources, asking about a score, and the decision log

## Four sources, and how far to trust each

| Source | How it got there | How far to trust it | Marker | Tag |
|---|---|---|---|---|
| AI estimate (`ai`) | Inferred from what people said (`scoring.md`) | Directional | Dashed ring | "AI est." |
| Evidence update (`evidence_update`) | You and Claude agreed, and Claude could point to quotes | Directional, better supported | Dashed ring | "Updated from evidence" |
| Your judgement (`judgement`) | You and Claude discussed it; no quotes back it | Your team's hypothesis | Square | "Your judgement" with the reason |
| Survey (`survey`) | Measured top-2-box | Measured, with a margin of error | Plain circle | "Survey", n, and "zone could change" when it applies |

**Based on.** The page banner, the image and the read-out summarise the mix:
`jtbd_files.py based-on jobs.csv` prints "Based on: 6 AI estimates · 2 team judgements · 1 evidence update". Read-outs and images get forwarded, so they say "team judgement(s)"; only the page, which its author reads, says "your judgement".

**How far to trust it** (`jtbd_files.py based-on` prints this line too):
- Mostly estimates: "Scores include AI estimates: good for choosing what to survey. Run the survey before deciding what to build."
- Any judgement: "2 scores reflect the team's view rather than customer evidence. Survey before deciding what to build."
- All survey: only the margins of error and any "zone could change" flags.

**Your judgement over measured data.** Allowed, because the team may know something the survey
missed, but the page, the spreadsheet and the decision log flag it, because it's the change most
likely to hide a bias.

## Asking about a score (card 7a)

The user asks why a score is where it is. Run `jtbd_files.py explain jobs.csv --label N` and answer
from it: the quotes behind it (with IDs), how many sources raised it, quotes that point the other
way, and what evidence would change it.

> "11 of 14 business travellers raised it without being asked, and the front desk sees it every morning (E-012, E-066, E-088). No one said it didn't matter. It would drop if leisure guests rarely arrive early; only 2 of them mention it."

If the user disagrees:
1. **Look for evidence** in `evidence.csv` (and the research, if attached). If quotes support the
   change, make it an evidence update and name them:
   `jtbd_files.py change jobs.csv --label N --importance X --source evidence_update --evidence E-… --reason "…"`
2. **No evidence:** say so, and offer to record it as their judgement, with their reason:
   > "None of the interviews say that, so I can't raise it from the evidence. I can record it as your judgement, with your reason ('weekend flights arrive early'). It'll show as your judgement on the page, not as evidence. Do that?"
3. Only on a clear yes: `change … --source judgement --reason "<their words>"`.
4. Claude can say no to an evidence update, and says why. Seniority is not evidence.

## Applying edits handed back from the page (card 7)

The user attaches or pastes the page's jobs file export, or the "Copy changes for Claude" text.
- The export already carries the page's decision log rows: keep them, don't re-log them.
- Changes stated in chat: apply each with `jtbd_files.py change`, keeping the user's reason verbatim.
  If none was given, ask once; never invent one.
- Wording changes: re-run the statement checks (the Extractor's `lint_jobs.py`, or the checks in
  `scoring.md`), check the quotes still fit the new wording, and for survey scores warn that
  ratings were collected on the original wording.
- Adding, merging, splitting or dropping jobs: only on request, with new labels (never reuse a
  dropped job's number) and a log row (`field` = added, merged, split or dropped).

Then rebuild and report each job whose zone or wording changed:

> "Applied your edits to 1 job. Job 5 moved from Served right to Solid opportunity (importance 60 to 85; your reason: front desk sees this every morning). The updated page and summary are attached."

## Recording a decision (card 9)

When the user states a decision, `jtbd_files.py decide` adds a log row with `field = decision`:
the chosen jobs (`label`, e.g. `3; 7`), the question (`from`), the decision (`to`), each chosen
job's zone, score and source at the time (`zone_from`), the Based on line for those jobs
(`zone_to`), the user's reason, and the quote IDs collected from the chosen jobs. It prints:

> "Recorded the decision: focus 2027 on the hours around the stay. It rests on jobs 3, 7 and 6 quotes (E-012, E-066, E-088, E-077…). Based on: 2 AI estimates. Scores include AI estimates: good for choosing what to survey. Run the survey before deciding what to build."

On the next study or survey, `jtbd_files.py decisions` lists decisions and flags any chosen job
whose zone has moved ("Job 7, chosen on 2026-10-15, moved from High opportunity to Solid
opportunity."). Lead the read-out with that.

## The decision log

Every committed change is a log row in `jobs.csv` (`references/jobs-file.md`): when, which job,
what changed, any zone change, the source, who, the reason, evidence IDs and the version.
Append-only: a correction is a new row. It shows as History on each job on the page, a Decision
log sheet in the spreadsheet, and "What changed and why" in the read-out whenever anything moved.
Reasons pass the same privacy check as the research.
