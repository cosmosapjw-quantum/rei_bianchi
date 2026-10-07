Publication note: hash declarations in this historical report identify archived original bytes. Relocated publication hashes are recorded in ../PROVENANCE.json. Some historical guard/run artifacts are summarized rather than copied; use ../README.md for the supported replay boundary.

# Independent bounded-prototype review

## Verdict

**PARTIAL. Do not promote this implementation to a coupled history or production solver.**

The final research report accurately separates useful analytic/normal-inventory results from failed numerical gates. The frozen contract was not relaxed. Two accuracy requirements remain failed, general near-empty panel admission remains incomplete, and the first oracle run has an unresolved retrospective live-sample-count gap. These qualifications prevent an aggregate PASS, while the contract explicitly permits an honest partial research result.

- **Specification:** partial. The reviewed fixtures establish the intended continuous-sweep and shared-owner mechanisms, but not every T1–T7 admission/accuracy requirement.
- **Engineering quality:** partial. The small standalone implementation is inspectable, its important failed gates are now exposed, and targeted tail-loss regressions reject. It is not a general-purpose safe panel API.
- **Claims/reporting:** the stable `FINAL_REPORT.md` and `RESULTS.json` are consistent with the retained final evidence. No coupled-history, 37-field, production, or speedup acceptance follows.

## Material unresolved findings

### 1. Narrow-support inverse reconstruction misses the frozen scaled-mean target

**High severity for further solver use; high confidence.** `src/primitives.rs:348–381`, especially the normalized target at lines 352–353, and `oracle.py`'s exact-input mean gates.

All ten tested approximately 1e-7-width cases fail the 5e-13 absolute scaled-mean target. The largest discrepancy is 1.6128156568442465e-9. The oracle interprets the authoritative binary64 N/M/L/R inputs exactly, then integrates the reconstructed density independently. Matching the internally rounded target does not establish matching those input moments at the required scaled accuracy.

The ordinary relative N/M round-trip test can pass because this small support width suppresses the visible relative M discrepancy. Its maximum 4.183e-16 residual therefore does not invalidate this finding. Wider tested supports pass the separate scaled-mean gate. The smallest next step is a separately bounded stable centered/scaled or compensated input-moment construction, or explicit rejection when the frozen gate cannot be met. Do not replace the input oracle with the implementation's own intermediate target.

### 2. Positive initial quadrature is conservative but insufficiently accurate at 64 subdivisions

**High severity for claiming the frozen quadrature target; high confidence.** `src/tests.rs`, `t7c_quadrature_target`, `results/initial_opacity_convergence.csv`, and the independent initial-opacity integral in `oracle.py`.

The 64-subdivision absorption error is 1.9104938742349023e-5 against the independent high-precision integral, exceeding the unchanged 1e-6 target. Comparison to the 512-subdivision diagnostic gives 1.8809283225607557e-5. The latter is correctly treated as a finite-resolution comparison, not an exact answer.

The original assertion incorrectly borrowed the 1e-3 reconstruction-bias threshold. Review required separating the quadrature gate and retaining its failure. The final suite does so: `T7c_quadrature_target FAIL`, exit 1. Positive moment construction and shared-owner identities are useful, but cannot substitute for this absorption-accuracy requirement. Higher-order/refined positive quadrature needs its own approved bounded validation; the report's extrapolation is not new acceptance evidence.

### 3. General near-empty initial-panel admission remains unsafe

**Medium severity within this isolated prototype, high severity if reused as a general solver API; high confidence from source inspection.** `src/primitives.rs:148–159`, `174–186`, and `202–205`.

`initial_transaction` skips a computed zero interval mass, and weighted owner aggregation does not propagate authoritative log information or detect every underflowed weighted contribution. A positive sufficiently small initial density can therefore disappear during moment formation or aggregation. This path is not covered by the new mixed-characteristic rejection guards. The final report explicitly identifies this as an unresolved admission defect outside the tested normal-inventory fixtures. General tail transport and conservative aggregate tail bounds remain unimplemented; no universal empty-state safety claim is justified.

## Requirements and supporting evidence

| Requirement/risk | Reviewed evidence | Result and boundary |
| --- | --- | --- |
| Continuous export for a smooth density | `initial_transaction` rebuilds swept-interval quadrature; T1 and T2 compare transparent controls and off-phase crossings | PASS for tested controls; intentional physical atom retains its jump |
| Genuine source-front zero trace | `density_value` contains `(1-y)` at every interior point, not just an endpoint override; T5 approaches the front from inside | PASS for finite tested beta/support; mathematical shape has zero interior limiting trace |
| Causal source support | Source entry/leave bounds and cutoff split in source transactions; exact source density is zero ahead of the front; T6 rejects a leaking support | PASS for prescribed source-only fixture; not a joined projected multistep history |
| Shared number/energy owners | One kernel supplies species count/energy, redshift, source and stock; `add_scaled` uses the same positive weight for all components | PASS for tested normal-inventory controls; no ledger repair or source rescaling found |
| Initial moment consistency | Analytic interval mass and energy moment determine weight N and eta=log(M/N) before owner evaluation; sample CSV contains moment residuals | PASS for tested density/splits; separate higher-moment quadrature accuracy FAIL above |
| Event topology and physical cutoffs | Sorted exact event deduplication preserves adjacent-float events; final T3b exercises HI/HeI/HeII with all rates positive | PASS for tested event cases; exhaustive near-coincident-event robustness is not established |
| Local analytic kernel | 84 declared cases, direct high-precision integrated histories, nonnegative heat checks and invalid-input controls | PASS for declared case matrix; not a proof over every finite input accepted by the function |
| Original zero-initial budgets | T4 independently audits stock, redshift, export and emitted owners with the frozen number/energy formulas | PASS; maximum allowance ratios 2.7538484e-6 and 6.3410755e-6 |
| Closure inversion and moments | Forward moment/root checks plus independent exact-input scaled-mean checks | PARTIAL: ten narrow-support gate failures remain |
| Tail retention/rejection | Kernel logarithmic readouts, explicit `Inventory::LogTail`, and final T5b regressions | PASS for targeted kernel/characteristic rejection paths; general panel transport remains unsupported |
| Negative controls | T6 corrupts outflow, cutoff energy, absorption energy mean, remap energy, source consistency and causal support | PASS as algebraic/owner negative controls; these are not end-to-end mutant solver histories |
| Separate reconstruction bias | T7b projects exact source moments and measures an E^-3 observable while varying panel count | PASS for that isolated observable: 1.0613606e-7 at 64 panels versus 1e-3 target |
| Resource and immutable-input contract | Receipts, supervisor inspection, final oracle instrumentation, and independent input hashes | PARTIAL for full historical resource certification; observed totals within caps and all frozen inputs unchanged |

