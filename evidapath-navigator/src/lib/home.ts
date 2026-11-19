import type { Scholarship, University } from "./mock-data";

// Homepage hero picks, shared by the server loader (so the first paint already has them)
// and the page (which recomputes once the full data arrives in the browser).

/** Fully priced and checked, one per country, so the preview shows a spread. */
export function pickFeatured(all: University[]): University[] {
  const good = all.filter(
    (u) => u.costs.totalAnnual != null && u.evidenceConfidence.startsWith("Verified"),
  );
  const seen = new Set<string>();
  const spread = good.filter((u) => !seen.has(u.country) && seen.add(u.country));
  return (spread.length >= 3 ? spread : good.length >= 3 ? good : all).slice(0, 3);
}

export type HomeStats = (readonly [number, string])[];

export function homeStats(unis: University[], scholarships: Scholarship[]): HomeStats | null {
  if (!unis.length) return null;
  return [
    [unis.length, "universities"],
    [new Set(unis.map((u) => u.country)).size, "countries"],
    [unis.reduce((n, u) => n + (u.programDetails?.length || 1), 0), "programmes"],
    [
      scholarships.filter((x) => x.verificationStatus.startsWith("Verified")).length,
      "scholarships checked",
    ],
  ];
}
