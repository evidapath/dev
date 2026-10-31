import { analyze, type DecisionAnalysis, type StudentInput } from "./decision-engine";
import type { FxRates } from "./fx.functions";
import type { Scholarship, University } from "./mock-data";

// Groups Find My Path results the way a student reads them:
//   1. what I can afford (my country first, then elsewhere if needed)
//   2. strong matches for my profile that cost more — and how to close the gap
//   3. probably affordable, but not every cost is published
//   4. reach options (big gap, or grades below the published requirement)
// Built entirely on the decision engine, so every number is published data.

export type PathwayGroup = "within" | "stretch" | "unpriced" | "reach";

export interface PathwayRow {
  u: University;
  a: DecisionAnalysis;
  group: PathwayGroup;
  inRegion: boolean;
  /** USD per year still to find after guaranteed aid (> 0 only when over budget). */
  gapPerYear: number | null;
  /** Net yearly cost after guaranteed aid. */
  netAnnualUsd: number | null;
  issue: { text: string; tone: "ok" | "warn" | "bad" };
}

export interface PathwayResult {
  groups: Record<PathwayGroup, PathwayRow[]>;
  withinInRegion: number;
  withinElsewhere: number;
  regionLimited: boolean;
}

const FIT_RANK = { strong: 0, unknown: 1, edge: 2, gap: 3 } as const;
const OUTSIDE_REGION_LIMIT = 6;

function issueFor(
  a: DecisionAnalysis,
  gapPerYear: number | null,
  group: PathwayGroup,
): PathwayRow["issue"] {
  if (a.academic.level === "gap")
    return { text: "Grades below the published requirement", tone: "bad" };
  if (gapPerYear != null && gapPerYear > 0)
    return {
      text: `${a.financial.annualComplete ? "" : "At least "}≈ $${Math.round(gapPerYear).toLocaleString()}/yr over your budget`,
      tone: "warn",
    };
  if (a.taughtIn) return { text: `Taught in ${a.taughtIn}`, tone: "warn" };
  if (!a.admissions.nextDeadline && a.admissions.pastDeadlines > 0)
    return { text: "This year's deadlines have passed", tone: "warn" };
  if (a.academic.level === "edge")
    return { text: "Grades borderline for the published requirement", tone: "warn" };
  if (group === "unpriced")
    return { text: "Living costs not published — confirm before relying on it", tone: "warn" };
  if (a.academic.aLevelTermsOnly)
    return { text: "Ask for the requirement in your curriculum", tone: "warn" };
  return { text: "No blockers found in the published data", tone: "ok" };
}

export function buildPathways({
  universities,
  scholarships,
  fx,
  input,
  region,
}: {
  universities: University[];
  scholarships: Scholarship[];
  fx: FxRates | null;
  input: StudentInput;
  region: string;
}): PathwayResult {
  const anywhere = region === "Open to anywhere" || region === "All" || !region;
  const rows: PathwayRow[] = [];

  for (const u of universities) {
    const a = analyze(u, input, scholarships, universities, fx);
    if (!a.offersSubject) continue;
    const inRegion = anywhere || u.country === region;
    const f = a.financial;
    const netAnnualUsd =
      f.annualUsd != null ? Math.max(0, f.annualUsd - f.guaranteedAnnualUsd) : null;
    const gapPerYear = f.gapDegreeUsd != null && f.years ? f.gapDegreeUsd / f.years : null;

    let group: PathwayGroup;
    if (f.fit === "within") group = "within";
    else if (f.fit === "unknown") group = "unpriced";
    else
      group =
        a.academic.level === "gap" || (gapPerYear ?? 0) > input.budgetUsd ? "reach" : "stretch";

    // Outside the chosen country, only show what the student can (probably) afford.
    if (!inRegion && group !== "within" && group !== "unpriced") continue;
    rows.push({
      u,
      a,
      group,
      inRegion,
      gapPerYear,
      netAnnualUsd,
      issue: issueFor(a, gapPerYear, group),
    });
  }

  // English-taught first (most international students need it), then the best
  // academic fit, then the lowest net cost.
  const byFitThenCost = (x: PathwayRow, y: PathwayRow) =>
    Number(!!x.a.taughtIn) - Number(!!y.a.taughtIn) ||
    FIT_RANK[x.a.academic.level] - FIT_RANK[y.a.academic.level] ||
    (x.netAnnualUsd ?? Infinity) - (y.netAnnualUsd ?? Infinity);

  const withinIn = rows.filter((r) => r.group === "within" && r.inRegion).sort(byFitThenCost);
  const withinOut = rows
    .filter((r) => r.group === "within" && !r.inRegion)
    .sort(byFitThenCost)
    .slice(0, OUTSIDE_REGION_LIMIT);

  return {
    groups: {
      within: [...withinIn, ...withinOut],
      stretch: rows
        .filter((r) => r.group === "stretch")
        .sort((x, y) => (x.gapPerYear ?? 0) - (y.gapPerYear ?? 0) || byFitThenCost(x, y)),
      unpriced: [
        ...rows.filter((r) => r.group === "unpriced" && r.inRegion).sort(byFitThenCost),
        ...rows
          .filter((r) => r.group === "unpriced" && !r.inRegion && r.netAnnualUsd != null)
          .sort(byFitThenCost)
          .slice(0, 4),
      ],
      reach: rows
        .filter((r) => r.group === "reach")
        .sort((x, y) => (x.gapPerYear ?? 0) - (y.gapPerYear ?? 0)),
    },
    withinInRegion: withinIn.length,
    withinElsewhere: withinOut.length,
    regionLimited: !anywhere,
  };
}
