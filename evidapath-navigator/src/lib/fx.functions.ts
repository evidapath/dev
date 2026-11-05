import { createServerFn } from "@tanstack/react-start";

// Exchange rates used ONLY to compare a university's cost against the student's
// USD budget. Source: European Central Bank daily reference rates via Frankfurter.
// AED is pegged by the UAE Central Bank at 3.6725 per USD, so it is fixed here.
// BDT isn't in the ECB set: it comes from Bangladesh Bank's daily USD/BDT
// weighted average rate (WAR), https://www.bb.org.bd/en/index.php/econdata/exchangerate
// If the rates can't be fetched, `rates` is null and callers must not guess.
export interface FxRates {
  /** Units of each currency per 1 USD. */
  rates: Record<string, number>;
  date: string;
  /** Date of Bangladesh Bank's BDT rate, when it loaded. */
  bdtDate?: string;
}

const AED_PER_USD = 3.6725;
const TTL_MS = 12 * 60 * 60 * 1000;
let cache: { at: number; value: FxRates } | null = null;

/** Fetch (or reuse) the rates. Usable directly from other server code. */
export async function loadFxRates(): Promise<FxRates | null> {
  if (cache && Date.now() - cache.at < TTL_MS) return cache.value;
  try {
    const [res, bdt] = await Promise.all([
      fetch("https://api.frankfurter.dev/v1/latest?from=USD"),
      loadBdt(),
    ]);
    if (!res.ok) throw new Error(`FX fetch failed: ${res.status}`);
    const body = (await res.json()) as { date: string; rates: Record<string, number> };
    const value: FxRates = {
      date: body.date,
      rates: { ...body.rates, USD: 1, AED: AED_PER_USD, ...(bdt ? { BDT: bdt.rate } : {}) },
      ...(bdt ? { bdtDate: bdt.date } : {}),
    };
    cache = { at: Date.now(), value };
    return value;
  } catch (err) {
    console.error("[fx] rates unavailable, budget comparison disabled:", err);
    return cache?.value ?? null;
  }
}

/**
 * Bangladesh Bank's USD/BDT weighted average rate (WAR) from its exchange-rate page.
 * Null when the page can't be read or doesn't parse; BDT is then simply unavailable.
 */
async function loadBdt(): Promise<{ rate: number; date: string } | null> {
  try {
    const res = await fetch("https://www.bb.org.bd/en/index.php/econdata/exchangerate");
    if (!res.ok) return null;
    const text = (await res.text())
      .replace(/<[^>]+>/g, " ")
      .replace(/&nbsp;/g, " ")
      .replace(/\s+/g, " ");
    // "A. USD/BDT Exchange Rate Currency Bid Rate Ask Rate WAR USD 124.3200 124.3500 124.3400"
    const m = text.match(/USD\/BDT Exchange Rate.*?USD ([\d.]+) ([\d.]+) ([\d.]+)/);
    const d = text.match(/Exchange Rate of Taka \(([A-Z][a-z]{2} \d{1,2}, \d{4})\)/);
    const rate = m ? Number(m[3]) : NaN;
    // Sanity range so a layout change can't slip in a wrong number.
    if (!(rate > 50 && rate < 300)) return null;
    return { rate, date: d ? new Date(`${d[1]} UTC`).toISOString().slice(0, 10) : "" };
  } catch {
    return null;
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
