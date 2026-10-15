#!/usr/bin/env python3
"""The two handoff files every JTBD skill reads and writes: evidence.csv and jobs.csv.

Every skill carries an identical copy of this file in its scripts/ folder, so each skill
works when installed on its own.

Commands:
    python jtbd_files.py validate FILE.csv [--evidence evidence.csv]
    python jtbd_files.py migrate OLD_jobs.csv [--out jobs.csv]       v0.6 jobs file -> schema 1.0
    python jtbd_files.py renumber drafts.csv --out jobs.csv           D1, D2 ... -> 1, 2 ...
    python jtbd_files.py change jobs.csv --label 5 --importance 85 --source judgement \
                         --by user --reason "Front desk sees this every morning" [--evidence E-012]
    python jtbd_files.py explain jobs.csv --label 3 [--evidence evidence.csv]
    python jtbd_files.py based-on jobs.csv
    python jtbd_files.py privacy FILE_OR_TEXT ... [--denylist FILE]
    python jtbd_files.py decide jobs.csv --jobs 3,7 --decision TEXT [--question TEXT] [--reason TEXT]
    python jtbd_files.py decisions jobs.csv          list decisions; flag chosen jobs whose zone has moved

Schema 1.0, in short (full spec: references/*-file.md in each skill):
- evidence.csv: one row per verbatim quote.
- jobs.csv: three kinds of row, told apart by record_type:
    job          one per job (scores, wording, evidence, where each score came from)
    log          the decision log: one row per committed change, append-only; a row with
                 field "decision" records what the team decided and the evidence behind it
    calibration  the last estimate-vs-survey gap, for the next study
"""
import argparse, csv, datetime, os, re, sys

SCHEMA_VERSION = "1.0"

# ---- Zone rules (team guide). landscape.py holds the same numbers; a parity test checks they agree.
TABLE_STAKES_SAT, MODEST_SAT_MIN, MODEST_IMP_MIN, SOLID_OPP, HIGH_OPP = 85, 80, 90, 10, 12


def opportunity(imp, sat):
    return imp / 10 + max(imp - sat, 0) / 10


def zone(imp, sat):
    o = opportunity(imp, sat)
    if sat > imp:
        return "Over-served"
    if sat > TABLE_STAKES_SAT:
        return "Table stakes"
    if sat >= MODEST_SAT_MIN and imp >= MODEST_IMP_MIN:
        return "Modest opportunity"
    if sat < MODEST_SAT_MIN and o > HIGH_OPP:
        return "High opportunity"
    if sat < MODEST_SAT_MIN and o >= SOLID_OPP:
        return "Solid opportunity"
    return "Served right"


UNDERSERVED = ("High opportunity", "Solid opportunity", "Modest opportunity")

# ---- Where a score came from. Shown on the page, the image, the spreadsheet and the read-out.
SOURCES = {
    "ai": "AI estimate",                 # inferred from what people said
    "evidence_update": "evidence update",  # changed in conversation, and Claude could point to quotes
    "judgement": "your judgement",       # changed in conversation or on the page; no quotes back it
    "survey": "survey",                  # measured top-2-box
}
SOURCE_ALIASES = {"edited": "judgement", "your judgement": "judgement", "your_judgement": "judgement",
                  "evidence update": "evidence_update", "updated from evidence": "evidence_update",
                  "ai estimate": "ai", "estimate": "ai", "": "ai"}
BASED_ON_ORDER = ["ai", "judgement", "evidence_update", "survey"]

# ---- Columns
EVIDENCE_COLS = ["schema_version", "evidence_id", "source_id", "location", "quote", "type",
                 "behavior", "speaker_role", "context", "notes"]
EVIDENCE_TYPES = {"goal", "friction", "workaround", "trigger", "desired_outcome", "metric",
                  "feature_request", "alternative"}
