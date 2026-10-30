import { annualCostUsd } from "./budget";
import { fmtDate, teachingLanguage, usd } from "./decision-engine";
import type { LiveData } from "./use-live-data";
import type { ProgramView, University } from "./mock-data";

// EvidaPath data briefs: short findings computed live from the verified
// university and scholarship records. Nothing here is written by hand — if the
// data changes, the briefs change.

export type BriefCategory = "Affordability" | "Admissions" | "Scholarships" | "Deadlines";

export interface Brief {
  slug: string;
  category: BriefCategory;
  title: string;
  lead: string;
  takeaway: string;
  columns: [string, string];
  rows: { label: string; value: string; href?: string }[];
  basis: string; // how many records the brief is computed from
  money?: boolean; // figures converted to USD
}

const flagName = (u: University) => `${u.flag} ${u.name}`;

export function buildBriefs(data: LiveData): Brief[] {
  const { universities: unis, scholarships, fx } = data;
  const briefs: Brief[] = [];

  // 1. Lowest verified all-in cost per year
  const allIn = unis
    .map((u) => ({ u, c: annualCostUsd(u, fx) }))
    .filter((x): x is { u: University; c: { usd: number; complete: true } } => !!x.c?.complete)
    .sort((a, b) => a.c.usd - b.c.usd);
  if (allIn.length) {
    const cheapest = allIn.slice(0, 6);
    const dearest = allIn[allIn.length - 1]!;
    briefs.push({
      slug: "lowest-all-in-cost",
      category: "Affordability",
      title: "The lowest verified all-in cost of a year at university",
      lead: `Of ${allIn.length} universities where tuition, fees and living costs are all published, the cheapest year costs ≈ ${usd(cheapest[0]!.c.usd)} and the most expensive ≈ ${usd(dearest.c.usd)} — a ${Math.round(dearest.c.usd / cheapest[0]!.c.usd)}× difference.`,
      takeaway:
        "Living costs, not tuition, decide the bill at many of the cheapest options — check the living-cost source on each card.",
      columns: ["University", "Per year (USD)"],
      rows: cheapest.map(({ u, c }) => {
        const p = u.programDetails?.[0];
        const lang = p ? teachingLanguage(p) : undefined;
        return {
          label: `${flagName(u)}${p ? ` · ${p.name}` : ""}${lang ? ` (${lang})` : ""}`,
          value: `≈ ${usd(c.usd)}`,
        };
      }),
      basis: `${allIn.length} universities with a complete published cost`,
      money: true,
    });
  }

  // 2. Near-free tuition (and what the catch is)
  const lowTuition = unis
    .flatMap((u) =>
      (u.programDetails ?? []).map((p) => ({
        u,
        p,
        t:
          p.costs.tuitionPerYear != null && p.costs.currency
            ? annualCostUsd({ ...u, costs: { ...p.costs, totalAnnual: null } }, fx)
            : null,
      })),
    )
    .filter((x) => x.t && x.t.usd < 3000);
  if (lowTuition.length) {
    const byUni = new Map<string, (typeof lowTuition)[number]>();
    for (const x of lowTuition) if (!byUni.has(x.u.id)) byUni.set(x.u.id, x);
    const list = [...byUni.values()];
    const german = list.filter((x) => teachingLanguage(x.p)).length;
    briefs.push({
      slug: "near-free-tuition",
      category: "Affordability",
      title: "Where tuition is (almost) free — and the catch",
      lead: `${list.length} universities charge international students under $3,000 a year in tuition or semester fees. ${german} of their listed programmes are not taught in English.`,
      takeaway:
        "Near-free tuition usually means public universities in Germany: budget for living costs and, often, German to C1.",
      columns: ["University · programme", "Tuition / fees per year"],
      rows: list.slice(0, 8).map(({ u, p, t }) => ({
        label: `${flagName(u)} · ${p.name}${teachingLanguage(p) ? ` (${teachingLanguage(p)})` : ""}`,
        value: `≈ ${usd(t!.usd)}`,
      })),
      basis: `${unis.length} universities checked`,
      money: true,
    });
  }

  // 3. Guaranteed vs competitive scholarships
  const guaranteed = scholarships.filter((s) => s.selectionBasis === "guaranteed");
  const competitive = scholarships.filter((s) => s.selectionBasis === "competitive");
  const openToAll = scholarships.filter((s) => (s.eligibleCitizenships ?? []).includes("all"));
  briefs.push({
    slug: "guaranteed-vs-competitive",
    category: "Scholarships",
    title: "Guaranteed funding is rare — know which awards you can count on",
    lead: `EvidaPath tracks ${scholarships.length} undergraduate scholarships. ${guaranteed.length} are confirmed as guaranteed for eligible students and ${competitive.length} as competitive; the rest depend on criteria you should check. ${openToAll.length} are open to any citizenship.`,
    takeaway:
      "Only plan around guaranteed awards. Treat competitive scholarships as upside, never as part of the base budget.",
    columns: ["Scholarship", "Basis"],
    rows: [...guaranteed, ...competitive].map((s) => ({
      label: s.name,
      value: s.selectionBasis === "guaranteed" ? "Guaranteed" : "Competitive",
      ...(s.officialSource ? { href: s.officialSource } : {}),
    })),
    basis: `${scholarships.length} verified scholarship records`,
  });

  // 4. Published IB requirements
  const ib = unis
    .flatMap((u) =>
      (u.programDetails ?? []).flatMap((p) =>
        p.admissionsByCurriculum
          .filter((r) => /baccalaureate|\bIB\b/i.test(r.curriculum) && r.threshold)
          .map((r) => {
            const m = r.threshold!.match(
              /\bIB(?: Diploma)?[^0-9.;]{0,25}?(\d{2})\b|\b(\d{2})\s*(?:IB\s*)?points/i,
            );
            return m ? { u, p, score: Number(m[1] ?? m[2]) } : null;
          }),
      ),
    )
    .filter(
      (x): x is { u: University; p: ProgramView; score: number } =>
        !!x && x.score >= 24 && x.score <= 45,
    )
    .sort((a, b) => b.score - a.score);
  if (ib.length) {
    briefs.push({
      slug: "ib-requirements",
      category: "Admissions",
      title: "What IB score do universities actually publish?",
      lead: `${ib.length} programmes publish an IB points requirement, from ${ib[ib.length - 1]!.score} up to ${ib[0]!.score}. Many others review holistically or publish only in A-level terms.`,
      takeaway:
        "A published minimum is a floor, not a target — competitive courses often admit well above it.",
      columns: ["University · programme", "IB points"],
      rows: ib
        .slice(0, 10)
        .map(({ u, p, score }) => ({ label: `${flagName(u)} · ${p.name}`, value: String(score) })),
      basis: `${ib.length} published IB requirements`,
    });
  }

  // 5. Upcoming deadlines (next 90 days)
  const today = new Date().toISOString().slice(0, 10);
  const horizon = new Date(Date.now() + 90 * 864e5).toISOString().slice(0, 10);
  const soon = unis
    .flatMap((u) => (u.deadlines ?? []).map((d) => ({ u, d })))
    .filter(
      ({ d }) =>
        d.deadline && d.deadline.slice(0, 10) >= today && d.deadline.slice(0, 10) <= horizon,
    )
    .sort((a, b) => a.d.deadline!.localeCompare(b.d.deadline!));
  briefs.push({
    slug: "deadlines-next-90-days",
    category: "Deadlines",
    title: "Application deadlines in the next 90 days",
    lead: soon.length
      ? `${soon.length} published application deadlines fall between now and ${fmtDate(horizon)}. The next is ${soon[0]!.u.name} (${soon[0]!.d.label}) on ${fmtDate(soon[0]!.d.deadline!)}.`
      : "No published application deadlines fall in the next 90 days.",
    takeaway:
      "Early rounds (ED/EA) close first and can be binding — check the round before you apply.",
    columns: ["University · round", "Deadline"],
    rows: soon
      .slice(0, 12)
      .map(({ u, d }) => ({ label: `${flagName(u)} · ${d.label}`, value: fmtDate(d.deadline!) })),
    basis: "official application deadlines",
  });

  return briefs;
}
