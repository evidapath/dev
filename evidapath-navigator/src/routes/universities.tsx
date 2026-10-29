import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  GraduationCap,
  Search,
  ShieldCheck,
  MapPin,
  ArrowRight,
  ExternalLink,
  Filter,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { getUniversities } from "../lib/universities.functions";
import type { University } from "../lib/mock-data";
import { formatCost } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/universities")({
  head: () => ({
    meta: [
      { title: "University Cost Database — EvidaPath" },
      {
        name: "description",
        content:
          "The university database built around decisions, not rankings. Tuition, living costs, prerequisites, and affordability will be displayed as verified data is added.",
      },
      { property: "og:title", content: "University Cost Database — EvidaPath" },
      {
        property: "og:description",
        content:
          "Cost of attendance, scholarship availability, and admissions evidence — currently being built and verified.",
      },
      ogUrlMeta("/universities"),
    ],
    links: [canonicalLink("/universities")],
  }),
  component: UniversitiesDirectoryPage,
});

function UniversitiesDirectoryPage() {
  const [query, setQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("All");
  const [universities, setUniversities] = useState<University[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUniversities = useServerFn(getUniversities);
  useEffect(() => {
    let active = true;
    fetchUniversities()
      .then((res) => {
        if (!active) return;
        setUniversities(res.universities);
        setSource(res.source);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchUniversities]);

  const countries = useMemo(
    () => Array.from(new Set(universities.map((u) => u.country).filter(Boolean))).sort(),
    [universities],
  );

  const filtered = universities.filter((u) => {
    const matchesQuery =
      u.name.toLowerCase().includes(query.toLowerCase()) ||
      u.city.toLowerCase().includes(query.toLowerCase()) ||
      u.country.toLowerCase().includes(query.toLowerCase());

    const matchesCountry = selectedCountry === "All" || u.country === selectedCountry;
    return matchesQuery && matchesCountry;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <GraduationCap className="w-3.5 h-3.5" />
          <span>University Intelligence Database</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          EvidaPath University Cost Database
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          The university database built around decisions, not rankings. Every profile is designed to
          model tuition, estimated living costs, program duration, and actionable scholarships.
          Verified figures, source attribution, and verification dates will appear as data is added.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            {source === "sanity"
              ? "Live data connected. Every figure traces to an official source, and each university shows its verification status. Where official sources are incomplete or conflict, we show that rather than inventing a number."
              : "Illustrative product preview. Live analysis will use verified EvidaPath data. University data currently being verified."}
          </span>
        </div>
      </div>

      {/* Filter and Search */}
      <div className="bg-card border border-border rounded-2xl p-5 shadow-xs flex flex-col sm:flex-row items-center gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by university name, city or country..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full h-10 pl-9 pr-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="w-full sm:w-64">
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          >
            <option value="All">All Jurisdictions</option>
            {countries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* University Profiles Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <UniversityCardSkeleton key={i} index={i} />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-muted-foreground animate-in fade-in duration-300">
          No universities match your search.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((univ, i) => (
            <UniversityCard key={univ.id} univ={univ} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}

// Skeleton placeholder shown while verified data loads — keeps the grid layout
// stable (no pop-in / layout shift) and signals progress with a gentle pulse.
function UniversityCardSkeleton({ index = 0 }: { index?: number }) {
  return (
    <div
      className="rounded-2xl border border-border bg-card p-6 space-y-6 motion-safe:animate-in motion-safe:fade-in fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "400ms" }}
      aria-hidden="true"
    >
      <div className="animate-pulse space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 w-8 rounded-full bg-muted" />
          <div className="h-5 w-24 rounded bg-muted" />
        </div>
        <div className="space-y-2">
          <div className="h-5 w-3/4 rounded bg-muted" />
          <div className="h-3 w-1/2 rounded bg-muted" />
        </div>
        <div className="h-9 w-full rounded-lg bg-muted" />
        <div className="space-y-2.5">
          <div className="h-3 w-full rounded bg-muted" />
          <div className="h-3 w-5/6 rounded bg-muted" />
          <div className="h-3 w-2/3 rounded bg-muted" />
        </div>
        <div className="flex gap-2 pt-2">
          <div className="h-9 w-28 rounded-lg bg-muted" />
          <div className="h-9 w-28 rounded-lg bg-muted" />
        </div>
      </div>
    </div>
  );
}

// One university card. When the university has multiple programs (programDetails),
// shows a program selector so the student sees THAT program's own cost + admissions
// (Suhail: program-specific, not university-wide). Falls back to the flat fields for
// single-program universities.
function UniversityCard({ univ, index = 0 }: { univ: University; index?: number }) {
  const details = univ.programDetails;
  const [sel, setSel] = useState(0);
  const pv = details?.[sel];

  // Displayed values: the selected program view when present, else the flat fields.
  const costs = pv?.costs ?? univ.costs;
  const durationYears = pv?.durationYears ?? univ.durationYears;
  const residencyNote = pv?.costResidencyNote ?? univ.costResidencyNote;
  const admissions = pv?.admissionsByCurriculum ?? univ.admissionsByCurriculum;

  return (
    <div
      className="rounded-2xl border border-border bg-card p-6 shadow-xs flex flex-col justify-between space-y-6 transition-all duration-200 ease-out hover:border-primary/40 hover:shadow-md hover:-translate-y-0.5 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-3 fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "450ms" }}
    >
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-3xl">{univ.flag}</span>
          <span className="text-xs font-mono font-semibold bg-secondary px-2.5 py-0.5 rounded text-foreground">
            {durationYears > 0 ? `${durationYears}-Year Degree` : "Duration pending"}
          </span>
        </div>

        <div>
          <h3 className="font-display font-bold text-lg text-foreground">{univ.name}</h3>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
            <MapPin className="w-3 h-3 text-muted-foreground" />
            {univ.city}, {univ.country}
          </p>
        </div>

        {/* Program selector (only when the university has more than one program) */}
        {details && details.length > 1 && (
          <div>
            <label className="block text-[10px] uppercase font-semibold text-muted-foreground mb-1">
              Program
            </label>
            <select
              value={sel}
              onChange={(e) => setSel(Number(e.target.value))}
              className="w-full h-9 px-2 rounded-lg border border-input bg-background text-xs text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              {details.map((p, i) => (
                <option key={i} value={i}>
                  {p.name}
                  {p.degree ? ` (${p.degree})` : ""}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Cost & Requirements Table */}
        <div className="bg-secondary/40 rounded-xl p-3.5 border border-border space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Academic Threshold:</span>
            <span className="font-medium text-muted-foreground text-right">
              {univ.academicRequirements.target}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Tuition / year:</span>
            <span className="font-mono font-medium text-muted-foreground">
              {formatCost(costs.tuitionPerYear, costs.currency)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Living / year (Est):</span>
            <span className="font-mono font-medium text-muted-foreground">
              {formatCost(costs.livingPerYear, costs.currency)}
            </span>
          </div>
          {costs.livingSource && (
            <p
              className={`text-[10px] leading-snug text-right ${
                costs.livingSource.startsWith("Unofficial")
                  ? "text-bronze"
                  : "text-muted-foreground"
              }`}
            >
              Living cost: {costs.livingSource}
            </p>
          )}
          <div className="flex justify-between pt-1 border-t border-border/60">
            <span className="text-muted-foreground font-semibold">Total Degree Outlay:</span>
            <span className="font-mono font-bold text-muted-foreground">
              {formatCost(costs.totalDegree, costs.currency)}
            </span>
          </div>
          {residencyNote && (
            <p className="text-[10px] text-bronze pt-1 leading-snug">{residencyNote}</p>
          )}
        </div>

        {/* Affordability Index & Evidence */}
        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Affordability Index:</span>
            <span className="font-semibold px-2 py-0.5 rounded text-[11px] bg-secondary text-muted-foreground">
              {univ.affordabilityIndex.category}
            </span>
          </div>
          <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
            <span className="flex items-center gap-1">
              <span
                className={`inline-block w-1.5 h-1.5 rounded-full ${
                  univ.evidenceConfidence.startsWith("Verified") ? "bg-primary" : "bg-bronze"
                }`}
              />
              <strong>{univ.evidenceConfidence}</strong>
            </span>
            <span>Verified: {univ.lastVerified}</span>
          </div>
        </div>

        {/* Verified admissions + deadlines (surfaced from Sanity) */}
        {(univ.deadlines?.length || admissions?.length) && (
          <details className="text-xs border-t border-border/60 pt-2">
            <summary className="cursor-pointer text-primary font-semibold select-none">
              Admissions & deadlines
            </summary>
            <div className="mt-2 space-y-3">
              {univ.deadlines && univ.deadlines.length > 0 && (
                <div className="space-y-1">
                  <p className="text-[10px] uppercase font-semibold text-muted-foreground">
                    Application deadlines
                  </p>
                  {univ.deadlines.map((d, i) => (
                    <div key={i} className="flex justify-between gap-2 text-muted-foreground">
                      <span>
                        {d.label}
                        {d.binding ? " (binding)" : ""}
                      </span>
                      <span className="font-mono text-right">
                        {(d.deadline ?? "").slice(0, 10)}
                        {isPast(d.deadline) && (
                          <span className="text-bronze font-sans font-semibold"> · passed</span>
                        )}
                        {d.decisionDate ? ` · decision ${d.decisionDate.slice(0, 10)}` : ""}
                      </span>
                    </div>
                  ))}
                  {univ.deadlines[0]?.platform && (
                    <p className="text-[10px] text-muted-foreground">
                      via {univ.deadlines[0].platform}
                    </p>
                  )}
                </div>
              )}
              {admissions && admissions.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-[10px] uppercase font-semibold text-muted-foreground">
                    Entry requirements by qualification
                  </p>
                  {admissions.map((a, i) => (
                    <div key={i} className="rounded bg-secondary/40 p-2 space-y-0.5">
                      <p className="font-semibold text-foreground">{a.curriculum}</p>
                      {a.threshold && <p className="text-muted-foreground">{a.threshold}</p>}
                      {a.threshold && otherTermsNote(a.curriculum, a.threshold) && (
                        <p className="text-[10px] text-bronze">
                          {otherTermsNote(a.curriculum, a.threshold)}
                        </p>
                      )}
                      {a.subjects.length > 0 && (
                        <p className="text-muted-foreground">Subjects: {a.subjects.join("; ")}</p>
                      )}
                      {a.tests.length > 0 && (
                        <p className="text-muted-foreground">Tests: {a.tests.join(", ")}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </details>
        )}
      </div>

      <div className="pt-4 border-t border-border flex items-center justify-between">
        <Link to="/find-my-path">
          <Button
            size="sm"
            variant="outline"
            className="border-border text-foreground hover:bg-secondary text-xs"
          >
            Would this work for you?
          </Button>
        </Link>
        <Link to="/find-my-path">
          <Button
            size="sm"
            className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs"
          >
            Analyze My Fit →
          </Button>
        </Link>
      </div>
    </div>
  );
}

// Some universities publish entry grades only in A-level terms ("AAB or equivalent").
// When that text is shown under another qualification, say so plainly rather than
// leaving an IB or American-diploma student to guess what "AAB" means for them.
const OWN_TERMS: { match: RegExp; own: RegExp; name: string }[] = [
  { match: /baccalaureate|\bIB\b/i, own: /\bIB\b|baccalaureate|points/i, name: "IB" },
  {
    match: /american|high school|\bAP\b/i,
    own: /\bGPA\b|\bSAT\b|\bACT\b|\bAP\b|high school|diploma/i,
    name: "American high school",
  },
];
function otherTermsNote(curriculum: string, threshold: string): string | null {
  const kind = OWN_TERMS.find((k) => k.match.test(curriculum));
  if (!kind || kind.own.test(threshold) || !/a[- ]?level|A\*/i.test(threshold)) return null;
  return `Published in A-level terms only. Ask the university for its ${kind.name} equivalent.`;
}

// True when an ISO date (YYYY-MM-DD…) is before today, so a closed deadline is never
// shown as if it were still open.
function isPast(date: string | null | undefined): boolean {
  const day = date?.slice(0, 10);
  if (!day || !/^\d{4}-\d{2}-\d{2}$/.test(day)) return false;
  return day < new Date().toISOString().slice(0, 10);
}
