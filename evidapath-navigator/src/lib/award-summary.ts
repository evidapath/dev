// The headline of a scholarship award, picked out of the published wording
// ("CAD $30,000/yr", "Up to 45% off tuition", "Full tuition", "100% of need").
// The full text is always shown as well; nothing here is computed or converted.

export interface AwardHeadline {
  value: string;
  label: string;
}

const CURRENCY =
  /(?:(CAD|AUD|AED|GBP|EUR|MYR|USD|RM|A\$|£|€)\s?\$?|\$)\s?(\d[\d,]*(?:\.\d+)?)(?:\s?[–-]\s?(?:CAD|AUD|£|€|\$)?\s?\$?(\d[\d,]*))?/;

function period(after: string): string {
  // Only the words right after the amount, up to the next clause or "+".
  const near = after.split(/[.;+]/)[0]!.slice(0, 30);
  if (/over \d years/i.test(near)) return `in total, ${near.match(/over \d years/i)![0]}`;
  if (/\/\s?month|per month/i.test(near)) return "per month";
  if (/\/\s?yr|\/\s?year|per year|a year|each year/i.test(near)) return "per year";
  if (/one-time|one-off/i.test(near)) return "one-time";
  if (/first[- ]year|year one|year 1|level 1/i.test(near)) return "first year";
  return "award";
}

export function awardHeadline(text: string | undefined): AwardHeadline | null {
  if (!text) return null;
  const t = text.trim();

  if (/(100%|full)( of)?( demonstrated)?( financial)? need|meets? (USC-determined )?need/i.test(t))
    return { value: "100% of need", label: "need-based aid" };
  if (/^full[- ]ride/i.test(t)) return { value: "Full ride", label: "tuition and living" };
  if (
    /^(full (coverage of )?tuition|100% (of )?tuition|full tuition|tuition, books|course fees)/i.test(
      t,
    )
  )
    return {
      value: "Full tuition",
      label: /housing|accommodation|living|stipend|residence|maintenance/i.test(t)
        ? "plus living support"
        : "covered",
    };

  if (/^(variable|varies)/i.test(t)) return { value: "Varies", label: "set by the university" };
  if (/^tiered/i.test(t)) return { value: "Tiered", label: "by your grades" };
  if (/^household[- ]income[- ]banded|income[- ]banded/i.test(t))
    return { value: "Tiered", label: "by household income" };
  if (/full[- ]ride/i.test(t)) return { value: "Up to full ride", label: "depends on the award" };

  const money = t.match(CURRENCY);
  const pct = t.match(/(up to\s+)?(\d{1,3})(?:\s?[–-]\s?(\d{1,3}))?%/i);
  const moneyAt = money?.index ?? Infinity;
  const pctAt = pct?.index ?? Infinity;

  if (pct && pctAt <= moneyAt) {
    const v = pct[3] ? `${pct[2]}–${pct[3]}%` : `${pct[1] ? "Up to " : ""}${pct[2]}%`;
    return {
      value: v,
      label: /first[- ]year|year one|first-semester/i.test(t)
        ? "off first-year tuition"
        : "off tuition",
    };
  }
  if (money) {
    const cur = money[1] === "RM" ? "MYR" : (money[1] ?? "$");
    const sym = cur === "$" || cur === "£" || cur === "€" || cur === "A$" ? cur : `${cur} `;
    const range = money[3] ? `–${money[3]}` : "";
    const upTo = /^\s*up to/i.test(t.slice(0, money.index)) ? "Up to " : "";
    return {
      value: `${upTo}${sym}${money[2]}${range}`,
      label: period(t.slice(money.index! + money[0].length)),
    };
  }
  if (/^\d[\d,]*$/.test(t)) return { value: t, label: "award" };
  if (/variable|varies|case by case|amount per criteria/i.test(t))
    return { value: "Varies", label: "set by the university" };
  return null;
}
