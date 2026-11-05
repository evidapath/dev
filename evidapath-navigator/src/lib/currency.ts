import { useEffect, useState } from "react";
import type { FxRates } from "./fx.functions";

// The currency a student thinks in. Budgets are still stored and compared in USD;
// this only changes how they're shown and typed. Remembered on this device.

const KEY = "evidapath.currency";
const EVENT = "evidapath:currency";

/** Currencies offered in the picker: every ECB reference currency, plus AED and BDT. */
export const CURRENCIES: readonly (readonly [
  code: string,
  name: string,
  flag: string,
  keywords?: string,
])[] = [
  ["USD", "US dollar", "🇺🇸", "united states america"],
  ["EUR", "Euro", "🇪🇺", "europe germany france netherlands spain italy ireland"],
  ["GBP", "British pound", "🇬🇧", "uk united kingdom sterling"],
  ["AED", "UAE dirham", "🇦🇪", "emirates dubai abu dhabi"],
  ["INR", "Indian rupee", "🇮🇳", "india"],
  ["CNY", "Chinese yuan", "🇨🇳", "china renminbi rmb"],
  ["MYR", "Malaysian ringgit", "🇲🇾", "malaysia"],
  ["SGD", "Singapore dollar", "🇸🇬", "singapore"],
  ["HKD", "Hong Kong dollar", "🇭🇰", "hong kong"],
  ["IDR", "Indonesian rupiah", "🇮🇩", "indonesia"],
  ["PHP", "Philippine peso", "🇵🇭", "philippines"],
  ["THB", "Thai baht", "🇹🇭", "thailand"],
  ["KRW", "South Korean won", "🇰🇷", "korea"],
  ["JPY", "Japanese yen", "🇯🇵", "japan"],
  ["BDT", "Bangladeshi taka", "🇧🇩", "bangladesh"],
  ["CAD", "Canadian dollar", "🇨🇦", "canada"],
  ["AUD", "Australian dollar", "🇦🇺", "australia"],
  ["NZD", "New Zealand dollar", "🇳🇿", "new zealand"],
  ["CHF", "Swiss franc", "🇨🇭", "switzerland"],
  ["SEK", "Swedish krona", "🇸🇪", "sweden"],
  ["NOK", "Norwegian krone", "🇳🇴", "norway"],
  ["DKK", "Danish krone", "🇩🇰", "denmark"],
  ["ISK", "Icelandic króna", "🇮🇸", "iceland"],
  ["PLN", "Polish złoty", "🇵🇱", "poland zloty"],
  ["CZK", "Czech koruna", "🇨🇿", "czech republic czechia"],
  ["HUF", "Hungarian forint", "🇭🇺", "hungary"],
  ["RON", "Romanian leu", "🇷🇴", "romania"],
  ["TRY", "Turkish lira", "🇹🇷", "turkey türkiye"],
  ["ILS", "Israeli shekel", "🇮🇱", "israel"],
  ["ZAR", "South African rand", "🇿🇦", "south africa"],
  ["BRL", "Brazilian real", "🇧🇷", "brazil"],
  ["MXN", "Mexican peso", "🇲🇽", "mexico"],
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
