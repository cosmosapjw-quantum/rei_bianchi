# REI numerical research checkpoint, 2026-10-07

Incremental parent: `d1f40c2f893b0c4e3c03e72538d59a9bfcf99cec`.
This is a bounded research checkpoint. Original 37 field allowances and both number/energy budgets are unchanged. Conservation alone is not a history-accuracy certificate.

## Results and limits

- **R1, accepted finite fixture:** manufactured FLRW z=12 to 11.5, 1024 fixed nodes, union121 outputs. Three independent archived references pass all 37 fields; worst Gamma_HeII allowance ratio 0.4479077555, overall worst 0.9064143972 (CMB reservoir). The union's three subsets are not independent reruns. All 32 guarded microsteps remain unestimated.
- **R2, accepted subscopes:** zero initial radiation and zero source, z=30 to 20, neutral 30 K and low-ionization 20/300 K cases. The separate static pure-H constant-alpha kernel passes its own assumptions. Strong/hot/cold failures, the 10000 K reference failure, nonzero radiation stock and physical REC-to-REI handoff remain unresolved.
- **R5, diagnostic only:** the terminal exact stored-state energy defect remains about 1.03627e-30 erg/H, exceeding the original approximately 1e-30 budget. Higher precision in the final sum does not fix the state error. The 117363-case scalar arithmetic study includes stiff-recombination, subnormal and overflow counterexamples; none of its alternative formulas is integrated into the solver.
- **Exact transaction-local cache:** immutable successful cross sections are memoized by packet slot, energy bits and absorber channel. Public signatures, arithmetic order and failure gates are preserved. Tests reduce one fixture from 120 to 3 provider evaluations; 1108 transaction outputs and 45 history-file pairs match exactly. A separately reviewed full R1 replay matches all nine persisted files and all original scientific comparison metrics. This is a short-fixture identity bridge, not a long-history certificate.
- **Performance:** controlled local process-CPU microbenchmarks observe 25.947% and 32.940% reductions at 32 and 512 nodes. These are not full-trajectory or universal speedups. Historical full-run wall times are not used for a speed ratio.
- **Long FLRW pilot, failed spectral adequacy:** both Radau references complete z=12 to 10 on 273 epochs and pass their own budgets, but p64 versus p128 fails 8/37 fields. Worst out_E and out_N allowance ratios are 1362.1124 and 335.1653. Whole-node lower-boundary transfers create grid-phase-dependent stock staircases. Endpoint agreement does not rescue the history.
- **Continuous-boundary design, math only:** positive two-moment panels and a continuously cut occupied interval have independent design review. Moment realizability, source-front support, moment-exact quadrature and coupled 37-field validation remain implementation gates. No new boundary prototype is included.

## Contents and reproducibility

`spectral/` contains four compact 121-row numerical tables, exact configuration/schedule and results. `long-flrw/` contains the two compact full 273-row histories and the failed field assessment. Large spectral states, executables, build trees and run logs are omitted. `cache/IDENTITY_OUTPUT_HASHES.json` binds all nine full replay outputs retained in the research archive; those full files are not all copied here.

From the repository root:

    cargo test --offline --locked --all-targets --manifest-path rust/rei_microphysics/Cargo.toml
    python docs/research_program/igm_next_nodes_20261007/verify_checkpoint.py
    python -m unittest discover -s docs/research_program/igm_next_nodes_20261007/roundoff/regime-probe -p test_regimes.py

The first command covers all four cache tests. `atomic_provider.rs` adds only `cfg(test)` counters; release builds contain no counter instrumentation. The actual production delta is confined to `igm_photo.rs` and `igm_step.rs`. The transaction and benchmark Rust fixtures under `cache/` can be copied into a disposable checkout's examples directory for baseline/candidate reproduction; they are not registered production examples.

The scalar probe, exact-local analyzer, and boundary arithmetic script write their result JSON beside themselves. Run them in a disposable copy if preserving this checkpoint's hashes. Scalar-probe file references and boundary-script output paths were relocated; their numerical formulas were not changed. The archived input source and adapted script hashes are explicit. The boundary script requires mpmath; the reference tools use NumPy/SciPy. No new runtime dependency is added to the Rust crate.

The static kernel can be tested by copying `sourcefree/kernel.rs` and `sourcefree/kernel_test.rs` into a disposable crate test directory. Keep the kernel file beside its test, because it is imported by path. It is an isolated constant-density, constant-alpha test, not a coupled cosmological-history test.

## Review and publication qualification

Scientific reviews are scoped in `ACCEPTANCE_SCOPES.json`, `cache/INDEPENDENT_REVIEW.json`, `cache/IDENTITY_BRIDGE_REVIEW.json`, and `boundary-design/INDEPENDENT_REVIEW.md`. Public projections omit execution locations and coordination metadata while preserving numerical values and scientific limitations. `SOURCE_PROVENANCE.json` identifies original and staged hashes for relocated material.

Repository-wide formatting was already failing on 12 unchanged legacy paths at the parent commit. The two optional, unregistered cache harnesses also have formatting debt. This checkpoint does not repair unrelated formatting and does not claim green CI or merge readiness.
