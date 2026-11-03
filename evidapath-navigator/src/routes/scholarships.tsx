import { useScholarshipsFn } from "../lib/use-live-data";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { usePaged } from "../lib/use-paged";
import { ShowMore } from "../components/ShowMore";
import {
  BookOpen,
  ShieldCheck,
  Search,
  Filter,
  ArrowRight,
  DollarSign,
  Award,
  Clock,
  Building2,
  CalendarDays,
  Globe2,
  GraduationCap,
} from "lucide-react";
import { Button } from "../components/ui/button";
import type { Scholarship } from "../lib/mock-data";
import { canonicalLink, ogUrlMeta } from "../lib/seo";
import { awardHeadline } from "../lib/award-summary";
import { eligibility, fmtDate } from "../lib/decision-engine";
import { PageHeader, HeaderStats } from "../components/PageHeader";

export const Route = createFileRoute("/scholarships")({
  head: () => ({
    meta: [
      { title: "EvidaPath Scholarship Graph — Funding Intelligence" },
      {
        name: "description",
        content:
          "Don't search thousands of scholarships. Find the ones connected to you through eligibility, citizenship, and academic thresholds — as verified data is added.",
      },
      {
        property: "og:title",
        content: "EvidaPath Scholarship Graph — Funding Intelligence",
      },
      {
        property: "og:description",
        content:
          "Structured scholarship records — currently being built and verified against official sources.",
      },
      ogUrlMeta("/scholarships"),
    ],
    links: [canonicalLink("/scholarships")],
  }),
  component: ScholarshipsGraphPage,
});

const FLAG: Record<string, string> = {
  "United Arab Emirates": "🇦🇪",
  "United Kingdom": "🇬🇧",
  "United States": "🇺🇸",
  Canada: "🇨🇦",
  Australia: "🇦🇺",
  Germany: "🇩🇪",
  Netherlands: "🇳🇱",
  Malaysia: "🇲🇾",
};

type QuickFilter = "uae" | "guaranteed" | "checked";
const QUICK: Record<QuickFilter, { label: string; test: (s: Scholarship) => boolean }> = {
  uae: {
    label: "🇦🇪 Open to UAE students",
    // Same rule the decision engine uses; "check" (unclear) is left out.
    test: (s) => s.countriesOfStudy.some((c) => eligibility(s, "ae", c) === "yes"),
  },
  guaranteed: {
    label: "Guaranteed if you qualify",
    test: (s) => s.selectionBasis === "guaranteed",
  },
  checked: {
    label: "Confirmed on the official page",
    test: (s) => s.verificationStatus.startsWith("Verified"),
  },
};

