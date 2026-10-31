import { annualCostUsd, budgetFit, matchesSubject, BUDGET_MAX, type BudgetFit } from "./budget";
import type { FxRates } from "./fx.functions";
import { toUsd } from "./fx.functions";
import type { ProgramView, Scholarship, University } from "./mock-data";
import { bandPercent } from "./curricula";

// EvidaPath decision engine: compares ONE student's stated profile with ONE
// university's verified data. Every output is traceable to a published figure;
// when the evidence is missing it says so instead of estimating. It never
// produces an admission "chance".

export interface StudentInput {
  curriculum: string; // as chosen in Find My Path ("IB Diploma", "Cambridge A-Levels", …)
  gradeBand: string; // e.g. "Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7"
  subject: string;
  budgetUsd: number; // annual; BUDGET_MAX or more = no limit
  citizenship: string; // free text ("UAE", "India", …)
}

export type Level = "strong" | "edge" | "gap" | "unknown";

export interface AcademicFit {
  level: Level;
  headline: string;
  requirement: string | null; // the published text for the student's curriculum
  curriculumLabel: string | null; // which row of the university's data was used
  studentBand: string;
  subjects: string[];
  aLevelTermsOnly: boolean;
}

export interface FundingItem {
  name: string;
  award: string;
  basis: "guaranteed" | "competitive" | "check";
  eligible: "yes" | "check";
  deadline?: string;
  annualUsd: number | null; // only for guaranteed % of tuition (counted in the plan)
  source: string;
}

export interface FinancialFit {
  level: Level;
  fit: BudgetFit;
  annualUsd: number | null;
  annualComplete: boolean;
  years: number;
  degreeUsd: number | null;
  guaranteedAnnualUsd: number;
  netDegreeUsd: number | null;
  budgetDegreeUsd: number | null;
  gapDegreeUsd: number | null; // > 0 = shortfall against budget over the degree
  funding: FundingItem[];
  currency: string;
  localAnnual: number | null;
  livingSource?: string;
}

export interface Alternative {
  id: string;
  name: string;
  flag: string;
  program: string;
  annualUsd: number;
  fit: BudgetFit;
  /** Set when the programme is taught in a language other than English. */
  language?: string;
  /** True when annualUsd includes living costs; false = tuition only. */
  complete: boolean;
}

const LANGUAGE_NAMES: Record<string, string> = {
  de: "German",
  nl: "Dutch",
  fr: "French",
  ar: "Arabic",
  ms: "Malay",
};

/** Name of the teaching language when the programme is NOT available in English. */
export function teachingLanguage(p: ProgramView): string | undefined {
  const langs = (p.languages ?? []).map((l) => l.toLowerCase());
  if (!langs.length || langs.includes("en")) return undefined;
  return LANGUAGE_NAMES[langs[0]!] ?? langs[0]!.toUpperCase();
}

export interface Lever {
  kind: "deadline" | "academic" | "funding" | "budget" | "language" | "evidence";
  text: string;
}

export interface DecisionAnalysis {
  program: ProgramView | null;
  programName: string;
  /** Set when the programme isn't taught in English. */
  taughtIn?: string;
  offersSubject: boolean;
  matchingPrograms: string[];
  academic: AcademicFit;
  admissions: {
    level: Level;
    published: number; // curricula with a published requirement
    nextDeadline: { label: string; date: string } | null;
    pastDeadlines: number;
    confidence: string;
    sourceUrl: string;
  };
  financial: FinancialFit;
  alternatives: Alternative[];
  levers: Lever[];
}

// ─── Academic comparison ───────────────────────────────────────────────────

const A_POINTS: Record<string, number> = { "A*": 6, A: 5, B: 4, C: 3, D: 2, E: 1 };

function aLevelScore(grades: string): number | null {
  const parts = grades.toUpperCase().match(/A\*|[A-E]/g);
  if (!parts || parts.length < 3) return null;
  return parts.slice(0, 3).reduce((s, g) => s + (A_POINTS[g] ?? 0), 0);
}

/** Student's band as numeric ranges per system (lower = worst case, upper = best case). */
function studentRanges(band: string) {
  const ib = band.match(/IB\s*(\d{2})(?:\s*-\s*(\d{2})|\+)/i);
  const al = band.match(/((?:A\*|[A-E]){3})(?:\s*-\s*((?:A\*|[A-E]){3}))?/);
  const gpa = band.match(/GPA\s*(\d\.\d)(?:\s*-\s*(\d\.\d))?/i);
  const range = (lo: number | null, hi: number | null) =>
    lo == null ? null : { lo: Math.min(lo, hi ?? lo), hi: Math.max(lo, hi ?? lo) };
  return {
    ib: ib ? range(Number(ib[1]), ib[2] ? Number(ib[2]) : ib[0].includes("+") ? 45 : null) : null,
    alevel: al ? range(aLevelScore(al[1]!), al[2] ? aLevelScore(al[2]) : null) : null,
    gpa: gpa ? range(Number(gpa[1]), gpa[2] ? Number(gpa[2]) : null) : null,
  };
}

