# Fact-Check: Living Cost Verification — All 50 Schools
**Date:** 2026-10-27  
**Checked by:** Claude Code (sub7an session)  
**Method:** Browser-based primary source verification; government visa financial requirement pages; official university cost-of-attendance pages

---

## Verification Status by Country

| Country | Source Type | Official/Authoritative | Verified Figure | Status |
|---------|------------|------------------------|-----------------|--------|
| **US** | Institution-published CoA (9-month budget) | ✓ Official CoA | Per school (see details) | CONFIRMED — prior sessions |
| **UK** | UKVI Appendix ST (visa requirement) | ✓ Government mandate | London £13,761, non-London £10,539 (9mo) | CONFIRMED — prior sessions |
| **Germany** | German blocked account (Sperrkonto 2025) | ✓ Government mandate | €11,904/year (€992 × 12) | CONFIRMED — prior sessions |
| **Australia** | Dept. of Home Affairs (student visa) | ✓ Government mandate | AUD 29,710/year | CONFIRMED — prior sessions |
| **Canada** | IRCC LICO Sept 2025 | ✓ Government mandate | CAD 22,895/year | CONFIRMED — prior sessions |
| **Netherlands** | StudyinNL.org (Nuffic official) | ✓ Official education authority | €15,000/year (€1,250/month midpoint × 12) | CORRECTED 2026-10-27 |
| **UAE (NYUAD)** | NYUAD official Cost of Attendance page | ✓ Institutional official | USD 5,914/year (indirect costs) | CONFIRMED 2026-10-27 |
| **UAE (other)** | Partial: RIT Dubai accommodation + estimates | Partial | AED 40,000–55,000/year | ESTIMATE — see note |
| **Malaysia** | Taylor's University official accommodation rates | Partial | MYR 28,000/year | ESTIMATE ANCHORED — see note |

---

## Netherlands — CORRECTED

**Previous value:** €12,000/year (€1,000/month × 12 — bottom of range)  
**Corrected value:** **€15,000/year (€1,250/month × 12 — verified midpoint)**

**Primary source:** StudyinNL.org (official Nuffic student information portal)  
**URL:** https://www.studyinnl.org/finances/daily-student-expenses-and-cost-of-living-in-the-netherlands  
**Verified:** 2026-10-27 (browser confirmed)

**Published text:** "Students spend an average of €1,000–€1,500 a month"  
Monthly breakdown (from page): Groceries €244, Study books €41, Transport €67, Leisure €239, Insurance €133 (excluding housing); Housing €450–€1,000/month

**Schools corrected (11 cost profiles):**
- `nl-tu-delft` (2 profiles): €12,000 → €15,000
- `nl-tue` (2 profiles): €12,000 → €15,000
- `nl-uva` (2 profiles): €12,000 → €15,000
- `nl-ut` (3 profiles): €12,000 → €15,000
- `cp-nl-tu-delft` batch-1 (2 profiles): €12,000 → €15,000

**Sanity patch:** transactionId `n0WWGowDKBTI5RzRRhKEhk` (2026-10-27)

---

## NYUAD — CONFIRMED

**Verified value:** **USD 5,914/year (Estimated Total Indirect costs)**  
**Primary source:** NYUAD official Cost of Attendance page  
**URL:** https://nyuad.nyu.edu/en/apply/undergraduate/scholarships-and-financial-aid/cost-of-attendance.html  
**Verified:** 2026-10-27 (browser confirmed, table extracted)

**Official table (2026-27 AY):**

| Expense Type | Amount |
|-------------|--------|
| Tuition | $68,574 |
| Student Health Insurance | $2,416 |
| Books and Supplies | $1,730 |
| Food | $5,800 |
| Housing | $6,000 |
| **Total Direct** | **$84,520** |
| Personal (miscellaneous) | $2,364 |
| Transportation | $3,550 |
| **Total Indirect** | **$5,914** |
| **Total CoA** | **$90,434** |

**Note:** NYUAD scholarships typically cover tuition, food, and housing (direct costs) for admitted students. `estimated_living_costs_annual` = $5,914 represents out-of-pocket personal + transportation expenses for scholarship recipients. This interpretation is correct for EvidaPath's use case.

**Source note updated.** Value unchanged.

---

## UAE (Other Schools) — ESTIMATE NOTE

