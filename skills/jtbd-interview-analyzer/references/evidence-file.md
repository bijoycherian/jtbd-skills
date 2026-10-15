# evidence.csv (schema 1.0)

One row per verbatim quote. The JTBD Extractor reads it; `check_quotes.py` and
`jtbd_files.py validate` check it. UTF-8, comma-separated, a header row, quotes around any
field containing a comma.

| Column | Required | Values |
|---|---|---|
| `schema_version` | yes | `1.0` on every row. Skills refuse a different major version |
| `evidence_id` | yes | Stable ID, `E-001`, `E-002`… Never renumber once the user has seen them |
| `source_id` | yes | The source's ID (`INT-03`, `FD-02`, `SUP-118`, `FUN-01`). Pseudonymised: never a person's name |
| `location` | yes | Where in the source: `INT-03.md, line 7` or a timestamp `00:14:32` |
| `quote` | yes | Verbatim, 25 words or fewer. `...` joins parts that appear in order. Annotations go in `[square brackets]` at the end |
| `type` | yes | `goal` · `friction` · `workaround` · `trigger` · `desired_outcome` · `metric` · `feature_request` · `alternative` |
| `behavior` | no | `observed` (they did it, or the data shows it) or `stated` (they say they would, or believe) |
| `speaker_role` | yes | As stated in the source (`business traveller`, `front desk`). Who the study is about is decided later, at checkpoint 1 |
| `context` | no | The situation it happened in |
| `notes` | no | Your interpretation, labelled `[inference]` |

## Types

- **friction:** something got in the way. **workaround:** what they do instead (often the strongest signal).
- **alternative:** a product, service or habit they hire for the job today.
- **metric:** a number, always with its denominator, period and definition. A metric shows
  *where* something happens, never *why*.
- **feature_request:** a clue to a need, never a job by itself.

## Example

```csv
schema_version,evidence_id,source_id,location,quote,type,behavior,speaker_role,context,notes
1.0,E-012,INT-03,"INT-03.md, line 7",I land at 7am and I'm sitting in the lobby until 3.,friction,stated,business traveller,Arriving on a red-eye,
1.0,E-140,FUN-01,"FUN-notes.md, line 3",Pre-arrival email: most guests never open the offer page.,metric,observed,system,,[where, not why]
```

## Source-type guidance

- **Interviews:** prefer stories about a specific recent time over general opinions, which are `stated`.
- **Tickets:** one ticket can give several quotes. A bug is rarely an opportunity; confusion or a
  missing capability usually is.
- **Staff interviews** (front desk, support agents) are evidence *about* customers. The staff
  member is a speaker role, not a persona.
