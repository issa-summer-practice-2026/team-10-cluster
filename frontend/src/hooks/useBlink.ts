import { useEffect, useState } from "react";

/**
 * A single shared on/off blink clock. Every lamp that reads the returned value
 * flashes on exactly the same phase, so multiple turn indicators (e.g. both
 * sides during hazard) blink in unison instead of drifting apart.
 *
 * Returns `true` (steady on) while `active` is false; while active it flips
 * every `periodMs`, always starting lit.
 */
export function useBlink(active: boolean, periodMs = 440): boolean {
  const [on, setOn] = useState(true);

  useEffect(() => {
    if (!active) {
      setOn(true);
      return;
    }
    setOn(true); // begin the cycle lit
    const id = window.setInterval(() => setOn((v) => !v), periodMs);
    return () => window.clearInterval(id);
  }, [active, periodMs]);

  return on;
}
