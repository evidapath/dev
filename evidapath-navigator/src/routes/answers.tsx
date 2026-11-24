import { createFileRoute, Link } from "@tanstack/react-router";
import { HelpCircle } from "lucide-react";
import type { ReactNode } from "react";
import { PageHeader } from "../components/PageHeader";
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

const money = (f: FeeFact) =>
  f.tuition === 0 ? `no tuition fee (0 ${f.currency})` : formatCost(f.tuition, f.currency);
// "the United Kingdom", "the Netherlands"; "Canada", "Germany".
const place = (c: string) => (/^(United |Netherlands)/.test(c) ? `the ${c}` : c);
const at = (f: FeeFact) => `${f.programme} at ${f.university}${f.year ? ` (${f.year})` : ""}`;

function costQuestion(c: CountryCost, multi: boolean) {
  return `How much does it cost an international student to study in ${place(c.country)}?${multi ? ` (fees in ${c.currency})` : ""}`;
}
function costAnswer(c: CountryCost) {
  const unis = `${c.universities} ${c.universities === 1 ? "university" : "universities"}`;
  if (c.lowest.tuition === c.highest.tuition)
    return `On EvidaPath, yearly tuition for international students at ${unis} in ${place(c.country)} is ${money(c.lowest)} for all ${c.programmes} programmes listed${c.lowest.year ? ` (${c.lowest.year})` : ""}.`;
  return `On EvidaPath, yearly tuition for international students at ${unis} in ${place(c.country)} (${c.programmes} programmes) ranges from ${money(c.lowest)} for ${at(c.lowest)} to ${money(c.highest)} for ${at(c.highest)}.`;
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
  const multi = (c: CountryCost) => d.data.costs.filter((x) => x.country === c.country).length > 1;
  const qa: { q: string; a: string }[] = [];
  const dub = dubai(d.data.costs);
  if (dub)
    qa.push({
      q: "Which is the cheapest university in Dubai for international students?",
      a: dub.answer,
    });
  for (const c of d.data.costs) qa.push({ q: costQuestion(c, multi(c)), a: costAnswer(c) });
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

function Source({ url, title }: { url: string | null; title: string | null }) {
  if (!url) return <span className="text-muted-foreground">source on file</span>;
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="text-primary underline">
      {title ? "source" : new URL(url).hostname}
    </a>
  );
}

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

function FeeTable({ rows }: { rows: FeeFact[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm min-w-[520px]">
        <thead className="text-left text-muted-foreground">
          <tr className="border-b border-border">
            <th className="py-2 pr-3 font-semibold">University (lowest-fee programme)</th>
            <th className="py-2 pr-3 font-semibold">Tuition / year</th>
            <th className="py-2 pr-3 font-semibold">Year</th>
            <th className="py-2 font-semibold">Source</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((f) => (
            <tr
              key={`${f.universityId}-${f.programme}`}
              className="border-b border-border/60 align-top"
            >
              <td className="py-2 pr-3">
                {f.university}
                <span className="block text-xs text-muted-foreground">{f.programme}</span>
              </td>
              <td className="py-2 pr-3 tabular-nums font-medium">
                {money(f)}
                {f.note && (
                  <span className="block text-xs font-normal text-muted-foreground max-w-xs">
                    {f.note}
                  </span>
                )}
              </td>
              <td className="py-2 pr-3 text-muted-foreground">{f.year ?? "not stated"}</td>
              <td className="py-2">
                <Source url={f.sourceUrl} title={f.sourceTitle} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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

// The next step for a visitor who arrives from a search: check their own fit.
function FitCta() {
  return (
    <div className="rounded-2xl border border-primary/30 bg-primary/5 p-5 flex flex-col sm:flex-row sm:items-center gap-3 justify-between">
      <p className="text-sm text-foreground">
        <span className="font-semibold">Which of these fit your grades and budget?</span> Answer 4
        questions and see the universities that match, with the same sourced figures. No sign-in
        needed.
      </p>
      <Link
        to="/find-my-path"
        className="inline-flex min-h-11 items-center justify-center rounded-xl bg-primary px-5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 shrink-0"
      >
        Find My Path
      </Link>
    </div>
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
  const multi = (c: CountryCost) => d.data.costs.filter((x) => x.country === c.country).length > 1;
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
            {d.data.costs.map((c) => {
              const q = costQuestion(c, multi(c));
              return (
                <QA key={q} id={id()} q={q} a={costAnswer(c)}>
                  <FeeTable rows={c.perUniversity} />
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
