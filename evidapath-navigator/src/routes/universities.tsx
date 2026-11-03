import { useUniversitiesFn } from "../lib/use-live-data";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { usePaged } from "../lib/use-paged";
import { ShowMore } from "../components/ShowMore";
import { GraduationCap, Search, ShieldCheck } from "lucide-react";
import type { University } from "../lib/mock-data";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { UniversityCard, UniversityCardSkeleton } from "../components/UniversityCard";

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
      {/* Header: what this is, in numbers counted from the live data */}
      <div className="relative overflow-hidden rounded-3xl border border-border bg-card shadow-sm">
        <div
          aria-hidden
          className="absolute inset-0 -z-0 bg-[radial-gradient(45%_70%_at_0%_0%,oklch(0.6_0.17_155/0.10),transparent),radial-gradient(40%_60%_at_100%_100%,oklch(0.53_0.15_62/0.08),transparent)]"
        />
        <div className="relative px-6 sm:px-10 pt-8 sm:pt-10 pb-6 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Universities</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-display font-extrabold tracking-tight text-foreground leading-[1.05]">
            Compare the real cost{" "}
            <span className="font-serif italic font-medium text-primary tracking-normal">
              before you apply.
            </span>
          </h1>
          <p className="max-w-2xl text-sm sm:text-base text-muted-foreground leading-relaxed">
            Tuition, living costs and entry grades for each programme, from official sources: the
            university itself, or the government where it sets the figure. Where a figure isn't
            published, we say so instead of guessing.
          </p>
          {source === "sanity" && universities.length > 0 && (
            <dl className="grid grid-cols-3 gap-3 max-w-xl pt-2">
              {[
                [String(universities.length), "universities"],
                [String(countries.length), "countries"],
                [
                  String(universities.reduce((n, u) => n + (u.programDetails?.length || 1), 0)),
                  "programmes",
                ],
              ].map(([v, k]) => (
                <div key={k} className="rounded-2xl bg-secondary/60 px-4 py-3">
                  <dt className="sr-only">{k}</dt>
                  <dd className="font-display font-extrabold text-2xl sm:text-3xl text-foreground tabular-nums leading-none">
                    {v}
                  </dd>
                  <p className="text-[11px] text-muted-foreground mt-1">{k}</p>
                </div>
              ))}
            </dl>
          )}
        </div>

        {/* Search + country chips */}
        <div className="relative border-t border-border/70 bg-background/60 backdrop-blur px-6 sm:px-10 py-5 space-y-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by university, city or country"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full h-12 pl-11 pr-4 rounded-full border border-input bg-card text-sm text-foreground shadow-xs focus:outline-hidden focus:ring-2 focus:ring-primary"
            />
          </div>
          <div className="flex sm:flex-wrap gap-2 overflow-x-auto sm:overflow-visible pb-1 -mx-1 px-1 [scrollbar-width:none]">
            {["All", ...countries].map((c) => {
              const on = selectedCountry === c;
              const flag = c === "All" ? "🌍" : universities.find((u) => u.country === c)?.flag;
              const n =
                c === "All"
                  ? universities.length
                  : universities.filter((u) => u.country === c).length;
              return (
                <button
                  key={c}
                  type="button"
                  onClick={() => setSelectedCountry(c)}
                  aria-pressed={on}
                  className={`shrink-0 inline-flex items-center gap-1.5 h-9 px-3.5 rounded-full border text-xs font-semibold transition-colors ${
                    on
                      ? "bg-primary text-primary-foreground border-primary shadow-sm"
                      : "bg-card text-foreground border-border hover:border-primary/40"
                  }`}
                >
                  <span className="text-sm leading-none">{flag}</span>
                  {c === "All" ? "All countries" : c}
                  <span className={on ? "opacity-80" : "text-muted-foreground"}>{n}</span>
                </button>
              );
            })}
          </div>
          {source !== "sanity" && !loading && (
            <p className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
              <ShieldCheck className="w-3.5 h-3.5" />
              Illustrative preview. University data is still being verified.
            </p>
          )}
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
