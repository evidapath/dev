import { money } from "../lib/verdict";

// Cost vs budget at a glance: one bar per year of study.
//   green  = what your budget covers
//   blue   = guaranteed scholarship
//   amber  = still to find
// A dashed tick marks the budget. All figures are USD per year.
export function CostBar({
  cost,
  aid,
  budget,
  complete,
  noLimit,
  compact = false,
}: {
  cost: number | null;
  aid: number;
  budget: number;
  complete: boolean;
  noLimit: boolean;
  compact?: boolean;
}) {
  if (cost == null) return <p className="text-xs text-muted-foreground">Cost not published</p>;
  const net = Math.max(0, cost - aid);
  const covered = noLimit ? net : Math.min(net, budget);
  const short = noLimit ? 0 : Math.max(0, net - budget);
  const scale = Math.max(cost, noLimit ? 0 : budget) || 1;
  const pct = (n: number) => `${(n / scale) * 100}%`;

  return (
    <figure
      className="space-y-1"
      aria-label={`Cost ${money(cost)} per year against a budget of ${money(budget)}`}
    >
      <div
        className={`relative w-full rounded-full bg-secondary overflow-visible ${compact ? "h-2" : "h-3"}`}
      >
        <div
          className="absolute inset-y-0 left-0 flex rounded-full overflow-hidden"
          style={{ width: pct(cost) }}
        >
          <div className="bg-primary" style={{ width: `${(covered / cost) * 100}%` }} />
          {aid > 0 && (
            <div
              className="bg-sky-500"
              style={{ width: `${(Math.min(aid, cost) / cost) * 100}%` }}
            />
          )}
          {short > 0 && (
            <div
              className={`bg-bronze ${complete ? "" : "bg-[repeating-linear-gradient(45deg,var(--color-bronze)_0_4px,transparent_4px_8px)]"}`}
              style={{ width: `${(short / cost) * 100}%` }}
            />
          )}
        </div>
        {!noLimit && (
          <div
            className="absolute -top-1 -bottom-1 w-0.5 bg-foreground/70 rounded"
            style={{ left: `calc(${pct(budget)} - 1px)` }}
            aria-hidden
          />
        )}
      </div>
      {!compact && (
        <figcaption className="flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-muted-foreground">
          <span>
            <span className="inline-block w-2 h-2 rounded-full bg-primary mr-1" />
            {noLimit ? "Cost" : "Your budget covers"} {money(covered)}
          </span>
          {aid > 0 && (
            <span>
              <span className="inline-block w-2 h-2 rounded-full bg-sky-500 mr-1" />
              Guaranteed aid {money(aid)}
            </span>
          )}
          {short > 0 && (
            <span className="text-bronze font-medium">
              <span className="inline-block w-2 h-2 rounded-full bg-bronze mr-1" />
              Short {complete ? "" : "≥ "}
              {money(short)}
            </span>
          )}
          {!complete && <span>Tuition only — living cost not published</span>}
        </figcaption>
      )}
    </figure>
  );
}