JOB_COLS = ["schema_version", "record_type", "label", "persona", "stage", "context", "barrier", "goal",
            "outcome", "importance", "satisfaction", "source", "n", "confidence", "importance_reason",
            "satisfaction_reason", "evidence_ids", "evidence", "contradicts", "provenance", "edit_reason",
            "survey_importance", "survey_satisfaction", "original_context", "original_barrier",
            "original_goal", "original_outcome"]
LOG_COLS = ["logged_at", "field", "from", "to", "zone_from", "zone_to", "by", "reason", "version"]
CALIB_COLS = ["importance_gap", "satisfaction_gap", "n_jobs", "survey_n", "applied"]
ALL_JOB_FILE_COLS = JOB_COLS + LOG_COLS + CALIB_COLS
WORDING = ("context", "barrier", "goal", "outcome")
LOG_FIELDS = {"importance", "satisfaction", "context", "barrier", "goal", "outcome", "persona", "stage",
              "added", "merged", "split", "dropped", "survey", "decision"}
REQUIRED_JOB = ["label", "persona", "stage", "context", "barrier", "goal", "outcome", "importance",
                "satisfaction", "source"]


def norm_source(s):
    s = (s or "").strip().lower()
    return SOURCE_ALIASES.get(s, s)


# ---- Privacy: things that must never reach jobs, quotes, reasons, file names or reports ----------
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE = re.compile(r"(?<!\w)(\+?\d[\d ()-]{7,}\d)(?!\w)")
ACCOUNT = re.compile(r"\b(acct|account|customer|user)[ _#-]?(id|no|number)?[ :#-]*\d{5,}\b", re.I)
SPEAKER = re.compile(r"^\s*\**([A-Z][a-z]+(?: [A-Z][a-z]+)+)\**\s*:", re.M)   # "Maria Lopez:" at line start
# In a transcript (a file with speaker labels), a one-word label is a speaker too: "George:"
LABEL = re.compile(r"^\s*\**([A-Z][a-z]+(?: \d+)?)\**\s*:\**\s*\S", re.M)
INTRO = re.compile(r"\b(?:my name is|I'm|I am|this is)\s+([A-Z][a-z]+ [A-Z][a-z]+)\b")
# A first name alone in an introduction: "I'm George, I run…", "my name is George", "this is George from…"
INTRO_ONE = re.compile(r"\b(?:[Mm]y name is\s+([A-Z][a-z]+)\b|(?:I'm|I am|[Tt]his is)\s+([A-Z][a-z]+)(?=[,.!]| from\b| here\b| speaking\b))")
PSEUDO = re.compile(r"^(User|Guest|Participant|Interviewer|Customer|Company|Front desk|Agent|P)\b", re.I)
NOT_NAMES = {"Front Desk", "Guest Revenue", "Customer Success", "Product Manager", "Team Lead",
             # words that start an introduction or a label but aren't names
             "Interviewer", "Moderator", "Researcher", "Facilitator", "Host", "Speaker", "Respondent",
             "Interviewee", "Staff", "Manager", "Note", "Notes", "Summary", "Context", "Question",
             "Answer", "Q", "A", "Here", "Sorry", "Fine", "Okay", "Sure", "Yes", "No", "Not", "So",
             "Just", "Really", "Glad", "Happy", "Done", "Back", "Calling", "Late", "New",
             # transcript header labels
             "Product", "Period", "Date", "Time", "Location", "Source", "Study", "Participant", "Role",
             "Topic", "Subject", "Status", "Duration", "Session", "Ticket", "Team", "Segment", "Persona",
             "Channel", "Language", "Recording", "Transcript", "Attendees", "Agenda", "Goal", "Goals"}


