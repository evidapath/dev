import { useEffect, useState } from "react";
import type { FxRates } from "./fx.functions";

// The currency a student thinks in. Budgets are still stored and compared in USD;
// this only changes how they're shown and typed. Remembered on this device.

const KEY = "evidapath.currency";
const EVENT = "evidapath:currency";

/** Currencies offered in the picker (all have an official daily rate). */
export const CURRENCIES: readonly (readonly [string, string])[] = [
  ["USD", "US dollar"],
  ["BDT", "Bangladeshi taka"],
  ["INR", "Indian rupee"],
  ["AED", "UAE dirham"],
  ["GBP", "British pound"],
  ["EUR", "Euro"],
  ["MYR", "Malaysian ringgit"],
  ["CNY", "Chinese yuan"],
  ["SGD", "Singapore dollar"],
  ["HKD", "Hong Kong dollar"],
  ["IDR", "Indonesian rupiah"],
  ["PHP", "Philippine peso"],
  ["THB", "Thai baht"],
  ["KRW", "South Korean won"],
  ["JPY", "Japanese yen"],
  ["CAD", "Canadian dollar"],
  ["AUD", "Australian dollar"],
  ["NZD", "New Zealand dollar"],
  ["CHF", "Swiss franc"],
  ["TRY", "Turkish lira"],
  ["ZAR", "South African rand"],
  ["BRL", "Brazilian real"],
  ["MXN", "Mexican peso"],
];

function read(): string {
  try {
    return localStorage.getItem(KEY) || "USD";
  } catch {
    return "USD";
  }
}

/** The chosen display currency, shared by every budget control on the page. */
export function useCurrency(): [string, (c: string) => void] {
  const [cur, setCur] = useState("USD");
  useEffect(() => {
    const sync = () => setCur(read());
    sync();
    window.addEventListener(EVENT, sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener(EVENT, sync);
      window.removeEventListener("storage", sync);
    };
  }, []);
  const set = (c: string) => {
    try {
      localStorage.setItem(KEY, c);
    } catch {
      /* storage unavailable: this page still uses it */
    }
    setCur(c);
    window.dispatchEvent(new Event(EVENT));
  };
  return [cur, set];
}

/** Units of `cur` per USD, or null when the rate isn't available. */
export function rateOf(cur: string, fx: FxRates | null): number | null {
  if (cur === "USD") return 1;
  return fx?.rates[cur] ?? null;
}

/** "4,973,600 BDT", rounded to a sensible step for the size of the number. */
export function fmtIn(usd: number, cur: string, fx: FxRates | null): string | null {
  const r = rateOf(cur, fx);
  if (r == null) return null;
  const v = usd * r;
  const step = v >= 1e7 ? 1e5 : v >= 1e6 ? 1e4 : v >= 1e5 ? 1e3 : v >= 1e4 ? 100 : 10;
  return `${(Math.round(v / step) * step).toLocaleString("en-US")} ${cur}`;
}

/** "≈ 2.16M BDT" / "≈ 640k INR": a short local equivalent for prices shown in USD. */
export function fmtInShort(usd: number, cur: string, fx: FxRates | null): string | null {
  const r = rateOf(cur, fx);
  if (r == null) return null;
  const v = usd * r;
  const n =
    v >= 1e9
      ? `${(v / 1e9).toFixed(2)}B`
      : v >= 1e6
        ? `${(v / 1e6).toFixed(2)}M`
        : v >= 1e4
          ? `${Math.round(v / 1e3)}k`
          : Math.round(v).toLocaleString("en-US");
  return `≈ ${n} ${cur}`;
}
