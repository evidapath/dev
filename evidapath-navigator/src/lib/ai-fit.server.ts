// EXPERIMENTAL (AI fit). Server-only. Builds the fact pack for one student from
// EvidaPath's checked data, asks Claude to choose the best-fitting programmes using
// only those facts, then validates every sentence it returns in code. Anything
// that can't be traced to a cited fact is removed before a student sees it.
//
// Off for everyone except the emails in AI_FIT_ALLOWLIST. Needs ANTHROPIC_API_KEY.

import { analyze, type DecisionAnalysis, type StudentInput } from "./decision-engine";
import { loadFxRates } from "./fx.functions";
import { getScholarshipsFromSanity, getUniversitiesFromSanity } from "./sanity.server";
import { getSupabaseServerClient } from "./supabase.server";
import { BUDGET_MAX } from "./budget";
import { evidenceFor } from "./fit-evidence";
import { visaFor } from "./visa";
import type { University } from "./mock-data";
import { AI_FIT_RULES_REMINDER, AI_FIT_SYSTEM_PROMPT, AI_FIT_TOOL } from "./ai-fit.prompt";

export const AI_FIT_MODEL = "claude-sonnet-5-5";

// ─── Access ────────────────────────────────────────────────────────────────

function allowlist(): Set<string> {
  return new Set(
    (process.env["AI_FIT_ALLOWLIST"] ?? "")
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean),
  );
}

/** The signed-in user's id and email, if they're on the allow-list and the key is set. */
export async function aiFitUser(): Promise<{ id: string; email: string } | null> {
  if (!process.env["ANTHROPIC_API_KEY"]) return null;
  const sb = getSupabaseServerClient();
  const {
    data: { user },
  } = await sb.auth.getUser();
  const email = user?.email?.toLowerCase();
  if (!user || !email || !allowlist().has(email)) return null;
  return { id: user.id, email };
}

// ─── Facts ─────────────────────────────────────────────────────────────────

export interface Fact {
  id: string;
  kind: string;
  text: string;
  source?: string;
}

interface Candidate {
  university_id: string;
  name: string;
  country: string;
  programme: string;
  facts: Fact[];
}

interface Meta {
  overBudget: boolean;
  belowGrades: boolean;
}

const usd = (n: number) => `$${Math.round(n).toLocaleString("en-US")}`;

function studentFacts(s: StudentInput): Fact[] {
  const noLimit = s.budgetUsd >= BUDGET_MAX;
  return [
    { id: "S:curriculum", kind: "student", text: `Curriculum: ${s.curriculum}.` },
    { id: "S:grades", kind: "student", text: `Predicted or current grade band: ${s.gradeBand}.` },
    { id: "S:subject", kind: "student", text: `Wants to study: ${s.subject}.` },
    {
      id: "S:budget",
      kind: "student",
      text: noLimit
        ? "Budget: no upper limit set."
        : `Budget: ${usd(s.budgetUsd)} a year for everything (tuition, fees and living costs).`,
    },
    {
      id: "S:citizenship",
      kind: "student",
      text: `Citizenship: ${s.citizenship || "not given"}.`,
    },
    {
      id: "S:languages",
      kind: "student",
      text: `Can study in: ${(s.languages?.length ? s.languages : ["en"]).join(", ")} (ISO codes).`,
    },
  ];
}

