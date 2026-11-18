// sim.ts <pending.ndjson[,more]> [student json] : run the site's own Sanity query + mapping on (current dataset + pending mutations), in memory.
import { parse, evaluate } from "groq-js";
import { readFileSync } from "node:fs";
const NAV = "/Users/subhanrao/Desktop/evidapath/evidapath-navigator/";
const env = readFileSync(NAV + ".env.local", "utf8");
const token = env.match(/^SANITY_READ_TOKEN=(.*)$/m)![1]!.trim().replace(/^"|"$/g, "");
const perspective = env.match(/^SANITY_PERSPECTIVE=(.*)$/m)?.[1]?.trim().replace(/^"|"$/g, "") || "published";
process.env.SANITY_READ_TOKEN = token; process.env.SANITY_PERSPECTIVE = perspective;
const realFetch = globalThis.fetch;
const q = (query: string) => realFetch(`https://jxwrtsiz.api.sanity.io/v2024-01-01/data/query/staging?perspective=${perspective}&query=${encodeURIComponent(query)}`, { headers: { Authorization: `Bearer ${token}` } }).then((r) => r.json()).then((j: any) => j.result);
const docs: any[] = await q(`*[_type in ["university","program","costProfile","admissionsRequirement","decisionPlan","applicantCategory","country","city","sourceRecord","scholarship"]]`);
const byId = new Map(docs.map((d) => [d._id, d]));
for (const file of process.argv[2]!.split(",")) for (const line of readFileSync(file, "utf8").split("\n").filter(Boolean)) {
  const m = JSON.parse(line);
  if (m.createOrReplace) { byId.set(m.createOrReplace._id, m.createOrReplace); continue; }
  const doc = byId.get(m.patch.id); if (!doc) continue;
  for (const [k, v] of Object.entries(m.patch.set ?? {})) {
    const parts = k.split("."); let o: any = doc;
    for (const part of parts.slice(0, -1)) o = o[part] ??= {};
    o[parts.at(-1)!] = v;
  }
}
const dataset = [...byId.values()];
(globalThis as any).fetch = async (url: any, init: any) => {
  const u = new URL(String(url));
  if (u.hostname.endsWith("sanity.io") && u.pathname.includes("/data/query/")) {
    const query = u.searchParams.get("query")!;
    const result = await (await evaluate(parse(query), { dataset })).get();
    return new Response(JSON.stringify({ result }), { headers: { "content-type": "application/json" } });
  }
  return realFetch(url, init);
};
const { getUniversitiesFromSanity, getScholarshipsFromSanity } = await import(NAV + "src/lib/sanity.server");
const { analyze } = await import(NAV + "src/lib/decision-engine");
const { loadFxRates } = await import(NAV + "src/lib/fx.functions");
const unis: any[] = await getUniversitiesFromSanity();
const schols = await getScholarshipsFromSanity();
const fx = await loadFxRates();
const student = JSON.parse(process.argv[3] ?? '{"curriculum":"IB Diploma","gradeBand":"Top Tier: IB 40+ / A*A*A / GPA 4.0 / 95%+ / Abitur 1.0-1.3","subject":"Medicine","budgetUsd":100000,"citizenship":"India","languages":["en"]}');
for (const u of unis) {
  const a: any = analyze(u, student, schols, unis, fx);
  if (!a.offersSubject) continue;
  console.log([u.id.padEnd(16), (a.programName ?? "").slice(0, 34).padEnd(34), a.academic.level.padEnd(6), (a.academic.headline ?? "").slice(0, 60).padEnd(60), "$" + (a.financial.annualUsd ?? "?"), a.admissions.nextDeadline?.date ?? "-"].join(" | "));
}
