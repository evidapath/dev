import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";
import { costAnswer, FeeTable, place } from "../components/fees";
import { FitCta } from "../components/FitCta";
import { getAnswers } from "../lib/answers.functions";
import { countryCostPath, slugify } from "../lib/paths";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

// Cost of studying in one country: each university's lowest yearly tuition for international
// students, from the same checked records as /answers. Fees in different currencies are
// shown in separate tables, never converted or compared.
export const Route = createFileRoute("/study-in/$country/cost")({
  loader: async ({ params }) => {
    const d = await getAnswers();
    const groups = d?.data.costs.filter((c) => slugify(c.country) === params.country) ?? [];
    if (!groups.length) throw notFound();
    return { country: groups[0]!.country, groups };
  },
  head: ({ loaderData }) => {
    if (!loaderData) return {};
    const { country, groups } = loaderData;
    const path = countryCostPath(country);
    const unis = new Set(groups.flatMap((g) => g.perUniversity.map((f) => f.universityId))).size;
    const title = `Cost of Studying in ${place(country)} for International Students`;
    const description = `Yearly tuition for international students at ${unis} ${unis === 1 ? "university" : "universities"} in ${place(country)}, from each university's own fee page, with the source for every figure.`;
    return {
      meta: [
        { title: title.length <= 48 ? `${title} | EvidaPath` : title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta(path),
      ],
      links: [canonicalLink(path)],
    };
  },
  component: CountryCostPage,
});

function CountryCostPage() {
  const { country, groups } = Route.useLoaderData();
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <Link
        to="/answers"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="w-4 h-4" /> Questions answered
      </Link>
      <header className="space-y-2">
        <h1 className="font-display font-bold text-3xl sm:text-4xl text-foreground leading-tight">
          Cost of studying in {place(country)} for international students
        </h1>
        <p className="text-sm text-muted-foreground max-w-2xl">
          Yearly tuition from each university's own fee page. Each row is the university's
          lowest-fee programme on EvidaPath; open a university to see every programme, living costs
          and entry requirements. Universities change fees, so confirm with the university before
          you apply or pay.
        </p>
      </header>

      {groups.map((g) => (
        <section
          key={g.currency}
          className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-3"
        >
          {groups.length > 1 ? (
            <h2 className="font-display font-bold text-lg text-foreground">Fees in {g.currency}</h2>
          ) : null}
          <p className="text-sm text-foreground">{costAnswer(g)}</p>
          <FeeTable rows={g.perUniversity} />
        </section>
      ))}

      <FitCta />

      <p className="text-sm text-muted-foreground">
        Only fees checked against the university's page are included. Missing a university?{" "}
        <Link to="/universities" hash="request-university" className="text-primary underline">
          Ask us to add it
        </Link>
        .
      </p>
    </div>
  );
}
