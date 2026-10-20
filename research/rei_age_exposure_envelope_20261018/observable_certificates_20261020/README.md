# Fixed-export observable source-age certificates

This additive analysis evaluates the previously theory-only energy, three species-event, age-moment, and normalized mean-age certificates on the same 57,344 exported labels and the same 8/16/32/64 birth clocks. It retains separate all, absorption-sensitive, and passive populations. The model keeps source weights, endpoint energies, geometry, and opacity fixed; only birth clocks change. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`. Native age/time HOLD decisions and nonlinear history claims are unchanged.

## Observed results

The Rust output contains directed intervals for seven observables in the order `N, U_ev, M1_s, M2_s2, HI, HeI, HeII`, signed paired differences, absolute label bounds, global moment fallbacks, and forward/reverse centered normalized mean bounds. Normalization requires a strictly positive denominator lower endpoint; otherwise it is explicitly `UNRESOLVED`. Each case includes photon-number and survivor-plus-absorbed same-energy ledgers that contain zero. The identity 64/64 pair has exactly zero stable kernels and error bounds.

The first full execution took 42.269 s. A controller-authorized targeted repair restricted exponential preload requests to actual node assignments. The revised execution took 13.422 s and computed 34,625 unique exact exponential arguments. Every scientific output float is bitwise identical to the first run; the comparison excludes execution metadata, timing, and cache counters. These timings describe this bounded implementation check and are not a benchmark or a general speedup claim. Both sets of raw outcomes remain available; the original is under `results/before_actual_request_cache/`.

An independent Python Decimal calculation uses 100 significant digits and direct two-exponential survival/moment formulas, with no copied stable difference kernels. It evaluates all input labels, all four clocks, and all three populations, then checks 612 aggregate interval and bound conditions. It passed in 12.855 s of subprocess wall time. All reference exponentials remain positive, including the largest optical depth, approximately 5452.864. Decimal references retain their approximately 100-digit strings. The revised run reused this reference through complete scientific bit parity; it did not repeat the full Decimal calculation. The cumulative two Rust executions plus one Decimal execution consumed 68.546 s against the 240 s analysis limit.

For the sensitive population, the absolute mean-age differences for clocks 8, 16, and 32 versus 64 are respectively approximately `9.22023e11`, `3.93992e11`, and `1.30813e11` s. The chosen certified upper bounds are `9.22060e11`, `3.94641e11`, and `1.35853e11` s. These are population-specific means; they are not divided by the all-population mass. The passive population has exactly zero number difference but nonzero age-moment and mean-age differences. The CSV files contain the full numerical comparisons.

`NORMALIZED_MEAN_BOUNDS.png` uses a logarithmic seconds axis so that independent mean differences and centered bounds remain visible alongside the much larger global fallback. The plot is generated solely from preserved JSON; changing this display does not rerun the analysis.

## Implementation and validation

`observable.rs` uses the existing public `certified` and `directed` APIs. The original crate, its upstream modules, the 22 vendored dependencies, and the original lockfile are unchanged. The build copies the crate into fresh scratch space and adds this analysis as a separate binary. Common exact clock ages are prepared once; actual-node requests are deduplicated by exact rational optical depth, evaluated with an indexed Rayon map, and inserted serially. All scientific accumulation follows the fixed node order. Signed kernels use signed interval arithmetic, without the old nonnegative clamp.

Ten focused Rust fixtures pass: passive number/age separation; identical births; positive versus passive rates; a stationary/cancellation moment example; both pair directions; unresolved zero-mass normalization; positive exponential upper bounds under central underflow; species conservation; small exponential thread parity; and complete small assigned-node Cache/case/pair parity across one and two Rayon workers. The original certified exponential proof and tests are reused without another full legacy suite. The additional wrapper preflight checks absent-output creation, rejection and preservation of a nonempty failed-build output directory, argument binding/help, and Python syntax.

The controller's requested executor role was a lower-tier coding agent. The runtime model identity was not independently observable and is not claimed from that request. `results/EXECUTION.json` records observed Rust and Cargo versions, commands, binary/source/input hashes, exit codes, wall and CPU times, and cumulative analysis consumption. The revised runner labels peak RSS correctly as the wrapper's cumulative child maximum rather than an isolated per-command peak.

## Reproduction

Run from the repository root with an installed Rust 1.94.1 prefix. Choose a fresh runtime directory. The default output directory is `RUNTIME/results`; `--out` can select another absent or empty directory. A nonempty output directory is rejected so that earlier success or failure logs remain intact.

```bash
python research/rei_age_exposure_envelope_20261018/observable_certificates_20261020/run.py \
  --runtime /tmp/rei-observable-fresh \
  --rust-prefix /tmp/age_runtime/prefix

python research/rei_age_exposure_envelope_20261018/observable_certificates_20261020/verify.py \
  --results /tmp/rei-observable-fresh/results

python research/rei_age_exposure_envelope_20261018/observable_certificates_20261020/summarize.py \
  --results /tmp/rei-observable-fresh/results
```

The runner uses `cargo build/test --release --offline --locked --bin observable -j 2`, a 240 s build cap, 120 s fixture/run caps, and two global Rayon workers. The validator is a separate direct reference calculation; use an external 120 s timeout when rerunning it. Python's standard library is sufficient for validation; Matplotlib is needed only to regenerate the plot. Input hashes are checked before the build. The scripts do not export new native nodes, call a nonlinear RHS, run native trajectories, or execute old optimization benchmarks.

## Preserved evidence

- `results/STUDY.json`: final Rust scientific values and actual mode counters.
- `results/EXECUTION.json`, `BUILD.*`, `FIXTURE_TESTS.*`, `RUN.*`: exact commands and raw current outcomes.
- `results/DECIMAL_REFERENCE.json`, `DECIMAL_RUN.*`: independent direct reference values and raw execution.
- `results/ACTUAL_REQUEST_CACHE_PARITY.json`: all-scientific-field bit parity and reference reuse.
- `results/WRAPPER_PREFLIGHT.json`: targeted output/path preflight facts.
- `results/OBSERVABLE_BOUNDS.csv`, `NORMALIZED_MEAN_BOUNDS.csv`, `NORMALIZED_MEAN_BOUNDS.png`: review tables and plot.
- `results/before_actual_request_cache/`: unchanged raw first-execution evidence.

The controller owns theory, frozen contract, scientific acceptance, and publication decisions. This implementation report states observed outcomes only.