type System = "ib" | "alevel" | "us" | "uae" | "cbse" | "abitur" | "other";

function systemOf(curriculum: string): System {
  if (/\bIB\b|baccalaureate/i.test(curriculum)) return "ib";
  if (/a[- ]?level/i.test(curriculum)) return "alevel";
  if (/UAE|Emirati|Ministry of Education/i.test(curriculum)) return "uae";
  if (/CBSE|ISC|Indian|Class XII/i.test(curriculum)) return "cbse";
  if (/US|american|high school|\bAP\b/i.test(curriculum)) return "us";
  if (/abitur/i.test(curriculum)) return "abitur";
  return "other";
}

const ROW_MATCH: Record<System, RegExp> = {
  ib: /baccalaureate|\bIB\b/i,
  alevel: /a[- ]?level/i,
  us: /american|U\.?S\.?|high school/i,
  uae: /UAE Secondary|Emirati|Ministry of Education/i,
  cbse: /CBSE|ISC|Indian|India|Class XII/i,
  abitur: /abitur/i,
  other: /general international|\bother\b|\bnational\b/i,
};

function compare(lo: number, hi: number, req: number): Level {
  if (lo >= req) return "strong";
  if (hi >= req) return "edge";
  return "gap";
}

function academicFit(
  rows: ProgramView["admissionsByCurriculum"],
  student: StudentInput,
): AcademicFit {
  const sys = systemOf(student.curriculum);
  // Curricula without their own row fall back to the university's "other
  // qualifications" row (its general guidance for every other system).
  const row =
    rows.find((r) => ROW_MATCH[sys].test(r.curriculum)) ??
    (sys === "uae" || sys === "cbse" || sys === "abitur"
      ? rows.find((r) => ROW_MATCH.other.test(r.curriculum))
      : undefined) ??
    null;
  const text = row?.threshold?.trim() || null;
  const base = {
    requirement: text,
    curriculumLabel: row?.curriculum ?? null,
    studentBand: student.gradeBand,
    subjects: row?.subjects ?? [],
    aLevelTermsOnly: false,
  };
  if (!text) {
    return {
      ...base,
      level: "unknown",
      headline: row
        ? "No published grade requirement for your curriculum"
        : "This university publishes no requirement for your curriculum in our data",
    };
  }
  const s = studentRanges(student.gradeBand);
  // Monash publishes a points score for three A Levels (A*/A=5 … E=1).
  const monashPts = text.match(/A Level score (\d+)[^.;]*?A\*\/A=5/i);
  if (sys === "alevel" && monashPts && s.alevel) {
    const req = Number(monashPts[1]);
    const band = student.gradeBand.match(/((?:A\*|[A-E]){3})(?:\s*-\s*((?:A\*|[A-E]){3}))?/);
    const pts = (g: string) =>
      (g.toUpperCase().match(/A\*|[A-E]/g) ?? [])
        .slice(0, 3)
        .reduce(
          (t, x) => t + ({ "A*": 5, A: 5, B: 4, C: 3, D: 2, E: 1 } as Record<string, number>)[x]!,
          0,
        );
    if (band) {
      const a = pts(band[1]!),
        b = band[2] ? pts(band[2]) : a;
      const level = compare(Math.min(a, b), Math.max(a, b), req);
      return {
        ...base,
        level,
        headline: headlineFor(level, `A Level score ${req}`, "your A-level band"),
      };
    }
  }
  // Ignore worked examples ("e.g. CCC = 9") when looking for a grade requirement.
  const plain = text.replace(/\(?e\.g\.[^)]*\)?/gi, "");
  const ibReq = text.match(
    /\bIB(?: Diploma)?[^0-9.;]{0,25}?(\d{2})\b|\b(\d{2})\s*(?:IB\s*)?points/i,
  );
  const alReq = plain.match(/\b((?:A\*|[A-E]){3})\b/);
  const gpaReq = text.match(
    /(\d\.\d{1,2})\s*(?:\/\s*4(?:\.0)?)?\s*GPA|GPA[^0-9]{0,12}(\d\.\d{1,2})/i,
  );
  const holistic = /holistic|no fixed|no minimum|not published/i.test(text);

  if (sys === "ib" && ibReq && s.ib) {
    const req = Number(ibReq[1] ?? ibReq[2]);
    const level = compare(s.ib.lo, s.ib.hi, req);
    return {
      ...base,
      level,
      headline: headlineFor(level, `IB ${req}`, `IB ${s.ib.lo}–${s.ib.hi}`),
    };
  }
  if (sys === "alevel" && alReq && s.alevel) {
    const req = aLevelScore(alReq[1]!)!;
    const level = compare(s.alevel.lo, s.alevel.hi, req);
    return { ...base, level, headline: headlineFor(level, alReq[1]!, "your A-level band") };
  }
  // Percentage-graded curricula (UAE MoE, Indian CBSE/ISC): "80%", "minimum 85%".
  const pctReq = plain.match(/(\d{2}(?:\.\d)?)\s*%/);
  const pct = bandPercent(student.gradeBand);
  if ((sys === "uae" || sys === "cbse") && pctReq && pct) {
    const req = Number(pctReq[1]);
    const level = compare(pct.lo, pct.hi, req);
    return { ...base, level, headline: headlineFor(level, `${req}%`, `${pct.lo}–${pct.hi}%`) };
  }
  if (sys === "us" && gpaReq && s.gpa) {
    const req = Number(gpaReq[1] ?? gpaReq[2]);
    const level = compare(s.gpa.lo, s.gpa.hi, req);
    return { ...base, level, headline: headlineFor(level, `GPA ${req}`, "your GPA band") };
  }
  // IB/US rows that only restate A-level grades: flag instead of comparing.
  if (
    (sys === "ib" || sys === "us" || sys === "uae" || sys === "cbse" || sys === "other") &&
    alReq &&
    !ibReq &&
    !gpaReq
  ) {
    return {
      ...base,
      level: "unknown",
      aLevelTermsOnly: true,
      headline: `Published only in A-level terms (${alReq[1]}) — ask for your curriculum's equivalent`,
    };
  }
  return {
    ...base,
    level: "unknown",
    headline: holistic
      ? "Holistic review — no fixed grade cut-off is published"
      : "Requirement published, but not as a grade we can compare",
  };
}

