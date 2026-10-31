---
description: Understand your customers deeply. Turn research, quotes, jobs or survey results into ranked jobs to be done, each linked to the quotes behind it
argument-hint: [files, folder, website or request]
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
| A website and no research | The URL route below, then all three skills | "You've given me a website and no research, so I'll look at what its customers say publicly." |

Rules that hold across the workflow:
- Ask the two questions (what to learn about customers; the decision it informs) before reading
  (on the URL route, the opening card set instead), and run the framing check on every run,
  including "just run it" and runs from jobs or survey files, before any gathering or scoring.
- Check in twice: the framing (main goal, who, when), then the job list. "Just run it" skips
  the check-ins, never the checks.
- Hand over files between steps (`evidence.csv`, then `jobs.csv`); never rely on memory.
- Never present AI-estimated scores as survey data. Every score shows its source.
- The user never needs to know which skill is running. Talk about their study, not the machinery:
  no tool names, folder listings, retries or internal checks, unless one changes what they get.
- Run each skill's scripts from that skill's own folder (where its SKILL.md is). Never guess a path
  or list folders to find one; if a file is missing, say which.
- Check the Landscape's chart libraries (its `requirements.txt`) once at the start and install what's
  missing then, not mid-run.

## The URL route

Only when the user gives a website and no research. Every other route above is unchanged.

1. **Look.** Read the homepage or about page, nothing else: what the product is and who its
   customers are. No reviews, forums or searches yet. If the site can't be read, say so in one
   line and go straight on to the opening questions, drafting the options from the name and the
   user's own words (a marketplace has at least two groups of customers). Never stop here.
2. **Opening questions, as one card set, before gathering anything.**
   - "[Name]'s homepage tells me what [name] offers, not what customers are trying to get done.
     What should I work from?" Public customer voice (recommended: I gather real quotes from
     public reviews, forums and press, check each against its saved source, then build the
     landscape from those) · I'll attach research (interviews, notes, tickets or survey results)
     · Draft jobs only (AI-drafted jobs scored as unverified estimates, with no quotes behind
     them).
   - Only when the site serves more than one group of customers: "Which customers do you want
     to learn about?" One option per group ("Guests: people booking stays"), plus "Both,
     separately: two landscapes, one per side".
   - "What decision will this landscape inform?" Product roadmap priorities · Competitive
     positioning · New market or offering · Learning / case study, each with a one-line
     description. Never mark one recommended.
   - Only when the user typed a question about the product, not just the website ("which
     features should Airbnb build?"): run the framing check (Extractor `references/framing.md`)
     on it, and ask the framing card from that file straight after this set, once you know
     which customers (its suggested question is about them). A bare website gets no framing
     card: the source and customer cards already make the study about people.
   After the cards, the research question is fixed before any search: the one chosen on the
   framing card, or for a bare website "Where do [chosen customers] struggle to [what the
   homepage says they come to do]?" Say it in one line as gathering starts.
3. **Homework.** Keep a progress list of five steps: gather public customer voice, extract and
   check quotes, draft jobs, score jobs and build the landscape, check the work. Search for what
   the chosen customers struggle with, in their words (problems, complaints, workarounds,
   switching), across review sites, forums and press, not for the product's features; stop at
   about 20 sources and skip any site you can't read, saying so. Save each page you quote from
   as `sources/REV-01.md`, `REV-02.md`…: its URL on the first line, then only the reviews you quote, copied exactly,
   with reviewer names replaced by "Reviewer 1", "Reviewer 2". The company's own pages and
   third-party reports or statistics are `DOC-` sources, never customer evidence alone. Then run
   the Interview Analyzer from its privacy check on `sources/`, so every quote is checked against
   the page it was saved from.
4. **"Evidence is in."** One paragraph, sent as a message before any card (step 5): how many
   sources of which kinds, names removed, how many quotes matched to the page they came from (the
   fetch tool returns excerpts, so never say "word for word" for web sources), the share that
   name the product, and the skew caveat (reviews over-represent friction, so satisfaction
   estimates lean low). Take every count from `evidence.csv`, and use the same count wherever it
   appears again; if quotes are added later, say so ("77, plus 3 that point the other way"). If
   more than about a third of quotes name the product, search once more for what customers
   struggle with in their own words before going on, and say in the read-out that the evidence
   leans on talk about the product.
5. **Checkpoint 1.** The framing check already ran in step 2: the Extractor works on the research
   question fixed there and never asks the framing card again. One message with "Evidence is in"
   and the proposed framing (main goal, who, when, each with quote counts), then the card:
   - "Is the main goal / who / when framing right?" OK as proposed (restating exactly what OK
     commits to: the groups and stages as listed in the message) · one specific edit, aimed at
     the weakest part of the evidence (a thin group or stage) with its quote count and what it
     changes ("Merge families in: 13 quotes; one group, all guests") · Just run it (skip the
     job-list check-in too; I'll still run every check).
6. **Checkpoint 2.** The draft jobs by stage in the message above, each with its quote count and
   any "thin" or "hypothesis" flag. Card: "How should I treat the job list?" OK, score all [n]
   (number them 1 to [n] and build the landscape) · up to two specific edits with a reason
   ("Drop thin jobs: D6 and D15, 2–3 quotes each").
7. **Then the Landscape as usual:** the map opens beside the chat, and the read-out leads with
   where customers struggle, then the decision, then how far to trust the scores.

**Card rules on this route.** These replace the quoted wording in the skills for this route only;
keep what each question asks and what each answer does.
- When the user has to decide, ask with your question card if one is available. Never ask a card
  about content the user can't see yet: send that content first. Short labels;
  the second line says what the option does. Long content goes in the message above the card.
- Each card's question is fixed, as written above; keep it short. The options are drafted from
  the research each run, and the details go in the message. Never write "see the message above",
  and never shorten a question the user is asked to agree to.
- Options are about people, never your product's features; decision options never name a
  solution.
- Mark an option recommended only with a stated reason, and never on the decision card.
- No card available: ask the same questions in text with the options numbered, and end with
  "Reply with numbers or in your own words."
- The user said to run without check-ins: carry on as "just run it" would, and say which
  options you used.
- "I'll attach research" picked: say "Attach with ＋ and send", wait, remind once if nothing
  arrives, then carry on from the same step with their files.
- Decision skipped: go on with "No decision given" and say so. When the read-out is ready, end
  with the same decision card, each option's second line written from the finished map; a pick
  adds the section on what the findings mean for that decision.
- Any other card skipped: ask it once more; skipped again, go on with the best reading (the
  recommended option, if there is one) and say which you used.
