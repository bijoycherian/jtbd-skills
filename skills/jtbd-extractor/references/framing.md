# Framing: the check, the two questions and the checkpoints

## The two inputs

| Input | About | Used for |
|---|---|---|
| **Research question** | People: "Where do guests struggle to make their stay fit around their travel plans?" | Extraction, jobs and scoring |
| **Decision** (optional) | The business: "Where should Guest Revenue focus in 2027?" | Only the read-out's "Implications for your decision" |

## The framing check (card 2a)

Four checks on the research question, and on the interview guide when there is one. It runs on
every run, including "just run it", warns and suggests, and never blocks.

| Check | Fails if | Example | What it suggests |
|---|---|---|---|
| About people, not product | The question names your products | "Which guest revenue product should we fund?" | "Where do guests struggle to make their stay fit around their travel plans?" |
| Not a business objective | The question is a metric or target | "How do we raise revenue per guest?" | Keep it as the decision; ask a question about people |
| Audience is clear | You can't say who was studied | "Our guests" | "Guests who stayed 1–3 nights in the last 6 months" |
| Not leading | The guide asks about your offers before the person's own story | Opens with "What do you think of our upgrade?" | Warn; the coverage report's product-mention share shows the effect |

When a check fails, the question becomes the decision, and the user sees three options:

> "Your question is about our products, so it may steer the study towards what we already sell. I suggest running it on a question about guests instead: 'Where do guests struggle to make their stay fit around their travel plans?' Your product question isn't lost: I'll answer it at the end.
>
> Reply with one of:
> • yes (recommended): use the suggested question
> • your own wording: I'll use that instead
> • keep mine: use your original question (the results will note that they focus on your products)"

| Reply | What happens |
|---|---|
| **yes** | The suggested question drives the study; the product question is the decision |
| Own wording | That wording drives the study; check it again |
| **keep mine** | The original question drives the study. Say: "OK, running on your question. The read-out, page and run report will note that the framing centres on current products, so the evidence may be skewed." Record `framing_note` for the read-out |

The check may also say JTBD is the wrong method, for example for a usability question about one
screen. Say so, and offer to continue anyway.

Checks 1 and 2 adapt Sunita Mohanty's guidelines that jobs describe human needs rather than
features, and struggles rather than business objectives; check 3 her step of defining the
audience; check 4 her advice to avoid leading questions.

## Checkpoint 1: the framing (card 4)

Propose three things, each with how many quotes back it. Users see plain labels; the jobs
file stores them as the core job, `persona` and `stage`.

> "Here's how I'd frame the study.
> Main goal: Make my stay fit around my travel plans (412 quotes).
> Who: business travellers (198), leisure guests (151), families (31; few quotes, so treat with care).
> When: booking, before arrival, arrival, the stay, departure.
> Reply 'ok', or tell me what to change, for example: 'split business travellers by trip length'."

- **Main goal:** the core job, in the customer's words, solution-free.
- **Who:** 1–4 personas from speaker roles and stories. Staff (front desk, support) are evidence
  about customers, not a persona. Flag any persona with few quotes.
- **When:** 3–8 stages in the order the job happens, named in the study's own terms.

Write nothing further until the user replies. Any reply that confirms or corrects counts.

## Checkpoint 2: the job list (card 5)

Show draft jobs labelled `D1`, `D2`… grouped by stage, one line each (the "help me" part, in
plain words), then:

> "11 draft jobs (D1 to D11), by stage. … Reply 'ok', or for example 'merge D4 and D5', 'drop D9'."

Apply merges, splits, renames and drops to the drafts, re-run the lint and link checks, then
renumber with `jtbd_files.py renumber` and confirm:

> "Done: 9 jobs, numbered 1 to 9 on your map. D4 and D5 are now one ('Find a room that fits this stay'), and D9 is gone. Scoring now."

Draft labels are never reused as final numbers, so "drop D9" can't be confused with job 9.

## "Just run it"

Skips checkpoints 1 and 2, never the checks. The framing check still runs. The read-out states
the framing that was used.
