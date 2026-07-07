# 05 — Hyper-flash on a bulb-out

> One Issue, one PR. New here? Read [../workflow.md](../workflow.md) first.

**Goal:** when a bulb is out and an indicator is on, flash faster (real cars do
this to warn you).

**Why:** derive a new signal from existing inputs.

> **Note:** `bulb_out` already lights a **bulb-failure telltale** in the shipped
> app. This exercise adds the *separate* **hyper-flash** behaviour — the
> indicators blinking **faster** while a bulb is out — as a new derived signal.

## The change

**`backend/app/cluster.py`** — add a `ClusterState` field:

```python
    redline: bool
    hyperflash: bool   # <-- add this line
```

Add it to `to_dict` (top level):

```python
            "gear": self.gear,
            "hyperflash": self.hyperflash,   # <-- add this line
            "odometer_km": self.odometer_km,
```

Set it in `derive_state`:

```python
        redline=clamp(inp.rpm, 0.0, RPM_MAX) >= REDLINE_RPM,
        hyperflash=inp.bulb_out and (inp.left or inp.right or inp.hazard),   # <-- add
```

**`backend/tests/test_cluster.py`** — update the top-level shape test to include
the new key, then add a behavior test:

```python
    def test_to_dict_top_level_shape(self):
        d = derive_state(RawInput()).to_dict()
        assert set(d) == {
            "speed", "rpm", "fuel", "temp", "gear",
            "hyperflash", "odometer_km", "telltales",
        }

    def test_hyperflash_when_bulb_out_and_indicating(self):
        assert derive_state(RawInput(bulb_out=True, left=True)).hyperflash is True
        assert derive_state(RawInput(left=True)).hyperflash is False
```

*(Optional frontend)* add `hyperflash: boolean` to `frontend/src/types.ts`, pass
`state.hyperflash` into `TelltaleRow`, and shorten the shared `useBlink` period
(e.g. `useBlink(anyTurn, hyperflash ? 200 : 440)`) so the indicators flash faster.

## Issue

*Issues → New issue.* Title: `Hyper-flash indicators on bulb-out`

~~~md
**What:** expose a `hyperflash` flag that is true when a bulb is out **and** an
indicator (left/right/hazard) is on.
**Why:** derive a new signal from existing inputs — mirrors the real-car warning
where a failed bulb makes the turn signal flash roughly twice as fast.

**Acceptance**
- [ ] `hyperflash` is a top-level field in `/api/state`
- [ ] it is true only when `bulb_out` and an indicator are both on
- [ ] the top-level shape test is updated and a behaviour test is added; CI green
~~~

## Pull request

Branch `feat/hyperflash`. Title: `feat: hyper-flash indicators on bulb-out`

~~~md
Derives a `hyperflash` flag (`bulb_out` and an active indicator) and adds it to
the `/api/state` top level.

- `backend/app/cluster.py`: `ClusterState.hyperflash`, set in `derive_state`,
  emitted in `to_dict`
- `backend/tests/test_cluster.py`: updated shape test + `test_hyperflash_...`

Closes #<n>
~~~

**Done when:** merged and green; enabling "Bulb out" + a turn signal in the
simulator sets `hyperflash` in `/api/state`.

*Goes red if:* you add the `ClusterState` field but forget to set it in
`derive_state` (constructor error) or forget the shape-test update.
