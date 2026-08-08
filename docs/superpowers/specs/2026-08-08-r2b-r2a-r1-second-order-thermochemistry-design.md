# R2B-R2A Adaptive Globalization and Performance Design

## 1. Scope and durable boundary

This design continues the durable R2B-R2 result:

- nominal `dt`, `dt/2`, `dt/4`, `dt/8` failed the first-slab hard Picard gate;
- the same owner-correct physical map converged at `dt/256` with residual below `1e-10`;
- no clipping, owner reassignment, opacity inversion, or recombination surrogate is permitted.

The next bounded stage is

`P0.5-B2C2B0C-R2C-R1B-R2B-R2A-ADAPTIVE-INTERNAL-MICROSTEP-ACCEPTANCE-AND-GLOBALIZATION-LOCK`.

This stage may close only the adaptive acceptance/globalization and performance contract. It must not promote production node chemistry unless every required lane and ledger closes.

## 2. Research questions

1. Can recursive internal bisection, beginning at the locked `dt/8` partition, reach the already witnessed convergence regime without post-hoc timestep selection?
2. Can a positivity-preserving globalization make the fixed-point iteration robust without changing the physical operator?
3. Can the 46,080-node hot path be reduced from repeated DataFrame/JAX boundary crossings to one-time tensorization and compile-once kernels while preserving byte- and tolerance-level parity?
4. Do photon, nuclei, resolved thermal, and unresolved-energy gates remain componentwise closed under full-step/two-half-step acceptance?

## 3. Predeclared adaptive policy

For each canonical macro interval:

1. Start from eight equal internal steps (`dt/8`).
2. For each attempted internal step, solve three independent trials:
   - one full backward-Euler step;
   - first half backward-Euler step;
   - second half backward-Euler step.
3. Each trial must independently pass:
   - fixed-point residual `< 1e-10`;
   - owner and H/He nuclei residuals `< 1e-11`;
   - photon residual `< 1e-8`;
   - positivity without clipping;
   - resolved thermal cone;
   - unresolved energy routing;
   - exact-zero resolved source for `EFFECTIVE_HI_SUBGRID`.
4. Only after all three trials pass, evaluate blockwise full-vs-two-half local error with threshold `2e-4`.
5. If a trial or local-error gate fails, reject transactionally and bisect that internal step.
6. Minimum allowed internal step is `dt/1024`.
7. A successful internal step commits exactly once; rejected attempts and event rollback preserve parent state and ledger bytes.
8. Failure at `dt/1024` produces the earliest explicit certificate and no fitted repair.

Because `dt/256` is already an empirical existence witness for the first slab, this policy reaches that scale after exactly five bisections from `dt/8`; however, the witness does not by itself prove the full interval or thermal/local-error gates, which remain load-bearing tests.

## 4. Positivity-preserving globalization

For the fixed-point map `G(Y)`, use safeguarded damped Picard:

`Y_{k+1} = Y_k + lambda_k [G(Y_k)-Y_k]`.

The candidate set is predeclared:

`lambda in {1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64}`.

Accept the largest candidate that:

- remains in the positive H/He/thermal cone;
- preserves owner support and structural zeros;
- decreases the weighted fixed-point residual by the predeclared sufficient-decrease rule.

If no candidate is accepted, the internal step fails and is bisected. No projection or clipping is permitted. Convex damping is primary because convex combinations of positive parent and positive map states remain positive; Anderson acceleration may be retained only as a non-production auditor until a separate positivity safeguard is proven.

## 5. Performance architecture

### 5.1 One-time tensorization

At stage initialization, convert all canonical tables into immutable contiguous arrays:

- forcing: `[interval, quadrature_node, group]`;
- canonical total `kappa_g`, `J_g`;
- static node measure, density, column length, macro index;
- species/group cross-section matrix;
- owner/group support matrix;
- historical auditor weights.

