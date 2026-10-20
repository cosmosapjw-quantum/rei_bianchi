# BRPERF01 native gas rate-bundle receiver

This independent, opt-in crate reuses one temperature-only H/He rate bundle for
the H/He/D collision RHS. The original parent crate remains unchanged.

## API

The package name is `rei_brperf01_native_rates`. All state, configuration,
budget, error, and result types are the original parent types. `GasRhs` is a
re-export of `parent::midpoint_gas::GasRhs`.

```rust,ignore
rhs_with_rates(&state, &config, prepared_temperature_k, &rates)?;
rhs_with_evaluator(&state, &config, &mut evaluator)?;
step_with_evaluator(&state, &config, duration_s, &mut evaluator)?;
step_strang_with_evaluator(&state, &config, duration_s, &mut evaluator)?;
```

An evaluator has type
`FnMut(f64) -> Result<parent::igm_rates::IgmRates, parent::ForwardError>`.
It is called once per RHS stage, hence twice for a nonzero explicit midpoint
step. A zero step does not call it. The evaluator path uses the original EOS
evaluation order; it does not add a separate EOS pass to prepare a bundle.

`rhs_with_rates` rejects any `prepared_temperature_k` whose floating-point bits
differ from the state's EOS temperature, including a one-ULP mismatch. The error
is `NetworkError::SourceMismatch`. Nonfinite coefficients produce
`NetworkError::NonFinite`; negative coefficients produce
`NetworkError::InvalidInput`. Structural validation includes diagnostic
coefficients. Physical provenance and interpolation error remain the selected
backend's contract; supplying finite numbers alone does not establish either.

## Preserved arithmetic and owners

The receiver RHS is copied from `parent/crate/src/midpoint_gas.rs`, with a
minimal dependency replacement recorded in
`evidence/RHS_ALLOWED_DEPENDENCY_REPLACEMENT.diff`. H/He collision, CMB,
free-free, species updates, and energy accumulation retain the original
expression order.

The private D collision adapter projects the original H-equality D coefficients
from the same `IgmRates` bundle. It preserves the original coefficient unit
conversion before the ordered density product; reassociating those operations
would break bit parity. Its CI, Case-A RR, RR kinetic cooling, and CE energy
terms preserve the original six-row energy accumulation, including zero PI and
CX rows. Arithmetic checks for otherwise unused D temperature and diagnostic
outputs are retained to preserve original rejection behavior.

The original `DAtomicProvider::photo_input_from_bound_rates(0, 0, source)`
constructs the sole private collision input. Consequently the provider and
photo threshold identity agree by construction. No new public D photo-input
API is exposed. When `use_cx` is true in the instantaneous RHS, the original
`d_atomic_rhs(..., DChargeExchange::Savin2002)` still evaluates CX; its native
validation and rate acquisition remain intact.

`step_with_evaluator` delegates state updates to original `midpoint_gas::apply`.
`step_strang_with_evaluator` delegates both CX half-flows to original
`midpoint_gas::cx_flow` and budget addition to original `add_budget`. It changes
neither CX controls nor the original work-limit classification. No photon,
geometry, source-birth, four-corner control, or production activation is added.

The fixture's D binding-energy defect of 0.0037 eV is explicitly a manufactured
regression control. It is not a new full-EoR initial-condition claim. Additional
T/He3/neutron populations in tests remain passive contributors to density,
electrons, EOS, and the existing global free-free owner.

## Executed validation

The 9 tests passed under both debug and optimized release builds:

| Comparison or guard | Scope |
| --- | --- |
| Direct RHS bit parity | 1,024 combinations: 16 temperatures, 4 density scales, spectators on/off, 8 collision/CX/CMB masks |
| Midpoint step result/error parity | 60 comparisons, including zero steps and deliberately inadmissible large steps |
| Native Strang history bit parity | 32 accepted steps across 4 temperatures, all H/He/D collision, CX, and CMB channels enabled |
| Evaluator calls | One per RHS, two per nonzero midpoint step, zero for zero duration |
| Prepared-temperature mismatch | One ULP, NaN, infinity, and negative temperature rejected |
| Invalid bundle/population | Negative and nonfinite coefficients rejected; original population constructor rejects negatives |
| Original contract failures | Source identity, photon ownership, CX ownership, temperature domain, invalid durations |
| Work-limit classification | Both original and adapter return `Cx(WorkLimit)` with a deliberately exhausted work budget |
| Arithmetic underflow rejection | Original and adapter return the same error |

Bit comparisons serialize every `GasRhs`, `FullState`, `EventBudget`, and
`NetworkResult` field used by these APIs, including all population entries,
photon bins, clocks, reservoirs, and attempt counters. The comparison does not
substitute formatted text or a floating-point tolerance for bit equality.

Strict Clippy (`--all-targets -- -D warnings`) and scoped rustfmt pass. Source
hashes in `evidence/ORIGINAL_SOURCE_IDENTITY.json` were checked unchanged. The
12 entries in that file are the adapter's source/manifest dependency inventory;
that count should not be described as the project's 12 physical-owner audit.

These results admit the direct-backend native receiver control. Table-induced
trajectory error and expanding photon-coupled histories require their own
validation; no previous convergence claim is inherited here.

## Reproduction

With the pinned Rust runtime and offline registry configured:

```sh
python3 RUN_VALIDATION.py
```

The runner records each command's exit status, logs, and source-hash checks.
`Cargo.toml` points to the unchanged source snapshot by relative path. A package
restore may update that path to an identical snapshot, whose hashes are checked
by the validation runner.
