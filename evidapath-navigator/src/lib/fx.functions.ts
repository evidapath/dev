import { createServerFn } from "@tanstack/react-start";

// Exchange rates used ONLY to compare a university's cost against the student's
// USD budget. Source: European Central Bank daily reference rates via Frankfurter.
// AED is pegged by the UAE Central Bank at 3.6725 per USD, so it is fixed here.
// If the rates can't be fetched, `rates` is null and callers must not guess.
export interface FxRates {
  /** Units of each currency per 1 USD. */
  rates: Record<string, number>;
  date: string;
}

const AED_PER_USD = 3.6725;
const TTL_MS = 12 * 60 * 60 * 1000;
let cache: { at: number; value: FxRates } | null = null;

/** Fetch (or reuse) the rates. Usable directly from other server code. */
export async function loadFxRates(): Promise<FxRates | null> {
  if (cache && Date.now() - cache.at < TTL_MS) return cache.value;
  try {
    const res = await fetch("https://api.frankfurter.dev/v1/latest?from=USD");
    if (!res.ok) throw new Error(`FX fetch failed: ${res.status}`);
    const body = (await res.json()) as { date: string; rates: Record<string, number> };
    const value: FxRates = {
      date: body.date,
      rates: { ...body.rates, USD: 1, AED: AED_PER_USD },
    };
    cache = { at: Date.now(), value };
    return value;
  } catch (err) {
    console.error("[fx] rates unavailable, budget comparison disabled:", err);
    return cache?.value ?? null;
  }
}

export const getFxRates = createServerFn({ method: "GET" }).handler(loadFxRates);

/** Convert an amount in `currency` to USD, or null if the rate is unknown. */
export function toUsd(amount: number, currency: string, fx: FxRates | null): number | null {
  const rate = fx?.rates[currency.toUpperCase()];
  return rate ? amount / rate : null;
}

/** Convert between two currencies via USD, or null if either rate is unknown. */
export function convert(
  amount: number,
  from: string,
  to: string,
  fx: FxRates | null,
): number | null {
  if (from.toUpperCase() === to.toUpperCase()) return amount;
  const usd = toUsd(amount, from, fx);
  const rate = fx?.rates[to.toUpperCase()];
  return usd != null && rate ? usd * rate : null;
}
