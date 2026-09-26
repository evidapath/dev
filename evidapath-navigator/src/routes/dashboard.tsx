import { createFileRoute, Link } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Compass,
  BarChart3,
  CalendarCheck,
  PiggyBank,
  GraduationCap,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Vault,
  Scale,
  ClipboardList,
  CheckCircle2,
  Circle,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { useAuth } from "../components/AuthContext";
import { requireAuth } from "../lib/route-guard";
import { DataStatus } from "../components/DataStatus";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: ({ context, location }) => requireAuth(context, location.pathname),
  head: () => ({
    meta: [
      { title: "My EvidaPath — Dashboard" },
      {
        name: "description",
        content:
          "Your personal EvidaPath member area: what to do next, applications, offers, and funding.",
      },
      { property: "og:title", content: "My EvidaPath — Dashboard" },
      {
        property: "og:description",
        content: "Your continuous education decision-intelligence roadmap.",
      },
    ],
  }),
  component: DashboardPage,
});

// Next-step logic — answers "What should I do next?"
// Ordered journey: Profile → Explore → Applications → Offers → Funding
const JOURNEY = [
  {
    step: 1,
    label: "Academic Readiness",
    desc: "Complete your profile so EvidaPath can map your evidence.",
    href: "/academic-readiness",
    icon: Sparkles,
  },
  {
    step: 2,
    label: "Explore universities",
    desc: "Choose 3–5 universities to explore in depth.",
    href: "/universities",
    icon: Compass,
  },
  {
    step: 3,
    label: "Add your applications",
    desc: "Track the universities you're applying to.",
    href: "/applications",
    icon: ClipboardList,
  },
  {
    step: 4,
    label: "Record your offers",
    desc: "Add admission offers and scholarship awards to your Offer Vault.",
    href: "/offer-vault",
    icon: Vault,
  },
  {
    step: 5,
    label: "Compare & fund",
    desc: "Compare offers and model your family's funding gap.",
    href: "/fund",
    icon: PiggyBank,
  },
];

function DashboardPage() {
  const { user } = useAuth();

  // MVP: no persisted progress yet, so we surface the first step as the
  // active "Next Step". When profile state is connected, this becomes dynamic.
  const currentStep = 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* Welcome header */}
      <div className="space-y-3 max-w-3xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
          <LayoutDashboard className="w-3.5 h-3.5" />
          <span>My EvidaPath</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-display font-extrabold text-foreground">
          What should I do next?
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
          Signed in as{" "}
          <span className="font-medium text-foreground">{user?.email ?? "EvidaPath member"}</span>.
          Follow your path one step at a time — complexity appears only when you need it.
        </p>
      </div>

      {/* Next Step panel — dominant, action-oriented */}
      <div className="rounded-2xl border border-primary/30 bg-primary/5 p-6 sm:p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-xl">
          <p className="text-[11px] font-bold uppercase tracking-wider text-primary">
            Your next step
          </p>
          <h2 className="text-xl sm:text-2xl font-display font-bold text-foreground">
            {JOURNEY[currentStep].label}
          </h2>
          <p className="text-sm text-muted-foreground">{JOURNEY[currentStep].desc}</p>
        </div>
        <Link to={JOURNEY[currentStep].href} className="shrink-0">
          <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6 h-11 flex items-center gap-2">
            Continue <ArrowRight className="w-4 h-4" />
          </Button>
        </Link>
      </div>

      {/* Journey progress — what comes next */}
      <div className="space-y-4">
        <h3 className="font-display font-bold text-base text-foreground">Your path</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {JOURNEY.map((j, i) => {
            const Icon = j.icon;
            const done = i < currentStep;
            const active = i === currentStep;
            return (
              <Link
                key={j.step}
                to={j.href}
                className={`rounded-xl border p-4 flex flex-col gap-2 transition-all ${
                  active
                    ? "border-primary/50 bg-primary/5 shadow-xs"
                    : "border-border bg-card hover:border-primary/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-muted-foreground">
                    {String(j.step).padStart(2, "0")}
                  </span>
                  {done ? (
                    <CheckCircle2 className="w-4 h-4 text-primary" />
                  ) : active ? (
                    <Circle className="w-4 h-4 text-primary fill-primary/20" />
                  ) : (
                    <Circle className="w-4 h-4 text-border" />
                  )}
                </div>
                <Icon className="w-4 h-4 text-muted-foreground" />
                <span className="text-xs font-semibold text-foreground leading-snug">
                  {j.label}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Quick access to product modules (secondary) */}
      <div className="space-y-4">
        <h3 className="font-display font-bold text-base text-foreground">Quick access</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[
            {
              label: "Analyze My Fit",
              desc: "Where you stand vs. evidence",
              href: "/analyze",
              icon: BarChart3,
            },
            {
              label: "My Plan",
              desc: "Actions by timing & control",
              href: "/plan",
              icon: CalendarCheck,
            },
            {
              label: "Offer Vault",
              desc: "Store offers & awards",
              href: "/offer-vault",
              icon: Vault,
            },
            {
              label: "Compare Offers",
              desc: "Side-by-side net cost",
              href: "/compare-offers",
              icon: Scale,
            },
            { label: "Funding", desc: "Family capital plan", href: "/fund", icon: PiggyBank },
            {
              label: "Universities",
              desc: "Browse the database",
              href: "/universities",
              icon: GraduationCap,
            },
            {
              label: "Scholarships",
              desc: "Eligibility-based search",
              href: "/scholarships",
              icon: ShieldCheck,
            },
            {
              label: "Account & Data",
              desc: "Session & deletion",
              href: "/account",
              icon: ShieldCheck,
            },
          ].map((m) => {
            const Icon = m.icon;
            return (
              <Link
                key={m.href}
                to={m.href}
                className="rounded-xl border border-border bg-card p-4 hover:border-primary/40 transition-all flex flex-col gap-2"
              >
                <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-xs font-semibold text-foreground">{m.label}</span>
                <span className="text-[11px] text-muted-foreground">{m.desc}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Trust footer — single status treatment */}
      <DataStatus level="illustrative">
        Illustrative product preview. Personalized data populates here as verified datasets are
        connected to your account. Your data is accessed only through your authenticated session and
        is subject to Row Level Security.
      </DataStatus>
    </div>
  );
}
