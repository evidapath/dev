# EvidaPath — Handoff Context

> For a fresh Claude Code session picking up this project mid-stream.

---

## What this project is

EvidaPath is a university-search and offer-vault platform for UAE students. Stack: TanStack Start (React, Cloudflare Workers), Sanity CMS (content), Supabase (student data). Live at evidapath.com.

Key constraint: **never publish hallucinated facts**. Every data field that isn't primary-source verified must be stored as `null` or a caveat string — not a plausible value.

---

## Active work: Batch-2 university import

**Goal:** Import 50 universities into Sanity as DRAFTS (not published). Suhail's requirement doc lists all 50 with required fields.

### Status — 43/50 done as drafts

| Done | Schools |
|------|---------|
| UAE (8/8) | AUS, UAEU, Khalifa, UOS, Birmingham Dubai, Heriot-Watt Dubai, RIT Dubai, Canadian U Dubai |
| US (10/10) | Princeton, MIT, Harvard, Stanford, UPenn, Cornell, NYU, USC, Purdue, ASU |
| UK (7/7) | Cambridge, Imperial, UCL, Warwick, Manchester, Birmingham, Nottingham |
| Canada (5/5) | Waterloo, UBC, McGill, McMaster, Alberta |
| Germany (5/5) | RWTH Aachen, Heidelberg, TU Berlin, KIT, LMU Munich |
| Netherlands (3/3) | TU/e Eindhoven, UvA Amsterdam, University of Twente |

### Remaining (7 schools)

- ~~**Netherlands (3):** TU/e Eindhoven, UvA Amsterdam, University of Twente~~ ✓
- **Malaysia (4):** Malaya, Monash Malaysia, Nottingham Malaysia, Taylor's — **needs `country-my` created first**
- **Australia (4):** Melbourne, Sydney, Monash, UNSW — **needs `country-au` created first**

### Skip these (already in DB from Batch-1):
Oxford, Toronto, TU Munich, TU Delft, NYUAD

---

## Import tooling

**Main script:** `sanity-studio/scripts/import_universities.py`

```bash
# Dry run (safe, no writes):
python3 import_universities.py --school <id>

# Execute (writes to Sanity):
SANITY_TOKEN=<write-token> python3 import_universities.py --school <id> --execute
```

- The script builds the full university scaffold: uni doc + country ref + programs (CS/Engineering/Business/Economics where offered) + admissions + costs + scholarships + sources — all as Sanity **drafts** (`drafts.` prefix on _id).
- Internal refs use **base IDs** (no `drafts.` prefix) so they resolve correctly in both preview and after publishing.
- Each university in the script is a Python dict. Add new ones following the existing pattern (see `us-cornell`, `us-harvard` etc. for reference).

**Sanity project:** `jxwrtsiz`, dataset: `staging`

