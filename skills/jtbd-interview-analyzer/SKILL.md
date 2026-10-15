---
name: jtbd-interview-analyzer
description: Turns a whole study's raw research into verified, quotable evidence for jobs-to-be-done work. Reads interview transcripts, support tickets and funnel data one source at a time, checks them for personal data, and writes evidence.csv with every quote checked word for word against its source, plus a coverage report. Use when a study's research needs mining for what customers said, including when it is pasted inline, when quotes need checking against their sources, or when a study needs a privacy check or a size plan before analysis. Usually runs first in the /jtbd workflow.
license: MIT
user-invocable: false
---

# JTBD Interview Analyzer

## Overview

Turns research into evidence the rest of the workflow can trust: short verbatim quotes, each
with its source, location, type and speaker role, checked by script. Nothing private is read
past the privacy check, and every source is either quoted or listed as having nothing relevant.
Output: `evidence.csv` (schema in `references/evidence-file.md`) and a coverage report. This
skill does not write jobs or scores; it hands `evidence.csv` to the JTBD Extractor.

## When to Use

- Interview transcripts, notes, tickets or funnel notes need turning into quotes
- Quotes need checking against their sources
- A study needs a privacy check or a size plan before anyone analyses it
- The first step of `/jtbd` when the user attaches raw research

**Not for:** writing job statements (JTBD Extractor), scoring or charting jobs (Opportunity
Landscape), or summarising a single call.

## Process

### 1. List what you can read (card 1)
Run `python scripts/size_plan.py <research folder or files>`. Show its first lines as they are:
what it can read, and anything it can't, such as a PDF without a text layer. Then say: "I'll check
each source for personal data before reading it." Recordings: ask
for the transcript the meeting tool produced; never guess content from a file name.

Give every source a stable ID if it doesn't have one: `INT-01` interviews, `FD-01` staff
interviews, `SUP-118` tickets, `FUN-01` funnel or analytics notes, `DOC-01` internal
documents. Internal documents add context but never count as customer evidence alone.

### 2. Check for private details before reading further (card 3a)
Run `python scripts/jtbd_files.py privacy <research> [--denylist private/denylist.txt]`.
If it reports anything, stop and say which file and line, without repeating the name:

> "I've paused before reading further. Interview 6, line 14 contains what looks like a real name. Replace it with a pseudonym such as Guest 6 and re-attach the file. I'll continue from there."

When the fixed file arrives, re-run the check, then: "Thanks, Interview 6 is clear. Carrying on."
If the material looks like it shouldn't be in this AI tool at all (health, financial or
children's data, or a company that only allows approved tools), say so and stop until the
user confirms. Never put a real name in quotes, notes, file names or messages.

The script catches full names, speaker labels and introductions, but not a first name in the
middle of a sentence ("Thanks George", "my manager George"). While reading, treat a person's
name anywhere in a source the same way: pause, name the file and line, never repeat the name.

### 3. Size the study (card 3b)
`size_plan.py` also prints the plan. Up to the one-pass limit, read everything in one go.
Above it, say so before starting, using the script's wording, and wait for "start" or a
smaller set of sources:

> "This study is about 300k words across 63 sources, so I'll read it in batches and show progress as each one finishes; it will take longer than a small study. Studies this large haven't been fully tested yet, so splitting it into two will give more reliable results. Shall I start? You can also remove some sources first."

The limits live in `scripts/limits.json`. Don't quote different numbers.

### 4. Read every source and pull quotes (card 3)
Start with: "Reading your 24 sources in 2 batches. You'll see progress here as each one finishes. No private details found." (use the real counts). Then, **one source at a time**:
1. Read the whole source. Don't search it for keywords: real interviews don't announce their needs.
2. Pull every goal, friction, workaround, trigger, desired outcome, metric, feature request and
   alternative (what people use instead today), whatever the research question was.
3. Write one row per quote to `evidence.csv`: verbatim, 25 words or fewer, with `location`
   (line or timestamp) and `speaker_role` as stated in the source.
4. Post one progress line per source ("INT-06: 4 quotes").

In batches, append each batch to the same file, so nothing depends on memory.

### 5. Check every quote and report coverage
```bash
python scripts/check_quotes.py evidence.csv <research folder>
python scripts/jtbd_files.py validate evidence.csv
python scripts/coverage.py evidence.csv <research folder> --product-terms "<your product names>"
```
Fix every quote reported NOT FOUND: copy the words exactly, or drop the row. Then report:

> "Done. I pulled out 412 quotes and checked each one against its source. One interview (Front desk 5) had nothing relevant, so it won't shape the results."

If more than about a third of quotes mention your own products, say the interview guide may
have been leading.

### 6. Hand over
End with one line that works by hand in any tool: "Next: the JTBD Extractor groups these
quotes into jobs. In /jtbd that happens now; on its own, attach `evidence.csv` and ask for the jobs."

## Common Rationalizations

| Excuse | Reply |
|---|---|
| "The quote is close enough." | A paraphrase breaks traceability. `check_quotes.py` must pass on every row. |
| "This source looks irrelevant; skip it." | List it as having no relevant quotes. Never drop it silently. |
| "Search for keywords to go faster." | Read each source. Keyword search finds the obvious and misses needs people describe in their own words. |
| "The name is only in one line; I'll just not quote it." | Stop and ask for a pseudonym. The source is still being read. |
| "The study's a bit over the limit; one pass will do." | Use the plan `size_plan.py` prints. Above the limit, quality drops silently. |
| "Only quote what fits the research question." | Pull every struggle. The framing check decides the question; extraction stays complete. |

## Red Flags

- A quote with no `location`, or one `check_quotes.py` can't find
- A coverage report with no empty or skipped sources on a large study
- A real name, email or phone number anywhere in the output or in a message
- Evidence pulled by keyword search or a script instead of reading each source
- A recording treated as if it had been read
- Different size limits quoted from those in `scripts/limits.json`

## Verification

- [ ] `size_plan.py` output shown: what it can read and anything it can't
- [ ] `jtbd_files.py privacy` shows 0 findings, or the run paused until fixed
- [ ] `check_quotes.py` shows 0 not found
- [ ] `jtbd_files.py validate evidence.csv` shows 0 errors
- [ ] `coverage.py` output reported, with every source quoted or listed
- [ ] Next step given in one line
