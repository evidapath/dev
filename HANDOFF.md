# EvidaPath handoff

**Last updated:** 2026-11-18, end of the course-expansion session.
**Read first:** `CLAUDE.md` (the rules; loaded automatically by Claude Code in this folder).
The previous handoff (2026-10-29) is in git history (`git show 38b31cd:HANDOFF.md`); parts
of it are out of date, see "Corrections to the old handoff" below.

## 1. Resuming after a restart (exact steps)

In Terminal:

```
cd ~/Desktop/evidapath && git status && git log --oneline -5
```

Expect a clean tree on `main`, latest commit at or after the one that added this file.
Then start Claude Code in that folder and send:

```
Read CLAUDE.md and HANDOFF.md fully, confirm the hooks in .claude/settings.json are active, then continue from HANDOFF.md section 5 ("Next work") following every rule strictly.
```

What survives the restart, and what doesn't:
- In git: all research JSONs, the builder, tools (`scripts/research/`), hooks, pending
  files, notes. Nothing important lives only in the old session.
- Local only, git-ignored, survives: `.research-cache/` (783 saved official pages and PDFs
  the builder checks quotes against), `evidapath-navigator/.env.local` and `.dev.vars`
  (tokens), the git pre-commit hook.
- Doesn't survive: the browser session `res` used by `bfetch.sh`. Reopen it when needed:
  `cd ~/Desktop/evidapath/evidapath-navigator && playwright-cli -s=res open about:blank`.
- Once per machine: `cd scripts/research/sim && bun install` (groq-js for the simulator).

Quick health check for a new session (all read-only):

```
cd ~/Desktop/evidapath && python3 -I scripts/research/q.py 'count(*[_type=="program"])' && python3 -I scripts/research/check_applied.py fact-checks/pending/2026-11-17-data-fixes.ndjson | tail -1
```

Expect `265` programmes (higher once new batches are applied) and `0 not in place`.

## 2. What EvidaPath is, and where it runs

- App: `evidapath-navigator/` (TanStack Start, Bun, Cloudflare Workers). Data from Sanity
  project `jxwrtsiz`, dataset `staging`, read server-side with a read token.
- Staging: https://evidapath-staging.evidapath.workers.dev (Subhan deploys with
  wrangler from `deploy/cloudflare/`).
- Live evidapath.com: the interim GHL AI Studio site, fed by `scripts/sync-ghl.sh --push`
  (Subhan) then Publish in AI Studio. The domain is locked at Squarespace until about
  2026-12-28; after that hosting moves to Cloudflare.
- Supabase: Offer Vault (student applications/offers), RLS on.
- Repo: github.com/evidapath/dev (public). Claude commits and pushes after a secret scan;
  Subhan runs applies, deploys and GHL pushes.

## 3. State of the data (verified 2026-11-18)

- 53 universities, 265 programmes in Sanity staging (published).
- Every pending file from 2026-11-11 to 2026-11-17 is applied. `check_applied.py` was run
  on each; the only differences are intended later changes:
  - shared source excerpts that later files added quotes to (none lost text);
  - the AUS fee records that the 2026-11-17 fixes corrected;
  - Birmingham Medicine's faculty name (fixed on 2026-11-12).
- Course expansion log, per subject (done / blocked / not offered / found on the way):
  `fact-checks/research/courses-2026-11/README.md`. Read it before adding programmes.
- Subjects covered now: Computer Science, Economics, Business, Engineering (general and
  Civil, Electrical, Chemical, Mechanical branches), Medicine, Psychology, Law,
  Biology/Life Sciences, Architecture.

Batches this session (all applied):

