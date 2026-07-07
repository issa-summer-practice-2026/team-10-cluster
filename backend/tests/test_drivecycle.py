"""Unit tests for the drive-cycle loader (`app.drivecycle`)."""

import pytest

from app.drivecycle import Frame, load_drive_cycle, validate_frame
from app.state import VehicleState


class TestBundledCycle:
    def test_loads_frames(self):
        frames = load_drive_cycle()
        assert len(frames) > 0
        assert all(isinstance(f, Frame) for f in frames)

    def test_is_time_sorted(self):
        times = [f.t for f in load_drive_cycle()]
        assert times == sorted(times)

    def test_starts_at_zero(self):
        assert load_drive_cycle()[0].t == 0.0

    def test_is_playable_through_the_store(self):
        # Every bundled frame must be valid input for the real validator,
        # i.e. the authored data never goes out of range or uses bad keys.
        store = VehicleState()
        for frame in load_drive_cycle():
            store.apply_input(frame.inputs)


class TestValidateFrame:
    def test_good_frame(self):
        frame = validate_frame({"t": 1.5, "inputs": {"speed_kmh": 50}})
        assert frame.t == 1.5
        assert frame.inputs["speed_kmh"] == 50

    def test_missing_t(self):
        with pytest.raises(ValueError):
            validate_frame({"inputs": {}})

    def test_bad_t_type(self):
        with pytest.raises(ValueError):
            validate_frame({"t": "soon"})

    def test_negative_t(self):
        with pytest.raises(ValueError):
            validate_frame({"t": -1})

    def test_unknown_input_key(self):
        with pytest.raises(ValueError):
            validate_frame({"t": 0, "inputs": {"nitro": 1}})

    def test_inputs_not_object(self):
        with pytest.raises(ValueError):
            validate_frame({"t": 0, "inputs": [1, 2]})

    def test_frame_not_object(self):
        with pytest.raises(ValueError):
            validate_frame([1, 2, 3])


class TestLoadErrors:
    def test_rejects_non_array(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text('{"t": 0}', encoding="utf-8")
        with pytest.raises(ValueError):
            load_drive_cycle(path)

    def test_rejects_malformed_frame(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text('[{"t": 0}, {"inputs": {}}]', encoding="utf-8")
        with pytest.raises(ValueError):
            load_drive_cycle(path)