def privacy_findings(text, denylist=()):
    """[(line_no, kind)] for likely personal data. Never returns the matched text itself, so the
    caller can't echo a real name back to the user."""
    out = []
    # a transcript: two or more lines open with a pseudonym or role label ("Interviewer:", "Guest 3:")
    transcript = sum(1 for m in LABEL.finditer(text) if PSEUDO.match(m.group(1))) >= 2
    for no, line in enumerate(text.splitlines(), 1):
        if EMAIL.search(line):
            out.append((no, "an email address"))
        if PHONE.search(line) and len(re.sub(r"\D", "", PHONE.search(line).group(1))) >= 9:
            out.append((no, "a phone number"))
        if ACCOUNT.search(line):
            out.append((no, "an account ID"))
        names = [m.group(1) for m in list(SPEAKER.finditer(line)) + list(INTRO.finditer(line))]
        names += [m.group(1) or m.group(2) for m in INTRO_ONE.finditer(line)]
        if transcript:
            names += [m.group(1) for m in LABEL.finditer(line)]
        for name in names:
            if not PSEUDO.match(name) and name not in NOT_NAMES:
                out.append((no, "what looks like a real name"))
        low = line.lower()
        for term in denylist:
            if term and term.lower() in low:
                out.append((no, "a term on your privacy list"))
    seen, uniq = set(), []
    for f in out:
        if f not in seen:
            seen.add(f); uniq.append(f)
    return uniq


def load_denylist(path):
    if not path or not os.path.exists(path):
        return []
    return [l.strip() for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]


# ---- Reading and writing ------------------------------------------------------------------------
def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items() if k} for row in r]
        return rows, [(h or "").strip().lower() for h in (r.fieldnames or [])]


def kind_of(header):
    if "evidence_id" in header and "quote" in header:
        return "evidence"
    if "label" in header or "id" in header:
        return "jobs"
    return "unknown"


def read_jobs(path):
    """(jobs, logs, calibration, header). A v0.6 file (no record_type) reads as all jobs."""
    rows, header = read_rows(path)
    jobs, logs, calib = [], [], []
    for r in rows:
        if "label" not in r and "id" in r:
            r["label"] = r.pop("id")
        t = (r.get("record_type") or "job").lower()
        if t == "log":
            logs.append(r)
        elif t == "calibration":
            calib.append(r)
        else:
            r["record_type"] = "job"
            r["source"] = norm_source(r.get("source"))
            jobs.append(r)
    return jobs, logs, calib, header


def write_jobs(path, jobs, logs=(), calib=(), extra_header=()):
    cols = list(ALL_JOB_FILE_COLS)
    for h in extra_header:
        if h and h not in cols:
            cols.append(h)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore")
        w.writeheader()
        for kind, rows in (("job", jobs), ("log", logs), ("calibration", calib)):
            for r in rows:
                r = dict(r)
                r["schema_version"] = SCHEMA_VERSION
                r["record_type"] = kind
                w.writerow(r)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


# ---- Validation ---------------------------------------------------------------------------------
def validate_evidence(path):
    rows, header = read_rows(path)
    errs, warns = [], []
    missing = [c for c in ("evidence_id", "source_id", "location", "quote", "type", "speaker_role") if c not in header]
    if missing:
        errs.append("missing columns: " + ", ".join(missing))
        return errs, warns, rows
    if "schema_version" not in header:
        errs.append("no schema_version column (expected %s)" % SCHEMA_VERSION)
    seen = set()
    for i, r in enumerate(rows, 2):
        v = r.get("schema_version", "")
        if v and v.split(".")[0] != SCHEMA_VERSION.split(".")[0]:
            errs.append(f"line {i}: schema_version {v} is not {SCHEMA_VERSION}")
        if not r["evidence_id"]:
            errs.append(f"line {i}: blank evidence_id")
        elif r["evidence_id"] in seen:
            errs.append(f"line {i}: duplicate evidence_id {r['evidence_id']}")
        seen.add(r["evidence_id"])
        if not r["quote"]:
            errs.append(f"line {i}: blank quote")
        elif len(r["quote"].split()) > 40:
            warns.append(f"line {i}: quote is {len(r['quote'].split())} words; keep quotes short (25 or fewer)")
        if not r["source_id"] or not r["location"]:
            errs.append(f"line {i}: source_id and location are required")
        if r["type"] and r["type"] not in EVIDENCE_TYPES:
            errs.append(f"line {i}: type {r['type']!r} is not one of {', '.join(sorted(EVIDENCE_TYPES))}")
        if privacy_findings(r["quote"] + " " + r.get("notes", "")):
            errs.append(f"line {i}: the quote or notes contain personal data; replace it with a pseudonym")
    return errs, warns, rows


