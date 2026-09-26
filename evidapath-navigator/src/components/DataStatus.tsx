// Single, consistent data-trust status treatment used across the app.
// Consolidates repeated caveats ("illustrative product preview",
// "pending verified data", "datasets being verified") into one component
// so the same copy is not repeated on every card.

import { ShieldCheck } from "lucide-react";

type StatusLevel = "live" | "beta" | "illustrative" | "pending" | "coming";

const LEVELS: Record<StatusLevel, { label: string; dot: string; text: string; chip: string }> = {
  live: {
    label: "LIVE",
    dot: "bg-primary",
    text: "text-primary",
    chip: "bg-primary/10 text-primary",
  },
  beta: {
    label: "BETA",
    dot: "bg-bronze",
    text: "text-bronze",
    chip: "bg-bronze/10 text-bronze",
  },
  illustrative: {
    label: "ILLUSTRATIVE",
    dot: "bg-bronze",
    text: "text-bronze",
    chip: "bg-bronze/10 text-bronze",
  },
  pending: {
    label: "NOT YET VERIFIED",
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
    chip: "bg-secondary text-muted-foreground",
  },
  coming: {
    label: "COMING LATER",
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
    chip: "bg-secondary text-muted-foreground",
  },
};

/** Compact inline status chip — use inside cards / tables. */
export function StatusChip({ level = "pending" }: { level?: StatusLevel }) {
  const s = LEVELS[level];
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${s.chip}`}
    >
      <span className={`inline-block w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {s.label}
    </span>
  );
}

/**
 * Page-level status banner. Use ONCE per page/section instead of repeating
 * the same caveat across multiple cards.
 */
export function DataStatus({
  level = "illustrative",
  children,
}: {
  level?: StatusLevel;
  children?: React.ReactNode;
}) {
  const s = LEVELS[level];
  return (
    <div className="flex items-start gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
      <ShieldCheck className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${s.text}`} />
      <span>
        {children ??
          "Illustrative product preview. Live analysis will use verified EvidaPath data as datasets are built and verified."}
      </span>
    </div>
  );
}

/** Neutral placeholder line for a single empty data field. */
export function PendingValue({ label }: { label?: string }) {
  return (
    <span className="font-mono font-medium text-muted-foreground">
      {label ?? "Pending verified data"}
    </span>
  );
}
