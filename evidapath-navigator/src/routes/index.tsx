import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo } from "react";
import { ArrowRight, ShieldCheck, CheckCircle2, Sparkles } from "lucide-react";
import { Button } from "../components/ui/button";
import { PathwaysEntryHero } from "../components/PathwaysEntryHero";
import { DecisionModelDemo } from "../components/DecisionModelDemo";
import { buildBriefs } from "../lib/data-briefs";
import { useLiveData } from "../lib/use-live-data";
import { ReadinessMap } from "../components/ReadinessMap";
import { HowItWorks } from "../components/HowItWorks";
import { UniversityCard } from "../components/UniversityCard";
import { formatCost, formatCurrency } from "../lib/format";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "EvidaPath — Know where you stand. See where you can go." },
      {
        name: "description",
        content:
          "Premium education decision-intelligence platform. Evidence-based academic readiness, university cost modeling, scholarship graphs, and 4-year capital planning.",
      },
      { property: "og:title", content: "EvidaPath — Academic & Financial Decision Intelligence" },
      {
        property: "og:description",
        content: "Pathways, not wishful thinking. Evidence-based academic strategy.",
      },
      { property: "og:type", content: "website" },
      ogUrlMeta("/"),
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [canonicalLink("/")],
  }),
  component: Index,
});

