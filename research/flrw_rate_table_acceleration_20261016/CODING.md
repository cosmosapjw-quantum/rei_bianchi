# Temperature-rate implementation

C1–C4 architecture is prepared against the Astra-owned contract; completion is gated by frozen theory intake. The numerical implementation has not started.

## C1 — baseline and inputs

Frozen source baseline: `4583ed342b8476e86e42b023d6de1d0f50820adb`. This local source tree has no `.git` metadata; the publisher owns exact remote source intake and publication. The direct Grackle 3.4.1 bundle is the reference. The table remains opt-in. Default direct point evaluation may reuse its single immutable coefficient bundle after equality verification.

## C2 — equation-to-code map

`igm_rates.rs::igm_rates(T)` owns source literals and all channel units. `igm_thermal.rs::igm_point_rhs` owns event/density/energy products. `axbi_rates.rs::AxbiProvider::point` currently invokes both the RHS and a second direct bundle. A `PreparedIgmRates` record binds one temperature to one immutable bundle; the point adapter reuses it. The D H-equality approximation consumes the same prepared H coefficients with unchanged unit conversions.

## C3 — numerical design

`rate_table.rs::LogRateGrid<const N>` will store coefficient-major logarithms on an immutable uniform log-temperature grid. Source wrappers certify branch-smooth cells and structural exact-zero channels; unsupported cells evaluate the unchanged direct provider. Log-linear interpolation acts only on finite positive normal values. The IGM wrapper stores fifteen independent channels, derives selected DR cooling from the exact source branch, reconstructs diagnostic predicates, and preserves exact source CI floors. No derivative API is implemented.

Batch evaluation first prepares cell indices and interpolation fractions for identical input temperatures, then traverses channel-major contiguous output arrays. A bounded scoped-thread batch preserves input order and uses at most four threads. This is a data layout and work-sharing interface; SIMD acceleration will only be claimed if measured directly.

## C4 — execution and resource plan

Toolchain/build limits and aggregate run limits are owned by the root contract. The prescribed order is frozen theory → shared grid/provider implementation → targeted API/boundary verification → coefficient accuracy probe → same-input timings → independent review → handoff. The additional provider owner writes only its new module/test/data. This owner writes the shared grid, existing prepared-rate consumers, and module registrations. Existing native campaigns and their checkpoints are outside these commands.

The official minimal Rust 1.94.1 toolchain was installed into a task-specific scratch prefix. `cargo --version` succeeds; `rustc --version` receives SIGBUS before compilation. This is an environment failure, so Rust numerical verification awaits diagnosis or another approved executor.
