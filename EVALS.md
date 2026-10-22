# Evals: how we test the skills

What we promise, what "good" means at each stage, the bar a release must clear, and the headline
results. The tiers follow [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/main/evals),
plus a scoring tier of our own (Tier 0), because zones must never vary between runs. Three of the behaviour cases are published in [`eval-samples/`](eval-samples/) so you can see,
and run, how they work; the other 25 of the 28 cases stay in the development repo.

## What we promise

You can count on five things. The stages below check each one.

- The files open, and the next step can read them.
- Quotes are word for word, names are never repeated, and estimates are never passed off as survey data.
- The study is about people: jobs describe needs, not features, and the right skill runs.
- You stay in control: checkpoints happen, and every edit is logged with its reason.
- An opportunity map that informs your roadmap.

## Four tiers

| Tier | What it checks | Bar | Cost |
|---|---|---|---|
| 0 Scoring and contracts | Zone rules and score arithmetic, file formats, the handoffs between skills, the privacy check (full list under Free checks) | All pass, on every change | Free |
| 1 Structure | Each skill's frontmatter, name, description and required sections; under 500 lines; every referenced file exists; shared files identical in every skill | All pass, on every change | Free |
| 2 Routing | Which skill a prompt picks, approximated by word overlap (not Claude's real choice) | 14 of 15 should-pick prompts pick their skill; every should-pick-another prompt goes to its owner; no two descriptions 75% alike | Free |
| 3 Behaviour | Real runs with `claude plugin eval`, with and without the skills, graded on the files and the full trace, including pressure cases (time, authority, sunk cost) | The release bar below | Tokens |

The rest of this page is Tier 3, except Free checks, which lists Tier 0 in full.

## How a run is judged

Each grader is one pass/fail check: the work Claude produced, compared with a written standard,
by a script or an LLM judge, giving a verdict.

- A run's score is the share of its graders that passed; a case's score is the mean over its runs.
- An LLM judge is sampled 3 times on each grader, and the majority decides.
- Each case runs with the skills and without them (plain Claude), so every result shows what the
  skills add.
- Results are grouped as a funnel: a run counts at the first stage where it breaks.

## Stages: what good looks like

The stages follow Bryan Bischof's capability funnel.

| Stage | Good looks like | Failure looks like | Example cases |
|---|---|---|---|
| **1 Valid output**<br>Do the files open, and can the next step read them? | Files parse, the page and spreadsheet open, zones match the script, the run stays within its turn budget | A broken CSV, a zone that differs from the script, a run that hits the turn cap | every case |
| **2 Safe**<br>Could a team see this without a made-up quote, a leaked name, or a guess shown as data? | Every quote matches its source; no personal name in the reply or any file; every score labelled with its source | One invented quote, a name echoed back, an estimate shown as survey data | `analyzer-larkstay-research`, `analyzer-privacy-pause`, `landscape-pressure-fake-survey` |
| **3 Relevant**<br>Is it about customers' struggles, not our product? | A product-first question gets a warning and a people-first one doesn't; jobs describe needs, not features; the plugin stays quiet on unrelated work | A false alarm, "dashboard" in a job, the plugin firing on a call summary | `extractor-framing-check`, `extractor-framing-quiet`, `landscape-stays-quiet` |
| **4 Intent match**<br>Did it do what the user asked, the way they asked? | Checkpoints happen; "just run it" skips check-ins but never the framing check; every edit is logged with its reason | A silent edit, a skipped checkpoint, a lost reason | `extractor-pressure-just-run-it`, `extractor-checkpoint-2`, `landscape-edit-with-reason` |
| **5 Solves the job**<br>Did the team make a better call? | The team records a decision from the map, with its quotes; survey answers replace AI estimates | A decision with no quotes, an estimate treated as fact, survey answers ignored | `landscape-record-decision`, `landscape-survey-ratings` |

## Release bar

- **Safe:** every grader in every Safe case passes in all 3 runs, scored even when an earlier stage broke. Any miss blocks the release.
- **Valid output:** file checks pass in every run (1.0).
- **Relevant, Intent match:** each case scores 0.8 or more over 3 runs.
- **Value:** with the skills scores at least 0.25 higher than without, on average across all behaviour cases. Skill-fired checks are reported, not scored. Not yet measured on 1.0.x; the 1.0.2 run will report it.
- **Solves the job:** the decision and survey cases score 0.8 or more over 3 runs. Whether teams decide better can’t be checked by an eval.

Models are pinned for every reported run, and the Claude Code version is recorded. Failures caused
by the environment (a usage limit, a sandbox refusing a file write) are reported separately from
failures of the skills.

## Results

| Version | Date | Claude Code | Cases × runs | With the skills | Without | Notes |
|---|---|---|---|---|---|---|
| 1.0.0 | 2026-10-14 | 2.1.299 | 1 of 24 × 1 | 1.00 | not run | Setup check only (the suite had 24 cases then). 1.0.2 is in development; its full run will be the next row |
| 0.6.0 | 2026-10-14 | 2.1.296 | 9 × 3 | 1.00 | 0.65 | 9 Opportunity Landscape cases only |

Where Claude without the skills scored the same, the case guards behaviour a capable model already
has (spotting flaws, flagging a small sample), so a change can't make it worse. The skills' value
shows in the cases that need checked quotes, scripted scores and a logged history.

## What evals can't check

| What | Why evals can't check it | How we check it |
|---|---|---|
| Question cards (from 1.0.2) | Eval runs don't offer the card tool, so they only see the numbered text fallback | By hand, in the Claude app and Claude Code |
| `/jtbd` with a website (from 1.0.2) | Eval runs have no web access | Hand runs on several websites in both apps before each release, each compared with a recorded reference run: card order, framing check, "Evidence is in", time to the map. Recorded in each release's notes |

## Sample cases

[`eval-samples/`](eval-samples/) holds three cases, each with its prompt and graders. They use the
fictional Larkstay study in [`examples/larkstay/`](examples/larkstay/).

| Case | Stage | What it checks |
|---|---|---|
| `analyzer-larkstay-research` | Valid output, Safe | The privacy check runs first, every quote is checked by script, an unreadable PDF is reported, an interview with nothing relevant is listed |
| `extractor-framing-check` | Relevant | A question about the product is flagged, the product question isn't lost, and three choices are offered (yes recommended, own wording, keep mine) |
| `landscape-stays-quiet` | Relevant | A plain call summary: the plugin doesn't fire, with or without the skills |

Graders come in three kinds used here: `tool_used` (a tool was or wasn't called, optionally matching its
input), `file_exists`, and `llm` (a judge with written PASS and FAIL lines). Each judge grader checks one thing. One of the framing case's three:

```markdown
---
type: llm
---

PASS if it offers 3 choices: the suggested question (marked recommended), the user's own wording, and keep the original.
FAIL if it offers fewer, or refuses to continue.
```

To run them (this spends tokens):

```bash
claude plugin eval . --eval-dir eval-samples --trust-plugin --scaffold --allow-tools Bash Write Edit
```

`--scaffold` runs each case's `scaffold.sh`, which writes the Larkstay files into the case's
empty workspace.

## Example: one run, judged

Illustrative; not part of a release result. The framing case from `eval-samples/`, run on 2026-10-21 with a 1.0.2 development build, Claude Code 2.1.306, `claude-sonnet-5-5` and the default judge.

**Prompt:** "Here's our evidence file (evidence.csv). Research question: which guest revenue product should we fund in Q1 2027? Turn it into jobs."

**With the skills.** Graders `product-first-flagged`, `decision-kept`, `three-choices`: all PASS (3 of 3 judge votes each).

> Before I start, there's a problem with the research question. "Which guest revenue product should we fund in Q1 2027?" is about your products, so it may steer the study toward what you already sell. [...] Your product question isn't lost: it becomes the decision, and I'll answer it at the end.
>
> I suggest running the study on a question about guests instead: "Where do guests struggle to make their stay fit around their travel plans?"
>
> Reply with one of: **yes** (recommended) · **your own wording** · **keep mine** (the read-out will note that the framing centres on current products).

**Without the skills.** Same graders: all FAIL (3 of 3 judge votes each).

> I read the 22 evidence rows and wrote five jobs to `jobs.md`, each citing its evidence IDs. My recommendation is to fund the early check-in / late checkout product in Q1 2027.

Plain Claude answered the product question as asked, which is the steer the framing check exists to stop.

The judge model matters: when these three checks were one bundled grader, a stricter judge model failed the reply with the skills too. Splitting it into one check per grader fixed that, and every reported run still names its judge.

## Free checks (Tier 0, every change)

Scripts check, without calling a model:

- Zone rules and score arithmetic: every zone boundary is tested, and all 10,201 importance × satisfaction pairs agree between the page, the spreadsheet and the script
- The evidence and jobs file formats
- Every quote in the sample, matched word for word against its source
- Each onboarding step's script, on the sample study
- The page's export feeding the next run
- The decision record: linked to its quotes, and flagged when a later score change moves a job it rests on
- The contradiction rule: a warning until a conflict between sources is settled
- The privacy check: full names, speaker labels and introductions such as "I'm George"
- The starter kit
- Published files: a release script scans every one against a deny list of private terms

## Not measured yet

Study-size limits (generated transcripts don't test reading capacity), stability across runs,
how AI estimates compare with real survey results, and whether teams make a better call.
