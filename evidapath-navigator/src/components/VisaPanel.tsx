import { BadgeCheck, Briefcase, ExternalLink, Plane, Wallet } from "lucide-react";
import { VISA_CHECKED, visaFor } from "../lib/visa";

/** Student visa money, work while studying and work after graduating, for one country. */
export function VisaPanel({ country }: { country: string }) {
  const v = visaFor(country);
  if (!v) return null;
  return (
    <section className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 shadow-xs">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-display font-bold text-lg text-foreground flex items-center gap-2">
          <Plane className="w-4 h-4 text-primary" />
          Visa & work in {v.country}
        </h2>
        <span className="text-xs text-muted-foreground">{v.visa}</span>
      </div>

      {v.money.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-xs font-semibold text-foreground flex items-center gap-1.5">
            <Wallet className="w-3.5 h-3.5 text-primary" /> Money for the visa
          </p>
          <dl className="grid gap-x-4 gap-y-1 sm:grid-cols-[max-content_1fr] text-xs">
            {v.money.map((m) => (
              <div key={m.label} className="contents">
                <dt className="text-muted-foreground">{m.label}</dt>
                <dd className="text-foreground font-medium">{m.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {(v.work || v.after) && (
        <div className="grid gap-3 sm:grid-cols-2">
          {v.work && (
            <div className="rounded-xl bg-secondary/50 p-3 text-xs space-y-1">
              <p className="font-semibold text-foreground flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5 text-primary" /> Working while you study
              </p>
              <p className="text-muted-foreground">{v.work}</p>
            </div>
          )}
          {v.after && (
            <div className="rounded-xl bg-secondary/50 p-3 text-xs space-y-1">
              <p className="font-semibold text-foreground flex items-center gap-1.5">
                <BadgeCheck className="w-3.5 h-3.5 text-primary" /> Staying to work after
              </p>
              <p className="text-muted-foreground">{v.after}</p>
            </div>
          )}
        </div>
      )}

      {v.note && <p className="text-xs text-bronze">{v.note}</p>}

      <div className="text-[11px] text-muted-foreground space-y-1">
        <p className="flex flex-wrap gap-x-3 gap-y-1">
          {v.sources.map((s) => (
            <a
              key={s.url}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline inline-flex items-center gap-0.5"
            >
              {s.label} <ExternalLink className="w-2.5 h-2.5" />
            </a>
          ))}
        </p>
        <p>
          From government pages, checked {VISA_CHECKED}. Rules change: check the official page
          before you apply.
        </p>
      </div>
    </section>
  );
}
