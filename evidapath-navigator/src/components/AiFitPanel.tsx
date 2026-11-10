// EXPERIMENTAL (AI fit). Shown only to allow-listed accounts (the server decides).
// Every sentence on this panel survived the server's checks: it cites facts from
// EvidaPath's checked data, and those facts are shown under it.

import { useServerFn } from "@tanstack/react-start";
import { FlaskConical, Loader2, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { getAiFit, getAiFitAccess } from "../lib/ai-fit.functions";
import type { CitedLine, FitResult } from "../lib/ai-fit.server";
import type { StudentInput } from "../lib/decision-engine";

const CATEGORY: Record<string, string> = {
  best_overall_fit: "Best overall fit",
  strongest_academic_match: "Strongest academic match",
  best_value: "Best value",
  worth_a_stretch: "Worth a stretch",
  safer_option: "Safer option",
};

function Line({ l, tone = "text-foreground" }: { l: CitedLine; tone?: string }) {
  return (
    <li className="space-y-0.5">
      <p className={`text-sm ${tone}`}>{l.text}</p>
      {l.facts.length > 0 && (
        <details className="text-[11px] text-muted-foreground">
          <summary className="cursor-pointer select-none">Evidence ({l.facts.length})</summary>
          <ul className="mt-1 space-y-1 pl-3 border-l border-border">
            {l.facts.map((f) => (
              <li key={f.id}>
                {f.text}{" "}
                {f.source && (
                  <a
                    href={f.source}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    source ↗
                  </a>
                )}
              </li>
            ))}
          </ul>
        </details>
      )}
    </li>
  );
}

export function AiFitPanel({ input }: { input: StudentInput }) {
  const access = useServerFn(getAiFitAccess);
  const run = useServerFn(getAiFit);
  const [enabled, setEnabled] = useState(false);
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");
  const [result, setResult] = useState<FitResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    access()
      .then((r) => setEnabled(r.enabled))
      .catch(() => setEnabled(false));
  }, [access]);
  if (!enabled) return null;

  const go = () => {
    setState("loading");
    run({ data: input })
      .then((r) => {
        setResult(r);
        setState("done");
      })
      .catch((e: Error) => {
        setError(e.message || "Something went wrong.");
        setState("error");
      });
  };

  return (
    <section className="rounded-2xl border-2 border-dashed border-primary/40 bg-primary/5 p-5 sm:p-6 space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="inline-flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-primary">
            <FlaskConical className="w-3.5 h-3.5" /> Experimental · test accounts only
          </p>
          <h2 className="font-display font-bold text-lg text-foreground">AI fit check</h2>
          <p className="text-xs text-muted-foreground max-w-2xl">
            Claude reads only EvidaPath's checked facts (costs, entry requirements, scholarships,
            deadlines, visa rules and accreditation) and picks the programmes that fit you best. It
            can't add facts: every sentence must cite one, and we remove any that don't. Your
            answers (not your name or email) are sent to Anthropic to do this.
          </p>
        </div>
        <button
          onClick={go}
          disabled={state === "loading"}
          className="inline-flex items-center gap-1.5 h-10 px-4 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 disabled:opacity-60"
        >
          {state === "loading" ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <FlaskConical className="w-4 h-4" />
          )}
          {state === "done" ? "Run again" : "Check my fit"}
        </button>
      </div>

      {state === "error" && <p className="text-sm text-bronze">{error}</p>}

      {state === "done" && result && (
        <div className="space-y-4">
          {result.summary && (
            <ul>
              <Line l={result.summary} />
            </ul>
          )}
          {result.picks.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No pick survived the checks for these answers. Try changing your subject or budget.
            </p>
          ) : (
            <ol className="grid gap-3 md:grid-cols-2">
              {result.picks.map((p, i) => (
                <li
                  key={p.university_id}
                  className="rounded-xl border border-border bg-card p-4 space-y-2"
                >
                  <p className="text-[11px] font-bold uppercase tracking-wider text-primary">
                    {i + 1}. {CATEGORY[p.category] ?? p.category}
                  </p>
                  <p className="font-display font-bold text-foreground leading-snug">
                    {p.name}
                    <span className="block text-xs font-normal text-muted-foreground">
                      {p.programme} · {p.country}
                    </span>
                  </p>
                  {p.headline && (
                    <p className="text-sm font-medium text-foreground">{p.headline}</p>
                  )}
                  <ul className="space-y-2">
                    {p.reasons.map((l, k) => (
                      <Line key={k} l={l} />
                    ))}
                  </ul>
                  {p.cautions.length > 0 && (
                    <ul className="space-y-2 pt-1 border-t border-border/60">
                      {p.cautions.map((l, k) => (
                        <Line key={k} l={l} tone="text-bronze" />
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ol>
          )}
          {result.gaps.length > 0 && (
            <div className="text-xs text-muted-foreground space-y-1">
              <p className="font-semibold text-foreground">
                Missing information that could change this
              </p>
              <ul className="list-disc pl-4 space-y-0.5">
                {result.gaps.map((g, k) => (
                  <li key={k}>{g.text}</li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            {result.candidates} programmes considered · {result.removed} AI statements removed by
            our checks · model {result.model}
          </p>
        </div>
      )}
    </section>
  );
}
