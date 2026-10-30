import { useEffect, useState } from "react";
import { ChevronDown, HelpCircle, X } from "lucide-react";

// Plain-language "how this page works" panel. Open on a student's first visit,
// can be hidden (remembered on this device) and reopened from the "How this
// works" button at any time.

export interface GuideStep {
  title: string;
  text: string;
}

export function PageGuide({
  id,
  title,
  intro,
  steps,
  tip,
}: {
  id: string;
  title: string;
  intro?: string;
  steps: GuideStep[];
  tip?: string;
}) {
  const key = `evidapath.guide.hidden.${id}`;
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try {
      setOpen(localStorage.getItem(key) !== "1");
    } catch {
      setOpen(true);
    }
  }, [key]);

  const set = (next: boolean) => {
    setOpen(next);
    try {
      if (next) localStorage.removeItem(key);
      else localStorage.setItem(key, "1");
    } catch {
      /* storage unavailable — the guide just won't remember */
    }
  };

  if (!open)
    return (
      <button
        onClick={() => set(true)}
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
      >
        <HelpCircle className="w-3.5 h-3.5" />
        How this page works
      </button>
    );

  return (
    <section
      aria-label={title}
      className="rounded-2xl border border-primary/25 bg-primary/5 p-5 sm:p-6 space-y-4 motion-safe:animate-in motion-safe:fade-in duration-300"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-[11px] font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5" /> How this works
          </p>
          <h2 className="font-display font-bold text-lg text-foreground">{title}</h2>
          {intro && <p className="text-sm text-muted-foreground max-w-3xl">{intro}</p>}
        </div>
        <button
          onClick={() => set(false)}
          aria-label="Hide this guide"
          className="p-1.5 rounded-lg text-muted-foreground hover:bg-primary/10 shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <ol className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {steps.map((s, i) => (
          <li key={s.title} className="rounded-xl bg-card border border-border p-4 space-y-1.5">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">
              {i + 1}
            </span>
            <p className="text-sm font-semibold text-foreground">{s.title}</p>
            <p className="text-xs text-muted-foreground leading-relaxed">{s.text}</p>
          </li>
        ))}
      </ol>
      {tip && (
        <p className="text-xs text-foreground bg-card/70 border border-border rounded-lg px-3 py-2">
          <span className="font-semibold">Tip: </span>
          {tip}
        </p>
      )}
      <button
        onClick={() => set(false)}
        className="inline-flex items-center gap-1 text-xs font-semibold text-muted-foreground hover:text-foreground"
      >
        Got it, hide this <ChevronDown className="w-3 h-3 rotate-180" />
      </button>
    </section>
  );
}
