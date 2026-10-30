import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { ArrowRight, Database, ExternalLink, ShieldCheck } from "lucide-react";
import { useLiveData } from "../lib/use-live-data";
import { buildBriefs, type Brief, type BriefCategory } from "../lib/data-briefs";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/intelligence")({
  head: () => ({
    meta: [
      { title: "EvidaPath Intelligence — Evidence for Better Education Decisions" },
      {
        name: "description",
        content:
          "Research and intelligence publications examining how academic benchmarks, university affordability, scholarships, and pathways interact.",
      },
      {
        property: "og:title",
        content: "EvidaPath Intelligence — Evidence-Based Education Research",
      },
      {
        property: "og:description",
        content:
          "Live data briefs on costs, admissions, scholarships and deadlines, computed from verified university records.",
      },
      ogUrlMeta("/intelligence"),
    ],
    links: [canonicalLink("/intelligence")],
  }),
  component: IntelligencePage,
});

function IntelligencePage() {
  const { data, loading } = useLiveData();
  const briefs = useMemo(() => (data ? buildBriefs(data) : []), [data]);
  const [category, setCategory] = useState<"All" | BriefCategory>("All");
  const categories: ("All" | BriefCategory)[] = [
    "All",
    "Affordability",
    "Admissions",
    "Scholarships",
    "Deadlines",
  ];
  const shown = briefs.filter((b) => category === "All" || b.category === category);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <header className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>EvidaPath Intelligence</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Evidence for better education decisions.
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Live data briefs, computed directly from EvidaPath's verified university and scholarship
          records. When the data is corrected or extended, these findings update with it.
        </p>
      </header>

      <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Brief category">
        {categories.map((c) => (
          <button
            key={c}
            role="tab"
            aria-selected={category === c}
            onClick={() => setCategory(c)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
              category === c
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-card text-muted-foreground border-border hover:text-foreground"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {loading && !data ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" aria-busy="true">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-72 rounded-2xl bg-secondary/60 animate-pulse" />
          ))}
        </div>
      ) : !data ? (
        <p className="text-sm text-muted-foreground">
          Live data is unavailable right now — please try again shortly.
        </p>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {shown.map((b) => (
            <BriefCard key={b.slug} b={b} />
          ))}
        </div>
      )}

      <div className="rounded-2xl border border-border bg-secondary/40 p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p className="font-display font-bold text-foreground">
            See how these findings apply to you
          </p>
          <p className="text-sm text-muted-foreground">
            Run the same data against your own grades, budget and citizenship.
          </p>
        </div>
        <Link
          to="/find-my-path"
          className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition-colors shrink-0"
        >
          Find My Path <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}

function BriefCard({ b }: { b: Brief }) {
  return (
    <article
      id={b.slug}
      className="rounded-2xl border border-border bg-card p-6 space-y-4 shadow-xs flex flex-col"
    >
      <div className="flex items-center justify-between gap-2 text-xs">
        <span className="font-semibold text-primary bg-primary/10 px-2.5 py-0.5 rounded-full">
          {b.category}
        </span>
        <span className="inline-flex items-center gap-1 text-muted-foreground">
          <Database className="w-3 h-3" /> Live data
        </span>
      </div>
      <h2 className="font-display font-bold text-xl text-foreground leading-snug">{b.title}</h2>
      <p className="text-sm text-muted-foreground leading-relaxed">{b.lead}</p>
      {b.rows.length > 0 && (
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full text-xs">
            <thead className="bg-secondary/60 text-muted-foreground">
              <tr>
                <th className="text-left font-semibold px-3 py-2">{b.columns[0]}</th>
                <th className="text-right font-semibold px-3 py-2">{b.columns[1]}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {b.rows.map((r) => (
                <tr key={r.label}>
                  <td className="px-3 py-2 text-foreground">
                    {r.href ? (
                      <a
                        href={r.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-primary inline-flex items-center gap-1"
                      >
                        {r.label} <ExternalLink className="w-3 h-3 opacity-60" />
                      </a>
                    ) : (
                      r.label
                    )}
                  </td>
                  <td className="px-3 py-2 text-right font-mono text-foreground whitespace-nowrap">
                    {r.value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="mt-auto space-y-1.5 pt-1">
        <p className="text-sm text-foreground font-medium">{b.takeaway}</p>
        <p className="text-[11px] text-muted-foreground">
          Computed from {b.basis}.{b.money ? " USD at ECB reference rates." : ""}
        </p>
      </div>
    </article>
  );
}
