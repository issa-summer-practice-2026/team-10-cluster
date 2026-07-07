"""Endpoint tests via the Flask test client (`app.routes`)."""

from app.cluster import TELLTALE_KEYS


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_version_reflects_env(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.get_json() == {"version": "9.9.9"}


def test_state_shape(client):
    resp = client.get("/api/state")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data) == {"speed", "rpm", "fuel", "temp", "gear", "odometer_km", "telltales"}
    assert set(data["telltales"]) == set(TELLTALE_KEYS)


def test_input_updates_state(client):
    assert client.post("/api/input", json={"speed_kmh": 123.0}).status_code == 204
    data = client.get("/api/state").get_json()
    assert data["speed"]["value"] == 123.0


def test_input_partial_leaves_other_fields(client):
    before = client.get("/api/state").get_json()
    client.post("/api/input", json={"rpm": 3000.0})
    after = client.get("/api/state").get_json()
    assert after["rpm"]["value"] == 3000.0
    assert after["gear"] == before["gear"]


def test_input_bad_value_400(client):
    resp = client.post("/api/input", json={"speed_kmh": "fast"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_input_unknown_field_400(client):
    assert client.post("/api/input", json={"turbo": 1}).status_code == 400


def test_input_out_of_range_400(client):
    assert client.post("/api/input", json={"fuel_pct": 999}).status_code == 400


def test_input_non_json_400(client):
    resp = client.post("/api/input", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_input_bad_value_does_not_change_state(client):
    client.post("/api/input", json={"speed_kmh": 60.0})
    client.post("/api/input", json={"speed_kmh": "oops"})
    assert client.get("/api/state").get_json()["speed"]["value"] == 60.0


def test_signal_hazard_lights_both(client):
    assert client.post("/api/signal/hazard").status_code == 204
    telltales = client.get("/api/state").get_json()["telltales"]
    assert telltales["hazard"] and telltales["left"] and telltales["right"]


def test_signal_off_clears(client):
    client.post("/api/signal/left")
    client.post("/api/signal/off")
    telltales = client.get("/api/state").get_json()["telltales"]
    assert not telltales["left"] and not telltales["hazard"]


def test_signal_bad_action_400(client):
    assert client.post("/api/signal/sideways").status_code == 400


def test_drive_cycle_served(client):
    resp = client.get("/api/drive-cycle")
    assert resp.status_code == 200
    frames = resp.get_json()
    assert isinstance(frames, list) and frames
    assert "t" in frames[0] and "inputs" in frames[0]


def test_unknown_api_route_404_json(client):
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


def test_spa_root_serves_without_build(client):
    # No frontend build during tests -> friendly HTML page, not a 500.
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"instrument-cluster" in resp.data


def test_spa_client_route_falls_through(client):
    # A client-side route (no matching file) should also return the shell/page.
    resp = client.get("/simulator")
    assert resp.status_code == 200


# --- signal toggle semantics (turn / hazard as one exclusive mode) ---------


def _telltales(client):
    return client.get("/api/state").get_json()["telltales"]


def test_signal_left_toggles_on_then_off(client):
    client.post("/api/signal/left")
    assert _telltales(client)["left"] is True
    client.post("/api/signal/left")  # pressing left again turns it off
    after = _telltales(client)
    assert after["left"] is False and after["hazard"] is False


def test_signal_right_toggles_on_then_off(client):
    client.post("/api/signal/right")
    assert _telltales(client)["right"] is True
    client.post("/api/signal/right")
    assert _telltales(client)["right"] is False


def test_signal_left_then_right_is_mutually_exclusive(client):
    client.post("/api/signal/left")
    client.post("/api/signal/right")
    after = _telltales(client)
    assert after["right"] is True and after["left"] is False


def test_signal_hazard_toggles_off(client):
    client.post("/api/signal/hazard")
    assert _telltales(client)["hazard"] is True
    client.post("/api/signal/hazard")
    assert _telltales(client)["hazard"] is False


def test_signal_hazard_while_left_on_keeps_only_hazard(client):
    client.post("/api/signal/left")
    client.post("/api/signal/hazard")
    on = _telltales(client)
    # hazard on, and both indicators lit *via hazard* (so they blink in phase)
    assert on["hazard"] is True and on["left"] is True and on["right"] is True
    # toggling hazard off clears everything -> confirms the raw left was cleared
    client.post("/api/signal/hazard")
    off = _telltales(client)
    assert off["hazard"] is False and off["left"] is False and off["right"] is False


def test_signal_left_after_hazard_switches_to_left(client):
    client.post("/api/signal/hazard")
    client.post("/api/signal/left")
    after = _telltales(client)
    assert after["left"] is True and after["hazard"] is False and after["right"] is False