function candidateFacts(
  u: University,
  a: DecisionAnalysis,
  s: StudentInput,
): { facts: Fact[]; meta: Meta } {
  const id = (k: string) => `${u.id}:${k}`;
  const f = a.financial;
  const facts: Fact[] = [];
  const noLimit = s.budgetUsd >= BUDGET_MAX;

  facts.push({
    id: id("programme"),
    kind: "programme",
    text: `Programme: ${a.programName}${f.years ? `, ${f.years} years` : ""}.`,
  });
  if (a.taughtIn)
    facts.push({ id: id("language"), kind: "language", text: `Taught in ${a.taughtIn}.` });
  if (a.feeTier)
    facts.push({
      id: id("fee-tier"),
      kind: "cost",
      text: `Fee rate used for this student: ${a.feeTier}.`,
    });

  // Cost and budget
  let overBudget = false;
  if (f.annualUsd == null) {
    facts.push({
      id: id("cost"),
      kind: "cost",
      text: "Cost per year: not published, so it can't be compared with the budget.",
    });
  } else {
    const scope = f.annualComplete
      ? "all-in (tuition, fees and living)"
      : "tuition only (living cost not published)";
    facts.push({
      id: id("cost"),
      kind: "cost",
      text: `Cost per year, ${scope}: ${usd(f.annualUsd)} (converted to US dollars at official rates).`,
      source: u.officialSourceUrl,
    });
    const net = f.annualUsd - f.guaranteedAnnualUsd;
    if (f.guaranteedAnnualUsd > 0)
      facts.push({
        id: id("aid"),
        kind: "scholarship",
        text: `Guaranteed scholarship for this student: ${usd(f.guaranteedAnnualUsd)} a year, leaving ${usd(net)} a year.`,
      });
    if (noLimit) {
      facts.push({
        id: id("budget"),
        kind: "budget",
        text: "No budget limit set, so cost wasn't compared.",
      });
    } else if (net <= s.budgetUsd) {
      facts.push({
        id: id("budget"),
        kind: "budget",
        text: `Fits the student's budget: ${usd(net)} a year against a ${usd(s.budgetUsd)} budget${f.annualComplete ? "" : " (tuition only; living costs would be extra)"}.`,
      });
    } else {
      overBudget = true;
      facts.push({
        id: id("budget"),
        kind: "budget",
        text: `Over the student's budget by ${usd(net - s.budgetUsd)} a year (${usd(net)} against ${usd(s.budgetUsd)}).`,
      });
    }
  }

  // Entry requirement and selectivity
  const ac = a.academic;
  facts.push({
    id: id("entry"),
    kind: "entry",
    text: `Entry for ${ac.curriculumLabel ?? "this student's curriculum"}: ${ac.headline}.${
      ac.requirement
        ? ` Published requirement: ${ac.requirement}`
        : " No requirement published for this curriculum."
    }`,
    source: a.admissions.sourceUrl,
  });
  if (ac.reqLevel != null)
    facts.push({
      id: id("selectivity"),
      kind: "selectivity",
      text: `Selectivity of the published requirement: ${ac.reqLevel.toFixed(2)} on EvidaPath's 0 to 1 scale (higher asks for higher grades). Not a quality measure.`,
    });
  if (ac.subjects.length)
    facts.push({
      id: id("subjects"),
      kind: "entry",
      text: `Required subjects: ${ac.subjects.join(", ")}.`,
    });

  // English test
  if (a.program?.english)
    facts.push({
      id: id("english"),
      kind: "english",
      text: `English requirement: ${a.program.english}`,
    });

  // Deadline
  if (a.admissions.nextDeadline)
    facts.push({
      id: id("deadline"),
      kind: "deadline",
      text: `Next application deadline: ${a.admissions.nextDeadline.date} (${a.admissions.nextDeadline.label}).`,
    });

  // Scholarships the student may be eligible for
  a.financial.funding.slice(0, 4).forEach((x, i) =>
    facts.push({
      id: id(`sch${i + 1}`),
      kind: "scholarship",
      text: `Scholarship: ${x.name}. ${x.basis === "guaranteed" ? "Guaranteed if eligible" : x.basis === "competitive" ? "Competitive" : "Criteria to check"}. Award: ${x.award}.${x.eligible === "check" ? " Citizenship eligibility needs checking." : ""}${x.deadline ? ` Deadline: ${x.deadline}.` : ""}`,
      ...(x.source ? { source: x.source } : {}),
    }),
  );

  // Visa and work
  const v = visaFor(u.country);
  const money = v?.money.find((m) => /money to show/i.test(m.label));
  if (money)
    facts.push({
      id: id("visa"),
      kind: "visa",
      text: `Visa money to show: ${money.value}.`,
      ...(v!.sources[0] ? { source: v!.sources[0].url } : {}),
    });
  if (v?.after)
    facts.push({
      id: id("work-after"),
      kind: "visa",
      text: `After graduating: ${v.after}`,
      ...(v.sources.at(-1) ? { source: v.sources.at(-1)!.url } : {}),
    });

  // Subject-level accreditation evidence
  for (const e of evidenceFor(u.id, a.program?.name))
    facts.push({
      id: `ev:${e.id}`,
      kind: "accreditation",
      text: `${e.body} (${e.scope === "school" ? "school or faculty level" : "this programme"}): ${e.statement} Checked ${e.checked}.`,
      source: e.source,
    });

  return { facts, meta: { overBudget, belowGrades: ac.level === "gap" } };
}

