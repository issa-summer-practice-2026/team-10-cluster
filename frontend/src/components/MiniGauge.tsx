import type { ReactNode } from "react";

import { polarToCartesian } from "../lib/gauges";

// Compact 180-degree arc gauge (fuel / temperature), drawn on its own small
// coordinate system so it reads like a real sub-gauge rather than a raw bar.
const CX = 50;
const CY = 50;
const R = 40;
const START = -90;
const SWEEP = 180;

function miniArcPath(from: number, to: number): string {
  const a0 = START + from * SWEEP;
  const a1 = START + to * SWEEP;
  const s = polarToCartesian(CX, CY, R, a0);
  const e = polarToCartesian(CX, CY, R, a1);
  const large = a1 - a0 > 180 ? 1 : 0;
  return `M ${s.x} ${s.y} A ${R} ${R} 0 ${large} 1 ${e.x} ${e.y}`;
}

interface MiniGaugeProps {
  label: string;
  icon: ReactNode;
  fraction: number;
  /** Value text shown under the arc (e.g. "62%" or "94\u00b0"). */
  readout?: ReactNode;
  /** Colour the fill + icon as a warning when true. */
  warn?: boolean;
  /** Mirror the arc so a pair can bracket the cluster symmetrically. */
  flip?: boolean;
}

export function MiniGauge({
  label,
  icon,
  fraction,
  readout,
  warn = false,
  flip = false,
}: MiniGaugeProps) {
  const f = Math.min(1, Math.max(0, fraction));
  return (
    <div className={`mini${warn ? " warn" : ""}`}>
      <svg
        viewBox="0 0 100 60"
        className="mini-svg"
        style={flip ? { transform: "scaleX(-1)" } : undefined}
        aria-hidden="true"
      >
        <path className="mini-track" d={miniArcPath(0, 1)} />
        <path className="mini-fill" d={miniArcPath(0, Math.max(0.0001, f))} />
      </svg>
      <div className="mini-foot">
        <span className="mini-icon">{icon}</span>
        <span className="mini-label">{label}</span>
        {readout !== undefined && <span className="mini-readout">{readout}</span>}
      </div>
    </div>
  );
}
