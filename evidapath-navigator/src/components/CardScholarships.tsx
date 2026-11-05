import { Link } from "@tanstack/react-router";
import { CalendarDays, GraduationCap, Sparkles, Users } from "lucide-react";
import { useEffect, useState } from "react";
import type { Scholarship } from "../lib/mock-data";
import { useScholarshipsFn } from "../lib/use-live-data";
import { awardHeadline } from "../lib/award-summary";
import { fmtDate } from "../lib/decision-engine";

const ISO = /^\d{4}-\d{2}-\d{2}/;
const PENDING = /^pending|not yet/i;

function who(s: Scholarship): string {
  const c = s.citizenshipEligible;
  if (!c || PENDING.test(c)) return "Check the official page";
  return /^all$/i.test(c.trim()) ? "All nationalities" : c;
}

/**
 * A university's scholarships on its card, right under the costs: a one-line
 * summary that opens to each award's amount, who can apply, grades and deadline.
 * Scholarships come from the shared (cached) scholarships request.
 */
export function CardScholarships({ uniId }: { uniId: string }) {
  const fetchSchols = useScholarshipsFn();
  const [list, setList] = useState<Scholarship[] | null>(null);
  useEffect(() => {
    let live = true;
    fetchSchols()
      .then((r) => live && setList(r.scholarships.filter((s) => s.universityIds?.includes(uniId))))
      .catch(() => live && setList([]));
    return () => {
      live = false;
    };
  }, [fetchSchols, uniId]);

  if (!list) return <div className="h-10 rounded-lg bg-secondary/50 animate-pulse" />;

  const today = new Date().toISOString().slice(0, 10);
  const upcoming = list
    .map((s) => s.applicationDeadline)
    .filter((d): d is string => !!d && ISO.test(d) && d.slice(0, 10) >= today)
    .sort()[0];
  const guaranteed = list.filter((s) => s.selectionBasis === "guaranteed").length;

  if (list.length === 0)
    return (
      <p className="rounded-lg border border-dashed border-border px-3 py-2 text-[11px] text-muted-foreground flex items-center gap-1.5">
        <Sparkles className="w-3 h-3 shrink-0" />
        No scholarships in our data for this university yet.
      </p>
    );

  return (
    <details className="group/sch rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 text-xs">
      <summary className="cursor-pointer select-none list-none flex items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 font-semibold text-foreground">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          {list.length} scholarship{list.length === 1 ? "" : "s"}
          {guaranteed ? ` · ${guaranteed} guaranteed` : ""}
          {upcoming ? (
            <span className="font-normal text-muted-foreground">
              · next deadline {fmtDate(upcoming)}
            </span>
          ) : null}
        </span>
        <span className="text-primary font-semibold shrink-0 group-open/sch:hidden">Show ↓</span>
        <span className="text-primary font-semibold shrink-0 hidden group-open/sch:inline">
          Hide ↑
        </span>
      </summary>
      <ul className="mt-2 space-y-2">
        {list.map((s) => {
          const head = awardHeadline(
            s.awardSummary ?? (s.awardValue != null ? String(s.awardValue) : undefined),
          );
          const d = s.applicationDeadline;
          const closed = d && ISO.test(d) && d.slice(0, 10) < today;
          return (
            <li key={s.id} className="rounded-md bg-card border border-border/70 p-2.5 space-y-1">
              <div className="flex items-start justify-between gap-2">
                <a
                  href={s.officialSource || undefined}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-semibold text-foreground hover:text-primary leading-snug"
                >
                  {s.name}
                </a>
                {head && (
                  <span className="shrink-0 text-[10px] font-semibold text-primary">
                    {head.value} {head.label}
                  </span>
                )}
              </div>
              <p className="flex gap-1.5 text-muted-foreground">
                <Users className="w-3 h-3 mt-0.5 shrink-0" aria-label="Who can apply" />
                <span className="line-clamp-2">{who(s)}</span>
              </p>
              {!PENDING.test(s.academicThreshold) && (
                <p className="flex gap-1.5 text-muted-foreground">
                  <GraduationCap className="w-3 h-3 mt-0.5 shrink-0" aria-label="Grades" />
                  <span className="line-clamp-2">{s.academicThreshold}</span>
                </p>
              )}
              <p className="flex gap-1.5 text-muted-foreground">
                <CalendarDays className="w-3 h-3 mt-0.5 shrink-0" aria-label="Deadline" />
                <span className={d && !closed ? "text-foreground font-medium" : ""}>
                  {d
                    ? `${closed ? "Closed this cycle · " : "Apply by "}${fmtDate(d)}`
                    : "Deadline not published"}
                </span>
              </p>
            </li>
          );
        })}
      </ul>
      <Link
        to="/scholarships"
        className="mt-2 inline-block text-primary font-semibold hover:underline"
      >
        All scholarships →
      </Link>
    </details>
  );
}
