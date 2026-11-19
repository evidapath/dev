import { createFileRoute, Link } from "@tanstack/react-router";
import { LegalDoc } from "../components/LegalDoc";
import { ADULT_AGE, MIN_AGE, OPERATOR, PRIVACY_EMAIL, PROCESSORS } from "../lib/legal";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/privacy")({
  head: () => ({
    meta: [
      { title: "Privacy Policy — EvidaPath" },
      {
        name: "description",
        content:
          "What personal data EvidaPath collects, why, who it is shared with, how long it is kept, and how to see, change or delete it.",
      },
      { property: "og:title", content: "Privacy Policy — EvidaPath" },
      ogUrlMeta("/privacy"),
    ],
    links: [canonicalLink("/privacy")],
  }),
  component: PrivacyPage,
});

const mail = <a href={`mailto:${PRIVACY_EMAIL}`}>{PRIVACY_EMAIL}</a>;

const COLLECTED = [
  {
    what: "Account: email address and sign-in details (the password is handled by Supabase; we never see it). If you use Google sign-in, Google confirms your email.",
    why: "To create your account and sign you in.",
    basis: "Needed to provide the service you asked for.",
  },
  {
    what: "The age group you confirm at sign-up and, if you are under 18, your parent or guardian's email and their agreement.",
    why: "To check you are old enough and that a parent has agreed where needed.",
    basis: "Legal obligation; needed to provide the service.",
  },
  {
    what: "Find My Path answers: curriculum, grade band, subject, region, budget, citizenship, preferences, study languages.",
    why: "To show universities and programmes that fit you, and to save your profile if you're signed in.",
    basis: "Needed to provide the service you asked for.",
  },
  {
    what: "Saved universities and notes.",
    why: "To keep your shortlist.",
    basis: "Needed to provide the service you asked for.",
  },
  {
    what: "Offer Vault: applications, offers, scholarships and awards, enrollment decisions, outcomes, and documents you upload (for example offer letters).",
    why: "To let you store and compare your offers privately. Only you can see them.",
    basis: "Needed to provide the service you asked for.",
  },
  {
    what: "Form submissions: name, email, phone (optional), target intake, what you need help with, your saved universities; university and course requests; deadline-reminder dates; feedback answers and comments.",
    why: "To reply, run the counseling waitlist, send the reminders you switched on, decide which universities to add, and improve the site.",
    basis: "Your consent when you send the form. You can withdraw it at any time.",
  },
  {
    what: "When a signed-in student finishes Find My Path for the first time: their email and answers are added to our contact records.",
    why: "So our team can follow up with help on their options.",
    basis:
      "Our legitimate interest in helping students who use the service. You can object at any time.",
  },
  {
    what: "Technical data: IP address, browser, pages opened, error reports.",
    why: "To run, secure and fix the website.",
    basis: "Our legitimate interest in a secure, working service.",
  },
];

