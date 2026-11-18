#!/bin/sh
# UserPromptSubmit hook: added to Claude's context on every prompt, so the rules are in front of
# every task, not only at session start. Full rules: CLAUDE.md at the repo root.
cat <<'TXT'
EVIDAPATH STANDING RULES (from CLAUDE.md; apply to this task, no exceptions):
1. No hallucination, no guessing. Every fact (fee, grade, deadline, duration, faculty, count, URL) comes from a primary source read in THIS task and is quoted verbatim; numbers must appear in the quote. If it isn't published or a page won't load: say so and leave it out. Never fill a gap with a plausible value, a memory, a search-summary, or "usually". Search-engine summaries are leads, never sources.
2. Run the 9 questions on every step and act on them: (1) better? (2) right user (a student making a high-stakes decision)? (3) what faults would a reviewer find, removed? (4) fits the site, what else does it affect? (5) best result? (6) TESTED against the real system, or assumed? (7) primary source for every fact, and the UI shows uncertainty instead of manufacturing certainty? (8) undo path and blast radius on live/student data? (9) inside the current phase/request?
3. Test, don't assume: dry-run every Sanity file, run the site's own code (scripts/research/sim) before and after, rebuild and diff when the builder changes.
4. Subhan runs Sanity applies, deploys and GHL syncs. Claude writes pending files and gives the full copy-paste commands at the end of every report.
5. Never print or commit secrets (Sanity tokens, the test password, API keys); secret-scan before every commit; never rewrite pushed history.
6. Report plainly: what was done, what was NOT done and why, what is uncertain, with figures and sources.
TXT
