# VigilODE native API, immutable evidence, and Rust package intake

Date: 2026-10-19 UTC. Independent Astra reviewer: `/root/dropbox_v15_intake`.

**Decision:** the useful bounded next integration is a same-native-RHS Radau IIA reference at immutable VigilODE source `8a8bd409b1d96c7b7421f496d229e119fd3d284e`. Root selected this contract and assigned implementation to a separate lower-tier coder. This intake performed read/download, source staging, dependency retrieval and retained-CSV analysis. It performed no solver build or solver execution and changed no numerical source, Git object, branch or cloud file.

## 1. Exact source and discovery coverage

The observed main HEAD is `8d0c79184e09efb5bdadc24a6315c60a71a44264`. Its complete Git tree has 677 entries; the current research-publication tree has 6,059. Main is not the newest numerical research line.

All 147 branch HEADs were inventoried through two REST pages (100 + 47). The observation was sequential, not atomic. The PR collection returned all 71 records. The latest PR, [#71](https://github.com/cosmosapjw-quantum/vigilode/pull/71), is a draft benchmark-publication PR targeting `claude/nice-dijkstra-208xq0` at base `a21d573980f66fe02891bd216153443b5352f921`. Its HEAD advanced from initial-list `fa07baf27a37674848d963e30e010d54e4af3f33` to detail/branch `0bab431e1031f86eb3ddb44371240bce49ae2376` during intake.

The Run 2 report identifies measured Rust source `8a8bd409b1d96c7b7421f496d229e119fd3d284e`. All **461 Git blobs** under crates/, plus Cargo.toml, Cargo.lock and rust-toolchain.toml, are identical between that source and publication HEAD 0bab431. Subsequent Python/publication changes do not constitute a fresh Rust binary measurement.

No AGENTS.md file, case-insensitively, appears anywhere in either complete main or current publication Git tree. This does not address unrelated workspace policies.

Evidence files: BRANCH_HEADS_OBSERVED.json, RECENT_PULL_REQUESTS.json, LATEST_PR_71.json, MAIN_TREE.json, MEASURED_SOURCE_TREE.json, PUBLISHED_SOURCE_TREE.json, IMMUTABLE_API_IDENTITY.json.

## 2. New retained benchmark evidence and its limits

The original CRLF CSVs were retrieved as whole bytes; SHA-256 and Git blob SHA-1 independently match the publication.

| Dataset | Reported measurement source | Bytes | Actual unique rows/status |
|---|---|---:|---|
| Run 1 endpoint sweep | ccaeaa50beb4580505a36d25ccb919ec3ca38c7f | 52,654 | 154 completed, all deterministic |
| Run 2 requested-grid triage | 8a8bd409b1d96c7b7421f496d229e119fd3d284e | 1,005,255 | 2,700 settings: 2,639 ok; 54 refused; 7 solver_failure |

Run 1 SHA-256: `8a78b5a9c9b9e37dcc599efc7a348457437f606399d2bf236759b7e02d14909c`.
Run 2 SHA-256: `03eda7909f39c467d1ddce7990dd2707b94a4dbb9bde5e036e21f1cf9435e2fa`.

Independent CSV aggregation gives Run 1 maximum saved endpoint WRMS plus empirical spread 0.9917799399710141. Among Run 2's 2,639 successful rows, 2,329 have R_up≤1, 2,580 have R_up≤10, and 2,626 have R_up≤100. Six failures are seq-mf-gmres on manufactured-vector-32 at h0_scale=2 (invalid inner-forcing flow norm); the seventh is pexprb54s4-fused on complex-dahlquist-32 (attempt/minimum-step limit). Exact failed rows remain preserved.

The nonlinear Prothero–Robinson uniform101 cell at rtol=1e-8 and h0_scale=1 has status ok for all three arms, but R_up is 6.63271e-7 for output-time stepping, 1751.99041 for dense-off, and 1.093303 for dense-enforce. A successful return therefore does not imply requested-grid accuracy. R_up uses an empirical reference radius and is not a continuous-time certificate.

**The publication explicitly lacks original native stdout, host/compiler receipts, process exit files, independent reference trajectories and paired timing/profiler receipts for these campaigns.** The CSVs are primary retained numerical observations. Their status columns cannot be substituted for independently observed process exits. The source labels above come from the primary published reports and are kept distinct from the later posting HEAD. No new native rei history is established by these VigilODE artifacts.

The repository-root RUN_RECORD.json is instead a Python gate-correction command at `314981e283ff9ae9961f2ec3fb220226c8b8dbab`, exit 0, with campaign_solver_reruns=0. It must not be relabeled a native run. The initially observed Actions run 39245944093 has an actual job log ending with exit 1 for ledger SHA/preregistration checks; that is not a numerical verdict and is not asserted to describe later HEAD 0bab431 CI.

Primary source: [benchmark README](https://github.com/cosmosapjw-quantum/vigilode/blob/0bab431e1031f86eb3ddb44371240bce49ae2376/research/benchmark_results_20261019/README.md), [Run 1 report](https://github.com/cosmosapjw-quantum/vigilode/blob/0bab431e1031f86eb3ddb44371240bce49ae2376/research/benchmark_results_20261019/run1/REPORT_KO.md), [Run 2 report](https://github.com/cosmosapjw-quantum/vigilode/blob/0bab431e1031f86eb3ddb44371240bce49ae2376/research/benchmark_results_20261019/run2/REPORT_KO.md).

Local: run1_original.csv, run2_original.csv, BENCHMARK_INTAKE_RECEIPT.json, RUN1_ORIGINAL_RESPONSE.json, RUN2_ORIGINAL_RESPONSE.json, VIG_CI_LOG.json.

## 3. Exact public APIs

All paths refer to source 8a8bd409. The compact copy preserves their exact Git blobs.

| Public API | File in crates/ | Actual role |
|---|---|---|
| OdeProblem::new | rodas5p-integrators/src/problem.rs | Arc callbacks; requires explicit Jacobian or JVP |
| radau_iia3_tableau | rodas5p-integrators/src/radau.rs | Returns public A, b, c |
| radau_step | rodas5p-integrators/src/radau.rs | One step; returns endpoint, all K_i, Newton report |
| integrate_radau_fixed | same | All accepted times/states and work counters; discards K_i |
| integrate_radau_adaptive_observed | same | Separate adaptive/output policy; not rei's physical clock |
| solve_dense_newton | rodas5p-integrators/src/nonlinear.rs | Modified Newton and bounded refresh; callback Err aborts |
| DenseMatrix, LuFactorization | rodas5p-core/src/matrix.rs | Public faer-backed partial-pivot dense LU |
| solve_gmres_into | rodas5p-krylov/src/gmres_into.rs | Caller workspace matrix-free solve |
| LinearOperator | rodas5p-core/src/operator.rs | Send+Sync operator and work-accounting interface |

The callbacks are:
- RHS: Fn(f64, &[f64], &mut [f64]) -> CoreResult<()> + Send + Sync.
- Jacobian: Fn(f64, &[f64]) -> CoreResult<DenseMatrix> + Send + Sync.

Construction:
```rust
OdeProblem::new(
    name, dimension, rhs_arc,
    None, Some(jacobian_arc), None, None,
    autonomous, None, None,
)
```

The one-step call is `radau_step(&problem,t,&y,h,&config,&mut counters)` and returns RadauStepReport. For identity mass it solves
K_i = h F(t+c_i h, Y_i), Y_i = y + Σ_j A_ij K_j.
Returned stage_increments[i] is **K_i**, not a derivative or stage state. The endpoint is y_new = y + Σ_i b_i K_i.

The public tableau has:
c = ((4−√6)/10,(4+√6)/10,1);
b = ((16−√6)/36,(16+√6)/36,1/9).

It solves a full real **3n×3n modified-Newton system**. The report explicitly labels transformed small real/complex solves deferred. A representative final-stage Jacobian is reused between bounded refreshes. With no batch callback, the three native RHS evaluations are serial.

The Newton routine immediately returns an error if a trial residual callback returns Err. It does not backtrack that domain error. The final Radau endpoint check tests finiteness only. Stage and endpoint physical admissibility must be enforced by the client. Generic OdeProblem::request_continuous_residual_authority explicitly returns UnsupportedUnboundModel.

Exact sources:
[problem.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/8a8bd409b1d96c7b7421f496d229e119fd3d284e/crates/rodas5p-integrators/src/problem.rs),
[radau.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/8a8bd409b1d96c7b7421f496d229e119fd3d284e/crates/rodas5p-integrators/src/radau.rs),
[nonlinear.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/8a8bd409b1d96c7b7421f496d229e119fd3d284e/crates/rodas5p-integrators/src/nonlinear.rs),
[matrix.rs](https://github.com/cosmosapjw-quantum/vigilode/blob/8a8bd409b1d96c7b7421f496d229e119fd3d284e/crates/rodas5p-core/src/matrix.rs).

## 4. Native integration implications

The root-selected experiment uses the same native closure/rates in an independent Radau discretization. It should retain existing SSPRK/default APIs and use a named opt-in reference path.

With fixed documented coordinate scales q=D^-1u and optional time scale τ=t/T, the callback is dq/dτ=T D^-1F(Dq,t). Include native photon/gas state and cumulative P/C/R/D, heat, binding, escape, CMB and work in the same augmented vector. They must share the same A,b. An unrelated endpoint rectangle for cumulative channels would violate this design.

For a linear physical balance combining states and cumulative channels, the shared RK stages retain the algebraic identity up to solved stage residuals and floating-point assembly. This is not a time-accuracy proof. Root separately derives and checks the balance algebra; this intake claims no new solver result.

Necessary clauses already relayed:
1. Preserve native physics, source normalization, EOS and default pathways.
2. Feed actual chronological physical-birth segments and accepted physical dt; the generic t+h report does not define the cosmological clock.
3. Reconstruct accepted Y_i from y,A,K for independent native stage-event audit.
4. Preserve domain-error failure; do not clip or project trial/end states.
5. Enforce gas domain and photon realizability at stages/endpoints.
6. Finite-difference Jacobian perturbations must remain admissible. Independent N/U perturbations at zero or a moment boundary can leave the realizable cone; do not conceal that failure.
7. Do not infer positivity, uniform stiff accuracy, Case B, fullEoR, signed Bianchi, continuous-time certification or whole-source-on order from the method's name.
8. Matrix-free Krylov and full controller/certificate migration offer no established benefit for the existing four-variable gas solve in this finite task.

## 5. Exact source and dependency staging

Workspace version 0.1.0; edition 2024; Rust/toolchain 1.94.1; MIT. Existing rei tools at v15_work/toolchain/bin are at the required version according to the prior actual execution receipt; this intake did not rerun the compiler.

Pinned declarations include faer0.24.4 (default-features=false; std,linalg,sparse-linalg), serde1.0.229, serde_json1.0.151 with float_roundtrip, thiserror2.0.19 and rayon1.12.0. Cargo.lock fixes all transitive packages.

The previous v15 Cargo home had no registry cache. A separate `cargo fetch --locked --target x86_64-unknown-linux-gnu` completed with exit0 in1.770008 seconds. This was dependency retrieval, **not compilation**. Its 101 archives total8,165,551 bytes; every SHA-256 matches Cargo.lock. Offline build readiness remains dependencies-fetched, not build-passed.

Paths relative to /workspace/scratch/6af5e9e6c737:
- v16_work/vigilode_intake/native_source_closure/: 477 unchanged workspace+fixture files,8,339,626 bytes; all matched to immutable Git blobs.
- v16_work/vigilode_intake/cargo_home/: isolated downloaded dependencies.
- v15_work/toolchain/bin/: reusable cargo/rustc.
- v16_work/vigilode_intake/immutable_8a8bd_source/: retained expanded crate/fixture/docs/tool source.
- vigilode_8a8bd409b1d96c7b7421f496d229e119fd3d284e.tar.gz: full immutable original source/evidence archive,53,500,226 bytes, SHA-256823164c2e78c0b3229e45df0087dd9af094d6900b6eb76f1dd66d9f3fb4af409.

The compact copy includes all workspace manifests to preserve Cargo resolution; default-feature core,krylov,integrators are the build scope. Coefficient include_str fixtures are included. Optional audit2-bateman-authority references historical research files and is outside the compact closure.

A concrete workspace ENOSPC occurred when writing this report. Only the redundant expanded immutable research/ directory (282,616,652 bytes) was reclaimed; its full exact archive remains. All crate sources, compact source, current CSV evidence and dependency cache remain. Therefore the original receipt's5,555 extracted-file count describes the completed initial extraction, not present expanded historical payload. Root separately coordinated space reclamation; no native input/source was changed.

Receipts: SOURCE_DOWNLOAD_RECEIPT.json, NATIVE_SOURCE_CLOSURE_RECEIPT.json, SOURCE_AND_CACHE_BYTE_RECEIPT.json, DEPENDENCY_FETCH_COMMAND.json, DEPENDENCY_FETCH_RECEIPT.json and fetch stdout/stderr.
Official dependency-fetch semantics: https://doc.rust-lang.org/cargo/commands/cargo-fetch.html

## 6. Current specialized Rust package findings

Exa searches requested8+6 results (sources_reviewed counter14), followed by official registry/docs/source reads. No package was installed or added beyond the exact existing vigilode lockfile.

| Version observed | Useful capability | Dependency detail | Finite-task decision |
|---|---|---|---|
| faer0.24.4, MSRV1.84.0 | PartialPivLu and Solve; dense/sparse algebra and matrix-free traits | Already pinned by vigilode. Registry default features add rayon/rand/npy; vigilode disables defaults. | Reuse through vigilode; no second backend and no presumed speedup. |
| diffsol0.17.1, published2026-09-28 | BDF, SDIRK/ESDIRK, custom tableaux, output quadrature, dense output, sensitivities | Exact normalized Cargo explicitly enables both nalgebra/faer in diffsol-la0.2.0 and diffsol-nl0.2.0, even though those dependencies set default-features=false. Disabling top-level defaults alone does not establish a one-backend closure. Optional JIT/CUDA/SuiteSparse/Sundials add further requirements. | Possible later independent BDF/SDIRK comparator; not needed for this vigilode-Radau task. |
| diffsol-nl0.2.0 inspected | Time-unaware NonLinearOp, Jacobian trait, NewtonNonlinearSolver, BacktrackingLineSearch | Uses diffsol-la; separate backend feature selection requires its own exact manifest review if adopted. | Concrete nonlinear layer, but no demonstrated advantage over the present four-variable physical-domain solver. |
| nalgebra0.35.0, MSRV1.89.0 | SMatrix<T,R,C> uses static ArrayStorage, including a4×4 representation | Additional backend; default std+macros. | Relevant small-system alternative, but would duplicate an adequate backend now. |

Faer's own documentation emphasizes medium/large matrices, not small-vector performance. This is a design description, not a rei timing measurement. The augmented Radau3n system should be assessed using the actual bounded run.

Diffsol's README retains a0.16 install example despite the registry/current normalized source identifying0.17.1. The exact0.17.1 Cargo source was used for dependency conclusions. The first nalgebra alias URL was unavailable; its official base-module alias page succeeded.

Primary sources:
- https://crates.io/crates/faer
- https://docs.rs/faer/0.24.4/faer/linalg/solvers/struct.PartialPivLu.html
- https://docs.rs/faer/latest/faer/
- https://crates.io/crates/diffsol
- https://docs.rs/crate/diffsol/0.17.1/source/Cargo.toml
- https://docs.rs/diffsol/latest/diffsol/
- https://docs.rs/diffsol-nl/0.2.0/diffsol_nl/
- https://crates.io/crates/nalgebra
- https://docs.rs/nalgebra/latest/nalgebra/base/type.SMatrix.html

Raw primary reads: VIG_EXA_RUST.json, VIG_EXA_KRYLOV.json, VIG_EXA_PRIMARY.json, VIG_EXA_EXACT.json, VIG_EXA_FINAL.json.

## 7. Review handoff

Root and /root/v16_bounded_coder received the immutable source/cache paths, callback signatures, stage semantics and fatal domain-error behavior before implementation. Intake is complete. The later Astra review will inspect the newly written adapter and actual new stdout/exits/raw trajectories after data-ready notification. The old14tests/52transportrows/16coupledsettings will not be rerun or recounted as new work.