| Commit | What |
|---|---|
| 3f585e3 | Medicine: 8 programmes |
| fc4797b | Engineering branches: 19 |
| 35c9cac, ec7ca4a | Psychology 7, Law 5, Biology 7, Architecture 3; Cambridge College fee and Warwick Business fee fixes |
| fcfd74b | US majors: 20 (same-college reuse); 60 programmes had "AUS online application" as their form, fixed |
| f053f56 | Netherlands Psychology: UvA, Twente; source excerpts made append-only; 2 excerpts restored |
| aeeab66, 21c864f | Canada: UBC, Toronto, McGill, Waterloo Psychology and Biology (8) |
| e56664a | UAE: AUS 4, Heriot-Watt Dubai 4, Birmingham Dubai 1 |
| 9987b10 | RIT Dubai Psychology, CUD Psychology (BA, BSc), UNSW Architectural Studies |
| 5b84c9b | Sharjah: Civil, Electrical and Electronics Engineering, Law in English |
| aa1f048 | Data fixes: Taylor's international fees, UM 3.5-year degrees and SST, Twente TOEFL, McGill CS and RIT CoE durations, AUS compulsory fees, fee notes |
| 38b31cd | `docs/aeo-plan.md` |

## 4. Open items

### Decisions waiting for Subhan
1. Answer/agent engine plan (`docs/aeo-plan.md`): approve the plan to start Phase 1.
2. AnswerThePublic: he creates the free account and runs the seed searches listed in the
   plan, saving CSV exports to `fact-checks/aeo/answerthepublic/`. Claude never creates
   the account.
3. AI crawlers in robots.txt: allow search/answer crawlers only, or training crawlers too.
4. Whether to publish a public data file, and its licence.

### Data still to check (not changed; no quotable source found yet)
- McGill BA Economics and BCom stored as 3 years. McGill's Commerce rules say "three- or
  four-year 120-credit program" (120 credits for students from outside Quebec without
  CEGEP); no Faculty of Arts statement found yet. Science was fixed to 4 from an explicit quote.
- Universiti Malaya Architecture: 3.5-year degree; the builder's `tuition_formula`
  handles whole years only, so it wasn't added. (Programme/cost records do accept 3.5,
  as UM Computer Science and Economics now use.)

### Blocked (don't work around)
- Bot checks: UCL, Oxford, Monash (AU and Malaysia), Melbourne (Cloudflare); Purdue fee
  page (F5 challenge); UBC's students.ubc.ca tuition page (403). UBC fees come from the
  Academic Calendar instead.
- Interactive pages not completed: Alberta cost calculator (opened a browser dialog when
  driven; stopped), McMaster (Gateway admission, interactive requirement and cost pages),
  Sydney (fee and ATAR captured for Psychology: A$63,600 a year 2027 international, ATAR
  80.0, 3 years; IB/A-Level equivalents behind a qualification search; held back).
- Zayed University: only a 2018 study plan and older catalogues with conflicting credit
  totals; not added.
- UAE University and Sharjah Medicine: limited by nationality; held until programmes can
  carry a nationality restriction.

## 5. Next work (in this order unless Subhan says otherwise)

1. If Subhan approves the plan: AEO Phase 1. Server-side data loading for
   `/universities`; one page per university and per programme with sources and check
   dates; sitemap from Sanity; current page descriptions; `noindex` on the workers.dev
   host. Then Phase 2 (schema.org JSON-LD, generated from the same record the page
   renders, validated). Details and property list: `docs/aeo-plan.md`.
2. When AnswerThePublic exports arrive: cluster questions, keep only the ones answerable
   from verified records, build question pages (Phase 3).
3. Remaining course gaps from the README (only where an official page can be read).
4. Earlier open follow-ups: GHL email reminders (`docs/deadline-reminders-ghl.md`), US
   Common Data Set facts.

## 6. Tools (all in the repo)

