import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { ShieldAlert, FileCheck, BadgeCheck } from "lucide-react";
import type { VerificationLevel } from "../../lib/offer-vault.types";
import { formatCurrency } from "../../lib/format";
import { Illustration, type IllustrationName } from "../Illustration";

export function VerificationBadge({ level }: { level: VerificationLevel }) {
  const map = {
    self_reported: {
      label: "Self-reported",
      icon: ShieldAlert,
      cls: "bg-secondary text-muted-foreground border-border",
    },
    document_verified: {
      label: "Document-verified",
      icon: FileCheck,
      cls: "bg-primary/10 text-primary border-primary/30",
    },
    institution_verified: {
      label: "Institution-verified",
      icon: BadgeCheck,
      cls: "bg-primary/15 text-primary border-primary/40",
    },
  } as const;
  const v = map[level];
  const Icon = v.icon;
  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded border ${v.cls}`}
    >
      <Icon className="w-3 h-3" />
      {v.label}
    </span>
  );
}

export function EmptyState({
  icon: Icon,
  illustration,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  illustration?: IllustrationName;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-border bg-card/50 p-10 text-center flex flex-col items-center gap-3 max-w-xl mx-auto">
      {illustration ? (
        <Illustration name={illustration} />
      ) : (
        <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center">
          <Icon className="w-6 h-6 text-muted-foreground" />
        </div>
      )}
      <h3 className="font-display font-bold text-base text-foreground">{title}</h3>
      <p className="text-sm text-muted-foreground leading-relaxed max-w-md">{description}</p>
      {action}
    </div>
  );
}

export function PendingData({ label }: { label: string }) {
  return <span className="font-mono text-xs text-muted-foreground italic">{label}</span>;
}

export function Money({
  value,
  currency = "USD",
  pendingLabel = "Pending verified data",
}: {
  value: number | null;
  currency?: string;
  pendingLabel?: string;
}) {
  if (value === null || value === undefined) return <PendingData label={pendingLabel} />;
  return <span className="font-mono">{formatCurrency(value, currency)}</span>;
}

export function IllustrativePreviewLabel({ text }: { text?: string }) {
  return (
    <div className="flex items-center gap-2 text-[11px] text-muted-foreground bg-secondary/50 border border-border rounded-lg px-3 py-2">
      <span className="inline-block w-1.5 h-1.5 rounded-full bg-bronze" />
      <span>
        {text ?? "Illustrative product preview. Live analysis will use verified EvidaPath data."}
      </span>
    </div>
  );
}

export function SectionCard({
  title,
  subtitle,
  children,
  action,
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 shadow-xs space-y-4">
      {(title || action) && (
        <div className="flex items-start justify-between gap-3 border-b border-border pb-3">
          <div>
            {title && <h3 className="font-display font-bold text-base text-foreground">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

export const inputCls =
  "w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary";
export const labelCls = "block text-xs font-semibold uppercase text-muted-foreground mb-1.5";

// The database only accepts 3-letter ISO codes, so currency is always picked
// from a list (typing "euro" used to make saving fail).
export const CURRENCIES: [string, string][] = [
  ["USD", "US dollar"],
  ["EUR", "Euro"],
  ["GBP", "British pound"],
  ["AED", "UAE dirham"],
  ["CAD", "Canadian dollar"],
  ["AUD", "Australian dollar"],
  ["MYR", "Malaysian ringgit"],
  ["SGD", "Singapore dollar"],
  ["CHF", "Swiss franc"],
  ["HKD", "Hong Kong dollar"],
  ["INR", "Indian rupee"],
  ["SAR", "Saudi riyal"],
  ["QAR", "Qatari riyal"],
  ["NZD", "New Zealand dollar"],
  ["JPY", "Japanese yen"],
  ["CNY", "Chinese yuan"],
];

export function CurrencySelect({
  value,
  onChange,
  id,
}: {
  value: string;
  onChange: (code: string) => void;
  id?: string;
}) {
  const known = CURRENCIES.some(([c]) => c === value);
  return (
    <select id={id} value={value} onChange={(e) => onChange(e.target.value)} className={inputCls}>
      {!known && value && <option value={value}>{value}</option>}
      {CURRENCIES.map(([code, name]) => (
        <option key={code} value={code}>
          {code} — {name}
        </option>
      ))}
    </select>
  );
}
