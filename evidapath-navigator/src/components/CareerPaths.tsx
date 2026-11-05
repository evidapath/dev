import { Link } from "@tanstack/react-router";
import { Briefcase, ExternalLink, GraduationCap } from "lucide-react";
import {
  CAREERS_CHECKED,
  CAREERS_SOURCE,
  careerUrl,
  careersFor,
  FAMILY_LABEL,
  type CareerFamily,
} from "../lib/careers";

const k = (n: number) => `£${Math.round(n / 1000)}k`;

/** Jobs a degree can lead to, with UK pay and the degrees each job takes. */
export function CareerPaths({
  family,
  limit,
  heading = true,
}: {
  family: CareerFamily | null;
  /** Show this many and link to /careers for the rest. */
  limit?: number;
  heading?: boolean;
}) {
  const all = careersFor(family);
  if (!family || all.length === 0) return null;
  const shown = limit ? all.slice(0, limit) : all;

  return (
    <section className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 shadow-xs">
      {heading && (
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 className="font-display font-bold text-lg text-foreground flex items-center gap-2">
            <Briefcase className="w-4 h-4 text-primary" />
            Where {/^[AEIOU]/.test(FAMILY_LABEL[family]) ? "an" : "a"} {FAMILY_LABEL[family]} degree
            can lead
          </h2>
          <span className="text-xs text-muted-foreground">
            {all.length} careers · UK pay, starter → experienced
          </span>
        </div>
      )}
      <ul className="grid gap-3 sm:grid-cols-2">
        {shown.map((c) => (
          <li
            key={c.slug}
            className="rounded-xl border border-border bg-background/60 p-4 space-y-1.5"
          >
            <div className="flex items-start justify-between gap-2">
              <a
                href={careerUrl(c)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-semibold text-foreground hover:text-primary inline-flex items-center gap-1"
              >
                {c.title}
                <ExternalLink className="w-3 h-3 opacity-60" />
              </a>
              <span className="shrink-0 text-xs font-mono font-semibold text-foreground">
                {k(c.salaryGbp[0])}–{k(c.salaryGbp[1])}
              </span>
            </div>
            <p className="text-xs text-muted-foreground">{c.summary}</p>
            <p className="text-[11px] text-muted-foreground flex gap-1.5">
              <GraduationCap className="w-3 h-3 mt-0.5 shrink-0" aria-label="Degrees" />
              <span>Degrees that lead in: {c.degrees}</span>
            </p>
            {c.note && <p className="text-[11px] text-bronze">{c.note}</p>}
          </li>
        ))}
      </ul>
      <div className="flex flex-wrap items-center justify-between gap-2 text-[11px] text-muted-foreground">
        <span>
          From the {CAREERS_SOURCE}, checked {CAREERS_CHECKED}. Typical paths, not promises; pay is
          for the UK and differs by country.
        </span>
        {limit && all.length > limit && (
          <Link
            to="/careers"
            search={{ subject: family }}
            className="text-primary font-semibold hover:underline"
          >
            See all {all.length} careers →
          </Link>
        )}
      </div>
    </section>
  );
}
