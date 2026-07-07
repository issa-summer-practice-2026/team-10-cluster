[![CI Pipeline](https://github.com/issa-summer-practice-2026/team-10-cluster/actions/workflows/CI.yml/badge.svg)](https://github.com/issa-summer-practice-2026/team-10-cluster/actions/workflows/CI.yml)

# instrument-cluster

A digital automotive **instrument cluster** — the starter app for the ISSA
Summer Practice DevOps week. It ships **fully working and green**. Your job for
the week is to build the **DevOps around it** (CI, PR/review flow, containers,
delivery, versioned releases), not to build or restyle the app.

## Start here — create your team repo

**Do this once per pair, before anything else.** You work in your *own copy* of
this template inside the `issa-summer-practice-2026` organization — you never
push to this shared template itself.

1. **One teammate creates the repo from this template.** On this repo's page,
   click **Use this template ▸ Create a new repository**, then set:
   - **Owner:** `issa-summer-practice-2026`
   - **Repository name:** `team-XX-cluster` (your team number, e.g.
     `team-01-cluster`)
   - **Visibility: Public** — required; this is what keeps Actions, GHCR, and
     Releases free.
   - Click **Create repository**.

   *Can't choose the org as the owner? Ask a mentor to add you to the org with
   repo-creation rights (or to create the repo for you).*

2. **Add your teammate as a collaborator.** In the new repo go to
   **Settings ▸ Collaborators ▸ Add people** and add your partner with
   **Write** access. Both of you need write to push branches, open PRs, and
   review each other's work.

3. **Both teammates clone it and set your identity:**
   ```bash
   git clone https://github.com/issa-summer-practice-2026/team-XX-cluster.git
   cd team-XX-cluster
   git config user.name  "Your Name"
   git config user.email "you@example.com"   # the email on your GitHub account
   ```
   Using your GitHub email is what makes your commits and reviews show up under
   **Insights ▸ Contributors**.

4. **Confirm it runs green** (details in [Quick start](#quick-start-recommended)
   below):
   ```bash
   python scripts/dev.py setup
   python scripts/dev.py test
   python scripts/dev.py run      # then open http://localhost:8000
   ```

5. **Make your first commit.** Add both names to the [Team](#team) section
   below, commit, and push — that's everyone's first push done.

> Leave `main` unprotected for now — you'll add branch protection on
> **Tuesday**, once your CI pipeline exists.

<!-- STATUS BADGES — add your CI + release badges here once the pipeline exists:
[![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](../../actions)
[![Release](https://img.shields.io/github/v/release/<owner>/<repo>)](../../releases)
-->

## What it is

- A dark, premium **cluster**: two SVG gauges (tachometer with redline +
  speedometer), a digital speed readout, gear indicator, fuel/temperature
  gauges, and a row of telltale lamps.
- A **simulator** panel to drive it: sliders, gear/toggle controls, turn
  signals, and a **▶ Play drive** that replays a bundled drive cycle.

## Architecture

- **Frontend** — React + TypeScript, built with Vite. It only *renders*; it
  polls `GET /api/state` and animates the gauges.
- **Backend** — Flask. It owns the vehicle state and the **deterministic
  cluster logic** (pure Python, unit-tested with pytest), exposes a JSON API,
  and **serves the built frontend** — so the whole thing runs as one service.

```
frontend/ (React + TS + Vite)  ──build──▶  frontend/dist
                                              │  served by
backend/  (Flask API + logic)  ◀─────────────┘
```

## Prerequisites

- **Python 3.11+**
- **Node.js LTS** (bundles npm)

## Quick start (recommended)

Cross-platform helper scripts live in `scripts/dev.py` (with a `Makefile`
wrapper on Unix):

```bash
python scripts/dev.py setup    # create venv, install backend + frontend deps
python scripts/dev.py dev      # API on :8000 + Vite dev server on :5173 (hot reload)
```

Then open the Vite dev server (usually http://localhost:5173). API calls are
proxied to Flask automatically.

To run it the way it will ship (one service, one port):

```bash
python scripts/dev.py run      # builds the frontend, then serves everything from Flask on :8000
```

On Unix you can use `make setup`, `make dev`, `make run`, `make test`,
`make lint` instead.

## Running things manually (without the scripts)

Backend:

```bash
cd backend
python -m venv ../.venv && ../.venv/bin/pip install -r dev-requirements.txt
../.venv/bin/python -m app          # serves on http://127.0.0.1:8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev                          # dev server on http://localhost:5173
# or: npm run build                  # emits frontend/dist for the backend to serve
```

## Testing & linting

```bash
python scripts/dev.py test    # backend: pytest    | frontend: vitest
python scripts/dev.py lint    # backend: ruff      | frontend: eslint + tsc
```

Backend coverage (used by CI): `cd backend && ../.venv/bin/pytest --cov=app`.

## HTTP API

| Method & path | Purpose |
|---|---|
| `GET /` , `GET /simulator` | Serve the single-page app |
| `GET /api/state` | Current derived cluster state (JSON) |
| `POST /api/input` | Set raw inputs (JSON body; any subset) |
| `POST /api/signal/<left\|right\|hazard\|off>` | Turn-signal / hazard state |
| `GET /api/drive-cycle` | Bundled drive-cycle frames |
| `GET /health` | Liveness check (for the CI smoke test) |
| `GET /version` | Running release (`APP_VERSION` env → `VERSION` file → default) |

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

`POST /api/input` accepts any subset of: `speed_kmh`, `rpm`, `fuel_pct`,
`coolant_temp_c`, `gear`, and the boolean toggles `high_beam`, `check_engine`,
`battery`, `bulb_out`. Out-of-range or wrong-type values are rejected with HTTP
400. (`oil` and `seatbelt` are student add-targets — see `docs/backlog/`.)

## Project layout

```
backend/   Flask API + pure cluster logic (app/) + pytest tests (tests/)
frontend/  React + TS + Vite app (src/)
scripts/   dev.py cross-platform task runner
docs/      getting-started · architecture · workflow  +  backlog/ (exercises)
```

## Team

Both teammates: add your name and GitHub handle here (and set
`git config user.email` to your GitHub email so your commits count).

- Vornicu David — @VornicuDavid
- Melinte Alexandru — @melinte-alexandru

## Your DevOps tasks (this is the week) — TODO

The app is done. **These are not** — they're what you build. No solutions are
included on purpose.

- [ ] **CI pipeline** (`.github/workflows/ci.yml`) — two tracks:
  - **backend**: install deps → `ruff check` → `pytest` (upload coverage) →
    `python -m compileall` → boot the app and `curl --fail /health`.
  - **frontend**: `npm ci` → `npm run lint` → `npm run typecheck` →
    `npm run test` → `npm run build`.
- [ ] **Branch protection** on `main` — require a PR, require the CI check to
  pass, require 1 review; tick "Do not allow bypassing the above settings".
- [ ] **Multi-stage `Dockerfile`** — stage 1 (Node) builds the frontend; stage 2
  (`python:3.x-slim`) installs backend deps, copies `backend/` + the built
  `frontend/dist`, sets `APP_VERSION`, and runs the app (remember `HOST=0.0.0.0`
  inside the container). One image, one service.
- [ ] **Continuous Delivery + auto-release** — on merge to `main`, build and push
  the image to GHCR and cut a GitHub Release whose notes are generated from the
  merged PRs. Confirm the running container's `/version` matches the release.

See the Monday course + lab briefs for the day-by-day plan.

## Guided code changes

When you need a small code change to push through the pipeline, use the
ready-made exercises in [`docs/backlog/`](docs/backlog/). Each is a small,
self-contained diff **plus a test**, with ready-to-paste Issue + PR text — the
point is the issue → PR → review → green CI → merge → release workflow, not the
code. See [`docs/workflow.md`](docs/workflow.md) for that flow, and
[`docs/`](docs/) for setup and architecture.

## Notes

- **Security**: this is an unauthenticated local demo / public template — no
  auth, no secrets, no real data. It is not production-secure by design.
- No database: vehicle state is in memory and resets on restart.
