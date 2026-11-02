// Turns a published entry requirement (free text, verbatim from the university)
// into the one figure a student looks for first. The full wording is always shown
// alongside; this only picks out what is already written there.

export type KeyFigure =
  | { kind: "figure"; value: string; label: string }
  | { kind: "holistic" }
  | { kind: "unverified" }
  | null;

// Short tab names for the qualification list.
export function shortQualification(curriculum: string): string {
  if (/baccalaureate|\bIB\b/i.test(curriculum)) return "IB";
  if (/a[- ]?level/i.test(curriculum)) return "A-Levels";
  if (/american|us high school|\bAP\b/i.test(curriculum)) return "American";
  if (/\bUAE\b|emirat/i.test(curriculum)) return "UAE";
  if (/ontario|OSSD/i.test(curriculum)) return "Ontario";
  if (/\bCBSE\b|indian/i.test(curriculum)) return "CBSE";
  if (/general international|other/i.test(curriculum)) return "Other";
  return curriculum.replace(/\s*\(.*\)\s*/g, " ").trim();
}

// Three A-Level grades, best first ("A*AA", "AAB–ABB"). The order check keeps
// currency codes and the like ("AED", "CAD") out.
const A_LEVEL_G = /(?<![A-Za-z*])((?:[A-E]\*?){3}(?:\s*[–-]\s*(?:[A-E]\*?){3})?)(?![A-Za-z])/g;
const RANK: Record<string, number> = { "A*": 0, A: 1, B: 2, C: 3, D: 4, E: 5 };
function bestFirst(g: string) {
  const r = (g.match(/[A-E]\*?/g) ?? []).map((x) => RANK[x]!);
  return r.every((v, k) => k === 0 || v >= r[k - 1]!);
}
function aLevelGrades(text: string): string | null {
  for (const m of text.matchAll(A_LEVEL_G))
    if (m[1]!.split(/\s*[–-]\s*/).every(bestFirst)) return m[1]!;
  return null;
}

