# Getting started

How to set up, build, run, test, and lint the `instrument-cluster` app on your
own laptop. Nothing here is graded — it's the working baseline everything else
builds on.

## Prerequisites

- **Python 3.11+** (`python --version`)
- **Node.js LTS** (`node --version`, bundles `npm`)
- **Git**, and a code editor

That's it — no database, no cloud account, no Docker (until Thursday).

> **Two toolchains, on purpose.** This is a **React + TypeScript (Vite)**
> frontend *and* a **Flask (Python)** backend. You need **both** Python and
> Node installed. That two-toolchain shape is what later makes your Dockerfile a
> realistic **multi-stage** build and your CI a **two-track** pipeline.

## Quick start (recommended)

Cross-platform helper scripts live in `scripts/dev.py` (Python is already a
prerequisite, so they run identically on Windows/macOS/Linux). On Unix there's a
`Makefile` wrapper (`make setup`, `make dev`, ...).

```bash
python scripts/dev.py setup    # create the venv, install backend + frontend deps
python scripts/dev.py dev      # Flask API on :8000 + Vite dev server on :5173 (hot reload)
```

Open the Vite dev server (usually http://localhost:5173). API calls are proxied
to Flask automatically, so there's no CORS to configure.

To run it the way it will ship — **one service, one port** (this is what your
container will do):

```bash
python scripts/dev.py run      # builds the frontend, then serves everything from Flask on :8000
```

Then open http://127.0.0.1:8000.

## Running it manually (without the scripts)

Useful to understand what the scripts do — and what your Dockerfile will do.

**Backend** (Flask API + serves the built frontend):

```bash
cd backend
python -m venv ../.venv
../.venv/bin/pip install -r dev-requirements.txt
../.venv/bin/python -m app          # http://127.0.0.1:8000
```

**Frontend** (React + TS + Vite):

```bash
cd frontend
npm install
npm run dev                          # dev server on http://localhost:5173 (proxies to Flask)
# or, to ship it:
npm run build                        # emits frontend/dist, which Flask serves in "run" mode
```

> In dev mode you run **both** processes (that's what `dev.py dev` does). In
> ship/prod mode you **build the frontend once** and Flask serves `frontend/dist`
> as a single service — no Node needed at runtime.

## Test & lint

```bash
python scripts/dev.py test    # backend: pytest        | frontend: vitest
python scripts/dev.py lint    # backend: ruff          | frontend: eslint + tsc
```

Or per track:

```bash
# backend
cd backend && ../.venv/bin/ruff check . && ../.venv/bin/pytest
../.venv/bin/pytest --cov=app         # coverage (your CI uploads this)

# frontend
cd frontend && npm run lint && npm run typecheck && npm run test && npm run build
```

Everything ships **green** on a clean checkout. If something's red before you've
changed anything, fix your environment (versions above) — not the app.

## Verifying it works

- The **cluster** renders in the browser: two gauges, telltale lamps, a centre
  display, and a simulator at `/simulator`.
- `GET /health` returns `{"status":"ok"}`.
- `GET /version` returns the running build.
- `GET /api/state` returns the live cluster JSON (see
  [architecture.md](architecture.md#http-api)).

Next: skim [architecture.md](architecture.md), then follow
[workflow.md](workflow.md) to ship your first [backlog](backlog/) item.
