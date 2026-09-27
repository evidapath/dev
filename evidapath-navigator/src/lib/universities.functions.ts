import { createServerFn } from "@tanstack/react-start";
import { getUniversitiesFromSanity } from "./sanity.server";
import { UNIVERSITIES_DATA } from "./mock-data";
import type { University } from "./mock-data";

// Reads verified university intelligence from Sanity (server-side). Falls back to
// the illustrative mock set only if Sanity is unreachable/misconfigured, so a
// data outage degrades to clearly-labeled placeholders rather than a broken page.
export const getUniversities = createServerFn({ method: "GET" }).handler(
  async (): Promise<{ universities: University[]; source: "sanity" | "mock" }> => {
    try {
      const universities = await getUniversitiesFromSanity();
      if (universities.length > 0) return { universities, source: "sanity" };
      return { universities: UNIVERSITIES_DATA, source: "mock" };
    } catch (err) {
      console.error("[universities] Sanity fetch failed, using mock fallback:", err);
      return { universities: UNIVERSITIES_DATA, source: "mock" };
    }
  },
);
