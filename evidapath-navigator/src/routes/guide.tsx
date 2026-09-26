import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  BookOpen,
  Compass,
  BarChart3,
  CalendarCheck,
  PiggyBank,
  ShieldAlert,
  FileCheck2,
  BadgeCheck,
} from "lucide-react";
import {
  Section,
  FeatureBlock,
  ScreenshotPlaceholder,
  GuideHeader,
  Sidebar,
  StatusBadge,
} from "../components/guide/shared";
import {
  StatusMap,
  QAIntro,
  QATests,
  QAChecklist,
  Limitations,
  ReportTemplate,
} from "../components/guide/qa";

export const Route = createFileRoute("/guide")({
  head: () => ({
    meta: [
      { title: "EvidaPath User & QA Guide" },
      {
        name: "description",
        content:
          "Internal EvidaPath user guide and QA testing guide. Documents the application as it exists today.",
      },
      { name: "robots", content: "noindex, nofollow" },
    ],
  }),
  component: GuidePage,
});

function GuidePage() {
  const [active, setActive] = useState("welcome");

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-10">
        <aside className="lg:sticky lg:top-24 lg:self-start lg:max-h-[calc(100vh-7rem)] lg:overflow-y-auto">
          <Sidebar active={active} onSelect={setActive} />
        </aside>

        <div className="min-w-0 space-y-12">
          <GuideHeader />

          <Section
            id="welcome"
            title="Welcome to EvidaPath"
            intro="EvidaPath is an emerging education decision-intelligence platform. It helps ambitious students and families understand their academic position, available pathways, the true financial implications of those pathways, and the actions they can still take."
          >
            <div className="rounded-xl border border-border bg-card p-5 text-sm text-muted-foreground leading-relaxed space-y-2">
              <p>
                <strong className="text-foreground">Core promise:</strong> Know where you stand. See
                where you can go.
              </p>
              <p>
                This guide documents the application{" "}
                <strong className="text-foreground">as it exists today</strong>. Where features are
                illustrative, mocked, or not yet available, they are labeled with a status badge.
                EvidaPath is an emerging platform whose live datasets are currently being built and
                verified.
              </p>
            </div>
            <ScreenshotPlaceholder
              label="EvidaPath Homepage & Decision Model"
              note="Public homepage showing hero, primary CTAs, 4 interconnected questions, and interactive Decision Model demo."
              src="https://vibe.filesafe.space/1790101091506917993/assets/a73984ed-43c6-414d-b980-85bed9c33df7.png"
            />
          </Section>

          <Section
            id="what-it-does"
            title="What EvidaPath Does"
            intro="EvidaPath organizes the education decision across four connected questions: Discover, Analyze, Plan, and Fund. The platform connects a student's profile to universities, scholarships, affordability, and a personal roadmap."
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {[
                {
                  icon: Compass,
                  title: "Discover",
                  text: "Find universities that fit your academic profile, budget, and ambitions.",
                },
                {
                  icon: BarChart3,
                  title: "Analyze",
                  text: "See where you stand relative to evidence for a target university or program.",
                },
                {
                  icon: CalendarCheck,
                  title: "Plan",
                  text: "Know what to do next — actions organized by importance and timing.",
                },
                {
                  icon: PiggyBank,
                  title: "Fund",
                  text: "Understand what an education actually costs and where the funding gap is.",
                },
              ].map((m) => {
                const Icon = m.icon;
                return (
                  <div
                    key={m.title}
                    className="rounded-xl border border-border bg-card p-4 flex gap-3"
                  >
                    <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                      <Icon className="w-4.5 h-4.5" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-sm text-foreground">{m.title}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{m.text}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </Section>

          <Section
            id="status-map"
            title="Feature Status Map"
            intro="A quick reference for what is operational, partial, illustrative, or planned. Use this before assuming any figure is verified."
          >
            <StatusMap />
          </Section>

          <Section
            id="find-my-path"
            title="Find My Path — Guided Intake"
            intro="The first-run experience. A visitor does not need to understand the whole platform first — they answer a few questions and see realistic options."
          >
            <div className="flex items-center gap-2">
              <StatusBadge status="BETA" />
              <span className="text-xs text-muted-foreground">
                Intake is operational; pathway results use illustrative data.
              </span>
            </div>
            <FeatureBlock
              purpose="A simple guided intake that asks the minimum needed to return useful options."
              why="So a first-time visitor gets value in under 3 minutes instead of learning the platform's full architecture."
              steps={[
                "Open /find-my-path (the primary CTA on the homepage and header).",
                "Step 1 — Where are you studying now? (curriculum)",
                "Step 2 — How are you doing academically? (grade band)",
                "Step 3 — What do you want to study? (subject)",
                "Step 4 — Where would you consider studying? (region / Open to anywhere)",
                "Step 5 — What can your family realistically spend? (annual budget slider)",
                "Step 6 — Citizenship / residency (for tuition/eligibility modeling)",
                "Step 7 — Optional preferences (city, language, degree length)",
                "Click Show My Options.",
              ]}
              expected="The intake completes and shows 5–8 illustrative pathway cards. Answers stay on-device for the session; sign in to save permanently."
            />
            <ScreenshotPlaceholder label="Find My Path guided intake + step indicator" />
          </Section>

          <Section
            id="results"
            title="Results & Pathway Cards"
            intro="After intake, EvidaPath returns a small number of pathway options with progressive disclosure — complexity appears only when you ask for it."
          >
            <FeatureBlock
              purpose="Show 5–8 pathways, each initially displaying only the essentials: university, program, location, academic fit, estimated cost, funding potential, main gap/risk, and a short 'Why this made your list'."
              why="To avoid overwhelming the user with every admissions stage, evidence field, and source up front."
              steps={[
                "After Show My Options, review the pathway cards.",
                "Tap a card to expand deeper analysis: admissions requirements, prerequisites, costs, scholarships, evidence status.",
                "Use Explore this option, Save, or Compare from the expanded view.",
                "Start over, browse all universities, or sign in to save your path.",
              ]}
              expected="Cards expand inline. All figures are clearly labeled illustrative until verified data is connected. No admissions probability or opaque score is produced."
            />
            <ScreenshotPlaceholder label="Pathway results cards with progressive disclosure" />
          </Section>

          <Section
            id="create-account"
            title="Creating an Account"
            intro="Account creation is powered by Supabase Auth. EvidaPath never sees your password."
          >
            <FeatureBlock
              purpose="Create a private EvidaPath account to save your path and access the member area."
              why="The Academic Readiness Profile, Applications, Offer Vault, Compare Offers, and Family Capital Plan all require an authenticated account."
              steps={[
                "Open /sign-in and select the Sign Up tab.",
                "Enter your email and a password (minimum 6 characters).",
                "Click Create Account.",
                "If email confirmation is enabled, check your inbox for a verification link and click it.",
                "After confirming, sign in — new users are routed to /academic-readiness.",
              ]}
              expected="A verification email arrives (if enabled). After confirming, signing in lands a new user on /academic-readiness to begin their path."
            />
            <ScreenshotPlaceholder
              label="Sign Up & Authentication Options"
              note="Sign Up interface with Google OAuth button, 'or continue with email' divider, and password fields."
              src="https://vibe.filesafe.space/1790101091506917993/assets/b34a6749-3192-475b-bda0-3a448de8c927.png"
            />
          </Section>

          <Section
            id="sign-in"
            title="Signing In"
            intro="Sign in supports email/password, Google OAuth, magic link, and password reset."
          >
            <FeatureBlock
              purpose="Authenticate into your EvidaPath account."
              why="To reach protected pages and your private decision roadmap."
              steps={[
                "Open /sign-in.",
                "Sign In tab: enter email + password, or click Continue with Google.",
                "Google: the account chooser always appears (select_account).",
                "Magic link: click 'Sign in with a magic link instead' and use the emailed link.",
                "Forgot password: click 'Forgot password?' to receive a reset link.",
              ]}
              expected="Returning users land on /dashboard. New users land on /academic-readiness. A safe redirect= query param (e.g. /sign-in?redirect=%2Fdashboard) takes priority. Already-authenticated users visiting /sign-in are bounced away."
            />
            <div className="rounded-xl border border-border bg-card p-4 text-xs text-muted-foreground space-y-1">
              <p>
                <strong className="text-foreground">Post-login routing:</strong>
              </p>
              <p>
                • <code className="font-mono">redirect</code> param → that destination (priority).
              </p>
              <p>
                • Returning user (Sign In) → <code className="font-mono">/dashboard</code>.
              </p>
              <p>
                • New user (Sign Up) → <code className="font-mono">/academic-readiness</code>.
              </p>
            </div>
            <ScreenshotPlaceholder
              label="Sign In Interface"
              note="Live sign-in card with Google account chooser and password recovery."
              src="https://vibe.filesafe.space/1790101091506917993/assets/b34a6749-3192-475b-bda0-3a448de8c927.png"
            />
          </Section>

          <Section
            id="academic-readiness"
            title="Academic Readiness Profile"
            intro="The diagnostic starting point for your path. Protected route."
          >
            <div className="flex items-center gap-2">
              <StatusBadge status="BETA" />
              <span className="text-xs text-muted-foreground">
                Form is operational and records a lead; live readiness analysis is illustrative.
              </span>
            </div>
            <FeatureBlock
              purpose="Enter your grades/predicted grades, curriculum, intended subject, geographic preference, and annual family budget."
              why="To turn your academic record into a decision map and begin your EvidaPath journey."
              steps={[
                "Open /academic-readiness (requires sign-in).",
                "Complete Candidate Profile & Contact (name, email).",
                "Complete Academic Evidence & Focus (curriculum, grade band, subject, budget).",
                "Click Create My Readiness Profile.",
              ]}
              expected="A confirmation screen shows your recorded profile. High-alignment institutions and prerequisite gaps display 'Pending verified data'. Budget envelope reflects your selection. Note: the profile currently submits to lead tracking and is not yet persisted to your Supabase account for re-editing."
            />
            <ScreenshotPlaceholder label="Academic Readiness form + confirmation" />
          </Section>

          <Section
            id="dashboard"
            title="Dashboard & Next Step"
            intro="The member area answers one question: 'What should I do next?' Protected route."
          >
            <FeatureBlock
              purpose="A large Next Step panel at the top drives the next action, followed by a journey progress strip and quick-access modules."
              why="So the student always knows the single most useful next action instead of facing ten equal cards."
              steps={[
                "Sign in (returning users land here).",
                "The Next Step panel shows the current priority (e.g. Complete your Academic Readiness profile).",
                "Click Continue to act on it.",
                "Below, the journey strip shows Profile → Explore → Applications → Offers → Funding.",
                "Quick access tiles link to Analyze, Plan, Offer Vault, Compare, Funding, Universities, Scholarships, Account.",
              ]}
              expected="The Next Step panel is dominant. Progress markers show done/active/upcoming. A single consolidated status note replaces repeated caveats."
            />
            <ScreenshotPlaceholder label="Dashboard Next Step panel + journey strip" />
          </Section>

          <Section
            id="discover"
            title="Discovering Universities"
            intro="Public route. University discovery and the University Cost Database."
          >
            <div className="flex items-center gap-2">
              <StatusBadge status="MOCK DATA" />
              <span className="text-xs text-muted-foreground">
                University records are illustrative/demo, not verified.
              </span>
            </div>
            <FeatureBlock
              purpose="Search and filter universities by name, city, and country."
              why="To find universities that fit your profile, budget, and geography."
              steps={[
                "Open /universities.",
                "Type in the search box or filter by jurisdiction.",
                "Review each card: degree duration, academic threshold, tuition, living cost, total degree outlay, affordability category.",
                "Use Analyze Fit or Model in Plan actions.",
              ]}
              expected="Filtered university cards appear. All figures are clearly labeled illustrative — 'University data currently being verified.'"
            />
            <ScreenshotPlaceholder
              label="EvidaPath University Cost Database"
              note="Searchable university database designed around tuition, living costs, duration, and affordability."
              src="https://vibe.filesafe.space/1790101091506917993/assets/8346ba5a-7aba-4a5a-b30c-3fdc6804bd92.png"
            />
          </Section>

          <Section
            id="applications"
            title="Applications"
            intro="Track the universities you are applying to. Protected route, backed by Supabase."
          >
            <FeatureBlock
              purpose="Store applications with university, program, cycle, decision plan, date, and status."
              why="Applications are the parent record for offers. An application must be marked 'admitted' before you can create an offer."
              steps={[
                "Open /applications (requires sign-in).",
                "Click Add Application.",
                "Select a university, enter program/cycle/decision plan/date.",
                "Choose a status: planning, started, submitted, in_review, waitlisted, admitted, rejected, withdrawn.",
                "Save. Edit or delete later as needed.",
              ]}
              expected="The application appears in your list. When status is 'admitted', an 'Add offer' link appears to take you to the Offer Vault."
            />
            <ScreenshotPlaceholder label="Applications list + Add Application editor" />
          </Section>

          <Section
            id="offer-vault"
            title="Offer Vault"
            intro="Store admission offers and see what each means financially. Protected route, backed by Supabase."
          >
            <FeatureBlock
              purpose="Create an offer attached to an admitted application, including offer date, response deadline, deposit, deposit deadline, currency, and conditions."
              why="An offer is the basis for award entry, document upload, enrollment decisions, and offer analysis."
              steps={[
                "Open /offer-vault (requires sign-in).",
                "Click Add Offer.",
                "Select an admitted application (if none exist, you'll be prompted to create one first).",
                "Enter offer date, response deadline, deposit amount/deadline, currency, conditions.",
                "Click Create offer.",
              ]}
              expected="The offer appears in the Offer Vault list with its verification badge (Self-reported by default) and a net annual family cost (or 'Pending verified cost data')."
            />
            <ScreenshotPlaceholder label="Offer Vault list + Add Offer dialog" />
          </Section>

          <Section
            id="awards"
            title="Scholarships & Financial Aid"
            intro="Add scholarship/aid awards to an offer. Multiple awards per offer. Protected."
          >
            <FeatureBlock
              purpose="Record scholarships, grants, need-based aid, merit aid, tuition waivers, housing awards, government sponsorships, and external scholarships."
              why="Awards reduce your estimated net family cost and update your funding gap."
              steps={[
                "In the Offer Vault, open an offer.",
                "In 'Scholarships, grants & aid', click Add award.",
                "Enter award name, type, amount, currency, frequency, duration, renewal criteria, min GPA, need vs merit.",
                "Save award.",
              ]}
              expected="The award appears with a Self-reported badge. The offer's analysis updates to subtract the award from estimated cost."
            />
            <ScreenshotPlaceholder label="Awards section + Add award editor" />
          </Section>

          <Section
            id="documents"
            title="Uploading an Award / Offer Letter"
            intro="Upload private documents to support award verification. Protected, private Storage."
          >
            <FeatureBlock
              purpose="Upload offer letters, scholarship letters, financial aid letters, award notices, enrollment confirmations."
              why="Documents support moving an award from Self-reported toward Document-verified."
              steps={[
                "In an offer's 'Offer & award documents' section, choose a document type.",
                "Click Upload and select a file.",
                "The file is stored at <user-id>/<offer-id>/<filename> in the private student-documents bucket.",
                "Click the file name to open it via a short-lived signed URL (300s).",
              ]}
              expected="The document appears in the list. Only you can read it — no public URLs are ever generated. Deleting the record removes the metadata."
            />
            <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 text-xs text-foreground">
              <strong>Security:</strong> Files are private. Storage policies require the
              authenticated owner and a user-scoped path. Signed URLs only.
            </div>
            <ScreenshotPlaceholder label="Documents section with an uploaded file" />
          </Section>

          <Section
            id="verification"
            title="Verification Levels"
            intro="Every offer and award carries a verification level. The database enforces these — students cannot self-promote."
          >
            <div className="space-y-3">
              {[
                {
                  icon: ShieldAlert,
                  label: "Self-reported",
                  text: "Entered by the student. Default for all student-created records.",
                },
                {
                  icon: FileCheck2,
                  label: "Document-verified",
                  text: "Assigned only by a trusted EvidaPath verification process after an uploaded document has actually been evaluated and supports the claim. Uploading a file alone does NOT trigger this status.",
                },
                {
                  icon: BadgeCheck,
                  label: "Institution-verified",
                  text: "Future direct confirmation from the institution/provider. Not assigned by students.",
                },
              ].map((v) => {
                const Icon = v.icon;
                return (
                  <div
                    key={v.label}
                    className="rounded-xl border border-border bg-card p-4 flex gap-3"
                  >
                    <div className="w-9 h-9 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                      <Icon className="w-4.5 h-4.5 text-muted-foreground" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold text-sm text-foreground">{v.label}</h3>
                      <p className="text-xs text-muted-foreground mt-0.5">{v.text}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="rounded-xl border border-bronze/30 bg-bronze/5 p-4 text-xs text-foreground space-y-1">
              <p className="font-semibold">Important</p>
              <p>
                A student cannot promote verification_level to document_verified or
                institution_verified through the UI or a direct API request. The database rejects
                it. Editing a material field on a verified record automatically resets it to
                Self-reported.
              </p>
              <p>
                Note: the UI exposes a 'Mark verified' button on self-reported awards as a
                convenience, but the server function is intended for a trusted backend workflow. In
                the current MVP, all student-created records remain Self-reported until a trusted
                verification process is implemented.
              </p>
            </div>
          </Section>

          <Section
            id="compare-offers"
            title="Comparing Offers"
            intro="Compare admitted universities side by side. Protected route."
          >
            <FeatureBlock
              purpose="Compare offers by university, program, duration, published tuition, scholarship awarded, net annual family cost, total family cost, funding gap, deposit, acceptance deadline, renewal requirements, and verification status."
              why="To choose between admitted universities on evidence, not a single opaque score."
              steps={[
                "Create at least two offers in the Offer Vault.",
                "Open /compare-offers.",
                "Review the comparison table.",
              ]}
              expected="A side-by-side table appears. If fewer than two offers exist, an empty state directs you to the Offer Vault. No single score is produced."
            />
            <ScreenshotPlaceholder label="Compare Offers table" />
          </Section>

          <Section
            id="fund"
            title="Family Education Capital Plan"
            intro="Model multi-year education costs and funding gaps. Protected route."
          >
            <div className="flex items-center gap-2">
              <StatusBadge status="BETA" />
              <span className="text-xs text-muted-foreground">
                Interactive; cost basis is illustrative until verified data is connected.
              </span>
            </div>
            <FeatureBlock
              purpose="Compare two pathways side by side with family annual capacity and target scholarship sliders, plus a verified-awards panel pulled from your Offer Vault."
              why="To see what a decision actually requires financially and where a funding gap remains."
              steps={[
                "Open /fund (requires sign-in).",
                "Select Pathway A and Pathway B universities.",
                "Adjust Family Annual Capacity and Target Scholarship sliders.",
                "Review cumulative degree cost, modeled scholarships, family commitment, and remaining gap.",
                "The Verified Awards panel shows awards pulled from your Offer Vault.",
              ]}
              expected="Each pathway shows a remaining family capital gap (or 'Pending verified data' where cost data is missing). A capital delta analysis compares the two pathways when both have data."
            />
            <ScreenshotPlaceholder label="Family Education Capital Plan with two pathways" />
          </Section>

          <Section
            id="funding-gap"
            title="Funding Gap"
            intro="The funding gap is the core financial output that connects offers, awards, and the capital plan."
          >
            <div className="rounded-xl border border-border bg-card p-5 text-sm text-muted-foreground leading-relaxed space-y-3">
              <p>
                <strong className="text-foreground">Concept:</strong> Published/estimated annual
                cost minus verified + reported awards = estimated net annual family cost. Over the
                degree duration, minus expected family contribution, this yields the remaining
                funding gap.
              </p>
              <p>
                <strong className="text-foreground">Where it appears:</strong>
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>Offer Vault → Offer Analysis (per offer).</li>
                <li>Compare Offers → 'Remaining funding gap' row.</li>
                <li>Fund → 'Remaining Family Capital Gap' per pathway.</li>
              </ul>
              <p>
                When verified cost data is not yet connected, gaps display{" "}
                <em>'Pending verified data'</em> rather than an invented number. Your stored awards
                still reduce the gap automatically once cost data exists.
              </p>
            </div>
          </Section>

          <Section
            id="sign-out"
            title="Signing Out"
            intro="Logout clears the session immediately and returns you to the homepage."
          >
            <FeatureBlock
              purpose="End your authenticated session."
              why="To secure your account on shared devices and confirm protected pages require sign-in again."
              steps={[
                "Click your email / Sign Out in the header (desktop) or mobile menu.",
                "The app calls supabase.auth.signOut(), clears session state, and navigates to /.",
              ]}
              expected="Navigation reverts to the unauthenticated state (Sign In link, no member modules). Protected routes redirect to /sign-in."
            />
            <ScreenshotPlaceholder label="Authenticated navigation & Sign Out dropdown" />
          </Section>

          <Section
            id="qa"
            title="QA Testing Guide"
            intro="For QA testers. Run each test, record PASS/FAIL, and capture evidence on failure."
          >
            <QAIntro />
            <QATests />
            <QAChecklist />
          </Section>

          <Section
            id="limitations"
            title="Known Limitations"
            intro="Documented honestly so testers and users do not mistake illustrative content for verified data."
          >
            <Limitations />
          </Section>

          <Section
            id="report"
            title="Reporting a Problem"
            intro="Use this template when filing a QA issue so reports are actionable."
          >
            <ReportTemplate />
          </Section>

          <div className="flex items-center gap-2 text-[11px] text-muted-foreground border-t border-border pt-6">
            <BookOpen className="w-3.5 h-3.5 text-primary shrink-0" />
            <span>
              End of guide. This page is unlisted, noindex/nofollow, and excluded from the sitemap
              and main navigation.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
