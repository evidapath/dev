import { Link } from "@tanstack/react-router";
import { ArrowRight, BarChart3, CalendarCheck, Compass, Sparkles } from "lucide-react";
import type { ReactNode } from "react";

// "How EvidaPath works" — a four-step flow diagram with a tiny preview of what
// each step shows. Drawn in code (no stock art) so it stays crisp and on-brand.

const STEPS: {
  n: number;
  title: string;
  text: string;
  to: string;
  cta: string;
  icon: typeof Compass;
  art: ReactNode;
}[] = [
  {
    n: 1,
    title: "Tell us 4 things",
    text: "Curriculum, grades, subject, budget. 30 seconds.",
    to: "/find-my-path",
    cta: "Start",
    icon: Sparkles,
    art: (
      <div className="space-y-1.5">
        {["IB Diploma", "IB 37–39", "Computer Science", "$40k / yr"].map((t) => (
          <div
            key={t}
            className="h-5 rounded-md bg-card border border-border px-2 text-[10px] leading-5 text-muted-foreground"
          >
            {t}
          </div>
        ))}
      </div>
    ),
  },
  {
    n: 2,
    title: "See what fits",
    text: "What you can afford first, then good matches that cost more.",
    to: "/find-my-path",
    cta: "See options",
    icon: Compass,
    art: (
      <div className="space-y-2">
        {[
          { w: "70%", c: "bg-primary", t: "Fits budget" },
          { w: "88%", c: "bg-primary", t: "Fits budget" },
          { w: "100%", c: "bg-bronze", t: "$8.5k short" },
        ].map((r, i) => (
          <div key={i} className="space-y-0.5">
            <div className="flex justify-between text-[9px] text-muted-foreground">
              <span className="h-1.5 w-16 rounded bg-muted-foreground/25 mt-1" />
              <span>{r.t}</span>
            </div>
            <div className="h-1.5 rounded-full bg-card border border-border overflow-hidden">
              <div className={`h-full ${r.c}`} style={{ width: r.w }} />
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    n: 3,
    title: "Check your fit",
    text: "Grades vs requirement, real cost, scholarships you qualify for.",
    to: "/analyze",
    cta: "Analyze",
    icon: BarChart3,
    art: (
      <div className="grid grid-cols-3 gap-1.5 text-center">
        {[
          ["Grades", "Meets", "text-primary"],
          ["Cost", "$38k", "text-foreground"],
          ["Aid", "2", "text-sky-600"],
        ].map(([l, v, c]) => (
          <div key={l} className="rounded-md bg-card border border-border py-1.5">
            <p className="text-[9px] text-muted-foreground">{l}</p>
            <p className={`text-xs font-bold font-mono ${c}`}>{v}</p>
          </div>
        ))}
      </div>
    ),
  },
  {
    n: 4,
    title: "Plan and fund it",
    text: "Dated next steps, offers compared, the funding gap closed.",
    to: "/plan",
    cta: "My plan",
    icon: CalendarCheck,
    art: (
      <div className="relative h-14">
        <div className="absolute left-0 right-0 top-7 h-1 rounded-full bg-card border border-border" />
        {[8, 38, 62, 90].map((l, i) => (
          <span
            key={l}
            className={`absolute top-[22px] w-3 h-3 -translate-x-1/2 rounded-full border-2 border-secondary ${i === 2 ? "bg-sky-500" : "bg-primary"}`}
            style={{ left: `${l}%` }}
          />
        ))}
        <span className="absolute left-[8%] top-0 -translate-x-1/2 text-[9px] text-muted-foreground">
          Today
        </span>
        <span className="absolute left-[38%] top-0 -translate-x-1/2 text-[9px] text-muted-foreground">
          Apply
        </span>
        <span className="absolute left-[62%] top-0 -translate-x-1/2 text-[9px] text-muted-foreground">
          Aid
        </span>
        <span className="absolute left-[90%] top-0 -translate-x-1/2 text-[9px] text-muted-foreground">
          Offer
        </span>
      </div>
    ),
  },
];

export function HowItWorks() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <span className="text-xs font-bold uppercase tracking-wider text-primary">
          How it works
        </span>
        <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground">
          From “where could I go?” to a plan, in 4 steps
        </h2>
      </div>
      <ol className="relative grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        {/* connector line behind the cards (desktop) */}
        <div
          aria-hidden
          className="hidden lg:block absolute top-9 left-[12%] right-[12%] h-0.5 bg-gradient-to-r from-primary/20 via-primary/50 to-primary/20"
        />
        {STEPS.map((s) => {
          const Icon = s.icon;
          return (
            <li key={s.n} className="relative">
              <Link
                to={s.to}
                className="group h-full flex flex-col rounded-2xl border border-border bg-card p-5 gap-4 hover:border-primary/50 hover:shadow-md hover:-translate-y-0.5 transition-all"
              >
                <div className="flex items-center gap-3">
                  <span className="relative z-10 w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-sm ring-4 ring-background">
                    {s.n}
                  </span>
                  <Icon className="w-5 h-5 text-primary" />
                </div>
                <div className="rounded-xl bg-secondary/60 p-3 min-h-[92px]" aria-hidden>
                  {s.art}
                </div>
                <div className="space-y-1 flex-1">
                  <h3 className="font-display font-bold text-foreground">{s.title}</h3>
                  <p className="text-sm text-muted-foreground leading-snug">{s.text}</p>
                </div>
                <span className="text-sm font-semibold text-primary inline-flex items-center gap-1 group-hover:gap-1.5 transition-all">
                  {s.cta} <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </Link>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
