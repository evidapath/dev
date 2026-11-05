import type { ProgramView } from "./mock-data";

/**
 * Tests a programme lists across its admissions rows (SAT, ACT, TMUA, …), without
 * duplicates. Application forms that some records list as "tests" (e.g. "UCAS
 * Application") are left out: they aren't tests.
 */
export function otherTests(
  p: Pick<ProgramView, "admissionsByCurriculum"> | null | undefined,
): string[] {
  const seen = new Map<string, string>();
  for (const r of p?.admissionsByCurriculum ?? [])
    for (const t of r.tests) {
      if (/application|portfolio|interview/i.test(t)) continue;
      const key = t.replace(/\s*\(.*\)$/, "").toLowerCase();
      if (!seen.has(key)) seen.set(key, t);
    }
  return [...seen.values()];
}