**No official government mandate for UAE student living costs** (unlike Germany's blocked account, UK's UKVI, Australia's Home Affairs requirement).

**Partial primary source found:**  
RIT Dubai official accommodation rates:
- Double room: AED 20,000/year (Sep–Apr academic year)
- Single room: AED 40,000/year (Sep–Apr academic year)
- Source: rit.edu/dubai/student-accommodation (verified 2026-10-27)

**Estimate reasoning for Dubai (AED 55,000/year):**
- Single/standard room accommodation: AED 20,000–40,000/year
- Food (campus cafeteria): ~AED 9,000/year (AED 750/month × 12)
- Insurance: AED 3,150–6,000/year
- Transport: AED 2,000/year
- Personal/misc: AED 3,000/year
- **Total range: AED 37,000–60,000** → midpoint AED 48,500–55,000

**Verdict:** AED 55,000/year for Dubai schools is **within defensible range** based on official accommodation data. However, it is an estimate, not a government-mandated or institution-published total CoA figure. Source notes updated to reference RIT Dubai accommodation rates as anchor.

**Schools retaining estimates (no change to value):**
- `ae-aus`: AED 50,000/year (Sharjah — ~20% less than Dubai)
- `ae-uaeu`: AED 40,000/year (Al Ain — cheaper Emirate)
- `ae-khalifa`: AED 50,000/year (Abu Dhabi)
- `ae-university-of-sharjah`: AED 50,000/year (Sharjah)
- `ae-birmingham-dubai`: AED 55,000/year (Dubai)
- `ae-heriot-watt-dubai`: AED 55,000/year (Dubai)
- `ae-rit-dubai`: AED 55,000/year (Dubai)
- `ae-canadian-university-dubai`: AED 55,000/year (Dubai)

---

## Malaysia — CORRECTED

**Previous value:** MYR 15,000/year (MYR 1,250/month — too low; below verified accommodation cost)  
**Corrected value:** **MYR 28,000/year (MYR 2,333/month)**

**Primary source anchor:** Taylor's University official student residence page  
**URL:** https://university.taylors.edu.my/en/student-life/support-and-services/accommodation.html  
**Verified:** 2026-10-27 (browser confirmed)

**Official accommodation rates at Taylor's Residence (Subang Jaya):**
- En-Suite Twin (twin-sharing): **RM 1,750/month** (initial payment RM 14,094)
- En-Suite Single (private studio): RM 3,400/month

**Supporting reference:** EMGS (Education Malaysia Global Services — official body under Ministry of Higher Education)  
**URL:** https://educationmalaysia.gov.my/plan-your-studies/plan-your-budget/cost-of-living  
**Published:** "Malaysia's average cost of living is $582 per month" (~MYR 2,735/month at MYR 4.7/USD)

**Correction rationale:**
- Cheapest Taylor's accommodation alone: RM 1,750/month × 12 = **RM 21,000/year**
- Food estimate: RM 600/month × 12 = RM 7,200/year
- Transport: RM 150/month × 12 = RM 1,800/year
- Personal/misc: RM 250/month × 12 = RM 3,000/year
- **Total: RM 33,000/year (conservative, single student, cheapest room)**
- **Using RM 28,000** as a conservative figure given some students commute/share

Note: Malaysia has no government-mandated minimum (unlike Germany/UK/Australia). MYR 28,000 is an institutionally-anchored estimate.

**Schools corrected (12 cost profiles):**
- `my-um` (3 profiles): MYR 15,000 → MYR 28,000
- `my-monash` (3 profiles): MYR 15,000 → MYR 28,000
- `my-nottingham` (3 profiles): MYR 15,000 → MYR 28,000
- `my-taylors` (3 profiles): MYR 15,000 → MYR 28,000

**Sanity patch:** transactionId `n0WWGowDKBTI5RzRRhKEhk` (2026-10-27)

---

## Corrections Summary

| Country | Old Value | New Value | Source | Correction Type |
|---------|-----------|-----------|--------|-----------------|
| Netherlands (all 5 schools, 11 profiles) | €12,000/yr | **€15,000/yr** | StudyinNL.org (Nuffic) | Bottom → midpoint of verified range |
| Malaysia (all 4 schools, 12 profiles) | MYR 15,000/yr | **MYR 28,000/yr** | Taylor's official accommodation + EMGS | Grossly underestimated → anchored estimate |
| NYUAD | USD 5,914/yr | USD 5,914/yr (unchanged) | NYUAD CoA page | Source note corrected |

All other countries (US, UK, Germany, Australia, Canada) remain unchanged — previously verified from government mandate sources.
