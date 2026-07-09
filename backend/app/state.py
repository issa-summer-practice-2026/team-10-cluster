"""In-memory vehicle-state store.

Holds the current :class:`~app.cluster.RawInput` behind a lock and applies
validated updates from the API. Validation is strict (wrong type, unknown field,
out-of-range value, or invalid gear all raise :class:`ValueError`, which the
route layer turns into HTTP 400) and **atomic**: a batch is fully validated
before any change is applied, so a bad field never corrupts existing state.
"""

from dataclasses import replace
from threading import Lock

from app.cluster import (
    FUEL_MAX_PCT,
    RPM_MAX,
    SPEED_MAX_KMH,
    TEMP_MAX_C,
    TEMP_MIN_C,
    RawInput,
    gear_display,
)

# field name -> (inclusive lo, inclusive hi) for numeric inputs
_NUMERIC_RANGES: dict[str, tuple[float, float]] = {
    "speed_kmh": (0.0, SPEED_MAX_KMH),
    "rpm": (0.0, RPM_MAX),
    "fuel_pct": (0.0, FUEL_MAX_PCT),
    "coolant_temp_c": (TEMP_MIN_C, TEMP_MAX_C),
    "odometer_km": (0.0, 10_000_000.0),
}

_BOOL_FIELDS: frozenset[str] = frozenset(
    {
        "left",
        "right",
        "hazard",
        "high_beam",
        "check_engine",
        "battery",
        "oil",
        "seatbelt",
        "bulb_out",
    }
)

_SIGNAL_ACTIONS: frozenset[str] = frozenset({"left", "right", "hazard", "off"})

# Turn signal + hazard form ONE mutually-exclusive mode, each mapping to the
# (left, right, hazard) raw booleans. Hazard lights both indicators (see
# compute_telltales) and never coexists with a single turn signal, so the two
# indicators are only ever lit together *via hazard* — which is what keeps them
# blinking in unison instead of drifting out of phase.
_MODE_FLAGS: dict[str, tuple[bool, bool, bool]] = {
    "left": (True, False, False),
    "right": (False, True, False),
    "hazard": (False, False, True),
    "off": (False, False, False),
}


def _signal_mode(raw: RawInput) -> str:
    """Current turn/hazard mode derived from the raw booleans."""
    if raw.hazard:
        return "hazard"
    if raw.left:
        return "left"
    if raw.right:
        return "right"
    return "off"


def _validate_numeric(field: str, value: object, lo: float, hi: float) -> float:
    # bool is a subclass of int, so reject it explicitly for numeric fields.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number")
    number = float(value)
    if not (lo <= number <= hi):
        raise ValueError(f"{field} out of range [{lo}, {hi}]: {number}")
    return number


class VehicleState:
    """Thread-safe holder of the current raw vehicle inputs."""

    def __init__(self, initial: RawInput | None = None) -> None:
        self._raw = initial or RawInput()
        self._lock = Lock()

    def apply_input(self, fields: dict) -> None:
        """Validate and apply a partial set of raw inputs.

        Raises ``ValueError`` on an unknown field, wrong type, out-of-range
        value, or invalid gear. Unspecified fields are left unchanged.
        """
        if not isinstance(fields, dict):
            raise ValueError("input must be a JSON object")

        updates: dict[str, object] = {}
        for key, value in fields.items():
            if key in _NUMERIC_RANGES:
                lo, hi = _NUMERIC_RANGES[key]
                updates[key] = _validate_numeric(key, value, lo, hi)
            elif key in _BOOL_FIELDS:
                if not isinstance(value, bool):
                    raise ValueError(f"{key} must be a boolean")
                updates[key] = value
            elif key == "gear":
                updates[key] = gear_display(value)
            else:
                raise ValueError(f"unknown input field: {key!r}")

        with self._lock:
            self._raw = replace(self._raw, **updates)

    def set_signal(self, action: str) -> None:
        """Toggle turn-signal / hazard state like a real stalk + hazard switch.

        The three indicators form one mutually-exclusive mode. Pressing the
        currently-active mode turns it off; pressing another switches to it:

        * ``left`` when off -> left on; ``left`` again -> off.
        * ``left`` then ``right`` -> right on, left off (mutually exclusive).
        * ``hazard`` while ``left`` is on -> left off, hazard on (both indicators
          lit via hazard, in phase); ``hazard`` again -> off.
        * ``off`` always clears everything.
        """
        if action not in _SIGNAL_ACTIONS:
            raise ValueError(f"unknown signal action: {action!r}")

        with self._lock:
            if action == "off":
                target = "off"
            elif action == _signal_mode(self._raw):
                target = "off"  # pressing the active mode toggles it off
            else:
                target = action
            left, right, hazard = _MODE_FLAGS[target]
            self._raw = replace(self._raw, left=left, right=right, hazard=hazard)

    def snapshot(self) -> RawInput:
        """Return the current raw inputs (a consistent, immutable snapshot)."""
        with self._lock:
            return self._raw
