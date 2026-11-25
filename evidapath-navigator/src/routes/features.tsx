import { createFileRoute, Link } from "@tanstack/react-router";
import {
  BadgeDollarSign,
  Briefcase,
  CalendarCheck,
  FileCheck2,
  GraduationCap,
  Landmark,
  Plane,
  Scale,
  Sparkles,
} from "lucide-react";
import type { ComponentType, ReactNode } from "react";
import { place } from "../components/fees";
import { FitCta } from "../components/FitCta";
import { PageHeader } from "../components/PageHeader";
import { CURRICULA } from "../lib/curricula";
import { VISAS } from "../lib/visa";
import { canonicalLink, canonicalUrl, ogUrlMeta } from "../lib/seo";
import { jsonLdScript } from "../lib/structured-data";

// What EvidaPath does, in public. Search engines and AI assistants only see public pages,
// so tools that need an account (plan, funding gap, Offer Vault, applications) were invisible
// to them. Each claim below matches the code that does it; change both together:
// curricula (lib/curricula.ts), costs (lib/sanity.server.ts totalIncludes, CostSplit),
// scholarships (decision-engine eligibility/guaranteed), visas (lib/visa.ts, /compare),
// careers (lib/careers.ts, CareerPaths on /analyze), result picks (components/PathwayResults.tsx).

const postStudy = Object.values(VISAS)
  .filter((v) => v.after)
  .map((v) => place(v.country));
const linksOnly = Object.values(VISAS)
  .filter((v) => !v.after)
  .map((v) => place(v.country));
const list = (xs: string[]) =>
  xs.length > 1 ? `${xs.slice(0, -1).join(", ")} and ${xs.at(-1)}` : (xs[0] ?? "");

type Feature = {
  icon: ComponentType<{ className?: string }>;
  title: string;
  body: ReactNode;
  /** The same claim in one plain sentence, for the structured data. */
  plain: string;
  access: "No account needed" | "Free account";
  to?: string;
  cta?: string;
};

