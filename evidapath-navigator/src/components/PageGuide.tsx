import { useEffect, useState } from "react";
import { ChevronDown, HelpCircle, X } from "lucide-react";

// Slim "how this page works" line. One sentence by default; "Show steps" opens
// the numbered steps. Dismissing hides it on this device; a small link brings
// it back.

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
  const [hidden, setHidden] = useState(true);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    try {
      setHidden(localStorage.getItem(key) === "1");
    } catch {
      setHidden(false);
    }
  }, [key]);

  const hide = (next: boolean) => {
    setHidden(next);
    setOpen(false);
    try {
      if (next) localStorage.setItem(key, "1");
      else localStorage.removeItem(key);
    } catch {
      /* storage unavailable — the guide just won't remember */
    }
  };

  if (hidden)
    return (
      <button
        onClick={() => hide(false)}
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
      >
        <HelpCircle className="w-3.5 h-3.5" />
        How this page works
      </button>
    );

  return (
    <section
      aria-label={title}
      className="rounded-xl border border-primary/25 bg-primary/5 px-4 py-3 space-y-3 motion-safe:animate-in motion-safe:fade-in duration-300"
    >
      <div className="flex items-center gap-3">
        <HelpCircle className="w-4 h-4 text-primary shrink-0" />
        <p className="text-sm text-foreground flex-1">
          <span className="font-semibold">{title}.</span>{" "}
          <span className="text-muted-foreground">{intro ?? `${steps.length} quick steps.`}</span>
        </p>
        <button
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          className="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:underline shrink-0"
        >
          {open ? "Hide steps" : "Show steps"}
          <ChevronDown className={`w-3 h-3 transition-transform ${open ? "rotate-180" : ""}`} />
        </button>
        <button
          onClick={() => hide(true)}
          aria-label="Dismiss this guide"
          className="p-1 rounded-md text-muted-foreground hover:bg-primary/10 shrink-0"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
      {open && (
        <>
          <ol className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
            {steps.map((s, i) => (
              <li key={s.title} className="rounded-lg bg-card border border-border p-3 space-y-1">
                <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-[11px] font-bold shrink-0">
                    {i + 1}
                  </span>
                  {s.title}
                </p>
                <p className="text-xs text-muted-foreground leading-relaxed">{s.text}</p>
              </li>
            ))}
          </ol>
          {tip && (
            <p className="text-xs text-foreground">
              <span className="font-semibold">Tip: </span>
              {tip}
            </p>
          )}
        </>
      )}
    </section>
  );
}