function headlineFor(level: Level, req: string, yours: string): string {
  if (level === "strong") return `Your band meets the published ${req}`;
  if (level === "edge") return `Borderline: ${req} is published; ${yours} only partly reaches it`;
  return `Below the published ${req}`;
}

// ─── Funding ───────────────────────────────────────────────────────────────

const COUNTRY_CODES: [RegExp, string][] = [
  [/\b(uae|emirat|united arab)/i, "ae"],
  [/\bindia/i, "in"],
  [/\bpakistan/i, "pk"],
  [/\b(uk|united kingdom|brit)/i, "gb"],
  [/\b(us|usa|united states|americ)/i, "us"],
  [/\bcanad/i, "ca"],
  [/\begypt/i, "eg"],
  [/\bjordan/i, "jo"],
  [/\bsaudi/i, "sa"],
  [/\bnigeria/i, "ng"],
];

export function citizenshipCode(text: string): string | null {
  for (const [re, code] of COUNTRY_CODES) if (re.test(text)) return code;
  return null;
}

function eligibility(s: Scholarship, code: string | null): "yes" | "no" | "check" {
  const list = (s.eligibleCitizenships ?? []).map((c) => c.toLowerCase());
  if (list.includes("all")) return "yes";
  if (list.length === 1 && /^[a-z]{2}$/.test(list[0]!)) {
    if (!code) return "check";
    return list[0] === code ? "yes" : "no";
  }
  return "check";
}

function guaranteedPct(award: string): number | null {
  if (/up to|tier|varies|need/i.test(award)) return null;
  if (/full (tuition|coverage)|100%/i.test(award)) return 100;
  const m = award.match(/(\d{1,3})\s*%/);
  return m ? Number(m[1]) : null;
}

// ─── Main ──────────────────────────────────────────────────────────────────

// Closely related programme names, tried when a university has no exact match.
const RELATED: [RegExp, string[]][] = [
  [/econ/i, ["Economics", "Commerce", "Business"]],
  [/business|management|commerce|finance/i, ["Business", "Commerce", "Management", "Economics"]],
  [
    /computer|computing|software|informatic|\bcs\b/i,
    ["Computer Science", "Computing", "Informatics", "Software"],
  ],
  [/engineer/i, ["Engineering"]],
];

