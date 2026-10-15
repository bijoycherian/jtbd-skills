# jobs.csv (schema 1.0)

One file carries the jobs, their decision log and the last calibration, so the team's
history travels with the jobs into the next study. The JTBD Extractor writes it; the
Opportunity Landscape scores it, logs every change to it, and the map page exports it.
`jtbd_files.py validate jobs.csv --evidence evidence.csv` checks it.

The JTBD Extractor and the Opportunity Landscape carry identical copies of this file.

UTF-8, comma-separated, one header row, quotes around any field containing a comma. Every row
has `schema_version` (`1.0`) and `record_type`: `job`, `log` or `calibration`.

## Job rows (`record_type = job`)

| Column | Required | Values |
|---|---|---|
| `label` | yes | Final job number (`1`, `2`…), shown on the chart. Drafts use `D1`, `D2`… and are renumbered after checkpoint 2 (`jtbd_files.py renumber`). Never reuse a dropped job's number |
| `persona` | yes | Exactly one. Users see this as **Who** |
| `stage` | yes | One of the study's stages, in its own terms. Users see this as **When** |
| `context` | yes | `When …` |
| `barrier` | yes | `but …` (a struggle, not a missing feature) |
| `goal` | yes | `help me …` (a need, never a solution) |
| `outcome` | yes | `so …` |
| `importance`, `satisfaction` | yes | 0–100: % rating 4–5 (estimated or measured) |
| `source` | yes | Where the scores came from: `ai`, `evidence_update`, `judgement` or `survey` (below) |
| `n` | if survey | Respondents behind the ratings |
| `confidence` | if ai | High, Medium, Low or Hypothesis |
| `importance_reason`, `satisfaction_reason` | if ai | One sentence each, naming the evidence |
| `evidence_ids` | yes* | IDs from evidence.csv, separated by `; ` |
| `evidence` | yes* | The same quotes inline: `INT-03: I land at 7am… || FD-02: Every morning…`, so the page and spreadsheet can show them |
| `contradicts` | no | Quotes that point the other way, same format. Never drop them |
| `provenance` | yes | `verified` (quotes checked against sources) or `unverified` (the user brought jobs without quotes) |
| `edit_reason` | if changed | The latest reason, verbatim. The full history is in the log rows |
| `survey_importance`, `survey_satisfaction` | if a survey score is overridden | The measured values, kept so the page shows "your judgement over measured data" |
| `original_context` … `original_outcome` | if reworded | The wording the scores and quotes were made for. Set once, never overwritten |

\* Not needed when `provenance` is `unverified`.

### Score sources

| `source` | Means | Marker | How it gets set |
|---|---|---|---|
| `ai` | AI estimate from what people said | Circle, dashed ring | Scoring with no survey |
| `evidence_update` | Changed in conversation, and Claude could point to quotes | Circle, dashed ring | `jtbd_files.py change --source evidence_update --evidence E-…` |
| `judgement` | You and Claude discussed it; no customer evidence behind it | Square | `change --source judgement`, or an edit on the page |
| `survey` | Measured top-2-box | Circle, no ring | `landscape.py --ratings` |

v0.6 files used `edited`; it reads as `judgement` (`jtbd_files.py migrate`).

## Log rows (`record_type = log`): the decision log

One row per committed change, never per step of a drag. Append-only: a correction is a new
row; old rows are never edited or deleted. `jtbd_files.py change` writes them.

| Column | Values |
|---|---|
| `label` | The job |
| `logged_at` | ISO date-time, UTC |
| `field` | `importance`, `satisfaction`, `context`, `barrier`, `goal`, `outcome`, `persona`, `stage`, `added`, `merged`, `split`, `dropped`, `survey` or `decision` |
| `from`, `to` | Old and new value |
| `zone_from`, `zone_to` | Zone before and after |
| `source` | As above |
| `by` | `user` (a person, never a name), `claude` or `page` |
| `reason` | Verbatim. Passes the same privacy check as sources |
| `evidence_ids` | For an evidence update |
| `version` | Skill and rubric version |

### Decision rows (`field = decision`)

What the team decided, linked to its evidence. `label` lists the chosen jobs (`3; 7`), `from` the
decision question, `to` the decision, `zone_from` each chosen job's zone, score and source at the
time (`3: High opportunity · 14.9 · AI estimate | 7: …`), `zone_to` the Based on line for those
jobs, `reason` the user's words, `evidence_ids` the quotes behind the chosen jobs. `source` is
blank. Written by `jtbd_files.py decide`; `jtbd_files.py decisions` flags chosen jobs whose zone
has since moved.

## Calibration row (`record_type = calibration`)

At most one: the last estimate-vs-survey gap, applied to the next study's estimates with a
note the user can turn off. Columns: `importance_gap`, `satisfaction_gap` (survey minus
estimate, average points), `n_jobs`, `survey_n`, `applied` (`yes`/`no`).

## Survey ratings

Respondent-level ratings (`landscape.py --ratings`), 1–5 answers, in either layout:
- **Wide** (the survey template's export): `respondent_id, persona, attention_pass, J01_imp, J01_sat, …`
- **Long:** `respondent_id, persona, label, importance, satisfaction`

`J01` matches label `1`. `NA`, blank or anything outside 1–5 is missing. Dropped and reported:
failed attention check, the same answer to every question (10 or more), and (with
`duration_sec`) under a third of the median time.
