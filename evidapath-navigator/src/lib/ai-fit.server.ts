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

// Sonnet by default. Set AI_FIT_MODEL=claude-haiku-5-5 to use Haiku (cheaper; in
// tests on the same students it chose the same top picks, and every answer still
// goes through validate()). Any other value is ignored.
const MODELS = ["claude-sonnet-5-5", "claude-haiku-5-5"];
export const aiFitModel = (): string => {
  const m = process.env["AI_FIT_MODEL"];
  return m && MODELS.includes(m) ? m : MODELS[0]!;
};

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
  addComparisons(candidates, meta);
  return { student: studentFacts(s), candidates, meta };
}

// Positions across the whole list, worked out here so the model never has to
// (and can't get them wrong): how demanding each published requirement is among
// those the student's band meets, and how cheap each all-in cost is among those
// that fit the budget. The validator lets "highest"/"lowest" claims through only
// when they cite one of these facts.
function addComparisons(candidates: Candidate[], meta: Map<string, Meta>) {
  const ord = (n: number) => (n === 1 ? "1st" : n === 2 ? "2nd" : n === 3 ? "3rd" : `${n}th`);
  const factOf = (c: Candidate, kind: string) => c.facts.find((f) => f.kind === kind);
  const place = (
    rows: { c: Candidate; v: number }[],
    better: (a: number, b: number) => boolean,
    say: (pos: number, n: number, tied: boolean) => string,
  ) => {
    for (const r of rows) {
      const pos = 1 + rows.filter((o) => better(o.v, r.v)).length;
      const tied = rows.some((o) => o !== r && o.v === r.v);
      r.c.facts.push({
        id: `${r.c.university_id}:compare-${r.c.facts.filter((f) => f.kind === "comparison").length + 1}`,
        kind: "comparison",
        text: say(pos, rows.length, tied),
      });
    }
  };
  const meets = candidates
    .map((c) => ({
      c,
      v: Number(factOf(c, "selectivity")?.text.match(/(\d\.\d\d) on/)?.[1]),
      ok: /^Entry for [^:]*: Your band meets/.test(factOf(c, "entry")?.text ?? ""),
    }))
    .filter((x) => x.ok && Number.isFinite(x.v));
  const grades = (scope: string) => (pos: number, n: number, tied: boolean) =>
    `Compared across this list: of the ${n} programmes ${scope}, this one's published requirement is ${
      pos === 1
        ? `${tied ? "joint " : ""}the highest`
        : pos === n
          ? `${tied ? "joint " : ""}the lowest`
          : `${tied ? "joint " : ""}${ord(pos)} of ${n}, counting from the one that asks for the most`
    } (selectivity scale).`;
  if (meets.length > 1)
    place(meets, (a, b) => a > b, grades("whose published requirement your band meets"));
  const meetsInBudget = meets.filter((x) => !meta.get(x.c.university_id)?.overBudget);
  if (meetsInBudget.length > 1 && meetsInBudget.length < meets.length)
    place(
      meetsInBudget,
      (a, b) => a > b,
      grades("whose published requirement your band meets and that fit your budget"),
    );
  const costs = candidates
    .map((c) => ({ c, f: factOf(c, "cost") }))
    .filter((x) => x.f && /all-in/.test(x.f.text) && !meta.get(x.c.university_id)?.overBudget)
    .map((x) => ({ c: x.c, v: Number(x.f!.text.match(/\$([\d,]+)/)?.[1]?.replace(/,/g, "")) }))
    .filter((x) => Number.isFinite(x.v));
  const noLimit = candidates.some((c) => /No budget limit/.test(factOf(c, "budget")?.text ?? ""));
  if (costs.length > 1 && !noLimit)
    place(
      costs,
      (a, b) => a < b,
      (pos, n, tied) =>
        `Compared across this list: of the ${n} programmes with an all-in cost that fits your budget, this one's cost is ${
          pos === 1
            ? `${tied ? "joint " : ""}the lowest`
            : `${tied ? "joint " : ""}${ord(pos)} of ${n}, counting from the cheapest`
        }.`,
    );
}

/** "46 programmes match … 13 fit your budget …": counted from the facts. */
function codeSummary(pack: ReturnType<typeof buildPack>): CitedLine {
  const has = (re: RegExp, kind: string) =>
    pack.candidates.filter((c) => c.facts.some((f) => f.kind === kind && re.test(f.text)));
  const n = pack.candidates.length;
  const meets = has(/^Entry for [^:]*: Your band meets/, "entry");
  const fits = has(/^Fits/, "budget");
  const both = meets.filter((c) => fits.includes(c)).length;
  const noLimit = has(/No budget limit/, "budget").length > 0;
  const facts = pack.student.filter((f) => ["S:subject", "S:grades", "S:budget"].includes(f.id));
  const progs = (k: number) => `${k} programme${k === 1 ? "" : "s"}`;
  const text = noLimit
    ? `${progs(n)} here offer your subject (or a closely related one) in a language you study in. Your grade band meets the published requirement at ${meets.length} of them. You set no budget limit, so cost wasn't used to narrow them.`
    : `${progs(n)} here offer your subject (or a closely related one) in a language you study in. ${fits.length} fit your budget, your grade band meets the published requirement at ${meets.length}, and ${both} do both.`;
  return { text, facts };
}

// ─── Validation ────────────────────────────────────────────────────────────

const BANNED =
  /\b(rank\w*|top[- ]?ranked|top \d+|prestig\w*|reputation\w*|renowned|world[- ]class|elite|leading|famous|ivy league|russell group|best university|highly regarded|well[- ]known)\b/i;
