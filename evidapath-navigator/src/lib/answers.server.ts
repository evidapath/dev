// Answers to the questions students search for (AnswerThePublic, see
// fact-checks/aeo/answerthepublic/), built only from verified Sanity records. Every figure
// carries the university, programme, academic year and the source page it was read from.
// Records not re-checked against their source are left out.

import { notChecked, sanityQuery, tierKind } from "./sanity.server";

export interface FeeFact {
  university: string;
  universityId: string;
  city: string | null;
  programme: string;
  tuition: number;
  currency: string;
  year: string | null;
  sourceUrl: string | null;
  sourceTitle: string | null;
  /** The record's own explanation of the figure (e.g. a whole-course total spread over years). */
  note: string | null;
}

export interface CountryCost {
  country: string;
  currency: string;
  universities: number;
  programmes: number;
  lowest: FeeFact;
  highest: FeeFact;
  /** Each university's lowest-fee programme, cheapest first. */
  perUniversity: FeeFact[];
}

export interface RequirementFact {
  university: string;
  programme: string;
  curriculum: string;
  text: string;
  year: string | null;
  sourceUrl: string | null;
  sourceTitle: string | null;
}

export interface AnswersData {
  costs: CountryCost[];
  ib: RequirementFact[];
  english: RequirementFact[];
  sat: RequirementFact[];
}

const COSTS_QUERY = `*[_type=="costProfile" && defined(tuition_annual) && defined(program_ref)]{
  tuition_annual, currency, academic_year, verification_status, tuition_basis,
  "feeNote": extension_metadata.fields[key=="fee_note"][0].value,
  "residencyLabel": residency_category_ref->label,
  "programme": program_ref->{program_name, degree_type,
    "uni": university_ref->{id, canonical_name, "country": country_ref->name, "city": primary_city_ref->name}},
  "source": source_refs[0]->{url, title}
}`;

const ADMISSIONS_QUERY = `*[_type=="admissionsRequirement" && defined(program_ref)]{
  curriculum_type, academic_threshold, verification_status, academic_year,
  "tests": standardized_tests[]{test_name, required, notes},
  "english": language_requirements[]{language, min_score},
  "programme": program_ref->{program_name, degree_type,
    "uni": university_ref->{id, canonical_name}},
  "source": source_refs[0]->{url, title}
}`;

interface CostRow {
  tuition_annual: number;
  currency: string | null;
  academic_year: string | null;
  verification_status: string | null;
  tuition_basis: string | null;
  feeNote: string | null;
  residencyLabel: string | null;
  programme: {
    program_name: string | null;
    degree_type: string | null;
    uni: { id: string; canonical_name: string; country: string | null; city: string | null } | null;
  } | null;
  source: { url: string | null; title: string | null } | null;
}

interface AdmissionRow {
  curriculum_type: string | null;
  academic_threshold: string | null;
  verification_status: string | null;
  academic_year: string | null;
  tests: { test_name: string | null; required: string | null; notes: string | null }[] | null;
  english: { language: string | null; min_score: string | null }[] | null;
  programme: {
    program_name: string | null;
    degree_type: string | null;
    uni: { id: string; canonical_name: string } | null;
  } | null;
  source: { url: string | null; title: string | null } | null;
}

// Fee notes can carry research remarks after the explanation; keep the first sentence,
// which says how the figure is made up.
const firstSentence = (t: string | null) =>
  t ? t.split(/(?<=[a-z0-9)%])\.\s+(?=[A-Z])/)[0]!.replace(/\.?$/, ".") : null;

// A note is shown to students only when it explains the figure beside it: it must contain
// that figure and no research remarks (estimates, "secondary sources", field names). Notes
// written for an earlier year's fee, or for the research log, stay off the page.
const RESEARCH_REMARK =
  /~|≈|=>|conflict|secondary source|confidence|primary source|_|verify|re-check|expected|approx|estimate/i;
function noteFor(note: string | null, tuition: number): string | null {
  // A recorded conflict between official pages must stay visible, in plain words.
  if (note && /source conflict/i.test(note))
    return "The university's own pages give different figures for this fee; confirm with the university.";
  const t = firstSentence(note);
  if (!t || RESEARCH_REMARK.test(t)) return null;
  // A sentence cut short by the splitter (e.g. at "incl.") leaves a bracket open.
  if ((t.match(/\(/g) ?? []).length !== (t.match(/\)/g) ?? []).length) return null;
  const n = Math.round(tuition);
  const shown = [String(n), n.toLocaleString("en-US")];
  return shown.some((x) => t.includes(x)) ? t : null;
}

// The academic year as stored can carry a working note in brackets; show the year only.
const shortYear = (y: string | null) => (y ? y.split(" (")[0]!.trim() : null);
const progName = (p: { program_name: string | null; degree_type: string | null }) => {
  const name = p.program_name ?? "Programme";
  return p.degree_type && !name.includes(`(${p.degree_type})`)
    ? `${name} (${p.degree_type})`
    : name;
};

