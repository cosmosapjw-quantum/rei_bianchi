Publication note: hash declarations in this historical report identify archived original bytes. Relocated publication hashes are recorded in ../PROVENANCE.json. Some historical guard/run artifacts are summarized rather than copied; use ../README.md for the supported replay boundary.

# Independent V2 bounded-prototype review

## Verdict

**PASS for the selected, bounded pure-radiation control matrix. No coupled or production release.**

No material unresolved defect was found within that selected matrix after the review corrections below. The 512-subdivision opacity candidate passes the unchanged independent accuracy gate; 64, 128, and 256 remain rejected candidates. The original exact-binary64-input closure target is preserved and passes on the 30 reconstructed-density fixtures. All 138 expanded arithmetic fixtures pass, but those are normalization-only checks.

- **Specification:** pass for the declared V2 fixtures and fail-closed initial-moment/weighted-owner lane, with the admission and coverage boundaries below.
- **Engineering quality:** acceptable as an isolated research prototype. This is not a certification of every input accepted by every public helper, full logarithmic-tail transport, or a production API.
- **Claims:** the stable `FINAL_REPORT.md` and `RESULTS.json` accurately distinguish selected passing evidence, rejected candidates, and untested integration. Their numerical claims agree with the raw final results.

`NEXT_SHORT_COUPLED_CONTRACT.md` is a proposal only. This review neither authorizes its execution nor validates a nonlinear coupled result, projected multistep history, cosmological history, or 37-field certificate.

## Findings corrected during review

### 1. A subnormal intermediate could recover to a normal final moment

**Material admission defect, corrected; high confidence.** The earlier `try_moments` checked final N/M and selected factors, but not each multiplication. For `Density { l: 0, r: 3e-16, a: MIN_POSITIVE, k: 2e17 }`, `amp * width` lost precision in the subnormal range before a large phi factor returned the result to the normal range. Thus final normality did not establish safe initial moment formation.

The retained `intermediate_red` run reproduces erroneous admission. Final `src/primitives.rs:486–530` checks each relevant multiplicative operand and result before amplification. The corresponding regression in `src/tests.rs:428–439` now passes. There is no density floor or repair of the resulting moment.

### 2. A subnormal exponential could recover after multiplication by a large amplitude

**Material admission defect, corrected; high confidence.** `Density { l: -744, r: -743.5, a: 1e308, k: 0 }` previously admitted normal final moments despite the severely rounded subnormal `exp(l)` factor. The separate `V2_energy_intermediate` regression failed in `admission_edges_red` and passes in the final run. `src/primitives.rs:526` now validates the exponential before consuming it through `normal_product`.

These two corrections are important: checking only the final products would not close V1's general initial-moment admission gap.

### 3. Rounded width admission could include an exact width outside the declared interval

**Low-impact boundary-contract defect, corrected; high confidence.** Comparing only the rounded DD value admitted `l=2^-100, r=1e-7`, whose exact binary64-endpoint difference is below the minimum. The red boundary assertion is retained. Final `src/primitives.rs:702–708` compares both DD parts against the declared bounds; the lower-bound regression now rejects. The symmetric upper-bound condition is present in source.

### 4. Nonfinite log metadata was overwritten during aggregation

**Bounded validation defect, corrected; high confidence.** The implementation owner added a separate red regression showing that a normal scalar owner with NaN log metadata was accepted and overwritten. Final `src/primitives.rs:545–547` rejects nonfinite log metadata before mutation, and the final weighted-admission group passes. This validates finite metadata and authoritative zero/tail checks; it is not a general proof that arbitrary caller-supplied finite logs match their scalar values.

All four corrections preserve the ordinary support, owner, closure, and source regressions. The failed raw runs remain retained rather than being replaced by the final green result.

## Requirement-to-evidence assessment

