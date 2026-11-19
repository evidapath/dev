import { createServerFn } from "@tanstack/react-start";
import { getAnswersFromSanity, type AnswersData } from "./answers.server";
import { getScholarshipsFromSanity } from "./sanity.server";
import type { Scholarship } from "./mock-data";

// Data for /answers: verified records only. No mock fallback; if Sanity is unreachable the
// page says so instead of showing placeholder figures as answers.
export const getAnswers = createServerFn({ method: "GET" }).handler(
  async (): Promise<{ data: AnswersData; uaeScholarships: Scholarship[] } | null> => {
    try {
      const [data, scholarships] = await Promise.all([
        getAnswersFromSanity(),
        getScholarshipsFromSanity(),
      ]);
      const uaeScholarships = scholarships.filter((s) =>
        s.countriesOfStudy.some((c) => /united arab emirates|\bUAE\b/i.test(c)),
      );
      return { data, uaeScholarships };
    } catch (err) {
      console.error("[answers] Sanity fetch failed:", err);
      return null;
    }
  },
);