def validate_jobs(path, evidence_path=None):
    jobs, logs, calib, header = read_jobs(path)
    errs, warns = [], []
    legacy = "record_type" not in header
    if legacy:
        warns.append("this is a v0.6 jobs file (no schema_version or record_type); "
                     "run `jtbd_files.py migrate` to bring it to schema " + SCHEMA_VERSION)
    for c in REQUIRED_JOB:
        if c not in header and not (c == "source" and legacy):
            errs.append(f"missing column: {c}")
    if errs:
        return errs, warns, jobs
    ev_ids = None
    if evidence_path:
        ev_ids = {r["evidence_id"] for r in read_rows(evidence_path)[0]}
    labels = set()
    for j in jobs:
        L = j.get("label")
        if not L:
            errs.append("a job row has no label"); continue
        if L in labels:
            errs.append(f"job {L}: duplicate label")
        labels.add(L)
        if re.fullmatch(r"D\d+", L):
            errs.append(f"job {L}: still has a draft label; renumber after checkpoint 2")
        for c in REQUIRED_JOB:
            if c != "source" and not j.get(c):
                errs.append(f"job {L}: {c} is blank")
        for c in ("importance", "satisfaction"):
            x = num(j.get(c))
            if j.get(c) and (x is None or not 0 <= x <= 100):
                errs.append(f"job {L}: {c} must be 0-100")
        src = j.get("source")
        if src not in SOURCES:
            errs.append(f"job {L}: source {src!r} is not one of {', '.join(SOURCES)}")
        if src == "ai":
            for c in ("importance_reason", "satisfaction_reason", "confidence"):
                if not j.get(c):
                    warns.append(f"job {L}: AI estimate without {c}")
            # a contradicting quote is settled while scoring, never left as an "if" for the read-out
            reasons = (j.get("importance_reason") or "") + " " + (j.get("satisfaction_reason") or "")
            settled = re.search(r"(minus|less|[-−])\s*10\b|deduct|contradict", reasons, re.I)
            for sid in dict.fromkeys(re.findall(r"\b([A-Z]{2,5}-\d+)\s*:", j.get("contradicts") or "")):
                if sid not in reasons and not settled:
                    warns.append(f"job {L}: contradicting quote from {sid} not settled; say in a reason whether it "
                                 "is the same persona and about importance (-10) or not")
        if src == "survey" and not j.get("n"):
            errs.append(f"job {L}: survey score without n")
        if src == "judgement" and not j.get("edit_reason"):
            warns.append(f"job {L}: your judgement without a reason")
        unverified = (j.get("provenance") or "").lower() == "unverified"
        if not unverified and not (j.get("evidence") or j.get("evidence_ids")):
            errs.append(f"job {L}: no evidence (mark provenance 'unverified' if the user supplied it without quotes)")
        if ev_ids is not None:
            for e in filter(None, re.split(r"[;,|\s]+", j.get("evidence_ids", ""))):
                if e not in ev_ids:
                    errs.append(f"job {L}: evidence_id {e} is not in {os.path.basename(evidence_path)}")
        for c in ("context", "barrier", "goal", "outcome", "edit_reason"):
            if privacy_findings(j.get(c, "")):
                errs.append(f"job {L}: {c} contains personal data")
    last = ""
    for k, g in enumerate(logs, 1):
        L = g.get("label")
        is_decision = g.get("field") == "decision"
        for x in (split_labels(L) if is_decision else [L]):
            if x not in labels:
                errs.append(f"log row {k}: job {x} is not in the file")
        if is_decision:
            if not g.get("to"):
                errs.append(f"log row {k}: a decision row needs the decision text (to)")
            if privacy_findings(g.get("to", "")):
                errs.append(f"log row {k}: decision text contains personal data")
        if g.get("field") not in LOG_FIELDS:
            errs.append(f"log row {k}: field {g.get('field')!r} is not one of {', '.join(sorted(LOG_FIELDS))}")
        if not is_decision and norm_source(g.get("source")) not in SOURCES and g.get("source") != "calibration":
            errs.append(f"log row {k}: source {g.get('source')!r} unknown")
        t = g.get("logged_at", "")
        if not re.match(r"\d{4}-\d{2}-\d{2}", t):
            errs.append(f"log row {k}: logged_at must be an ISO date-time")
        elif t < last:
            errs.append(f"log row {k}: out of order; the log is append-only, so add corrections as new rows")
        last = max(last, t)
        if privacy_findings(g.get("reason", "")):
            errs.append(f"log row {k}: reason contains personal data")
    if len(calib) > 1:
        errs.append("more than one calibration row; keep only the latest")
    return errs, warns, jobs