| Requirement or risk | Evidence and result | Boundary |
| --- | --- | --- |
| Initial empty versus unsupported near-empty state | `try_moments`, final `V2_initial_admission` and `V2_energy_intermediate`: exact zero/empty intersection admitted; positive subnormal input, unsafe intermediate, overflow, and invalid input rejected | Normal-only lane; no full log-tail evolution |
| Atomic weighted owner updates | `try_add_scaled`, final `V2_weighted_admission`: scalar/log/pair validation, every positive weighted product, every candidate sum, then one commit | Cannot reconstruct provenance already discarded upstream |
| Floating-point boundary coverage | Successful MIN_POSITIVE and twice-MIN_POSITIVE pairs; rejected subnormal weights, true zero-product underflow, nonfinite/negative owners, product overflow, finite-product sum overflow; zero-weight no-op and unchanged accumulator assertions | Targeted boundary coverage, not exhaustive fuzzing |
| Raw N/M normalized target | 138 exact-input arithmetic fixtures checked against an independent 80-digit oracle; maximum absolute error 5.450638291957682e-17 | Arithmetic helper only, not 138 admitted reconstructions |
| Reconstructed-density scaled mean | 30 independent high-precision integrations of reconstructed ordinary/front densities; maximum absolute error 2.8831085657006487e-16, below 5e-13 | Fixed tested widths/betas and inversion bracket |
| Positive initial-opacity quadrature | Independent integrated absorption reference; selected 512 error 2.956499557859949e-7, below 1e-6 | One declared opacity-control fixture; not a universal order guarantee |
| Retained failed candidates | 64: 1.9104938742349023e-5; 128: 4.770484589164452e-6; 256: 1.187954289408449e-6 | All still fail the same 1e-6 gate |
| Shared owners, source support, smooth/atomic distinction | Final T1–T4, T3b, T5b, T6, and T7; original source budget allowance ratios 2.753848391759241e-6 for number and 6.341075472659316e-6 for energy | Tested pure-radiation and source-only controls |
| Reconstruction bias kept separate | T7b isolates the source reconstruction E^-3 observable; 64-panel relative bias 1.0613605512836729e-7 against 1e-3 | No joined projected source/absorption history |
| Immutable V1 and baseline | Independently recomputed all 102 inherited V1 and 11 source/design/evidence hashes; all match | Exact frozen input set, not a repository-wide audit |

The passing `T7c_inherited64_failure_reproduced` group means the inherited accuracy failure remains reproducible. It does not mean the 64-subdivision numerical approximation passes. Both oracle and aggregate results retain its failed accuracy status explicitly.

## Arithmetic and oracle independence

The final normalization helper at `src/primitives.rs:608–728` uses TwoSum-style compensated sums, FMA product residuals, corrected division, DD range reduction/Taylor/squaring for exp, and the exact DD difference of the supplied binary64 endpoints. A common power-of-two scale normalizes N and M before division. Unsupported nonnormal scaled moments reject rather than silently proceeding. The final answer alone is rounded back to binary64. The fixed raw-moment interface, 5e-13 scaled-mean criterion, and 1e-6 quadrature criterion were not changed.

The scoped exponential range, finite iteration bounds, and normal physical input scaling are consistent with the stated method. The 138-fixture agreement establishes empirical numerical accuracy over the tested domain/scaling combinations. It does not establish a rigorous interval-error bound over the entire admitted coordinate domain, and the final report correctly avoids that claim.

The important oracle checks are not self-comparisons:

- `oracle.py:43–49` interprets authoritative L/R/N/M and inverse beta as exact binary64 values, independently integrates the reconstructed density, and compares with the high-precision target implied by those moments.
- `oracle.py:80–83` recomputes expanded arithmetic targets from the actual rounded input moments. The generating mean is not used as the reference after rounding.
- `make_fixtures.py` first constructs and rounds each expanded moment, then computes the reference from that stored value. The normalization-only fixture test's exact equality to a rounded reference is supplemented by the independent higher-precision absolute-error gate.
- `oracle.py:69–79` integrates the continuous opacity control using high-precision adaptive tanh-sinh quadrature. The finite 512 rule is not its own acceptance oracle.
- Kernel count/energy and source redshift references are integrated independently from histories. No residual-based ledger repair was found.

The high-precision oracle reports 1,026 component/root checks with no failure and maximum tolerance ratio 0.011155055795756149. Of 172 approximation-gate records, the only failures are the three explicitly rejected opacity candidates. `RESULTS.json`'s complete accuracy-gate array, component count, and failure list were directly compared with the oracle JSON and match exactly.

## Residual limitations

