import { useState } from "react";
import { Trash2 } from "lucide-react";

// Two-step delete: the bin icon asks "Delete? Yes / Cancel" inline instead of
// deleting on the first click (no browser dialog).
export function ConfirmDelete({ label, onConfirm }: { label: string; onConfirm: () => void }) {
  const [asking, setAsking] = useState(false);
  if (!asking)
    return (
      <button
        onClick={() => setAsking(true)}
        className="p-2 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
        aria-label={label}
      >
        <Trash2 className="w-4 h-4" />
      </button>
    );
  return (
    <span className="inline-flex items-center gap-1.5 text-xs" role="group" aria-label={label}>
      <span className="text-muted-foreground">Delete?</span>
      <button
        onClick={() => {
          setAsking(false);
          onConfirm();
        }}
        className="px-2 py-1 rounded-md bg-destructive text-destructive-foreground font-semibold hover:bg-destructive/90"
      >
        Yes
      </button>
      <button
        onClick={() => setAsking(false)}
        className="px-2 py-1 rounded-md border border-border text-foreground hover:bg-secondary"
      >
        Cancel
      </button>
    </span>
  );
}
