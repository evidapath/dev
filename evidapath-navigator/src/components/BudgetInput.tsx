import { useEffect, useState } from "react";
import { BUDGET_MAX, BUDGET_MIN } from "../lib/budget";
import { CURRENCIES, fmtIn, rateOf, useCurrency } from "../lib/currency";
import type { FxRates } from "../lib/fx.functions";
import { SearchSelect, type SearchOption } from "./SearchSelect";

const CURRENCY_OPTIONS: SearchOption[] = CURRENCIES.map(([code, name, flag, kw]) => ({
  value: code,
  label: `${code} · ${name}`,
  short: code,
  prefix: flag,
  keywords: [code, name, ...(kw ? [kw] : [])],
}));
import { useFxRatesFn } from "../lib/use-live-data";

/**
 * A yearly budget control in the student's own currency. The value stays in USD
 * (what matching uses); the picker changes how it's shown and lets the student
 * type an exact amount in their currency.
 */
export function BudgetInput({
  usd,
  onChange,
  label = "Annual budget",
  id = "budget",
  max = BUDGET_MAX,
  noLimitAtMax = true,
  hint = "The whole year: tuition, fees and living costs, not tuition only.",
}: {
  usd: number;
  onChange: (usd: number) => void;
  label?: string;
  id?: string;
  max?: number;
  /** The top of the slider means "no limit" (budget filters), not a number. */
  noLimitAtMax?: boolean;
  /** What the amount covers, shown under the label. */
  hint?: string;
}) {
  const [cur, setCur] = useCurrency();
  const fetchFx = useFxRatesFn();
  const [fx, setFx] = useState<FxRates | null>(null);
  useEffect(() => {
    let live = true;
    fetchFx()
      .then((r) => live && setFx(r))
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [fetchFx]);

  const rate = rateOf(cur, fx);
  const noLimit = noLimitAtMax && usd >= max;
  const local = fmtIn(usd, cur, fx);
  const usdText = `$${Math.round(usd).toLocaleString("en-US")}`;
  const shown = noLimit ? "No limit" : cur === "USD" || !local ? `${usdText}/yr` : `${local}/yr`;

  // Typing an exact amount in the chosen currency.
  const [typed, setTyped] = useState("");
  const commit = () => {
    const n = Number(typed.replace(/[^\d.]/g, ""));
    if (n > 0 && rate) onChange(Math.min(max, Math.max(BUDGET_MIN, Math.round(n / rate))));
    setTyped("");
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap justify-between items-center gap-2">
        <label htmlFor={id} className="text-xs font-semibold uppercase text-muted-foreground">
          {label}
        </label>
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-foreground">{shown}</span>
          <SearchSelect
            aria-label="Currency"
            options={CURRENCY_OPTIONS}
            value={cur}
            onChange={setCur}
            searchPlaceholder="Type a currency or country…"
            className="h-8 min-w-24 rounded-md border border-input bg-background px-2 text-xs font-semibold text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
          />
        </div>
      </div>
      {hint && <p className="text-[11px] text-muted-foreground -mt-1">{hint}</p>}
      <input
        id={id}
        type="range"
        min={BUDGET_MIN}
        max={max}
        step="5000"
        value={Math.min(Math.max(usd, BUDGET_MIN), max)}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-primary"
        aria-label={`${label} (shown in ${cur})`}
      />
      <div className="flex justify-between items-center gap-2 text-[10px] text-muted-foreground">
        <span>{fmtIn(BUDGET_MIN, cur, fx) ?? `$${BUDGET_MIN / 1000}k`}</span>
        {cur !== "USD" && !noLimit && <span>≈ {usdText} a year</span>}
        <span>
          {fmtIn(max, cur, fx) ?? `$${max / 1000}k`}
          {noLimitAtMax ? "+ (no limit)" : ""}
        </span>
      </div>
      {cur !== "USD" &&
        (rate ? (
          <div className="flex items-center gap-2">
            <input
              inputMode="decimal"
              placeholder={`Or type an amount in ${cur}`}
              value={typed}
              onChange={(e) => setTyped(e.target.value)}
              onBlur={commit}
              onKeyDown={(e) => e.key === "Enter" && commit()}
              className="h-8 flex-1 min-w-0 rounded-md border border-input bg-background px-2 text-xs text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
              aria-label={`Type your yearly budget in ${cur}`}
            />
            <span className="text-[10px] text-muted-foreground shrink-0">
              {cur === "BDT"
                ? `Bangladesh Bank rate${fx?.bdtDate ? `, ${fx.bdtDate}` : ""}`
                : cur === "AED"
                  ? "UAE Central Bank peg"
                  : `ECB rate${fx?.date ? `, ${fx.date}` : ""}`}
            </span>
          </div>
        ) : (
          <p className="text-[10px] text-bronze">
            The {cur} rate isn't available right now, so the budget is shown in USD.
          </p>
        ))}
    </div>
  );
}
