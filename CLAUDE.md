# EvidaPath: rules for every Claude Code session

Read this whole file, then `HANDOFF.md`, before doing anything. These rules come from
Subhan (owner) and apply to every task, however small. They are not defaults to weigh
against convenience: if a rule and speed conflict, the rule wins. Hooks in
`.claude/settings.json` repeat the rules on every prompt and block the riskiest commands
(`scripts/hooks/`), but the hooks are a backstop; following the rules is your job.

EvidaPath helps international secondary-school students choose, afford and apply to
universities abroad. A wrong fee, grade or deadline can cost a real student a place or
money. Bangladesh is not a target market; keep everything generic for international
students.

## Rule 1. No hallucination. No guessing. None.

- Every fact you store, display or state to Subhan (fee, grade, score, deadline,
  duration, credits, faculty name, degree name, URL, count, "X is the same as Y") must
  come from a primary source you read **in this task**: the university's own page or
  PDF, or the government page where the government sets the figure.
- Quote it verbatim. Every number you store must appear in the quote of the source it
  cites (`scripts/programmes/build.py` enforces this; hand-written patch files must do the
  same: assert each quote is on the saved page before writing, as
  `scripts/research/gen/fixes.py` does).
- Not sources, only leads to a source: search-engine summaries (WebSearch answer text has
  been wrong in this project, e.g. it put AUS Biology in the wrong college), your own
  memory, Studyportals/IDP/forums, older records in Sanity you haven't re-checked.
- If a figure isn't published, a page won't load, is behind a bot check, or two official
  pages disagree: say so, store nothing (or store the conflict as a conflict), and list it
  in the report. "Not published" is a correct answer; a plausible number is not.
- Never work around a bot check or CAPTCHA (Cloudflare "verify you are human",
  F5/TSPD challenge pages, 403s from bot protection). Record the site as blocked.
- Our own calculations (yearly average of a published total, rate × published credits)
  are allowed only from quoted inputs, and are labelled "our calculation".
- Apply this to your own claims too: before saying "X is missing", "Y was applied",
  "Z is unchanged", check the real system and show the evidence.

## Rule 2. The 9 questions, on every step

Run these before acting and again before reporting. When one changes the plan, say so in
the report so Subhan sees why.

1. Can it be done better?
2. Is this aimed at the correct user: a student making a real, high-stakes decision?
3. If I reviewed this, what faults would I find, and how do I remove them?
4. Does it fit what the site is for, and what else does it affect?
5. Is this the best possible result? If not, how do I make it the best?
6. Have I tested this against the real system, or am I assuming?
7. Does every fact trace to a primary source, and does the UI show uncertainty instead of
   manufacturing certainty?
8. If this is wrong, can I undo it, and what is the blast radius on live and student data?
9. Is this inside the current request, or am I expanding beyond it?

What they mean in practice here:
- (3)/(6): after building, look at the actual output records (thresholds, fees, notes),
  dry-run them against Sanity, and run the site's own code on them
  (`scripts/research/sim`, before vs after). Negative-test new builder checks (feed them
  a bad input and confirm they refuse).
- (4)/(8): a change to the builder or a shared record can affect earlier batches: rebuild
  earlier subject folders and diff. Patches carry `ifRevisionID` so a changed record is
  refused, not overwritten. Shared source excerpts may only grow, never lose text.
- (7): when a value can't be compared (e.g. a grade format the engine doesn't parse), the
  site must show "not published / can't compare", never a fake match.

## Rule 3. Who does what

- Subhan runs: Sanity applies (`scripts/apply-sanity-mutations.sh`), staging deploys
  (`wrangler deploy`), GHL pushes (`scripts/sync-ghl.sh --push`), Studio deploys, AI Studio
  publish. Claude writes pending files under `fact-checks/pending/`, dry-runs them, and
  gives him the commands. The Bash guard hook blocks Claude from running these.
- Claude may commit and push to `github.com/evidapath/dev` (public repo), after a secret
  scan. Never force-push, amend, rebase or otherwise rewrite pushed history (AI Studio
  syncs from it).
- Never create accounts, enter passwords, or sign up for services (e.g. AnswerThePublic):
  ask Subhan. Local sign-in to the dev app with the test password is allowed; never commit
  or print it.

## Rule 4. Secrets

- Never print or commit: Sanity tokens (`evidapath-navigator/.env.local`, `.dev.vars`,
  `sanity-studio/.env.local`), the test password, Anthropic/API keys. Read a token only into
  a shell variable: `TOKEN="$(grep '^SANITY_READ_TOKEN=' evidapath-navigator/.env.local | cut -d= -f2- | tr -d '"')"`.
