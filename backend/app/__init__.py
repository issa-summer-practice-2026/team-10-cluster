"""instrument-cluster backend package.

The Flask application factory ``create_app`` is defined here. The pure,
deterministic cluster logic lives in :mod:`app.cluster` and imports nothing from
Flask, so it can be unit-tested in isolation.

Flask is imported lazily (inside ``create_app``) so that importing the pure
logic (``from app.cluster import ...``) never requires the web framework.
"""

import os
from pathlib import Path

__all__ = ["create_app"]

# Default location of the built frontend (``frontend/dist`` at the repo root),
# relative to this file: backend/app/__init__.py -> repo root.
_DEFAULT_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def create_app(frontend_dist: str | os.PathLike | None = None):
    """Create and configure the Flask app (JSON API + built-SPA serving).

    ``frontend_dist`` (or the ``FRONTEND_DIST`` env var) points at the built
    frontend directory. When it is absent (e.g. before ``npm run build`` or when
    developing against the Vite dev server), the root route shows a friendly
    "no build yet" page instead of erroring.
    """
    from flask import Flask, jsonify

    from app.routes import register_routes
    from app.state import VehicleState

    app = Flask(__name__, static_folder=None)
    store = VehicleState()
    app.config["VEHICLE_STATE"] = store

    dist = Path(frontend_dist or os.environ.get("FRONTEND_DIST") or _DEFAULT_FRONTEND_DIST)
    app.config["FRONTEND_DIST"] = dist

    register_routes(app, store, dist)

    @app.errorhandler(400)
    def _bad_request(err):
        return jsonify({"error": getattr(err, "description", "bad request")}), 400

    @app.errorhandler(404)
    def _not_found(err):
        return jsonify({"error": "not found"}), 404

    return app