/** Universities named in the questions students searched for (AnswerThePublic, UAE). */
const IB_ASKED = ["ca-university-of-toronto", "uk-warwick", "ca-waterloo"];
const ENGLISH_ASKED = ["ae-uaeu"];
const SAT_ASKED = ["ae-aus", "us-harvard", "us-mit"];

export async function getAnswersFromSanity(): Promise<AnswersData> {
  const [costRows, admissionRows] = await Promise.all([
    sanityQuery<CostRow[]>(COSTS_QUERY),
    sanityQuery<AdmissionRow[]>(ADMISSIONS_QUERY),
  ]);

  // Fees international students pay: the international tier, or one fee for everyone.
  const fees: (FeeFact & { country: string })[] = [];
  for (const r of costRows) {
    const uni = r.programme?.uni;
    if (!uni?.country || !r.currency || notChecked(r.verification_status)) continue;
    const kind = tierKind(r.residencyLabel ?? "International students");
    if (kind !== "international" && kind !== "uniform") continue;
    fees.push({
      country: uni.country,
      university: uni.canonical_name,
      universityId: uni.id,
      city: uni.city,
      programme: progName(r.programme!),
      tuition: Math.round(r.tuition_annual),
      currency: r.currency,
      year: shortYear(r.academic_year),
      sourceUrl: r.source?.url ?? null,
      sourceTitle: r.source?.title ?? null,
      note:
        noteFor(r.feeNote, r.tuition_annual) ??
        (r.tuition_basis === "per-credit"
          ? "Worked out from the published per-credit rate."
          : null),
    });
  }

  // One group per country and currency: fees in different currencies are never compared.
  const groups = new Map<string, (FeeFact & { country: string })[]>();
  for (const f of fees) {
    const k = `${f.country}|${f.currency}`;
    groups.set(k, [...(groups.get(k) ?? []), f]);
  }
  const costs: CountryCost[] = [];
  for (const list of groups.values()) {
    const sorted = [...list].sort((a, b) => a.tuition - b.tuition);
    const perUni = new Map<string, FeeFact>();
    for (const f of sorted) if (!perUni.has(f.universityId)) perUni.set(f.universityId, f);
    costs.push({
      country: sorted[0]!.country,
      currency: sorted[0]!.currency,
      universities: perUni.size,
      programmes: sorted.length,
      lowest: sorted[0]!,
      highest: sorted.at(-1)!,
      perUniversity: [...perUni.values()],
    });
  }
  costs.sort((a, b) => a.country.localeCompare(b.country) || b.programmes - a.programmes);

  const req = (r: AdmissionRow, text: string, curriculum: string): RequirementFact => ({
    university: r.programme!.uni!.canonical_name,
    programme: progName(r.programme!),
    curriculum,
    text,
    year: shortYear(r.academic_year),
    sourceUrl: r.source?.url ?? null,
    sourceTitle: r.source?.title ?? null,
  });
  const checked = admissionRows.filter(
    (r) => r.programme?.uni && !notChecked(r.verification_status),
  );
  const ib = checked
    .filter(
      (r) =>
        IB_ASKED.includes(r.programme!.uni!.id) &&
        /baccalaureate|\bIB\b/i.test(r.curriculum_type ?? "") &&
        r.academic_threshold,
    )
    .map((r) => req(r, r.academic_threshold!, "IB"));
  const englishSeen = new Set<string>();
  const english = checked
    .filter((r) => ENGLISH_ASKED.includes(r.programme!.uni!.id))
    .flatMap((r) =>
      (r.english ?? [])
        .filter((l) => l.min_score && /^(en|english)$/i.test(l.language ?? ""))
        .map((l) => req(r, l.min_score!, r.curriculum_type ?? "")),
    )
    .filter((f) => {
      const k = `${f.programme}|${f.text}`;
      if (englishSeen.has(k)) return false;
      englishSeen.add(k);
      return true;
    });
  const satSeen = new Set<string>();
  const sat = checked
    .filter((r) => SAT_ASKED.includes(r.programme!.uni!.id))
    .flatMap((r) =>
      (r.tests ?? [])
        .filter((t) => /\bSAT\b/i.test(t.test_name ?? ""))
        .map((t) =>
          req(
            r,
            `${t.test_name}: ${(t.required ?? "not stated").replace(/_/g, " ")}${t.notes ? `. ${t.notes}` : ""}`,
            r.curriculum_type ?? "",
          ),
        ),
    )
    .filter((f) => {
      const k = `${f.university}|${f.programme}|${f.text}`;
      if (satSeen.has(k)) return false;
      satSeen.add(k);
      return true;
    });

  const byUniProg = (a: RequirementFact, b: RequirementFact) =>
    a.university.localeCompare(b.university) || a.programme.localeCompare(b.programme);
  return {
    costs,
    ib: ib.sort(byUniProg),
    english: english.sort(byUniProg),
    sat: sat.sort(byUniProg),
  };
}
