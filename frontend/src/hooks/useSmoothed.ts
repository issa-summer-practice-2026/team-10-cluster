import { useEffect, useRef, useState } from "react";

/**
 * Ease a numeric value toward `target` with frame-rate-independent
 * exponential smoothing, the way a real gauge needle is damped: it never
 * snaps, it glides. `tauMs` is the time constant (larger = heavier / slower
 * to settle). A `snapEpsilon` avoids animating forever on tiny residuals.
 *
 * The animation runs on requestAnimationFrame, so a jump (e.g. 0 -> 125 km/h
 * from a drive-cycle step or a poll) sweeps smoothly instead of teleporting.
 */
export function useSmoothed(target: number, tauMs = 260, snapEpsilon = 0.0005): number {
  const [value, setValue] = useState(target);
  const valueRef = useRef(target);
  const targetRef = useRef(target);
  targetRef.current = target;

  useEffect(() => {
    let raf = 0;
    let last = performance.now();

    const step = (now: number) => {
      const dt = Math.min(now - last, 100); // clamp long frame gaps (tab was hidden)
      last = now;

      const current = valueRef.current;
      const goal = targetRef.current;
      const diff = goal - current;

      if (Math.abs(diff) < snapEpsilon) {
        if (current !== goal) {
          valueRef.current = goal;
          setValue(goal);
        }
      } else {
        const alpha = 1 - Math.exp(-dt / tauMs);
        const next = current + diff * alpha;
        valueRef.current = next;
        setValue(next);
      }

      raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [tauMs, snapEpsilon]);

  return value;
}
