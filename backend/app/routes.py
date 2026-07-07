"""HTTP layer: the JSON API plus serving of the built single-page frontend.

Routes are intentionally thin — parse the request, call the store / pure logic,
serialize. The data API lives under ``/api``; operational endpoints ``/health``
and ``/version`` sit at the root (handy for probes and the CI smoke test); any
other GET falls through to the SPA (so client-side routes like ``/simulator``
work), or to a friendly "no build yet" page when the frontend has not been built.
"""

from pathlib import Path

from flask import abort, jsonify, request, send_from_directory

from app.cluster import derive_state
from app.drivecycle import load_drive_cycle
from app.version import get_version

_NO_BUILD_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>instrument-cluster</title>
<style>
  body{{background:#05070a;color:#e8eef6;font-family:system-ui,sans-serif;
       display:grid;place-items:center;min-height:100vh;margin:0}}
  .card{{max-width:40rem;padding:2rem;line-height:1.6}}
  code{{background:#0b1018;padding:.15rem .4rem;border-radius:.3rem;color:#18a9e7}}
  h1{{color:#18a9e7}}
</style></head><body><div class="card">
  <h1>instrument-cluster</h1>
  <p>The backend is running, but the frontend has not been built yet.</p>
  <p><b>Dev mode:</b> run <code>python scripts/dev.py dev</code> and open the Vite
     dev server (usually <code>http://localhost:5173</code>).</p>
  <p><b>Single-service mode:</b> run <code>python scripts/dev.py run</code>
     (builds the frontend, then serves it here).</p>
  <p>API is live: <code>/api/state</code>, <code>/health</code>,
     <code>/version</code>.</p>
</div></body></html>
"""


def _serve_spa(dist: Path):
    index = dist / "index.html"
    if index.is_file():
        return send_from_directory(dist, "index.html")
    return _NO_BUILD_PAGE, 200, {"Content-Type": "text/html; charset=utf-8"}


def register_routes(app, store, frontend_dist) -> None:
    """Register all routes on ``app``, wired to the given state ``store``."""
    dist = Path(frontend_dist)

    # ---- JSON API -------------------------------------------------------
    @app.get("/api/state")
    def api_state():
        return jsonify(derive_state(store.snapshot()).to_dict())

    @app.post("/api/input")
    def api_input():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            abort(400, description="expected a JSON object body")
        try:
            store.apply_input(payload)
        except ValueError as exc:
            abort(400, description=str(exc))
        return "", 204

    @app.post("/api/signal/<action>")
    def api_signal(action: str):
        try:
            store.set_signal(action)
        except ValueError as exc:
            abort(400, description=str(exc))
        return "", 204

    @app.get("/api/drive-cycle")
    def api_drive_cycle():
        frames = load_drive_cycle()
        return jsonify([{"t": frame.t, "inputs": frame.inputs} for frame in frames])

    # ---- operational ----------------------------------------------------
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/version")
    def version():
        return jsonify({"version": get_version()})

    # ---- built SPA + client-side routing --------------------------------
    @app.get("/")
    def spa_root():
        return _serve_spa(dist)

    @app.get("/<path:path>")
    def spa_catch_all(path: str):
        # Unknown API routes must 404 as JSON, not fall through to the SPA.
        if path.startswith("api/"):
            abort(404)
        candidate = (dist / path).resolve()
        # Serve a real build asset if it exists and stays inside dist.
        if dist.is_dir() and candidate.is_file() and dist.resolve() in candidate.parents:
            return send_from_directory(dist, path)
        return _serve_spa(dist)
