# VigilODE fresh source and execution intake for REI age exposure

Date: 2026-10-19 UTC. Intake is read-only. No VigilODE or REI branch was changed, no native solver campaign was launched, and no production admission was issued.

## Recommended next unit

Use the existing VigilODE **affine error transport** implementation, pinned to `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406`, as a dependency of a task-local REI conditional source-age envelope. Feed it actual prepared native photon nodes, gas fractions, and source inventory from the saved age64 run. Prove the nonnegative scalar leaf recurrence in REI, use exact dyadic rational arithmetic for exponential enclosures and conversion checks, and let VigilODE compose the resulting error maps.

The intended numerical experiment freezes a recorded gas state and geometry, preserves the actual 64-packet photon source inventory, and changes birth-time resolution only. This defines a precise external-opacity reference model. It can measure age-exposure sensitivity without claiming a bound on the evolving nonlinear Grackle trajectory. Its source, coefficients, and outputs are independently inspectable. It is more immediately useful than replacing the native ODE driver while its norm, callback, event, and moment-representation contracts remain separate research obligations.

The parent subsequently selected a minimal source facade: preserve the exact upstream affine_transport.rs and directed.rs bytes at this pin, retain the MIT notice, and explicitly identify a small CoreError/import compatibility layer. This avoids compiling unrelated solver modules. The full Cargo dependency option below remains the comparison considered during intake. The selected experiment compares the same 64 source packets under birth-time compression to 8/16/32 bins and the original 64 times, at frozen recorded endpoint gas and geometry. Implementation and independent review are separate work after this read-only intake.

## Scope actually inspected

- GitHub repository metadata, all 147 branches, metadata of all 71 pull requests, the latest 10 commits of the active benchmark code branch, relevant branch comparisons, recent Actions runs, and the releases endpoint.
- Complete nontruncated trees of the benchmark and production-audit branches (6059 and 6012 entries), plus the all-DAG tree. No `AGENTS.md` was found in these trees; direct root AGENTS lookup also returned 404.
- 28 pinned files from the PR71 intake snapshot, 13 all-DAG files, 9 additional all-DAG source/manifest/license/test files, and 2 explicitly re-fetched all-DAG directed/error modules. Every saved byte stream passed its Git blob SHA1 check.
- The two new benchmark CSVs, using the repository's existing standard-library verifier once. This was readback/integrity verification, not a solver execution.
- Primary documentation and source for the specialized Rust packages below using the selected Exa connector.
- REI's existing positive native donor, positive accessor, saved age64 setup, observations, endpoint, accepted coordinates, and solver receipt.
- Drive/Dropbox traversal is owned by the separate backup-intake agent. PR71 itself contains no provider ID, archive filename, folder link, or download link for its reported full campaign bundle.

This scope does not assert that every file in all 147 branches was read.

## Fresh branch and execution evidence

| Lane | Observed identity | Interpretation |
|---|---|---|
| Default main | `8d0c79184e09efb5bdadc24a6315c60a71a44264` | Stale relative to the research branches. |
| Active benchmark code | `claude/nice-dijkstra-208xq0`, `a21d573980f66fe02891bd216153443b5352f921` | Code HEAD on 2026-10-19, not the binary identity of every measured CSV. |
| Production audit | `da91553f019e011556ee042975f3cf05fc21a7c7` | Ancestor of the active benchmark code. |
| PR71 original intake | `0bab431e1031f86eb3ddb44371240bce49ae2376` | Exact source snapshot used to inspect the two numerical CSVs. |
| PR71 latest recheck | `ac1cd2a4738c2441c92e5fdae5f70aba35e53544` | Draft open, updated 2026-10-19 12:36:16 UTC, 11 commits, 19 changed files. Adds strict-comparison RED contract artifacts, no new solver CSV. |
| All-DAG reuse branch | `research/all-dag-completion-20261018`, `ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406` | Contains public affine transport and newer scoped verified-model APIs absent from the benchmark branch. Diverged from PR71; do not assume newest PR means a superset. |
| Cloud completion | `86afb40adcb0eda00c017c44b3553a8479c6c640` | Ancestor of the all-DAG branch. |

The all-DAG branch and initial PR71 snapshot each contain 21 commits absent from the other, with merge base `59d95eb7404882f024eb8bd3856f2ce4f1f830c9`. Select dependencies by exact API and source pin rather than merging these lanes.

