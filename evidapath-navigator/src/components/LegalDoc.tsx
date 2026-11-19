import type { ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import { LEGAL_UPDATED } from "../lib/legal";

// Shared layout for the Privacy, Terms and Cookies pages: readable column, a contents
// list linking to each section, and links between the three documents.

const tab =
  "rounded-full border border-border px-3 py-1 text-muted-foreground hover:border-primary/40 hover:text-foreground [&.active]:border-primary [&.active]:text-primary";

export function LegalDoc({
  title,
  intro,
  sections,
}: {
  title: string;
  intro: ReactNode;
  sections: { id: string; heading: string; body: ReactNode }[];
}) {
  return (
    <article className="max-w-3xl mx-auto px-4 sm:px-6 py-10 space-y-8 text-foreground">
      <header className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-primary">Legal</p>
        <h1 className="font-display font-bold text-3xl sm:text-4xl">{title}</h1>
        <p className="text-sm text-muted-foreground">Last updated {LEGAL_UPDATED}</p>
        <div className="text-base leading-relaxed text-foreground/90">{intro}</div>
        <nav aria-label="Legal documents" className="flex flex-wrap gap-2 pt-1 text-sm">
          <Link to="/privacy" className={tab}>
            Privacy Policy
          </Link>
          <Link to="/terms" className={tab}>
            Terms of Use
          </Link>
          <Link to="/cookies" className={tab}>
            Cookies &amp; storage
          </Link>
        </nav>
      </header>

      <nav
        aria-label="On this page"
        className="rounded-2xl border border-border bg-card p-5 text-sm"
      >
        <p className="font-semibold mb-2">On this page</p>
        <ol className="grid sm:grid-cols-2 gap-x-6 gap-y-1 list-decimal list-inside text-muted-foreground">
          {sections.map((s) => (
            <li key={s.id}>
              <a href={`#${s.id}`} className="hover:text-primary hover:underline">
                {s.heading}
              </a>
            </li>
          ))}
        </ol>
      </nav>

      {sections.map((s, i) => (
        <section key={s.id} id={s.id} className="scroll-mt-24 space-y-3">
          <h2 className="font-display font-bold text-xl">
            {i + 1}. {s.heading}
          </h2>
          <div className="space-y-3 text-[15px] leading-relaxed text-foreground/90 [&_a]:text-primary [&_a]:underline [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-1.5 [&_th]:text-left [&_th]:font-semibold [&_th]:p-2 [&_td]:p-2 [&_td]:align-top [&_tr]:border-b [&_tr]:border-border">
            {s.body}
          </div>
        </section>
      ))}
    </article>
  );
}
