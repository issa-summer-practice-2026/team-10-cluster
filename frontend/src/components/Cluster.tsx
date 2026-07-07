import { useEffect, useState } from "react";

import { useSmoothed } from "../hooks/useSmoothed";
import type { ClusterState } from "../types";
import "../styles/cluster.css";
import { DigitalReadout } from "./DigitalReadout";
import { Gauge } from "./Gauge";
import { MediaCard } from "./MediaCard";
import { MiniGauge } from "./MiniGauge";
import { NavStrip } from "./NavStrip";
import { TelltaleRow } from "./TelltaleRow";

// Redline zone start on the tach dial. Mirrors REDLINE_RPM / RPM_MAX
// (6500 / 8000) from the backend cluster logic.
const TACH_REDLINE_FRACTION = 0.8125;

const FUEL_ICON = (
  <svg viewBox="0 0 24 24" width="15" height="15">
    <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="4" width="9" height="16" rx="1.5" />
      <line x1="4" y1="10" x2="13" y2="10" />
      <path d="M13 9h3a2 2 0 0 1 2 2v5a1.6 1.6 0 0 0 3 0v-7l-2.4-2.4" />
    </g>
  </svg>
);

const TEMP_ICON = (
  <svg viewBox="0 0 24 24" width="15" height="15">
    <g fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 4v9" />
      <circle cx="12" cy="16" r="3.2" />
      <path d="M6 20q2-2 4 0t4 0" />
    </g>
  </svg>
);

/**
 * On mount, sweep the needles (0 -> full -> release to live) like a real
 * cluster's power-on self-test, then hand control back to the live values.
 * The sweep target is fed through the same smoothing as live data, so it
 * glides rather than snaps.
 */
function useStartupSweep(): number | null {
  const [sweep, setSweep] = useState<number | null>(0);
  useEffect(() => {
    const up = window.setTimeout(() => setSweep(1), 120);
    const release = window.setTimeout(() => setSweep(null), 1500);
    return () => {
      window.clearTimeout(up);
      window.clearTimeout(release);
    };
  }, []);
  return sweep;
}

export function Cluster({ state }: { state: ClusterState }) {
  const sweep = useStartupSweep();

  // Everything the eye tracks is eased toward its target so needles glide.
  const rpmFraction = useSmoothed(sweep ?? state.rpm.fraction, 230);
  const speedFraction = useSmoothed(sweep ?? state.speed.fraction, 260);
  const speedValue = useSmoothed(state.speed.value, 260);
  const rpmValue = useSmoothed(state.rpm.value, 230);
  const fuelFraction = useSmoothed(state.fuel.fraction, 500);
  const tempFraction = useSmoothed(state.temp.fraction, 500);

  return (
    <div className="cluster">
      <TelltaleRow telltales={state.telltales} />

      <div className="cluster-main">
        <div className="dial dial--left">
          <Gauge
            gradientId="tach-grad"
            fraction={rpmFraction}
            numerals={{ max: 8000, step: 1000, divide: 1000 }}
            redlineFraction={TACH_REDLINE_FRACTION}
            accent="var(--warn)"
            caption={"rpm \u00d71000"}
            subReadout={
              <span className="tach-readout">
                <b>{Math.round(rpmValue).toLocaleString()}</b>
                <i>rpm</i>
              </span>
            }
          />
          <MiniGauge
            label="FUEL"
            icon={FUEL_ICON}
            fraction={fuelFraction}
            readout={`${Math.round(state.fuel.pct)}%`}
            warn={state.telltales.low_fuel}
          />
        </div>

        <div className="mid">
          <div className="mid-speed">
            <DigitalReadout speed={speedValue} unit={state.speed.unit} gear={state.gear} />
          </div>
          <MediaCard />
          <NavStrip />
        </div>

        <div className="dial dial--right">
          <Gauge
            gradientId="speed-grad"
            fraction={speedFraction}
            numerals={{ max: 260, step: 40 }}
            caption={state.speed.unit}
          />
          <MiniGauge
            label="TEMP"
            icon={TEMP_ICON}
            fraction={tempFraction}
            readout={`${Math.round(state.temp.value_c)}\u00b0`}
            warn={state.telltales.coolant}
            flip
          />
        </div>
      </div>

      <div className="cluster-foot">
        <span>ODO {Math.round(state.odometer_km).toLocaleString()} km</span>
        <span className="foot-dot" />
        <span>Range 540 km</span>
        <span className="foot-dot" />
        <span>Outside 18&deg;C</span>
      </div>

      <div className="cluster-brand">
        <b>Aumovio</b> &middot; ISSA Summer Practice
      </div>
    </div>
  );
}