function buildPack(
  s: StudentInput,
  unis: University[],
  data: { scholarships: Parameters<typeof analyze>[2]; fx: Parameters<typeof analyze>[4] },
) {
  const langs = new Set(s.languages?.length ? s.languages : ["en"]);
  const candidates: Candidate[] = [];
  const meta = new Map<string, Meta>();
  for (const u of unis) {
    const a = analyze(u, s, data.scholarships, unis, data.fx);
    if (!a.offersSubject || !a.program) continue;
    const taught = a.program.languages?.length ? a.program.languages : ["en"];
    if (!taught.some((l) => langs.has(l))) continue;
    const { facts, meta: m } = candidateFacts(u, a, s);
    candidates.push({
      university_id: u.id,
      name: u.name,
      country: u.country,
      programme: a.programName,
      facts,
    });
    meta.set(u.id, m);
  }
  return { student: studentFacts(s), candidates, meta };
}

// ─── Validation ────────────────────────────────────────────────────────────

const BANNED =
  /\b(rank\w*|top[- ]?ranked|top \d+|prestig\w*|reputation\w*|renowned|world[- ]class|elite|leading|famous|ivy league|russell group|best university|highly regarded|well[- ]known)\b/i;
const PREDICT =
  /\b(will get in|likely to (be admitted|get in)|good chance|guaranteed (a place|admission)|you('| a)re in)\b/i;
const num = (s: string) => (s.match(/\d[\d,]*(?:\.\d+)?/g) ?? []).map((n) => n.replace(/,/g, ""));

export interface CitedLine {
  text: string;
  facts: Fact[];
}
export interface FitPick {
  university_id: string;
  name: string;
  country: string;
  programme: string;
  category: string;
  headline: string;
  reasons: CitedLine[];
  cautions: CitedLine[];
}
export interface FitResult {
  summary: CitedLine | null;
  picks: FitPick[];
  gaps: CitedLine[];
  removed: number;
  model: string;
  candidates: number;
}

interface RawLine {
  text?: unknown;
  fact_ids?: unknown;
}

function validate(raw: unknown, pack: ReturnType<typeof buildPack>): FitResult {
  const factIndex = new Map<string, { fact: Fact; uni: string | null }>();
  for (const f of pack.student) factIndex.set(f.id, { fact: f, uni: null });
  for (const c of pack.candidates)
    for (const f of c.facts) factIndex.set(f.id, { fact: f, uni: c.university_id });
  let removed = 0;

  // One line is kept only if: it cites ≥1 known fact; every cited fact belongs to
  // this university (or the student); it has no banned or predicting words; and
  // every number in it appears in one of the cited facts.
  const line = (l: RawLine, uni: string | null, anyUni = false): CitedLine | null => {
    const text = typeof l.text === "string" ? l.text.trim() : "";
    const ids = Array.isArray(l.fact_ids)
      ? l.fact_ids.filter((x): x is string => typeof x === "string")
      : [];
    const facts = ids
      .map((i) => factIndex.get(i))
      .filter((x): x is { fact: Fact; uni: string | null } => !!x);
    const ok =
      text.length > 0 &&
      facts.length > 0 &&
      facts.length === ids.length &&
      facts.every((x) => anyUni || x.uni === null || x.uni === uni) &&
      !BANNED.test(text) &&
      !PREDICT.test(text) &&
      num(text).every((n) => facts.some((x) => num(x.fact.text).includes(n)));
    if (!ok) {
      removed++;
      return null;
    }
    return { text, facts: facts.map((x) => x.fact) };
  };

  const r = (raw ?? {}) as {
    summary?: unknown;
    summary_fact_ids?: unknown;
    picks?: unknown;
    data_gaps?: unknown;
  };
  const summary = line({ text: r.summary, fact_ids: r.summary_fact_ids }, null, true);
  const seen = new Set<string>();
  const perCategory = new Map<string, number>();
  const picks: FitPick[] = [];
  type RawPick = {
    university_id?: unknown;
    category?: unknown;
    headline?: unknown;
    reasons?: unknown;
    cautions?: unknown;
  };
  for (const p of Array.isArray(r.picks) ? (r.picks as RawPick[]) : []) {
    const uid = typeof p.university_id === "string" ? p.university_id : "";
    const cand = pack.candidates.find((c) => c.university_id === uid);
    const cat = typeof p.category === "string" ? p.category : "";
    const headline = typeof p.headline === "string" ? p.headline.trim() : "";
    const m = pack.meta.get(uid);
    const catOk = [
      "best_overall_fit",
      "strongest_academic_match",
      "best_value",
      "worth_a_stretch",
      "safer_option",
    ].includes(cat);
    const overallOk = cat !== "best_overall_fit" || (m && !m.overBudget && !m.belowGrades);
    if (
      !cand ||
      seen.has(uid) ||
      !catOk ||
      !overallOk ||
      (perCategory.get(cat) ?? 0) >= 2 ||
      BANNED.test(headline) ||
      num(headline).length
    ) {
      removed++;
      continue;
    }
    const reasons = (Array.isArray(p.reasons) ? (p.reasons as RawLine[]) : [])
      .map((x) => line(x, uid))
      .filter((x): x is CitedLine => !!x);
    const cautions = (Array.isArray(p.cautions) ? (p.cautions as RawLine[]) : [])
      .map((x) => line(x, uid))
      .filter((x): x is CitedLine => !!x);
    // A stretch pick must say why it's a stretch; every pick needs a surviving reason.
    if (!reasons.length || (cat === "worth_a_stretch" && !cautions.length)) {
      removed++;
      continue;
    }
    seen.add(uid);
    perCategory.set(cat, (perCategory.get(cat) ?? 0) + 1);
    picks.push({
      university_id: uid,
      name: cand.name,
      country: cand.country,
      programme: cand.programme,
      category: cat,
      headline,
      reasons,
      cautions,
    });
  }
  const gaps = (Array.isArray(r.data_gaps) ? (r.data_gaps as RawLine[]) : [])
    .map((g) => {
      const ids = Array.isArray(g.fact_ids) ? g.fact_ids : [];
      return ids.length
        ? line(g, null, true)
        : typeof g.text === "string" && !BANNED.test(g.text) && !num(g.text).length
          ? { text: g.text, facts: [] }
          : null;
    })
    .filter((x): x is CitedLine => !!x);

  return { summary, picks, gaps, removed, model: AI_FIT_MODEL, candidates: pack.candidates.length };
}

// ─── The call ──────────────────────────────────────────────────────────────

const lastRun = new Map<string, number>();

export async function runAiFit(userId: string, s: StudentInput): Promise<FitResult> {
  const now = Date.now();
  if (now - (lastRun.get(userId) ?? 0) < 15_000)
    throw new Error("Please wait a few seconds before trying again.");
  lastRun.set(userId, now);

  const [unis, scholarships, fx] = await Promise.all([
    getUniversitiesFromSanity(),
    getScholarshipsFromSanity(),
    loadFxRates(),
  ]);
  const pack = buildPack(s, unis, { scholarships, fx });
  if (!pack.candidates.length)
    return { summary: null, picks: [], gaps: [], removed: 0, model: AI_FIT_MODEL, candidates: 0 };

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env["ANTHROPIC_API_KEY"] ?? "",
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: AI_FIT_MODEL,
      max_tokens: 4000,
      temperature: 0,
      system: AI_FIT_SYSTEM_PROMPT,
      tools: [AI_FIT_TOOL],
      tool_choice: { type: "tool", name: AI_FIT_TOOL.name },
      messages: [
        {
          role: "user",
          content: JSON.stringify({
            student: pack.student,
            candidates: pack.candidates,
            rules: AI_FIT_RULES_REMINDER,
          }),
        },
      ],
    }),
    signal: AbortSignal.timeout(90_000),
  });
  if (!res.ok) {
    // Status only: never log the request (it has the student's answers) or the key.
    console.error("[ai-fit] Claude API error:", res.status);
    throw new Error("The AI service didn't respond. Please try again.");
  }
  const body = (await res.json()) as {
    content?: { type: string; name?: string; input?: unknown }[];
  };
  const call = body.content?.find((c) => c.type === "tool_use" && c.name === AI_FIT_TOOL.name);
  const result = validate(call?.input, pack);
  console.info(
    "[ai-fit] picks:",
    result.picks.length,
    "removed:",
    result.removed,
    "candidates:",
    result.candidates,
  );
  return result;
}

export { buildPack as _buildPackForTests, validate as _validateForTests };