function pickProgram(
  u: University,
  subject: string,
): { program: ProgramView | null; matches: string[] } {
  const progs = u.programDetails ?? [];
  const find = (term: string) =>
    progs.filter((p) =>
      matchesSubject({ ...u, programs: [p.name, p.fieldOfStudy] } as University, term),
    );
  let matches = find(subject);
  if (!matches.length) {
    const related = RELATED.find(([re]) => re.test(subject))?.[1] ?? [];
    for (const term of related) {
      matches = find(term);
      if (matches.length) break;
    }
  }
  return { program: matches[0] ?? progs[0] ?? null, matches: matches.map((p) => p.name) };
}

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export function analyze(
  u: University,
  student: StudentInput,
  scholarships: Scholarship[],
  universities: University[],
  fx: FxRates | null,
): DecisionAnalysis {
  const { program, matches } = pickProgram(u, student.subject);
  const view: University = program ? { ...u, costs: program.costs } : u;
  const rows = program?.admissionsByCurriculum ?? u.admissionsByCurriculum ?? [];

  // Academic + admissions evidence
  const academic = academicFit(rows, student);
  const now = today();
  const dated = (u.deadlines ?? []).filter((d) => d.deadline);
  const upcoming = dated
    .filter((d) => d.deadline!.slice(0, 10) >= now)
    .sort((a, b) => a.deadline!.localeCompare(b.deadline!));
  const published = rows.filter((r) => r.threshold && r.threshold.trim() !== "").length;
  const verified = /verified against/i.test(u.evidenceConfidence);
  const admissions = {
    level: (verified ? "strong" : published > 0 ? "edge" : "unknown") as Level,
    published,
    nextDeadline: upcoming[0]
      ? { label: upcoming[0].label, date: upcoming[0].deadline!.slice(0, 10) }
      : null,
    pastDeadlines: dated.length - upcoming.length,
    confidence: u.evidenceConfidence,
    sourceUrl: u.officialSourceUrl,
  };

  // Financial
  const cost = annualCostUsd(view, fx);
  const fit = budgetFit(cost, student.budgetUsd);
  const years = program?.durationYears || u.durationYears || 0;
  const code = citizenshipCode(student.citizenship);
  const tuitionUsd =
    view.costs.tuitionPerYear != null
      ? toUsd(view.costs.tuitionPerYear, view.costs.currency, fx)
      : null;
  const funding: FundingItem[] = scholarships
    .filter((s) => (s.universityIds ?? []).includes(u.id))
    .map((s) => ({ s, el: eligibility(s, code) }))
    .filter(({ el }) => el !== "no")
    .map(({ s, el }) => {
      const award = s.awardSummary ?? "See official source";
      const basis = s.selectionBasis ?? "check";
      const pct = basis === "guaranteed" && el === "yes" ? guaranteedPct(award) : null;
      return {
        name: s.name,
        award,
        basis,
        eligible: el === "yes" ? "yes" : "check",
        ...(s.applicationDeadline ? { deadline: s.applicationDeadline } : {}),
        annualUsd: pct != null && tuitionUsd != null ? Math.round((tuitionUsd * pct) / 100) : null,
        source: s.officialSource,
      } satisfies FundingItem;
    })
    .sort(
      (a, b) =>
        ["guaranteed", "competitive", "check"].indexOf(a.basis) -
        ["guaranteed", "competitive", "check"].indexOf(b.basis),
    );
  const guaranteedAnnualUsd = funding.reduce((sum, f) => sum + (f.annualUsd ?? 0), 0);
  const annualUsd = cost ? Math.round(cost.usd) : null;
  const degreeUsd = annualUsd != null && years ? annualUsd * years : null;
  const netDegreeUsd =
    degreeUsd != null ? Math.max(0, degreeUsd - guaranteedAnnualUsd * years) : null;
  const noLimit = student.budgetUsd >= BUDGET_MAX;
  const budgetDegreeUsd = noLimit || !years ? null : student.budgetUsd * years;
  const gapDegreeUsd =
    netDegreeUsd != null && budgetDegreeUsd != null ? netDegreeUsd - budgetDegreeUsd : null;
  const netFit: BudgetFit =
    gapDegreeUsd == null ? fit : gapDegreeUsd > 0 ? "over" : cost?.complete ? "within" : "unknown";
  const financial: FinancialFit = {
    level: netFit === "within" ? "strong" : netFit === "over" ? "gap" : "unknown",
    fit: netFit,
    annualUsd,
    annualComplete: !!cost?.complete,
    years,
    degreeUsd,
    guaranteedAnnualUsd,
    netDegreeUsd,
    budgetDegreeUsd,
    gapDegreeUsd,
    funding,
    currency: view.costs.currency,
    localAnnual: view.costs.totalAnnual ?? view.costs.tuitionPerYear,
    ...(view.costs.livingSource ? { livingSource: view.costs.livingSource } : {}),
  };

  // Alternatives: same subject, fits budget (or cheapest known), never this university.
  const alternatives: Alternative[] = universities
    .filter((o) => o.id !== u.id)
    .map((o) => {
      const p = pickProgram(o, student.subject);
      if (!p.matches.length || !p.program) return null;
      const c = annualCostUsd({ ...o, costs: p.program.costs }, fx);
      if (!c) return null;
      const language = teachingLanguage(p.program);
      return {
        id: o.id,
        name: o.name,
        flag: o.flag,
        program: p.program.name,
        annualUsd: Math.round(c.usd),
        fit: budgetFit(c, student.budgetUsd),
        complete: c.complete,
        ...(language ? { language } : {}),
      };
    })
    .filter((a): a is Alternative => !!a && a.fit !== "over")
    // English-taught first, then verified-total before tuition-only, then cheapest.
    .sort(
      (a, b) =>
        Number(!!a.language) - Number(!!b.language) ||
        Number(a.fit !== "within") - Number(b.fit !== "within") ||
        a.annualUsd - b.annualUsd,
    )
    .slice(0, 3);

  // Levers: concrete, controllable next steps derived from the gaps above.
  const levers: Lever[] = [];
  if (admissions.nextDeadline)
    levers.push({
      kind: "deadline",
      text: `Apply by ${fmtDate(admissions.nextDeadline.date)} (${admissions.nextDeadline.label}).`,
    });
  else if (admissions.pastDeadlines > 0)
    levers.push({
      kind: "deadline",
      text: "All published deadlines for this cycle have passed — plan for the next intake.",
    });
  const taughtIn = program ? teachingLanguage(program) : undefined;
  if (taughtIn)
    levers.push({
      kind: "language",
      text: `This programme is taught in ${taughtIn} — you'll need to prove ${taughtIn} proficiency to enrol.`,
    });
  if (academic.subjects.length)
    levers.push({
      kind: "academic",
      text: `Make sure your subjects include: ${academic.subjects.join(", ")}.`,
    });
  if (academic.level === "edge" || academic.level === "gap")
    levers.push({
      kind: "academic",
      text: "Your predicted grades are the biggest lever — target the published requirement, and keep a safer option on your list.",
    });
  if (academic.aLevelTermsOnly)
    levers.push({
      kind: "evidence",
      text: "Email admissions to ask for the requirement in your own curriculum before you apply.",
    });
  const lang = academic.requirement?.match(/IELTS[^.;]*?(\d\.\d)/i);
  if (lang)
    levers.push({
      kind: "language",
      text: `Book an English test early — IELTS ${lang[1]} is required.`,
    });
  const competitive = funding.filter((f) => f.basis !== "guaranteed");
  if (netFit === "over") {
    if (competitive.length)
      levers.push({
        kind: "funding",
        text: `Apply for ${competitive[0]!.name}${competitive[0]!.deadline ? ` by ${fmtDate(competitive[0]!.deadline)}` : ""} — it could narrow the gap.`,
      });
    if (alternatives[0])
      levers.push({
        kind: "budget",
        text: `Compare with ${alternatives[0].name} (≈ $${alternatives[0].annualUsd.toLocaleString()}/yr${alternatives[0].complete ? "" : " tuition only"} for ${alternatives[0].program}).`,
      });
  } else if (competitive.length) {
    levers.push({
      kind: "funding",
      text: `${competitive.length} scholarship${competitive.length > 1 ? "s" : ""} to check — start with ${competitive[0]!.name}.`,
    });
  }
  if (!cost?.complete)
    levers.push({
      kind: "evidence",
      text: "Living costs aren't fully published here — budget a margin until they are.",
    });

  return {
    program,
    programName: program?.name ?? u.programs[0] ?? "",
    ...(taughtIn ? { taughtIn } : {}),
    offersSubject: matches.length > 0,
    matchingPrograms: matches,
    academic,
    admissions,
    financial,
    alternatives,
    levers,
  };
}

export function fmtDate(iso: string): string {
  const d = new Date(`${iso.slice(0, 10)}T00:00:00Z`);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
        timeZone: "UTC",
      });
}

export function usd(n: number | null): string {
  return n == null ? "Not published" : `$${Math.round(n).toLocaleString()}`;
}
