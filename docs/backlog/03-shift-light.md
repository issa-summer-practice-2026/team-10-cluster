# 03 — Shift-light at redline

> One Issue, one PR. New here? Read [../workflow.md](../workflow.md) first.

**Goal:** light an upshift ("shift now") lamp as revs approach the redline.

**Why:** a threshold-driven telltale, like low-fuel and overheat — practises
adding a tunable constant + a telltale key together.

## The change

**`backend/app/cluster.py`** — add a constant near the other tunables:

```python
REDLINE_RPM = 6500.0
SHIFT_LIGHT_RPM = 6000.0   # <-- add: shift lamp lights at/over this
```

Add `"shift_light"` to `TELLTALE_KEYS`, then add the rule in
`compute_telltales`:

```python
        "coolant": inp.coolant_temp_c >= OVERHEAT_TEMP_C,
        "shift_light": inp.rpm >= SHIFT_LIGHT_RPM,   # <-- add this line
        "low_fuel": inp.fuel_pct <= LOW_FUEL_PCT,
```

**`backend/tests/test_cluster.py`** — add:

```python
    def test_shift_light_at_threshold(self):
        assert compute_telltales(RawInput(rpm=6000))["shift_light"] is True

    def test_shift_light_below_threshold(self):
        assert compute_telltales(RawInput(rpm=5999))["shift_light"] is False
```

*(Optional frontend)* add a `shift_light` lamp to
`frontend/src/components/TelltaleRow.tsx` (`LAMPS` + an icon in `ICONS`) and
`shift_light: boolean` to `frontend/src/types.ts` if you want it on screen.

## Issue

*Issues → New issue.* Title: `Shift-light telltale at redline`

~~~md
**What:** light a "shift now" telltale at/above `SHIFT_LIGHT_RPM` (6000 rpm).
**Why:** a threshold-driven telltale, like low-fuel / overheat — practises adding
a tunable constant + a telltale key together.

**Acceptance**
- [ ] `shift_light` lights at/above 6000 rpm and is off below
- [ ] `shift_light` is in `TELLTALE_KEYS`
- [ ] tests cover both sides of the threshold; CI green
~~~

## Pull request

Branch `feat/shift-light`. Title: `feat: shift-light telltale at redline`

~~~md
Adds a `shift_light` telltale that lights at/above `SHIFT_LIGHT_RPM` (6000 rpm).

- `backend/app/cluster.py`: `SHIFT_LIGHT_RPM` constant, `"shift_light"` in
  `TELLTALE_KEYS`, rule in `compute_telltales`
- `backend/tests/test_cluster.py`: at/below threshold tests

Closes #<n>
~~~

**Done when:** merged and green; revving past 6000 in the simulator lights the
lamp (add a `shift_light` lamp to `TelltaleRow` if you want it visible).

*Goes red if:* you add the rule but not the `TELLTALE_KEYS` entry (or vice
versa) — the telltale-keys test fails.
