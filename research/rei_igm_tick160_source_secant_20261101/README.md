# REI tick160: source-authentic two-snapshot diagnostic

Scope: frozen 46,080-node original REI H/He accepted state (PR320) versus successful original 26-event source snapshots at t0 and tick160 (PR321). **No new cosmological IVP, no source-consistent time history, no promotion of the 28/88 central DAG.** The midpoint of independently bounded source fluxes is not a coherent realization; trapezoid residuals are **not** physical local truncation errors.

## Reproduce

Unzip in a new isolated directory, with Python ≥3.11 and NumPy, pandas, matplotlib installed. Then run:

```
bash REPRODUCE.sh
```

The 43MB original source ZIP files inside `source/` are byte-locked and retrieved originally from GitHub Actions run `41259585168` (accepted-state archive) and `41266684253` (source-26-event artifact). The script checks hashes/CRCs, recalculates 46,080 nodewise source-vs-accepted representative diagnostics, validates independent standard-library/Decimal65 recomputation, regenerates two science figures, runs 25 normal and 25 optimized unit tests, and verifies the output manifest. It never modifies the original REI owner repository or source inputs.

**Evidence:** `REPORT_KO.md`, `R6_C9_ADVERSARIAL_REVIEW_KO.md`, `results/SUMMARY.json`, `results/INDEPENDENT_AUDIT.json`, `STAGE_LEDGER.csv` (20 stages, all central 28/88, zero canonical gain). The full 26-event common-parent nonlinear difference map `F_h - F_{h/2} o F_{h/2}` and first canonical interval are not certified. Source correction, additional IVP, merge, force push, and threshold changes are not performed here.

Reference: Pawlik & Schaye (2011), MNRAS 412 1943, DOI https://doi.org/10.1111/j.1365-2966.2010.18032.x, background physics only, not a validation of this particular original REI implementation.
