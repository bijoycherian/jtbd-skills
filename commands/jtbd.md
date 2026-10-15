---
description: Understand your customers deeply. Turn research, quotes, jobs or survey results into ranked jobs to be done, each linked to the quotes behind it
argument-hint: [files, folder or request]
---
Run the JTBD workflow on: $ARGUMENTS

If nothing is listed above, use the files and request already in this conversation. If there is
nothing to work from, say: "Attach your research (interviews, notes, tickets, funnel notes), or
quotes, jobs or survey results if you already have them. Then I'll ask two quick questions.
Tip: anonymise your research first (e.g. User 1, Company A). I'll check too, and pause on any
personal details I find."

First, say what you detected and where you'll start, in one line, then follow that skill's Process:

| Attached | Start with | Say |
|---|---|---|
| Transcripts, notes, tickets, funnel notes | `jtbd-interview-analyzer`, then `jtbd-extractor`, then `jtbd-opportunity-landscape` | the Analyzer's list of what it can read |
| `evidence.csv` | `jtbd-extractor`, then `jtbd-opportunity-landscape` | "You've given me quotes, so I'll start by proposing the framing. Say 'start from research' to run everything." |
| `jobs.csv` (or pasted jobs) | `jtbd-opportunity-landscape` | "You've given me jobs, so I'll score them. These will be marked unverified unless you attach the evidence." |
| A completed survey export with `jobs.csv` | `jtbd-opportunity-landscape`, step 9 | "You've given me survey results and your jobs file, so I'll build the map from measured scores." |
| `jobs.csv` and new research | All three; the Extractor starts from the existing jobs | "You've given me last study's jobs and new research, so this study starts from those jobs." |

Rules that hold across the workflow:
- Ask the two questions (what to learn about customers; the decision it informs) before reading,
  and run the framing check on every run, including "just run it".
- Check in twice: the framing (main goal, who, when), then the job list. "Just run it" skips
  the check-ins, never the checks.
- Hand over files between steps (`evidence.csv`, then `jobs.csv`); never rely on memory.
- Never present AI-estimated scores as survey data. Every score shows its source.
- The user never needs to know which skill is running.