1. Positive subnormal states/contributions are rejected. This deliberately sacrifices coverage for fail-closed behavior; it is not a log-tail transport implementation. The normal-only policy is established at initial analytic moment formation and weighted aggregation, rather than by a universal audit of all public helpers.
2. A zero owner arriving without authoritative metadata cannot reveal that an upstream operation previously rounded a positive physical quantity to zero. General tiny-time kernel/source evaluation is therefore not certified by these aggregation tests. The final report discloses this limitation.
3. The extended normalization cases do not enlarge the fixed reconstruction beta bracket or certify every corresponding closure. The 30 independent reconstructed-density cases remain the end-to-end closure evidence.
4. Quadrature estimates are not interval-certified bounds. Fixture-level convergence and the independent reference support the selected result, not all possible physical cross sections or future coupled stages.
5. No gas coupling, repeated projected evolution, full output-schedule invariance, long cosmological history, production performance, or 37-field acceptance follows from this review.

These are explicit stopping boundaries, not hidden passing requirements.

## Execution, resource evidence, and provenance

This reviewer ran **no numerical experiment, compilation, dependency installation, or solver history**. Read-only work consisted of source/log inspection, JSON evidence comparison, SHA-256 verification, and byte accounting. Requested adversarial regressions were executed by the implementation owner sequentially under the shared supervisor; their red/final evidence was then inspected independently. The sole reviewer-written artifact is this document.

Final supervised receipts show:

- `rustc --edition=2021 -D warnings -O src/tests.rs -o prototype`: exit 0 (`final_compile`).
- `./prototype`: exit 0; all 16 groups pass (`final`), empty stderr.
- `python oracle.py`: exit 0; selected-candidate PASS (`final_oracle`), empty stderr.

The complete new V2 numerical batch, including failed attempts, totals **37.062199 CPU seconds and 37.343219057023816 wall seconds**, below the frozen 120/180-second limits. The supervisor serializes children with a process lock, limits numerical address space to 512 MiB, and sets single-thread environment variables. Recorded RSS values are below the cap; the receipt uses a cumulative child high-water field and should not be treated as an exact isolated RSS measurement for each command.

The oracle has live-node instrumentation from its first V2 integral run, clears caches per integral, and records a conservative high-water bound of **2,157**, below 4,096. Source inspection supports the much smaller Rust quadrature-vector occupancy. File bytes immediately before this review were **5,043,029**, below 32 MiB. Aggregate output size is checked after runs rather than hard-limited cumulatively during every write; observed compliance is supported, not a universal hard-resource proof.

V1 remains exactly 102 files, with no unexpected or missing file relative to the inherited set, and every recorded byte hash matches. Its original PARTIAL verdict and retrospective first-oracle instrumentation gap remain historical facts. Later V2 evidence does not erase either.

Reviewed stable identities:

| Artifact | SHA-256 |
| --- | --- |
| `CONTRACT.json` | `efc6852072556006a2d77d7d82b71d1bdcea4c2c7a152d4970accb83198005b2` |
| `ARITHMETIC_ADMISSION.json` | `63f33460e60b6ca162ea92779bbfafd311cd030905e6365d23a3700a544b18a1` |
| `src/primitives.rs` | `62794f11c3cb24f52b99d349de00621617ed0841a59fa84f55e64ecbabfd2192` |
| `src/tests.rs` | `54ecd13091a8029c2fb75908d649f387119e5dde3adb29317aa8a907be281deb` |
| `oracle.py` | `77b87365ee8e10a0dc3ba1388f2b5312cad1e352bd676a2ebe70dd2cbff22df9` |
| `run_bounded.py` | `5636c9add3621e545afd52a534ee729741d5799c4c456eeb999512a5ae903559` |
| `results/HIGH_PRECISION_ORACLE.json` | `937efc8d78e8acef42dffe6774da9b5ef57773516d42e671e4624d99a0888b1f` |
| `RESOURCE_RECEIPT.json` | `bc6ee6303ea5da4598ee57789ec2775b124cb111d75f45414776ff37d55e5ece` |
| `FINAL_REPORT.md` | `be674e1c1cd1a44bcac9f85468c71ee959ab96d47d039168a4901e3411fbb883` |
| `RESULTS.json` | `058b2fe0f4a03f6ee85b30577405ca9bfa08de8c7664a2710c9fdc9a152f2968` |

The accepted result is the bounded V2 research record above. Any subsequent source change or integration needs evidence appropriate to that new scope.
