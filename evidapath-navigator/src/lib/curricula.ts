// The curricula and grade bands students choose from, shared by every form so
// the decision engine always receives the same labels.

export const CURRICULA = [
  "IB Diploma",
  "Cambridge A-Levels",
  "US High School Diploma + APs",
  "UAE Ministry of Education (Emirati Secondary)",
  "Indian CBSE / ISC (Class XII)",
  "German Abitur",
  "National Curriculum / Other",
] as const;

// Each band is described in every scale we compare against. Percentages are for
// percentage-graded curricula (UAE MoE, Indian CBSE/ISC).
export const GRADE_BANDS = [
  "Top Tier: IB 40+ / A*A*A / GPA 4.0 / 95%+",
  "Strong: IB 37-39 / A*AA / GPA 3.8-3.9 / 90-94%",
  "Competitive: IB 34-36 / AAA-AAB / GPA 3.6-3.7 / 85-89%",
  "Foundation: IB 30-33 / ABB-BBB / GPA 3.3-3.5 / 75-84%",
] as const;

/** Percentage range for a band, also for bands saved before % was added. */
export function bandPercent(band: string): { lo: number; hi: number } | null {
  const m = band.match(/(\d{2})\s*-\s*(\d{2})\s*%|(\d{2})\s*%\+/);
  if (m) return m[3] ? { lo: Number(m[3]), hi: 100 } : { lo: Number(m[1]), hi: Number(m[2]) };
  if (/^top/i.test(band)) return { lo: 95, hi: 100 };
  if (/^strong/i.test(band)) return { lo: 90, hi: 94 };
  if (/^competitive/i.test(band)) return { lo: 85, hi: 89 };
  if (/^foundation/i.test(band)) return { lo: 75, hi: 84 };
  return null;
}

/** Show a saved value even if it predates the current list. */
export function withCurrent<T extends string>(list: readonly T[], current: string): string[] {
  return list.includes(current as T) ? [...list] : [current, ...list];
}
