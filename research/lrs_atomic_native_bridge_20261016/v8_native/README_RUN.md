# Reproduce the native RR/DR subset

This experiment links to frozen PR #150 commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4`; the `igm_rates.rs` SHA-256 must be `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`. It does not patch production. The Rust executable is a standalone example in a copied owner crate.

Create a new run directory from a repository containing the owner commit. `prepare_owner.sh` runs the exact `git archive` selection, checks the native rate source SHA, and copies only this experimental example and runner into that new directory:

```bash
./prepare_owner.sh /path/to/rei_bianchi /new/unique/run/directory
cd /new/unique/run/directory
cd rust/rei_microphysics
cargo build --release --example native_rrdr
cd ../..
bash run_native.sh
```

`run_native.sh` writes 30 CSV, 30 stderr, and 30 time files in `results/native`. Its six conditions and five resolutions are explicit in the script. For a single case, run `rust/rei_microphysics/target/release/examples/native_rrdr STEPS XEND DENSITY_FACTOR T0`.

From the independent PR #165 descendant checkout with SciPy and NumPy available, compare raw CSV against V8's `rhs_independent`:

```bash
python3 compare_native_radau.py /path/to/results/native NATIVE_RADAU_RESULTS.json
python3 verify_native_outputs.py /path/to/results/native NATIVE_RADAU_RESULTS.json NATIVE_CHECKS.json
```

The `a`, `H_s`, `nh_cm3`, `nhe_cm3`, and `dtmid_s` fields in each CSV row use that step's **midpoint X**. The `X`, stocks, electron fraction, gas energy and cumulative ledgers are **end of step** values. `ne_cm3` is the end-of-step electron fraction times **midpoint** `nh_cm3`; it is a diagnostic label, not the proper end-of-step electron density. All `exposure_*` fields use the same midpoint `strength = ΔX nH(Xmid)/H(Xmid)`. The unphased four channel fields use pre-step electron fraction and midpoint `alpha(Tmid)`; `exposure_begin_*`, `exposure_mid_*`, and `exposure_end_*` use respectively pre, average, and post electron fractions together with `alpha(Tbegin)`, `alpha(Tmid)`, and `alpha(Tend)`. They do not evaluate `nH/H` at the named phase. The escaped-radiation ledger is energy only: `binding_* + cooling_*`; escaped photon count is not defined by this closure.
