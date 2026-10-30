import { useEffect, useState } from "react";

/**
 * Render long lists a page at a time ("Show more"), so a phone isn't asked to
 * lay out 60 rich cards at once. Resets to the first page when `resetKey` changes
 * (e.g. a new search or filter).
 */
export function usePaged<T>(items: T[], resetKey: string, size = 12) {
  const [count, setCount] = useState(size);
  useEffect(() => setCount(size), [resetKey, size]);
  return {
    visible: items.slice(0, count),
    remaining: Math.max(0, items.length - count),
    showMore: () => setCount((c) => c + size),
  };
}
