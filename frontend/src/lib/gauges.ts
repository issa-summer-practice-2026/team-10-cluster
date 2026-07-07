// Pure gauge geometry helpers. Kept framework-free so they are easy to unit
// test (see gauges.test.ts) and to reason about. All angles are in degrees,
// measured clockwise from the 12 o'clock (straight-up) position, matching an
// SVG `rotate()` of a shape that points up.

// A gauge needle sweeps from START_DEG clockwise through SWEEP_DEG total,
// leaving a gap at the bottom.
export const START_DEG = -120;
export const SWEEP_DEG = 240;

export interface Point {
  x: number;
  y: number;
}

/** Map a 0..1 gauge fraction to a needle angle in degrees (clamped). */
export function fractionToAngle(
  fraction: number,
  startDeg: number = START_DEG,
  sweepDeg: number = SWEEP_DEG,
): number {
  const clamped = Math.min(1, Math.max(0, fraction));
  return startDeg + clamped * sweepDeg;
}

/** Point on a circle for an angle measured clockwise from straight up. */
export function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number): Point {
  const a = (angleDeg * Math.PI) / 180;
  return { x: cx + r * Math.sin(a), y: cy - r * Math.cos(a) };
}

/**
 * SVG arc path following the gauge sweep between two 0..1 fractions.
 * Drawn clockwise (sweep-flag 1), matching the needle direction.
 */
export function arcPath(
  cx: number,
  cy: number,
  r: number,
  fromFraction: number,
  toFraction: number,
): string {
  const a0 = fractionToAngle(fromFraction);
  const a1 = fractionToAngle(toFraction);
  const start = polarToCartesian(cx, cy, r, a0);
  const end = polarToCartesian(cx, cy, r, a1);
  const largeArc = a1 - a0 > 180 ? 1 : 0;
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 1 ${end.x} ${end.y}`;
}