function PrivacyPage() {
  return (
    <LegalDoc
      title="Privacy Policy"
      intro={
        <p>
          EvidaPath helps students compare universities abroad. This policy explains, in plain
          language, what we collect, why, who sees it, how long we keep it and what you can do about
          it. We don't sell your data, we don't show ads, and we don't use advertising or analytics
          cookies.
        </p>
      }
      sections={[
        {
          id: "who",
          heading: "Who we are",
          body: (
            <>
              <p>
                The site is run by {OPERATOR}. We decide how your personal data is used (we are the
                "controller").
              </p>
              <p>Contact for anything about privacy: {mail}.</p>
            </>
          ),
        },
        {
          id: "collect",
          heading: "What we collect, why, and on what legal basis",
          body: (
            <>
              <p>
                You can browse universities, scholarships and careers without an account and without
                giving us any personal data.
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm min-w-[560px]">
                  <thead>
                    <tr>
                      <th>Data</th>
                      <th>Why</th>
                      <th>Legal basis</th>
                    </tr>
                  </thead>
                  <tbody>
                    {COLLECTED.map((r) => (
                      <tr key={r.what}>
                        <td>{r.what}</td>
                        <td>{r.why}</td>
                        <td>{r.basis}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p>
                We don't ask for sensitive information (such as health, religion or ethnicity).
                Please don't upload documents that contain it, or other people's data, to the Offer
                Vault.
              </p>
            </>
          ),
        },
        {
          id: "children",
          heading: "Children and parents",
          body: (
            <>
              <p>
                EvidaPath is for secondary-school students and their families. You must be at least{" "}
                {MIN_AGE} to create an account. If you are under {ADULT_AGE}, a parent or guardian
                must agree to you using EvidaPath before you create an account; we ask for their
                email so we can contact them.
              </p>
              <p>
                We don't knowingly collect data from children under {MIN_AGE}. If you believe a
                child under {MIN_AGE} has given us data, email {mail} and we will delete it.
              </p>
              <p>
                For students under {ADULT_AGE} we use only what is needed to provide the service: no
                advertising, no selling of data, no tracking across other websites and no profiling
                for marketing.
              </p>
              <p>Parents and guardians can ask us to see or delete their child's data at {mail}.</p>
            </>
          ),
        },
        {
          id: "sharing",
          heading: "Who we share it with",
          body: (
            <>
              <p>
                We use these service providers to run EvidaPath. They process data for us, not for
                their own purposes:
              </p>
              <ul>
                {PROCESSORS.map((p) => (
                  <li key={p.name}>
                    <strong>{p.name}</strong>: {p.what} Purpose: {p.why} {p.where}
                  </li>
                ))}
              </ul>
              <p>
                We share your data with no one else, except where the law requires it (for example a
                valid request from a court or regulator). Universities don't receive your data from
                us; you apply to them directly.
              </p>
            </>
          ),
        },
        {
          id: "transfers",
          heading: "International transfers",
          body: (
            <p>
              Our database is hosted in the United States, and some providers above process data in
              other countries. Where the law of your country requires safeguards for sending data
              abroad, we rely on our providers' data protection terms. Email {mail} for details.
            </p>
          ),
        },
        {
          id: "retention",
          heading: "How long we keep it",
          body: (
            <ul>
              <li>
                Account, profile, saved universities and Offer Vault data: until you delete your
                account. Deleting it removes them straight away.
              </li>
              <li>
                Form submissions and contact records: until you ask us to delete them, and no longer
                than 3 years after we last heard from you.
              </li>
              <li>
                AI fit requests: we don't store them. We send them to Anthropic only to write the
                answer.
              </li>
              <li>
                Technical logs: kept briefly by our hosting providers for security and fixing
                faults.
              </li>
            </ul>
          ),
        },
        {
          id: "rights",
          heading: "Your rights",
          body: (
            <>
              <p>Depending on where you live, you can ask us to:</p>
              <ul>
                <li>tell you what data we hold about you and give you a copy;</li>
                <li>correct data that is wrong;</li>
                <li>delete your data;</li>
                <li>stop or limit using your data, or object to how we use it;</li>
                <li>send your data to you or another service in a common format;</li>
                <li>withdraw consent you gave (this doesn't affect what happened before).</li>
              </ul>
              <p>
                Email {mail} from the address you use with us. We reply within one month. You can
                also complain to the data protection authority where you live (for example the
                Information Commissioner's Office in the UK).
              </p>
            </>
          ),
        },
        {
          id: "delete-account",
          heading: "Deleting your account",
          body: (
            <>
              <p>
                Signed in, go to <Link to="/account">Account</Link> and choose Delete account. This
                permanently deletes your login, profile, saved universities, every Offer Vault
                record and every document you uploaded. It can't be undone.
              </p>
              <p>
                Form submissions you sent (for example the counseling waitlist) are kept in our
                contact records, which are separate. To delete those too, email {mail}.
              </p>
            </>
          ),
        },
        {
          id: "ai",
          heading: "AI and automated suggestions",
          body: (
            <p>
              Find My Path ranks programmes using fixed rules on published data, and the optional AI
              fit check uses Claude (Anthropic) to explain the fit. These are suggestions to help
              you decide. They make no decision about you, and no decision with legal or similar
              effects is made automatically. Always check with the university before you apply or
              pay.
            </p>
          ),
        },
        {
          id: "security",
          heading: "Security",
          body: (
            <p>
              Your private data is protected by sign-in and database rules that let only you read
              your own records; uploaded documents are kept in private storage. No system is
              perfectly secure; if we learn of a breach affecting you, we will tell you and the
              authorities where the law requires.
            </p>
          ),
        },
        {
          id: "cookies",
          heading: "Cookies and browser storage",
          body: (
            <p>
              We use a sign-in cookie and a few browser-storage items that remember your choices. No
              advertising or analytics cookies. Full list and how to clear them:{" "}
              <Link to="/cookies">Cookies &amp; storage</Link>.
            </p>
          ),
        },
        {
          id: "changes",
          heading: "Changes to this policy",
          body: (
            <p>
              If we change this policy we will update the date at the top, and tell signed-in users
              by email or on the site before a significant change takes effect.
            </p>
          ),
        },
      ]}
    />
  );
}
