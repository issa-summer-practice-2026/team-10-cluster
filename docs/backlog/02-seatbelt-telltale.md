# 02 — Seat-belt telltale *(warm-up)*

> One Issue, one PR. New here? Read [../workflow.md](../workflow.md) first.

**Goal:** light the **seat-belt** lamp from a new toggle.

**Why:** same shape as [01](01-oil-telltale.md), so a second pair can take it —
the lamp is **already drawn** in the cluster and sits dark, so this is a
**backend-only** change that lights up on merge.

## The change

**`backend/app/cluster.py`** — add a field to `RawInput`:

```python
    battery: bool = False
    seatbelt: bool = False   # <-- add this line
    bulb_out: bool = False
```

Add `"seatbelt"` to `TELLTALE_KEYS`:

```python
    "low_fuel",
    "seatbelt",   # <-- add this line
    "bulb_out",
)
```

In `compute_telltales`, add the rule:

```python
        "low_fuel": inp.fuel_pct <= LOW_FUEL_PCT,
        "seatbelt": inp.seatbelt,   # <-- add this line
        "bulb_out": inp.bulb_out,
    }
```

**`backend/app/state.py`** — make the toggle settable by adding `"seatbelt"` to
`_BOOL_FIELDS`:

```python
        "battery",
        "seatbelt",   # <-- add this line
        "bulb_out",
    }
```

**`backend/tests/test_cluster.py`** — add a test:

```python
    def test_seatbelt_lit_from_toggle(self):
        assert compute_telltales(RawInput(seatbelt=True))["seatbelt"] is True
```

*(No frontend needed — the `seatbelt` lamp already ships in `TelltaleRow`.
Optional: **uncomment** the `{ name: "seatbelt", label: "Seat belt" }` line in
`LAMP_TOGGLES` (`frontend/src/components/Simulator.tsx`) for a clickable toggle.)*

## Issue

*Issues → New issue.* Title: `Seat-belt telltale`

~~~md
**What:** add a seat-belt telltale driven by a new `seatbelt` input.
**Why:** the shipped cluster already draws the seat-belt lamp but the backend
never lights it — wire it up. A clean, self-contained warm-up for the
issue → PR → CI → merge flow.

**Acceptance**
- [ ] `seatbelt` is settable via `POST /api/input`
- [ ] `seatbelt` is in `TELLTALE_KEYS` and lights when the input is true
- [ ] a unit test covers it; backend `pytest` + `ruff` are green in CI
~~~

## Pull request

Branch `feat/seatbelt-telltale`. Title: `feat: seat-belt telltale`

~~~md
Lights the (already-drawn) seat-belt lamp from a new `seatbelt` input.

- `backend/app/cluster.py`: `RawInput.seatbelt`, `"seatbelt"` in `TELLTALE_KEYS`,
  rule in `compute_telltales`
- `backend/app/state.py`: `"seatbelt"` added to `_BOOL_FIELDS`
- `backend/tests/test_cluster.py`: `test_seatbelt_lit_from_toggle`

Closes #<n>
~~~

**Done when:** merged and green; `POST /api/input {"seatbelt": true}` lights the
seat-belt lamp in `/api/state`.

*Goes red if:* you add the rule but forget `"seatbelt"` in `TELLTALE_KEYS` (or
vice versa) — the `to_dict` telltale-keys test fails.
