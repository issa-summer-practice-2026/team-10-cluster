// TypeScript mirror of the backend's GET /api/state contract.
// Keep this in sync with `ClusterState.to_dict()` in backend/app/cluster.py.

export interface Telltales {
  left: boolean;
  right: boolean;
  hazard: boolean;
  high_beam: boolean;
  check_engine: boolean;
  battery: boolean;
  oil?: boolean; // lamp ships in the UI but backend omits it — students add it (docs/backlog/01-oil-telltale)
  coolant: boolean;
  low_fuel: boolean;
  seatbelt?: boolean; // lamp ships in the UI but backend omits it — students add it (docs/backlog/02-seatbelt-telltale)
  bulb_out: boolean;
}

export type TelltaleName = keyof Telltales;

export interface ClusterState {
  speed: { value: number; unit: string; fraction: number };
  rpm: { value: number; fraction: number; redline: boolean };
  fuel: { pct: number; fraction: number };
  temp: { value_c: number; fraction: number };
  gear: string;
  odometer_km: number;
  telltales: Telltales;
}

export type SignalAction = "left" | "right" | "hazard" | "off";

export interface DriveFrame {
  t: number;
  inputs: Record<string, unknown>;
}