# ---- Operations ---------------------------------------------------------------------------------
def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def apply_change(jobs, logs, label, changes, source, by, reason, evidence_ids="", version=""):
    """Change one job and append one log row per field. Returns the log rows added.

    Rules (see the Opportunity Landscape skill, step 'Ask about a score'):
    - source evidence_update needs evidence_ids; without them, use judgement.
    - overriding a survey score keeps the survey values in survey_importance/satisfaction.
    - the log is append-only: a correction is a new change, never an edit of an old row."""
    source = norm_source(source)
    if source not in ("evidence_update", "judgement", "survey"):
        raise ValueError("source must be evidence_update, judgement or survey")
    if source == "evidence_update" and not evidence_ids:
        raise ValueError("an evidence update must name the evidence IDs behind it; otherwise record it as judgement")
    if privacy_findings(reason or ""):
        raise ValueError("the reason contains personal data; reword it without names or contact details")
    job = next((j for j in jobs if j.get("label") == str(label)), None)
    if job is None:
        raise ValueError(f"no job {label}")
    i0, s0 = num(job["importance"]), num(job["satisfaction"])
    z0 = zone(i0, s0)
    if job.get("source") == "survey" and source != "survey" and ({"importance", "satisfaction"} & set(changes)):
        job.setdefault("survey_importance", fmt(i0)); job["survey_importance"] = job["survey_importance"] or fmt(i0)
        job["survey_satisfaction"] = job.get("survey_satisfaction") or fmt(s0)
    added, t = [], now_iso()
    for field, value in changes.items():
        old = job.get(field, "")
        if field in WORDING and not job.get("original_" + field):
            job["original_" + field] = old
        job[field] = fmt(float(value)) if field in ("importance", "satisfaction") else value
        added.append({"label": job["label"], "logged_at": t, "field": field, "from": old, "to": job[field],
                      "source": source, "by": by, "reason": reason or "", "evidence_ids": evidence_ids,
                      "version": version})
    if {"importance", "satisfaction"} & set(changes):
        job["source"] = source
    z1 = zone(num(job["importance"]), num(job["satisfaction"]))
    for a in added:
        a["zone_from"], a["zone_to"] = z0, z1
    if reason:
        job["edit_reason"] = "; ".join(filter(None, [job.get("edit_reason"), reason]))
    logs.extend(added)
    return added


def split_labels(s):
    return [x for x in re.split(r"[;,\s]+", str(s or "")) if x]


def _snapshot(j):
    i, s_ = num(j["importance"]), num(j["satisfaction"])
    return f"{j['label']}: {zone(i, s_)} · {opportunity(i, s_):.1f} · {SOURCES[norm_source(j.get('source'))]}"