const PREDICT =
  /\b(will get in|likely to (be admitted|get in)|good chance|guaranteed (a place|admission)|you('| a)re in)\b/i;
const SUPERLATIVE =
  /\b(highest|lowest|cheapest|smallest|largest|biggest|closest|most (?:selective|demanding|affordable)|least (?:selective|demanding|expensive))\b/i;
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

  // A pick's line may cite another university's selectivity or cost only to
  // compare, and only if the comparison is true: it must cite this university's
  // own fact of that kind, say one direction ("higher"/"more" or "lower"/"less"),
  // and that direction must hold against every other one cited. Costs compare only
  // like with like (all-in with all-in, tuition with tuition).
  const value = (f: Fact) =>
    f.kind === "selectivity"
      ? Number(f.text.match(/(\d\.\d\d) on/)?.[1])
      : Number(f.text.match(/\$([\d,]+)/)?.[1]?.replace(/,/g, ""));
  const scope = (f: Fact) => (f.kind === "cost" ? /all-in/.test(f.text) : true);
  const comparisonOk = (text: string, uni: string, facts: { fact: Fact; uni: string | null }[]) => {
    // "Highest" / "lowest" / "cheapest" claims come only from this university's own
    // "comparison" fact (worked out in code across the whole list), and the fact
    // must say that same extreme.
    if (SUPERLATIVE.test(text)) {
      const cmp = facts
        .filter((x) => x.uni === uni && x.fact.kind === "comparison")
        .map((x) => x.fact.text)
        .join(" ");
      if (!cmp || /\bclosest\b/i.test(text)) return false;
      if (/\b(highest|largest|biggest|most)\b/i.test(text) && !/\bhighest\b/.test(cmp))
        return false;
      if (/\b(lowest|cheapest|smallest|least)\b/i.test(text) && !/\blowest\b/.test(cmp))
        return false;
    }
    const others = facts.filter((x) => x.uni !== null && x.uni !== uni);
    // "cheaper than the US programmes" with nothing cited to compare against. "than
    // you(r)" and "than [the] 3.00 GPA" are fine: the number is checked separately.
    if (!others.length)
      return !/\bthan\b(?!\s+(?:you\b|your\b|(?:the\s+|a\s+)?[$£€]?\d))/i.test(text);
    const up = /\b(higher|more|greater|above)\b/i.test(text);
    const down = /\b(lower|less|fewer|below|cheaper)\b/i.test(text);
    if (up === down) return false;
    return others.every((o) => {
      if (o.fact.kind !== "selectivity" && o.fact.kind !== "cost") return false;
      const own = facts.find((x) => x.uni === uni && x.fact.kind === o.fact.kind);
      if (!own || scope(own.fact) !== scope(o.fact)) return false;
      const a = value(own.fact);
      const b = value(o.fact);
      return Number.isFinite(a) && Number.isFinite(b) && (up ? a > b : a < b);
    });
  };

  // One line is kept only if: it cites ≥1 known fact; every cited fact belongs to
  // this university (or the student), apart from a true comparison (above); it has
  // no banned or predicting words; and every number in it appears in one of the
  // cited facts.
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
      (anyUni || (uni !== null && comparisonOk(text, uni, facts))) &&
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
    picks?: unknown;
    data_gaps?: unknown;
  };
  // The summary is counted here, not written by the model: in tests a model's
  // summary mixed up two universities, and a summary can't be checked line by line.
  const summary = codeSummary(pack);
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
    if (!cand || seen.has(uid) || !catOk || !overallOk || (perCategory.get(cat) ?? 0) >= 2) {
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
      // A headline cites nothing, so it's shown only if it passes the same word,
      // number and comparison checks against this pick's own facts; else it's left out.
      headline:
        headline &&
        !BANNED.test(headline) &&
        !PREDICT.test(headline) &&
        !num(headline).length &&
        comparisonOk(
          headline,
          uid,
          cand.facts.map((fact) => ({ fact, uni: uid })),
        )
          ? headline
          : "",
      reasons,
      cautions,
    });
  }
  // A gap note must cite facts about one university (plus the student's), and is
  // checked like a pick's line for that university.
  const gaps = (Array.isArray(r.data_gaps) ? (r.data_gaps as RawLine[]) : [])
    .map((g) => {
      const ids = Array.isArray(g.fact_ids) ? g.fact_ids : [];
      const unis = new Set(
        ids.map((i) => (typeof i === "string" ? factIndex.get(i)?.uni : null)).filter(Boolean),
      );
      if (unis.size !== 1) {
        removed++;
        return null;
      }
      return line(g, [...unis][0] as string);
    })
    .filter((x): x is CitedLine => !!x);

  return { summary, picks, gaps, removed, model: aiFitModel(), candidates: pack.candidates.length };
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
    return { summary: null, picks: [], gaps: [], removed: 0, model: aiFitModel(), candidates: 0 };

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env["ANTHROPIC_API_KEY"] ?? "",
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: aiFitModel(),
      // Sonnet 5.5 thinks before answering (about 2,000-3,000 tokens in tests), so
      // leave room. It rejects `temperature` and a forced tool_choice; the prompt
      // tells it to call submit_fit, and a reply without the call shows nothing.
      max_tokens: 16000,
      system: AI_FIT_SYSTEM_PROMPT,
      tools: [AI_FIT_TOOL],
      tool_choice: { type: "auto" },
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
    signal: AbortSignal.timeout(120_000),
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
