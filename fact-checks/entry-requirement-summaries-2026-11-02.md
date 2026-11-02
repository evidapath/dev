# Entry requirements in plain English — 2026-11-02 — WITHDRAWN, do not apply

Withdrawn the same day, before it was applied. A self-audit found 21 summaries stating things their source row
does not say (mainly "no minimum grade is published", and "interview round" for TUM's Stage 2). The rows themselves
were AI research output never checked against university pages, so polishing them would have made unverified data
read as fact. The file is kept in `fact-checks/withdrawn/` for the record only.


File: `fact-checks/withdrawn/2026-11-02-entry-requirement-summaries.ndjson` (610 mutations). Each one only
**sets a new field**, `student_summary`, on an `admissionsRequirement` row. Nothing existing is changed, so no backup
is needed. To undo, unset `student_summary` on the same ids.

## Why

The university cards showed `academic_threshold` as written. Those texts are research notes: "Math + a Science (min
grade equiv. B)", "Min 3.0 GPA … (non-Engineering minimum)", "see Program.extension_metadata…", "MEDIUM confidence",
"not verified from primary source this pass". Many universities also had one A-Level text copied onto their IB,
American and Other rows, so an IB student read A-Level wording, or an A-Level student saw a US GPA as the headline.

## What was written

One or two sentences per row, read from the row's own threshold text: 243 distinct texts across 610 rows (the one empty
TU Delft row is skipped). Rules:

- Only restate what the text says. No new grades, scores or conditions.
- Write for the qualification tab the row sits on. Where one text mixes A-Level and IB figures (Alberta, McGill,
  McMaster, UBC), the A-Level tab gets the A-Level part, the IB tab the IB part, and Other gets both.
- Rows marked unverified say "Entry grades not confirmed yet" and point to the course page.
- ASU states a US GPA on every tab. Its non-American rows add: "That's a US-scale GPA, so ask ASU how your grades
  convert."
- Research wording ("this pass", "confidence", internal field names) is dropped.

The site shows `student_summary` as "What you need". It falls back to the old wording only for rows that don't have one.

## Follow-up (not done here)

ASU's A-Level and IB rows only give a US GPA. ASU's own international pages may give A-Level or IB equivalents; that
needs a primary-source check.
