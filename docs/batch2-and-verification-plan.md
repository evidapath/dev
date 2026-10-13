# EvidaPath — Data Verification & Batch-2 Plan (2026-10-13)

Built from Suhail's Batch-2 requirements doc, the 50-university list, and the
priority table, plus a ground-truth audit of what's actually in Sanity today.
Every phase is run through the 9 review questions.

## 0. Ground truth (audited 2026-10-13)

For the initial 5 universities (NYUAD, TU Delft, Toronto, Oxford, TU Munich):
- **Verified & trustworthy:** FEES only — international + domestic tuition, mandatory
  fees, living costs where published (residency tiers correct as of the cost fix).
- **Exists but UNVERIFIED** (AI-generated, not checked vs primary sources): admissions
  requirements (4 curricula each), language of instruction, application deadlines
  (thin: only NYUAD has 3; others 1), scholarships (1–2 each), testing policy
  (NYUAD only), application documents.
- **Missing:** 3 of 4 program families. Only **Computer Science / Informatics** exists
  per university. Suhail requires CS + Engineering + Business + Economics.
- **Financial aid:** only NYUAD.

**Conclusion:** we are NOT ready to expand to 50. Per Suhail's own objective
("after the initial five-university validation is **complete**"), we must first
(A) verify the existing non-fee data and (B) expand program coverage for the 5.

## The 9 questions, applied to this plan

1. **Can it be done better?** Yes — instead of ad-hoc verification, use a systematic
   per-university × per-field tracker with source URL + date + status. And finish the
   5 fully before scaling, not in parallel.
2. **Correct user?** The student needs the RIGHT program (a business applicant needs
   business data, not CS) and accurate deadlines/requirements — not just fees. So
   program expansion + non-fee verification is squarely for them.
3. **Faults a reviewer would find?** Today the app shows these unis as "verified" but
   only fees are. A student could trust a wrong deadline/requirement. FIX: verify every
   displayed field, or mark per-field verification honestly (never show unverified as
   verified).
4. **Fits requirements / affects anything?** Suhail explicitly wants per-field source +
   verification date + status. Our schema already has this (record_status,
   verification_status, source_refs per record). We must USE and SURFACE it.
5. **Best possible result?** The 5 unis fully verified across ALL displayed fields, with
   4 program families each, before scaling. The batch import then follows the same bar.
6. **Tested, not assuming?** This plan is built on an actual Sanity audit, not a guess.
   Every field gets checked against a PRIMARY source, never trusting the existing
   AI-generated values.
7. **Every fact traces to source / show uncertainty?** Hard gate. A field is shown as
   fact only if verified against an official source; otherwise it's "pending/unverified".
8. **Reversible / blast radius?** All work in Sanity `staging` + git; drafts NOT
   auto-published (Suhail's rule). Nothing reaches students until verified. Safe.
9. **In scope / expanding?** Suhail's sequence is explicit: complete the 5 → import 10 →
   validate → import 40. CURRENT scope = complete + verify the 5. Batch import is the
   NEXT phase, not now.

## Phase A — Complete & verify the initial 5 (CURRENT FOCUS)

Acceptance: a student can run Discover + Target Analysis on the 5 with source-backed
results and accurate eligibility/affordability caveats; every DISPLAYED field is
verified against a primary source or honestly marked pending.

- **A1. Verification tracker.** Create `fact-checks/5-uni-field-matrix.md`: per uni ×
  per field (program, each curriculum's academic reqs, language, each deadline, tests,
  documents, each scholarship's eligibility/award/conditions, aid) → value, source URL,
  verified Y/N, date. This drives everything and is the audit trail.
- **A2. Verify existing non-fee data vs primary sources**, one category at a time across
  all 5 (start with the most decision-critical + checkable):
  1. Application **deadlines** + decision plans (exact dates — easy to verify).
  2. **Admissions requirements** per curriculum (grades/subjects) + **language**.
  3. **Tests** (SAT/ACT/English) + required **documents**.
  4. **Scholarships** (eligibility, award, deadline, conditions) + aid.
  Each verified field → set its record's `evidapath_verified`-style status; conflicts
  surfaced, unpublished values left pending (never invented).
- **A3. Expand programs** to CS + Engineering + Business + Economics for each uni
  (where offered). Each new program needs its own admissions reqs, costs (residency
  tiers), language, deadlines — same verification bar. (Large; may stage per family.)
- **A4. Surface verified non-fee data in the app** (Analyze/Universities) with per-field
  provenance, so "verified" means what it says.

## Phase B — Batch import (NEXT, after A)

Per Suhail: 50 institutions, but **4 are already done** (Oxford #19, Toronto #28, TUM
#33, TU Delft #39) → ~46 new. NYUAD (#15 is NYU New York, different). Sequence: import
**10 first**, validate records + analysis outputs, then **40 in controlled batches**.
Before importing: dedupe vs the 5, preserve schema + git, keep draft/verified/published
separate, do NOT auto-publish. Per-uni required data = Suhail's 8-point list; quality
standards = his (program-specific, intl-vs-domestic tuition, guaranteed-vs-competitive
aid, no AI admission probabilities, final verification by authoritative sources, store
uncertainty as such).

## Phase C — Other priority deliverables (interleave)

- P0 Fix My Path persistence — ✅ DONE (2026-10-13).
- P0 Hosting — decided (Cloudflare), needs execution (separate track).
- P1 Application journey — add notes + status tracking to Applications.
- P1 Counseling waitlist — form → GHL CRM.
- P2 Scholarships — folds into A2/A4 (verify eligibility/funding for the 5).
- P2 Usability testing — Subhan: 5 target-age students complete the core journey.

## First concrete actions (acting now)
1. Build the A1 verification tracker from the current Sanity data.
2. Start A2.1 — verify application deadlines for all 5 against official sources.
