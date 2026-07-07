import { useMemo, type ReactNode } from "react";

import { arcPath, fractionToAngle, polarToCartesian } from "../lib/gauges";

const CX = 100;
const CY = 100;
const R_ARC = 86;
const R_TICK_OUT = 76;
const R_TICK_IN_MINOR = 70;
const R_TICK_IN_MAJOR = 63;
const R_LABEL = 52;

interface Numerals {
  max: number;
  step: number;
  /** Divide the numeral before display (e.g. 1000 to show rpm in thousands). */
  divide?: number;
}

interface GaugeProps {
  /** 0..1 position of the needle / value arc (already smoothed by the caller). */
  fraction: number;
  /** Unique id (one per gauge instance) for the arc gradient. */
  gradientId: string;
  ticks?: number;
  majorEvery?: number;
  /** Numeral scale placed at each step's true fraction (value / max). */
  numerals?: Numerals;
  /** If set, a redline zone is drawn from this fraction to 1.0. */
  redlineFraction?: number;
  accent?: string;
  /** Small readout placed low on the face, clear of the needle hub. */
  subReadout?: ReactNode;
  caption?: string;
}

export function Gauge({
  fraction,
  gradientId,
  ticks = 40,
  majorEvery = 5,
  numerals,
  redlineFraction,
  accent = "var(--accent)",
  subReadout,
  caption,
}: GaugeProps) {
  const numMax = numerals?.max;
  const numStep = numerals?.step;
  const numDivide = numerals?.divide ?? 1;

  // Ticks and numerals depend only on the dial's scale, never on the live
  // value, so memoize them: at 60fps only the needle + value arc recompute.
  const tickLines = useMemo(() => {
    const lines = [];
    for (let i = 0; i <= ticks; i += 1) {
      const f = i / ticks;
      const isMajor = i % majorEvery === 0;
      const past = redlineFraction !== undefined && f >= redlineFraction;
      const angle = fractionToAngle(f);
      const outer = polarToCartesian(CX, CY, R_TICK_OUT, angle);
      const inner = polarToCartesian(CX, CY, isMajor ? R_TICK_IN_MAJOR : R_TICK_IN_MINOR, angle);
      lines.push(
        <line
          key={i}
          x1={outer.x}
          y1={outer.y}
          x2={inner.x}
          y2={inner.y}
          className={`tick${isMajor ? " major" : ""}${past ? " redline" : ""}`}
        />,
      );
    }
    return lines;
  }, [ticks, majorEvery, redlineFraction]);

  const numeralEls = useMemo(() => {
    if (numMax === undefined || numStep === undefined) return [];
    const els = [];
    const count = Math.floor(numMax / numStep);
    for (let i = 0; i <= count; i += 1) {
      const value = i * numStep;
      const p = polarToCartesian(CX, CY, R_LABEL, fractionToAngle(value / numMax));
      const past = redlineFraction !== undefined && value / numMax >= redlineFraction;
      els.push(
        <text
          key={value}
          x={p.x}
          y={p.y}
          className={`gauge-num${past ? " redline" : ""}`}
          textAnchor="middle"
        >
          {Math.round(value / numDivide)}
        </text>,
      );
    }
    return els;
  }, [numMax, numStep, numDivide, redlineFraction]);

  const angle = fractionToAngle(fraction);

  return (
    <div className="gauge">
      <svg viewBox="0 0 200 200" className="gauge-svg" role="img" aria-label={caption}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="1" x2="1" y2="0">
            <stop offset="0%" stopColor={accent} stopOpacity="0.12" />
            <stop offset="100%" stopColor={accent} />
          </linearGradient>
          <radialGradient id={`${gradientId}-face`} cx="50%" cy="42%" r="65%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.05)" />
            <stop offset="70%" stopColor="rgba(255,255,255,0.012)" />
            <stop offset="100%" stopColor="rgba(0,0,0,0.28)" />
          </radialGradient>
        </defs>

        {/* Physical dial: subtle face + machined bezel rings for depth. */}
        <circle className="dial-face" cx={CX} cy={CY} r="92" fill={`url(#${gradientId}-face)`} />
        <circle className="dial-bezel" cx={CX} cy={CY} r="92" />
        <circle className="dial-bezel-inner" cx={CX} cy={CY} r="43" />

        <path className="gauge-track" d={arcPath(CX, CY, R_ARC, 0, 1)} />
        <path
          className="gauge-value"
          d={arcPath(CX, CY, R_ARC, 0, Math.max(0.0001, fraction))}
          stroke={`url(#${gradientId})`}
        />
        {redlineFraction !== undefined && (
          <path className="gauge-redline" d={arcPath(CX, CY, R_ARC, redlineFraction, 1)} />
        )}

        <g className="gauge-ticks">{tickLines}</g>
        <g className="gauge-nums">{numeralEls}</g>

        <g className="needle" style={{ transform: `rotate(${angle}deg)` }}>
          <polygon className="needle-tip" points={`${CX},26 ${CX - 1.6},48 ${CX + 1.6},48`} />
          <polygon
            className="needle-body"
            points={`${CX - 1.6},48 ${CX + 1.6},48 ${CX + 2.7},101 ${CX - 2.7},101`}
          />
          <polygon
            className="needle-tail"
            points={`${CX - 2.4},100 ${CX + 2.4},100 ${CX + 1.4},121 ${CX - 1.4},121`}
          />
        </g>
        <circle className="needle-hub" cx={CX} cy={CY} r="8.5" />
        <circle className="needle-hub-dot" cx={CX} cy={CY} r="3.4" />
      </svg>

      {subReadout && <div className="gauge-sub">{subReadout}</div>}
      {caption && <div className="gauge-caption">{caption}</div>}
    </div>
  );
}
