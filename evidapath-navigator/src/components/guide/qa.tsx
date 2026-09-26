import { AlertTriangle, Lock, ShieldCheck } from "lucide-react";
import { StatusBadge } from "./shared";

export function QATest({
  title,
  steps,
  expected,
}: {
  title: string;
  steps: string[];
  expected: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="font-display font-bold text-sm text-foreground">TEST: {title}</h3>
        <span className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground border border-border rounded px-2 py-0.5">
          PASS / FAIL
        </span>
      </div>
      <div>
        <div className="text-[10px] font-semibold uppercase tracking-wide text-muted-foreground mb-1">
          Steps
        </div>
        <ol className="list-decimal list-inside space-y-1 text-xs text-foreground">
          {steps.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ol>
      </div>
      <div>
        <div className="text-[10px] font-semibold uppercase tracking-wide text-primary mb-1">
          Expected
        </div>
        <p className="text-xs text-foreground">{expected}</p>
      </div>
      <div className="text-[11px] text-muted-foreground border-t border-border/60 pt-2">
        <strong>On failure capture:</strong> screenshot, URL, exact error text, approximate time.
      </div>
    </div>
  );
}

export function QAIntro() {
  return (
    <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 text-xs text-foreground">
      <strong>How to use:</strong> For each test, follow the steps, confirm the expected result, and
      on failure capture a screenshot, the URL, exact error text, and approximate time.
    </div>
  );
}

export function QATests() {
  return (
    <div className="space-y-4">
      <QATest
        title="Email signup"
        steps={[
          "Sign out. Open /sign-in → Sign Up.",
          "Enter a fresh email + password (≥6 chars).",
          "Click Create Account.",
        ]}
        expected="If email confirmation is on, a verification email arrives; after confirming, sign-in works. If off, the user is routed to /academic-readiness."
      />
      <QATest
        title="Email verification"
        steps={["After signup, open the verification email.", "Click the confirmation link."]}
        expected="The link returns to /sign-in (or the redirect target) and the account can sign in."
      />
      <QATest
        title="Email/password sign-in (returning user)"
        steps={["Sign out. Open /sign-in.", "Enter existing email + password.", "Click Sign In."]}
        expected="Returning user lands on /dashboard. Email appears in the header."
      />
      <QATest
        title="Google sign-in"
        steps={[
          "Sign out. Open /sign-in.",
          "Click Continue with Google.",
          "Select a Google account.",
          "Complete authentication.",
        ]}
        expected="Google account chooser appears (prompt: select_account). Returning user → /dashboard. New user → /academic-readiness. redirect= takes priority."
      />
      <QATest
        title="Magic link"
        steps={[
          "Sign out. Open /sign-in.",
          "Click 'Sign in with a magic link instead'.",
          "Enter email, send, open the emailed link.",
        ]}
        expected="Magic link email arrives; clicking it signs the user in and routes to /dashboard (or redirect target)."
      />
      <QATest
        title="Password reset"
        steps={[
          "Sign out. Open /sign-in.",
          "Click 'Forgot password?'.",
          "Enter email, send reset link, open it, set a new password.",
        ]}
        expected="Reset email arrives; new password works on next sign-in."
      />
      <QATest
        title="Already-authenticated redirect"
        steps={["Sign in. Then navigate directly to /sign-in."]}
        expected="The user is bounced away to /dashboard (or redirect target), not left on /sign-in."
      />
      <QATest
        title="Find My Path intake (first-time visitor)"
        steps={[
          "Sign out. Open / (homepage) or click Find My Path in the header.",
          "Click Find My Path → /find-my-path.",
          "Step through all 7 intake questions.",
          "Click Show My Options.",
        ]}
        expected="5–8 pathway cards appear. All figures labeled illustrative. No account required to see results."
      />
      <QATest
        title="Pathway progressive disclosure"
        steps={["On the results page, tap a pathway card to expand it.", "Tap again to collapse."]}
        expected="Expanded card shows admissions, cost & funding, and 'Why this made your list'. Explore / Save / Compare actions appear. No opaque score."
      />
      <QATest
        title="Save path routes to sign-in"
        steps={["On results, click 'Save my path & sign in'."]}
        expected="Routes to /sign-in. After auth, the user can continue (redirect preserved where applicable)."
      />
      <QATest
        title="Dashboard Next Step panel"
        steps={["Sign in as a returning user → /dashboard."]}
        expected="A dominant Next Step panel shows the current priority with a Continue button. Journey strip shows Profile → Explore → Applications → Offers → Funding."
      />
      <QATest
        title="Protected route blocked when logged out"
        steps={[
          "Sign out. Open /dashboard, /applications, /offer-vault, /compare-offers, /fund, /academic-readiness.",
        ]}
        expected="Each redirects to /sign-in?redirect=<original path>. After sign-in, the user returns to the intended page."
      />
      <QATest
        title="Logout"
        steps={["Sign in. Click Sign Out in the header."]}
        expected="Session clears, user lands on /. Header shows Sign In. Protected pages now redirect to /sign-in."
      />
      <QATest
        title="Add application"
        steps={[
          "Sign in. Open /applications. Click Add Application.",
          "Fill fields, set status, save.",
        ]}
        expected="Application appears in the list. Persists on reload."
      />
      <QATest
        title="Edit / delete application"
        steps={["Open an application, edit status (e.g. admitted), save.", "Delete another."]}
        expected="Status updates; deleted application disappears."
      />
      <QATest
        title="Create admitted offer"
        steps={[
          "Mark an application admitted. Open /offer-vault. Click Add Offer.",
          "Select the admitted application, fill offer fields, create.",
        ]}
        expected="Offer appears in Offer Vault with Self-reported badge and net cost (or pending)."
      />
      <QATest
        title="Add award"
        steps={["Open an offer. Click Add award. Fill award fields, save."]}
        expected="Award appears with Self-reported badge. Offer analysis subtracts the award."
      />
      <QATest
        title="Cannot self-promote verification"
        steps={[
          "On a self-reported award, attempt to set verification_level to document_verified via any means.",
        ]}
        expected="The database rejects direct promotion. Record stays Self-reported."
      />
      <QATest
        title="Upload document"
        steps={["Open an offer. In documents, choose a type, upload a file."]}
        expected="File uploads to private storage at <user-id>/<offer-id>/<file>. Metadata written. File opens via signed URL only."
      />
      <QATest
        title="Document privacy"
        steps={["Attempt to read another user's document path or list the bucket."]}
        expected="Access denied by Storage RLS policies. No public URL exists."
      />
      <QATest
        title="Compare offers"
        steps={["Create ≥2 offers. Open /compare-offers."]}
        expected="Side-by-side table renders. Public cost and private awards remain conceptually separate. No opaque score."
      />
      <QATest
        title="Family Capital Plan"
        steps={["Open /fund. Adjust sliders. Review gaps."]}
        expected="Gaps compute where cost data exists; otherwise 'Pending verified data'. Verified awards panel reflects Offer Vault awards."
      />
      <QATest
        title="Cross-user isolation"
        steps={[
          "As User A, create records. Sign out, sign in as User B.",
          "Open /applications, /offer-vault, /compare-offers.",
        ]}
        expected="User B sees only their own records. User A's data is invisible."
      />
    </div>
  );
}

export function QAChecklist() {
  const items = [
    "Find My Path intake loads (logged-out)",
    "All 7 intake steps complete",
    "Show My Options returns 5–8 pathways",
    "Pathway cards expand/collapse (progressive disclosure)",
    "No admissions probability or opaque score shown",
    "Save path routes to sign-in",
    "Email signup",
    "Verification email received",
    "Email confirmation",
    "Google signup",
    "Google account chooser",
    "Returning Google login",
    "Magic link sign-in",
    "Password reset",
    "Logout",
    "Protected routes blocked after logout",
    "Already-authenticated redirect away from /sign-in",
    "redirect= preserved through auth",
    "Academic Readiness opens",
    "Profile can be entered",
    "Dashboard Next Step panel loads",
    "Journey strip renders (Profile → Funding)",
    "Add application",
    "Edit application status",
    "Application persists on reload",
    "Create admitted offer",
    "Offer appears in Offer Vault",
    "Response deadline displays",
    "Deposit information displays",
    "Upload offer letter",
    "Upload scholarship letter",
    "File remains private",
    "Student retrieves own document",
    "Add scholarship/aid award",
    "Award appears",
    "Verification begins Self-reported",
    "User cannot self-promote to Document-verified",
    "Award updates funding analysis",
    "Two offers can be compared",
    "Public cost vs private awards kept separate",
    "No illustrative figure shown as verified fact",
    "Family Capital Plan loads",
    "Award affects projected funding gap",
    "Missing info labeled clearly",
    "User A cannot see User B records",
    "Unauthenticated user blocked from protected routes",
    "Logout revokes protected access",
  ];
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="font-display font-bold text-sm text-foreground mb-3">QA Checklist</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5 text-xs text-foreground">
        {items.map((item) => (
          <label key={item} className="flex items-center gap-2">
            <input type="checkbox" className="accent-primary w-3.5 h-3.5" />
            <span>{item}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export function StatusMap() {
  const rows: {
    area: string;
    status: "LIVE" | "BETA" | "MOCK DATA" | "COMING LATER";
    note: string;
  }[] = [
    { area: "Email/password auth", status: "LIVE", note: "Supabase Auth, RLS-scoped sessions." },
    {
      area: "Google sign-in",
      status: "LIVE",
      note: "OAuth with account chooser (prompt: select_account).",
    },
    { area: "Magic link / OTP", status: "LIVE", note: "Email-based one-time sign-in." },
    { area: "Password reset", status: "LIVE", note: "Reset email sent via Supabase." },
    {
      area: "Protected routing + redirect preservation",
      status: "LIVE",
      note: "beforeLoad guards; redirect param preserved.",
    },
    {
      area: "Academic Readiness Profile form",
      status: "BETA",
      note: "Form submits to lead tracking; analysis is illustrative.",
    },
    {
      area: "Find My Path guided intake",
      status: "BETA",
      note: "Operational intake; pathway results illustrative.",
    },
    {
      area: "Dashboard (Next Step)",
      status: "LIVE",
      note: "Next Step panel + journey strip; progress static until profile state connected.",
    },
    {
      area: "Applications (Supabase)",
      status: "LIVE",
      note: "CRUD against student_applications, RLS-protected.",
    },
    {
      area: "Offer Vault (Supabase)",
      status: "LIVE",
      note: "Offers, awards, documents, enrollment — RLS-protected.",
    },
    {
      area: "Document upload (Storage)",
      status: "LIVE",
      note: "Private bucket, signed URLs only.",
    },
    {
      area: "Verification levels",
      status: "LIVE",
      note: "Self-reported default; DB prevents self-promotion.",
    },
    { area: "Compare Offers", status: "LIVE", note: "Side-by-side table; needs ≥2 offers." },
    {
      area: "Family Education Capital Plan",
      status: "BETA",
      note: "Interactive sliders; cost basis illustrative.",
    },
    {
      area: "University Cost Database",
      status: "MOCK DATA",
      note: "Illustrative records, not verified.",
    },
    { area: "Scholarship Graph", status: "MOCK DATA", note: "Illustrative records, not verified." },
    {
      area: "Intelligence articles",
      status: "MOCK DATA",
      note: "Example headlines, not published research.",
    },
    {
      area: "Outcomes Dataset",
      status: "COMING LATER",
      note: "Schema designed; no public outcomes yet.",
    },
  ];
  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-secondary/40">
            <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground p-3">
              Area
            </th>
            <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground p-3 w-32">
              Status
            </th>
            <th className="text-left text-[11px] font-semibold uppercase tracking-wide text-muted-foreground p-3">
              Note
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.area} className="border-b border-border/60 last:border-0">
              <td className="p-3 text-foreground font-medium">{r.area}</td>
              <td className="p-3">
                <StatusBadge status={r.status} />
              </td>
              <td className="p-3 text-xs text-muted-foreground">{r.note}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Limitations() {
  const items: { label: string; text: string }[] = [
    {
      label: "University cost data is illustrative",
      text: "The University Cost Database and university cards use demo/illustrative records. No tuition, living-cost, or total-degree figures are verified yet.",
    },
    {
      label: "Scholarship records are illustrative",
      text: "The Scholarship Graph shows example records. Award values, eligibility, and verification labels are not sourced from verified data.",
    },
    {
      label: "Academic Readiness analysis is illustrative",
      text: "The form records a lead but does not yet persist a re-editable profile to your account or produce verified readiness analysis.",
    },
    {
      label: "Intelligence articles are example headlines",
      text: "Article content is placeholder; no published EvidaPath research findings exist yet.",
    },
    {
      label: "Outcomes Dataset is not yet available",
      text: "The schema is designed for future anonymized outcomes, but no public outcomes data exists.",
    },
    {
      label: "Verification is Self-reported in the MVP",
      text: "No trusted backend verification workflow is live. All student-created records remain Self-reported.",
    },
    {
      label: "No admissions probabilities",
      text: "EvidaPath does not calculate or display admissions probabilities or acceptance percentages.",
    },
  ];
  return (
    <div className="space-y-2">
      {items.map((i) => (
        <div key={i.label} className="rounded-xl border border-border bg-card p-4">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-bronze shrink-0" />
            <h3 className="font-display font-bold text-sm text-foreground">{i.label}</h3>
          </div>
          <p className="text-xs text-muted-foreground">{i.text}</p>
        </div>
      ))}
    </div>
  );
}

export function ReportTemplate() {
  const template = `Page / URL:
Account type: (email / Google / new / returning)
What I was trying to do:
Steps taken:
1.
2.
3.
Expected result:
Actual result:
Error message:
Screenshot: (attach)
Browser/device:
Date/time:`;

  return (
    <div className="rounded-xl border border-border bg-card p-5 space-y-3">
      <h3 className="font-display font-bold text-sm text-foreground">QA Issue Template</h3>
      <button
        onClick={() => navigator.clipboard?.writeText(template)}
        className="text-xs flex items-center gap-1.5 text-primary hover:underline"
      >
        Copy template
      </button>
      <pre className="text-xs text-foreground bg-secondary/40 rounded-lg p-4 overflow-x-auto whitespace-pre-wrap font-mono">
        {template}
      </pre>
      <div className="rounded-xl border border-border bg-secondary/30 p-4 text-xs text-muted-foreground">
        <p className="flex items-center gap-1.5">
          <Lock className="w-3.5 h-3.5" />
          Do not include passwords, tokens, Supabase keys, or other students' private data in any
          report.
        </p>
      </div>
      <div className="flex items-center gap-2 text-[11px] text-muted-foreground border-t border-border pt-4">
        <ShieldCheck className="w-3.5 h-3.5 text-primary shrink-0" />
        <span>
          Evidence before opinion. EvidaPath is being built to distinguish verified facts,
          institutional information, estimates, and analytical interpretation.
        </span>
      </div>
    </div>
  );
}
