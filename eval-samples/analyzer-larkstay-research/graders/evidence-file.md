---
type: llm
focus: { source: file, path: evidence.csv }
---

PASS if the file has columns schema_version, evidence_id, source_id, location, quote, type and speaker_role, at least 15 rows, every row citing a source ID such as INT-03, and no real person's name.
FAIL otherwise.
