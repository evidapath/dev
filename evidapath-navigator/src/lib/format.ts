// Helper for rendering nullable cost fields that have no verified source yet.
// Returns a neutral placeholder string instead of fabricated numbers.

export function formatCost(value: number | null, currency?: string): string {
  if (value === null || value === undefined) {
    return "Pending verified data";
  }
  const formatted = value.toLocaleString();
  return currency ? `${formatted} ${currency}` : formatted;
}

export function formatCurrency(value: number | null, currency = "USD"): string {
  if (value === null || value === undefined) {
    return "Pending verified data";
  }
  // "$" only for US dollars; other currencies read "15,000 EUR", never "$15,000 EUR".
  return currency === "USD"
    ? `$${value.toLocaleString()} USD`
    : `${value.toLocaleString()} ${currency}`;
}

export function isPending(value: number | null | undefined): boolean {
  return value === null || value === undefined;
}
