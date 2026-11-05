import { PageGuide } from "../components/PageGuide";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useServerFn } from "@tanstack/react-start";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CalendarCheck,
  CheckCircle2,
  ChevronDown,
  Circle,
  CircleHelp,
  DollarSign,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import { requireAuth } from "../lib/route-guard";
import { DeadlineTimeline } from "../components/DeadlineTimeline";
import { Illustration } from "../components/Illustration";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { getProfile, listSavedUniversities } from "../lib/profile.functions";
import { useLiveData } from "../lib/use-live-data";
import { analyze, deadlinesFor, fmtDate, type StudentInput } from "../lib/decision-engine";
import { currentCurriculum } from "../lib/curricula";
import { storedUkHome } from "../lib/residence";
import { PageHeader } from "../components/PageHeader";

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
const FILTER_KEY = "evidapath.plan.university";

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
  // Which university's to-do list is open; remembered on this device.
  const [filter, setFilterState] = useState("all");
  useEffect(() => {
    try {
      const v = localStorage.getItem(FILTER_KEY);
      if (v) setFilterState(v);
    } catch {
      /* storage unavailable */
    }
  }, []);
  const setFilter = (id: string) => {
    setFilterState(id);
    try {
      localStorage.setItem(FILTER_KEY, id);
    } catch {
      /* storage unavailable */
    }
  };
  const [showAll, setShowAll] = useState(false);

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
          curriculum: currentCurriculum(p?.curriculum) || "IB Diploma",
          gradeBand: p?.grade_band || "Strong: IB 37-39 / A*AA / GPA 3.8-3.9",
          subject: p?.intended_subject || "Computer Science",
          budgetUsd: p?.annual_budget ?? 40000,
          citizenship: p?.citizenship || "",
          ukHome: storedUkHome(),
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
      for (const d of deadlinesFor(u, a.programName)) {
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

  const unis = Array.from(new Map(items.map((i) => [i.uniId, i.uni])).entries());
  // A remembered university that's no longer on the path falls back to "all".
  const current = filter !== "all" && unis.some(([id]) => id === filter) ? filter : "all";
  const shown = items.filter((i) => current === "all" || i.uniId === current);
  const dated = shown.filter((i) => i.date).sort((a, b) => a.date!.localeCompare(b.date!));
  const anytime = shown.filter((i) => !i.date);
  // Soonest dated deadline first, then preparation, skipping what's done.
  const nextUp = [...dated, ...anytime].filter((i) => !done.has(i.id)).slice(0, 3);
  // Progress counts only the university being viewed.
  const completed = shown.filter((i) => done.has(i.id)).length;
  const currentName = unis.find(([id]) => id === current)?.[1];
  const ready = !loading && savedIds !== null && input !== null;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <PageHeader
        icon={CalendarCheck}
        eyebrow="Plan"
        title="Your plan,"
        accent="soonest first."
        intro="Your next steps for every university on your path, with dates."
      />

      <PageGuide
        id="plan"
        title="Your to-do list, with dates"
        steps={[
          {
            title: "Save universities",
            text: "The plan is built from universities on your path. Save them from Find My Path or the university list.",
          },
          {
            title: "Pick a university",
            text: "Each university has its own to-do list and progress. Choose “All universities” to see your next steps across them.",
          },
          {
            title: "Deadlines first, then preparation",
            text: "Each list starts with official deadlines, soonest first, then subjects, English tests and funding steps.",
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
        <div className="rounded-2xl border border-dashed border-border bg-card p-8 text-center space-y-3 flex flex-col items-center">
          <Illustration name="plan" />
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
                  aria-selected={current === id}
                  onClick={() => setFilter(id)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    current === id
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-card text-muted-foreground border-border hover:text-foreground"
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
            <span className="text-xs text-muted-foreground">
              {currentName ? `${currentName}: ` : ""}
              {completed} of {shown.length} done
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-secondary overflow-hidden" aria-hidden>
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${shown.length ? (completed / shown.length) * 100 : 0}%` }}
            />
          </div>

          <DeadlineTimeline
            items={dated.map((i) => ({
              id: i.id,
              date: i.date!,
              label: `${i.uni} — ${KIND_META[i.kind].label.toLowerCase()}`,
              kind: i.kind === "scholarship" ? "scholarship" : "deadline",
              done: done.has(i.id),
            }))}
          />
          <PlanSection
            title="Your next 3"
            empty={
              currentName ? `All done for ${currentName} — nice work.` : "All done — nice work."
            }
            items={nextUp}
            done={done}
            toggle={toggle}
          />
          <button
            onClick={() => setShowAll(!showAll)}
            aria-expanded={showAll}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-foreground hover:text-primary"
          >
            <ChevronDown
              className={`w-4 h-4 transition-transform ${showAll ? "rotate-180" : ""}`}
            />
            {showAll ? "Hide full plan" : `See full plan (${shown.length} steps)`}
          </button>
          {showAll &&
            // One to-do list per university, each with its own progress.
            unis
              .filter(([id]) => current === "all" || id === current)
              .map(([id, name]) => {
                const mine = items.filter((i) => i.uniId === id);
                const list = [
                  ...mine.filter((i) => i.date).sort((a, b) => a.date!.localeCompare(b.date!)),
                  ...mine.filter((i) => !i.date),
                ];
                const n = mine.filter((i) => done.has(i.id)).length;
                return (
                  <PlanSection
                    key={id}
                    title={name}
                    progress={`${n} of ${mine.length} done`}
                    empty="Nothing to do here yet."
                    items={list}
                    done={done}
                    toggle={toggle}
                    hideUni
                  />
                );
              })}
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
  progress,
  hideUni,
}: {
  title: string;
  empty: string;
  items: PlanItem[];
  done: Set<string>;
  toggle: (id: string) => void;
  /** e.g. "2 of 5 done", shown beside the title. */
  progress?: string;
  /** Leave the university off each row (the section is one university's list). */
  hideUni?: boolean;
}) {
  return (
    <section className="space-y-3">
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="font-display font-bold text-lg text-foreground">{title}</h2>
        {progress && <span className="text-xs text-muted-foreground shrink-0">{progress}</span>}
      </div>
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
                    {!hideUni && (
                      <>
                        <span>·</span>
                        <span>{i.uni}</span>
                      </>
                    )}
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
