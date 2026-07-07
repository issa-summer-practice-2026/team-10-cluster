# Architecture

What the app is, how it's put together, its HTTP API, and what's deliberately
missing (that missing part is your week's work).

## What it is

A digital automotive **instrument cluster**:

- a dark, premium **cluster** view — two SVG gauges (tachometer with a redline
  zone + speedometer), a centre display with the digital speed and gear, fuel and
  temperature arc gauges, and a row of **telltale lamps**;
- a **simulator** (`/simulator`) that drives it — sliders, a gear selector,
  turn-signal and lamp toggles, and a **▶ Play drive** that replays a bundled
  drive cycle.

The app ships **fully working, styled, and green**. You don't build or restyle
it — you build the DevOps around it.

## Frontend + backend (one service)

- **Frontend** — **React + TypeScript**, built with **Vite**. It only *renders*:
  it polls `GET /api/state` and animates the gauges/lamps. It never computes
  vehicle logic.
- **Backend** — **Flask**. It owns the in-memory vehicle state and the
  **deterministic cluster logic** (pure Python, unit-tested with `pytest`),
  exposes a JSON API, and **serves the built frontend** — so the whole thing runs
  as **one service on one port**.

```
frontend/ (React + TS + Vite)  ──npm run build──▶  frontend/dist
                                                       │  served by
backend/  (Flask API + pure logic)  ◀──────────────────┘
```

The pure logic lives in `backend/app/cluster.py` (no Flask import, no I/O): given
a `RawInput` it returns a render-ready `ClusterState`. All thresholds and gauge
ranges are named constants at the top of that file, so a guided change is a
small, labelled edit.

## Project layout

```
backend/    Flask API + pure cluster logic (app/) + pytest tests (tests/)
frontend/   React + TS + Vite app (src/)
scripts/    dev.py cross-platform task runner (setup/dev/build/run/test/lint)
docs/       this documentation + backlog/ exercises
```

## HTTP API

| Method & path | Purpose |
|---|---|
| `GET /` , `GET /simulator` | Serve the single-page app |
| `GET /api/state` | Current derived cluster state (JSON) |
| `POST /api/input` | Set raw inputs (JSON body; any subset) |
| `POST /api/signal/<left\|right\|hazard\|off>` | Turn-signal / hazard (a toggle mode) |
| `GET /api/drive-cycle` | Bundled drive-cycle frames |
| `GET /health` | Liveness check (for the CI smoke test) → `{"status":"ok"}` |
| `GET /version` | Running release (`APP_VERSION` env → `VERSION` file → default) |

> The state endpoint is **`/api/state`** (not `/state`). `/health` and
> `/version` are top-level operational endpoints (no `/api` prefix).

### `GET /api/state` shape

```json
{
  "speed": { "value": 82.0, "unit": "km/h", "fraction": 0.315 },
  "rpm":   { "value": 3200, "fraction": 0.40, "redline": false },
  "fuel":  { "pct": 40.0, "fraction": 0.40 },
  "temp":  { "value_c": 104.0, "fraction": 0.711 },
  "gear":  "D",
  "odometer_km": 12000.0,
  "telltales": {
    "left": false, "right": false, "hazard": false, "high_beam": true,
    "check_engine": false, "battery": false, "coolant": false,
    "low_fuel": false, "bulb_out": false
  }
}
```

- `fraction` values are `0.0–1.0` for direct needle/arc mapping on the frontend.
- The contract is **additive**: exercises add fields/telltale keys, never remove
  them, so the frontend keeps working.
- **`POST /api/input`** accepts any subset of: `speed_kmh`, `rpm`, `fuel_pct`,
  `coolant_temp_c`, `gear`, and the boolean toggles `high_beam`, `check_engine`,
  `battery`, `bulb_out`. Out-of-range or wrong-type values are rejected with
  **HTTP 400**.

### Telltales & the "already-drawn but dark" lamps

The backend lights these telltales: `left, right, hazard, high_beam,
check_engine, battery, coolant, low_fuel, bulb_out`. Turn/hazard is a single
mutually-exclusive **toggle** mode; hazard lights both indicators, and they blink
in unison.

The frontend **also draws an `oil` and a `seat-belt` lamp** — but they ship
**dark**, because their backend keys are intentionally omitted. Wiring them up is
the first two [backlog](backlog/) exercises (backend-only; the lamp lights the
moment you merge).

## What's deliberately missing — your week

The app is done; these are **not**, on purpose (no solutions included):

- **CI pipeline** (`.github/workflows/`) — a **two-track** pipeline:
  - *backend*: install → `ruff` → `pytest` (+ coverage) → `compileall` → boot +
    `curl --fail /health`;
  - *frontend*: `npm ci` → `npm run lint` → `npm run typecheck` →
    `npm run test` → `npm run build`.
- **Branch protection** on `main` (require a passing PR + a review).
- **Multi-stage `Dockerfile`** — stage 1 (Node) builds the frontend; stage 2
  (`python:3.x-slim`) installs backend deps, copies `backend/` + the built
  `frontend/dist`, sets `APP_VERSION`, and runs the app. One image, one service.
- **Continuous Delivery + auto-release** — on merge to `main`, build/push the
  image to GHCR and cut a GitHub Release whose notes come from the merged PRs;
  the running container's `/version` matches the release.

See [workflow.md](workflow.md) for how changes land, and [backlog/](backlog/) for
the guided code changes you'll push through that pipeline.
