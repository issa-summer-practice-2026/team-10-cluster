import type { ReactNode } from "react";

import { useBlink } from "../hooks/useBlink";
import type { TelltaleName, Telltales } from "../types";

// Simple, recognizable inline-SVG telltale glyphs (24x24, using currentColor).
const ICONS: Partial<Record<TelltaleName, ReactNode>> = {
  left: <polygon points="15,5 6,12 15,19" fill="currentColor" />,
  right: <polygon points="9,5 18,12 9,19" fill="currentColor" />,
  high_beam: (
    <g>
      <path d="M6 6 Q15 6 15 12 Q15 18 6 18 Z" fill="currentColor" />
      <g stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
        <line x1="1" y1="8" x2="4" y2="8" />
        <line x1="1" y1="12" x2="4" y2="12" />
        <line x1="1" y1="16" x2="4" y2="16" />
      </g>
    </g>
  ),
  check_engine: (
    <path
      d="M4 10h2V8h3l1.5-1.5h3V8H20a1 1 0 0 1 1 1v2h1v3h-1v2a1 1 0 0 1-1 1h-9l-2-2H4z"
      fill="currentColor"
    />
  ),
  oil: (
    <g fill="currentColor">
      <path d="M3 13h10l4-2 4 1v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <path d="M18 7c1.2 1.6 1.2 2.6 0 3.3-1.2-.7-1.2-1.7 0-3.3z" />
    </g>
  ),
  battery: (
    <g>
      <rect x="3" y="8" width="18" height="11" rx="1.5" fill="currentColor" />
      <rect x="6" y="5" width="3" height="3" fill="currentColor" />
      <rect x="15" y="5" width="3" height="3" fill="currentColor" />
      <g stroke="var(--bg-0)" strokeWidth="1.6" strokeLinecap="round">
        <line x1="6" y1="13.5" x2="9" y2="13.5" />
        <line x1="7.5" y1="12" x2="7.5" y2="15" />
        <line x1="15" y1="13.5" x2="18" y2="13.5" />
      </g>
    </g>
  ),
  coolant: (
    <g>
      <rect x="10.5" y="3" width="3" height="10" rx="1.5" fill="currentColor" />
      <circle cx="12" cy="15" r="3.2" fill="currentColor" />
      <path
        d="M3 20 q2 -2 4 0 t4 0 t4 0 t4 0"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
      />
    </g>
  ),
  low_fuel: (
    <g>
      <path d="M5 4a1 1 0 0 1 1-1h5a1 1 0 0 1 1 1v15H5z" fill="currentColor" />
      <path
        d="M12 8h3a2 2 0 0 1 2 2v5a1.5 1.5 0 0 0 3 0v-6l-2.2-2.2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
      <line x1="4" y1="20" x2="13" y2="20" stroke="currentColor" strokeWidth="1.8" />
    </g>
  ),
  seatbelt: (
    <g fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="5.4" r="1.9" fill="currentColor" stroke="none" />
      <path d="M6.5 20l1-7.5 3.5-1.5" />
      <path d="M11 11l3.2 3.2L15.5 20" />
      <path d="M7.2 13.5h6.2" />
    </g>
  ),
  bulb_out: (
    <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8.5 13.6a5 5 0 1 1 7 0c-.8.7-1.3 1.5-1.5 2.6h-4c-.2-1.1-.7-1.9-1.5-2.6z" />
      <line x1="9.7" y1="18.7" x2="14.3" y2="18.7" />
      <line x1="10.6" y1="21" x2="13.4" y2="21" />
      <path d="M12 3.1V1.6 M4.7 6 3.5 4.8 M19.3 6 20.5 4.8" />
    </g>
  ),
};

type Tone = "signal" | "beam" | "warn" | "danger";

interface LampConfig {
  name: TelltaleName;
  tone: Tone;
  turn?: boolean;
}

// Left-to-right order across the telltale bar.
const LAMPS: LampConfig[] = [
  { name: "left", tone: "signal", turn: true },
  { name: "high_beam", tone: "beam" },
  { name: "check_engine", tone: "warn" },
  { name: "oil", tone: "warn" },
  { name: "battery", tone: "danger" },
  { name: "coolant", tone: "danger" },
  { name: "low_fuel", tone: "warn" },
  { name: "seatbelt", tone: "danger" },
  { name: "bulb_out", tone: "warn" },
  { name: "right", tone: "signal", turn: true },
];

export function TelltaleRow({ telltales }: { telltales: Telltales }) {
  // Hazard lights both indicators (via the backend), so this covers hazard too.
  const anyTurn = telltales.left || telltales.right;
  const blinkOn = useBlink(anyTurn);
  return (
    <div className="telltales">
      {LAMPS.map(({ name, tone, turn }) => {
        const lit = telltales[name];
        // Turn indicators flash on the shared clock (in unison); the rest are steady.
        const showLit = lit && (turn ? blinkOn : true);
        const cls = `lamp lamp--${tone}${turn ? " turn" : ""}${showLit ? " lit" : ""}`;
        return (
          <span key={name} className={cls} title={name} aria-label={`${name}${lit ? " on" : " off"}`}>
            <svg viewBox="0 0 24 24" width="26" height="26">
              {ICONS[name]}
            </svg>
          </span>
        );
      })}
    </div>
  );
}
