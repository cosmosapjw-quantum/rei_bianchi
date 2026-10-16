# R9 Unit6 — independent lightweight microphysics

**Final scientific decision:** PASS_SCOPED_LOCAL_IMPLEMENTATION_ALL_THREE_LANES; 18 focused tests passed. See [Korean report](REPORT_KO.md), [eight-programme DAG](progress/DAG.md), and [independent review](review/IMPLEMENTATION_REVIEW.md).

This additive package contains three external-calculation-independent units:

1. Streamed QR/TSQR evaluation of cached daughter-spectrum residual diagnostics.
2. C99 hydrogenic two-photon kernel completing the actual 32 saved E1 cascade mixtures.
3. No-shakeoff charge-resolved Be7 electron-capture maps, generator, uniformization and actual-donor conditional evolution.

The existing Unit4/Unit5 checkpoint, solver and external NCP job are unchanged. No physical H action or NCP action was performed. Actual spectral refinement remains HOLD. All eight complete physical programmes remain open.

## Files and evidence

- `spec/`: frozen mathematics, input identities, tolerances and stopping rules.
- `code/`: standalone Python kernels and C99 two-photon kernel.
- `inputs/`: byte-identical publicly publishable source copies needed by these units.
- `tests/`: the executed focused tests and bounded runners.
- `results/laneA/`, `results/laneB/`, `evidence/EC_RESULTS.json`: actual observations, including all prescribed quadratures and conditional exposure families.
- `review/`: theory and implementation decisions by an independent reviewer.
- `docs/`: per-lane implementation records and timings.
- `progress/`: every R1–R10 and C1–C10 step, DAG and delivery receipts.

Pre-review execution receipts deliberately retain PENDING_INDEPENDENT_REVIEW. The final review supersedes that field without rewriting contemporaneous evidence. Requested model and observable runtime identity are recorded separately; the latter is UNKNOWN where telemetry was unavailable.

## Reproduction

Python, NumPy, SciPy, a C99 compiler and GNU `timeout` are required. Recorded runtime versions and the actual compiler command are in the execution evidence. No package installation or solver replay is part of these commands.

Preserve original evidence by reproducing in a fresh **artifact directory**. From this package root:

```sh
rei_repro_dir="$(mktemp -d)"
cp -R code tests inputs spec "$rei_repro_dir/"
mkdir -p "$rei_repro_dir/results/laneA" "$rei_repro_dir/results/laneB" "$rei_repro_dir/evidence"
cd "$rei_repro_dir"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
timeout 29s python tests/run_residual_evidence.py
timeout 30s bash tests/run_twophoton.sh
timeout 29s python -m unittest discover -s tests -p test_ec_bridge.py -v
```

The residual CLI test intentionally requires a previously absent `results/laneA/cli_output`; use another fresh artifact directory for a second repetition. Test outputs are new observations, not replacements for the published original evidence. The commands above are documented for future use and were not redundantly rerun during final packaging.

A standalone conditional donor report can be generated without the test suite:

```sh
python code/ec_bridge.py --donor inputs/laneC/R5_DONOR_BBN.json --out NEW.json
```

`NEW.json` must not exist. It is a conditional calculation; its prepared-Be3 clock is not a recombination/cosmological history and its physical heat remains null.

## Optional connection after external results return

The QR implementation is an opt-in postprocessor of a compatible cache containing `V`, `KV`, `u`. It performs no Hamiltonian action and does not resume a solver:

```sh
python code/residual_qr.py postprocess   --checkpoint /absolute/path/to/compatible_checkpoint.npz   --weight 0.42436081799220793 --out /absolute/path/to/new_diagnostic_directory   --block-rows 64 --batch-points 256
```

The explicit weight is the unresolved complement for the pinned Li→Be+ input; it is not an ionization probability. A different input requires its own correct weight. This command was not run on the actual NCP checkpoint here. NPZ loading materializes the saved arrays, and the 11.38 timing ratio is from one N512/m32 synthetic comparison, not an allocation or production-speed guarantee. Original refinement criteria and cumulative external budgets remain unchanged.

T6 output is a per-precursor source yield. Its LiI response coefficients assume the explicitly declared incident flux and coverage, not an inferred cosmological flux. T7 requires physical rates, charge history, daughter energy/shakeoff data and native integration before a closed plasma trajectory is available.

## Delivery

S1 theory/design was published at d48372c98ee1fc0c7710561ed5b7392844e62707 and backed up twice. S2 contains code, actual outputs, review and report. Raw synthetic NPZ and the compiled shared object are in the full backup archive; text/code/CSV evidence is published in GitHub. `progress/MANIFEST_FINAL.json` lists each file and its delivery class. `progress/DELIVERY_FINAL.json` records actual final backup IDs, commit and verification levels after publication. This final receipt is intentionally outside the immutable archive it describes.