export function keyFigure(curriculum: string, threshold: string | null): KeyFigure {
  if (!threshold) return null;
  if (/not verified/i.test(threshold)) return { kind: "unverified" };

  const ib = /baccalaureate|\bIB\b/i.test(curriculum);
  const aLevel = /a[- ]?level/i.test(curriculum);
  // A US GPA is meaningless as the headline for an A-Level or IB student.
  const gpaFits = !ib && !aLevel;

  // "Typical" only when the words next to the figure say so: AUS says "minimum
  // 24 points" in a line that also says "admission is competitive".
  const typicalNear = (fig: string | null | undefined) => {
    if (!fig) return false;
    const at = threshold.indexOf(fig);
    const before = threshold.slice(Math.max(0, at - 60), at);
    const after = threshold.slice(at, at + fig.length + 25);
    if (/min(imum)?\b|at least/i.test(before.slice(-30))) return false;
    if (/^\s*typical(ly)?\b|typical admitted range/i.test(threshold)) return true;
    return /typical|admitted range|competitive/i.test(before + after);
  };
  // IB scores: "24 points", "IB 31", or the part after "IB:" in a mixed line
  // ("A-Level: … AAB–AAA. IB: HL Maths; 35–38 competitive").
  const ibPart = threshold.slice(Math.max(0, threshold.search(/\bIB\b/)));
  const ibScore =
    threshold.match(/(?<!\d)(\d{2}(?:\s*[–-]\s*\d{2})?\+?)\s*(?:IB\s*)?points/i) ??
    (/\bIB\b/.test(threshold)
      ? ibPart.match(/(?<![\d.])((?:2\d|3\d|4[0-5])(?:\s*[–-]\s*(?:2\d|3\d|4[0-5]))?\+?)(?![\d.%])/)
      : null);
  const grades = aLevelGrades(threshold);
  const gpa = threshold.match(/GPA\s*(?:of\s*)?(\d\.\d{1,2})|(\d\.\d{1,2})\s*GPA/i);
  const noAverage = /no (?:minimum|fixed)[^.;]*(?:average|cut-?off)/i.test(threshold);
  const pct = noAverage ? null : threshold.match(/(\d{2,3})\s*%/);
  // "minimum 75% (Elite track) or 85% (General track)": show the spread, not the lowest.
  const clause = pct ? threshold.slice(pct.index).split(";")[0]! : "";
  const clausePcts = [...clause.matchAll(/(\d{2,3})\s*%\s*\(/g)].map((m) => Number(m[1]));
  const pctValue =
    clausePcts.length > 1
      ? `${Math.min(...clausePcts)}–${Math.max(...clausePcts)}%`
      : pct
        ? `${pct[1]}%`
        : "";

  const figures: KeyFigure[] = [];
  if (ib && ibScore)
    figures.push({
      kind: "figure",
      value: ibScore[1]!,
      // A range ("34–38+") is a spread of scores, not a minimum.
      label:
        typicalNear(ibScore[1]) || /[–-]/.test(ibScore[1]!)
          ? "IB points (typical)"
          : "IB points minimum",
    });
  if (aLevel && grades)
    figures.push({
      kind: "figure",
      value: grades,
      label: /e\.g\.\s*$/.test(threshold.slice(0, threshold.indexOf(grades)))
        ? "A-Level grades (example)"
        : typicalNear(grades)
          ? "A-Level grades (typical)"
          : "A-Level grades",
    });
  if (pct)
    figures.push({
      kind: "figure",
      value: pctValue,
      label: /typical|admitted range/i.test(threshold)
        ? "Typical average"
        : clausePcts.length > 1
          ? "Minimum average (varies by track)"
          : "Minimum average",
    });
  if (gpa && gpaFits)
    figures.push({
      kind: "figure",
      value: gpa[1] ?? gpa[2]!,
      label: typicalNear(gpa[1] ?? gpa[2]) ? "GPA (typical)" : "Minimum GPA",
    });
  if (grades && !aLevel && /a[- ]?level/i.test(threshold))
    figures.push({ kind: "figure", value: grades, label: "A-Level grades (or equivalent)" });

  if (figures[0]) return figures[0];
  if (/holistic|no fixed (grade )?cut-?off/i.test(threshold)) return { kind: "holistic" };
  return null;
}

// "Guideline only", "competitive" etc. — worth a small tag next to the figure.
export function isCompetitive(threshold: string | null): boolean {
  return (
    !!threshold &&
    /competitive|guideline|can be higher|most programmes admit higher/i.test(threshold)
  );
}

// Split the published wording into short points for reading. Sentences only;
// nothing is reworded.
export function sentences(threshold: string): string[] {
  return threshold
    .split(/(?<=[.;])\s+(?=[A-Z(])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

// Some universities publish entry grades only in A-level terms ("AAB or equivalent").
// When that text is shown under another qualification, say so plainly rather than
// leaving an IB or American-diploma student to guess what "AAB" means for them.
const OWN_TERMS: { match: RegExp; own: RegExp; name: string }[] = [
  { match: /baccalaureate|\bIB\b/i, own: /\bIB\b|baccalaureate|points/i, name: "IB" },
  {
    match: /american|high school|\bAP\b/i,
    own: /\bGPA\b|\bSAT\b|\bACT\b|\bAP\b|high school|diploma/i,
    name: "American high school",
  },
];
export function otherTermsNote(curriculum: string, threshold: string): string | null {
  if (!/a[- ]?level|A\*/i.test(threshold)) return null;
  // "Other qualification" rows were often imported with the A-level text; say so
  // rather than imply those grades apply to every other curriculum.
  if (/general international|other/i.test(curriculum))
    return "Shown in A-level terms. The university converts other qualifications using its own equivalence tables — check its international entry requirements for your country.";
  const kind = OWN_TERMS.find((k) => k.match.test(curriculum));
  if (!kind || kind.own.test(threshold)) return null;
  return `Published in A-level terms only. Ask the university for its ${kind.name} equivalent.`;
}

// True when an ISO date (YYYY-MM-DD…) is before today, so a closed deadline is never
// shown as if it were still open.
