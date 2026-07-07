import { useEffect, useState } from "react";

import aumovioLogo from "./assets/aumovio-logo.png";
import { getVersion } from "./api";
import { Cluster } from "./components/Cluster";
import { Simulator } from "./components/Simulator";
import { useClusterState } from "./hooks/useClusterState";
import type { ClusterState } from "./types";

// Idle defaults shown until the first /api/state poll returns (mirrors the
// backend's default RawInput: parked, engine idling, tank ~2/3).
const INITIAL_STATE: ClusterState = {
  speed: { value: 0, unit: "km/h", fraction: 0 },
  rpm: { value: 800, fraction: 800 / 8000, redline: false },
  fuel: { pct: 65, fraction: 0.65 },
  temp: { value_c: 90, fraction: (90 - 40) / (130 - 40) },
  gear: "P",
  odometer_km: 12000,
  telltales: {
    left: false,
    right: false,
    hazard: false,
    high_beam: false,
    check_engine: false,
    battery: false,
    coolant: false,
    low_fuel: false,
    bulb_out: false,
  },
};

function useVersion(): string {
  const [version, setVersion] = useState("…");
  useEffect(() => {
    let active = true;
    getVersion()
      .then((v) => {
        if (active) setVersion(v);
      })
      .catch(() => {
        if (active) setVersion("unknown");
      });
    return () => {
      active = false;
    };
  }, []);
  return version;
}

function usePath(): [string, (to: string) => void] {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const navigate = (to: string) => {
    if (to !== window.location.pathname) {
      window.history.pushState(null, "", to);
      setPath(to);
    }
  };
  return [path, navigate];
}

export function App() {
  const version = useVersion();
  const live = useClusterState();
  const state = live ?? INITIAL_STATE;
  const [path, navigate] = usePath();
  const onSimulator = path === "/simulator";

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <img className="brand-logo" src={aumovioLogo} alt="Aumovio" />
          <span className="brand-divider" />
          <span className="brand-tag">
            <b>Instrument Cluster</b>
            <span>ISSA Summer Practice</span>
          </span>
        </div>
        <nav className="app-nav">
          <button
            type="button"
            className={onSimulator ? "" : "active"}
            onClick={() => navigate("/")}
          >
            Cluster
          </button>
          <button
            type="button"
            className={onSimulator ? "active" : ""}
            onClick={() => navigate("/simulator")}
          >
            Simulator
          </button>
        </nav>
        <span className="version">v{version}</span>
      </header>
      <main className="app-main">
        <Cluster state={state} />
        {onSimulator && <Simulator telltales={state.telltales} />}
      </main>
    </div>
  );
}
