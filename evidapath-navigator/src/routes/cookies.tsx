import { useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { LegalDoc } from "../components/LegalDoc";
import { Button } from "../components/ui/button";
import { CLEARABLE_KEYS, PRIVACY_EMAIL, STORAGE } from "../lib/legal";
import { canonicalLink, ogUrlMeta } from "../lib/seo";

export const Route = createFileRoute("/cookies")({
  head: () => ({
    meta: [
      { title: "Cookies and Browser Storage — EvidaPath" },
      {
        name: "description",
        content:
          "Every cookie and browser-storage item EvidaPath uses, what it does, how long it lasts, and how to clear it. No advertising or analytics cookies.",
      },
      { property: "og:title", content: "Cookies and Browser Storage — EvidaPath" },
      ogUrlMeta("/cookies"),
    ],
    links: [canonicalLink("/cookies")],
  }),
  component: CookiesPage,
});

// The "simple means of objecting" for preference storage: removes every item below except
// the sign-in cookie (sign out to remove that).
function ClearChoices() {
  const [done, setDone] = useState<null | boolean>(null);
  const clear = () => {
    try {
      for (const k of CLEARABLE_KEYS) localStorage.removeItem(k);
      setDone(true);
    } catch {
      setDone(false);
    }
  };
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Button onClick={clear} variant="outline" className="text-sm">
        Clear my saved choices on this device
      </Button>
      {done === true && (
        <span className="text-sm text-primary">Cleared. Reload the page to see the defaults.</span>
      )}
      {done === false && (
        <span className="text-sm text-destructive">
          Your browser blocked this; clear site data in your browser settings instead.
        </span>
      )}
    </div>
  );
}

function CookiesPage() {
  return (
    <LegalDoc
      title="Cookies and browser storage"
      intro={
        <p>
          EvidaPath uses no advertising or analytics cookies and doesn't track you on other
          websites. Our visit counts come from Cloudflare Web Analytics, which stores nothing on
          your device. We use one sign-in cookie and a few items in your browser's storage that
          remember choices you made. Because these are needed for the features you use or only
          change how the site looks for you, we don't ask for consent, but you can clear them at any
          time.
        </p>
      }
      sections={[
        {
          id: "list",
          heading: "What we store on your device",
          body: (
            <div className="overflow-x-auto">
              <table className="w-full text-sm min-w-[560px]">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>What it does</th>
                    <th>Type</th>
                    <th>How long</th>
                  </tr>
                </thead>
                <tbody>
                  {STORAGE.map((s) => (
                    <tr key={s.name}>
                      <td className="font-mono text-xs break-all">{s.name}</td>
                      <td>{s.purpose}</td>
                      <td>{s.kind}</td>
                      <td>{s.lasts}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ),
        },
        {
          id: "clear",
          heading: "Clear or block them",
          body: (
            <>
              <p>
                This button removes everything in the table except the sign-in cookie (sign out to
                remove that). The site still works; it just forgets your choices.
              </p>
              <ClearChoices />
              <p>
                You can also block or delete cookies and site data in your browser's settings. If
                you block the sign-in cookie you won't be able to sign in.
              </p>
            </>
          ),
        },
        {
          id: "third-party",
          heading: "Other services",
          body: (
            <p>
              Pages load fonts from Google Fonts, which receives your IP address but sets no cookie
              from our site. If you choose Google sign-in, Google's own cookies apply on Google's
              pages. Forms send what you type to our contact system only when you press send. See
              the <Link to="/privacy">Privacy Policy</Link> for every service we use.
            </p>
          ),
        },
        {
          id: "contact",
          heading: "Questions",
          body: (
            <p>
              Email <a href={`mailto:${PRIVACY_EMAIL}`}>{PRIVACY_EMAIL}</a>.
            </p>
          ),
        },
      ]}
    />
  );
}
