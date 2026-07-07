"""Bundled drive-cycle loader.

A drive cycle is a time-ordered list of frames; each frame has a timestamp ``t``
(seconds from start) and an ``inputs`` object (a subset of raw vehicle inputs to
apply at that time). :func:`load_drive_cycle` parses and validates the bundled
JSON; the browser fetches it (via ``GET /api/drive-cycle``) and replays it by
posting each frame's inputs, so playback needs no server-side timers.

Validation here is *structural* (frame shape + known input keys); the value
ranges are enforced by :meth:`app.state.VehicleState.apply_input` when a frame is
actually applied.
"""

import json
from dataclasses import dataclass
from pathlib import Path

# Input keys a frame may set (mirrors the settable RawInput fields).
_ALLOWED_INPUT_KEYS = frozenset(
    {
        "speed_kmh",
        "rpm",
        "fuel_pct",
        "coolant_temp_c",
        "gear",
        "left",
        "right",
        "hazard",
        "high_beam",
        "check_engine",
        "battery",
        "bulb_out",
        "odometer_km",
    }
)

DRIVE_CYCLE_PATH = Path(__file__).resolve().parent / "data" / "drive_cycle.json"


@dataclass(frozen=True)
class Frame:
    """One drive-cycle step: apply ``inputs`` at ``t`` seconds from start."""

    t: float
    inputs: dict


def validate_frame(obj: object) -> Frame:
    """Validate one raw frame object; raise ``ValueError`` if malformed."""
    if not isinstance(obj, dict):
        raise ValueError("frame must be an object")
    if "t" not in obj:
        raise ValueError("frame is missing 't'")
    t = obj["t"]
    if isinstance(t, bool) or not isinstance(t, (int, float)):
        raise ValueError("frame 't' must be a number")
    if t < 0:
        raise ValueError("frame 't' must be >= 0")

    inputs = obj.get("inputs", {})
    if not isinstance(inputs, dict):
        raise ValueError("frame 'inputs' must be an object")
    unknown = set(inputs) - _ALLOWED_INPUT_KEYS
    if unknown:
        raise ValueError(f"frame has unknown input keys: {sorted(unknown)}")

    return Frame(t=float(t), inputs=dict(inputs))


def load_drive_cycle(path: str | Path = DRIVE_CYCLE_PATH) -> list[Frame]:
    """Load, validate, and time-sort the drive-cycle file at ``path``."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("drive cycle must be a JSON array of frames")
    frames = [validate_frame(item) for item in raw]
    frames.sort(key=lambda frame: frame.t)
    return frames
