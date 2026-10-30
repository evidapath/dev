import { PageGuide } from "../components/PageGuide";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CalendarCheck,
  CheckCircle2,
  Circle,
  CircleHelp,
  DollarSign,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { getProfile, listSavedUniversities } from "../lib/profile.functions";
import { useLiveData } from "../lib/use-live-data";
import { analyze, fmtDate, type StudentInput } from "../lib/decision-engine";

export const Route = createFileRoute("/plan")({
  head: () => ({
    meta: [
      { title: "Your Plan — EvidaPath" },
      {
        name: "description",
        content:
          "A dated action plan built from your saved universities: application and scholarship deadlines, subjects, tests and funding steps.",
      },
      { property: "og:title", content: "Your Plan — EvidaPath" },
      {
        property: "og:description",
        content: "Know what to do next, and by when, for every university on your path.",
      },
      ogUrlMeta("/plan"),
    ],
    links: [canonicalLink("/plan")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: PlanPage,
});

type Kind = "deadline" | "scholarship" | "academic" | "language" | "funding" | "evidence";

interface PlanItem {
  id: string;
  kind: Kind;
  title: string;
  uni: string;
  uniId: string;
  date?: string; // ISO yyyy-mm-dd when the official source gives one
  source?: string;
}

const KIND_META: Record<Kind, { label: string; icon: typeof CalendarCheck }> = {
  deadline: { label: "Application", icon: CalendarCheck },
  scholarship: { label: "Scholarship", icon: Sparkles },
  academic: { label: "Academic", icon: GraduationCap },
  language: { label: "Language test", icon: BookOpen },
  funding: { label: "Funding", icon: DollarSign },
  evidence: { label: "Ask the university", icon: CircleHelp },
};

const DONE_KEY = "evidapath.plan.done";

function readDone(): Set<string> {
  try {
    return new Set(JSON.parse(localStorage.getItem(DONE_KEY) ?? "[]") as string[]);
  } catch {
    return new Set();
  }
}

function isoDate(text: string | undefined): string | undefined {
  const m = text?.match(/\b(20\d{2}-\d{2}-\d{2})\b/);
  return m?.[1];
}

function PlanPage() {
  const { data, loading } = useLiveData();
  const [savedIds, setSavedIds] = useState<string[] | null>(null);
  const [input, setInput] = useState<StudentInput | null>(null);
  const [done, setDone] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState("all");

  const fetchProfile = useServerFn(getProfile);
  const fetchSaved = useServerFn(listSavedUniversities);
  useEffect(() => {
    setDone(readDone());
    let live = true;
    Promise.all([fetchProfile().catch(() => null), fetchSaved().catch(() => [])]).then(
      ([p, saved]) => {
        if (!live) return;
        setSavedIds(saved.map((s) => s.sanity_university_id));
        setInput({
          curriculum: p?.curriculum || "IB Diploma",
          gradeBand: p?.grade_band || "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
          subject: p?.intended_subject || "Computer Science",
          budgetUsd: p?.annual_budget ?? 40000,
          citizenship: p?.citizenship || "",
        });
      },
    );
    return () => {
      live = false;
    };
  }, [fetchProfile, fetchSaved]);

  const items = useMemo<PlanItem[]>(() => {
    if (!data || !savedIds || !input) return [];
    const out: PlanItem[] = [];
    const today = new Date().toISOString().slice(0, 10);
    for (const id of savedIds) {
      const u = data.universities.find((x) => x.id === id);
      if (!u) continue;
      const a = analyze(u, input, data.scholarships, data.universities, data.fx);
      const base = { uni: u.name, uniId: u.id };
      for (const d of u.deadlines ?? []) {
        if (!d.deadline || d.deadline.slice(0, 10) < today) continue;
        out.push({
          ...base,
          id: `${u.id}:dl:${d.label}`,
          kind: "deadline",
          title: `Submit your application — ${d.label}${d.platform ? ` (via ${d.platform})` : ""}`,
          date: d.deadline.slice(0, 10),
          source: u.officialSourceUrl,
        });
      }
      for (const f of a.financial.funding) {
        if (f.basis === "guaranteed") continue;
        const date = isoDate(f.deadline);
        if (date && date < today) continue;
        out.push({
          ...base,
          id: `${u.id}:sch:${f.name}`,
          kind: "scholarship",
          title: `Check eligibility and apply: ${f.name}`,
          ...(date ? { date } : {}),
          source: f.source,
        });
      }
      for (const l of a.levers) {
        if (l.kind === "deadline") continue; // already listed with its date
        if (l.kind === "funding" && /scholarship/i.test(l.text)) continue; // listed above
        out.push({
          ...base,
          id: `${u.id}:lv:${l.text}`,
          kind: l.kind === "budget" ? "funding" : l.kind,
          title: l.text,
        });
      }
    }
    return out;
  }, [data, savedIds, input]);

  const toggle = (id: string) =>
    setDone((cur) => {
      const next = new Set(cur);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      try {
        localStorage.setItem(DONE_KEY, JSON.stringify([...next]));
      } catch {
        /* storage unavailable — progress just isn't remembered */
      }
      return next;
    });

  const shown = items.filter((i) => filter === "all" || i.uniId === filter);
  const dated = shown.filter((i) => i.date).sort((a, b) => a.date!.localeCompare(b.date!));
  const anytime = shown.filter((i) => !i.date);
  const unis = Array.from(new Map(items.map((i) => [i.uniId, i.uni])).entries());
  const completed = items.filter((i) => done.has(i.id)).length;
  const ready = !loading && savedIds !== null && input !== null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <header className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <CalendarCheck className="w-3.5 h-3.5" />
          <span>Decision Suite • Plan</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Your plan
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-3xl">
          Every step below comes from the universities saved to your path and their official
          deadlines, requirements and scholarships. Tick things off as you go.
        </p>
      </header>

      <PageGuide
        id="plan"
        title="Your to-do list, with dates"
        steps={[
          {
            title: "Save universities",
            text: "The plan is built from universities on your path. Save them from Find My Path or the university list.",
          },
          {
            title: "Work through “Coming up”",
            text: "These have official deadlines — application rounds and scholarships — soonest first.",
          },
          {
            title: "Then “Prepare now”",
            text: "Subjects to check, English tests to book, questions to ask universities, and funding steps.",
          },
          {
            title: "Tick things off",
            text: "Click the circle when something's done. Your ticks are remembered on this device.",
          },
        ]}
      />

      {!ready ? (
        <div className="space-y-3" aria-busy="true">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 rounded-xl bg-secondary/60 animate-pulse" />
          ))}
        </div>
      ) : savedIds.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card p-8 text-center space-y-3">
          <p className="font-display font-bold text-lg text-foreground">
            Save a university to start your plan
          </p>
          <p className="text-sm text-muted-foreground">
            Your plan is built from the universities on your path — their deadlines, requirements
            and scholarships.
          </p>
          <Link
            to="/find-my-path"
            className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors"
          >
            Find universities <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div
              className="flex flex-wrap gap-1.5"
              role="tablist"
              aria-label="Filter by university"
            >
              {[["all", "All universities"] as const, ...unis].map(([id, name]) => (
                <button
                  key={id}
                  role="tab"
                  aria-selected={filter === id}
                  onClick={() => setFilter(id)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    filter === id
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-card text-muted-foreground border-border hover:text-foreground"
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
            <span className="text-xs text-muted-foreground">
              {completed} of {items.length} done
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-secondary overflow-hidden" aria-hidden>
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${items.length ? (completed / items.length) * 100 : 0}%` }}
            />
          </div>

          <PlanSection
            title="Coming up"
            empty="No upcoming dated deadlines for this cycle."
            items={dated}
            done={done}
            toggle={toggle}
          />
          <PlanSection
            title="Prepare now"
            empty="Nothing else to prepare — nice."
            items={anytime}
            done={done}
            toggle={toggle}
          />
        </>
      )}
    </div>
  );
}

function PlanSection({
  title,
  empty,
  items,
  done,
  toggle,
}: {
  title: string;
  empty: string;
  items: PlanItem[];
  done: Set<string>;
  toggle: (id: string) => void;
}) {
  return (
    <section className="space-y-3">
      <h2 className="font-display font-bold text-lg text-foreground">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-muted-foreground">{empty}</p>
      ) : (
        <ul className="space-y-2">
          {items.map((i) => {
            const meta = KIND_META[i.kind];
            const Icon = meta.icon;
            const isDone = done.has(i.id);
            return (
              <li
                key={i.id}
                className={`flex items-start gap-3 rounded-xl border bg-card p-4 transition-colors ${
                  isDone ? "border-border/60 opacity-60" : "border-border hover:border-primary/40"
                }`}
              >
                <button
                  onClick={() => toggle(i.id)}
                  aria-pressed={isDone}
                  aria-label={isDone ? "Mark as not done" : "Mark as done"}
                  className="mt-0.5 text-primary shrink-0"
                >
                  {isDone ? (
                    <CheckCircle2 className="w-5 h-5" />
                  ) : (
                    <Circle className="w-5 h-5 text-muted-foreground" />
                  )}
                </button>
                <div className="min-w-0 flex-1 space-y-1">
                  <p
                    className={`text-sm font-medium text-foreground ${isDone ? "line-through" : ""}`}
                  >
                    {i.title}
                  </p>
                  <p className="text-xs text-muted-foreground flex flex-wrap items-center gap-x-2 gap-y-1">
                    <span className="inline-flex items-center gap-1">
                      <Icon className="w-3 h-3" />
                      {meta.label}
                    </span>
                    <span>·</span>
                    <span>{i.uni}</span>
                    {i.source && (
                      <>
                        <span>·</span>
                        <a
                          href={i.source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline"
                        >
                          Official source
                        </a>
                      </>
                    )}
                  </p>
                </div>
                {i.date && (
                  <span className="shrink-0 text-xs font-mono font-semibold text-foreground bg-secondary rounded-md px-2 py-1">
                    {fmtDate(i.date)}
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
