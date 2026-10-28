# Conditional source algebra units, 2026-10-28

These are two new finite exact-rational diagnostic units authorized by the corrected frozen numerical contract. They do not execute production models, rate fits, ODE trajectories, native science, old tests or old campaigns.

- `bass_crossblock/`: conditional 6 x 23 chemical geometry Jacobian block, enclosing A and B separately before the quadratic electron product; four potential geometry columns [1,2,3,13], 24 potentially nonzero entries and 114 structural zeros within this block.
- `vigilode_interval_remainder/`: uniform independent recombination-rate-box quadratic remainder and Hessian bound in unchanged physical metric; center-plus-radius operator majorant, exact squared-metric controls and radius-omission adversary.

`worker.py` embeds all new exact controls and writes `RESULTS.json`, `DIAGNOSTIC_INPUTS.json`, the preimport `SOURCE_HASH_MANIFEST.json` and a saved SVG. `RUN_RECEIPT.json` measures this whole science/reference/SVG child. `RENDER.receipt.json` measures only SVG-to-PNG rendering; `AGGREGATE_RESOURCES.json` totals both children and reports parent overhead separately. Host/global overhead is unknown, not zero. All authoritative comparisons are rational; plot labels are approximate display values.

Original commands (already executed once, exit 0):

```
python bass_crossblock/run_bounded.py
python vigilode_interval_remainder/run_bounded.py
python render_saved.py
```

Run from this directory or use absolute script paths. The runner refuses overwrite of existing logs/receipts; preserved outputs must be retained. A new scientific run requires root direction; do not remove previous evidence to replay a run.

Packaging must retain `common.py`, the unchanged `reuse/` subtree, both unit directories, and `../bounded_child.py`. Import paths deliberately use this local copied dependency tree. `reuse/source_intake/SOURCE_IDENTITIES.json` records pinned original repository identities. No owner checkout was changed.

Scope remains conditional on supplied source-field/rate/scale inputs. Actual corridor binding, full geometry and Thomson/tau rows, owner capsule, time variation and callback rounding remain open. All model/trajectory/whole-domain completion ceilings remain false/null, production HOLD, L4 false, central progress delta 0. Fresh independent authority review is required before admission.
