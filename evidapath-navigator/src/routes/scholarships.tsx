import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import {
  BookOpen,
  ShieldCheck,
  Search,
  Filter,
  ArrowRight,
  DollarSign,
  Award,
  Clock,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { SCHOLARSHIPS_DATA } from "../lib/mock-data";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/scholarships")({
  head: () => ({
    meta: [
      { title: "EvidaPath Scholarship Graph — Funding Intelligence" },
      {
        name: "description",
        content:
          "Don't search thousands of scholarships. Find the ones connected to you through eligibility, citizenship, and academic thresholds — as verified data is added.",
      },
      {
        property: "og:title",
        content: "EvidaPath Scholarship Graph — Funding Intelligence",
      },
      {
        property: "og:description",
        content:
          "Structured scholarship records — currently being built and verified against official sources.",
      },
      ogUrlMeta("/scholarships"),
    ],
    links: [canonicalLink("/scholarships")],
  }),
  component: ScholarshipsGraphPage,
});

function ScholarshipsGraphPage() {
  const [search, setSearch] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("All");

  const filtered = SCHOLARSHIPS_DATA.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.provider.toLowerCase().includes(search.toLowerCase()) ||
      s.universitiesCovered.toLowerCase().includes(search.toLowerCase());

    const matchesCountry =
      selectedCountry === "All" || s.countriesOfStudy.includes(selectedCountry);

    return matchesSearch && matchesCountry;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <BookOpen className="w-3.5 h-3.5" />
          <span>Funding Intelligence</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          EvidaPath Scholarship Graph
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Don't search thousands of generic scholarships. Find the funding structures connected to
          your citizenship, academic profile, and target universities. Scholarship eligibility will
          be evaluated against verified program criteria as records are sourced.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            Illustrative product preview. Live analysis will use verified EvidaPath data.
            Scholarship records currently being verified.
          </span>
        </div>
      </div>

      {/* Filter and Match Bar */}
      <div className="bg-card border border-border rounded-2xl p-5 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by scholarship name, provider, or university..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-10 pl-9 pr-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          />
        </div>

        <div className="w-full md:w-60">
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          >
            <option value="All">All Study Countries</option>
            <option value="Canada">Canada</option>
            <option value="Germany">Germany</option>
            <option value="United Kingdom">United Kingdom</option>
            <option value="Netherlands">Netherlands</option>
            <option value="United Arab Emirates">United Arab Emirates</option>
          </select>
        </div>

        <Link to="/academic-readiness" className="shrink-0 w-full md:w-auto">
          <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs h-10 px-4">
            Match Scholarships to My Profile
          </Button>
        </Link>
      </div>

      {/* Scholarship Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((s) => (
          <div
            key={s.id}
            className="rounded-2xl border border-border bg-card p-6 shadow-xs flex flex-col justify-between space-y-5 hover:border-primary/40 transition-all"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-muted-foreground font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  {s.verificationStatus}
                </span>
                <span className="text-muted-foreground font-mono">{s.lastChecked}</span>
              </div>

              <div>
                <h3 className="font-display font-bold text-lg text-foreground">{s.name}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Provider: <strong>{s.provider}</strong>
                </p>
              </div>

              <div className="bg-secondary/40 rounded-xl p-3 border border-border/80 space-y-2 text-xs">
                <div>
                  <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                    Institutions Covered
                  </span>
                  <span className="font-medium text-foreground">{s.universitiesCovered}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                    Eligible Citizenship
                  </span>
                  <span className="font-medium text-foreground">{s.citizenshipEligible}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block text-[10px] uppercase font-semibold">
                    Academic Threshold
                  </span>
                  <span className="font-medium text-foreground">{s.academicThreshold}</span>
                </div>
              </div>

              <div className="text-xs text-muted-foreground leading-relaxed">
                {s.eligibilitySummary}
              </div>
            </div>

            <div className="pt-4 border-t border-border flex items-center justify-between">
              <div>
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground block">
                  Award Value
                </span>
                <span className="font-mono font-bold text-sm text-muted-foreground">
                  {s.awardValue === null
                    ? "Pending verified data"
                    : `$${s.awardValue.toLocaleString()}`}{" "}
                  / {s.awardFrequency}
                </span>
              </div>

              <Link to="/fund">
                <Button
                  size="sm"
                  variant="outline"
                  className="text-xs border-border text-foreground hover:bg-secondary"
                >
                  Add to Capital Plan
                </Button>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
