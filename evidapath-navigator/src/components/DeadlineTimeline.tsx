import { fmtDate } from "../lib/decision-engine";

// A horizontal timeline of dated deadlines from today, month ticks along the
// bottom, one dot per deadline. Dots that are close together stack upward so
// labels never overlap. Purely presentational; dates come from official data.

export interface TimelineItem {
  id: string;
  date: string; // yyyy-mm-dd
  label: string;
  sub?: string;
  done?: boolean;
  kind?: "deadline" | "scholarship";
}

const DAY = 864e5;

export function DeadlineTimeline({ items }: { items: TimelineItem[] }) {
  const today = new Date(new Date().toISOString().slice(0, 10) + "T00:00:00Z").getTime();
  const pts = items
    .map((i) => ({ ...i, t: new Date(i.date + "T00:00:00Z").getTime() }))
    .filter((i) => !Number.isNaN(i.t) && i.t >= today)
    .sort((a, b) => a.t - b.t);
  if (pts.length === 0) return null;

  // Span: today → last deadline, at least 60 days, padded a little.
  const end = Math.max(pts[pts.length - 1]!.t, today + 60 * DAY) + 10 * DAY;
  const pos = (t: number) => ((t - today) / (end - today)) * 100;

  // Month ticks
  const ticks: { t: number; label: string }[] = [];
  const d = new Date(today);
  d.setUTCDate(1);
  d.setUTCMonth(d.getUTCMonth() + 1);
  while (d.getTime() < end) {
    if ((d.getTime() - today) / (end - today) < 0.06) {
      d.setUTCMonth(d.getUTCMonth() + 1);
      continue;
    }
    ticks.push({
      t: d.getTime(),
      label: d.toLocaleDateString("en-GB", { month: "short", timeZone: "UTC" }),
    });
    d.setUTCMonth(d.getUTCMonth() + 1);
  }

  // Stack dots that sit within ~7% of each other.
  const placed: { left: number; row: number }[] = [];
  const rows = pts.map((p) => {
    const left = pos(p.t);
    let row = 0;
    while (placed.some((q) => q.row === row && Math.abs(q.left - left) < 9)) row++;
    placed.push({ left, row });
    return { ...p, left, row };
  });
  const maxRow = Math.max(...rows.map((r) => r.row));
  const daysTo = Math.round((pts[0]!.t - today) / DAY);

  return (
    <figure
      className="rounded-2xl border border-border bg-card p-5 space-y-3 overflow-hidden"
      aria-label="Upcoming deadlines timeline"
    >
      <figcaption className="flex items-baseline justify-between gap-3">
        <span className="font-display font-bold text-foreground">Deadlines ahead</span>
        <span className="text-xs text-muted-foreground">
          Next in{" "}
          <span className="font-semibold text-foreground">
            {daysTo === 0 ? "today" : `${daysTo} days`}
          </span>
        </span>
      </figcaption>
      <div className="relative mx-4" style={{ height: `${(maxRow + 1) * 34 + 40}px` }}>
        {/* track */}
        <div className="absolute left-0 right-0 bottom-6 h-1 rounded-full bg-secondary" />
        {/* today */}
        <div
          className="absolute bottom-[21px] -translate-x-1/2 flex flex-col items-center"
          style={{ left: "0%" }}
        >
          <span className="w-2.5 h-2.5 rounded-full bg-foreground ring-4 ring-foreground/10" />
        </div>
        <span className="absolute bottom-0 left-0 text-[10px] font-semibold text-foreground">
          Today
        </span>
        {/* month ticks */}
        {ticks.map((t) => (
          <span
            key={t.t}
            className="absolute bottom-0 -translate-x-1/2 text-[10px] text-muted-foreground"
            style={{ left: `${pos(t.t)}%` }}
          >
            {t.label}
          </span>
        ))}
        {/* deadlines */}
        {rows.map((r) => (
          <div
            key={r.id}
            className="absolute -translate-x-1/2 group"
            style={{ left: `${Math.min(r.left, 98)}%`, bottom: `${22 + r.row * 34}px` }}
          >
            <span
              title={`${r.label} — ${fmtDate(r.date)}${r.sub ? ` · ${r.sub}` : ""}`}
              className={`block w-3.5 h-3.5 rounded-full border-2 border-card shadow-sm ${
                r.done
                  ? "bg-muted-foreground/40"
                  : r.kind === "scholarship"
                    ? "bg-sky-500"
                    : "bg-primary"
              }`}
            />
            {/* always-visible short date; full label on hover/focus */}
            <span className="absolute left-1/2 -translate-x-1/2 bottom-4 whitespace-nowrap text-[10px] font-semibold text-foreground group-hover:opacity-0">
              {fmtDate(r.date).replace(/ \d{4}$/, "")}
            </span>
            <span className="pointer-events-none absolute left-1/2 -translate-x-1/2 bottom-4 whitespace-nowrap rounded-md bg-foreground text-background text-[11px] px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
              {fmtDate(r.date)} · {r.label}
            </span>
          </div>
        ))}
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted-foreground">
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-primary mr-1" />
          Application
        </span>
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-sky-500 mr-1" />
          Scholarship
        </span>
        <span>
          <span className="inline-block w-2 h-2 rounded-full bg-muted-foreground/40 mr-1" />
          Done
        </span>
      </div>
    </figure>
  );
}