| Tool | Use |
|---|---|
| `scripts/research/fetch.sh <url>` | Save an official page (HTML + text) to `.research-cache/pages/` |
| `scripts/research/bfetch.sh <url> [secs]` | Same, through the browser, for script-rendered pages |
| `scripts/research/ubcreq.sh`, `utreq.sh` | UBC / U of T requirement pickers (country / school system) |
| `python3 -I scripts/research/raw.py <id>` | Figures embedded in page data |
| `python3 -I scripts/research/q.py '<GROQ>'` | Read-only Sanity query |
| `python3 -I scripts/programmes/build.py <folder> .research-cache/pages <out>` | Build research JSONs into mutations; refuses unsourced values |
| `python3 -I scripts/research/keep_new.py <built> <pending>` | Drop records already in Sanity |
| `python3 -I scripts/research/check_applied.py <pending>` | Is a file already in Sanity? (use on any 409) |
| `scripts/research/sim/sim.ts` | Run the site's own code on staging + pending changes; see its README |
| `scripts/research/gen/*.py` | The generators that wrote this session's research JSONs (examples) |
| `scripts/hooks/` | Rules reminder (every prompt), Bash guard, git pre-commit secret scan |
| `python3 scripts/hooks/test-guard.py` | Self-test: the guard blocks and allows the right commands (17 cases) |
| `git diff --cached \| sh scripts/hooks/secret-scan.sh` | Secret scan; must print 0. Private patterns (the test password) live in the git-ignored `.secret-patterns` |

Note: the Bash guard checks the whole command text, so a command that merely contains
words like a force-push (in a heredoc or test) is blocked too. Write such text with the
file tools instead.

Dry-run a pending file (read-only):

```
cd ~/Desktop/evidapath && TOKEN="$(grep '^SANITY_READ_TOKEN=' evidapath-navigator/.env.local | cut -d= -f2- | tr -d '"')" && jq -s -c '{mutations: .}' fact-checks/pending/<file>.ndjson > /tmp/body.json && curl -s -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" "https://jxwrtsiz.api.sanity.io/v2024-01-01/data/mutate/staging?dryRun=true" -d @/tmp/body.json | head -c 300
```

## 7. Data model notes that matter

- `program` → `university_ref`; `costProfile` and `admissionsRequirement` →
  `program_ref`; one `costProfile` per residency category
  (`applicantCategory-<uni>-residency-<x>`, e.g. `international`, `all-students`,
  `eu-eea`, `domestic`, `malaysian`); one `admissionsRequirement` per curriculum
  (`a-level`, `ib`, `us-hs`, `cbse`, `uae-shs`, `international-other`, …).
- `decisionPlan`: university-wide, or `program_ref` + `plan_type: program_specific_stage`;
  a programme's own deadline replaces the university-wide one.
- `sourceRecord` ids for this pass: `sourceRecord-ev-<sha1(url)[:12]>`
  (`#page-data` appended for embedded-data pages). Excerpts only ever gain quotes.
- Fee notes live in `extension_metadata.fields[_key=="fee_note"].value`; patch them by
  `_key`.
- The site matches subjects by programme name and field (`RELATED` in
  `decision-engine.ts`); a request for one engineering branch never falls back to another
  branch.
- Durations may be fractional (3.5); the app divides semesters by 2 when the unit is
  semesters.

## 8. Corrections to the old handoff (2026-10-29)

- "International fees only": no longer. Each fee group is stored separately
  (international, home/UK, EU/EEA, domestic, Malaysian…) and the site picks by the
  student's citizenship.
- "Draft-only, Suhail signs off": since 2026-10-30 Subhan has authority and Claude may make
  the sign-off call after primary-source checks. Applies are still run by Subhan.
- "Universiti Malaya is public, so no SST": wrong. UM's course pages say fees are "Not
  inclusive of 6% Sales and Service Tax (SST)". Records corrected on 2026-11-17.
- "Birmingham UK fees are null": Birmingham now publishes fees on course pages (2027
  entry), used for the Medicine and engineering records. Birmingham Psychology and Law
  pages had no 2027 details as of 2026-11-12.
- Per-country background in the old file (NYUAD aid, Melbourne Model, German tuition
  rules, UK living cost sources) is still useful context; re-verify before relying on any
  figure in it.
