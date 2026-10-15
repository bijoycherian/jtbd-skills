#!/usr/bin/env python3
"""Pre-fill the JTBD survey template with your jobs (card 8).

Usage:
    python survey_template.py jobs.csv --out jtbd-survey.xlsx [--template JTBD_survey_template.xlsx]

Without --template, writes a complete template: How to run it, Job key, Questionnaire (1-5
scale, a persona question and an attention check) and a Responses sheet whose header is the
export layout --ratings reads (respondent_id, persona, attention_pass, J01_imp, J01_sat, ...).
With --template, fills that file's Job key sheet instead and keeps everything else as it is.
Wording comes from the jobs file word for word, so the ratings come back matched to each job.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jtbd_files as jf  # noqa: E402
from landscape import survey_item  # noqa: E402

MIN_VALID = 200
SCALE_IMP = "1 Not at all important · 2 · 3 · 4 · 5 Extremely important"
SCALE_SAT = "1 Not at all satisfied · 2 · 3 · 4 · 5 Completely satisfied · Doesn't apply"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jobs"); ap.add_argument("--out", default="jtbd-survey.xlsx"); ap.add_argument("--template")
    a = ap.parse_args()
    import openpyxl
    from openpyxl.styles import Alignment, Font
    jobs = sorted(jf.read_jobs(a.jobs)[0], key=lambda j: (len(j["label"]), j["label"]))
    items = [(j, survey_item(j)) for j in jobs]
    personas = sorted({j.get("persona", "") for j in jobs if j.get("persona")})
    bold = Font(bold=True)

    if a.template:
        wb = openpyxl.load_workbook(a.template)
        if "Job key" not in wb.sheetnames:
            sys.exit("The template has no 'Job key' sheet; run without --template to get a complete one.")
        ws = wb["Job key"]
        ws.delete_rows(2, ws.max_row)
        for j, (jid, goal, ctx, _, _) in items:
            ws.append([jid, goal, ctx, j.get("persona"), j.get("stage")])
        wb.save(a.out)
        print(f"Filled the Job key in {os.path.basename(a.template)} with {len(items)} jobs: {a.out}")
        return

    wb = openpyxl.Workbook()
    how = wb.active; how.title = "How to run it"
    for line in [
        ["JTBD survey: measure how important each job is and how well it's served today"],
        [""],
        ["1. Check the wording on the Questionnaire sheet reads naturally. Don't reword jobs here: change them in the jobs file, so ratings stay matched."],
        ["2. Copy the questions into your survey tool, in order. Every job gets the same two questions on a 1–5 scale."],
        [f"3. Aim for at least {MIN_VALID} valid answers. With 200, each score has a margin of about ±7 points."],
        ["4. Keep the attention check. Answers that fail it are dropped automatically."],
        ["5. Export the answers with the columns on the Responses sheet (one row per person), then start a new chat with /jtbd and attach the export with your jobs file."],
        [""],
        ["Scores are top-2-box: the % of people answering 4 or 5. Importance and satisfaction are counted separately, so 'Doesn't apply' stays out."],
    ]:
        how.append(line)
    how["A1"].font = Font(bold=True, size=13)
    how.column_dimensions["A"].width = 130

    key = wb.create_sheet("Job key")
    key.append(["job_id", "Job statement (help me …)", "Context (When you …)", "Persona", "Stage"])
    for j, (jid, goal, ctx, _, _) in items:
        key.append([jid, goal, ctx, j.get("persona"), j.get("stage")])

    q = wb.create_sheet("Questionnaire")
    q.append(["#", "Question", "Answers", "Column in the export"])
    q.append(["P", "Which best describes you?", " · ".join(personas + ["None of these"]), "persona"])
    half = len(items) // 2
    n = 0
    for k, (j, (jid, goal, ctx, qi, qs)) in enumerate(items):
        n += 1; q.append([n, qi, SCALE_IMP, f"{jid}_imp"])
        n += 1; q.append([n, qs, SCALE_SAT, f"{jid}_sat"])
        if k + 1 == half:
            q.append(["A", "To show you're reading carefully, please choose 2 for this question.", "1 · 2 · 3 · 4 · 5",
                      "attention_pass (yes if they chose 2)"])
    q.append(["O", "What do you use today to get these done? (optional)", "Free text", "current_solution"])

    resp = wb.create_sheet("Responses")
    resp.append(["respondent_id", "persona", "attention_pass", "duration_sec"]
                + [c for _, (jid, *_r) in items for c in (f"{jid}_imp", f"{jid}_sat")] + ["current_solution"])

    for ws, widths in ((key, [8, 50, 50, 20, 14]), (q, [5, 90, 60, 30]), (resp, [14, 18, 14, 12])):
        for c in ws[1]:
            c.font = bold
        for col, w in zip("ABCDE", widths):
            ws.column_dimensions[col].width = w
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
    wb.save(a.out)
    print(f"Here's the survey template with your {len(items)} jobs already filled in: {a.out}. "
          f"The Questionnaire sheet has every question ready to copy into your survey tool. "
          f"Aim for at least {MIN_VALID} answers.")


if __name__ == "__main__":
    main()
