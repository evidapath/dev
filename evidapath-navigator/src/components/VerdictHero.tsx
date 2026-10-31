import { Link } from "@tanstack/react-router";
import { ArrowRight, CalendarCheck } from "lucide-react";
import type { DecisionAnalysis } from "../lib/decision-engine";
import { BUDGET_MAX } from "../lib/budget";
import type { University } from "../lib/mock-data";
import { money, TONE_CLASS, verdictFor } from "../lib/verdict";
import { CostBar } from "./CostBar";

// The top of the Analyze page: the deal in one line, three numbers, one action.
export function VerdictHero({
  u,
  a,
  budgetUsd,
}: {
  u: University;
  a: DecisionAnalysis;
  budgetUsd: number;
}) {
  const noLimit = budgetUsd >= BUDGET_MAX;
  const v = verdictFor(a, budgetUsd, noLimit);
  const f = a.financial;
  const yrs = f.years || 1;
  const net = f.annualUsd != null ? Math.max(0, f.annualUsd - f.guaranteedAnnualUsd) : null;
  const diff = net != null && !noLimit ? net - budgetUsd : null;
  // The single most useful next step: a dated deadline, else the first lever.
  const next =
    a.levers.find((l) => l.kind === "deadline") ??
    a.levers.find((l) => l.kind === "funding") ??
    a.levers[0];

  const stat = (label: string, value: string, tone = "text-foreground") => (
    <div className="rounded-xl bg-secondary/50 p-3">
      <p className="text-[11px] text-muted-foreground">{label}</p>
      <p className={`font-mono font-bold text-lg ${tone}`}>{value}</p>
    </div>
  );

  return (
    <section className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-5 shadow-xs">
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">
          {u.flag} {u.name} · {a.programName.split(" (")[0]}
          {f.years ? ` · ${f.years} years` : ""}
          {a.feeTier ? ` · fee for ${a.feeTier.split(" (")[0]}` : ""}
        </p>
        <h2
          className={`text-2xl sm:text-3xl font-display font-extrabold leading-tight ${
            v.tone === "good"
              ? "text-primary"
              : v.tone === "bad"
                ? "text-destructive"
                : "text-bronze"
          }`}
        >
          {v.headline}
        </h2>
        <div className="flex flex-wrap gap-1.5">
          {v.tags.map((t) => (
            <span
              key={t.text}
              className={`text-xs font-medium px-2.5 py-0.5 rounded-full border ${TONE_CLASS[t.tone]}`}
            >
              {t.text}
            </span>
          ))}
        </div>
      </div>

      <CostBar
        cost={f.annualUsd}
        aid={f.guaranteedAnnualUsd}
        budget={budgetUsd}
        complete={f.annualComplete}
        noLimit={noLimit}
      />

      <div className="grid grid-cols-3 gap-2 sm:gap-3">
        {stat(f.annualComplete ? "Cost / year" : "Tuition / year", money(f.annualUsd))}
        {stat(
          "Guaranteed aid / yr",
          f.guaranteedAnnualUsd ? money(f.guaranteedAnnualUsd) : "$0",
          f.guaranteedAnnualUsd ? "text-sky-600" : "text-foreground",
        )}
        {diff == null
          ? stat("Whole degree", money(net != null ? net * yrs : null))
          : diff > 0
            ? stat(
                f.annualComplete ? "Short / year" : "Short / yr (min.)",
                money(diff),
                "text-bronze",
              )
            : stat("Left over / year", money(-diff), "text-primary")}
      </div>

      {next && (
        <div className="rounded-xl border border-primary/25 bg-primary/5 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-primary">
              Do this next
            </p>
            <p className="text-sm font-medium text-foreground">{next.text}</p>
          </div>
          <Link
            to="/plan"
            className="inline-flex items-center gap-1.5 h-9 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 shrink-0"
          >
            <CalendarCheck className="w-4 h-4" /> My plan <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </section>
  );
}
