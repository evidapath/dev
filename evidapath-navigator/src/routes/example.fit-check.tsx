import { createFileRoute, Link } from "@tanstack/react-router";
import { FlaskConical } from "lucide-react";
import { CareerPaths } from "../components/CareerPaths";
import { AnalysisFootnote, DecisionAnalysisView } from "../components/DecisionAnalysisView";
import { PageHeader } from "../components/PageHeader";
import { ScholarshipsAtGlance } from "../components/ScholarshipsAtGlance";
import { VerdictHero } from "../components/VerdictHero";
import { VisaPanel } from "../components/VisaPanel";
import { careerFamily } from "../lib/careers";
import { GRADE_BANDS } from "../lib/curricula";
import { analyze, type StudentInput } from "../lib/decision-engine";
import { slugify } from "../lib/paths";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { loadLive } from "../lib/use-live-data";

// The signed-in fit check (/analyze), run in public for a sample student so search engines,
// AI assistants and visitors can see what it produces. Same code as /analyze, live data; the
// student is made up and the page says so. Built on the server; only the result is sent.
const SAMPLE: StudentInput = {
  curriculum: "IB Diploma",
  gradeBand: GRADE_BANDS[2],
  subject: "Computer Science",
  budgetUsd: 60000,
  citizenship: "India",
  languages: ["en"],
};
const SAMPLE_UNI = "university-of-toronto";

export const Route = createFileRoute("/example/fit-check")({
  loader: async () => {
    const d = await loadLive();
    if (d.source !== "sanity") return null;
    const u = d.universities.find((x) => slugify(x.name) === SAMPLE_UNI);
    if (!u) return null;
    return { u, a: analyze(u, SAMPLE, d.scholarships, d.universities, d.fx) };
  },
  head: () => {
    const title = "Example Fit Check: An IB Student at the University of Toronto | EvidaPath";
    const description =
      "What EvidaPath's fit check shows, run for a sample IB student studying Computer Science with a $60,000 yearly budget: grades, full cost, scholarships, visa and careers.";
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta("/example/fit-check"),
      ],
      links: [canonicalLink("/example/fit-check")],
    };
  },
  component: ExampleFitCheck,
});

function ExampleFitCheck() {
  const d = Route.useLoaderData();
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <PageHeader
        icon={FlaskConical}
        eyebrow="Example"
        title="What a fit check looks like,"
        accent="for a sample student"
        intro="This is EvidaPath's fit check, the same one signed-in students use, run for a made-up student: IB Diploma, grade band IB 34-36, wants Computer Science, Indian citizen, can spend up to $60,000 a year. The university figures are live from our database. Sign in to run it on your own grades and budget."
      />

      {d ? (
        <section className="space-y-4">
          <VerdictHero u={d.u} a={d.a} budgetUsd={SAMPLE.budgetUsd} />
          <ScholarshipsAtGlance a={d.a} uniName={d.u.shortName || d.u.name} />
          <VisaPanel country={d.u.country} />
          <CareerPaths
            family={careerFamily(d.a.program?.fieldOfStudy ?? "", d.a.programName)}
            limit={4}
          />
          <DecisionAnalysisView u={d.u} a={d.a} />
          <AnalysisFootnote />
        </section>
      ) : (
        <p className="text-sm text-muted-foreground">
          The example can't load right now. Please try again shortly.
        </p>
      )}

      <div className="flex flex-wrap gap-3">
        <Link
          to="/sign-in"
          className="inline-flex items-center min-h-11 px-5 rounded-xl bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90"
        >
          Run it for yourself (free account)
        </Link>
        <Link
          to="/find-my-path"
          className="inline-flex items-center min-h-11 px-5 rounded-xl border border-border text-sm font-semibold text-foreground hover:bg-secondary"
        >
          Or try Find My Path, no sign-in
        </Link>
      </div>
    </div>
  );
}