**Per-school data required (from Suhail's spec):**
1. Official name, country, city, website
2. Programs: CS / Engineering / Business / Economics (include only what the school offers — never fabricate)
3. Accepted qualifications (A-Level, IB, US HS, other)
4. Program-specific academic + language requirements
5. Deadlines, required tests, required docs
6. **International** tuition + mandatory fees + living cost (distinguish intl vs domestic)
7. Scholarships — mark as `automatic`, `need_based`, `competitive`, or `guaranteed`
8. Source URL + verification date + confidence per material field
9. Store uncertain/unavailable fields as `null` — **never fill in a plausible value**

---

## Previewing drafts locally

```bash
# In evidapath-navigator/:
SANITY_READ_TOKEN=<read-token> SANITY_PERSPECTIVE=drafts bun run dev
```

(vite doesn't auto-load `.dev.vars` so pass both inline. Read token CAN read drafts.)

Default perspective is `published` — prod stays safe, never accidentally shows unverified drafts.

---

## Key files

| File | Purpose |
|------|---------|
| `sanity-studio/scripts/import_universities.py` | Batch-2 importer |
| `evidapath-navigator/src/lib/sanity.server.ts` | Sanity GROQ client + adapter |
| `evidapath-navigator/src/lib/universities.functions.ts` | Server fn wrapper (mock fallback) |
| `evidapath-navigator/.dev.vars` | Local env vars (gitignored) — SANITY_READ_TOKEN |
| `evidapath-navigator/src/lib/mock-data.ts` | Legacy mock data (still used as fallback) |

---

## What's already wired (don't re-do)

- Universities page → reads Sanity (published perspective)
- Scholarships page → reads Sanity
- Discover / Find-my-path / Analyze → reads Sanity
- Applications + Offer Vault → writes Supabase, cost lookup from Sanity
- Auth → Supabase Auth, works on both localhost and prod
- 5 Batch-1 schools (NYUAD, Oxford, Toronto, TUM, Delft) → PUBLISHED in Sanity staging, full program coverage (CS/Eng/Business/Econ where applicable)

---

## The 9 review questions — run on EVERY step, without miss

Subhan + Suhail's standing rule. Questions 1–5 are theirs; 6–9 were added after each caught a real error.

1. Can it be done better?
2. Is this targeted at the correct user? (the student making a real, high-stakes decision)
3. If I reviewed this, what faults would I find, and how do I remove them?
4. Does this fit the requirements of what the site is for, and does it affect anything else?
5. Is this the best possible result? If not, how do I make it the best?
6. **Have I tested this against the real system, or am I assuming?** (assumption is where hallucination enters)
7. **Does every fact trace to a primary source, and does the UI show uncertainty instead of manufacturing certainty?** (Suhail's core principle — hard gate)
8. **If this is wrong, can I undo it, and what's the blast radius on live/student data?** (why we dry-run, stage before prod, respect safety blocks)
9. **Is this inside the current phase goal, or am I expanding beyond it?** (phase = one student, five universities, Discover→Analyze→Plan→Fund; nothing more)

Actually run them before acting, not just when reminded. When one changes the plan, say so out loud so Subhan sees the reasoning.

---

## Hard rules (don't break these)

1. **Import as DRAFTS only** — never call `publish_to_sanity.py` on batch-2 schools without explicit sign-off from Suhail
2. **No hallucinated data** — null > plausible placeholder
3. **Program-specific costs** — never use university-wide averages for program-level fields
4. **International tuition** — always international (not domestic/EU)
5. **Scholarship distinction** — guaranteed need-based aid ≠ competitive merit scholarship

---

## Tokens / secrets

- Sanity **write token**: Subhan/Suhail hold it — not in the repo. Pass via `SANITY_TOKEN=...` env var.
- Sanity **read token**: in `evidapath-navigator/.dev.vars` as `SANITY_READ_TOKEN` (gitignored).
- Supabase: Subhan is Owner — credentials in `.env.local` (gitignored).

---

## Next step

Continue Batch-2 with **Malaysia batch** (4 schools — needs `country-my` created first):
Malaya, Monash Malaysia, Nottingham Malaysia, Taylor's.

Then Australia (4 — needs `country-au`).

**Netherlands batch DONE (43/50).** Before publishing Canada schools, verify McGill and McMaster fees from primary sources (both had PDF/SharePoint access issues this pass).

Each uni: 6–8 primary-source lookups. Do in batches of 3–4. Draft-only, verify before moving on.

**UK batch notes (25/50):** build_docs updated with `application_platform_name` + `decision_context_year` + per-programme `std_tests` — all UK schools use these. `country-gb` already published. Cambridge UCAS deadline is 15 Oct (NOT January). Birmingham fees not publicly disclosed (null stored — honest). Nottingham fees are 2027/28 proxies.

**Netherlands batch notes (43/50):** `country-nl` already published. KEY difference from Germany: ALL 3 NL universities teach listed programmes in English — no Dutch language required. Application platform: Studielink.nl for all three. UAE A-level students need IELTS (UAE school location does not qualify for UK-study English exemption). €100 application fee at all three. EU/EEA pay Dutch statutory fee (~€2,694/yr); non-EU pay institutional rates. Scholarships: TU/e and UT Twente have NO institutional Bachelor scholarships (confirmed); UvA has Amsterdam Merit Scholarship (€6,000/yr, very limited — ~1 per programme per year, non-EU only). IELTS thresholds: TU/e and UvA require 6.5 overall / 6.0 per section; UT Twente requires only 6.0 overall / 5.5 per section. Deadlines: TU/e Jan 15; UvA Jan 15 for numerus fixus; UT Twente May 1 for non-EU/visa (earlier than most NL universities). Fees: TU/e €18,600/yr all programmes; UvA CS €21,900/yr (2027-28), UvA Economics €15,730/yr (2027-28); UT TCS/ME €16,400/yr, IBA €12,300/yr (all 2026-27). UvA fees are 2027-28 figures (only year confirmed from primary source). de-lmu spec appears after NL block in the file due to insertion order — functionally correct.

**Germany batch notes (40/50):** `country-de` already published. CRITICAL structural difference: ALL German Bachelor programmes are in German (exception: KIT Carl Benz School BSc Mechanical Engineering International is English-medium). Primary language requirement is German C1 (TestDaF TDN 4-4-4-4 or DSH-2), NOT English. Fee tiers: Baden-Württemberg state law (Heidelberg, KIT) charges non-EU students €1,500/semester tuition; NRW (RWTH), Berlin (TU Berlin), and Bavaria-LMU are FREE for non-EU students (semester contribution only). LMU Munich confirmed NO non-EU tuition despite Bavaria's 2024/25 fee introduction (TUM only adopted it). Fees: RWTH €716/year, Heidelberg €3,380/year, TU Berlin €758/year, KIT €3,368/year, LMU €194/year. All Deutschlandstipendium scholarships (€300/month, competitive). build_docs updated: `lang_instruction` per-programme field + `lang_req.language` + `lang_req.req_name` fields (backward-compatible). Application platforms: uni-assist VPD for most; KIT Carl Benz has own portal; LMU direct (no uni-assist). Standard deadline July 15; Carl Benz April 30.

**Canada batch notes (35/50):** `country-ca` already published. OUAC for Ontario (Waterloo, McMaster); direct portals for UBC, McGill, Alberta. No SAT/ACT required for A-level/IB applicants. Key data notes: Waterloo fees from primary source (official 2026 fee schedule — CS/Eng $69,884, AFM $55,346, Economics $54,020). UBC fees from secondary sources (fees page 403; Board-approved rates confirmed in multiple sources). McGill fees MEDIUM confidence (PDF binary-compressed — BEng $65,168, BCom $71,687, BSc CS ~$64,786, BA Econ ~$54,000). McMaster fees LOW-MEDIUM confidence (cost estimator only — CS $56,233, Eng $69,354, Business $50,003, Social Sci $45,158). Alberta Engineering $49,952 + Business $46,547 + CS $39,792 confirmed; Economics/Arts fee nulled (not found). McMaster and McGill fees must be verified from primary sources before go-live. Alberta tuition guarantee (locked at admission rate for program duration + 1 yr). McGill requires Quebec CAQ in addition to study permit.
