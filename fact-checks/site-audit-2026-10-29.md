# Site + data audit — 2026-10-29

**Scope:** every page (signed in/out, desktop + 390px phone), and all 1,841 published Sanity records in
`staging`. Method: Playwright crawl of 17 routes; automated consistency checks over a full export; HTTP check
of all 275 source URLs; dead links re-checked in a real browser; affected facts re-verified on official pages.

## Site (code) — fixed in 02b13ec and cb20177
- Budget filters ignored (Find My Path) or compared foreign currencies to a USD budget (Discover).
- Fund page ran on mock data, mixed currencies under "$", and had asymmetric scholarship maths.
- Home page featured mock universities and an unverified "DAAD undergraduate grant".
- Living costs had no visible source; ~21 UAE figures are unofficial ("regional advisory aggregates") —
  now labelled "Unofficial estimate".
- 86 IB / American-diploma entries only state A-level grades (import copied one text to every curriculum) —
  now labelled "Published in A-level terms only".
- Passed deadlines (e.g. Oxford 2026-10-15) now marked "passed".
- Stale "illustrative until verified data is connected" copy removed where data is live.

## Data fixed directly (formatting only, no facts changed)
- 180 requirement texts had a stray ". for <Programme>." tail — removed.
- Australia / Malaysia country records lacked ISO code + currency (missing flags) — added `au`/AUD, `my`/MYR.

## Dead source links — 16 URLs, 9 universities — facts re-verified on official pages
| Fact | Result | Official source (checked 2026-10-29) |
|---|---|---|
| UNSW Global University Award | ✅ "$10,000 for 1 year", Term 1 2027 | scholarships.unsw.edu.au/scholarships/id/1988 |
| UNSW BEng (Hons) 2027 tuition AUD 63,840 | ✅ AUD 1,330/UOC × 48 UOC | unsw.edu.au/student/managing-your-studies/fees/international |
| Sydney Intl UG Academic Excellence | ✅ "100% tuition fees and SSAF… max 4 years"; ~20/yr; **Sem 1 2027 closed, Sem 2 2027 open** | sydney.edu.au/scholarships/e/… |
| Sydney Eng/CS 2027 AUD 63,600 | ✅ | sydney.edu.au/study/fees-and-loans/international-student-tuition-fees.html |
| Warwick overseas Band 2 2026/27 £35,530 | ✅ | warwick.ac.uk/services/finance/studentfinance/fees/overseasfees/ |
| Warwick Global Excellence (6 full / 148 half…) | ✅ | warwick.ac.uk/study/scholarships-and-bursaries/warwick-global-excellence-scholarship-2026/ |
| Alberta President's Intl Distinction CAD 120k/4 yrs | ✅ 25 per year, deadline 10 Jan 2027 | ualberta.ca/…/international-entrance-scholarships/ |
| Alberta Intl Admission Scholarship ≤ CAD 10k | ✅ "up to CAN $10,000 based on admission average" (no in-Canada restriction on this page) | same |
| Nottingham UK CS BSc £33,500 (2027 entry) | ✅ | nottingham.ac.uk/…/Computer-Science-BSc-Hons.html |
| Nottingham Malaysia CS RM 59,000 (from Jan 2027) | ✅ | nottingham.edu.my/Study/Undergraduate-courses/Tuition-fees.aspx |
| Nottingham Malaysia High Achievers' Scholarship | ❓ **not found on any current official page** → set UNKNOWN / HUMAN_REVIEW | — |
| TU Delft IB "Maths AA HL only" | ✅ page moved | tudelft.nl/…/specific-diploma-requirements |
| **Taylor's tuition** | ❌ **wrong source + outdated**: 2025 MYR figures from a third-party agent PDF (sharifstudy.com). Official 2026: CS USD 40,049 / 3 yrs, Business USD 42,309 / 3 yrs, Mech Eng USD 53,930 / 4 yrs (+6% service tax for non-Malaysians). Old figures ~9–10% too low. | Taylor's programme pages ("Programme Information for 2026") |

**Pending:** the corrections above are in `fact-checks/pending/2026-10-29-dead-link-fixes.ndjson` (26 patches).
Writing them to Sanity was blocked by the session's safety check; apply with
`scripts/apply-sanity-mutations.sh fact-checks/pending/2026-10-29-dead-link-fixes.ndjson`.
Backup taken first: `~/Desktop/evidapath-sanity-backups/staging-backup-2026-10-29-before-link-fixes.ndjson`.

## Not resolved here (needs a human or a bigger pass)
- 36 source URLs blocked automated checks (Oxford, UCL, Monash, Melbourne, NYU, RWTH…) — likely fine in a
  browser, not individually confirmed.
- 84 "General International Secondary Qualification" entries largely restate A-level/IB terms (e.g. TU Berlin);
  generic but not wrong. Per-curriculum rewrite needs each university's official equivalence tables.
- UAE living costs (Dubai/Sharjah) rest on unofficial aggregates; an official or university source would be better.
- NYUAD Sheikh MBZ wording (see scholarships-initial-5-2026-10-29.md) still awaiting human sign-off.
