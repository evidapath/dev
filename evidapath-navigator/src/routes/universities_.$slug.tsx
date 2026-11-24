import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, CalendarDays, ExternalLink, MapPin } from "lucide-react";
import { FitCta } from "../components/FitCta";
import { formatCost, NOT_PUBLISHED } from "../lib/format";
import type { CostView, ProgramView, University } from "../lib/mock-data";
import { countryCostPath, slugify, universityPath } from "../lib/paths";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { jsonLdScript, universityJsonLd } from "../lib/structured-data";
import { loadUniversities } from "../lib/use-live-data";

// One page per university: every programme's fees, entry requirements and deadlines, as
// stored and sourced. Only verified records get a page; the illustrative fallback set
// never does. Missing figures read "Not published"; rows not re-checked say so.
export const Route = createFileRoute("/universities_/$slug")({
  loader: async ({ params }) => {
    const d = await loadUniversities();
    const u =
      d.source === "sanity" ? d.universities.find((x) => slugify(x.name) === params.slug) : null;
    if (!u) throw notFound();
    return u;
  },
  head: ({ loaderData: u }) => {
    if (!u) return {};
    const path = universityPath(u.name);
    const n = u.programDetails?.length ?? 0;
    const title = `${u.name}: Fees and Entry Requirements | EvidaPath`;
    const description = `Tuition, living costs, entry requirements and deadlines for ${n} ${n === 1 ? "programme" : "programmes"} at ${u.name}, ${u.city}, ${u.country}, taken from the university's own pages.`;
    return {
      meta: [
        { title },
        { name: "description", content: description },
        { property: "og:title", content: title },
        { property: "og:description", content: description },
        ogUrlMeta(path),
      ],
      links: [canonicalLink(path)],
      scripts: [jsonLdScript(universityJsonLd(u))],
    };
  },
  component: UniversityPage,
});

// International students first: they are who the site is for.
const TIER_ORDER = ["international", "uniform", "eu", "home", "domestic", "national"];

function longDate(iso: string | null): string {
  if (!iso) return NOT_PUBLISHED;
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "long",
        year: "numeric",
        timeZone: "UTC",
      });
}

function CostRows({
  label,
  c,
}: {
  label?: string | undefined;
  c: CostView & { notChecked?: boolean };
}) {
  return (
    <tr className="border-t border-border align-top">
      <td className="py-2 pr-3 text-muted-foreground">{label ?? "All students"}</td>
      <td className="py-2 pr-3 font-semibold text-foreground">
        {formatCost(c.tuitionPerYear, c.currency)}
      </td>
      <td className="py-2 pr-3">{formatCost(c.mandatoryFees, c.currency)}</td>
      <td className="py-2">
        {formatCost(c.livingPerYear, c.currency)}
        {c.livingSource ? (
          <span className="block text-xs text-muted-foreground">{c.livingSource}</span>
        ) : null}
      </td>
    </tr>
  );
}

