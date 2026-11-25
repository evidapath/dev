import { createFileRoute, Link } from "@tanstack/react-router";
import { HelpCircle } from "lucide-react";
import type { ReactNode } from "react";
import { PageHeader } from "../components/PageHeader";
import { FitCta } from "../components/FitCta";
import { countryCostPath } from "../lib/paths";
import { at, costAnswer, FeeTable, money, place, Source } from "../components/fees";
import { getAnswers } from "../lib/answers.functions";
import type { CountryCost, FeeFact, RequirementFact } from "../lib/answers.server";
import type { Scholarship } from "../lib/mock-data";
import { formatCost } from "../lib/format";
import { canonicalLink, canonicalUrl, ogUrlMeta } from "../lib/seo";
import { jsonLdScript } from "../lib/structured-data";

// Questions students search for (AnswerThePublic, UAE, 2026-11-19), answered from verified
// records. The first sentence of each answer is the direct answer; the same text goes into
// the FAQPage JSON-LD, so markup and page can't disagree.

type Loaded = NonNullable<Awaited<ReturnType<typeof getAnswers>>>;

function costQuestion(country: string) {
  return `How much does it cost an international student to study in ${place(country)}?`;
}
// One question per country; a country with fees in two currencies gets one table per
// currency inside the same answer (fees in different currencies are never compared).
function byCountry(costs: CountryCost[]): [string, CountryCost[]][] {
  const m = new Map<string, CountryCost[]>();
  for (const c of costs) m.set(c.country, [...(m.get(c.country) ?? []), c]);
  return [...m];
}
function dubai(costs: CountryCost[]) {
  const uae = costs.find((c) => c.country === "United Arab Emirates" && c.currency === "AED");
  const list = uae?.perUniversity.filter((f) => f.city === "Dubai") ?? [];
  if (!list.length) return null;
  return {
    list,
    answer: `Of the ${list.length} Dubai universities on EvidaPath, the lowest yearly tuition for international students is ${money(list[0]!)} for ${at(list[0]!)}.`,
  };
}
const reqLine = (r: RequirementFact) => `${r.university}, ${r.programme}: ${r.text}`;
const unisIn = (rows: RequirementFact[]) => [...new Set(rows.map((r) => r.university))];

function buildFaq(d: Loaded) {
  const qa: { q: string; a: string }[] = [];
  const dub = dubai(d.data.costs);
  if (dub)
    qa.push({
      q: "Which is the cheapest university in Dubai for international students?",
      a: dub.answer,
    });
  for (const [country, groups] of byCountry(d.data.costs))
    qa.push({ q: costQuestion(country), a: groups.map(costAnswer).join(" ") });
  if (d.data.ib.length)
    qa.push({
      q: `What are the IB requirements for ${unisIn(d.data.ib).join(", ")}?`,
      a: d.data.ib.map(reqLine).join(" "),
    });
  if (d.data.english.length)
    qa.push({
      q: "What is the minimum IELTS score for United Arab Emirates University (UAEU)?",
      a: d.data.english.map(reqLine).join(" "),
    });
  if (d.data.sat.length)
    qa.push({
      q: `Do I need the SAT for ${unisIn(d.data.sat).join(", ")}?`,
      a: d.data.sat.map(reqLine).join(" "),
    });
  const { open, nationals } = splitUae(d.uaeScholarships);
  if (open.length)
    qa.push({
      q: "What scholarships are available for international students in the UAE?",
      a:
        `EvidaPath lists ${open.length} scholarships at UAE universities that are not limited to UAE nationals: ${open.map((s) => `${s.name} (${s.provider})`).join("; ")}.` +
        (nationals.length
          ? ` A further ${nationals.length} are for UAE nationals only: ${nationals.map((s) => `${s.name} (${s.provider})`).join("; ")}.`
          : ""),
    });
  return qa;
}

export const Route = createFileRoute("/answers")({
  loader: () => getAnswers(),
  head: ({ loaderData }) => ({
    meta: [
      { title: "Study Abroad Costs and Entry Rules, Answered | EvidaPath" },
      {
        name: "description",
        content:
          "International student tuition by country, the cheapest Dubai universities, IB, IELTS and SAT rules, UAE scholarships. Each figure links to its source.",
      },
      { property: "og:title", content: "Study Abroad Costs and Entry Rules, Answered | EvidaPath" },
      ogUrlMeta("/answers"),
    ],
    links: [canonicalLink("/answers")],
    scripts: loaderData
      ? [
          jsonLdScript({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            url: canonicalUrl("/answers"),
            mainEntity: buildFaq(loaderData).map(({ q, a }) => ({
              "@type": "Question",
              name: q,
              acceptedAnswer: { "@type": "Answer", text: a },
            })),
          }),
        ]
      : [],
  }),
  component: AnswersPage,
});

function QA({ id, q, a, children }: { id: string; q: string; a: string; children?: ReactNode }) {
  return (
    <section
      id={id}
      className="scroll-mt-24 rounded-2xl border border-border bg-card p-6 space-y-3"
    >
      <h2 className="font-display font-bold text-lg text-foreground">{q}</h2>
      <p className="text-[15px] leading-relaxed text-foreground">{a}</p>
      {children}
    </section>
  );
}

function ReqList({ rows }: { rows: RequirementFact[] }) {
  return (
    <ul className="space-y-2 text-sm">
      {rows.map((r) => (
        <li
          key={`${r.university}-${r.programme}-${r.text}`}
          className="border-l-2 border-primary/30 pl-3"
        >
          <span className="font-semibold">
            {r.university}, {r.programme}
          </span>
          {r.curriculum && r.curriculum !== "IB" ? (
            <span className="text-muted-foreground"> ({r.curriculum})</span>
          ) : null}
          : {r.text} <Source url={r.sourceUrl} title={r.sourceTitle} />
        </li>
      ))}
    </ul>
  );
}

