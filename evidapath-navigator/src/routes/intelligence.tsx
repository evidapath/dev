import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import {
  ShieldCheck,
  ArrowRight,
  BookOpen,
  TrendingUp,
  Sparkles,
  Filter,
  FileText,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { INTELLIGENCE_ARTICLES } from "../lib/mock-data";
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
        content: "Analytical briefs and admissions analyses for ambitious families.",
      },
      ogUrlMeta("/intelligence"),
    ],
    links: [canonicalLink("/intelligence")],
  }),
  component: IntelligencePage,
});

function IntelligencePage() {
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = [
    "All",
    "Admissions Intelligence",
    "Affordability",
    "Scholarships & Funding",
    "Global University Markets",
  ];

  const filtered = INTELLIGENCE_ARTICLES.filter(
    (a) => selectedCategory === "All" || a.category === selectedCategory,
  );

  const featured = INTELLIGENCE_ARTICLES.find((a) => a.featured) || INTELLIGENCE_ARTICLES[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      {/* Header */}
      <div className="max-w-3xl space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>EvidaPath Research Publications</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          Evidence for better education decisions.
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Not a generic admissions blog. EvidaPath Intelligence will publish analytical briefs using
          EvidaPath data to explain how academics, affordability, scholarships, and pathways
          interact. The publications below are in development.
        </p>
        <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
          <span>
            Illustrative product preview. Research findings will appear here once produced from
            verified EvidaPath data.
          </span>
        </div>
      </div>

      {/* Featured Research Story */}
      <div className="rounded-3xl border border-border bg-gradient-to-br from-card via-card to-secondary/30 p-8 sm:p-12 shadow-xs space-y-6">
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <span className="font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full">
            Planned Research Brief • {featured.category}
          </span>
          <span className="text-muted-foreground font-mono">{featured.date}</span>
          <span className="text-muted-foreground">{featured.readTime}</span>
        </div>

        <h2 className="text-2xl sm:text-4xl font-display font-extrabold text-foreground leading-tight max-w-4xl">
          {featured.title}
        </h2>

        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-3xl">
          {featured.lead}
        </p>

        {/* Key Takeaway box */}
        <div className="bg-secondary/60 rounded-2xl p-5 border border-border/80 max-w-3xl space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-foreground block">
            Intended Analysis
          </span>
          <p className="text-xs sm:text-sm text-foreground/90 font-medium leading-relaxed">
            {featured.keyTakeaway}
          </p>
          <div className="pt-2 text-[11px] text-muted-foreground font-mono">
            {featured.dataSummary}
          </div>
        </div>

        <div className="pt-2 flex flex-wrap gap-4 items-center">
          <Link to="/fund">
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 text-xs h-10">
              Model Your Budget in Capital Plan →
            </Button>
          </Link>
          <Link to="/universities">
            <Button
              variant="outline"
              className="border-border text-foreground hover:bg-secondary text-xs h-10"
            >
              Explore Underlying University Costs
            </Button>
          </Link>
        </div>
      </div>

      {/* Categories Filter */}
      <div className="flex flex-wrap gap-2 border-b border-border pb-4">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedCategory === cat
                ? "bg-foreground text-background font-semibold"
                : "bg-secondary/60 text-muted-foreground hover:text-foreground"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((article) => (
          <div
            key={article.slug}
            className="rounded-2xl border border-border bg-card p-6 shadow-xs flex flex-col justify-between space-y-6 hover:border-primary/40 transition-all"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">
                  {article.category}
                </span>
                <span className="text-muted-foreground font-mono">{article.readTime}</span>
              </div>

              <h3 className="font-display font-bold text-lg text-foreground leading-snug">
                {article.title}
              </h3>

              <p className="text-xs text-muted-foreground leading-relaxed">{article.lead}</p>

              <div className="bg-secondary/30 rounded-lg p-3 text-[11px] text-muted-foreground border border-border/60">
                <strong className="text-foreground block mb-0.5">Intended analysis:</strong>
                {article.keyTakeaway}
              </div>
            </div>

            <div className="pt-4 border-t border-border flex items-center justify-between">
              <Link
                to="/analyze"
                className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
              >
                <span>Explore in Model</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
              <span className="text-[11px] text-muted-foreground">{article.date}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Annual Flagship Report Teaser: State of University Affordability */}
      <div className="rounded-3xl border border-border bg-secondary/50 p-8 sm:p-10 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <span className="text-[11px] font-bold uppercase tracking-wider text-primary">
            EvidaPath Research • Annual Report
          </span>
          <h3 className="font-display font-bold text-xl sm:text-2xl text-foreground">
            State of University Affordability
          </h3>
          <p className="text-xs sm:text-sm text-muted-foreground">
            What university really costs, and where the opportunities are changing. A planned
            EvidaPath research publication benchmarking net multi-year outlays across major global
            university markets. Report in development.
          </p>
        </div>

        <Link to="/academic-readiness">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 text-xs h-10">
            Request Report & Synthesis →
          </Button>
        </Link>
      </div>
    </div>
  );
}