function Programme({ p }: { p: ProgramView }) {
  const notChecked = p.costs.notChecked;
  return (
    <section
      id={slugify(p.name)}
      className="rounded-2xl border border-border bg-card p-5 sm:p-6 space-y-4 scroll-mt-20"
    >
      <div>
        <h2 className="font-display font-bold text-lg text-foreground">
          {p.name}
          {p.degree ? ` (${p.degree})` : ""}
        </h2>
        <p className="text-sm text-muted-foreground">
          {p.durationYears > 0 ? `${p.durationYears} years full time` : "Length not published"}
          {p.languages?.length ? ` · Taught in ${p.languages.join(", ").toUpperCase()}` : ""}
        </p>
      </div>

      <div className="overflow-x-auto">
        <h3 className="text-sm font-semibold text-foreground mb-1">Cost per year</h3>
        {notChecked ? (
          <p className="text-xs text-amber-700 dark:text-amber-400 mb-1">
            Not yet re-checked against the university's page.
          </p>
        ) : null}
        <table className="w-full text-sm min-w-[480px]">
          <thead>
            <tr className="text-left text-xs text-muted-foreground">
              <th className="pb-1 pr-3 font-medium">Who</th>
              <th className="pb-1 pr-3 font-medium">Tuition</th>
              <th className="pb-1 pr-3 font-medium">Compulsory fees</th>
              <th className="pb-1 font-medium">Living costs</th>
            </tr>
          </thead>
          <tbody>
            {p.costTiers?.length ? (
              [...p.costTiers]
                .sort((a, b) => TIER_ORDER.indexOf(a.kind) - TIER_ORDER.indexOf(b.kind))
                .map((t) => <CostRows key={t.label} label={t.label} c={t.costs} />)
            ) : (
              <CostRows label={p.costLabel} c={p.costs} />
            )}
          </tbody>
        </table>
        {p.costResidencyNote ? (
          <p className="text-xs text-muted-foreground mt-1">{p.costResidencyNote}</p>
        ) : null}
      </div>

      <div>
        <h3 className="text-sm font-semibold text-foreground mb-1">Entry requirements</h3>
        {p.admissionsByCurriculum.length ? (
          <ul className="space-y-2 text-sm">
            {p.admissionsByCurriculum.map((a) => (
              <li key={a.curriculum} className="border-l-2 border-primary/30 pl-3">
                <span className="font-semibold text-foreground">{a.curriculum}:</span>{" "}
                <span className="text-muted-foreground">
                  {a.summary ?? a.threshold ?? NOT_PUBLISHED}
                </span>
                {a.notChecked ? (
                  <span className="text-xs text-amber-700 dark:text-amber-400">
                    {" "}
                    (not yet re-checked)
                  </span>
                ) : null}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">{NOT_PUBLISHED}</p>
        )}
        <p className="text-sm text-muted-foreground mt-2">
          <span className="font-semibold text-foreground">English:</span>{" "}
          {p.english ?? NOT_PUBLISHED}
        </p>
      </div>
    </section>
  );
}

function UniversityPage() {
  const u: University = Route.useLoaderData();
  const programmes = u.programDetails ?? [];
  const deadlines = (u.deadlines ?? []).filter((d) => d.deadline);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <Link
        to="/universities"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="w-4 h-4" /> All universities
      </Link>

      <header className="space-y-2">
        <p className="text-3xl">{u.flag}</p>
        <h1 className="font-display font-bold text-3xl sm:text-4xl text-foreground leading-tight">
          {u.name}: fees and entry requirements
        </h1>
        <p className="text-sm text-muted-foreground flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="inline-flex items-center gap-1">
            <MapPin className="w-4 h-4" /> {u.city}, {u.country}
          </span>
          {u.type ? <span>{u.type}</span> : null}
          {u.lastVerified ? <span>Checked: {u.lastVerified}</span> : null}
        </p>
        <p className="text-sm text-muted-foreground max-w-2xl">
          {programmes.length} {programmes.length === 1 ? "programme" : "programmes"} on EvidaPath.
          Figures are taken from {u.name}'s own pages; where a figure isn't published, we say so.
          Confirm with the university before you apply or pay.
        </p>
        <div className="flex flex-wrap gap-3 text-sm">
          {u.officialSourceUrl ? (
            <a
              href={u.officialSourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-primary underline"
            >
              Official website <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : null}
          <Link to={countryCostPath(u.country)} className="text-primary underline">
            Cost of studying in {u.country}
          </Link>
        </div>
      </header>

      {programmes.length > 1 ? (
        <nav
          aria-label="Programmes"
          className="rounded-2xl border border-border bg-card p-5 text-sm"
        >
          <p className="font-semibold text-foreground mb-2">Programmes</p>
          <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-1">
            {programmes.map((p) => (
              <li key={p.name}>
                <a
                  href={`#${slugify(p.name)}`}
                  className="text-muted-foreground hover:text-primary hover:underline"
                >
                  {p.name}
                  {p.degree ? ` (${p.degree})` : ""}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}

      {deadlines.length ? (
        <section className="rounded-2xl border border-border bg-card p-5 sm:p-6">
          <h2 className="font-display font-bold text-lg text-foreground flex items-center gap-2">
            <CalendarDays className="w-5 h-5 text-primary" /> Application deadlines
          </h2>
          <ul className="mt-2 space-y-1 text-sm">
            {deadlines.map((d) => (
              <li key={`${d.label}-${d.program ?? ""}`}>
                <span className="font-semibold text-foreground">{longDate(d.deadline)}</span>
                <span className="text-muted-foreground">
                  {" "}
                  · {d.label}
                  {d.program ? ` (${d.program})` : ""}
                  {d.binding ? " · binding" : ""}
                  {d.platform ? ` · apply via ${d.platform}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <FitCta />

      {programmes.map((p) => (
        <Programme key={p.name} p={p} />
      ))}

      <p className="text-sm text-muted-foreground">
        Missing a course?{" "}
        <Link to="/universities" hash="request-university" className="text-primary underline">
          Ask us to add it
        </Link>
        .
      </p>
    </div>
  );
}
