import { useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { getUniversities } from "./universities.functions";
import { getScholarships } from "./scholarships.functions";
import { getFxRates, type FxRates } from "./fx.functions";
import type { Scholarship, University } from "./mock-data";

// One shared fetch of universities + scholarships + FX per page load, so several
// components on the same page (e.g. the home page) don't each refetch.

export interface LiveData {
  universities: University[];
  scholarships: Scholarship[];
  fx: FxRates | null;
  source: "sanity" | "mock";
}

let inflight: Promise<LiveData> | null = null;

export function useLiveData(): { data: LiveData | null; loading: boolean } {
  const [data, setData] = useState<LiveData | null>(null);
  const [loading, setLoading] = useState(true);
  const fetchUnis = useServerFn(getUniversities);
  const fetchSchols = useServerFn(getScholarships);
  const fetchFx = useServerFn(getFxRates);

  useEffect(() => {
    let live = true;
    inflight ??= Promise.all([fetchUnis(), fetchSchols(), fetchFx().catch(() => null)]).then(
      ([u, s, fx]) => ({
        universities: u.universities,
        scholarships: s.scholarships,
        fx,
        source: u.source,
      }),
    );
    inflight
      .then((d) => live && setData(d))
      .catch(() => {
        inflight = null; // allow a retry on the next mount
      })
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [fetchUnis, fetchSchols, fetchFx]);

  return { data, loading };
}
