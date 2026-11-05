import { createFileRoute, Link } from "@tanstack/react-router";
import { CheckCircle2, Circle, FileDown, FileText, Languages, Loader2, Share2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { PageHeader } from "../components/PageHeader";
import { requireAuth } from "../lib/route-guard";
import { useStudent } from "../lib/use-student";
import { analyze, fmtDate } from "../lib/decision-engine";
import { buildChecklist, ENGLISH_LEAD_DAYS, GROUP_ORDER } from "../lib/documents";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

const DONE_KEY = "evidapath.docs.done";

export const Route = createFileRoute("/documents")({
  head: () => ({
    meta: [
      { title: "Documents & Tests — EvidaPath" },
      {
        name: "description",
        content:
          "A checklist for each university on your path: English test, grades, admissions tests, applications, scholarships and visa documents. Download it as a PDF.",
      },
      ogUrlMeta("/documents"),
    ],
    links: [canonicalLink("/documents")],
  }),
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  component: DocumentsPage,
});

function readDone(): Set<string> {
  try {
    return new Set(JSON.parse(localStorage.getItem(DONE_KEY) ?? "[]") as string[]);
  } catch {
    return new Set();
  }
}

function DocumentsPage() {
  const { data, input, savedIds, loading } = useStudent();
  const [done, setDone] = useState<Set<string>>(new Set());
  const [making, setMaking] = useState(false);
  useEffect(() => setDone(readDone()), []);

  const unis = useMemo(() => {
    if (!data) return [];
    return savedIds.flatMap((id) => {
      const u = data.universities.find((x) => x.id === id);
      if (!u) return [];
      const a = analyze(u, input, data.scholarships, data.universities, data.fx);
      return [{ u, a, items: buildChecklist(u, a) }];
    });
  }, [data, savedIds, input]);

  const toggle = (id: string) =>
    setDone((cur) => {
      const next = new Set(cur);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      try {
        localStorage.setItem(DONE_KEY, JSON.stringify([...next]));
      } catch {
        /* storage unavailable — ticks just aren't remembered */
      }
      return next;
    });

  const pdf = () => {
    setMaking(true);
    import("../lib/plan-pdf")
      .then(({ downloadPlanPdf }) => downloadPlanPdf(unis, done, input))
      .catch((err: Error) => {
        console.error("[documents] PDF failed:", err);
        toast.error("Couldn't make the PDF — please try again.");
      })
      .finally(() => setMaking(false));
  };

  // A link to Compare with just these universities: no personal details in it.
  const share = () => {
    const url = `${window.location.origin}/compare?u=${unis.map((x) => x.u.id).join(",")}`;
    navigator.clipboard
      .writeText(url)
      .then(() =>
        toast.success("Link copied", {
          description:
            "It opens a side-by-side comparison of your universities. Your answers and ticks aren't in it; send the PDF for those.",
        }),
      )
      .catch(() => toast(url));
  };

  const english = unis.filter((x) => x.a.program?.english);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <PageHeader
        icon={FileText}
        eyebrow="Documents & tests"
        title="Everything to"
        accent="get ready."
        intro="A checklist for each university on your path: English test, grades, admissions tests, the application, scholarships and the visa."
        note="Built from official university and government pages. Ticks are remembered on this device."
      >
        <div className="flex flex-wrap gap-2">
          <button
            onClick={pdf}
            disabled={!unis.length || making}
            className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 disabled:opacity-50"
          >
            {making ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <FileDown className="w-4 h-4" />
            )}
            Download PDF
          </button>
          <button
            onClick={share}
            disabled={unis.length === 0}
            className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg border border-border bg-card text-sm font-semibold text-foreground hover:bg-secondary disabled:opacity-50"
          >
            <Share2 className="w-4 h-4" />
            Share with family
          </button>
        </div>
      </PageHeader>

      {loading ? (
        <div className="space-y-3" aria-busy="true">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-20 rounded-xl bg-secondary/60 animate-pulse" />
          ))}
        </div>
      ) : unis.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card p-8 text-center space-y-3">
          <p className="font-display font-bold text-lg text-foreground">
            Save a university to build your checklist
          </p>
          <Link
            to="/find-my-path"
            className="inline-flex h-10 px-4 items-center rounded-lg bg-primary text-primary-foreground text-sm font-semibold"
          >
            Find universities
          </Link>
        </div>
      ) : (
        <>
          {/* English test planner */}
          {english.length > 0 && (
            <section className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-3 shadow-xs">
              <h2 className="font-display font-bold text-lg text-foreground flex items-center gap-2">
                <Languages className="w-4 h-4 text-primary" />
                English test planner
              </h2>
              <ul className="divide-y divide-border/60">
                {english.map(({ u, a, items }) => {
                  const by = items.find((i) => i.group === "English test")?.date;
                  return (
                    <li
                      key={u.id}
                      className="py-2.5 grid gap-1 sm:grid-cols-[12rem_1fr_auto] sm:items-start text-xs"
                    >
                      <span className="font-semibold text-foreground">
                        {u.flag} {u.shortName || u.name}
                      </span>
                      <span className="text-muted-foreground">{a.program!.english}</span>
                      <span className="font-mono font-semibold text-foreground sm:text-right">
                        {by ? `Sit by ${fmtDate(by)}` : "—"}
                      </span>
                    </li>
                  );
                })}
              </ul>
              <p className="text-[11px] text-muted-foreground">
                Requirements as each university publishes them. "Sit by" is our suggestion:{" "}
                {ENGLISH_LEAD_DAYS / 7} weeks before that university's first deadline, so results
                arrive in time. Check the test's own results timing.
              </p>
            </section>
          )}

          {unis.map(({ u, items }) => {
            const n = items.filter((i) => done.has(i.id)).length;
            return (
              <section
                key={u.id}
                className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 shadow-xs"
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h2 className="font-display font-bold text-lg text-foreground">
                    {u.flag} {u.name}
                  </h2>
                  <span className="text-xs text-muted-foreground">
                    {n} of {items.length} done
                  </span>
                </div>
                <div className="h-1.5 rounded-full bg-secondary overflow-hidden" aria-hidden>
                  <div
                    className="h-full bg-primary transition-all duration-500"
                    style={{ width: `${items.length ? (n / items.length) * 100 : 0}%` }}
                  />
                </div>
                {GROUP_ORDER.map((g) => {
                  const list = items.filter((i) => i.group === g);
                  if (!list.length) return null;
                  return (
                    <div key={g} className="space-y-1.5">
                      <h3 className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                        {g}
                      </h3>
                      <ul className="space-y-1.5">
                        {list.map((i) => {
                          const isDone = done.has(i.id);
                          return (
                            <li
                              key={i.id}
                              className={`flex items-start gap-3 rounded-lg border p-3 ${isDone ? "border-border/60 opacity-60" : "border-border"}`}
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
                              <div className="min-w-0 flex-1 space-y-0.5">
                                <p
                                  className={`text-sm font-medium text-foreground ${isDone ? "line-through" : ""}`}
                                >
                                  {i.title}
                                </p>
                                {i.detail && (
                                  <p className="text-xs text-muted-foreground">{i.detail}</p>
                                )}
                                {i.source && (
                                  <a
                                    href={i.source}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-[11px] text-primary hover:underline"
                                  >
                                    Official source
                                  </a>
                                )}
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
                    </div>
                  );
                })}
              </section>
            );
          })}
        </>
      )}
    </div>
  );
}
