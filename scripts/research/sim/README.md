# sim.ts: run the site's own code on staging data plus pending changes

    cd scripts/research/sim && bun install        # once
    bun sim.ts <pending.ndjson[,more.ndjson]> '<student json>'

Loads every published document from Sanity staging, applies the pending file(s) in memory
(createOrReplace and patch.set), then runs the site's real `getUniversitiesFromSanity` and
`analyze` for the student, printing one line per university that offers the subject:
id | programme | level | headline | yearly USD | next deadline.
Use an empty file to see the current state; diff the two outputs to see exactly what a
pending file changes. Nothing is written anywhere.

Student example:
    '{"curriculum":"IB Diploma","gradeBand":"Top Tier: IB 40+ / A*A*A / GPA 4.0 / 95%+ / Abitur 1.0-1.3","subject":"Psychology","budgetUsd":100000,"citizenship":"India","languages":["en"]}'
