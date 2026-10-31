import type { DecisionAnalysis } from "./decision-engine";

// One-glance verdicts. Same numbers as the detailed analysis, said in a line a
// student can read in two seconds. Detail stays one tap away.

/** $8,486 → "$8.5k", $120,000 → "$120k", $950 → "$950". */
export function money(n: number | null | undefined): string {
  if (n == null || !Number.isFinite(n)) return "—";
  const v = Math.abs(Math.round(n));
  if (v < 1000) return `$${v}`;
  const k = v / 1000;
  return `$${k >= 100 ? Math.round(k) : (Math.round(k * 10) / 10).toString()}k`;
}

export type Tone = "good" | "warn" | "bad" | "neutral";

export interface Tag {
  text: string;
  tone: Tone;
}

export interface Verdict {
  tone: Tone;
  headline: string;
  tags: Tag[];
}

export function verdictFor(a: DecisionAnalysis, budgetUsd: number, noLimit: boolean): Verdict {
  const f = a.financial;
  const yrs = f.years || 1;
  const gapYr = f.gapDegreeUsd != null ? f.gapDegreeUsd / yrs : null;
  const toApply = f.funding.filter((x) => x.basis !== "guaranteed").length;
  const guaranteed = f.guaranteedAnnualUsd > 0;
  // Small gaps are "within reach", not "over budget" (≤ 5% of budget or $1,000).
  const nearMiss =
    !noLimit && f.fit === "over" && gapYr != null && gapYr <= Math.max(1000, budgetUsd * 0.05);
  // Universities that promise to meet 100% of demonstrated financial need.
  const fullNeed = f.funding.some((x) =>
    /100% of demonstrated|full(?:y)? (?:demonstrated )?need|meets (?:100%|full)/i.test(
      `${x.name} ${x.award}`,
    ),
  );

  const tags: Tag[] = [];
  // Money
  if (noLimit) {
    if (f.annualUsd != null)
      tags.push({
        text: `${money(f.annualUsd)}/yr${f.annualComplete ? "" : " tuition"}`,
        tone: "neutral",
      });
  } else if (f.fit === "within")
    tags.push({
      text: guaranteed ? "Fits budget with guaranteed aid" : "Fits your budget",
      tone: "good",
    });
  else if (nearMiss) tags.push({ text: `Just ${money(gapYr)}/yr short`, tone: "warn" });
  else if (f.tuitionFree && f.fit === "over" && gapYr != null)
    tags.push({ text: `No tuition · ${money(gapYr)}/yr living short`, tone: "warn" });
  else if (f.fit === "over" && gapYr != null)
    tags.push({
      text: `${f.annualComplete ? "" : "≥ "}${money(gapYr)}/yr short`,
      tone: gapYr > budgetUsd ? "bad" : "warn",
    });
  else tags.push({ text: "Living cost unknown", tone: "warn" });
  // Grades
  const g = a.academic;
  if (g.level === "strong") tags.push({ text: "Meets grades", tone: "good" });
  else if (g.level === "edge") tags.push({ text: "Grades borderline", tone: "warn" });
  else if (g.level === "gap") tags.push({ text: "Grades below", tone: "bad" });
  else if (g.aLevelTermsOnly) tags.push({ text: "Ask for your grade equivalent", tone: "neutral" });
  else tags.push({ text: "Holistic review", tone: "neutral" });
  // Blockers and boosts
  if (a.taughtIn) tags.push({ text: `Needs ${a.taughtIn}`, tone: "bad" });
  if (!a.admissions.nextDeadline && a.admissions.pastDeadlines > 0)
    tags.push({ text: "Deadline passed", tone: "warn" });
  if (a.levers.some((l) => /government study-abroad scholarships/.test(l.text)))
    tags.push({ text: "UAE government scholarships", tone: "neutral" });
  if (fullNeed && f.fit === "over") tags.push({ text: "Meets full financial need", tone: "good" });
  else if (toApply > 0 && f.fit === "over")
    tags.push({ text: `${toApply} scholarship${toApply > 1 ? "s" : ""} to try`, tone: "neutral" });

  const bad = tags.some((t) => t.tone === "bad");
  const warn = tags.some((t) => t.tone === "warn");
  const tone: Tone = bad ? "bad" : warn ? "warn" : "good";

  let headline: string;
  if (a.taughtIn)
    headline =
      f.fit === "within" ? `Affordable, but you'd need ${a.taughtIn}` : `Taught in ${a.taughtIn}`;
  else if (g.level === "gap") headline = "Your grades are below what they publish";
  else if (f.fit === "within" && (g.level === "strong" || g.level === "unknown"))
    headline = noLimit
      ? g.level === "strong"
        ? "Your grades meet their requirement"
        : "Holistic admissions — strong preparation matters"
      : guaranteed
        ? "Fits your budget thanks to guaranteed aid"
        : "Fits your budget";
  else if (f.fit === "within") headline = "Fits your budget — grades borderline";
  else if (nearMiss) headline = `Just within reach — ${money(gapYr)}/yr short`;
  else if (f.tuitionFree && f.fit === "over" && gapYr != null)
    headline = `No tuition for you — ${money(gapYr)}/yr short on living costs (less if you live at home)`;
  else if (f.fit === "over" && gapYr != null)
    headline = fullNeed
      ? `${money(gapYr)}/yr short on paper — but they meet full financial need`
      : guaranteed
        ? `${money(gapYr)}/yr short even after your guaranteed scholarship`
        : toApply
          ? `${money(gapYr)}/yr short — scholarships could help`
          : `${money(gapYr)}/yr short — no scholarship found yet`;
  else if (f.fit === "unknown") headline = "Tuition fits — check living costs";
  else headline = "Worth a look";

  return { tone, headline, tags };
}

export const TONE_CLASS: Record<Tone, string> = {
  good: "text-primary bg-primary/10 border-primary/25",
  warn: "text-bronze bg-bronze/10 border-bronze/25",
  bad: "text-destructive bg-destructive/10 border-destructive/20",
  neutral: "text-muted-foreground bg-secondary border-border",
};
