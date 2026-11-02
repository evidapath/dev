import type { SearchOption } from "../components/SearchSelect";
import type { University } from "./mock-data";

// Short names students type for countries ("uk", "usa", "uae").
const COUNTRY_ALIASES: Record<string, string[]> = {
  "United Kingdom": ["uk", "britain", "england"],
  "United States": ["us", "usa", "america"],
  "United Arab Emirates": ["uae", "emirates", "dubai"],
};

export function universityOption(u: University, label = u.name, group?: string): SearchOption {
  return {
    value: u.id,
    prefix: u.flag,
    label,
    keywords: [u.country, ...(COUNTRY_ALIASES[u.country] ?? [])],
    ...(group ? { group } : {}),
  };
}
