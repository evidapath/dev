// Helper for rendering nullable cost fields that have no verified source yet.
// Returns a neutral placeholder string instead of fabricated numbers.

/** Shown wherever an official figure doesn't exist (or isn't published) yet. */
export const NOT_PUBLISHED = "Not published";

/** One money style across the site: whole units, then the currency code ("39,062 USD"). */
function money(value: number, currency?: string): string {
  const n = Math.round(value).toLocaleString("en-US");
  return currency ? `${n} ${currency}` : n;
}

export function formatCost(value: number | null, currency?: string): string {
  if (value === null || value === undefined) return NOT_PUBLISHED;
  return money(value, currency);
}

export function formatCurrency(value: number | null, currency = "USD"): string {
  if (value === null || value === undefined) return NOT_PUBLISHED;
  return money(value, currency);
}

export function isPending(value: number | null | undefined): boolean {
  return value === null || value === undefined;
}