Primary links: [PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71), [all-DAG source](https://github.com/cosmosapjw-quantum/vigilode/tree/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406), [benchmark code](https://github.com/cosmosapjw-quantum/vigilode/tree/a21d573980f66fe02891bd216153443b5352f921).

### Two actual benchmark datasets

Run1 contains **154 rows**, all marked completed and deterministic. Its 52654-byte CSV has SHA256 `8a78b5a9c9b9e37dcc599efc7a348457437f606399d2bf236759b7e02d14909c` and Git blob `01f8b90c0c72eeffe3a568d36f2bae6bc45c0349`. Measured source SHA is `ccaeaa50beb4580505a36d25ccb919ec3ca38c7f`. Maximum endpoint WRMS plus empirical reference spread is 0.9917799399710141. The cases are Robertson, HIRES, van der Pol, and Brusselator sizes 100 and 400.

For the reported Brusselator-400 target, the medians are 409.833040 ms (base), 25.659520 ms (fast), and 7.164704 ms (banded slices). These are scoped shared-host diagnostics; the dataset does not establish a broad speed claim. Source/base fast steps agree in 35 matched cells, but the overhead difference is not established by a profiler receipt in this PR.

[Run1 primary report and CSV](https://github.com/cosmosapjw-quantum/vigilode/tree/0bab431e1031f86eb3ddb44371240bce49ae2376/research/benchmark_results_20261019/run1).

Run2 contains **2700 rows: 2639 ok, 54 refused, 7 solver_failure**. Its 1005255-byte CSV has SHA256 `03eda7909f39c467d1ddce7990dd2707b94a4dbb9bde5e036e21f1cf9435e2fa` and Git blob `2800aea255360901e8da92ff14c013c1cd772fdf`. The measured source SHA is `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, not the later code HEAD. Among successful rows, 2329 have R_up <= 1, 2580 <= 10, and 2626 <= 100. There are 1320 successful endpoint rows and 1319 successful uniform-101 rows. Their maxima are 14.062535 and 1751.990413 respectively.

A particularly relevant exact slice is nonlinear Prothero-Robinson, uniform-101 outputs, rtol 1e-8, h0_scale 1:

| Driver | R_up | Accepted | Rejected |
|---|---:|---:|---:|
| seq-direct, lands on requested output times | 6.632710004483773e-7 | 106 | 0 |
| seq-direct-dense-off | 1751.990412875421 | 11 | 0 |
| seq-direct-dense-enforce | 1.0933030660056111 | 21 | 23 |

The last variant improves this requested-grid diagnostic greatly but still does not achieve R_up <= 1 in that row. These are empirical output-grid comparisons, not continuous certificates. The fast-ctl-pi subset has 144/144 applicable rows <= 1, with maximum 0.8860318531740459; the subset restriction matters.

[Run2 primary report and CSV](https://github.com/cosmosapjw-quantum/vigilode/tree/0bab431e1031f86eb3ddb44371240bce49ae2376/research/benchmark_results_20261019/run2).

The existing `verify_csv.py` returned exit 0 and `PASS_SCOPED_CSV_INTEGRITY`. This does not rerun a benchmark. The full profiler, allocation, paired timing, plotting, and reference payloads are not all present in PR71; the report mentions an approximately 184 MB bundle without a retrieval locator.

### New successful CI job did not execute the benchmark

The first strict-comparison status, run 39252371864, is `BOOTSTRAP_ONLY` with `benchmark_executed:false`. The latest run 39253322042 is:

```json
{"stage":"C2_RED","test_exit":1,"benchmark_executed":false}
```

Its exact Git blob is `272e39e6104d458d693ceed1836b9c085b14520a`. Do not classify the Actions workflow success as numerical solver success.

[Latest strict status](https://github.com/cosmosapjw-quantum/vigilode/blob/ac1cd2a4738c2441c92e5fdae5f70aba35e53544/research/strict_solver_comparison_20261019/runs/39253322042/status.json).

### Existing all-DAG execution evidence and erratum

The all-DAG saved completion validates source `33e45625be0803771156704263c3b1c1f92d2b40`, with a 414-file source manifest SHA256 `5a461ee10fc178e188631e242705d992978d68292d4a10f0ee3f856854cea916`. It records Rust/Cargo 1.94.1, Python 3.12.3, Ryzen 5900X with 24 threads, locked offline builds, six contract command groups passing, and six client examples exiting 0. The local timing set contains 450 rows. Later documentation reused these results without rerunning unchanged source.

Read the explicit timing erratum: the original report reverses the direction of the dense/structured ratio. For 8 modes dense is faster (84901 ns versus 191383 ns, ratio 0.43693); at 32 modes structured is faster (949563 versus 600991 ns, ratio 1.55831); the 128-mode paired ratio is 8.91756 favoring structured. These remain diagnostic instrumented timings.

A12 is `PASS_SCOPED_CERTIFICATE_APIS_BROAD_PRODUCTION_HOLD`. This is positive scoped evidence for reusable APIs, not arbitrary-client admission.

[Completion evidence and erratum](https://github.com/cosmosapjw-quantum/vigilode/tree/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/research/all_dag_completion_20261018).

## Exact reusable API

The module `crates/rodas5p-integrators/src/affine_transport.rs` at the all-DAG pin has Git blob `1c7024c2e1c567b337f82b0ba4530a1747022f51`. It imports only Rayon join, the core directed `add_up`/`mul_up` operations, and core error types. It is publicly exported by the integrators library. The core directed module is also public.

Available interfaces:

```rust
AffineErrorMap::new(gain: f64, defect: f64) -> CoreResult<Self>
map.gain()
map.defect()
map.apply(radius: f64) -> CoreResult<f64>
later.after(earlier) -> CoreResult<Self>

AffinePrefixWorkspace::new(n: usize) -> CoreResult<Self>
workspace.evaluate(&maps, initial_radius) -> CoreResult<&[f64]>
parallel_error_prefix(&maps, initial_radius) -> CoreResult<AffinePrefixBounds>
```

The represented map is radius -> gain * radius + defect. The constructor requires finite nonnegative coefficients. Composition computes g2*g1 and g2*d1+d2 with upward rounding. Prefix evaluation uses a fixed balanced tree with O(n) work and logarithmic ideal span and exposes all prefix radii, work counts, and tree depth. An existing contract test checks bitwise equality across one and four threads, exact-fraction comparison, subnormal cases, empty input, and refusal of invalid or overflowing inputs.

The library composes **caller-established bounds**. It cannot infer the physical gain or defect from an ODE callback.

[Affine source](https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-integrators/src/affine_transport.rs), [existing contract](https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-integrators/tests/affine_transport_contract.rs).

### Dependency shape

Use an exact `rev`, not a moving branch:

```toml
rodas5p-core = { git = "https://github.com/cosmosapjw-quantum/vigilode", rev = "ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406" }
rodas5p-integrators = { git = "https://github.com/cosmosapjw-quantum/vigilode", rev = "ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406" }
num-rational = "=0.4.2"
num-bigint = "=0.4.6"
```

The full upstream dependency is broader than the affine module: integrators also depends on core, krylov, faer, rayon, serde, and thiserror. Default research feature flags are empty. Workspace package version is 0.1.0, edition 2024, Rust floor 1.94.1. Workspace declarations include faer 0.24.4, Rayon 1.12.0, serde 1.0.229, serde_json 1.0.151 with float_roundtrip, and thiserror 2.0.19. Cargo.lock Git blob is `3539daa972b78bbfb532bf293bd1cdc6a09c5903`. These are upstream constraints; the consuming project still needs its own resolved lockfile.

A reduced exact-source facade could reduce build breadth, but would require explicitly preserving the MIT notice and source identity, and is a different integration decision. No such facade was created during this intake.

[Upstream Cargo manifest](https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/Cargo.toml), [integrators dependencies](https://github.com/cosmosapjw-quantum/vigilode/blob/ee65d4dbecf3b3cd5f4587c27f87ef297d2bb406/crates/rodas5p-integrators/Cargo.toml).

## What the other APIs do and do not solve

### Scalar tolerance and custom norm

Public `sequential_step` returns a `StepResult` with public `error_vector`, candidate state, stages, step size, scalar norm, acceptance flag, certificate field, and work counters. An outer driver can compute the original REI grouped/block norm from that defect vector. However, upstream scalar atol/rtol and WRMS are used internally. An outer rejection also needs consistent counters, cache rollback, and timestep policy. Passing `force_accept:true` does not itself implement the original REI acceptance semantics.

`OdeProblem::new` accepts a fallible RHS, optional analytic Jacobian, and optional JVP; at least a Jacobian or JVP is required. A numerically implemented JVP is type-compatible, but its accuracy, domain safety, and extra callback work remain the client's obligations. For a nonautonomous callback without explicit partial_t, upstream takes a central finite difference at times on both sides of the requested time. This can cross a birth boundary and must not be silently applied to a discontinuous source history.

The protected adaptive driver restores saved Krylov state on rejected steps and retries LinearSolve, NonlinearSolve, and NonFinite failures. It treats InvalidInput as fatal. The REI native domain failure cannot simply be mapped to an unrelated error variant to force retry. Callback side effects are not automatically rolled back. The newer benchmark branch has a fix to charge some attempted callbacks before an Err result, but operator/JVP wrappers still have post-success charging paths.

### Verified model factory

The all-DAG `generic_verified` continuous-model provider is sealed within the crate. Public factories support specific model owners. An arbitrary REI callback and an asserted Lipschitz constant cannot be inserted through the public API and called verified. A new native model factory would be a separate substantial source change with a new proof obligation.

### Scaling and the native moment obstruction

`binary_split` can normalize a positive finite f64, including subnormals, into mantissa and exponent. But `binary_scale`, `times_power`, and weighted vectors return ordinary f64 values. There is no persistent factored mass × normalized-shape state. These helpers prevent some intermediate overflow or underflow; they cannot make an impossible same-support f64 moment assignment feasible when final weights must still be materialized. Fixing that obstruction requires a new retained representation and compatible rate/reduction consumers.

### Existing directed exponential

The core directed module provides outward arithmetic and a verified exponential interval. Its existing exp implementation returns the deliberately broad interval [0, 2^-1019] for x < -707. That is correct but too wide for a tight subnormal optical-survival result. A task-local exact-rational alternating-Taylor enclosure of exp(-tau), with power-of-two range reduction and outward squaring, is a justified specialized addition. Optical depth multiplication must itself be enclosed. Generic rational-to-f64 conversion is not a directed-rounding contract; compare the candidate back to its exact dyadic rational or use monotone bitwise search.

## Concrete actual-REI input and model

Saved age64 input/output directory:

`evidence/ncp_blockmax_20261019T084150Z/run/results/age64/attempt001/data/`

It contains setup, endpoint, observations, source inventory, 65 accepted coordinate arrays, and provider/solver receipts. Setup has 64 birth packets, 128 transport cells, 256 coordinates per packet, 4 gas coordinates, and 14 extra ledger coordinates (16402 total). Birth times are available in both log-a and proper time. Endpoint gas physical values are:

```text
[0.010065857799832125,
 0.010066719415292124,
 0.000999219556540277,
 1.1243735845579859]
```

The first three are gas fractions and the fourth is thermal energy in eV per H. This exact dataset records a completed q0 age64 blockmax run with 19756 RPC calls and 781.5622 s wall time; it is already an execution result and should not be repeated merely to obtain a frozen-opacity fixture.

The original donor `donors/pr171/positive_native.rs` constructs the gas absorbers as

```text
nh = n_h0 / a^3
nhe = n_he0 / a^3
ab = [nh*(1-f_HII), nhe*(1-f_HeII-f_HeIII), nhe*f_HeII]
```

The original `donors/pr171/positive_accessor.rs` already uses each prepared native node's number, reference frequency q, species cross sections, and excess energy, with

```text
lambda_j = c * ab_j * sigma_j
lambda = sum_j lambda_j
```

A read-only exporter can live alongside that accessor, use the existing prepare/evaluate validation, and serialize these exact binary64 node fields with geometry, gas, source, and physics-source provenance. It need not modify the native evolution path.

For fixed coefficients the independently defined positive node flow is

```text
n_next = exp(-lambda * delta_t) * n + birth
photoevent_j = lambda_j/lambda * n * (1-exp(-lambda*delta_t))
```

with the zero-hazard limit handled explicitly. Using log-a instead of proper time requires declaring the coefficient lambda/H and the geometry treatment. The saved proper times are preferable when preserving the original background clock.

To isolate source-age sensitivity, keep the actual 64-packet weights and node properties fixed and replace only birth times by age8/16/32 midpoint bins. The union event grid accommodates all versions. For two coefficient/source histories, a leaf inequality is

```text
e_next <= a_upper*e
          + abs(a-b)_upper*n_B_upper
          + abs(birth_A-birth_B)_upper
```

where a and b are enclosed attenuation factors. VigilODE's exact affine API then composes these local obligations. A declared nonnegative hazard-uncertainty interval can enlarge the model family; a hull of sparse gas samples alone does not certify the true gas path between samples.

Use original source birth templates when the aim is source-age response. Exporting normalized accepted endpoint cohorts instead answers a different frozen residual-survivor question. The native moment closure reconstructs its quadrature as the shape evolves, so either frozen-node experiment must state its model scope explicitly.

## Specialized Rust package choices, verified from primary documentation

| Package | Exact useful version | Task-specific role and limitation |
|---|---|---|
| num-rational | 0.4.2 | BigRational::from_float represents an input finite binary64 exactly. Suitable for dyadic fixture identity, Taylor remainder bounds, and directed-conversion checking. Its round() is half-away-from-zero, not an IEEE ties-to-even oracle. |
| num-bigint | 0.4.6 | Compatible integer type for num-rational 0.4.2. Latest 0.5.1 exists, but mixing that BigInt with num-rational's 0.4 dependency causes type-version incompatibility. |
| libm | 0.2.16 | Pure Rust frexp/scalbn, including subnormal normalization, useful for scale handling. Does not preserve an extended-exponent state by itself. |
| Diffsol | 0.16.1 | Existing VigilODE A07 harness already pins this version. It offers BDF/SDIRK/ERK, vector atol and JVP support, but would be an additional ODE comparator, with its own callback-domain bridge; unnecessary for the exact frozen scalar model. |
| rug | 1.30.0 | Correctly rounded multiprecision Float and Rational, useful as an independent high-precision oracle. Native GMP/MPFR/MPC build dependencies are heavier than needed for the immediate exact-dyadic envelope. |

Primary sources:

- [num-rational package](https://docs.rs/crate/num-rational/0.4.2), [implementation](https://docs.rs/num-rational/0.4.2/src/num_rational/lib.rs.html), [Cargo dependencies](https://docs.rs/crate/num-rational/0.4.2/source/Cargo.toml)
- [num-bigint compatible version](https://docs.rs/num-bigint/0.4.6/num_bigint/)
- [libm 0.2.16](https://docs.rs/crate/libm/0.2.16), [frexp implementation](https://docs.rs/libm/0.2.16/src/libm/math/frexp.rs.html), [scalbn implementation](https://docs.rs/libm/0.2.16/src/libm/math/scalbn.rs.html)
- [Diffsol 0.16.1](https://docs.rs/diffsol/0.16.1/diffsol/), [builder API](https://docs.rs/diffsol/0.16.1/diffsol/ode_solver/builder/struct.OdeBuilder.html)
- [rug 1.30.0](https://docs.rs/crate/rug/1.30.0), [Float API](https://docs.rs/rug/1.30.0/rug/struct.Float.html)

## Intake files

- `metadata_intake.json`: paginated GitHub branch/PR/tree/commit intake.
- `fetched_snapshot.json` and `snapshot_identity.json`: 28 exact PR71 files and blob identities.
- `all_dag_fetched_snapshot.json` and `all_dag_identity.json`: 13 exact all-DAG files and identities.
- `additional_intake_snapshot.json` and `additional_snapshot_identity.json`: fresh PR71 status/diff plus nine additional all-DAG public APIs, manifests, license, and contract tests.
- `snapshot/` and `all_dag_snapshot/`: decoded read-only source and numerical CSV files.
- `vendor_source_fetch.json` and `VENDOR_SOURCE_IDENTITY.json`: original affine, directed, error, license, and existing contract-test identities for the selected minimal facade. No shim or native exporter was implemented by this intake agent.

Publication, backups, and REI DAG updates remain owned by the parent task. This intake changes no protected owner checkout, PR150/R9 lane, or BASS HHeD lane. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

