import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import {
  Search,
  Filter,
  ShieldCheck,
  Compass,
  ArrowRight,
  DollarSign,
  Clock,
  MapPin,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { getUniversities } from "../lib/universities.functions";
import { getFxRates, type FxRates } from "../lib/fx.functions";
import { BUDGET_MAX, annualCostUsd, budgetFit } from "../lib/budget";
import { listSavedUniversities, saveUniversity } from "../lib/profile.functions";
import type { University } from "../lib/mock-data";
import { formatCost } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/discover")({
  head: () => ({
    meta: [
      { title: "Discover Universities & Global Pathways — EvidaPath" },
      {
        name: "description",
        content:
          "Discover universities that fit your academic profile, budget, geography and career ambitions. Decisions built around evidence, not rankings.",
      },
      { property: "og:title", content: "Discover Universities & Global Pathways — EvidaPath" },
      {
        property: "og:description",
        content:
          "Explore global academic pathways matching your profile — currently being built and verified.",
      },
      ogUrlMeta("/discover"),
    ],
    links: [canonicalLink("/discover")],
  }),
  component: DiscoverPage,
});

function DiscoverPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("All");
  const [maxBudget, setMaxBudget] = useState(80000);
  const [selectedDuration, setSelectedDuration] = useState("All");
  const [universities, setUniversities] = useState<University[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUniversities = useServerFn(getUniversities);
  const fetchFx = useServerFn(getFxRates);
  const [fx, setFx] = useState<FxRates | null>(null);
  useEffect(() => {
    let active = true;
    fetchFx()
      .then((r) => active && setFx(r))
      .catch(() => {});
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
  }, [fetchUniversities, fetchFx]);

  const countries = Array.from(new Set(universities.map((u) => u.country).filter(Boolean))).sort();

  // Save a university to the student's persisted "My Path" (Supabase, RLS-scoped).
  // Signed-out students are prompted to sign in rather than silently failing.
  const saveUniFn = useServerFn(saveUniversity);
  // Already-saved universities show "Saved" so a returning student can see their
  // path persisted. Signed-out: the list call fails and every card stays "Add".
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const listSavedFn = useServerFn(listSavedUniversities);
  useEffect(() => {
    let active = true;
    listSavedFn()
      .then((rows) => {
        if (active) setSavedIds(new Set(rows.map((r) => r.sanity_university_id)));
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, [listSavedFn]);
  const addToMyPath = (u: University) => {
    saveUniFn({ data: { sanity_university_id: u.id, university_name: u.name } })
      .then(() => {
        setSavedIds((s) => new Set(s).add(u.id));
        toast.success(`${u.shortName} saved to your path.`);
      })
      .catch((err: Error) => {
        // Surface the real reason rather than always blaming sign-in. A silent/
        // misleading catch here hid a table-GRANT bug for weeks.
        console.error("[addToMyPath] save failed:", err);
        const msg = /not authenticated/i.test(err?.message ?? "")
          ? "Sign in to save universities to your path."
          : "Could not save — please try again.";
        toast.error(msg);
      });
  };

  const filtered = universities.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.city.toLowerCase().includes(searchQuery.toLowerCase()) ||
      u.programs.some((p) => p.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCountry = selectedCountry === "All" || u.country === selectedCountry;
    // Costs are converted to USD before comparing with the (USD) budget. Only a
    // university whose known cost exceeds the budget is hidden; unknown costs stay.
    const matchesBudget = budgetFit(annualCostUsd(u, fx), maxBudget) !== "over";
    const matchesDuration =
      selectedDuration === "All" || u.durationYears.toString() === selectedDuration;

    return matchesSearch && matchesCountry && matchesBudget && matchesDuration;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3 max-w-3xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <Compass className="w-3.5 h-3.5" />
          <span>Decision Suite • Discover</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Discover Universities Built Around Decisions
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Filter beyond arbitrary prestige tables. Model academic prerequisites, multi-year net cost
          of attendance, program duration, and actionable funding opportunities. Verified figures
          will appear as data is added.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            {source === "sanity"
              ? "Live data connected. Figures trace to official sources and each university shows its verification status. Budget filtering applies only where cost is verified."
              : "Illustrative product preview. Live analysis will use verified EvidaPath data. University data currently being verified."}
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-5 rounded-2xl border border-border bg-card shadow-xs space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search text */}
          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1">
              Search University or Subject
            </label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
              <input
                type="text"
                placeholder="e.g. Computer Science, Oxford, Munich"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-10 pl-9 pr-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          {/* Country filter */}
          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1">
              Country / Destination
            </label>
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

          {/* Duration */}
          <div>
            <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1">
              Degree Duration
            </label>
            <select
              value={selectedDuration}
              onChange={(e) => setSelectedDuration(e.target.value)}
              className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
            >
              <option value="All">All Durations (3 or 4 yrs)</option>
              <option value="3">3-Year Fast Track (UK / EU)</option>
              <option value="4">4-Year Honours (North America / Asia)</option>
            </select>
          </div>

          {/* Max Annual Budget Slider */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="text-xs font-semibold uppercase text-muted-foreground">
                Max Annual Cost
              </label>
              <span className="font-mono text-xs font-bold text-foreground">
                {maxBudget >= BUDGET_MAX ? "No limit" : `$${maxBudget.toLocaleString()} USD`}
              </span>
            </div>
            <input
              type="range"
              min="20000"
              max="90000"
              step="5000"
              value={maxBudget}
              onChange={(e) => setMaxBudget(Number(e.target.value))}
              className="w-full accent-primary mt-2"
            />
          </div>
        </div>
      </div>

      {/* Results Count & Transparency note */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs text-muted-foreground">
        <span>
          Showing <strong>{filtered.length}</strong>{" "}
          {source === "sanity" ? "university profiles" : "illustrative university profiles"}
        </span>
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-muted-foreground" />
          <span>
            Annual cost = tuition + fees + living, from official sources; budget compared in USD
          </span>
        </div>
      </div>

      {/* Grid of Results */}
      {loading ? (
        <p className="text-sm text-muted-foreground">Loading verified university data…</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-muted-foreground">No universities match your filters.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((univ) => (
            <div
              key={univ.id}
              className="rounded-2xl border border-border bg-card p-6 shadow-xs hover:border-primary/40 transition-all flex flex-col justify-between space-y-5"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-2xl">{univ.flag}</span>
                  <span className="text-xs font-mono bg-secondary px-2.5 py-0.5 rounded text-foreground font-semibold">
                    {univ.durationYears} Years • {univ.costs.currency}
                  </span>
                </div>

                <div>
                  <h3 className="font-display font-bold text-lg text-foreground">{univ.name}</h3>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3 text-muted-foreground" />
                    {univ.city}, {univ.country}
                  </p>
                </div>

                {/* Requirements & Costs */}
                <div className="bg-secondary/40 rounded-xl p-3 border border-border/80 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Academic Threshold:</span>
                    <span className="font-medium text-muted-foreground text-right">
                      {univ.academicRequirements.target}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Annual Total Cost:</span>
                    <span className="font-mono font-bold text-muted-foreground">
                      {formatCost(univ.costs.totalAnnual, univ.costs.currency)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Degree Total Outlay:</span>
                    <span className="font-mono font-semibold text-muted-foreground">
                      {formatCost(univ.costs.totalDegree, univ.costs.currency)}
                    </span>
                  </div>
                </div>

                {/* Affordability Index Badge */}
                <div className="flex items-center justify-between text-xs pt-1">
                  <span className="text-muted-foreground">Affordability Index:</span>
                  <span className="font-semibold px-2 py-0.5 rounded text-[11px] bg-secondary text-muted-foreground">
                    {univ.affordabilityIndex.category}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-border flex items-center justify-between">
                <Link to="/analyze" search={{ uni: univ.id }}>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-border text-foreground hover:bg-secondary text-xs"
                  >
                    Analyze Fit
                  </Button>
                </Link>
                <Button
                  onClick={() => addToMyPath(univ)}
                  disabled={savedIds.has(univ.id)}
                  size="sm"
                  className="bg-primary hover:bg-primary/90 text-primary-foreground text-xs"
                >
                  {savedIds.has(univ.id) ? (
                    <>
                      <Check className="w-3 h-3" /> Saved
                    </>
                  ) : (
                    "Add to My Path"
                  )}
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
