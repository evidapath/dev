export function ShowMore({
  remaining,
  onClick,
  noun,
}: {
  remaining: number;
  onClick: () => void;
  noun: string;
}) {
  if (remaining <= 0) return null;
  return (
    <div className="flex justify-center pt-2">
      <button
        onClick={onClick}
        className="h-10 px-5 rounded-lg border border-border bg-card text-sm font-semibold text-foreground hover:bg-secondary hover:border-primary/40 transition-colors"
      >
        Show more {noun} ({remaining} left)
      </button>
    </div>
  );
}
