# Temperature-rate implementation

R1–R10 and C1–C10 are complete within scoped root admission. C8 adopts existing source-matched execution without replay, and fresh independent actor C9 is PASS_SCOPED.

## C1 — baseline and inputs

Frozen source baseline: `4583ed342b8476e86e42b023d6de1d0f50820adb`. This local source tree has no `.git` metadata; the publisher owns exact remote source intake and publication. The direct Grackle 3.4.1 bundle is the reference. The table remains opt-in. Default direct point evaluation may reuse its single immutable coefficient bundle after equality verification.

## C2 — equation-to-code map

`igm_rates.rs::igm_rates(T)` owns source literals and all channel units. `igm_thermal.rs::igm_point_rhs` owns event/density/energy products. `axbi_rates.rs::AxbiProvider::point` currently invokes both the RHS and a second direct bundle. A `PreparedIgmRates` record binds one temperature to one immutable bundle; the point adapter reuses it. The D H-equality approximation consumes the same prepared H coefficients with unchanged unit conversions.

## C3 — numerical design

`rate_table.rs::LogRateGrid<const N>` will store coefficient-major logarithms on an immutable uniform log-temperature grid. Source wrappers certify branch-smooth cells and structural exact-zero channels; unsupported cells evaluate the unchanged direct provider. Log-linear interpolation acts only on finite positive normal values. The IGM wrapper stores fifteen independent channels, derives selected DR cooling from the exact source branch, reconstructs diagnostic predicates, and preserves exact source CI floors. No derivative API is implemented.

Batch evaluation first prepares cell indices and interpolation fractions for identical input temperatures, then traverses channel-major contiguous output arrays. A bounded scoped-thread batch preserves input order and uses at most four threads. This is a data layout and work-sharing interface; SIMD acceleration will only be claimed if measured directly.

## C4 — execution and resource plan

Toolchain/build limits and aggregate run limits are owned by the root contract. The prescribed order is frozen theory → shared grid/provider implementation → targeted API/boundary verification → coefficient accuracy probe → same-input timings → independent review → handoff. The additional provider owner writes only its new module/test/data. This owner writes the shared grid, existing prepared-rate consumers, and module registrations. Existing native campaigns and their checkpoints are outside these commands.

The official minimal Rust 1.94.1 toolchain was installed into a task-specific scratch prefix. `cargo --version` succeeds; `rustc --version` receives SIGBUS before compilation. The targeted official Rust 1.85.1 alternative works and compiled the H/He prototype. The earlier SIGBUS is retained as an environment failure. Focused production verification uses unchanged actual source paths while omitting only the unrelated joint_affine module/reexports whose float next-up/down API requires a later compiler; the full production crate build is not verified on this compiler.

The initial 8193-node H/He R7 prototype failed the 10^-5 target with maximum sampled relative error 2.45372755×10^-5. Root authorized the prescribed 65537-node refinement, which passed with 3.83876979×10^-7 over 421,431 queries. These executions are reused rather than repeated during C stages. Fifteen independent channels produce sixteen output fields; exact structural-zero DR and diagnostic-source predicates are tested separately.

Active added-nucleus scope is lithium A=6,7 and q=0…3 under the required ElementalElectronicEquality policy. The source provider owner implements the frozen numerical rows, explicit state identities, number-rate conservation, and typed missing-source result for IsotopeResolved. Historical carbon exploration is inactive. No default inventory, nuclear evolution, photoionization, or thermal closure is introduced.

The source publisher compared actual remote fbe09a23d2c5152d646cd2a44d42f5324fcf63e8 with local owned sources. Four rate/consumer files match exactly. The latest lib.rs contains three additional module registrations that must be retained when adding the new modules. The source comparison is recorded in coding_evidence/FRESH_SOURCE_COMPARISON.json.

## C8 — adopted performance evidence

`REPORT.md` and `coding_evidence/C8.json` consolidate local Rust 1.85.1 and upstream PR177/178 Rust 1.94.1 as separate cohorts. `summarize_local_timings.py` reads only preserved stdout and emits all local three-sample median/min/max groups plus all three upstream fair-worker run-level groups. No scientific execution occurred. Default prepared point gain is 1.342x locally; matched-worker upstream N=262144 gains are 1.608x ordered and 1.371x random, with setup amortization explicit. Table value accuracy does not admit derivative/Jacobian use or a full trajectory. Upstream independent actor review was NOT_RUN; the fresh independent C9 subsequently passed within the scope recorded below. The current frontier is updated from immutable newer receipts rather than repeating completed mixture-EOS derivation.

## C9 — independent admission

Fresh read-only independent review at `evidence/C9_INDEPENDENT_REVIEW.json` is PASS_SCOPED with no blockers or repair. Root admits only coefficient/prepared-point validation and the conditional Li6/Li7 number component, with conditional measured throughput. No scientific tests/builds/runs were repeated. The upstream standalone Rust opt-in policy remains externally reported and advisory, without independent code admission here. Mechanical C9 publication then C10 handoff completion is authorized.

## C10 — scoped closeout

Root admitted the coefficient/prepared-point and conditional Li6/Li7 number-component result after fresh C9 PASS. Handoff, current scoped frontier, Korean resume prompt and self-contained focused restore instructions are finalized. Publication and real cloud readback belong to `FINAL_PUBLICATION.json` and publisher receipts. No production source, scientific output, default backend, physical model, native allocation, deadline or observer changed during closeout. The requested role identities remain distinct from unobserved runtime model identity.
