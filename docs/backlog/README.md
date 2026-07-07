# Backlog — guided change exercises

Each file here is one **backlog item** = one **Issue** = one **PR**. They're
small on purpose — the point is the DevOps loop, not the code. See
[../workflow.md](../workflow.md) for how a change lands
(issue → branch → PR that `Closes #<n>` → review → green CI → merge).

Every item gives you: **what to change and why**, the **exact code + test**,
**where to edit**, and ready-to-paste **Issue** and **PR** text.

| # | Exercise | What you touch | Frontend? |
|---|---|---|---|
| 01 | [Oil-pressure telltale](01-oil-telltale.md) | backend telltale (warm-up) | already drawn (dark) |
| 02 | [Seat-belt telltale](02-seatbelt-telltale.md) | backend telltale (warm-up) | already drawn (dark) |
| 03 | [Shift-light at redline](03-shift-light.md) | threshold telltale | optional |
| 04 | [km/h ↔ mph toggle](04-mph-toggle.md) | unit conversion | none (readout uses the unit) |
| 05 | [Hyper-flash on bulb-out](05-hyperflash.md) | derived signal | optional |
| — | [Conflict & revert drill](conflict-drill.md) | Git, not app code | — |

Split them across the pair. **Start with 01 and 02** — they're backend-only and
their lamps are already on the cluster, so they light the instant you merge.

## Stretch (design-your-own)

Bigger, intentionally not spelled out line-by-line. Once the flow is comfortable
— still issue → branch → PR (`Closes #<n>`) → review → green:

- **Trip computer** — accumulate distance + average speed over time in
  `VehicleState` (needs a time source); expose `trip_km` / `avg_speed` in
  `/api/state`.
- **Odometer accumulation** — grow `odometer_km` from `speed × Δt` the same way.
- **EV battery gauge + range** — add a `battery_pct` input + a `range_km`
  estimate; render a third `MiniGauge`.
- **Sequential turn indicators** — pure frontend: animate the arrow lamp in
  segments instead of a single blink.
- **Fancier startup animation** — extend the needle-sweep in `Cluster.tsx`.