- Secret-scan the staged diff before every commit:
  `git diff --cached | sh scripts/hooks/secret-scan.sh` must print 0. It checks token shapes
  plus the private patterns (the test password) kept one per line in the git-ignored
  `.secret-patterns` file at the repo root; never write those values into a tracked file,
  not even inside a scan pattern. The pre-commit git hook and the Bash guard run the same
  scan; in a fresh clone recreate `.secret-patterns` and run `scripts/hooks/install-git-hooks.sh`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Rule 5. Reporting

- Plain language; Subhan is non-technical. Lead with the outcome.
- Say what was done, what was NOT done and why (blocked, not published, ambiguous), and
  what is uncertain, with the figures and sources. Never "should work": tested or not.
- List data problems found in existing records as "to check" unless fixed from a source.
- End every report with the full copy-paste commands in one block (Subhan pastes it whole):
  apply file(s) → staging build + deploy → GHL dry run + push, chained with `&&`, then
  "preview and publish in AI Studio". Never "same as before". Template:

  ```
  cd ~/Desktop/evidapath && scripts/apply-sanity-mutations.sh fact-checks/pending/<file>.ndjson && cd ~/Desktop/evidapath/evidapath-navigator && bun install && bun run build && cd ../deploy/cloudflare && npx wrangler@4 deploy && cd ~/Desktop/evidapath && scripts/sync-ghl.sh && scripts/sync-ghl.sh --push
  ```

## How data gets in (the verified workflow)

1. Read the official page: `scripts/research/fetch.sh <url>` (saves HTML + text to
   `.research-cache/pages/<id>.*`, id = sha1(url)[:12]). Script-only pages:
   `scripts/research/bfetch.sh <url>` (browser, session `res`). Figures only in embedded
   page data: `python3 -I scripts/research/raw.py <id>` → `<id>-raw`. PDFs: download to
   `.research-cache/downloads/`, `pdftotext` (or `-layout`) into `.research-cache/pages/<name>.txt`
   with a matching `<name>.url` holding the PDF's URL.
2. Write one research JSON per programme in `fact-checks/research/courses-2026-11/<folder>/`
   (examples in every folder; generators in `scripts/research/gen/`).
3. Build: `python3 -I scripts/programmes/build.py <folder> .research-cache/pages <out.ndjson>`.
   It stops unless every quote is on its saved page and every stored number is in a cited
   quote. Options documented at the top of `build.py`: `living_from`, `fees_from`,
   `english.from_existing`, `college` (US-style shared admission/fees; `subjects_quote`
   when shared required subjects are quoted), `tuition_formula`, `tuition_per_credit` +
   `degree_credits` or `credits_per_year`, `tuition_per_term` + `terms_per_year` +
   `terms_evidence` (+ `mandatory_per_term`), `duration_source`, `deadline`.
4. Keep only new records when re-building a folder that was partly applied:
   `python3 -I scripts/research/keep_new.py <out.ndjson> <pending.ndjson>`.
5. Dry-run against Sanity (`/data/mutate/staging?dryRun=true`), check patched excerpts only
   append, run `scripts/research/sim` before/after, secret-scan, then write
   `fact-checks/pending/<date>-<name>.ndjson`, update
   `fact-checks/research/courses-2026-11/README.md` (done / blocked / found on the way),
   commit, push, report with commands.
6. If an apply fails with 409 (revision mismatch):
   `python3 -I scripts/research/check_applied.py <file>` before anything else. If it reports
   0 not in place, the file was already applied: don't re-apply.

Queries: `python3 -I scripts/research/q.py '<GROQ>'` (read-only, published perspective).

## Where things are

- `evidapath-navigator/`: the app (TanStack Start, Bun). `src/lib/sanity.server.ts`
  (Sanity → app), `src/lib/decision-engine.ts` (matching, `RELATED`, branch filter, analysis).
- `sanity-studio/`: schema (`schemaTypes/`), importer (`scripts/import_universities.py`).
- `scripts/programmes/build.py`: sourced-quote builder. `scripts/research/`: fetch, query,
  simulator, check tools. `scripts/hooks/`: rule hooks.
- `fact-checks/`: research JSONs, pending files, fact-check logs. `docs/`: plans
  (`aeo-plan.md` = answer/agent engine plan).
- `.research-cache/` (git-ignored): saved copies of official pages; rebuilding a folder
  needs its pages here (re-fetch if missing; quotes must still match the live page).
- Sanity: project `jxwrtsiz`, dataset `staging`. Staging site:
  https://evidapath-staging.evidapath.workers.dev. Live evidapath.com is the interim GHL site
  until the move to Cloudflare (domain lock ends ~2026-12-28).
