"""Run the backend dev server: ``python -m app``.

Host/port come from the environment (``HOST`` / ``PORT``). The default host is
``127.0.0.1`` (safe for local development); a container image should set
``HOST=0.0.0.0`` so the service is reachable from outside the container.
"""

import os

from app import create_app


def main() -> None:
    app = create_app()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
