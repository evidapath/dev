import { createServerFn } from "@tanstack/react-start";
import { getScholarshipsFromSanity } from "./sanity.server";
import { SCHOLARSHIPS_DATA } from "./mock-data";
import type { Scholarship } from "./mock-data";

// Reads scholarship intelligence from Sanity (server-side). Falls back to the
// illustrative mock set if Sanity is unreachable, so an outage degrades to
// clearly-labeled placeholders rather than a broken page.
export const getScholarships = createServerFn({ method: "GET" }).handler(
  async (): Promise<{ scholarships: Scholarship[]; source: "sanity" | "mock" }> => {
    try {
      const scholarships = await getScholarshipsFromSanity();
      if (scholarships.length > 0) return { scholarships, source: "sanity" };
      return { scholarships: SCHOLARSHIPS_DATA, source: "mock" };
    } catch (err) {
      console.error("[scholarships] Sanity fetch failed, using mock fallback:", err);
      return { scholarships: SCHOLARSHIPS_DATA, source: "mock" };
    }
  },
);