No DataFrame construction, filtering, groupby, merge, or row iteration is permitted inside a fixed-point, bisection, or refinement loop. Pandas remains an ingestion and audit boundary only.

### 5.2 Structure-of-arrays state

Represent the material state as contiguous `float64` arrays with shape `[6, N_node]`, not lists of dataclasses. Maintain two preallocated scratch buffers and swap references after accepted iterations. Transaction rollback swaps the accepted buffer reference rather than deep-copying 46,080 Python objects.

### 5.3 Cached static factors

Precompute and hash:

- `W_i L_i`;
- supported `sigma_sg`;
- macro reductions/scatter indices;
- static geometry and Jeans factors;
- exact-zero masks;
- quadrature weights and interval maps.

Only state-dependent neutral/ionic fractions and temperature-dependent factors are recomputed per iteration.

### 5.4 Thermal kernel

The thermal balance is evaluated as one batched, fixed-shape kernel. Compilation occurs once outside the adaptive recursion. Runtime loops must not cross repeatedly between pandas, NumPy, and JAX.

Two predeclared backends are benchmarked after warm-up:

- array-native NumPy reference;
- one `jax.jit` batched kernel with static shapes and no Python loop in the compiled region.

The faster backend that passes parity gates becomes the stage candidate; backend selection is based on the locked benchmark matrix, not on science results. The unused backend remains an independent oracle.

### 5.5 Incremental diagnostics

Compute expensive global diagnostics only:

- on rejected attempts for the earliest-certificate record;
- on accepted internal steps;
- at macro endpoints.

Per-iteration logging stores compact norms and counters, not full node tables. Full node snapshots are written only at accepted macro endpoints or fail-closed terminal states.

## 6. Benchmark matrix and acceptance

Run after one warm-up compile/load:

- owner-law evaluation, 100 calls;
- thermal root, 100 calls;
- one Picard iteration, 20 calls;
- first-slab `dt/256` convergence witness;
- full first canonical interval under adaptive control.

Compare legacy oracle and optimized candidate using identical inputs. Required parity:

- owner fractions and group moments `< 1e-11` relative;
- H/He nuclei `< 1e-11`;
- photon ledger `< 1e-8`;
- thermal state `< 2e-4` blockwise;
- identical structural zeros and failure classification.

Performance gate:

- at least `5x` wall-clock speedup for the first-slab convergence witness, or
- at least `3x` speedup and at least `50%` peak-memory reduction.

If neither gate closes, optimization remains diagnostic and the legacy oracle stays authoritative.

## 7. Research-harness hypothesis matrix

- H1: recursive bisection alone closes the first canonical interval.
- H2: bisection plus safeguarded damping is required.
- H3: thermal local error, not fixed-point convergence, becomes the next earliest blocker.
- H4: an unowned subgrid-energy exchange term is exposed.
- H5: numerical overhead, not arithmetic work, dominates runtime; one-time tensorization and compile-once execution remove it.

Disallowed explanations include physical nonexistence inferred from macro-step failure, post-hoc lane selection, and fitted opacity/owner transfer.

## 8. Adversarial tests

- force a noncontractive owner response and verify bisection/rollback;
- inject one-ulp parent-state corruption and verify byte-identity failure;
- leak subgrid heating into resolved energy and verify exact-zero gate failure;
- permute node order and verify macro reductions and hashes are invariant after inverse permutation;
- change unsupported support and verify structural-zero failure;
- force JAX recompilation and verify compile counter catches it;
- compare cold and warm timings separately;
- inject an oscillating damped-Picard map and verify no false acceptance;
- verify no cross-lane state reuse.

## 9. Claim boundary

A pass may claim an adaptive, owner-correct, transaction-safe first-interval history and a verified optimized implementation only for the tested forcing and lanes. It may not claim full five-interval production history, R2C-R2, B2C2B, recombination splice, CAMB transfer, or Bianchi feedback unless their separate gates are subsequently closed.
