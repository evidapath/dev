import type { ComponentType, ReactNode } from "react";

/**
 * The one page-header style used across the app: a soft tinted panel with a small
 * label, a plain title with a serif-italic accent, one line of intro, an optional
 * source note, and room for page controls (search, chips, stats) underneath.
 */
export function PageHeader({
  icon: Icon,
  eyebrow,
  title,
  accent,
  intro,
  note,
  aside,
  children,
}: {
  icon: ComponentType<{ className?: string }>;
  eyebrow: string;
  title: string;
  accent?: string;
  intro: ReactNode;
  note?: ReactNode;
  /** Shown beside the title on wide screens (e.g. live counts). */
  aside?: ReactNode;
  /** Controls under the header, on a lighter strip (search, filters). */
  children?: ReactNode;
}) {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-sm">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(45%_70%_at_0%_0%,oklch(0.6_0.17_155/0.10),transparent),radial-gradient(40%_60%_at_100%_100%,oklch(0.53_0.15_62/0.08),transparent)]"
      />
      <div className="relative px-6 sm:px-10 pt-8 sm:pt-10 pb-7 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
        <div className="space-y-4 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
            <Icon className="w-3.5 h-3.5" />
            <span>{eyebrow}</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-display font-extrabold tracking-tight text-foreground leading-[1.05]">
            {title}
            {accent && (
              <>
                {" "}
                <span className="font-serif italic font-medium text-primary tracking-normal">
                  {accent}
                </span>
              </>
            )}
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">{intro}</p>
          {note && <p className="text-[11px] text-muted-foreground leading-relaxed">{note}</p>}
        </div>
        {aside}
      </div>
      {children && (
        <div className="relative border-t border-border/70 bg-background/60 backdrop-blur px-6 sm:px-10 py-5 space-y-4">
          {children}
        </div>
      )}
    </div>
  );
}

/** A row of big live numbers for a PageHeader `aside`. */
export function HeaderStats({ items }: { items: readonly (readonly [string | number, string])[] }) {
  return (
    <dl className="grid grid-cols-3 gap-3 lg:w-[22rem]">
      {items.map(([v, k]) => (
        <div key={k} className="rounded-2xl bg-secondary/60 px-4 py-3">
          <dd className="font-display font-extrabold text-2xl sm:text-3xl text-foreground tabular-nums leading-none">
            {v}
          </dd>
          <dt className="text-[11px] text-muted-foreground mt-1">{k}</dt>
        </div>
      ))}
    </dl>
  );
}
