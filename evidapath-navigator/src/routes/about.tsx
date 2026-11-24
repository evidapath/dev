import { createFileRoute, Link } from "@tanstack/react-router";
import { ShieldCheck } from "lucide-react";
import type { ReactNode } from "react";
import { PageHeader } from "../components/PageHeader";
import { PRIVACY_EMAIL } from "../lib/legal";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { loadUniversities } from "../lib/use-live-data";

// Who runs EvidaPath and how figures are checked. The method below is the one in the repo's
// CLAUDE.md ("How data gets in"); change both together. Counts come from the live data so
// they can't go stale, and are left out if the data didn't load.
export const Route = createFileRoute("/about")({
  loader: () => loadUniversities(),
  head: () => ({
    meta: [
      { title: "About EvidaPath and How We Check Figures | EvidaPath" },
      {
        name: "description",
        content:
          "EvidaPath is free. Fees, grades and deadlines are quoted from each university's own page; if a figure isn't published, we say so. Here is how we check.",
      },
      { property: "og:title", content: "About EvidaPath and How We Check Figures" },
      ogUrlMeta("/about"),
    ],
    links: [canonicalLink("/about")],
  }),
  component: AboutPage,
});

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-border bg-card p-6 space-y-3">
      <h2 className="font-display font-bold text-lg text-foreground">{title}</h2>
      <div className="space-y-3 text-sm text-muted-foreground leading-relaxed">{children}</div>
    </section>
  );
}

function AboutPage() {
  const d = Route.useLoaderData();
  const unis = d?.source === "sanity" ? d.universities : [];
  const countries = new Set(unis.map((u) => u.country)).size;
  const programmes = unis.reduce((n, u) => n + (u.programDetails?.length || 1), 0);

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <PageHeader
        icon={ShieldCheck}
        eyebrow="About"
        title="Figures you can check,"
        accent="before you decide"
        intro="EvidaPath helps secondary-school students, wherever they live, choose, afford and apply to universities abroad. It's free. A wrong fee, grade or deadline can cost a student a place or a lot of money, so we take figures from the university's own published pages, and the site says so when a figure isn't published."
      />

      <Section title="What's on EvidaPath">
        {unis.length > 0 && (
          <p>
            {unis.length} universities in {countries} countries and {programmes} programmes, with
            tuition, living costs, entry requirements by qualification, English tests and
            application deadlines.
          </p>
        )}
        <p>
          Start with{" "}
          <Link to="/find-my-path" className="text-primary underline">
            Find My Path
          </Link>{" "}
          (4 questions, no sign-in), browse{" "}
          <Link to="/universities" className="text-primary underline">
            universities
          </Link>
          , or read the{" "}
          <Link to="/answers" className="text-primary underline">
            questions students ask
          </Link>
          . Missing a university or course?{" "}
          <Link to="/universities" hash="request-university" className="text-primary underline">
            Ask us to add it
          </Link>
          .
        </p>
      </Section>

      <Section title="How we check a figure">
        <ol className="list-decimal pl-5 space-y-2">
          <li>
            We read the university's own page or PDF (or the government page, where the government
            sets the figure). Search engines, ranking sites and forums are only used to find that
            page, never as the source.
          </li>
          <li>
            We copy the figure word for word, together with the page it came from. Our tools refuse
            to save a number that doesn't appear in the quoted text.
          </li>
          <li>
            If a university doesn't publish a figure, the site says "not published" rather than
            showing an estimate. If two official pages disagree, we show that they disagree.
          </li>
          <li>
            When we work something out (for example a yearly fee from a per-credit rate, or a
            whole-course total spread over the years), we say so.
          </li>
          <li>
            Universities change fees and rules, so always confirm with the university before you
            apply or pay.
          </li>
        </ol>
      </Section>

      <Section title="How EvidaPath is run">
        <p>
          EvidaPath is a small independent project. We don't show ads and we don't sell anyone's
          data. The{" "}
          <Link to="/privacy" className="text-primary underline">
            Privacy Policy
          </Link>{" "}
          says who is responsible for your data and what we collect.
        </p>
      </Section>

      <Section title="Found a mistake?">
        <p>
          Email{" "}
          <a href={`mailto:${PRIVACY_EMAIL}`} className="text-primary underline">
            {PRIVACY_EMAIL}
          </a>{" "}
          with the page and the figure. We check it against the university's page and correct it.
        </p>
      </Section>
    </div>
  );
}