def decide(jobs, logs, labels, decision, question="", reason="", by="user", version=""):
    """Record a decision as a log row: which jobs, what was decided, and the evidence behind it.
    The zones and scores at the time are kept, so a later study can say if a chosen job has moved."""
    labels = split_labels(labels)
    byl = {j["label"]: j for j in jobs}
    missing = [x for x in labels if x not in byl]
    if not labels or missing:
        raise ValueError("name the jobs the decision rests on" if not labels else "no job " + ", ".join(missing))
    if not decision.strip():
        raise ValueError("say what was decided")
    for t in (decision, reason):
        if privacy_findings(t):
            raise ValueError("the decision or reason contains personal data; use a role, not a name")
    chosen = [byl[x] for x in labels]
    ev = []
    for j in chosen:
        for e in filter(None, re.split(r"[;,|\s]+", j.get("evidence_ids", ""))):
            if e not in ev:
                ev.append(e)
    row = {"record_type": "log", "label": "; ".join(labels), "logged_at": now_iso(), "field": "decision",
           "from": question, "to": decision, "zone_from": " | ".join(_snapshot(j) for j in chosen),
           "zone_to": based_on(chosen), "source": "", "by": by, "reason": reason,
           "evidence_ids": "; ".join(ev), "version": version}
    logs.append(row)
    return row


def decision_drift(jobs, logs):
    """For each recorded decision, the chosen jobs whose zone is no longer what it was when decided."""
    byl = {j["label"]: j for j in jobs}
    out = []
    for g in (x for x in logs if x.get("field") == "decision"):
        then = {p.split(":")[0].strip(): p for p in (g.get("zone_from") or "").split(" | ") if ":" in p}
        for L, snap in then.items():
            j = byl.get(L)
            if not j:
                out.append((g, L, snap, "no longer in the jobs file"))
                continue
            z_then = snap.split(":", 1)[1].split(" · ")[0].strip()
            z_now = zone(num(j["importance"]), num(j["satisfaction"]))
            if z_then != z_now:
                out.append((g, L, z_then, z_now))
    return out


def based_on(jobs):
    """'Based on: 6 AI estimates · 2 team judgement · 1 evidence update' (read-outs and images get forwarded, so: team)"""
    c = {}
    for j in jobs:
        s = norm_source(j.get("source"))
        c[s] = c.get(s, 0) + 1
    parts = []
    for s in BASED_ON_ORDER:
        if c.get(s):
            name = ("team judgement" if s == "judgement" else SOURCES[s]) + ("s" if s == "ai" and c[s] != 1 else "")
            parts.append(f"{c[s]} {name}")
    return "Based on: " + " · ".join(parts)


def confidence_note(jobs):
    """The read-out's line on how far to trust the scores (references/score-sources.md)."""
    c = [norm_source(j.get("source")) for j in jobs]
    judged = c.count("judgement")
    if judged:
        return (f"{judged} score{'s reflect' if judged != 1 else ' reflects'} the team's view rather than "
                "customer evidence. Survey before deciding what to build.")
    if c and all(s == "survey" for s in c):
        return "All scores are measured; check the margins of error and any 'zone could change' flags."
    return "Scores include AI estimates: good for choosing what to survey. Run the survey before deciding what to build."


def renumber(rows):
    """Draft labels D1, D2 ... -> 1, 2 ... in the order given. Returns (rows, mapping)."""
    mapping, out = [], []
    for k, r in enumerate(rows, 1):
        r = dict(r)
        old = r.get("label", "")
        r["label"] = str(k)
        mapping.append((old, str(k)))
        out.append(r)
    return out, mapping


def migrate(jobs):
    for j in jobs:
        j["source"] = norm_source(j.get("source"))
        j.setdefault("provenance", "verified" if j.get("evidence") else "unverified")
        if not j.get("provenance"):
            j["provenance"] = "verified" if j.get("evidence") else "unverified"
    return jobs


