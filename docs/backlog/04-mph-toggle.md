# 04 — km/h ↔ mph toggle

> One Issue, one PR. New here? Read [../workflow.md](../workflow.md) first.

**Goal:** display speed in mph when a toggle is on.

**Why:** unit conversion with a single, obvious seam (`speed_unit`) — the readout
already renders whatever unit the API returns.

## The change

**`backend/app/cluster.py`** — add a constant and a `RawInput` field:

```python
MPH_PER_KMH = 0.621371   # <-- add near the tunables

# in RawInput:
    odometer_km: float = 12000.0
    use_mph: bool = False   # <-- add this line
```

Replace the speed lines in `derive_state`:

```python
        speed_value=clamp(inp.speed_kmh, 0.0, SPEED_MAX_KMH) * (MPH_PER_KMH if inp.use_mph else 1.0),
        speed_unit="mph" if inp.use_mph else "km/h",
```

**`backend/app/state.py`** — add `"use_mph"` to `_BOOL_FIELDS` so it is settable.

**`backend/tests/test_cluster.py`** — add:

```python
    def test_speed_in_mph(self):
        state = derive_state(RawInput(speed_kmh=100, use_mph=True))
        assert state.speed_unit == "mph"
        assert state.speed_value == pytest.approx(62.1371)
```

*(Optional frontend)* add a "mph" toggle to the simulator that
`POST`s `{ "use_mph": true }`; the readout already shows `speed.unit`.

## Issue

*Issues → New issue.* Title: `km/h ↔ mph speed toggle`

~~~md
**What:** show speed in mph when a `use_mph` toggle is on (km/h otherwise).
**Why:** a clean unit-conversion seam through `speed_unit` — the readout already
renders whatever unit the API returns.

**Acceptance**
- [ ] `use_mph` is settable via `POST /api/input`
- [ ] `speed.unit` becomes `"mph"` and `speed.value` is converted when on
- [ ] a test asserts both the unit and the converted value; CI green
~~~

## Pull request

Branch `feat/mph-toggle`. Title: `feat: km/h ↔ mph speed toggle`

~~~md
Adds a `use_mph` input; when set, `derive_state` converts the speed value and
sets `speed_unit` to `"mph"`.

- `backend/app/cluster.py`: `MPH_PER_KMH`, `RawInput.use_mph`, speed lines in
  `derive_state`
- `backend/app/state.py`: `"use_mph"` added to `_BOOL_FIELDS`
- `backend/tests/test_cluster.py`: `test_speed_in_mph`

Closes #<n>
~~~

**Done when:** merged and green; toggling in the simulator flips the readout unit
and value.

*Goes red if:* you use `inp.use_mph` before adding it to `RawInput` — the tests
error out.
