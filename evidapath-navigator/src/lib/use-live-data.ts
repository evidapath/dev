import { useCallback, useEffect, useState } from "react";
import { useServerFn } from "@tanstack/react-start";
import { getUniversities } from "./universities.functions";
import { getScholarships } from "./scholarships.functions";
import { getFxRates, type FxRates } from "./fx.functions";
import type { Scholarship, University } from "./mock-data";

// Client-side cache for the public reference data (universities, scholarships,
// FX). It changes rarely, so one fetch per 10 minutes is shared by every page:
// moving between pages is instant instead of refetching the same 50+ records.

const TTL_MS = 10 * 60 * 1000;

function cached<T>(load: () => Promise<T>) {
  let entry: { at: number; p: Promise<T> } | null = null;
  return () => {
    if (!entry || Date.now() - entry.at > TTL_MS) {
      const p = load().catch((err: unknown) => {
        entry = null; // let the next caller retry
        throw err;
      });
      entry = { at: Date.now(), p };
    }
    return entry.p;
  };
}

let uniCache: ReturnType<typeof cached<Awaited<ReturnType<typeof getUniversities>>>> | null = null;
let scholCache: ReturnType<typeof cached<Awaited<ReturnType<typeof getScholarships>>>> | null =
  null;
let fxCache: ReturnType<typeof cached<FxRates | null>> | null = null;

/** Drop-in for useServerFn(getUniversities), served from the shared cache. */
export function useUniversitiesFn() {
  const fn = useServerFn(getUniversities);
  return useCallback(() => (uniCache ??= cached(() => fn()))(), [fn]);
}

/**
 * For route loaders: universities rendered into the server HTML, so crawlers and answer
 * engines see the data. In the browser it shares the cache above; on the server it
 * fetches fresh for each request.
 */
export function loadUniversities() {
  if (typeof window === "undefined") return getUniversities();
  return (uniCache ??= cached(() => getUniversities()))();
}

/** Drop-in for useServerFn(getScholarships), served from the shared cache. */
export function useScholarshipsFn() {
  const fn = useServerFn(getScholarships);
  return useCallback(() => (scholCache ??= cached(() => fn()))(), [fn]);
}

/** Drop-in for useServerFn(getFxRates), served from the shared cache. */
export function useFxRatesFn() {
  const fn = useServerFn(getFxRates);
  return useCallback(() => (fxCache ??= cached(() => fn()))(), [fn]);
}

/** Route-loader twins of the hooks above: data rendered into the server HTML. */
export function loadScholarships() {
  if (typeof window === "undefined") return getScholarships();
  return (scholCache ??= cached(() => getScholarships()))();
}
export function loadFx(): Promise<FxRates | null> {
  if (typeof window === "undefined") return getFxRates().catch(() => null);
  return (fxCache ??= cached(() => getFxRates()))().catch(() => null);
}
export async function loadLive(): Promise<LiveData> {
  const [u, s, fx] = await Promise.all([loadUniversities(), loadScholarships(), loadFx()]);
  return { universities: u.universities, scholarships: s.scholarships, fx, source: u.source };
}

export interface LiveData {
  universities: University[];
  scholarships: Scholarship[];
  fx: FxRates | null;
  source: "sanity" | "mock";
}

export function useLiveData(): { data: LiveData | null; loading: boolean } {
  const [data, setData] = useState<LiveData | null>(null);
  const [loading, setLoading] = useState(true);
  const fetchUnis = useUniversitiesFn();
  const fetchSchols = useScholarshipsFn();
  const fetchFx = useFxRatesFn();

  useEffect(() => {
    let live = true;
    Promise.all([fetchUnis(), fetchSchols(), fetchFx().catch(() => null)])
      .then(([u, s, fx]) => {
        if (live)
          setData({
            universities: u.universities,
            scholarships: s.scholarships,
            fx,
            source: u.source,
          });
      })
      .catch(() => {})
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [fetchUnis, fetchSchols, fetchFx]);

  return { data, loading };
}
