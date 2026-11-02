import { useUniversitiesFn } from "../lib/use-live-data";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import { usePaged } from "../lib/use-paged";
import { ShowMore } from "../components/ShowMore";
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
import type { University } from "../lib/mock-data";
import { formatCost } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { AdmissionsPanel } from "../components/AdmissionsPanel";

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

  const fetchUniversities = useUniversitiesFn();
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
  const paged = usePaged(filtered, `${query}|${selectedCountry}`);

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
          {paged.visible.map((univ, i) => (
            <UniversityCard key={univ.id} univ={univ} index={i} />
          ))}
        </div>
      )}
      {!loading && (
        <ShowMore remaining={paged.remaining} onClick={paged.showMore} noun="universities" />
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

// "2026-10-21" → "Oct 2026"; anything else is shown as written.
function monthYear(date: string): string {
  if (!/^\d{4}-\d{2}-\d{2}/.test(date)) return date;
  return new Date(`${date.slice(0, 10)}T00:00:00Z`).toLocaleDateString("en-GB", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

// Header tint per country (an oklch hue), so neighbouring cards read apart.
const COUNTRY_HUE: Record<string, number> = {
  "United Kingdom": 255,
  "United States": 25,
  Canada: 15,
  Germany: 85,
  Netherlands: 50,
  "United Arab Emirates": 155,
  Australia: 200,
  Malaysia: 300,
  Switzerland: 0,
  France: 270,
  Ireland: 140,
  Singapore: 340,
};
function countryHue(country: string): number {
  return COUNTRY_HUE[country] ?? 230;
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
  const [admOpen, setAdmOpen] = useState(false);
  const admRef = useRef<HTMLDetailsElement>(null);

  const verified = univ.evidenceConfidence.startsWith("Verified");
  const affordability = univ.affordabilityIndex.category;

  return (
    <div
      className="group rounded-2xl border border-border bg-card shadow-sm overflow-hidden flex flex-col justify-between transition-all duration-200 ease-out hover:border-primary/30 hover:shadow-lg hover:-translate-y-1 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-3 fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "450ms" }}
    >
      {/* Header band, tinted by country so the grid isn't one white sheet */}
      <div
        className="uni-band px-6 pt-5 pb-4 border-b border-border/60"
        style={{ ["--band-h" as string]: countryHue(univ.country) }}
      >
        <div className="flex items-start justify-between gap-3">
          <span className="text-4xl leading-none drop-shadow-sm">{univ.flag}</span>
          <span className="text-[11px] font-semibold bg-card/80 backdrop-blur px-2.5 py-1 rounded-full text-foreground border border-border/60">
            {durationYears > 0 ? `${durationYears}-year degree` : "Duration pending"}
          </span>
        </div>
        <h3 className="font-display font-bold text-xl text-foreground mt-3 leading-tight">
          {univ.name}
        </h3>
        <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
          <MapPin className="w-3 h-3" />
          {univ.city}, {univ.country}
        </p>
      </div>

      <div className="px-6 pt-4 pb-5 space-y-4 flex-1">
        {/* Program selector (only when the university has more than one program) */}
        {details && details.length > 1 && (
          <div>
            <label className="block text-[11px] font-medium text-muted-foreground mb-1">
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

        {/* The two numbers a family asks first, big */}
        <div className="grid grid-cols-2 gap-2">
          <div className="rounded-xl bg-secondary/60 px-3 py-2.5">
            <p className="text-[11px] text-muted-foreground">Tuition / year</p>
            <p className="font-display font-bold text-lg text-foreground tabular-nums leading-tight mt-0.5">
              {formatCost(costs.tuitionPerYear, costs.currency)}
            </p>
          </div>
          <div className="rounded-xl bg-secondary/60 px-3 py-2.5">
            <p className="text-[11px] text-muted-foreground">Living / year (est.)</p>
            <p className="font-display font-bold text-lg text-foreground tabular-nums leading-tight mt-0.5">
              {formatCost(costs.livingPerYear, costs.currency)}
            </p>
          </div>
        </div>
        <div className="flex items-baseline justify-between gap-3 text-sm">
          <span className="text-muted-foreground">Whole degree</span>
          <span className="font-display font-bold text-foreground tabular-nums">
            {formatCost(costs.totalDegree, costs.currency)}
          </span>
        </div>
        {(costs.livingSource || residencyNote) && (
          <div className="space-y-1 text-[11px] leading-snug">
            {costs.livingSource && (
              <p
                className={
                  costs.livingSource.startsWith("Estimate")
                    ? "text-bronze"
                    : "text-muted-foreground"
                }
              >
                Living cost: {costs.livingSource}
              </p>
            )}
            {residencyNote && <p className="text-bronze">{residencyNote}</p>}
          </div>
        )}

        {/* Entry requirements + evidence, as chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          {admissions?.length ? (
            <button
              type="button"
              onClick={() => {
                setAdmOpen(true);
                requestAnimationFrame(() =>
                  admRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" }),
                );
              }}
              className="inline-flex items-center gap-1 rounded-full bg-accent text-accent-foreground font-semibold px-2.5 py-1 hover:bg-primary/15"
            >
              <GraduationCap className="w-3 h-3" />
              Entry grades ↓
            </button>
          ) : (
            <span className="rounded-full bg-secondary text-muted-foreground px-2.5 py-1 line-clamp-1">
              {univ.academicRequirements.target}
            </span>
          )}
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 font-medium ${
              verified ? "bg-accent text-accent-foreground" : "bg-bronze/10 text-bronze"
            }`}
            title={`Last checked: ${univ.lastVerified}`}
          >
            <ShieldCheck className="w-3 h-3" />
            {!verified
              ? univ.evidenceConfidence
              : /^\d{4}-/.test(univ.lastVerified)
                ? `Checked ${monthYear(univ.lastVerified)}`
                : "Being checked"}
          </span>
          {!affordability.startsWith("Pending") && (
            <span className="rounded-full bg-secondary text-foreground px-2.5 py-1 font-medium">
              {affordability}
            </span>
          )}
        </div>

        {/* Verified admissions + deadlines (surfaced from Sanity) */}
        {(univ.deadlines?.length || admissions?.length) && (
          <details
            ref={admRef}
            open={admOpen}
            onToggle={(e) => setAdmOpen(e.currentTarget.open)}
            className="text-xs border-t border-border/60 pt-2"
          >
            <summary className="cursor-pointer text-primary font-semibold select-none">
              Admissions & deadlines
            </summary>
            <AdmissionsPanel deadlines={univ.deadlines} admissions={admissions} />
          </details>
        )}
      </div>

      <div className="px-6 pb-5">
        <Link to="/find-my-path" className="block">
          <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-xl">
            Would this work for me? →
          </Button>
        </Link>
      </div>
    </div>
  );
}
