# Scoring: estimates, confidence and zones

Three parts, used at step 5 and step 7: how to estimate importance and satisfaction without a survey, how confident the evidence is, and how scores become zones.

## Estimating importance and satisfaction from qualitative research

Use only when no survey ratings exist. Estimates are a starting point for the user to
edit, never a finding. Every estimate is stored with `source = ai` and a one-line reason
that names the evidence.

Both numbers estimate **the share of this persona who would rate 4–5 on a 1–5 scale**,
so they have to reflect how *widespread* something is, not only how *intense* it is for
one person.

### Importance

| Estimate | Evidence pattern |
|---|---|
| 85–95 | ≥ 3 independent sources (people or tickets) in this persona, with cost, emotion or a costly workaround |
| 70–84 | 2 independent sources, or the core job the product exists for `[inference]` |
| 50–69 | One source with a concrete cost or consequence |
| 30–49 | Mentioned in passing, or a feature request with no story of harm |

Adjust:
- **Single-source cap: 70.** One vivid interview is still one person.
- **Contradiction in the same persona: −10.** Keep the contradicting quotes on the job. Settle
  each one while scoring: look up the speaker in `evidence.csv`, then say in the reason, naming
  the source ID, either that you took 10 off or why not (another persona, or it's about
  satisfaction). Never leave it as an "if" for the read-out; `validate` warns when it's unsettled.
- **Funnel or analytics data** can show that a step matters (where people drop), but
  not why. It may support importance; it never sets the cause.
- **Internal documents** (`DOC-`) never raise an estimate on their own.

### Satisfaction

| Estimate | Evidence pattern |
|---|---|
| 10–29 | Nothing works: abandoned feature, fully manual, "nobody looks at it" |
| 30–49 | A workaround exists but costs time or trust |
| 50–69 | Mixed: some people fine, others complain |
| 70–85 | Mostly works; minor complaints |
| 86–95 | Praised; no complaints |

No evidence about how well it works today → **50**, and say "satisfaction unknown" in
the reason.

### Spread check

After estimating, look at the zone counts. If more than about half the jobs land in
High opportunity, re-check the single-source cap and whether satisfaction is being
scored from complaints alone. Research skews toward pain because that's what people
talk about.

### What to write in the reasons

- Importance: how many sources, which persona, the cost or consequence.
- Satisfaction: what people do today and how well it works.
- Keep each reason to one sentence; the quotes carry the detail.

## Confidence rubric

Confidence describes how well the **evidence supports the opportunity existing and
mattering**. It is not a priority score and not a guess about solution success.

| Level | Criteria (all that apply to the level) |
|---|---|
| **High** | ≥ 3 independent sources **and** ≥ 2 source types (e.g. interviews + support or funnel); at least some `observed` behavior; contradictions are absent or explained by segment |
| **Medium** | 2+ independent sources, **or** 1 source type with strong observed behavior; contradictions exist but are minority or unexplained |
| **Low** | Single source, **or** mostly `stated` opinions/feature requests, **or** significant unresolved contradiction |
| **Hypothesis** | Inferred by the analyst from indirect evidence; no participant expressed it directly. Must be labeled `[inference]` |

### Adjusters

- Downgrade one level if most support comes from one segment but the opportunity is
  presented as general.
- Downgrade one level if the supporting evidence is mostly `feature_request` units.
- Do not upgrade on count alone. Ten mentions of the same mild annoyance stay Medium
  unless intensity or observed behavior backs them up.

### How to report

Always give the level **and** a one-line reason that names the evidence:

> **Confidence: Medium.** 4 interviews (INT-01, 02, 05, 06) describe the workaround;
> no support or funnel evidence yet; INT-04 says the current report is "good enough."

## ODI scoring and the opportunity landscape

Use this only when importance and satisfaction ratings exist (from a survey, or
explicitly assumed for illustration). Qualitative confidence (see the confidence
section above) and ODI zones answer different questions, so report both:
confidence = *is this need real?*; zone = *how under-served is it?*

