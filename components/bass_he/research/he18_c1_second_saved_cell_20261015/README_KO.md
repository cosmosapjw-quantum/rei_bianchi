# HE18 C1 local coding research, source-bound runnable baseline

## Read first

`REPORT_KO.md` explains the computed warm P01 second cell and independent cold AXBI fixed-a signed-partial diagnostic. They are **EXPLORATORY**, not physical/certified scientific conclusions. Public Git should contain code and limited derived statistics only; private `inputs/P01_STATE.npz`, HM12 emissivity, original `ENDPOINT_MEMORY_R7.json`, and five cold partial samples remain in this private delivery ZIP.

## Commands (run from `HE18_C1_20261014`)

```bash
python verify_release.py
python -m unittest discover -s tests -p 'test_*.py' -v
python src/second_cell_pilot.py --out results/C1_SECOND_CELL_PILOT_OWN_RUN.json
python rei_supplier/signed_parity.py --samples rei_supplier/source --out results/C1_REI_SIGNED_PARITY_OWN_RUN.json
python src/make_plots.py
```

The last output arguments must not exist; the scripts refuse an existing output, preserving old evidence. The graph script regenerates deterministic scientific *diagnostic* plots. Requires NumPy and Matplotlib. `Wolfram/xAct` math checks were performed via connected evaluator, not required to run this Python package.

## Explicit next scientific code stage

`C2` is the first stage mapping **actual warm second-cell gas/photon Jacobians and source/proper-time evaluation** to the new source-matched error problem, including the nonzero first-cell gas4 + photon2904 incoming error. C1 source-unit fix is complete; true second-cell error and all 16-cell certification still require whole-cell bounds, first-exit and provider arithmetic. Do not silently import cold MD14 coefficient numerics into warm FT03/HM12.

The separate REI supplier only reads prior five terminal *partial* display CSVs at identical scale factor. Not at identical proper time; numerical roundoff/convergence and full reionization admission remain unknown. No active rei_bianchi source/process/DAG mutations are made.
