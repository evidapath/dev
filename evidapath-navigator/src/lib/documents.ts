// A per-university checklist of documents and tests, built only from data we've
// checked: the programme's English requirement, entry grades and required
// subjects for the student's curriculum, admissions tests, application deadlines
// and platform, scholarships, and the country's visa rules. The one piece of
// advice that isn't a published fact (when to sit the English test) says so.

import { deadlinesFor, fmtDate, type DecisionAnalysis } from "./decision-engine";
import type { University } from "./mock-data";
import { visaFor } from "./visa";

export type DocGroup = "English test" | "Grades & tests" | "Application" | "Scholarships" | "Visa";

export interface DocItem {
  id: string;
  group: DocGroup;
  title: string;
  detail?: string;
  /** YYYY-MM-DD, when the item has a date. */
  date?: string;
  source?: string;
}

const ISO = /^\d{4}-\d{2}-\d{2}/;
const today = () => new Date().toISOString().slice(0, 10);

function minusDays(d: string, n: number): string {
  const t = new Date(`${d.slice(0, 10)}T00:00:00Z`);
  t.setUTCDate(t.getUTCDate() - n);
  return t.toISOString().slice(0, 10);
}

/** Days before the earliest deadline we suggest sitting the English test. */
export const ENGLISH_LEAD_DAYS = 42;

export function buildChecklist(u: University, a: DecisionAnalysis): DocItem[] {
  const id = (s: string) => `${u.id}:${s}`;
  const items: DocItem[] = [];
  const now = today();
  const upcoming = deadlinesFor(u, a.program?.name)
    .filter((d) => d.deadline && ISO.test(d.deadline) && d.deadline.slice(0, 10) >= now)
    .sort((x, y) => x.deadline!.localeCompare(y.deadline!));
  const first = upcoming[0];

  // English test
  if (a.program?.english) {
    const by = first ? minusDays(first.deadline!, ENGLISH_LEAD_DAYS) : null;
    items.push({
      id: id("english"),
      group: "English test",
      title: "Take an English test",
      detail: `${a.program.english}${
        by && by >= now
          ? ` Our suggestion: sit it by ${fmtDate(by)}, 6 weeks before your first deadline, so results arrive in time.`
          : ""
      }`,
      ...(by && by >= now ? { date: by } : {}),
    });
  }

  // Grades, subjects and admissions tests for the student's curriculum
  if (a.academic.requirement)
    items.push({
      id: id("grades"),
      group: "Grades & tests",
      title: `Predicted or final grades${a.academic.curriculumLabel ? ` (${a.academic.curriculumLabel})` : ""}`,
      detail: a.academic.requirement,
    });
  if (a.academic.subjects.length)
    items.push({
      id: id("subjects"),
      group: "Grades & tests",
      title: `Required subjects: ${a.academic.subjects.join(", ")}`,
    });
  const row = a.program?.admissionsByCurriculum.find(
    (r) => r.curriculum === a.academic.curriculumLabel,
  );
  for (const t of row?.tests ?? [])
    items.push({ id: id(`test:${t}`), group: "Grades & tests", title: `Also required: ${t}` });

  // Application
  for (const d of upcoming)
    items.push({
      id: id(`apply:${d.label}`),
      group: "Application",
      title: `Submit your application — ${d.label}`,
      ...(d.platform ? { detail: `Apply through ${d.platform}.` } : {}),
      date: d.deadline!.slice(0, 10),
      source: u.officialSourceUrl,
    });
  items.push({
    id: id("statement"),
    group: "Application",
    title: "Personal statement, essays and references",
    detail: `Check exactly what ${first?.platform ?? "the application"} asks for, and give referees plenty of notice.`,
  });

  // Scholarships (ones you'd apply for; guaranteed awards need no application)
  for (const f of a.financial.funding.filter((x) => x.basis !== "guaranteed")) {
    const dated = f.deadline && ISO.test(f.deadline) ? f.deadline.slice(0, 10) : undefined;
    if (dated && dated < now) continue;
    items.push({
      id: id(`sch:${f.name}`),
      group: "Scholarships",
      title: `Apply: ${f.name}`,
      detail: [f.award, f.grades, f.deadline && !dated ? `Deadline: ${f.deadline}` : ""]
        .filter(Boolean)
        .join(" · "),
      ...(dated ? { date: dated } : {}),
      ...(f.source ? { source: f.source } : {}),
    });
  }

  // Visa
  const v = visaFor(u.country);
  if (v) {
    items.push({
      id: id("passport"),
      group: "Visa",
      title: `Passport for your ${v.visa.toLowerCase()} application`,
    });
    for (const m of v.money)
      items.push({
        id: id(`visa:${m.label}`),
        group: "Visa",
        title: m.label === "Plus" ? `Also budget for ${m.value}` : `${m.label}: ${m.value}`,
        ...(v.sources[0] ? { source: v.sources[0].url } : {}),
      });
    if (!v.money.length)
      items.push({
        id: id("visa:check"),
        group: "Visa",
        title: `Check the ${v.visa} requirements`,
        ...(v.note ? { detail: v.note } : {}),
        ...(v.sources[0] ? { source: v.sources[0].url } : {}),
      });
  }
  return items;
}

export const GROUP_ORDER: DocGroup[] = [
  "English test",
  "Grades & tests",
  "Application",
  "Scholarships",
  "Visa",
];