function Index() {
  // Featured cards come from live data: universities with a verified full annual
  // cost, and scholarships whose guaranteed/competitive basis is confirmed.
  const { data } = useLiveData();
  const featuredUnis = useMemo(() => {
    const all = data?.universities ?? [];
    // Fully priced and checked, one per country, so the preview shows a spread.
    const good = all.filter(
      (u) => u.costs.totalAnnual != null && u.evidenceConfidence.startsWith("Verified"),
    );
    const seen = new Set<string>();
    const spread = good.filter((u) => !seen.has(u.country) && seen.add(u.country));
    return (spread.length >= 3 ? spread : good.length >= 3 ? good : all).slice(0, 3);
  }, [data]);
  const stats = useMemo(() => {
    const unis = data?.universities ?? [];
    if (!unis.length) return null;
    return [
      [unis.length, "universities"],
      [new Set(unis.map((u) => u.country)).size, "countries"],
      [unis.reduce((n, u) => n + (u.programDetails?.length || 1), 0), "programmes"],
      [
        (data?.scholarships ?? []).filter((x) => x.verificationStatus.startsWith("Verified"))
          .length,
        "scholarships checked",
      ],
    ] as const;
  }, [data]);
  const briefs = useMemo(() => (data ? buildBriefs(data) : []), [data]);
  const featuredScholarships = useMemo(() => {
    const all = data?.scholarships ?? [];
    const confirmed = all.filter(
      (s) => s.verificationStatus.startsWith("Verified") && !!s.awardSummary,
    );
    return (confirmed.length >= 3 ? confirmed : all).slice(0, 3);
  }, [data]);

  return (
    <div className="space-y-20 sm:space-y-28 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative pt-12 sm:pt-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Warm glows behind the headline, then the subtle grid */}
        <div
          aria-hidden
          className="absolute inset-x-0 top-0 -z-10 h-[640px] bg-[radial-gradient(40%_50%_at_30%_10%,oklch(0.6_0.17_155/0.12),transparent),radial-gradient(35%_45%_at_75%_5%,oklch(0.53_0.15_62/0.10),transparent)]"
        />
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#0000000a_1px,transparent_1px),linear-gradient(to_bottom,#0000000a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-[1.15fr_0.85fr] gap-12 items-center">
          <div className="text-center lg:text-left space-y-6">
            {/* Socratic Navigator Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-secondary/70 text-xs font-semibold text-foreground tracking-wide">
              <span className="w-2 h-2 rounded-full bg-primary" />
              <span>The Socratic Navigator • Evidence-Based Academic Strategy</span>
            </div>

            <h1 className="text-4xl sm:text-6xl xl:text-7xl font-display font-extrabold tracking-tight text-foreground leading-[1.08]">
              Know where you stand. <br className="hidden sm:inline" />
              <span className="font-serif italic font-medium text-primary tracking-normal">
                See where you can go.
              </span>
            </h1>

            <p className="max-w-2xl mx-auto lg:mx-0 text-base sm:text-xl text-muted-foreground leading-relaxed">
              University decisions combine academics, admissions, money, geography and career
              outcomes. EvidaPath brings the evidence together so students and families can
              understand where they stand, what is financially realistic, and what they can do next.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-2">
              <Link to="/find-my-path" className="w-full sm:w-auto">
                <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 h-12 rounded-xl text-base shadow-sm flex items-center justify-center gap-2">
                  <span>Find My Path</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link to="/universities" className="w-full sm:w-auto">
                <Button
                  variant="outline"
                  className="w-full sm:w-auto border-border bg-card hover:bg-secondary text-foreground font-semibold px-6 h-12 rounded-xl text-base"
                >
                  Explore Universities
                </Button>
              </Link>
            </div>

            <p className="text-xs text-muted-foreground pt-1">
              Tell us a few things about yourself and see realistic options.
            </p>

            {/* Core supporting mottos */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-x-6 gap-y-2 pt-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
                Pathways, not wishful thinking
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
                Evidence-based academic strategy
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-primary" />
                Turn ambition into a plan
              </span>
            </div>
            {stats && (
              <dl className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 max-w-2xl mx-auto lg:mx-0">
                {stats.map(([v, k]) => (
                  <div
                    key={k}
                    className="rounded-2xl border border-border bg-card/80 backdrop-blur px-4 py-3 text-left shadow-xs"
                  >
                    <dd className="font-display font-extrabold text-2xl text-foreground tabular-nums leading-none">
                      {v}
                    </dd>
                    <dt className="text-[11px] text-muted-foreground mt-1">{k}</dt>
                  </div>
                ))}
              </dl>
            )}
          </div>

          {/* A real card from the database, so families see what they get */}
          {featuredUnis[0] && (
            <div className="hidden lg:block relative">
              <div
                aria-hidden
                className="absolute -inset-6 rounded-[2rem] bg-[radial-gradient(60%_60%_at_50%_40%,oklch(0.6_0.17_155/0.18),transparent)]"
              />
              <p className="relative mb-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                Live example from the database
              </p>
              <div className="relative rounded-2xl shadow-2xl shadow-primary/10 hover:-translate-y-1 transition-transform duration-300">
                <UniversityCard univ={featuredUnis[0]} />
              </div>
            </div>
          )}
        </div>

        {/* 2. TWO PRIMARY ENTRY PATHWAYS */}
        <PathwaysEntryHero />
      </section>

      {/* 3. HOW IT WORKS — 4-step flow diagram */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <HowItWorks />
      </section>

      {/* 4. THE EVIDAPATH DECISION MODEL (INTERACTIVE) */}
      <section className="band max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-8">
          <span className="text-xs font-bold uppercase tracking-wider text-primary">
            Rigorous Analytical Framework
          </span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-2">
            The EvidaPath Decision Model
          </h2>
          <p className="text-sm sm:text-base text-muted-foreground mt-2">
            We do not reduce students to simplistic probability scores. We organize available
            evidence across six core dimensions so families make confident, transparent decisions.
          </p>
        </div>

        <DecisionModelDemo data={data} />
      </section>

      {/* 5. ACADEMIC READINESS PROFILE CALLOUT */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-secondary/80 to-cream border border-border rounded-3xl p-8 sm:p-12 flex flex-col lg:flex-row items-center justify-between gap-8">
          <div className="space-y-4 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Diagnostic Engine</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-display font-extrabold text-foreground">
              Turn your academic record into a decision map.
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
              Enter your curriculum, grades or predicted grades, subject interests, geographic
              preferences, and family budget. The system reveals where your current evidence creates
              opportunities, where gaps exist, and which levers are still actionable.
            </p>
            <div className="pt-2">
              <Link to="/find-my-path">
                <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 h-11 rounded-xl flex items-center gap-2">
                  <span>Find My Path</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>

          <ReadinessMap data={data} />
        </div>
      </section>

      {/* 6. UNIVERSITY COST DATABASE PREVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              EvidaPath University Cost Database
            </span>
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-1">
              The university database built around decisions, not rankings.
            </h2>
            <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
              Compare academic requirements, living costs, degree duration, and institutional
              funding rather than relying on vanity league tables.
            </p>
          </div>

          <Link to="/universities">
            <Button
              variant="outline"
              className="border-border text-foreground hover:bg-secondary flex items-center gap-1.5"
            >
              <span>Browse University Database</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredUnis.map((univ, i) => (
            <UniversityCard key={univ.id} univ={univ} index={i} />
          ))}
        </div>
      </section>

      {/* 7. SCHOLARSHIP GRAPH PREVIEW */}
      <section className="band max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div>
          <div className="max-w-3xl mb-8">
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              EvidaPath Scholarship Graph
            </span>
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-2">
              Don’t search thousands of scholarships. Find the ones connected to you.
            </h2>
            <p className="text-sm text-muted-foreground mt-2">
              Structured scholarship intelligence connecting students via eligibility criteria,
              citizenship, subject restrictions, and renewable terms.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {featuredScholarships.map((scholarship) => (
              <div
                key={scholarship.id}
                className="bg-card rounded-xl border border-border p-5 shadow-xs flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-muted-foreground font-semibold flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {scholarship.verificationStatus}
                    </span>
                    <span className="text-muted-foreground font-mono">
                      {scholarship.lastChecked}
                    </span>
                  </div>
                  <h4 className="font-display font-bold text-sm text-foreground">
                    {scholarship.name}
                  </h4>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {scholarship.eligibilitySummary}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-border flex items-center justify-between text-xs">
                  <span className="font-mono font-medium text-muted-foreground line-clamp-2 pr-3">
                    {scholarship.awardSummary
                      ? scholarship.awardSummary
                      : scholarship.awardValue === null
                        ? "Amount not published"
                        : `${formatCurrency(scholarship.awardValue, "USD")} / ${scholarship.awardFrequency}`}
                  </span>
                  <Link to="/scholarships" className="text-primary font-semibold hover:underline">
                    View Criteria →
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 flex justify-center">
            <Link to="/scholarships">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6">
                Match Scholarships to My Profile
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* 8. EVIDAPATH INTELLIGENCE RESEARCH */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              EvidaPath Intelligence & Research
            </span>
            <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-1">
              Evidence for better education decisions.
            </h2>
            <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
              Live data briefs on costs, admissions, scholarships and deadlines — computed straight
              from EvidaPath's verified records.
            </p>
          </div>

          <Link to="/intelligence">
            <Button variant="outline" className="border-border text-foreground hover:bg-secondary">
              All data briefs
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {briefs.slice(0, 3).map((article) => (
            <div
              key={article.slug}
              className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs mb-3">
                  <span className="font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">
                    {article.category}
                  </span>
                  <span className="text-muted-foreground">Live data</span>
                </div>
                <h3 className="font-display font-bold text-base text-foreground leading-snug">
                  {article.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-2 line-clamp-3">{article.lead}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-border">
                <Link
                  to="/intelligence"
                  hash={article.slug}
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  <span>Read the brief</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
