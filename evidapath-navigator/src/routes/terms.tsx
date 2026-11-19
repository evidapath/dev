import { createFileRoute, Link } from "@tanstack/react-router";
import { LegalDoc } from "../components/LegalDoc";
import { ADULT_AGE, GOVERNING_LAW, MIN_AGE, OPERATOR, PRIVACY_EMAIL } from "../lib/legal";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/terms")({
  head: () => ({
    meta: [
      { title: "Terms of Use — EvidaPath" },
      {
        name: "description",
        content:
          "The rules for using EvidaPath: who can use it, what the information is and isn't, accounts, your uploads, and our responsibilities.",
      },
      { property: "og:title", content: "Terms of Use — EvidaPath" },
      ogUrlMeta("/terms"),
    ],
    links: [canonicalLink("/terms")],
  }),
  component: TermsPage,
});

const mail = <a href={`mailto:${PRIVACY_EMAIL}`}>{PRIVACY_EMAIL}</a>;

function TermsPage() {
  return (
    <LegalDoc
      title="Terms of Use"
      intro={
        <p>
          These terms apply when you use EvidaPath. By using the site or creating an account you
          agree to them. Please read them with our <Link to="/privacy">Privacy Policy</Link>.
        </p>
      }
      sections={[
        {
          id: "who",
          heading: "Who we are",
          body: (
            <p>
              EvidaPath is run by {OPERATOR}. Contact: {mail}.
            </p>
          ),
        },
        {
          id: "eligibility",
          heading: "Who can use EvidaPath",
          body: (
            <p>
              Anyone can browse. To create an account you must be at least {MIN_AGE}. If you are
              under {ADULT_AGE}, a parent or guardian must agree to these terms and our Privacy
              Policy for you before you create an account.
            </p>
          ),
        },
        {
          id: "information",
          heading: "What our information is, and isn't",
          body: (
            <>
              <p>
                We collect fees, entry requirements, deadlines and scholarships from universities'
                and governments' own published pages, and link to the source. Where a figure isn't
                published, we say so instead of guessing.
              </p>
              <p>
                Universities change their figures and rules, and we may make mistakes. EvidaPath is
                information to help you decide; it is not legal, financial, immigration or
                admissions advice, and it doesn't guarantee an offer, a scholarship, a visa or a
                cost. Always confirm with the university (and the relevant government for visas)
                before you apply, accept an offer or pay anything.
              </p>
              <p>
                We are independent: universities don't pay us for placement or rankings, and we
                aren't acting for any university.
              </p>
              <p>If you find an error, tell us at {mail} so we can check it against the source.</p>
            </>
          ),
        },
        {
          id: "ai",
          heading: "AI fit check",
          body: (
            <p>
              The optional AI fit check is written by an AI model from your answers and our verified
              data. It can be wrong or incomplete. Treat it as a starting point, not a decision.
            </p>
          ),
        },
        {
          id: "account",
          heading: "Your account",
          body: (
            <ul>
              <li>Give a real email address you can access, and keep your sign-in details safe.</li>
              <li>Don't share your account or use someone else's.</li>
              <li>
                You can delete your account at any time from the <Link to="/account">Account</Link>{" "}
                page.
              </li>
            </ul>
          ),
        },
        {
          id: "content",
          heading: "What you upload",
          body: (
            <p>
              Documents and details you add to the Offer Vault stay yours. You allow us to store
              them and show them to you, which is all we use them for. Only upload documents that
              are yours or that you have permission to share.
            </p>
          ),
        },
        {
          id: "use",
          heading: "Acceptable use",
          body: (
            <>
              <p>Please don't:</p>
              <ul>
                <li>
                  try to access other people's accounts or data, or break the site's security;
                </li>
                <li>overload the site or interfere with how it works;</li>
                <li>upload anything unlawful, harmful, or that infringes someone's rights;</li>
                <li>send false requests or use the forms to send spam.</li>
              </ul>
              <p>We may suspend or close an account that breaks these rules.</p>
            </>
          ),
        },
        {
          id: "ours",
          heading: "Our content",
          body: (
            <p>
              The site's design, text and the way we compile and present data belong to EvidaPath.
              You may quote and share individual facts for personal or educational use with a link
              to the page. Figures published by universities and governments remain theirs.
            </p>
          ),
        },
        {
          id: "availability",
          heading: "Availability and changes",
          body: (
            <p>
              EvidaPath is free and still being built. We may change, add or remove features, and
              the site may sometimes be unavailable. If we change these terms we will update the
              date at the top and tell signed-in users before a significant change takes effect.
            </p>
          ),
        },
        {
          id: "liability",
          heading: "Our responsibility to you",
          body: (
            <>
              <p>
                We take care to keep our information accurate, but we can't promise it is complete,
                current or free of errors. As far as the law allows, we aren't responsible for
                decisions you make or losses you suffer because you relied on the site instead of
                confirming with the university or government.
              </p>
              <p>
                Nothing in these terms limits responsibility that the law doesn't allow to be
                limited, or your rights as a consumer.
              </p>
            </>
          ),
        },
        {
          id: "law",
          heading: "Governing law",
          body: (
            <p>
              {GOVERNING_LAW ??
                "The law that governs these terms will be stated here once EvidaPath is registered as a company. Until then, nothing here takes away the protections you have under the law of the country where you live."}
            </p>
          ),
        },
        {
          id: "contact",
          heading: "Contact",
          body: <p>Questions about these terms: {mail}.</p>,
        },
      ]}
    />
  );
}
