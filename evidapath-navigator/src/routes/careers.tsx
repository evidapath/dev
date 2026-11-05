import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Briefcase } from "lucide-react";
import { PageHeader } from "../components/PageHeader";
import { CareerPaths } from "../components/CareerPaths";
import { careersFor, FAMILY_LABEL, type CareerFamily } from "../lib/careers";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

const FAMILIES = Object.keys(FAMILY_LABEL) as CareerFamily[];

export const Route = createFileRoute("/careers")({
  validateSearch: (s: Record<string, unknown>): { subject?: CareerFamily } =>
    FAMILIES.includes(s["subject"] as CareerFamily)
      ? { subject: s["subject"] as CareerFamily }
      : {},
  head: () => ({
    meta: [
      { title: "Careers by Degree — EvidaPath" },
      {
        name: "description",
        content:
          "What each degree can lead to: jobs, UK pay from starter to experienced, and the degree subjects each job takes, from the UK government's National Careers Service.",
      },
      { property: "og:title", content: "Careers by Degree — EvidaPath" },
      ogUrlMeta("/careers"),
    ],
    links: [canonicalLink("/careers")],
  }),
  component: CareersPage,
});

function CareersPage() {
  const { subject = "computing" } = Route.useSearch();
  const navigate = useNavigate({ from: "/careers" });

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <PageHeader
        icon={Briefcase}
        eyebrow="Careers"
        title="What can your degree"
        accent="lead to?"
        intro="Pick a subject to see the jobs it commonly leads to, what they pay, and which degrees each job takes."
        note="Job profiles from the UK government's National Careers Service. Pay is the UK range from starter to experienced."
      >
        <div className="flex flex-wrap gap-2" role="tablist" aria-label="Subject">
          {FAMILIES.map((f) => (
            <button
              key={f}
              role="tab"
              aria-selected={subject === f}
              onClick={() => navigate({ search: { subject: f }, replace: true })}
              className={`h-9 px-3.5 rounded-full border text-xs font-semibold transition-colors ${
                subject === f
                  ? "bg-primary text-primary-foreground border-primary shadow-sm"
                  : "bg-card text-foreground border-border hover:border-primary/40"
              }`}
            >
              {FAMILY_LABEL[f]} <span className="opacity-70">{careersFor(f).length}</span>
            </button>
          ))}
        </div>
      </PageHeader>
      <CareerPaths family={subject} />
    </div>
  );
}