// "Nationals only" means the record's eligible citizenships are country codes with no "all"
// (e.g. ["ae"]). Everything else is open to international students, as stored.
function splitUae(rows: Scholarship[]) {
  const nationalsOnly = (s: Scholarship) => {
    const c = s.eligibleCitizenships ?? [];
    return c.length > 0 && !c.includes("all") && c.every((x) => !x.startsWith("not:"));
  };
  return { open: rows.filter((s) => !nationalsOnly(s)), nationals: rows.filter(nationalsOnly) };
}

function ScholarshipList({ rows }: { rows: Scholarship[] }) {
  return (
    <ul className="space-y-2 text-sm">
      {rows.map((s) => (
        <li key={s.id} className="border-l-2 border-primary/30 pl-3">
          <span className="font-semibold">{s.name}</span> ({s.provider})
          {s.awardSummary ? `: ${s.awardSummary}` : ""}{" "}
          {/under review/i.test(s.verificationStatus) ? (
            <span className="text-xs text-muted-foreground">(eligibility under review) </span>
          ) : null}
          {s.officialSource ? <Source url={s.officialSource} title={s.name} /> : null}
        </li>
      ))}
    </ul>
  );
}

function AnswersPage() {
  const d = Route.useLoaderData();
  if (!d)
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center text-sm text-muted-foreground">
        The answers can't load right now. Please try again shortly.
      </div>
    );
  const faq = buildFaq(d);
  const ans = (q: string) => faq.find((x) => x.q === q)?.a ?? "";
  const dub = dubai(d.data.costs);
  const uae = splitUae(d.uaeScholarships);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <PageHeader
        icon={HelpCircle}
        eyebrow="Answers"
        title="Questions students ask,"
        accent="answered with official figures"
        intro="What international students search for most, answered from the universities' own published pages. Each figure links to its source; where a yearly fee is worked out from a per-credit rate or a whole-course total, the table says so. Universities change fees and rules, so confirm with the university before you apply or pay."
      />

      <nav aria-label="Questions" className="rounded-2xl border border-border bg-card p-5 text-sm">
        <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
          {faq.map((x, i) => (
            <li key={x.q}>
              <a href={`#q${i + 1}`} className="hover:text-primary hover:underline">
                {x.q}
              </a>
            </li>
          ))}
        </ol>
      </nav>

      <FitCta />

      {(() => {
        let n = 0;
        const id = () => `q${++n}`;
        return (
          <>
            {dub && (
              <QA
                id={id()}
                q="Which is the cheapest university in Dubai for international students?"
                a={dub.answer}
              >
                <FeeTable rows={dub.list} />
              </QA>
            )}
            {byCountry(d.data.costs).map(([country, groups]) => {
              const q = costQuestion(country);
              return (
                <QA key={q} id={id()} q={q} a={groups.map(costAnswer).join(" ")}>
                  {groups.map((c) => (
                    <div key={c.currency} className="space-y-1">
                      {groups.length > 1 ? (
                        <p className="text-sm font-semibold">Fees in {c.currency}</p>
                      ) : null}
                      <FeeTable rows={c.perUniversity} />
                    </div>
                  ))}
                  <p className="text-sm">
                    <Link to={countryCostPath(country)} className="text-primary underline">
                      Cost of studying in {place(country)}
                    </Link>
                  </p>
                </QA>
              );
            })}
            {d.data.ib.length > 0 &&
              (() => {
                const q = `What are the IB requirements for ${unisIn(d.data.ib).join(", ")}?`;
                return (
                  <QA
                    id={id()}
                    q={q}
                    a="Each programme's IB requirement as the university publishes it:"
                  >
                    <ReqList rows={d.data.ib} />
                  </QA>
                );
              })()}
            {d.data.english.length > 0 && (
              <QA
                id={id()}
                q="What is the minimum IELTS score for United Arab Emirates University (UAEU)?"
                a="UAEU's English requirement as it publishes it, by programme:"
              >
                <ReqList rows={d.data.english} />
              </QA>
            )}
            {d.data.sat.length > 0 &&
              (() => {
                const q = `Do I need the SAT for ${unisIn(d.data.sat).join(", ")}?`;
                return (
                  <QA id={id()} q={q} a="What each programme says about the SAT:">
                    <ReqList rows={d.data.sat} />
                  </QA>
                );
              })()}
            {uae.open.length > 0 && (
              <QA
                id={id()}
                q="What scholarships are available for international students in the UAE?"
                a={`Open to international students (${uae.open.length}):`}
              >
                <ScholarshipList rows={uae.open} />
                {uae.nationals.length > 0 && (
                  <>
                    <p className="text-sm font-semibold pt-2">
                      For UAE nationals only ({uae.nationals.length}):
                    </p>
                    <ScholarshipList rows={uae.nationals} />
                  </>
                )}
                <p className="text-sm">
                  Eligibility and deadlines for each: <Link to="/scholarships">Scholarships</Link>.
                </p>
              </QA>
            )}
          </>
        );
      })()}

      <FitCta />

      <p className="text-sm text-muted-foreground">
        Can't find your university?{" "}
        <Link to="/universities" hash="request-university" className="text-primary underline">
          Ask us to add it
        </Link>
        .
      </p>
    </div>
  );
}
