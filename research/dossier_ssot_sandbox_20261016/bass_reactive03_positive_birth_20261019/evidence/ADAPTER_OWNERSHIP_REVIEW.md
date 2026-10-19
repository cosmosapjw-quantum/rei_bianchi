# BASS-REACTIVE-03: independent extension and ownership review

Date: 2026-10-19. Scope: immutable BASS-REACTIVE-02 crate, compiler adapter, and interfaces required for the proposed positive birth integral. The numerical implementation has not yet been reviewed by this audit.

## Verified baseline

The restored crate contains 97 files. SHA-256 inventory before and after baseline execution is identical for all 97. Rust 1.94.1 `cargo test --offline --locked --all-targets` executed 190 tests, with 0 failures and 0 ignored; strict Clippy also exited 0. All build products were directed outside the crate. These are current executions, not inherited PASS labels.

Evidence: `BASELINE_SOURCE_BEFORE.json`, `BASELINE_RUST_VERIFICATION.json`, `BASELINE_RUST_TESTS.log`, `BASELINE_CLIPPY.log`.

`owner_src` contains 13 Rust files: the 12 physical owner files plus `axbi_bass_background.rs`, the BASS background donor adapter. Preserve all 13 bytes, not just an unqualified numeric count of 12.

## Feasible additive compilation

An independent Cargo package can load the existing library as a public submodule and re-export its public items at the new crate root:

```rust
#[path = "../frozen/crate/src/lib.rs"]
pub mod upstream;
pub use upstream::*;

#[cfg(feature = "positive-birth")]
#[path = "positive_midpoint.rs"]
pub mod bound_midpoint;
```

The explicit root module takes precedence over the wildcard import. With the feature OFF, the original `upstream::bound_midpoint` is re-exported. With it ON, original modules that import `crate::bound_midpoint` see the additive implementation. The original module remains available as `upstream::bound_midpoint`, which is useful for a direct regression comparison. This is a compile-time proposal; the numerical feature is not implemented by this proof.

The actual adapter proof compiled all 19 existing integration test targets and passed strict Clippy. It also compiled calls to the existing `pub(crate)` methods `SourceAgeBridge::snapshot`, `opacity_channels`, `drift`, and `total_com_energy`. A separate Cargo dependency would not grant this visibility; same-crate inclusion does.

`pub mod upstream` is material: private `mod upstream` leaves the original shadowed module unreachable to clients and triggers `dead_code` warnings. Loading the identical physical file twice also triggers Clippy `duplicate_mod`; the extension must reside in a distinct new source file. The proof corrected both conditions without suppressing either lint. Its separate extension file is an exact copy used only to prove interface compatibility, not a new numerical method.

Evidence: `ADAPTER_COMPILE_PROOF.json`, `ADAPTER_COMPILE_PROOF.log`, `ADAPTER_STRICT_CLIPPY_PROOF.log` (superseded duplicate-module failure), `ADAPTER_STRICT_CLIPPY_PROOF_FINAL.log`. Probe package: `build/adapter_probe/`.

## Exact API and fixture constraints

`bound_budget` and `bound_adaptive` expect `MidpointBridge(SourceAgeBridge, RetardedControls, PoolLimits, Centering)`, with public fields `.0` through `.3`. `bass_reactive::BindingBridge` re-exports `crate::bound_midpoint::MidpointBridge`. Preserve this API if the original controllers are to compile unchanged. A new runtime field added to that tuple would break original constructors and would require additional adapter work; a compile-time opt-in avoids that need.

The restored `tests/bass_common/mod.rs` loads donor files relative to `env!("CARGO_MANIFEST_DIR")/../donor_input/donor`. The final new manifest directory must be a sibling of a faithful `donor_input` directory. Merely redirecting Rust source paths does not redirect that runtime fixture path. The cleanest portable package has `frozen/crate`, the new crate, and `donor_input` arranged explicitly; otherwise create a documented sibling symlink and validate all source hashes after restoration. This compile proof checked the test targets, but did not execute donor-fixture tests from its relocated manifest; the baseline fixture tests did execute from the restored original manifest.

## Physics and transaction ownership constraints

1. The physical source owner is `bound_source_age::SourceAgeBridge::source_births`: it derives redshift from the actual birth geometry and evaluates the original source before assigning spectral/angular labels and physical birth time. Any quadrature node must use its own geometry, Killing ray, source value and labels. No representative-birth substitution is justified by matching total photon number.

2. `bound_midpoint::photo` owns competitive HI/HeI/HeII/DI absorptions. It evaluates source-native channels against one predicted gas state, applies midpoint-volume density rescaling along each actual ray, and splits at threshold crossings. Species event numbers, their thermal excess and binding-energy change must be computed from the same weighted exposure, with each absorbed photon counted once.

3. `photo` prepares all photon residuals and all gas changes before committing. It rejects negative populations, unsupported temperatures, and a failed binding-energy ledger. The additive source integral must preserve this transactional behavior. A failed source or cubature preparation must leave the caller's initial state untouched.

4. `advance_with_diagnostics` has a temporary half-step predictor. None of its births, photon events, chemistry budgets or geometry work is committed. For `JointCxSplit`, native `midpoint_gas::cx_flow` is called for h/2 before and after the photon/non-CX corrector; the non-CX RHS uses `local.use_cx = false` and both half-flow budgets are added once. Reusing this sequence exactly preserves CX ownership. Merely repairing the corrector while retaining the GL predictor can leave an underresolved-opacity bias in the midpoint gas; quantify or repair that numerical dependency explicitly.

5. `SourceAgeBridge::drift` temporarily accumulates photon work; the midpoint transport then subtracts that drift-photon contribution and installs the transport work ledger. The ledger work is computed from final photon energy minus initial photon energy plus absorbed photon energy. Its exact cancellation is an accounting identity. The independent path-work quadrature remains a separate accuracy diagnostic. An AP birth repair must not count either the source energy or geometric work twice.

6. `bound_budget::attempt` evaluates the same immutable initial state at a coarse full step and two half steps for two CX precisions. It freezes one scale vector and keeps all four corners. The controller files can remain byte-identical through root module selection. Its current projection observes photon count, energy, P2, spectral/angular groups, and species events; it does not observe birth-age moments. Add age-distribution comparisons separately rather than claiming the unchanged controller certifies that dimension.

7. The native owner rejects `source_births` results with ncom <= 0. A generic source-integral routine may correctly accept j = 0, but that mathematical zero-source limit is different from passing an invalid zero-output object through MD14 source construction. Preserve owner validation and test the generic zero-source branch explicitly. Original opacity channels permit zero kappa through zero relevant neutral populations.

8. `bound_budget` treats only NegativePopulation, NegativeEnergy and TemperatureOutsideSource as recoverable outer-step rejections. `Cx(WorkLimit)` propagates as the original computational-budget error. A new birth-integral work limit must not be relabelled as CX failure, no physical solution, or failed temporal convergence.

## Review status

Baseline implementation: IMPLEMENTATION_VERIFIED.
Additive same-crate extension mechanism: COMPILE_AND_STRICT_CLIPPY_VERIFIED.
New positive birth algorithm, age moments, native coupled histories and scientific convergence: pending independent review of the actual new source and numerical evidence.