const FEATURES: Feature[] = [
  {
    icon: GraduationCap,
    title: "Entry requirements for your qualification",
    plain: `Entry requirements are stored for each programme and each qualification: ${CURRICULA.join("; ")}.`,
    body: (
      <>
        Each programme lists what it asks for by qualification, quoted from the university:{" "}
        {CURRICULA.join("; ")}. Find My Path compares your grade band with the published requirement
        and says when a requirement can't be compared rather than guessing a match.
      </>
    ),
    access: "No account needed",
    to: "/find-my-path",
    cta: "Try Find My Path",
  },
  {
    icon: BadgeDollarSign,
    title: "The full cost, not just tuition",
    plain:
      "Yearly tuition, compulsory fees and living costs, added up over the length of the degree; guaranteed scholarships are taken off to show what you would pay.",
    body: (
      <>
        Tuition, compulsory fees (including health insurance where the university charges it) and
        living costs, added up over the length of the degree. Where a scholarship is guaranteed for
        your grades, it is taken off so you see what your family would actually pay each year.
      </>
    ),
    access: "No account needed",
    to: "/universities",
    cta: "Browse universities",
  },
  {
    icon: Landmark,
    title: "Scholarships you can actually get",
    plain:
      "Scholarships are checked against your citizenship (eligible, not eligible, or check), marked guaranteed or competitive, and shown with the grades they ask for.",
    body: (
      <>
        Each scholarship is checked against your citizenship: eligible, not eligible, or "check"
        when the university's wording isn't clear. Awards are marked guaranteed or competitive and
        show the grades they ask for, and awards meant only for international students are left out
        for students from that country.
      </>
    ),
    access: "No account needed",
    to: "/scholarships",
    cta: "See scholarships",
  },
  {
    icon: Plane,
    title: "Visas and working after you graduate",
    plain: `Student-visa costs and money to show, work rules while studying, and staying to work after graduating, from government pages, for ${list(postStudy)}; official links for ${list(linksOnly)}.`,
    body: (
      <>
        For each country: the student-visa fee, the money you must show, how much you can work while
        studying, and the permit to stay and work after graduating, from government pages. Full
        details for {list(postStudy)}; for {list(linksOnly)} we give the official links only,
        because the figures weren't published clearly or the sites couldn't be read.
      </>
    ),
    access: "No account needed",
    to: "/compare",
    cta: "Compare universities",
  },
  {
    icon: Briefcase,
    title: "Careers and pay",
    plain:
      "Jobs each degree can lead to, with UK pay ranges from the UK government's National Careers Service; in the fit check they sit next to the cost of the degree.",
    body: (
      <>
        The jobs each degree can lead to, with UK pay from starter to experienced (from the UK
        government's National Careers Service). In the fit check for a university, they sit next to
        what the degree costs.
      </>
    ),
    access: "No account needed",
    to: "/careers",
    cta: "Careers by degree",
  },
  {
    icon: Sparkles,
    title: "Options you might not have considered",
    plain:
      "Find My Path picks out the strongest match for your grades, the best value among your matches, universities that meet full financial need, and the closest options above your budget.",
    body: (
      <>
        Find My Path doesn't only list famous names. It picks out the strongest match for your
        grades, the best value among your matches, universities that meet full financial need, and
        the closest options just above your budget, across every country you choose.
      </>
    ),
    access: "No account needed",
    to: "/find-my-path",
    cta: "See your options",
  },
  {
    icon: Scale,
    title: "Your fit at one university, explained",
    plain:
      "A fit check for one university: your grades against its published requirement, its costs, deadlines, scholarships, visa rules and careers in one place, with an optional AI explanation.",
    body: (
      <>
        Pick a university and see your grades against its published requirement, its full cost,
        deadlines, scholarships, visa rules and careers in one place, with an optional AI-written
        explanation of the trade-offs.
      </>
    ),
    access: "Free account",
    to: "/example/fit-check",
    cta: "See an example for a sample student",
  },
  {
    icon: CalendarCheck,
    title: "A dated plan and the family funding gap",
    plain:
      "A dated action plan from your saved universities (application and scholarship deadlines, tests, funding steps), and a funding plan comparing two universities: what your family can pay, expected scholarships, and the gap over the whole degree.",
    body: (
      <>
        A dated plan built from the universities you save: application and scholarship deadlines,
        tests and funding steps. The funding plan compares two universities: enter what your family
        can pay and the scholarships you expect, and see the gap left over the whole degree.
      </>
    ),
    access: "Free account",
  },
  {
    icon: FileCheck2,
    title: "Applications, documents and offers",
    plain:
      "Track applications and decisions, documents and tests, upload offers to the Offer Vault to see the real family cost, and compare offers before you commit.",
    body: (
      <>
        Track applications and decisions, keep documents and test scores together, upload your offer
        letters to the Offer Vault to see the real family cost, and compare offers side by side
        before you commit.
      </>
    ),
    access: "Free account",
  },
];

export const Route = createFileRoute("/features")({
  head: () => {
    const title = "What EvidaPath Does: Features for Students | EvidaPath";
    const description =
      "Entry requirements by qualification, full costs, scholarship eligibility, visas and post-study work, careers, and a dated plan. What's free and what needs an account.";
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta("/features"),
      ],
      links: [canonicalLink("/features")],
      scripts: [
        jsonLdScript({
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "@id": `${canonicalUrl("/")}#app`,
          name: "EvidaPath",
          url: canonicalUrl("/"),
          applicationCategory: "EducationalApplication",
          operatingSystem: "Web browser",
          isAccessibleForFree: true,
          offers: { "@type": "Offer", price: 0, priceCurrency: "USD" },
          featureList: FEATURES.map((f) => `${f.title}: ${f.plain}`),
          publisher: { "@id": `${canonicalUrl("/")}#organization` },
        }),
      ],
    };
  },
  component: FeaturesPage,
});

function FeaturesPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <PageHeader
        icon={Sparkles}
        eyebrow="What EvidaPath does"
        title="Everything a student needs to decide,"
        accent="in one place"
        intro="EvidaPath is free. Some tools work straight away; the ones that keep your plan, saved universities and documents need a free account. Every fee, grade and deadline is taken from the university's or government's own pages, and the site says so when a figure isn't published."
      />

      <div className="grid gap-4">
        {FEATURES.map((f) => (
          <section key={f.title} className="rounded-2xl border border-border bg-card p-5 sm:p-6">
            <div className="flex items-start gap-3">
              <f.icon className="w-6 h-6 text-primary shrink-0 mt-0.5" />
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-display font-bold text-lg text-foreground">{f.title}</h2>
                  <span
                    className={`text-[11px] font-semibold rounded-full px-2 py-0.5 border ${
                      f.access === "No account needed"
                        ? "border-primary/40 text-primary"
                        : "border-border text-muted-foreground"
                    }`}
                  >
                    {f.access}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.body}</p>
                {f.to ? (
                  <Link to={f.to} className="inline-block text-sm text-primary underline">
                    {f.cta}
                  </Link>
                ) : null}
              </div>
            </div>
          </section>
        ))}
      </div>

      <FitCta />

      <p className="text-sm text-muted-foreground">
        How we check figures:{" "}
        <Link to="/about" className="text-primary underline">
          About
        </Link>
        . To save your plan,{" "}
        <Link to="/sign-in" className="text-primary underline">
          create a free account
        </Link>
        .
      </p>
    </div>
  );
}