function ScholarshipsGraphPage() {
  const [search, setSearch] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("All");
  const [quick, setQuick] = useState<Set<QuickFilter>>(new Set());
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [source, setSource] = useState<"sanity" | "mock" | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchScholarships = useScholarshipsFn();
  useEffect(() => {
    let active = true;
    fetchScholarships()
      .then((res) => {
        if (!active) return;
        setScholarships(res.scholarships);
        setSource(res.source);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [fetchScholarships]);

  const countries = useMemo(
    () => Array.from(new Set(scholarships.flatMap((s) => s.countriesOfStudy))).sort(),
    [scholarships],
  );

  const filtered = scholarships.filter((s) => {
    const matchesSearch =
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.provider.toLowerCase().includes(search.toLowerCase()) ||
      s.universitiesCovered.toLowerCase().includes(search.toLowerCase());

    const matchesCountry =
      selectedCountry === "All" || s.countriesOfStudy.includes(selectedCountry);

    return matchesSearch && matchesCountry && [...quick].every((q) => QUICK[q].test(s));
  });
  const paged = usePaged(filtered, `${search}|${selectedCountry}|${[...quick].join()}`);
  const toggle = (q: QuickFilter) =>
    setQuick((cur) => {
      const next = new Set(cur);
      if (next.has(q)) next.delete(q);
      else next.add(q);
      return next;
    });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <PageHeader
        icon={BookOpen}
        eyebrow="Scholarships"
        title="Find the money"
        accent="that fits you."
        intro="Scholarships for the universities on EvidaPath, with who can apply, the grades they ask for and the amount, taken from the official pages."
        note={
          source === "sanity"
            ? "Where an official page doesn't confirm a detail, the card says it's under review."
            : "Illustrative preview. Scholarship records are still being verified."
        }
        aside={
          source === "sanity" && scholarships.length > 0 ? (
            <HeaderStats
              items={[
                [scholarships.length, "scholarships"],
                [scholarships.filter((s) => QUICK.checked.test(s)).length, "confirmed"],
                [scholarships.filter((s) => QUICK.guaranteed.test(s)).length, "guaranteed"],
              ]}
            />
          ) : undefined
        }
      >
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by scholarship, provider or university"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full h-12 pl-11 pr-4 rounded-full border border-input bg-card text-sm text-foreground shadow-xs focus:outline-hidden focus:ring-2 focus:ring-primary"
            />
          </div>
          <Link to="/academic-readiness" className="shrink-0">
            <Button className="w-full h-12 rounded-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm px-6">
              Match to my profile
            </Button>
          </Link>
        </div>
        <div className="flex flex-wrap gap-2">
          {(Object.keys(QUICK) as QuickFilter[]).map((q) => {
            const on = quick.has(q);
            return (
              <button
                key={q}
                type="button"
                onClick={() => toggle(q)}
                aria-pressed={on}
                className={`inline-flex items-center gap-1.5 h-9 px-3.5 rounded-full border text-xs font-semibold transition-colors ${
                  on
                    ? "bg-navy text-white border-navy"
                    : "bg-card text-foreground border-border hover:border-primary/40"
                }`}
              >
                {QUICK[q].label}
              </button>
            );
          })}
        </div>
        <div className="flex sm:flex-wrap gap-2 overflow-x-auto sm:overflow-visible pb-1 -mx-1 px-1 [scrollbar-width:none]">
          {["All", ...countries].map((c) => {
            const on = selectedCountry === c;
            const n =
              c === "All"
                ? scholarships.length
                : scholarships.filter((s) => s.countriesOfStudy.includes(c)).length;
            return (
              <button
                key={c}
                type="button"
                onClick={() => setSelectedCountry(c)}
                aria-pressed={on}
                className={`shrink-0 inline-flex items-center gap-1.5 h-9 px-3.5 rounded-full border text-xs font-semibold transition-colors ${
                  on
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-card text-foreground border-border hover:border-primary/40"
                }`}
              >
                <span className="text-sm leading-none">
                  {c === "All" ? "🌍" : (FLAG[c] ?? "🏳️")}
                </span>
                {c === "All" ? "All countries" : c}
                <span className={on ? "opacity-80" : "text-muted-foreground"}>{n}</span>
              </button>
            );
          })}
        </div>
      </PageHeader>

      {/* Scholarship Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="rounded-2xl border border-border bg-card p-6 space-y-5 motion-safe:animate-in motion-safe:fade-in fill-mode-both"
              style={{ animationDelay: `${Math.min(i, 8) * 60}ms`, animationDuration: "400ms" }}
              aria-hidden="true"
            >
              <div className="animate-pulse space-y-5">
                <div className="flex items-center justify-between">
                  <div className="h-3 w-24 rounded bg-muted" />
                  <div className="h-3 w-16 rounded bg-muted" />
                </div>
                <div className="space-y-2">
                  <div className="h-5 w-3/4 rounded bg-muted" />
                  <div className="h-3 w-1/2 rounded bg-muted" />
                </div>
                <div className="h-24 w-full rounded-xl bg-muted" />
                <div className="h-9 w-full rounded-lg bg-muted" />
              </div>
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-muted-foreground animate-in fade-in duration-300">
          No scholarships match your search.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {paged.visible.map((s, i) => (
            <ScholarshipCard key={s.id} s={s} index={i} />
          ))}
        </div>
      )}
      {!loading && (
        <ShowMore remaining={paged.remaining} onClick={paged.showMore} noun="scholarships" />
      )}
    </div>
  );
}

const PENDING_RE = /^pending|not yet/i;

function ScholarshipCard({ s, index }: { s: Scholarship; index: number }) {
  const head = awardHeadline(
    s.awardSummary ?? (s.awardValue != null ? String(s.awardValue) : undefined),
  );
  const unis = s.universitiesCovered.split(", ").filter((u) => u && !PENDING_RE.test(u));
  const guaranteed = s.selectionBasis === "guaranteed";
  const renewable = s.awardFrequency === "renewable";
  const dated = s.applicationDeadline && /^\d{4}-\d{2}-\d{2}/.test(s.applicationDeadline);
  const details = [
    s.eligibilitySummary,
    s.renewalCriteria && `Renewal: ${s.renewalCriteria}`,
  ].filter((x) => x && !PENDING_RE.test(x));

  return (
    <div
      className="rounded-2xl border border-border bg-card p-5 shadow-xs flex flex-col justify-between gap-4 transition-all duration-200 ease-out hover:border-primary/40 hover:shadow-md hover:-translate-y-0.5 motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-3 fill-mode-both"
      style={{ animationDelay: `${Math.min(index, 8) * 60}ms`, animationDuration: "450ms" }}
    >
      <div className="space-y-3">
        {/* The award, big */}
        <div className={`rounded-xl p-4 ${guaranteed ? "bg-primary/10" : "bg-secondary/60"}`}>
          <p className="font-display text-2xl font-extrabold leading-tight text-foreground">
            {head?.value ?? "See award details"}
          </p>
          <p className="text-xs text-muted-foreground">{head?.label ?? "amount not summarised"}</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {s.selectionBasis && (
              <span
                className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                  guaranteed ? "bg-primary text-primary-foreground" : "bg-bronze/15 text-bronze"
                }`}
                title={
                  guaranteed
                    ? "Every eligible admitted student receives this award."
                    : "Limited awards — applicants are selected; not guaranteed."
                }
              >
                {guaranteed ? "Guaranteed if eligible" : "Competitive"}
              </span>
            )}
            {renewable && (
              <span className="rounded-full bg-background px-2 py-0.5 text-[10px] font-semibold text-foreground border border-border">
                Renewable
              </span>
            )}
            {dated && (
              <span className="rounded-full bg-background px-2 py-0.5 text-[10px] font-semibold text-bronze border border-border inline-flex items-center gap-1">
                <Clock className="w-3 h-3" /> Apply by{" "}
                {fmtDate(s.applicationDeadline!.slice(0, 10))}
              </span>
            )}
          </div>
        </div>

        <div>
          <h3 className="font-display font-bold text-base text-foreground leading-snug">
            {s.name}
          </h3>
          <p className="text-xs text-muted-foreground">{s.provider}</p>
        </div>

        <ul className="space-y-2 text-xs">
          {unis.length > 0 && (
            <Row Icon={Building2} label="Where">
              <span className="flex flex-wrap gap-1">
                {unis.slice(0, 3).map((u) => (
                  <span key={u} className="rounded-md bg-secondary px-1.5 py-0.5 text-foreground">
                    {u}
                  </span>
                ))}
                {unis.length > 3 && (
                  <span className="text-muted-foreground">+{unis.length - 3} more</span>
                )}
              </span>
            </Row>
          )}
          <Row Icon={Globe2} label="Who can apply">
            {/^ALL$/i.test(s.citizenshipEligible.trim())
              ? "All nationalities"
              : s.citizenshipEligible}
          </Row>
          {!PENDING_RE.test(s.academicThreshold) && (
            <Row Icon={GraduationCap} label="Grades">
              <span className="line-clamp-2">{s.academicThreshold}</span>
            </Row>
          )}
          {s.applicationDeadline && !dated && (
            <Row Icon={CalendarDays} label="Deadline">
              <span className="line-clamp-2">{s.applicationDeadline}</span>
            </Row>
          )}
        </ul>

        {(details.length > 0 || (s.awardSummary && head)) && (
          <details className="text-xs">
            <summary className="cursor-pointer select-none font-semibold text-primary">
              Full details
            </summary>
            <div className="mt-1.5 space-y-1.5 text-muted-foreground">
              {s.awardSummary && <p>Award: {s.awardSummary}</p>}
              {!PENDING_RE.test(s.academicThreshold) && <p>Grades: {s.academicThreshold}</p>}
              {details.map((d) => (
                <p key={d}>{d}</p>
              ))}
            </div>
          </details>
        )}
      </div>

      <div className="pt-3 border-t border-border flex items-center justify-between gap-2">
        <span
          className={`text-[10px] flex items-center gap-1 rounded-full px-2 py-0.5 ${
            s.verificationStatus.startsWith("Verified")
              ? "bg-primary/10 text-primary border border-primary/25 font-semibold"
              : "bg-bronze/10 text-bronze"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5" />
          {s.verificationStatus.startsWith("Verified") ? "Confirmed" : s.verificationStatus}
        </span>
        <Link to="/fund">
          <Button
            size="sm"
            variant="outline"
            className="text-xs border-border text-foreground hover:bg-secondary"
          >
            Add to plan
          </Button>
        </Link>
      </div>
    </div>
  );
}

function Row({
  Icon,
  label,
  children,
}: {
  Icon: typeof Globe2;
  label: string;
  children: ReactNode;
}) {
  return (
    <li className="flex gap-2">
      <Icon className="w-4 h-4 text-primary shrink-0 mt-px" />
      <div className="min-w-0">
        <p className="text-[10px] uppercase font-semibold text-muted-foreground">{label}</p>
        <div className="text-foreground">{children}</div>
      </div>
    </li>
  );
}
