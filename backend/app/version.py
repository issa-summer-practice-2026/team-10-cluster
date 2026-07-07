"""Running-release resolution.

Precedence (so a released container can stamp the version with no code change):

1. the ``APP_VERSION`` environment variable, if set;
2. the bundled ``VERSION`` file next to the backend;
3. a hard-coded default.

``get_version`` therefore always returns something.
"""

import os
from pathlib import Path

_DEFAULT_VERSION = "0.0.0-dev"
_VERSION_FILE = Path(__file__).resolve().parent.parent / "VERSION"


def _read_version_file() -> str | None:
    try:
        text = _VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def get_version() -> str:
    """Return the running release identifier (never empty)."""
    env = os.environ.get("APP_VERSION")
    if env and env.strip():
        return env.strip()
    return _read_version_file() or _DEFAULT_VERSION
