// Small line illustrations for empty states. Hand-built SVG in the site's
// palette (primary green, bronze, sky) — light, crisp at any size, no stock art.

export type IllustrationName = "applications" | "offers" | "compare" | "plan" | "search";

const stroke = "var(--color-foreground)";
const green = "var(--color-primary)";
const bronze = "var(--color-bronze)";
const soft = "var(--color-secondary)";
const card = "var(--color-card)";
const onGreen = "var(--color-primary-foreground)";

export function Illustration({
  name,
  className = "w-40 h-28",
}: {
  name: IllustrationName;
  className?: string;
}) {
  return (
    <svg viewBox="0 0 160 112" className={className} fill="none" aria-hidden role="img">
      <ellipse cx="80" cy="102" rx="58" ry="6" fill={soft} />
      {name === "applications" && (
        <g strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="46" y="18" width="62" height="78" rx="8" fill={card} stroke={stroke} />
          <rect x="64" y="12" width="26" height="12" rx="4" fill={soft} stroke={stroke} />
          {[38, 54, 70].map((y, i) => (
            <g key={y}>
              <circle
                cx="60"
                cy={y}
                r="5"
                fill={i < 2 ? green : card}
                stroke={i < 2 ? green : stroke}
              />
              {i < 2 && <path d={`M57.5 ${y} l2 2 l3.5 -4`} stroke={onGreen} />}
              <path d={`M72 ${y} h26`} stroke={stroke} opacity="0.35" />
            </g>
          ))}
          <path d="M112 30 l14 -8 M114 42 l16 0" stroke={green} />
        </g>
      )}
      {name === "offers" && (
        <g strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="36" y="36" width="88" height="58" rx="6" fill={card} stroke={stroke} />
          <path d="M36 42 l44 30 l44 -30" stroke={stroke} />
          <rect x="56" y="14" width="48" height="40" rx="4" fill={card} stroke={stroke} />
          <path d="M64 26 h32 M64 34 h24" stroke={stroke} opacity="0.35" />
          <circle cx="98" cy="46" r="9" fill={green} />
          <path d="M94 46 l3 3 l5 -6" stroke={onGreen} />
        </g>
      )}
      {name === "compare" && (
        <g strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M80 20 v70 M60 92 h40" stroke={stroke} />
          <path d="M40 34 h80" stroke={stroke} />
          <path d="M40 34 l-12 26 h24 z" fill={card} stroke={stroke} />
          <path d="M120 34 l-12 26 h24 z" fill={card} stroke={stroke} />
          <rect x="31" y="50" width="18" height="8" rx="2" fill={green} />
          <rect x="111" y="46" width="18" height="12" rx="2" fill={bronze} />
          <circle cx="80" cy="18" r="4" fill={stroke} />
        </g>
      )}
      {name === "plan" && (
        <g strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="40" y="22" width="80" height="72" rx="8" fill={card} stroke={stroke} />
          <path d="M40 40 h80" stroke={stroke} />
          <path d="M58 16 v12 M102 16 v12" stroke={stroke} />
          {[0, 1, 2, 3].map((c) =>
            [0, 1, 2].map((r) => (
              <rect
                key={`${c}${r}`}
                x={50 + c * 17}
                y={48 + r * 14}
                width="10"
                height="8"
                rx="2"
                fill={c === 2 && r === 1 ? green : c === 3 && r === 0 ? bronze : soft}
              />
            )),
          )}
        </g>
      )}
      {name === "search" && (
        <g strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="72" cy="52" r="24" fill={card} stroke={stroke} />
          <path d="M90 70 l20 20" stroke={stroke} strokeWidth="5" />
          <path d="M60 52 h24 M72 40 v24" stroke={green} />
        </g>
      )}
    </svg>
  );
}