### Inputs per statement

| Field | Meaning |
|---|---|
| `importance` | % of respondents rating importance 4–5 on a 1–5 scale (0–100) |
| `satisfaction` | % rating satisfaction 4–5 with how well they can do it today (0–100) |
| `n` | number of respondents for that statement and segment |
| `segment` / `persona` | **one** persona per map; never mix |

If `n` is missing, the ratings are **assumed**. Every table and chart must then say
`ILLUSTRATIVE: assumed ratings, not survey data`.

### Opportunity score

```
opportunity = importance/10 + max(importance − satisfaction, 0)/10      (range 0–20)
```

### Zones (team guide), applied in this order

**Underserved** is the group of the three opportunity zones (High, Solid, Modest), as in
standard ODI where any job with a score above 10 is underserved. The team guide adds
*Modest*: important jobs that are only somewhat satisfied (80–85%). Standard ODI also
calls scores above 15 "extreme" opportunities; the guide folds them into High.

| # | Zone | Rule |
|---|---|---|
| 1 | Over-served | satisfaction > importance |
| 2 | Table stakes | satisfaction > 85 |
| 3 | Modest opportunity | 80 ≤ satisfaction ≤ 85 **and** importance ≥ 90 |
| 4 | High opportunity | satisfaction < 80 **and** opportunity > 12 |
| 5 | Solid opportunity | satisfaction < 80 **and** 10 ≤ opportunity ≤ 12 |
| 6 | Served right | everything else |

Two cut-offs are read from the guide's chart, not stated in its text:
importance ≥ 90 for *Modest opportunity* (where the light-green box starts) and *Table stakes*
sitting below the diagonal (rule 1 runs first). Change them in one place:
the constants at the top of `scripts/landscape.py`.

Order matters: a statement with opportunity 10.9 but satisfaction 86.7 is
**Table stakes**, not Solid.

Interpretation note: the guide describes *Over-served* as "unimportant and well
satisfied", but the rule is geometric. A statement with importance 82 and
satisfaction 91 lands there. Say "satisfaction exceeds importance" in the write-up,
not "unimportant".

### Uncertainty

With `n`:
- Report the 95% margin for each percentage: `1.96 × √(p(1−p)/n) × 100`.
- **Zone stability:** resample importance and satisfaction 2,000 times from a binomial
  with the same n and p. Stability is the % of resamples that land in the same zone.
  Below 80% → flag **zone could change** (within the margin of error).
- Below 30 respondents per persona → flag **small sample**. Report direction, not zones.
- Do not rank statements against each other when their score difference is smaller
  than the margin.

- **Split importance:** 30% or more rate importance 4–5 *and* 30% or more rate it 1–2.
  Often two groups; check by persona.
- **Strong pain:** half or more rate satisfaction 1–2. Prefer it over jobs in the same zone
  with milder answers.
- **Personas disagree:** importance differs by 20 points or more between personas.
- **Whose ratings:** score each job on the persona it belongs to. Pooling everyone lets
  another persona's indifference pull a job down.

Doing this by hand (no code): use the margin and say which boundary it crosses.

Without `n`, mark a statement **borderline** when its opportunity score is within
0.25 of 10 or 12, or its satisfaction within 1 point of 80 or 85.

### Statement checks before surveying or plotting

- **One need per statement.** Split anything joined by "and" across two needs.
- **No solution in the goal.** "Help me get vehicle details" is a need; "chat that
  autotranslates in the app" is a solution. Reword before surveying.
- **Customer voice only.** No internal diagnoses ("because we are not a logistics-enabled
  platform") or internal jargon (page or team acronyms).
- **Distinct outcomes.** If several statements share the same "so I can…", the outcome
  isn't telling them apart.
- **Barrier vs rating.** If the barrier says the capability doesn't exist ("I don't
  have the option", "I can't") but satisfaction ≥ 80, flag a contradiction. Either
  the question measured something else or the barrier is wrong.
