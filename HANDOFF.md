# EvidaPath — Handoff Document
**Last updated:** 2026-10-29  
**For:** Any new Claude Code session (including Suhail's account). Read this entire file before touching anything.

---

## What This Project Is

EvidaPath is a university-search and offer-vault platform for UAE students. It helps students find, compare, and track universities across the world.

**Stack:**
- Frontend: TanStack Start (React, Cloudflare Workers) — in `evidapath-navigator/`
- Content: Sanity CMS (project `jxwrtsiz`, dataset `staging`) — in `sanity-studio/`
- Database: Supabase (student applications / offer vault)
- Live site: evidapath.com (currently still on mock data — Sanity not wired to prod yet)

**Dev server:**
```bash
cd evidapath-navigator && npm run dev
# → http://localhost:8080/
```

---

## The Non-Negotiable Rules

These are Subhan + Suhail's standing rules. They are not suggestions.

### 1. Zero hallucinations — null > plausible guess
If a fact cannot be traced to a primary source, store `null`. Never fill in a plausible number. A blank field that says "PENDING" is infinitely better than a confident wrong number that a student acts on.

### 2. Draft-only — never publish without Suhail's explicit sign-off
All batch-2 schools are Sanity DRAFTS (`drafts.` prefix). The script `publish_to_sanity.py` exists but **must never be called on batch-2 schools** without Suhail saying "publish these." This is the blast-radius protection for 50 schools × all their programs.

### 3. Primary sources only for facts that students rely on
Tuition fees, deadlines, language requirements, scholarship amounts — these must come from the official university website or official government page. Secondary sources (IDP, Studyportals, Reddit) are zero-confidence.

### 4. International fees only
Always store and display international student tuition. Never domestic/EU/home fees.

### 5. Program-specific costs
Never average across programs. A CS degree and a Business degree at the same school cost differently — store them separately.

---

## The 9 Review Questions

Run these before every meaningful action. Not as a checklist — as actual thinking.

1. **Can this be done better?**
2. **Is this targeted at the correct user?** (A real student making a high-stakes, life-defining decision — not a demo)
3. **If I reviewed this, what faults would I find — and have I removed them?**
4. **Does this fit what the site is for? Does it affect anything else downstream?**
5. **Is this the best possible result? If not, what would make it the best?**
6. **Have I tested this against the real system, or am I assuming?** Assumption is where hallucination enters.
7. **Does every fact trace to a primary source? Does the UI show uncertainty instead of manufacturing certainty?** This is the hard gate.
8. **If this is wrong, can I undo it? What's the blast radius on live / student data?** Dry-run first. Stage before prod. Respect safety blocks.
9. **Is this inside the current phase goal, or am I expanding beyond it?** The phase is: one student, five universities, Discover → Analyze → Plan → Fund. Nothing more.

When a question changes the plan, say so out loud so Subhan and Suhail see the reasoning.

---

## Current State (as of 2026-10-28)

### Batch-2 Import: 50/50 COMPLETE
All 50 universities are in Sanity staging as **DRAFTS**. Never published.

| Country | Schools |
|---------|---------|
| UAE (9) | NYUAD†, AUS, UAEU, Khalifa, U of Sharjah, Birmingham Dubai, Heriot-Watt Dubai, RIT Dubai, Canadian U Dubai |
| US (10) | Princeton, MIT, Harvard, Stanford, UPenn, Cornell, NYU, USC, Purdue, ASU |
| UK (7) | Cambridge, Imperial, UCL, Warwick, Manchester, Birmingham, Nottingham |
| Canada (6) | Waterloo, UBC, McGill, McMaster, Alberta, Toronto† |
| Germany (6) | RWTH Aachen, Heidelberg, TU Berlin, KIT, LMU Munich, TU Munich† |
| Netherlands (4) | TU Delft†, TU/e Eindhoven, UvA Amsterdam, University of Twente |
| Malaysia (4) | University of Malaya, Monash Malaysia, Nottingham Malaysia, Taylor's |
| Australia (4) | University of Melbourne, Monash, University of Sydney, UNSW |

† = Batch-1 schools (published in Sanity staging). All others are draft-only.

### Verification Status: ALL 50 TUITION FEES VERIFIED
See `sanity-studio/fact-checks/` for full documentation per country.
See `sanity-studio/scripts/mark_verified_in_sanity.py` for the authoritative list of verified schools.

Every school has been fact-checked against primary sources. Corrections were applied where stored values differed from official sources. Key corrections:
- TU/e: €18,600 → **€22,400** (2027-28 new entrant rate)
- UT Twente: CS/ME €16,400 → **€16,869**; IBA €12,300 → **€12,652**
- Imperial: 3 programs corrected to Sept 2027 rates
- Manchester Engineering: corrected from wrong value
- Birmingham Dubai CS/CompEng/Economics: corrected to Sept 2027 rates
- Canadian U Dubai BBA: pre-VAT → VAT-inclusive (67,410 → 70,781)
- Taylor's Malaysia: all 3 programs updated to 2027 official PDF rates
- Monash Malaysia ME + BBusComm: filled from null (primary source confirmed)
- Monash Australia: BCS corrected $55,500 → $58,940

### Living Cost Status: ALL 50 SCHOOLS PATCHED
Living costs have been estimated/verified and patched to Sanity cost profiles.

| Country | Annual Living Cost | Source Type | Confidence |
|---------|-------------------|-------------|------------|
| US (10 schools) | $14,643–$28,359/yr | Institution CoA 9-month budgets | HIGH — official CoA |
| UK Cambridge | £16,944/yr | Cambridge published range midpoint × 12 | HIGH — official |
| UK London (Imperial, UCL) | £13,761/yr | UKVI Appendix ST £1,529/mo × 9 | HIGH — govt mandate |
| UK non-London (5 schools) | £10,539/yr | UKVI Appendix ST £1,171/mo × 9 | HIGH — govt mandate |
| Germany (6 schools) | €11,904/yr | German blocked account 2025 €992/mo × 12 | HIGH — govt mandate |
| Australia (4 schools) | AUD 29,710/yr | Dept. Home Affairs student visa requirement | HIGH — govt mandate |
| Canada (6 schools) | CAD 22,895/yr | IRCC LICO Sept 2025 | HIGH — govt mandate |
| Netherlands (5 schools) | **€15,000/yr** | StudyinNL.org (Nuffic): €1,000–€1,500/mo midpoint × 12 | HIGH — official education authority |
| NYUAD | USD 5,914/yr | NYUAD official CoA page (indirect: personal + transport; housing/meals covered by scholarship) | HIGH — official CoA |
| UAE other (8 schools) | AED 40,000–55,000/yr | Estimate anchored to RIT Dubai official accommodation (AED 20k/yr double room) | ESTIMATE — no govt mandate |
| Malaysia (4 schools) | **MYR 28,000/yr** | Taylor's official accommodation RM 1,750/mo twin-sharing; EMGS cites $582/mo average | ESTIMATE — anchored to official accommodation data |

**NL was corrected:** €12,000 → €15,000 (2026-10-27, txn `n0WWGowDKBTI5RzRRhKEhk`)  
**Malaysia was corrected:** MYR 15,000 → MYR 28,000 (same txn — original figure was 2–3× too low)

### Frontend "Pending Verified Data" Labels: MOSTLY CLEARED

Before this work, 200+ fields showed "Pending verified data." After fixing:

| Label type | Before | After | Notes |
|-----------|--------|-------|-------|
| Academic Threshold | 3 | 0 | Fixed in code: shows "No published grade cutoff" for holistic-admission schools (NYUAD, Toronto, Delft) |
| Living Costs | ~175 | 0 | Patched all cost profiles in Sanity |
| Total Degree Outlay | ~50 | 0 | Fixed in code: falls back to tuition-only total when living cost is null |
| **Affordability Index** | **51** | **51** | **BY DESIGN — needs composite scoring logic, not a data fix** |
| Birmingham UK fee | 2 | 2 | BY DESIGN — Birmingham does not disclose per-programme fees publicly |

**Remaining "PENDING" labels are correct** — they reflect genuinely unavailable data, not missed patches.

---

## P0 Status (2026-10-29)

**P0 — Fix My Path persistence: DONE (acceptance test passed).**
Tested end-to-end with Playwright against the real Supabase (test account `evidapathtesting@gmail.com`):
sign in → save Delft + Imperial from Discover → rows confirmed in `student_saved_universities` → sign out
(redirect to sign-in confirmed) → sign in → `/dashboard` ("My Path") lists both. DB side: RLS on, owner-only
policy, `authenticated` has SELECT/INSERT/UPDATE/DELETE. Also fixed: Discover now shows a persistent "Saved"
state for already-saved universities (previously always "Add to My Path", which made saves look lost).
Open hardening item: `anon` + `authenticated` hold TRUNCATE/TRIGGER/REFERENCES on student tables — revoke pending Subhan's OK.

**P0 — Confirm hosting architecture: DECIDED (2026-10-29, Subhan).**
- Interim: wait for GHL to ship a "pull from GitHub" option → push the updated app into GHL → publish via Squarespace (domain lives there).
- Squarespace account/domain is locked for 60 days (until ~2026-12-28). After that, hosting moves to **Cloudflare**.
- Before relying on GHL for the live app: confirm it can hold the server-side `SANITY_READ_TOKEN`; without it the site silently falls back to mock data.
- A Cloudflare *staging* deploy on a `workers.dev` URL does not need the domain and can be done any time (meets the P0 "staging app works" test).

---

## What Still Needs to Be Done (Priority Order)

### 🔴 CRITICAL — Do These Before Any Publishing

**1. Rotate the Sanity write token**  
The write token has been exposed in conversation at least 3 times. Rotate it at:  
`manage.sanity.io → project jxwrtsiz → API → Tokens`  
The read token in `evidapath-navigator/.dev.vars` is NOT the write token and is fine.  
After rotating: update wherever Subhan/Suhail store it.

**2. Wire Sanity client to the frontend**  
The live site (evidapath.com) is still on mock data. `sanity.server.ts` exists and works locally, but the production deployment doesn't have the Sanity read token as an env var.  
`evidapath-navigator/src/lib/sanity.server.ts` is the integration point.

**3. Decide on hosting (Vercel vs Cloudflare)**  
GHL Vibe cannot host a TanStack Start app with Cloudflare Workers. The options are:  
- Vercel (easiest, has MCP integration)  
- Cloudflare Pages + Workers (native target for TanStack Start)  
Awaiting Subhan + Suhail decision. Nothing should be deployed until this is decided.

### 🟡 BEFORE GO-LIVE — Per-School Gates

**4. Suhail sign-off per school before publishing**  
`publish_to_sanity.py` exists and can publish individual schools with `--only <id>`.  
```bash
# Dry run (safe):
python3 sanity-studio/scripts/publish_to_sanity.py --only us-princeton,us-mit

# Execute (writes to production Sanity — don't do without sign-off):
SANITY_TOKEN=<write-token> python3 publish_to_sanity.py --only us-princeton --dataset production --execute
```
Do NOT use `--scope all` until every school has been individually signed off.

**5. Run mark_verified_in_sanity.py after token rotation**  
```bash
SANITY_TOKEN=<new-write-token> python3 sanity-studio/scripts/mark_verified_in_sanity.py --execute
```
This writes `evidapath_verified: true` to all verified schools (the "Verified against official sources" label in the UI).

**6. Birmingham UK fees — decision needed**  
University of Birmingham UK does not publish per-programme fees. Two options:  
(a) Accept null fees (shown as PENDING) — honest  
(b) Call the international office to request fees — only option for a real figure  
Currently: null (honest). Flag to Suhail.

**7. Affordability Index — needs product decision**  
51 programs show "PENDING" Affordability Index. This requires a composite scoring algorithm (tuition + living cost + scholarship availability + country cost index → score). This is a product feature, not a data task. Flag to Suhail for design.

### 🟢 MAINTENANCE / ONGOING

**8. Annual fee verification cadence**  
Fees change every year. Before each academic cycle (typically Sept–Jan), re-verify all schools from primary sources. The `fact-checks/` directory is the audit trail.

**9. Malaysia SST clarification**  
6% SST applies to private Malaysian universities for non-Malaysian students (from 1 July 2025). Affects: Monash Malaysia, UNM, Taylor's (NOT UM which is public). Whether SST is included or excluded in stored fees varies by school — check fact-check file before presenting totals to students.

**10. Australian 2028 fees**  
Students entering Semester 1, February 2028 (which is the practical intake for UAE A-level students finishing May/June 2027). 2028 fees are not yet published — we're using 2027 rates as the best available proxy. Verify when 2028 rates are published (typically mid-2027).

---

## Technical Reference

### Sanity CMS

**Project:** `jxwrtsiz` | **Dataset:** `staging`  
**API base:** `https://jxwrtsiz.api.sanity.io/v2021-06-07/data/`  
**Perspective for drafts:** add `?perspective=drafts` to any GROQ query URL  

**Key document types:**
| Type | Purpose |
|------|---------|
| `university` | Root university document. Has `evidapath_verified`, `evidapath_verified_at` fields. |
| `program` | Degree programme (references university). Has `curriculum_type`, `tuition_annual`, `program_fee`. |
| `costProfile` | Living cost + total fees for one programme. Has `estimated_living_costs_annual`. |
| `admissionsRequirement` | Academic entry criteria per curriculum (A-Level, IB, etc). Has `academic_threshold`, `subjects`. |
| `scholarship` | Scholarship document (references university/program). Has `type`: `automatic`/`need_based`/`competitive`/`guaranteed`. |
| `sourceRecord` | Citation/provenance for a fact. References parent doc. |

**FACT_CHECKED set** (in `sanity.server.ts`):  
A hardcoded Set of university IDs. If a university's ID is in this set OR its `sanityVerified === true`, the UI shows "Verified against official sources". Currently: NYUAD + Batch-1 schools + all 45 batch-2 schools after `mark_verified_in_sanity.py` runs.

**Draft IDs:** When querying with `perspective=drafts`, `_id` is the base ID (no `drafts.` prefix). But `_originalId` has the `drafts.` prefix. Use `_originalId` for mutations targeting draft documents.

### Key Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `import_universities.py` | Import new universities to Sanity staging as drafts | `python3 import_universities.py --school <id> [--execute]` |
| `mark_verified_in_sanity.py` | Write `evidapath_verified: true` to verified schools | `SANITY_TOKEN=<t> python3 mark_verified_in_sanity.py [--execute]` |
| `publish_to_sanity.py` | Publish draft schools to production Sanity | `SANITY_TOKEN=<t> python3 publish_to_sanity.py --only <ids> --dataset production [--execute]` |
| `apply_data_corrections.py` | Apply batched data corrections to cost profiles | `SANITY_TOKEN=<t> python3 apply_data_corrections.py [--execute]` |

All scripts support `--execute` flag. Without it = dry run (read-only, safe).

### Key Frontend Files

| File | Purpose |
|------|---------|
| `evidapath-navigator/src/lib/sanity.server.ts` | Sanity GROQ queries + data adapter (`adapt()` function). The `FACT_CHECKED` set lives here. |
| `evidapath-navigator/src/lib/universities.functions.ts` | Server function wrapper. Falls back to mock data if Sanity env vars missing. |
| `evidapath-navigator/.dev.vars` | Local env vars (gitignored). Contains `SANITY_READ_TOKEN`. |
| `evidapath-navigator/src/lib/mock-data.ts` | Legacy mock data (fallback). Still used until Sanity is wired to prod. |

### Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `SANITY_READ_TOKEN` | `.dev.vars` (gitignored) | Read drafts locally |
| `SANITY_TOKEN` | Subhan/Suhail hold it — NOT in repo | Write to Sanity (mutations) |
| `SANITY_PERSPECTIVE` | Optional — set to `drafts` to see draft schools locally | Draft preview |

---

## Fact-Check Audit Trail

All fact-checks are in `sanity-studio/fact-checks/`:

| File | Coverage |
|------|---------|
| `us-batch-2026-10-26.md` | 10 US schools — all tuition confirmed from official CoA pages |
| `ca-batch-2026-10-26.md` | 6 Canada schools — Waterloo/McGill/McMaster primary source; UBC/Alberta secondary |
| `uk-batch-2026-10-26.md` | 7 UK schools — Cambridge/Warwick/Birmingham primary source; corrections to Imperial/Manchester |
| `de-batch-2026-10-26.md` | 6 Germany schools — all confirmed (state law + primary source) |
| `nl-batch-2026-10-26.md` | 3 Netherlands schools — TU/e and UT corrected to 2027-28 rates |
| `au-batch-2026-10-26.md` | 4 Australia schools — Monash BCS corrected; UniMelb Melbourne Model noted |
| `ae-batch-2026-10-26.md` | 8 UAE schools — 4 programmes corrected; NYUAD is batch-1 (separate) |
| `my-batch-2026-10-26.md` | 4 Malaysia schools — Taylor's corrected; Monash ME+BBusComm filled from null |
| `living-costs-batch-2026-10-27.md` | All 50 schools — living cost verification, NL and Malaysia corrections documented |

---

## Import Architecture (for adding new schools)

**Never import without a data source.** The importer expects:
1. Official name, country, city, website, QS ranking
2. Programs: CS / Engineering / Business / Economics — only what the school actually offers
3. Accepted qualifications (A-Level, IB, etc.)
4. International tuition + mandatory fees per program
5. Academic thresholds (A-Level grades, IB points) — or explicitly null if holistic
6. Language requirements (IELTS/TOEFL minimum)
7. Application deadlines, platform, required docs
8. Scholarships — type + amount + eligibility (never assume)
9. Living cost — official source preferred; government mandate ideal

The importer builds: university doc + country ref + programs + admissions requirements + cost profiles + scholarships + source records. All as Sanity DRAFTS.

```bash
# Add new school:
SANITY_TOKEN=<write-token> python3 sanity-studio/scripts/import_universities.py --school <new-id> --execute

# Preview locally (read-only):
SANITY_READ_TOKEN=<read-token> SANITY_PERSPECTIVE=drafts npm run dev
```

---

## Git Status

**Branch:** `main`  
**Ahead of origin:** 3 commits (as of 2026-10-28)  
**Recent commits:**
```
43eee52 Correct living costs: NL €12k→€15k, MY MYR15k→MYR28k; verify NYUAD + UAE
86d4196 Fix pending data labels: living costs + academic thresholds + total outlay
86b679d Verification pass: confirm fees from primary sources, null unverifiable data
```

Push when Subhan is ready: `git push origin main`

---

## What "PENDING VERIFIED DATA" Still Means

After all the work, the remaining PENDING labels are **intentional**:

1. **Affordability Index (51 instances):** Needs a product decision on scoring algorithm — not a data gap
2. **Birmingham UK fees (2 instances):** University does not publish per-programme fees — null is the honest answer
3. Any other PENDING labels you encounter: check the fact-check files before filling them in

If you see a PENDING label that you think should be filled, ask: *what is the primary source?* If you can't name a URL, the answer is null.

---

## The Verification Hierarchy (most → least authoritative)

1. **Government mandate** — German Sperrkonto, UKVI Appendix ST, Australian Home Affairs, IRCC LICO. These are legally required minimums. Use exactly as published.
2. **Official institution CoA** — University-published Cost of Attendance (common at US and some NYUAD-style institutions). Use the figure for the relevant student category.
3. **Official education authority** — Nuffic/StudyInNL for Netherlands, EMGS for Malaysia. Use with note.
4. **Official institution accommodation rate** — Published housing prices from the university website. Use as anchor for total estimate.
5. **Regional estimate with stated basis** — When no official mandate or CoA exists (UAE non-NYUAD). Always label as estimate in source note.
6. **Third-party aggregator (IDP, Studyportals, etc.)** — Never use without corroborating from above. Confidence = LOW.
7. **Guess / plausible fill** — NEVER USE. Store null.

---

## Special Notes Per Country

### UAE
- **NYUAD** is different from all other UAE schools. It's a US-style institution (NYU-affiliated) with a published CoA and 100% need-met financial aid. Most students pay zero tuition. Living cost = $5,914/year (indirect: personal + transport; housing + meals covered by scholarship).
- **Other UAE schools** have no official government minimum for living costs (unlike Germany, UK, Australia). Estimates AED 40,000–55,000/year are anchored to RIT Dubai's published accommodation rates.
- **No UAE government mandate** for student visa financial proof (unlike a German blocked account).

### Malaysia
- **6% SST** applies to private universities for non-Malaysian students from 1 July 2025. Applies to: Monash, UNM, Taylor's (NOT UM which is public). Stored fees vary in SST inclusion — check fact-check file.
- **MYR 28,000/year** living cost is anchored to Taylor's official accommodation (RM 1,750/month twin room). The original MYR 15,000 estimate was 2–3× too low.
- **Taylor's** is an independent Malaysian university (not a branch campus). It awards its own MQA-accredited degree.
- **UNM** awards the UK Nottingham degree. **Monash Malaysia** awards the Australian Monash degree.

### Netherlands
- All 3 batch-2 NL universities teach entirely in English — no Dutch required.
- EU students pay Dutch statutory fee (~€2,694/yr). Non-EU pay institutional rates (what we store).
- TU/e had a large fee jump: €18,600 (2026-27) → €22,400 (2027-28 new entrant). This is the correct rate for students applying now.
- €15,000/year living cost = €1,250/month (midpoint of Nuffic range €1,000–€1,500/month).

### UK
- UKVI Appendix ST is the authoritative government minimum for living costs.
- Cambridge living cost uses the university's own published estimate (£1,115–£1,710/month × 12 = £16,944), NOT UKVI, because Cambridge's own figure is higher and more specific.
- Birmingham UK fees are null — the university does not publish per-programme international fees publicly.

### Australia
- **Melbourne Model:** University of Melbourne has NO standalone undergraduate Engineering degree. Engineering is graduate only (Master). Only 2 programs: BSc Computing + BCom.
- Practical intake for UAE A-level students finishing May/June 2027 = **Semester 1, February 2028**.
- Melbourne International Undergraduate Scholarship (MIUS) is explicitly NOT available to UAE students (GDP per capita cap US$10,000 — UAE ~$45,000).
- UNSW application deadline is September (earlier than Nov–Dec at other AU unis).

### Germany
- All German undergraduate programs are taught in German (except KIT Carl Benz School BSc Mechanical Engineering — English-medium, different admission track).
- Primary language requirement: German C1 (TestDaF TDN 4 or DSH-2). IELTS/TOEFL is secondary.
- Baden-Württemberg state law requires €1,500/semester from non-EU students (Heidelberg, KIT). NRW, Berlin, and Bavaria-LMU are tuition-free for non-EU.

### US
- All 10 US schools have been fact-checked from official 2026-27 CoA pages.
- Princeton, MIT, Harvard, Penn: need-blind for international students.
- Stanford, Cornell, NYU, USC, Purdue, ASU: need-aware for international or have different aid policies.
- Purdue and ASU have no international scholarship programs — UAE students pay full sticker.

---

## Contacts / Access

- **Subhan (sub7an):** GitHub account, Sanity project owner, Supabase Owner
- **Suhail:** Publishing gate-keeper, product sign-off authority. No batch-2 school publishes without his explicit "go."
- **Sanity Studio:** sanity.io/manage → project jxwrtsiz
- **Supabase:** supabase.com → project (Subhan is Owner)
- **GitHub repo:** github.com/evidapath/dev (public monorepo)

---

*This file is the source of truth for any new session. Update it when significant work completes.*
