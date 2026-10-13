# A3 — Verified program offerings for the 5 (2026-10-13)

Before creating any new programs, mapped what each university ACTUALLY offers at
bachelor's level (verified vs official sources), for EvidaPath's international audience
(English-taught where language matters). Suhail wants CS + Engineering + Business +
Economics — but **not all 5 offer all 4**, and we must never invent a program (#7).

CS/Informatics already exists for all 5. New programs to add:

| Uni | Engineering | Business | Economics | # new |
|---|---|---|---|---|
| **NYU Abu Dhabi** | General Engineering (also Computer/Civil/Electrical/Bioengineering) | Business, Organizations & Society | Economics (Quant / Finance & Markets / Applied Policy) | 3 |
| **Oxford** | Engineering Science (MEng 4yr; **ESAT** test; A*A*A) | — (combined in E&M) | Economics & Management (BA 3yr; **TARA** test; A*AA) | 2 |
| **Toronto** | Faculty of Applied Science & Eng (prereqs Calculus/Chem/Physics) | Rotman Commerce (BCom; Finance&Econ/Accounting/Management; supp app Feb 1) | Economics (BA, Major/Specialist) | 3 |
| **TU Delft** | Aerospace Engineering (English) | ❌ none (pure technical university) | ❌ none | 1 |
| **TU Munich** | Aerospace (English) | Management & Technology (Munich, English option) | — (covered by M&T) | 2 |

**Total ≈ 11 new programs** (not 15 — Delft/TUM don't offer Business/Economics bachelor's).

## Key per-program facts already surfaced (to verify fully in Step 2)
- Oxford admissions tests differ by program: CS=TMUA, **Engineering Science=ESAT**, **E&M=TARA**. Must not reuse CS's TMUA.
- TU Delft English bachelor's = only Aerospace Eng, Applied Earth Sciences, CSE, Nanobiology. No business/econ.
- TUM English: Aerospace B.Sc. (100% EN), Management & Technology (EN option). (Our existing Informatics is German-taught.)
- Toronto Rotman Commerce is competitive (73%+ prereq avg) + Supplementary Application.
- NYUAD: Engineering + Economics + Business all exist (26 majors, liberal-arts core).

## Step 2 — how to create them (proposal)
Each new program = a Sanity `program` doc + per-curriculum `admissionsRequirement` docs +
residency-tiered `costProfile` docs + `decisionPlan`(s) + language + source_refs, every
field verified against primary sources (same bar as the 5 CS programs). This is a large
write effort (Subhan runs writes with a token). Recommend **depth-first**: build ONE
university's new programs fully first (Oxford or NYUAD — rich English data) as the
template, verify end-to-end in the app, then replicate to the others. Do NOT auto-publish
(Suhail's rule); keep draft/verified/published separate.

NOTE: tuition often differs by program/faculty (e.g. Toronto Engineering vs Arts&Sci CS
have different international fees; Oxford fee band differs by subject). Must fetch
program-specific costs, not reuse CS's (Suhail: "program-specific, not university-wide").

## Step 2 progress — Oxford template (research started 2026-10-13)

**Validated the program-specific-fee rule — fees differ a LOT by program at the same uni:**
- Oxford **Engineering Science**: overseas **£66,580** (2027, confirmed — top band, same as CS);
  Home £10,050; A*A*A (A*s in Maths/Further Maths/Physics); **ESAT** test (NOT CS's TMUA);
  4-yr MEng; English; UCAS deadline 15 Oct.
- Oxford **Economics & Management**: overseas **£43,600** (2026/27; 2027 not yet published —
  record honestly as 2026/27 pending 2027); Home ~£10,050; A*AA (Maths required); **TARA**
  test; 3-yr BA; English; UCAS deadline 15 Oct.
- ⇒ Reusing CS's £66,580 for E&M would overstate by ~£23k/yr. Per-program research is mandatory.

**Remaining per-program data still to fetch before creating Oxford's records:** admissions
requirements per curriculum (IB/US/other) for each, English-language requirement, decision
dates. Same depth as the original 5 CS programs.

### Oxford template — verified data ready for record creation (2026-10-13)

**Engineering Science** (MEng, 4 years, English; specialise Y3 into Biomedical/Chemical/
Civil/Electrical/Information/Mechanical):
- A-Level: A*A*A (A*s in Maths & Further Maths/Physics; Maths+Physics required) · **ESAT** test
- IB: 40 incl core (776 at HL, 7s in HL Maths + Physics) · ESAT
- Overseas tuition **£66,580** (2027, confirmed) · Home £10,050 · no separate college fee (combined)
- English: IELTS 7.5/7.0, TOEFL 110, C1 191 · UCAS deadline 15 Oct, decision ~Jan
- Sources: eng.ox.ac.uk/study/undergraduate/applications/entry-requirements; ox.ac.uk course fees/summary table

**Economics & Management** (BA, 3 years, English):
- A-Level: A*AA (Maths at A/A*) · **TARA** test
- IB: 39 incl core (766 at HL) · TARA
- Overseas tuition **£43,600** (2026/27; 2027 not yet published — record as 2026/27, flag pending) · Home ~£10,050
- English: IELTS 7.5/7.0 · UCAS deadline 15 Oct, decision ~Jan
- Sources: economics.ox.ac.uk/undergraduate-admissions-criteria; sbs.ox.ac.uk E&M; ox.ac.uk course fees

US-HS/AP admissions thresholds for these two still to fetch before finalizing (A-Level+IB done).

## Creation mechanism (decide with Suhail before writing)
The original data came from Suhail's pipeline (normalized records → `normalized_to_sanity_ndjson_v1_2.py`),
giving schema-correct interlinked docs. Adding programs via ad-hoc API mutations risks schema
drift (programs/admissions/costs need many required fields + references). **Recommend: add new
programs through Suhail's pipeline or the Studio editor (schema-enforced), not hand-written NDJSON.**
Confirm his preferred path before creating records.

## Honest scope note
Step 2 (create ~11 programs, each = program + per-curriculum admissions + residency-tiered
costs + deadlines + language + sources, all verified) is a large multi-session build,
comparable in effort to the original 5-university research. Best resourced deliberately,
depth-first one university at a time. Not a single-turn task.
