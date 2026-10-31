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
  // Blockers
  if (a.taughtIn) tags.push({ text: `Taught in ${a.taughtIn}`, tone: "bad" });
  if (!a.admissions.nextDeadline && a.admissions.pastDeadlines > 0)
    tags.push({ text: "Deadline passed", tone: "warn" });
  if (toApply > 0 && f.fit === "over")
    tags.push({ text: `${toApply} scholarship${toApply > 1 ? "s" : ""} to try`, tone: "neutral" });

  const bad = tags.some((t) => t.tone === "bad");
  const warn = tags.some((t) => t.tone === "warn");
  const tone: Tone = bad ? "bad" : warn ? "warn" : "good";

  let headline: string;
  if (a.taughtIn) headline = `Affordable, but you'd need ${a.taughtIn}`;
  else if (g.level === "gap") headline = "Your grades are below what they publish";
  else if (f.fit === "within" && (g.level === "strong" || g.level === "unknown"))
    headline = guaranteed ? "Fits your budget thanks to guaranteed aid" : "Fits your budget";
  else if (f.fit === "over" && gapYr != null)
    headline = toApply
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
