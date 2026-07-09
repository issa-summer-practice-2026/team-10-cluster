import { useEffect, useRef, useState } from "react";

import { getDriveCycle, postInput, postSignal } from "../api";
import type { SignalAction, TelltaleName, Telltales } from "../types";
import "../styles/simulator.css";

const GEARS = ["P", "R", "N", "D", "1", "2", "3", "4", "5", "6"];

// Telltales that are set directly (the rest — low_fuel, coolant — are derived
// from the fuel / temperature sliders, so they have no dedicated button).
const LAMP_TOGGLES: { name: TelltaleName; label: string }[] = [
  { name: "high_beam", label: "High beam" },
  { name: "check_engine", label: "Check engine" },
  { name: "battery", label: "Battery" },
  { name: "bulb_out", label: "Bulb out" },
  // Guided-change warm-ups: the oil and seat-belt lamps already render in the
  // cluster, but their backend keys are removed. After you add the key in the
  // backend (see docs/backlog/ — 01-oil-telltale, 02-seatbelt-telltale),
  // uncomment the matching line to get a clickable toggle here too.
  { name: "oil", label: "Oil" },
  { name: "seatbelt", label: "Seat belt" },
];

function send(partial: Record<string, unknown>) {
  postInput(partial).catch(() => undefined);
}

function signal(action: SignalAction) {
  postSignal(action).catch(() => undefined);
}

interface SliderProps {
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
  unit?: string;
  onChange: (value: number) => void;
}

function Slider({ label, min, max, step, value, unit = "", onChange }: SliderProps) {
  return (
    <label className="sim-slider">
      <span className="sim-slider-head">
        <span>{label}</span>
        <b>
          {Math.round(value)}
          {unit}
        </b>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

export function Simulator({ telltales }: { telltales: Telltales }) {
  const [speed, setSpeed] = useState(0);
  const [rpm, setRpm] = useState(800);
  const [fuel, setFuel] = useState(65);
  const [temp, setTemp] = useState(90);
  const [gear, setGear] = useState("P");
  const [playing, setPlaying] = useState(false);
  const playTimer = useRef<number | null>(null);

  const bind = (setter: (v: number) => void, field: string) => (value: number) => {
    setter(value);
    send({ [field]: value });
  };

  // Derive the active turn/hazard mode from live telltales. Hazard lights both
  // indicators, so a plain left/right is "active" only when hazard is off.
  const hazardActive = telltales.hazard;
  const leftActive = telltales.left && !telltales.hazard;
  const rightActive = telltales.right && !telltales.hazard;

  function stopDrive() {
    if (playTimer.current !== null) {
      window.clearInterval(playTimer.current);
      playTimer.current = null;
    }
    setPlaying(false);
  }

  async function startDrive() {
    stopDrive();
    let frames;
    try {
      frames = await getDriveCycle();
    } catch {
      return;
    }
    if (frames.length === 0) return;

    setPlaying(true);
    const startedAt = performance.now();
    let index = 0;
    playTimer.current = window.setInterval(() => {
      const elapsed = (performance.now() - startedAt) / 1000;
      while (index < frames.length && frames[index].t <= elapsed) {
        send(frames[index].inputs);
        index += 1;
      }
      if (index >= frames.length) stopDrive();
    }, 100);
  }

  useEffect(() => () => stopDrive(), []);

  return (
    <section className="sim">
      <div className="sim-sliders">
        <Slider label="Speed" min={0} max={260} step={1} value={speed} unit=" km/h" onChange={bind(setSpeed, "speed_kmh")} />
        <Slider label="RPM" min={0} max={8000} step={50} value={rpm} onChange={bind(setRpm, "rpm")} />
        <Slider label="Fuel" min={0} max={100} step={1} value={fuel} unit=" %" onChange={bind(setFuel, "fuel_pct")} />
        <Slider label="Temp" min={40} max={130} step={1} value={temp} unit=" °C" onChange={bind(setTemp, "coolant_temp_c")} />
      </div>

      <div className="sim-row">
        <span className="sim-label">Gear</span>
        <div className="sim-gears">
          {GEARS.map((g) => (
            <button
              key={g}
              type="button"
              className={`sim-gear${gear === g ? " active" : ""}`}
              onClick={() => {
                setGear(g);
                send({ gear: g });
              }}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      <div className="sim-row">
        <span className="sim-label">Signals</span>
        <button
          type="button"
          className={`sim-btn${leftActive ? " active" : ""}`}
          aria-pressed={leftActive}
          onClick={() => signal("left")}
        >
          ◀ Left
        </button>
        <button
          type="button"
          className={`sim-btn sim-btn--hazard${hazardActive ? " active" : ""}`}
          aria-pressed={hazardActive}
          onClick={() => signal("hazard")}
        >
          Hazard
        </button>
        <button
          type="button"
          className={`sim-btn${rightActive ? " active" : ""}`}
          aria-pressed={rightActive}
          onClick={() => signal("right")}
        >
          Right ▶
        </button>
      </div>

      <div className="sim-row">
        <span className="sim-label">Lamps</span>
        {LAMP_TOGGLES.map(({ name, label }) => (
          <button
            key={name}
            type="button"
            className={`sim-btn${telltales[name] ? " active" : ""}`}
            aria-pressed={telltales[name]}
            onClick={() => send({ [name]: !telltales[name] })}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="sim-row">
        <button
          type="button"
          className={`sim-play${playing ? " playing" : ""}`}
          onClick={() => (playing ? stopDrive() : void startDrive())}
        >
          {playing ? "■ Stop" : "▶ Play drive"}
        </button>
      </div>
    </section>
  );
}
