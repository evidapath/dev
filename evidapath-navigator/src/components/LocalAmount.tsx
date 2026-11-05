import { useEffect, useState } from "react";
import { fmtInShort, useCurrency } from "../lib/currency";
import type { FxRates } from "../lib/fx.functions";
import { useFxRatesFn } from "../lib/use-live-data";

/** A USD price in the student's chosen currency ("≈ 2.16M BDT"); nothing when it's USD. */
export function LocalAmount({ usd, className = "" }: { usd: number | null; className?: string }) {
  const [cur] = useCurrency();
  const fetchFx = useFxRatesFn();
  const [fx, setFx] = useState<FxRates | null>(null);
  useEffect(() => {
    if (cur === "USD") return;
    let live = true;
    fetchFx()
      .then((r) => live && setFx(r))
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [cur, fetchFx]);
  if (cur === "USD" || usd == null) return null;
  const text = fmtInShort(usd, cur, fx);
  return text ? <p className={`text-[10px] text-muted-foreground ${className}`}>{text}</p> : null;
}
