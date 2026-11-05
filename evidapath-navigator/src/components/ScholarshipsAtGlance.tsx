import { Link } from "@tanstack/react-router";
import { CalendarDays, GraduationCap, Sparkles, Users } from "lucide-react";
import { useState } from "react";
import { fmtDate, type DecisionAnalysis } from "../lib/decision-engine";
import { checkedLabel } from "../lib/dates";

const ISO = /^\d{4}-\d{2}-\d{2}/;
const SHOW = 4;

/**
 * The university's scholarships you could apply for, near the top of Analyse:
 * amount, who can apply, grades and deadline, each from the official page.
 */
export function ScholarshipsAtGlance({ a, uniName }: { a: DecisionAnalysis; uniName: string }) {
  const [all, setAll] = useState(false);
  const today = new Date().toISOString().slice(0, 10);
  // Open ones first (dated soonest first), then undated, then ones closed this cycle.
  // Open dated ones first (soonest first), then worded deadlines, then none, then closed.
  const rank = (d?: string) => (!d ? 2 : !ISO.test(d) ? 1 : d.slice(0, 10) < today ? 3 : 0);
  const list = [...a.financial.funding].sort(
    (x, y) =>
      rank(x.deadline) - rank(y.deadline) || (x.deadline ?? "").localeCompare(y.deadline ?? ""),
  );
  const shown = all ? list : list.slice(0, SHOW);

  return (
    <section
      id="scholarships"
      className="scroll-mt-24 rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 shadow-xs"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display font-bold text-lg text-foreground flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          Scholarships at {uniName}
        </h2>
        <span className="text-xs text-muted-foreground">
          {list.length
            ? `${list.length} you could apply for · from official pages`
            : "None found for you yet"}
        </span>
      </div>

      {list.length === 0 ? (
        <p className="text-sm text-muted-foreground">
          No scholarship you're eligible for is in our data for this university yet.{" "}
          <Link to="/scholarships" className="text-primary font-semibold hover:underline">
            Browse all scholarships
          </Link>
        </p>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {shown.map((s) => {
            const dated = s.deadline && ISO.test(s.deadline);
            const closed = dated && s.deadline!.slice(0, 10) < today;
            return (
              <li
                key={s.name}
                className={`rounded-xl border border-border bg-background/60 p-4 space-y-2 ${closed ? "opacity-70" : ""}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <a
                    href={s.source || undefined}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-foreground hover:text-primary leading-snug"
                  >
                    {s.name}
                  </a>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full border shrink-0 font-semibold ${
                      s.basis === "guaranteed"
                        ? "bg-primary/10 text-primary border-primary/25"
                        : "bg-secondary text-muted-foreground border-border"
                    }`}
                  >
                    {s.basis === "guaranteed"
                      ? "Guaranteed"
                      : s.basis === "competitive"
                        ? "Competitive"
                        : "Check criteria"}
                  </span>
                </div>
                <p className="text-xs text-foreground line-clamp-2">{s.award}</p>
                <dl className="text-xs text-muted-foreground space-y-1">
                  <div className="flex gap-1.5">
                    <dt className="shrink-0 pt-px">
                      <Users className="w-3.5 h-3.5" aria-label="Who can apply" />
                    </dt>
                    <dd className="line-clamp-2">
                      {s.eligible === "yes" ? (
                        <span className="text-primary font-medium">Open to you</span>
                      ) : (
                        <span className="text-bronze font-medium">Check your citizenship</span>
                      )}
                      {s.who ? ` · ${/^all$/i.test(s.who) ? "All nationalities" : s.who}` : ""}
                    </dd>
                  </div>
                  {s.grades && (
                    <div className="flex gap-1.5">
                      <dt className="shrink-0 pt-px">
                        <GraduationCap className="w-3.5 h-3.5" aria-label="Grades" />
                      </dt>
                      <dd className="line-clamp-2">{s.grades}</dd>
                    </div>
                  )}
                  <div className="flex gap-1.5">
                    <dt className="shrink-0 pt-px">
                      <CalendarDays className="w-3.5 h-3.5" aria-label="Deadline" />
                    </dt>
                    <dd>
                      {s.deadline ? (
                        <span className={closed ? "" : "text-foreground font-medium"}>
                          {closed ? "Closed this cycle · " : "Apply by "}
                          {fmtDate(s.deadline)}
                        </span>
                      ) : (
                        "Deadline not published — check the official page"
                      )}
                    </dd>
                  </div>
                </dl>
                {(s.checked || s.source) && (
                  <p className="text-[10px] text-muted-foreground flex flex-wrap gap-x-2">
                    {s.checked && <span>{checkedLabel(s.checked)}</span>}
                    {s.source && (
                      <a
                        href={s.source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary font-semibold hover:underline"
                      >
                        Official page ↗
                      </a>
                    )}
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}

      {list.length > SHOW && (
        <button
          onClick={() => setAll(!all)}
          className="text-sm font-semibold text-primary hover:underline"
        >
          {all ? "Show fewer" : `Show all ${list.length} scholarships`}
        </button>
      )}
    </section>
  );
}
