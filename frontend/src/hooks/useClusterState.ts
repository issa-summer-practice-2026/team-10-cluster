import { useEffect, useState } from "react";

import { getState } from "../api";
import type { ClusterState } from "../types";

/**
 * Poll GET /api/state on an interval and return the latest cluster state
 * (null until the first successful fetch). A transient fetch error keeps the
 * previous state rather than clearing the gauges.
 */
export function useClusterState(intervalMs = 120): ClusterState | null {
  const [state, setState] = useState<ClusterState | null>(null);

  useEffect(() => {
    let active = true;
    let inFlight = false;

    async function tick() {
      if (inFlight) return;
      inFlight = true;
      try {
        const next = await getState();
        if (active) setState(next);
      } catch {
        // Transient error: keep the last known state.
      } finally {
        inFlight = false;
      }
    }

    void tick();
    const id = window.setInterval(() => void tick(), intervalMs);
    return () => {
      active = false;
      window.clearInterval(id);
    };
  }, [intervalMs]);

  return state;
}
