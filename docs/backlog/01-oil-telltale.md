# 01 — Oil-pressure telltale *(warm-up)*

> One Issue, one PR. New here? Read [../workflow.md](../workflow.md) first.

**Goal:** light the **oil-pressure** lamp from a new toggle.

**Why:** the simplest possible end-to-end change — and the lamp is **already
drawn** in the cluster (it just sits dark because the backend doesn't send it
yet), so this is **backend-only**: the moment it merges, the lamp works.

## The change

**`backend/app/cluster.py`** — add a field to `RawInput`:

```python
    battery: bool = False
    oil: bool = False        # <-- add this line
    bulb_out: bool = False
```

Add `"oil"` to `TELLTALE_KEYS`:

```python
    "battery",
    "oil",        # <-- add this line
    "coolant",
```

In `compute_telltales`, add the rule:

```python
        "battery": inp.battery,
        "oil": inp.oil,        # <-- add this line
        "coolant": inp.coolant_temp_c >= OVERHEAT_TEMP_C,
```

**`backend/app/state.py`** — make the toggle settable by adding `"oil"` to
`_BOOL_FIELDS`:

```python
        "battery",
        "oil",        # <-- add this line
        "bulb_out",
    }
```

**`backend/tests/test_cluster.py`** — add a test:

```python
    def test_oil_lit_from_toggle(self):
        assert compute_telltales(RawInput(oil=True))["oil"] is True
```

*(No frontend needed — the `oil` lamp already ships in `TelltaleRow`. Optional:
**uncomment** the `{ name: "oil", label: "Oil" }` line in `LAMP_TOGGLES`
(`frontend/src/components/Simulator.tsx`) for a clickable toggle in the simulator.)*

## Issue

*Issues → New issue.* Title: `Oil-pressure telltale`

~~~md
**What:** add an oil-pressure telltale driven by a new `oil` input.
**Why:** the shipped cluster already draws the oil lamp but the backend never
lights it — wire it up. Simplest end-to-end change to warm up the
issue → PR → CI → merge flow.

**Acceptance**
- [ ] `oil` is settable via `POST /api/input`
- [ ] `oil` is in `TELLTALE_KEYS` and lights when the input is true
- [ ] a unit test covers it; backend `pytest` + `ruff` are green in CI
~~~

## Pull request

Branch `feat/oil-telltale`. Title: `feat: oil-pressure telltale`

~~~md
Lights the (already-drawn) oil lamp from a new `oil` input.

- `backend/app/cluster.py`: `RawInput.oil`, `"oil"` in `TELLTALE_KEYS`, rule in
  `compute_telltales`
- `backend/app/state.py`: `"oil"` added to `_BOOL_FIELDS`
- `backend/tests/test_cluster.py`: `test_oil_lit_from_toggle`

Closes #<n>
~~~

**Done when:** merged and green; `POST /api/input {"oil": true}` lights the oil
lamp in `/api/state` (visible immediately in the cluster).

*Goes red if:* you add the rule but forget `"oil"` in `TELLTALE_KEYS` (or vice
versa) — the `to_dict` telltale-keys test fails.
