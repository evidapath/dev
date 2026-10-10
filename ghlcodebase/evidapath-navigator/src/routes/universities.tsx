import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
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
import { UNIVERSITIES_DATA } from "../lib/mock-data";
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

  const filtered = UNIVERSITIES_DATA.filter((u) => {
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
            Illustrative product preview. Live analysis will use verified EvidaPath data. University
            data currently being verified.
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
            <option value="United Kingdom">United Kingdom</option>
            <option value="Canada">Canada</option>
            <option value="Germany">Germany</option>
            <option value="Netherlands">Netherlands</option>
            <option value="Singapore">Singapore</option>
            <option value="United Arab Emirates">United Arab Emirates</option>
          </select>
        </div>
      </div>

      {/* University Profiles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((univ) => (
          <div
            key={univ.id}
            className="rounded-2xl border border-border bg-card p-6 shadow-xs flex flex-col justify-between space-y-6 hover:border-primary/40 transition-all"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-3xl">{univ.flag}</span>
                <span className="text-xs font-mono font-semibold bg-secondary px-2.5 py-0.5 rounded text-foreground">
                  {univ.durationYears}-Year Degree
                </span>
              </div>

              <div>
                <h3 className="font-display font-bold text-lg text-foreground">{univ.name}</h3>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                  <MapPin className="w-3 h-3 text-muted-foreground" />
                  {univ.city}, {univ.country}
                </p>
              </div>

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
                    {formatCost(univ.costs.tuitionPerYear, univ.costs.currency)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Living / year (Est):</span>
                  <span className="font-mono font-medium text-muted-foreground">
                    {formatCost(univ.costs.livingPerYear, univ.costs.currency)}
                  </span>
                </div>
                <div className="flex justify-between pt-1 border-t border-border/60">
                  <span className="text-muted-foreground font-semibold">Total Degree Outlay:</span>
                  <span className="font-mono font-bold text-muted-foreground">
                    {formatCost(univ.costs.totalDegree, univ.costs.currency)}
                  </span>
                </div>
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
                  <span>
                    Confidence: <strong>{univ.evidenceConfidence}</strong>
                  </span>
                  <span>Verified: {univ.lastVerified}</span>
                </div>
              </div>
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
        ))}
      </div>
    </div>
  );
}
