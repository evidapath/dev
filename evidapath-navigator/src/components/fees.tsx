import { Link } from "@tanstack/react-router";
import { formatCost } from "../lib/format";
import type { CountryCost, FeeFact } from "../lib/answers.server";
import { universityPath } from "../lib/paths";

// Fee wording and the fee table shared by /answers and the country cost pages, so both say
// the same thing about the same records.

export const money = (f: FeeFact) =>
  f.tuition === 0 ? `no tuition fee (0 ${f.currency})` : formatCost(f.tuition, f.currency);
// "the United Kingdom", "the Netherlands"; "Canada", "Germany".
export const place = (c: string) => (/^(United |Netherlands)/.test(c) ? `the ${c}` : c);
export const at = (f: FeeFact) =>
  `${f.programme} at ${f.university}${f.year ? ` (${f.year})` : ""}`;

export function costAnswer(c: CountryCost) {
  const unis = `${c.universities} ${c.universities === 1 ? "university" : "universities"}`;
  if (c.lowest.tuition === c.highest.tuition)
    return `On EvidaPath, yearly tuition for international students at ${unis} in ${place(c.country)} is ${money(c.lowest)} for all ${c.programmes} programmes listed${c.lowest.year ? ` (${c.lowest.year})` : ""}.`;
  return `On EvidaPath, yearly tuition for international students at ${unis} in ${place(c.country)} (${c.programmes} programmes) ranges from ${money(c.lowest)} for ${at(c.lowest)} to ${money(c.highest)} for ${at(c.highest)}.`;
}

export function Source({ url, title }: { url: string | null; title: string | null }) {
  if (!url) return <span className="text-muted-foreground">source on file</span>;
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="text-primary underline">
      {title ? "source" : new URL(url).hostname}
    </a>
  );
}

export function FeeTable({ rows }: { rows: FeeFact[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm min-w-[520px]">
        <thead className="text-left text-muted-foreground">
          <tr className="border-b border-border">
            <th className="py-2 pr-3 font-semibold">University (lowest-fee programme)</th>
            <th className="py-2 pr-3 font-semibold">Tuition / year</th>
            <th className="py-2 pr-3 font-semibold">Year</th>
            <th className="py-2 font-semibold">Source</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((f) => (
            <tr
              key={`${f.universityId}-${f.programme}`}
              className="border-b border-border/60 align-top"
            >
              <td className="py-2 pr-3">
                <Link
                  to={universityPath(f.university)}
                  className="hover:text-primary hover:underline"
                >
                  {f.university}
                </Link>
                <span className="block text-xs text-muted-foreground">{f.programme}</span>
              </td>
              <td className="py-2 pr-3 tabular-nums font-medium">
                {money(f)}
                {f.note && (
                  <span className="block text-xs font-normal text-muted-foreground max-w-xs">
                    {f.note}
                  </span>
                )}
              </td>
              <td className="py-2 pr-3 text-muted-foreground">{f.year ?? "not stated"}</td>
              <td className="py-2">
                <Source url={f.sourceUrl} title={f.sourceTitle} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
