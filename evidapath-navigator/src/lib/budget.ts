import { toUsd, type FxRates } from "./fx.functions";
import type { University } from "./mock-data";

// Shared budget + subject matching so Find My Path, Discover and Browse all agree.

/** Budget sliders run from $20k to $90k; the top value means "no limit". */
export const BUDGET_MIN = 20000;
export const BUDGET_MAX = 90000;

export type BudgetFit = "within" | "unknown" | "over";

/**
 * Annual cost in USD for budget comparison. Uses the full annual total when it is
 * verified; otherwise tuition alone (a lower bound — if tuition already exceeds the
 * budget, the university is over budget). Null when the cost or rate is unknown.
 */
export function annualCostUsd(
  u: University,
  fx: FxRates | null,
): { usd: number; complete: boolean } | null {
  const total = u.costs.totalAnnual;
  const lower = total ?? u.costs.tuitionPerYear;
  if (lower == null || !u.costs.currency) return null;
  const usd = toUsd(lower, u.costs.currency, fx);
  return usd == null ? null : { usd, complete: total != null };
}

/** within = verified total fits; over = known cost exceeds; unknown = can't confirm. */
export function budgetFit(
  cost: { usd: number; complete: boolean } | null,
  budgetUsd: number,
): BudgetFit {
  const noLimit = !Number.isFinite(budgetUsd) || budgetUsd >= BUDGET_MAX;
  if (!cost) return "unknown";
  if (!noLimit && cost.usd > budgetUsd) return "over";
  return cost.complete ? "within" : "unknown";
}

export function matchesSubject(u: University, subject: string): boolean {
  const s = subject.trim().toLowerCase();
  if (s === "" || s === "any" || s.startsWith("undecided")) return true;
  const words = s.split(/[\s,/&]+/).filter((w) => w.length >= 3 && w !== "and");
  return u.programs.some((p) => {
    const name = p.toLowerCase();
    return name.includes(s) || (words.length > 0 && words.every((w) => name.includes(w)));
  });
}
