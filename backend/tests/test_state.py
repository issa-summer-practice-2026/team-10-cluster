"""Unit tests for the in-memory vehicle-state store (`app.state`)."""

import pytest

from app.cluster import SPEED_MAX_KMH, RawInput
from app.state import VehicleState


class TestApplyInput:
    def test_partial_update_keeps_other_fields(self):
        store = VehicleState()
        before = store.snapshot()
        store.apply_input({"speed_kmh": 100.0})
        snap = store.snapshot()
        assert snap.speed_kmh == 100.0
        assert snap.rpm == before.rpm

    def test_gear_is_normalized(self):
        store = VehicleState()
        store.apply_input({"gear": "d"})
        assert store.snapshot().gear == "D"

    def test_bool_field_applied(self):
        store = VehicleState()
        store.apply_input({"high_beam": True})
        assert store.snapshot().high_beam is True

    def test_multiple_fields_at_once(self):
        store = VehicleState()
        store.apply_input({"speed_kmh": 50.0, "rpm": 2500.0, "gear": "D"})
        snap = store.snapshot()
        assert (snap.speed_kmh, snap.rpm, snap.gear) == (50.0, 2500.0, "D")


class TestValidation:
    def test_unknown_field_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"turbo": 1})

    def test_non_dict_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input(["speed_kmh", 10])

    def test_numeric_wrong_type_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"speed_kmh": "fast"})

    def test_numeric_rejects_bool(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"speed_kmh": True})

    def test_bool_rejects_non_bool(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"high_beam": "yes"})

    def test_out_of_range_high_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"speed_kmh": SPEED_MAX_KMH + 1})

    def test_out_of_range_low_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"rpm": -1})

    def test_invalid_gear_raises(self):
        with pytest.raises(ValueError):
            VehicleState().apply_input({"gear": "X"})

    def test_failed_batch_does_not_corrupt_state(self):
        store = VehicleState()
        store.apply_input({"speed_kmh": 50.0})
        with pytest.raises(ValueError):
            # rpm is valid but gear is invalid -> whole batch must be rejected
            store.apply_input({"rpm": 3000.0, "gear": "X"})
        snap = store.snapshot()
        assert snap.speed_kmh == 50.0
        assert snap.rpm == RawInput().rpm


class TestSignals:
    def test_left_sets_left_only(self):
        store = VehicleState()
        store.set_signal("left")
        snap = store.snapshot()
        assert snap.left and not snap.right and not snap.hazard

    def test_right_sets_right_only(self):
        store = VehicleState()
        store.set_signal("right")
        snap = store.snapshot()
        assert snap.right and not snap.left and not snap.hazard

    def test_hazard_sets_hazard(self):
        store = VehicleState()
        store.set_signal("hazard")
        assert store.snapshot().hazard is True

    def test_off_clears_everything(self):
        store = VehicleState()
        store.set_signal("hazard")
        store.set_signal("left")
        store.set_signal("off")
        snap = store.snapshot()
        assert not snap.left and not snap.right and not snap.hazard

    def test_unknown_action_raises(self):
        with pytest.raises(ValueError):
            VehicleState().set_signal("diagonal")
