"""Pure, deterministic cluster logic: raw vehicle inputs -> derived cluster state.

This module is the tested core of the app. It is intentionally **pure**:

* no Flask import,
* no file, network, or other I/O,
* no module-level mutable state.

Given a :class:`RawInput` it returns a :class:`ClusterState` (same inputs ->
same outputs). The web layer stores raw inputs elsewhere and calls
:func:`derive_state`; the frontend renders the result.

All tunables live in the "constants" block below so a guided change is a small,
clearly-labelled edit (see ``docs/backlog/``).
"""

from dataclasses import dataclass

# --- Tunables (guided-change packets edit these) --------------------------
SPEED_MAX_KMH = 260.0  # full-scale of the speedometer
RPM_MAX = 8000.0  # full-scale of the tachometer
REDLINE_RPM = 6500.0  # tach redline starts here; `redline` flag trips at/above
TEMP_MIN_C = 40.0  # coolant gauge low end (cold)
TEMP_MAX_C = 130.0  # coolant gauge high end (hot)
FUEL_MAX_PCT = 100.0  # fuel is expressed 0..100 %
LOW_FUEL_PCT = 15.0  # low-fuel telltale lights at/under this
OVERHEAT_TEMP_C = 115.0  # coolant/overheat telltale lights at/over this
VALID_GEARS = ("P", "R", "N", "D", "1", "2", "3", "4", "5", "6")

# Stable telltale keys exposed in /api/state (packets add new ones, never remove).
TELLTALE_KEYS = (
    "left",
    "right",
    "hazard",
    "high_beam",
    "check_engine",
    "battery",
    "coolant",
    "low_fuel",
    "seatbelt",
    "bulb_out",
)


@dataclass(frozen=True)
class RawInput:
    """Primitive vehicle signals a driver / simulator provides.

    Defaults describe a presentable idling car (engine on, in Park, tank ~2/3).
    """

    speed_kmh: float = 0.0
    rpm: float = 800.0
    fuel_pct: float = 65.0
    coolant_temp_c: float = 90.0
    gear: str = "P"
    # signal / toggle inputs
    left: bool = False
    right: bool = False
    hazard: bool = False
    high_beam: bool = False
    check_engine: bool = False
    battery: bool = False
    seatbelt: bool = False 
    bulb_out: bool = False  # lights the bulb-failure telltale; also the hyper-flash packet's seam
    odometer_km: float = 12000.0


@dataclass(frozen=True)
class ClusterState:
    """Derived, render-ready cluster state. ``fraction`` values are 0.0-1.0."""

    speed_value: float
    speed_unit: str
    speed_fraction: float
    rpm: float
    rpm_fraction: float
    redline: bool
    fuel_pct: float
    fuel_fraction: float
    temp_c: float
    temp_fraction: float
    gear: str
    odometer_km: float
    telltales: dict[str, bool]

    def to_dict(self) -> dict:
        """Serialize to the stable, additive ``/api/state`` JSON shape."""
        return {
            "speed": {
                "value": self.speed_value,
                "unit": self.speed_unit,
                "fraction": self.speed_fraction,
            },
            "rpm": {
                "value": self.rpm,
                "fraction": self.rpm_fraction,
                "redline": self.redline,
            },
            "fuel": {"pct": self.fuel_pct, "fraction": self.fuel_fraction},
            "temp": {"value_c": self.temp_c, "fraction": self.temp_fraction},
            "gear": self.gear,
            "odometer_km": self.odometer_km,
            "telltales": dict(self.telltales),
        }


def clamp(value: float, lo: float, hi: float) -> float:
    """Constrain ``value`` to the inclusive range ``[lo, hi]``."""
    return max(lo, min(hi, value))


def gauge_fraction(value: float, lo: float, hi: float) -> float:
    """Map ``value`` in ``[lo, hi]`` to a clamped 0.0-1.0 gauge fraction."""
    if hi == lo:
        return 0.0
    return clamp((value - lo) / (hi - lo), 0.0, 1.0)


def gear_display(gear: object) -> str:
    """Normalize and validate a gear token; raise ``ValueError`` if unknown."""
    token = str(gear).strip().upper()
    if token not in VALID_GEARS:
        raise ValueError(f"invalid gear: {gear!r}")
    return token


def compute_telltales(inp: RawInput) -> dict[str, bool]:
    """Decide which telltale lamps are lit from the raw inputs and thresholds."""
    hazard = inp.hazard
    return {
        "left": inp.left or hazard,
        "right": inp.right or hazard,
        "hazard": hazard,
        "high_beam": inp.high_beam,
        "check_engine": inp.check_engine,
        "battery": inp.battery,
        "coolant": inp.coolant_temp_c >= OVERHEAT_TEMP_C,
        "low_fuel": inp.fuel_pct <= LOW_FUEL_PCT,
        "seatbelt": inp.seatbelt,
        "bulb_out": inp.bulb_out,
    }


def derive_state(inp: RawInput) -> ClusterState:
    """Compose the full derived cluster state from raw inputs (pure)."""
    return ClusterState(
        speed_value=clamp(inp.speed_kmh, 0.0, SPEED_MAX_KMH),
        speed_unit="km/h",
        speed_fraction=gauge_fraction(inp.speed_kmh, 0.0, SPEED_MAX_KMH),
        rpm=clamp(inp.rpm, 0.0, RPM_MAX),
        rpm_fraction=gauge_fraction(inp.rpm, 0.0, RPM_MAX),
        redline=clamp(inp.rpm, 0.0, RPM_MAX) >= REDLINE_RPM,
        fuel_pct=clamp(inp.fuel_pct, 0.0, FUEL_MAX_PCT),
        fuel_fraction=gauge_fraction(inp.fuel_pct, 0.0, FUEL_MAX_PCT),
        temp_c=clamp(inp.coolant_temp_c, TEMP_MIN_C, TEMP_MAX_C),
        temp_fraction=gauge_fraction(inp.coolant_temp_c, TEMP_MIN_C, TEMP_MAX_C),
        gear=gear_display(inp.gear),
        odometer_km=inp.odometer_km,
        telltales=compute_telltales(inp),
    )
