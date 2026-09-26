import { createFileRoute, Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Compass,
  BarChart3,
  ShieldCheck,
  DollarSign,
  BookOpen,
  Layers,
  CheckCircle2,
  TrendingUp,
  Sparkles,
  Scale,
  GraduationCap,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { PathwaysEntryHero } from "../components/PathwaysEntryHero";
import { DecisionModelDemo } from "../components/DecisionModelDemo";
import { UNIVERSITIES_DATA, SCHOLARSHIPS_DATA, INTELLIGENCE_ARTICLES } from "../lib/mock-data";
import { formatCost } from "../lib/format";
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
  return (
    <div className="space-y-20 sm:space-y-28 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative pt-12 sm:pt-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Subtle grid background pattern */}
        <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#0000000a_1px,transparent_1px),linear-gradient(to_bottom,#0000000a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

        <div className="max-w-5xl mx-auto text-center space-y-6">
          {/* Socratic Navigator Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-secondary/70 text-xs font-semibold text-foreground tracking-wide">
            <span className="w-2 h-2 rounded-full bg-primary" />
            <span>The Socratic Navigator • Evidence-Based Academic Strategy</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-display font-extrabold tracking-tight text-foreground leading-[1.08]">
            Know where you stand. <br className="hidden sm:inline" />
            <span className="text-primary">See where you can go.</span>
          </h1>

          <p className="max-w-3xl mx-auto text-base sm:text-xl text-muted-foreground leading-relaxed">
            University decisions combine academics, admissions, money, geography and career
            outcomes. EvidaPath brings the evidence together so students and families can understand
            where they stand, what is financially realistic, and what they can do next.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
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
          <div className="flex flex-wrap items-center justify-center gap-6 pt-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
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
        </div>

        {/* 2. TWO PRIMARY ENTRY PATHWAYS */}
        <PathwaysEntryHero />
      </section>

      {/* 3. THE 4 INTERCONNECTED QUESTIONS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="text-xs font-bold uppercase tracking-wider text-primary">
            Continuous Decision Intelligence
          </span>
          <h2 className="text-3xl sm:text-4xl font-display font-bold text-foreground mt-2">
            Four Interconnected Questions for Every Family
          </h2>
          <p className="text-sm sm:text-base text-muted-foreground mt-2">
            Higher education is not a linear application checklist. It is a multi-dimensional
            capital and academic allocation strategy.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Discover */}
          <div className="p-6 rounded-2xl border border-border bg-card shadow-xs hover:border-primary/50 transition-all flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground">
                <Compass className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Question 01
              </span>
              <h3 className="font-display font-bold text-lg text-foreground">DISCOVER</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                What universities and global pathways fit my academic profile, ambitions, geography,
                and financial reality?
              </p>
            </div>
            <Link
              to="/discover"
              className="mt-6 pt-4 border-t border-border flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
            >
              <span>Explore Pathways</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Card 2: Analyze */}
          <div className="p-6 rounded-2xl border border-border bg-card shadow-xs hover:border-primary/50 transition-all flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground">
                <BarChart3 className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Question 02
              </span>
              <h3 className="font-display font-bold text-lg text-foreground">ANALYZE</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                Where do I currently stand relative to the available evidence for a particular
                university or program?
              </p>
            </div>
            <Link
              to="/analyze"
              className="mt-6 pt-4 border-t border-border flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
            >
              <span>Run Profile Analysis</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Card 3: Plan */}
          <div className="p-6 rounded-2xl border border-border bg-card shadow-xs hover:border-primary/50 transition-all flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground">
                <Layers className="w-5 h-5 text-primary" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Question 03
              </span>
              <h3 className="font-display font-bold text-lg text-foreground">PLAN</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                What gaps exist, which ones can realistically be changed, and what should I do next?
              </p>
            </div>
            <Link
              to="/plan"
              className="mt-6 pt-4 border-t border-border flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
            >
              <span>View Controllable Levers</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {/* Card 4: Fund */}
          <div className="p-6 rounded-2xl border border-border bg-card shadow-xs hover:border-primary/50 transition-all flex flex-col justify-between">
            <div className="space-y-3">
              <div className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-foreground">
                <DollarSign className="w-5 h-5 text-bronze" />
              </div>
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Question 04
              </span>
              <h3 className="font-display font-bold text-lg text-foreground">FUND</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                What will this education actually cost, what funding could apply, and what is the
                financial gap the family needs to solve?
              </p>
            </div>
            <Link
              to="/fund"
              className="mt-6 pt-4 border-t border-border flex items-center gap-1.5 text-xs font-semibold text-bronze hover:underline"
            >
              <span>Model Capital Plan</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </section>

      {/* 4. THE EVIDAPATH DECISION MODEL (INTERACTIVE) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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

        <DecisionModelDemo />
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

          {/* Visual Mini Diagnostic Preview Card */}
          <div className="w-full lg:w-96 bg-card rounded-2xl border border-border p-5 shadow-sm space-y-3.5">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <span className="text-xs font-semibold text-foreground">Sample Readiness Map</span>
              <span className="text-[10px] bg-secondary text-muted-foreground px-2 py-0.5 rounded font-mono">
                Illustrative preview
              </span>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-muted-foreground">High Readiness Programs:</span>
                <span className="font-mono font-medium text-muted-foreground">Pending data</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Prerequisite Action Needed:</span>
                <span className="font-mono font-medium text-muted-foreground">Pending data</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Average Net Degree Cost:</span>
                <span className="font-mono font-medium text-muted-foreground">Pending data</span>
              </div>
            </div>
            <div className="pt-2 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground">
              <span>Confidence: Pending verified data</span>
              <span className="text-muted-foreground font-medium">Illustrative preview</span>
            </div>
          </div>
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

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {UNIVERSITIES_DATA.slice(0, 3).map((univ) => (
            <div
              key={univ.id}
              className="rounded-2xl border border-border bg-card p-6 shadow-xs hover:border-primary/40 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-2xl">{univ.flag}</span>
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-secondary text-foreground font-semibold">
                    {univ.durationYears}-Year Degree
                  </span>
                </div>
                <h3 className="font-display font-bold text-lg text-foreground">{univ.name}</h3>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {univ.city}, {univ.country}
                </p>

                <div className="mt-4 pt-4 border-t border-border space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Academic Target:</span>
                    <span className="font-medium text-muted-foreground text-right">
                      {univ.academicRequirements.target}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Annual Total Cost:</span>
                    <span className="font-mono font-medium text-muted-foreground">
                      {formatCost(univ.costs.totalAnnual, univ.costs.currency)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Affordability Index:</span>
                    <span className="font-semibold text-muted-foreground">
                      {univ.affordabilityIndex.category}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-border flex items-center justify-between">
                <Link to="/analyze" className="text-xs font-semibold text-primary hover:underline">
                  Analyze Fit →
                </Link>
                <Link
                  to="/universities"
                  className="text-xs text-muted-foreground hover:text-foreground"
                >
                  View Full Profile
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 7. SCHOLARSHIP GRAPH PREVIEW */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-secondary/40 border border-border rounded-3xl p-8 sm:p-12">
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
            {SCHOLARSHIPS_DATA.slice(0, 3).map((scholarship) => (
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
                  <span className="font-mono font-medium text-muted-foreground">
                    {scholarship.awardValue === null
                      ? "Pending verified data"
                      : `$${scholarship.awardValue.toLocaleString()}`}{" "}
                    / {scholarship.awardFrequency}
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
              Research publications examining how academics, affordability, scholarships, geography,
              and pathways interact.
            </p>
          </div>

          <Link to="/intelligence">
            <Button variant="outline" className="border-border text-foreground hover:bg-secondary">
              All Research Articles
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {INTELLIGENCE_ARTICLES.slice(0, 3).map((article) => (
            <div
              key={article.slug}
              className="rounded-2xl border border-border bg-card p-6 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs mb-3">
                  <span className="font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">
                    {article.category}
                  </span>
                  <span className="text-muted-foreground">{article.readTime}</span>
                </div>
                <h3 className="font-display font-bold text-base text-foreground leading-snug">
                  {article.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-2 line-clamp-3">{article.lead}</p>
              </div>

              <div className="mt-6 pt-4 border-t border-border">
                <Link
                  to="/intelligence"
                  className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                >
                  <span>Read Brief & Data Model</span>
                  <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 9. TRUST, METHODOLOGY & CONTINUOUS ROADMAP */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border border-border rounded-3xl bg-card p-8 sm:p-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div className="space-y-4">
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                Trust & Verification
              </span>
              <h2 className="text-3xl font-display font-bold text-foreground">
                Evidence before opinion.
              </h2>
              <p className="text-sm text-muted-foreground leading-relaxed">
                EvidaPath is being built to distinguish verified facts, institutional information,
                estimates, and analytical interpretation. Source attribution and verification dates
                will appear as verified data is added. We do not claim that something has been
                verified merely because it appears in the current prototype.
              </p>
              <div className="space-y-2 pt-2 text-xs text-foreground font-medium">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>
                    Cost-of-attendance figures will be added with source attribution and
                    verification dates as data is verified.
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>
                    Uncertainty will be communicated explicitly rather than manufacturing precision.
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  <span>Actionable levers prioritized by student control and real impact.</span>
                </div>
              </div>
            </div>

            <div className="bg-secondary/60 rounded-2xl p-6 border border-border space-y-4">
              <h3 className="font-display font-bold text-base text-foreground">
                The Continuous Decision Loop
              </h3>
              <div className="space-y-3 text-xs">
                <div className="flex items-center gap-3 bg-card p-2.5 rounded-lg border border-border">
                  <span className="font-mono font-bold text-primary">01</span>
                  <span className="font-semibold text-foreground">Student Profile</span>
                  <span className="text-muted-foreground">
                    → Academic prerequisites & budget bounds
                  </span>
                </div>
                <div className="flex items-center gap-3 bg-card p-2.5 rounded-lg border border-border">
                  <span className="font-mono font-bold text-primary">02</span>
                  <span className="font-semibold text-foreground">Discover & Analyze</span>
                  <span className="text-muted-foreground">→ Benchmark against evidence</span>
                </div>
                <div className="flex items-center gap-3 bg-card p-2.5 rounded-lg border border-border">
                  <span className="font-mono font-bold text-primary">03</span>
                  <span className="font-semibold text-foreground">Plan & Fund</span>
                  <span className="text-muted-foreground">
                    → Actionable levers & 4-year capital plan
                  </span>
                </div>
                <div className="flex items-center gap-3 bg-card p-2.5 rounded-lg border border-border">
                  <span className="font-mono font-bold text-primary">04</span>
                  <span className="font-semibold text-foreground">Outcomes</span>
                  <span className="text-muted-foreground">→ Longitudinal value verification</span>
                </div>
              </div>

              <div className="pt-2">
                <Link to="/find-my-path">
                  <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold">
                    Find My Path
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
