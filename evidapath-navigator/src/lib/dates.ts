/** "2026-10-21" → "Oct 2026"; anything else (e.g. "Not yet verified") is returned as is. */
export function monthYear(date: string): string {
  if (!/^\d{4}-\d{2}-\d{2}/.test(date)) return date;
  return new Date(`${date.slice(0, 10)}T00:00:00Z`).toLocaleDateString("en-GB", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

/** "Checked Oct 2026", or null when there's no real date. */
export function checkedLabel(date: string | null | undefined): string | null {
  return date && /^\d{4}-\d{2}-\d{2}/.test(date) ? `Checked ${monthYear(date)}` : null;
}
