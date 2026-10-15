# Changelog

## 1.0.0 — 2026-10-15

First public version.

- **One command, `/jtbd`.** Attach research, quotes, jobs or survey results; it says where it will
  start. Three skills hand files to each other: research → `evidence.csv` → `jobs.csv` → landscape.
- **Checked evidence.** A privacy check first, then every quote matched word for word against its
  source, with a coverage report that lists sources with nothing relevant.
- **Framing check** on your research question, and two checkpoints: the framing and the job list.
- **Every score shows its source:** AI estimate, evidence update, your judgement or survey, on the
  page, the chart and the read-out, with a "Based on" line and a note on how far to trust it.
- **Decision log.** Every score change is recorded in the jobs file with its reason, so the history
  travels into the next study.
- **Survey template** with your jobs filled in, to replace estimates with measured scores.
- **Decision record.** Tell Claude what you decided; it's saved in the jobs file with the quotes
  behind it, and the next study or survey flags any chosen job that has moved zone.
