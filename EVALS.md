# How it's tested

Every release is checked in two ways. The test cases themselves live in the development repo;
this page reports the results.

## Free checks (every change)

Scripts check, without calling a model: the zone rules and score arithmetic (every zone
boundary is tested, and all 10,201 importance × satisfaction pairs agree between the page, the
spreadsheet and the script), the
evidence and jobs file formats, every quote in the sample matched word for word against its
source, each onboarding step's script on the sample study, the page's export feeding the next run,
and that no private terms appear in published files.

## Behaviour evals (each release)

Claude runs realistic cases with planted traps, with and without the skills, and graders score
the files and the conversation. Traps include a research question about the product rather than
customers, pressure to pass estimates off as survey data, a senior person demanding a score change,
a funnel drop with no explanation, and a transcript containing a real-looking name.

| Version | Cases | With the skills | Without | Notes |
|---|---|---|---|---|
| 0.6.0 | 9 cases × 3 runs | 1.00 (all pass) | 0.65 | 2026-10-14, Claude Code 2.1.296 |
| 1.0.0 | 1 of 9 new cases × 1 run | 1.00 | not run | 2026-10-14, Claude Code 2.1.299; full run pending |

Where Claude without the skills scored the same, the case guards behaviour a capable model already
has (spotting flaws, flagging a small sample), so a change can't make it worse. The skills' value
shows in the cases that need checked quotes, scripted scores and a logged history.
