"""Unit tests for the pure cluster logic (`app.cluster`)."""

import pytest

from app.cluster import (
    LOW_FUEL_PCT,
    OVERHEAT_TEMP_C,
    REDLINE_RPM,
    SPEED_MAX_KMH,
    TELLTALE_KEYS,
    RawInput,
    clamp,
    compute_telltales,
    derive_state,
    gauge_fraction,
    gear_display,
)


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-1, 0, 10) == 0
    assert clamp(11, 0, 10) == 10


class TestGaugeFraction:
    def test_zero_at_min(self):
        assert gauge_fraction(0, 0, 100) == 0.0

    def test_one_at_max(self):
        assert gauge_fraction(100, 0, 100) == 1.0

    def test_half(self):
        assert gauge_fraction(50, 0, 100) == 0.5

    def test_clamps_below_range(self):
        assert gauge_fraction(-20, 0, 100) == 0.0

    def test_clamps_above_range(self):
        assert gauge_fraction(150, 0, 100) == 1.0

    def test_offset_range(self):
        assert gauge_fraction(85, 40, 130) == pytest.approx(0.5)

    def test_degenerate_range_is_zero(self):
        assert gauge_fraction(5, 10, 10) == 0.0


class TestGearDisplay:
    @pytest.mark.parametrize("gear", ["P", "R", "N", "D", "1", "3", "6"])
    def test_valid_gears_pass_through(self, gear):
        assert gear_display(gear) == gear

    def test_normalizes_case(self):
        assert gear_display("d") == "D"

    def test_strips_whitespace(self):
        assert gear_display("  N ") == "N"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            gear_display("X")


class TestRedline:
    def test_just_below(self):
        assert derive_state(RawInput(rpm=REDLINE_RPM - 1)).redline is False

    def test_at_threshold(self):
        assert derive_state(RawInput(rpm=REDLINE_RPM)).redline is True

    def test_above(self):
        assert derive_state(RawInput(rpm=REDLINE_RPM + 500)).redline is True


class TestTelltales:
    def test_low_fuel_at_threshold(self):
        assert compute_telltales(RawInput(fuel_pct=LOW_FUEL_PCT))["low_fuel"] is True

    def test_low_fuel_above_threshold(self):
        assert compute_telltales(RawInput(fuel_pct=LOW_FUEL_PCT + 1))["low_fuel"] is False

    def test_overheat_at_threshold(self):
        assert compute_telltales(RawInput(coolant_temp_c=OVERHEAT_TEMP_C))["coolant"] is True

    def test_overheat_below_threshold(self):
        assert compute_telltales(RawInput(coolant_temp_c=OVERHEAT_TEMP_C - 1))["coolant"] is False

    def test_hazard_forces_both_indicators(self):
        t = compute_telltales(RawInput(hazard=True))
        assert t["left"] and t["right"] and t["hazard"]

    def test_left_only(self):
        t = compute_telltales(RawInput(left=True))
        assert t["left"] and not t["right"] and not t["hazard"]

    def test_passthrough_toggles(self):
        t = compute_telltales(RawInput(high_beam=True, check_engine=True, battery=True))
        assert all(t[k] for k in ("high_beam", "check_engine", "battery"))

    def test_bulb_out_lights_telltale(self):
        assert compute_telltales(RawInput(bulb_out=True))["bulb_out"] is True
        assert compute_telltales(RawInput())["bulb_out"] is False

    def test_default_is_all_off(self):
        t = compute_telltales(RawInput())
        assert not any(t.values())

    def test_oil_lit_from_toggle(self):
        assert compute_telltales(RawInput(oil=True))["oil"] is True
        
    def test_seatbelt_lit_from_toggle(self):
        assert compute_telltales(RawInput(seatbelt=True))["seatbelt"] is True

class TestDeriveState:
    def test_to_dict_top_level_shape(self):
        d = derive_state(RawInput()).to_dict()
        assert set(d) == {"speed", "rpm", "fuel", "temp", "gear", "odometer_km", "telltales"}

    def test_to_dict_nested_shape(self):
        d = derive_state(RawInput()).to_dict()
        assert set(d["speed"]) == {"value", "unit", "fraction"}
        assert set(d["rpm"]) == {"value", "fraction", "redline"}
        assert set(d["fuel"]) == {"pct", "fraction"}
        assert set(d["temp"]) == {"value_c", "fraction"}

    def test_to_dict_telltale_keys(self):
        d = derive_state(RawInput()).to_dict()
        assert set(d["telltales"]) == set(TELLTALE_KEYS)

    def test_speed_unit_default_is_kmh(self):
        assert derive_state(RawInput(speed_kmh=50)).speed_unit == "km/h"

    def test_fractions_clamped_to_one(self):
        s = derive_state(RawInput(speed_kmh=99999, rpm=99999))
        assert s.speed_fraction == 1.0
        assert s.rpm_fraction == 1.0

    def test_values_clamped_to_max(self):
        assert derive_state(RawInput(speed_kmh=99999)).speed_value == SPEED_MAX_KMH

    def test_odometer_passes_through(self):
        assert derive_state(RawInput(odometer_km=42.5)).odometer_km == 42.5
