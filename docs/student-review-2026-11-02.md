# 50-student run — 2026-11-02

50 new personas (ids 21–70) through Find My Path on localhost, signed in, 1280px and 390px. Every curriculum and
grade band, all 8 countries plus "Open to anywhere", budgets $10k–$90k, free-text subjects and citizenships as a
student would type them ("CS", "Emirati", "Indian", "British", blank).

All 50 rendered; no crashes, no `undefined`/`NaN` on any results or analysis page.

## Fixed in this pass

| Persona | Before | After |
|---|---|---|
| Lucas (Brazil, IB Strong, Engineering, Germany, $15k, English only) | "2 fit your budget in Germany", but both are German-taught; top pick was Malaysia | "Nothing in Germany taught in your languages fits $15k/yr. 2 would if you study in German." |
| Oliver (US, Developing, Business, US, no limit) | Top pick MIT, then Princeton (full-need schools first) | Foundation and below: cheapest holistic first, labelled "Lowest cost — holistic admissions" (Purdue). Top Tier students unchanged (MIT first) |
| Tom, Raj, Ali, Wei, Fatma, Ravi, Adam, Arun, Noah, Lucas | "Best you can afford" was a school outside the country they chose, with no hint on the top card | "Best you can afford elsewhere" |
| Lucas | "1 cheaper options elsewhere" | "1 cheaper option elsewhere" |

There's no selectivity data in Sanity, so the Developing/Foundation change orders by cost, not by how selective a
school is.

## Checked and correct

- Raj (CBSE Foundation) shown as meeting Khalifa: Khalifa's verified CBSE minimum is 75%.
- Emiratis in the UAE (Zayed, Maryam, Yousef): no tuition at UAEU/HCT/Zayed, living costs only.
- EU citizens in the Netherlands (Emma, Julia) get the EU fee tier.
- Unsupported subjects (Medicine ×6, Law ×2, Psychology ×2, Architecture, Nursing) get "We don't cover X yet".
- "CS" matches Computer Science; blank citizenship works.

## Open (data, not code)

1. **UK Home fees.** Done and applied to staging (Tom re-run: "7 fit your budget in United Kingdom", Birmingham at $27.6k/yr Home, was "Nothing in United Kingdom fits $40k/yr"): British/Irish students get an "I've lived in the UK for the last 3 years"
   question; Home fees (£10,050, 2027 entry) staged for all 7 UK universities — see
   `fact-checks/uk-home-fees-2026-11-02.md`. Also found: no citizenship code for Ireland, Spain, Italy and other EU
   countries (so no EU fees for them), and "Ukrainian" read as British. Fixed.
2. **Data Science** (Meera, US): "Nothing for Data Science in United States yet". No programme is named that, so
   it doesn't match CS. Add as a subject only once there are verified Data Science programmes.
3. **Germany at $10k** (Max, Elif): nothing fits because every German profile's living cost is above ~$10k. Checked
   2026-11-02: the €11,904/yr is the official visa minimum (DAAD: "992 Euro pro Monat", Stand 1.1.2025, still
   current); DAAD puts real costs at €900–1,200/month. Correct as is.
4. **Canadian at Alberta** (Noah): domestic tier shows "Cost not published". Staged: Canadian fees from UAlberta's
   cost calculator, international fees confirmed — see `fact-checks/alberta-fees-2026-11-02.md`. UBC, McMaster,
   Waterloo and McGill have the same gap.
5. **UK Business with A-Levels** (Nadia): all "holistic" — no A-Level rows for Business at the UK schools. Staged: official 2027 offers for all five UK Business programmes, see `fact-checks/uk-business-entry-2026-11-02.md`
   (Economics has them).