# ---- CLI ----------------------------------------------------------------------------------------
def _cli():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("file"); v.add_argument("--evidence")
    m = sub.add_parser("migrate"); m.add_argument("file"); m.add_argument("--out")
    n = sub.add_parser("renumber"); n.add_argument("file"); n.add_argument("--out", required=True)
    c = sub.add_parser("change"); c.add_argument("file"); c.add_argument("--label", required=True)
    for f in ("importance", "satisfaction") + WORDING:
        c.add_argument("--" + f)
    c.add_argument("--source", required=True); c.add_argument("--by", default="user")
    c.add_argument("--reason", default=""); c.add_argument("--evidence", default="")
    c.add_argument("--version", default="")
    e = sub.add_parser("explain"); e.add_argument("file"); e.add_argument("--label", required=True)
    e.add_argument("--evidence")
    b = sub.add_parser("based-on"); b.add_argument("file")
    p = sub.add_parser("privacy"); p.add_argument("paths", nargs="+"); p.add_argument("--denylist")
    d = sub.add_parser("decide"); d.add_argument("file"); d.add_argument("--jobs", required=True)
    d.add_argument("--decision", required=True); d.add_argument("--question", default="")
    d.add_argument("--reason", default=""); d.add_argument("--by", default="user"); d.add_argument("--version", default="")
    ds = sub.add_parser("decisions"); ds.add_argument("file")
    a = ap.parse_args()

    if a.cmd == "validate":
        rows, header = read_rows(a.file)
        if kind_of(header) == "evidence":
            errs, warns, rows = validate_evidence(a.file)
            what = f"{len(rows)} quotes"
        else:
            errs, warns, rows = validate_jobs(a.file, a.evidence)
            what = f"{len(rows)} jobs"
        for w in warns:
            print("warning:", w)
        for e_ in errs:
            print("ERROR:", e_)
        print(f"{os.path.basename(a.file)}: {what}, {len(errs)} errors, {len(warns)} warnings")
        sys.exit(1 if errs else 0)
    if a.cmd == "migrate":
        jobs, logs, calib, header = read_jobs(a.file)
        write_jobs(a.out or a.file, migrate(jobs), logs, calib, header)
        print(f"Migrated {len(jobs)} jobs to schema {SCHEMA_VERSION}: 'edited' scores are now 'your judgement'.")
        return
    if a.cmd == "renumber":
        rows, header = read_rows(a.file)
        rows = [r for r in rows if (r.get("record_type") or "job") == "job"]
        out, mapping = renumber(rows)
        write_jobs(a.out, out, extra_header=header)
        print(f"Done: {len(out)} jobs, numbered 1 to {len(out)}.")
        for old, new in mapping:
            print(f"  {old} -> {new}")
        return
    if a.cmd == "change":
        jobs, logs, calib, header = read_jobs(a.file)
        changes = {f: getattr(a, f) for f in ("importance", "satisfaction") + WORDING if getattr(a, f) is not None}
        if not changes:
            sys.exit("Nothing to change: give --importance, --satisfaction or a wording field.")
        try:
            added = apply_change(jobs, logs, a.label, changes, a.source, a.by, a.reason, a.evidence, a.version)
        except ValueError as err:
            sys.exit(f"Not changed: {err}")
        write_jobs(a.file, jobs, logs, calib, header)
        z0, z1 = added[0]["zone_from"], added[0]["zone_to"]
        what = ", ".join(f"{x['field']} {x['from']} to {x['to']}" for x in added)
        print(f"Job {a.label}: {what}; {SOURCES[norm_source(a.source)]}. "
              + (f"Zone {z0} -> {z1}." if z0 != z1 else f"Zone unchanged ({z1})."))
        return
    if a.cmd == "decide":
        jobs, logs, calib, header = read_jobs(a.file)
        try:
            row = decide(jobs, logs, a.jobs, a.decision, a.question, a.reason, a.by, a.version)
        except ValueError as err:
            sys.exit(f"Not recorded: {err}")
        write_jobs(a.file, jobs, logs, calib, header)
        ev = split_labels(row["evidence_ids"])
        chosen = [j for j in jobs if j["label"] in split_labels(row["label"])]
        labels = split_labels(row['label'])
        jobs_txt = labels[0] if len(labels) == 1 else ", ".join(labels[:-1]) + " and " + labels[-1]
        quotes = f"{len(ev)} quote" + ("" if len(ev) == 1 else "s")
        print(f"Recorded the decision: {row['to']}. It rests on job{'s' if len(labels) > 1 else ''} {jobs_txt}, "
              f"backed by {quotes}" + (f" ({', '.join(ev[:4])}{'…' if len(ev) > 4 else ''})" if ev else "")
              + f". {row['zone_to']}.")
        print(confidence_note(chosen))
        return
    if a.cmd == "decisions":
        jobs, logs, _, _ = read_jobs(a.file)
        ds = [g for g in logs if g.get("field") == "decision"]
        if not ds:
            print("No decisions recorded yet."); return
        for g in ds:
            print(f"{g['logged_at'][:10]}: {g['to']} (jobs {', '.join(split_labels(g['label']))}; {g.get('zone_to', '')})")
        for g, L, was, now in decision_drift(jobs, logs):
            print(f"  Job {L}, chosen on {g['logged_at'][:10]}, " + (f"moved from {was} to {now}." if now != "no longer in the jobs file" else "is no longer in the jobs file."))
        return
    if a.cmd == "explain":
        jobs, logs, _, _ = read_jobs(a.file)
        j = next((x for x in jobs if x.get("label") == a.label), None)
        if not j:
            sys.exit(f"No job {a.label}")
        ev = [e for e in (j.get("evidence") or "").split("||") if e.strip()]
        co = [e for e in (j.get("contradicts") or "").split("||") if e.strip()]
        srcs = sorted({e.split(":")[0].strip() for e in ev})
        print(f"Job {a.label}: {j.get('goal')}  ({j.get('persona')}, {j.get('stage')})")
        print(f"  importance {j.get('importance')}, satisfaction {j.get('satisfaction')}: "
              f"{SOURCES.get(j.get('source'), j.get('source'))}; zone {zone(num(j['importance']), num(j['satisfaction']))}")
        print(f"  supported by {len(ev)} quote(s) from {len(srcs)} source(s): {', '.join(srcs) or 'none'}")
        if j.get("evidence_ids"):
            print(f"  evidence IDs: {j['evidence_ids']}")
        for k in ("importance_reason", "satisfaction_reason", "edit_reason"):
            if j.get(k):
                print(f"  {k.replace('_', ' ')}: {j[k]}")
        print(f"  points the other way: {len(co)} quote(s)")
        for e_ in co:
            print("    " + e_.strip())
        hist = [g for g in logs if g.get("label") == a.label]
        print(f"  decision log: {len(hist)} change(s)")
        for g in hist:
            print(f"    {g['logged_at']}  {g['field']} {g['from']} -> {g['to']}  ({SOURCES.get(norm_source(g.get('source')), g.get('source'))})  {g.get('reason')}")
        return
    if a.cmd == "based-on":
        jobs = read_jobs(a.file)[0]
        print(based_on(jobs))
        print(confidence_note(jobs))
        return
    if a.cmd == "privacy":
        deny = load_denylist(a.denylist)
        hits = 0
        for pth in a.paths:
            files = [os.path.join(r, f) for r, _, fs in os.walk(pth) for f in sorted(fs)] if os.path.isdir(pth) else [pth]
            for fp in files:
                try:
                    txt = open(fp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                for line, kind in privacy_findings(txt, deny):
                    hits += 1
                    print(f"{os.path.relpath(fp)}, line {line}: contains {kind}")
        print("No private details found." if not hits else f"{hits} finding(s). Replace them with pseudonyms "
              "(User 1, Company A) and re-attach before anything is read further.")
        sys.exit(1 if hits else 0)


if __name__ == "__main__":
    _cli()