The source-state and emitted ledgers use the same injected approximation. The source oracle's redshift reference is independently integrated from the time history rather than obtained by forcing the conservation residual to zero. Nonzero-initial identities remain separately labeled from the original empty-initial production budget.

## Findings corrected during review

1. The mixed characteristic originally discarded a source-free underflowed survivor's log metadata and advanced zero stock. The final boundary rejects an authoritative number or energy tail before aggregation (`src/primitives.rs:477–480`).
2. Positive-source underflow originally had no authoritative log marker. The kernel now rejects a positive-source, positive-duration zero survivor (`src/primitives.rs:110–111`).
3. Energy-only underflow now also rejects in the mixed characteristic. T5b includes all three cases. The red and final logs are retained.
4. The absorption-quadrature assertion now uses its own frozen 1e-6 target and reports failure, rather than borrowing the 1e-3 reconstruction target.
5. The closure oracle now checks the exact supplied binary64 moments separately from the internally rounded root target. The resulting narrow-support failures remain visible.
6. Source-order refinement now compares distinct orders (32 versus 64), backed by the independent source oracle, rather than accepting an order-64 self-comparison.
7. The final event regression includes all three absorbing species and their cutoff crossings.

These corrections improve the evidence. They do not erase the initial failures or turn the remaining gates into passes.

## Execution, provenance, and resources

To preserve the one-process numerical budget, this reviewer ran **no numerical experiment, compilation, dependency installation, or history**. Review commands were read-only file inspection, source/output inspection, SHA-256 verification, and file-size accounting. The sole written artifact is this review. Targeted regressions were requested from the implementation owner and executed sequentially under the shared supervisor; their final source, command receipts, and raw outputs were then inspected independently.

Final recorded commands/results:

- `rustc --edition=2021 -D warnings -O src/tests.rs -o prototype`: exit 0, empty compiler stdout/stderr.
- `./prototype` (`final` receipt): exit 1; ten groups PASS, T7c accuracy gate FAIL. The failure is expected evidence of an unmet requirement, not a passing test run.
- `python oracle.py` (`final_oracle` receipt): exit 2; 1,026 component/root checks pass, ten exact-input scaled-mean gates and one opacity-quadrature gate fail; explicit PARTIAL.

The final numerical receipt totals 56.095669 CPU seconds and 56.58035841301171 wall seconds, below 120/180 seconds. Compilation is separately measured. Directory size before adding this review was 5,110,046 bytes, well below 32 MiB. Per-process address-space limits are set to 512 MiB. The final oracle's instrumented conservative live-node high-water is 2,157, below 4,096; its quadrature error estimates are estimates, not interval-certified bounds.

The first oracle's live sample count was not instrumented and remains retrospectively UNVERIFIED. The later rerun cannot establish that earlier run's maximum. The final supervisor adds a nonblocking process lock and floors the remaining integer CPU allocation, but aggregate output is inspected after execution rather than prevented during every write. Observed compliance is supported; a universal hard resource-safety proof is not.

All eleven frozen source/design/evidence hashes were independently recomputed and matched, including the four production Python/Rust/comparator files. `CONTRACT.json` still hashes to `86750102c73889926e792575a3fe0acb2fa8214635a6178e8a0e80b76aa08f27`. No baseline mutation was found in that reviewed input set. This is not a repository-wide audit of unrelated work in sibling directories.

Reviewed final source identities:

- `src/primitives.rs`: `c0682b6fa150413b7192cd2506c76cf7d194b8a3a220e20864bd4bd9498e1f93`
- `src/tests.rs`: `a2c621947e5f0c0bc2db0ce6ac04ef7745f1e360d12ad98f28e9a423a15646bd`
- `oracle.py`: `a50af7874b0c130e796dbb3e95bd8532dfaacdbe40024746572132f70faf29ab`
- `run_bounded.py`: `5636c9add3621e545afd52a534ee729741d5799c4c456eeb999512a5ae903559`
- `results/HIGH_PRECISION_ORACLE.json`: `06f93266e013fdc1eecb7771e50661272812ada5fb2e107bb291589910a830d6`

## Stopping boundary

This review accepts the **honest partial research record**, not solver readiness. The next justified work is confined to the failed quadrature target, narrow-support input arithmetic, and fail-closed near-empty panel admission under a separate bounded authorization. A joined reconstructed multistep source/absorption history, gas coupling, full output-schedule invariance, all 37 fields, and long cosmological runs remain outside the demonstrated scope.
