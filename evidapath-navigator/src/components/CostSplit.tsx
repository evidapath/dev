import { money } from "../lib/verdict";

// Where a year's money goes: tuition, fees, living — one stacked bar, then the
// amounts. Guaranteed aid is shown coming off the top. USD per year.
const PARTS = [
  { key: "tuition", label: "Tuition", cls: "bg-navy dark:bg-sky-400" },
  { key: "fees", label: "Fees", cls: "bg-bronze" },
  { key: "living", label: "Living & other", cls: "bg-primary" },
] as const;

export function CostSplit({
  split,
  aid,
  budget,
  noLimit,
}: {
  split: { tuition: number; fees: number; living: number };
  aid: number;
  budget: number;
  noLimit: boolean;
}) {
  const total = split.tuition + split.fees + split.living;
  if (total <= 0) return null;
  const scale = Math.max(total, noLimit ? 0 : budget);
  const pct = (n: number) => `${(n / scale) * 100}%`;
  const net = Math.max(0, total - aid);

  return (
    <figure className="space-y-2" aria-label={`Yearly cost ${money(total)}`}>
      <div className="flex items-baseline justify-between gap-2">
        <figcaption className="text-[10px] uppercase font-semibold text-muted-foreground">
          Where {money(total)} a year goes
        </figcaption>
        {!noLimit && (
          <span
            className={`text-[11px] font-semibold ${net > budget ? "text-bronze" : "text-primary"}`}
          >
            {net > budget
              ? `${money(net - budget)} over your ${money(budget)}`
              : `${money(budget - net)} under your ${money(budget)}`}
          </span>
        )}
      </div>
      <div className="relative h-4 w-full rounded-md bg-secondary">
        <div
          className="absolute inset-y-0 left-0 flex overflow-hidden rounded-md"
          style={{ width: pct(total) }}
        >
          {PARTS.map((p) =>
            split[p.key] > 0 ? (
              <div
                key={p.key}
                className={p.cls}
                style={{ width: `${(split[p.key] / total) * 100}%` }}
                title={`${p.label} ${money(split[p.key])}`}
              />
            ) : null,
          )}
        </div>
        {!noLimit && (
          <div
            className="absolute -top-1 -bottom-1 w-0.5 rounded bg-foreground/70"
            style={{ left: `calc(${pct(budget)} - 1px)` }}
            aria-hidden
          />
        )}
      </div>
      <div className="grid grid-cols-3 gap-1.5">
        {PARTS.map((p) => (
          <div key={p.key} className="rounded-md bg-background border border-border px-2 py-1.5">
            <p className="flex items-center gap-1 text-[10px] text-muted-foreground">
              <span className={`inline-block w-2 h-2 rounded-sm ${p.cls}`} />
              {p.label}
            </p>
            <p className="font-mono text-xs font-semibold text-foreground">
              {split[p.key] > 0 ? money(split[p.key]) : p.key === "tuition" ? "Free" : "—"}
            </p>
          </div>
        ))}
      </div>
      {aid > 0 && (
        <p className="text-[11px] text-sky-600 dark:text-sky-400 font-medium">
          − {money(aid)} guaranteed scholarship → you pay {money(net)} a year
        </p>
      )}
    </figure>
  );
}
