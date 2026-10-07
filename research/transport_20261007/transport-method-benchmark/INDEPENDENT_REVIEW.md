Publication note: quoted hashes identify archived original bytes; current publication hashes are listed in ../PROVENANCE.json.

# Independent review: collisionless FLRW transport comparison

## Verdict

**Numerical-method and ledger review: pass for this research-only diagnostic.** The recorded intended failures of FV energy compatibility, unlimited-DG positivity, and limited-DG energy compatibility are real observations, not implementation failures to conceal. No production-readiness conclusion follows.

**Historical resource compliance: fail for the original unbounded-cache oracle.** Its instrumented replay reached 4,369 live distinct cached/active abscissae against a 4,096 cap. The cache-bounded replay completed at 2,157 and reproduced the oracle file byte-for-byte. The original failure remains in `ORACLE_SITE_AUDIT.failed-v1.json`; the compliant replay does not make the earlier execution compliant.

This final report reviews the completed 234-row benchmark, its source-hardened replay, and nine green unit tests. The signed-slope/independent-flux and actual-stock-event coverage gaps found during the initial review have been closed. Final and original source/output snapshots are identified below.

## Independently checked equations and implementation

- The physical-energy representation is h=a+b r, r=2(E−m)/d. Exact moments are N=d a and U=m d a+d²b/6. The number and energy weak tests are **1 and E**, not 1/E.
- With one shared face flux F=−E h_upwind, the implemented coefficients give N′=−F_R+F_L and U′=−E_R F_R+E_L F_L−U. Interior faces cancel in the global sums. The lower boundary exports threshold energy, and the upper boundary supplies no inflow.
- Work is independent of the residual: characteristic trajectories integrate E_initial−E_current/crossing; partial panels integrate these same losses over the declared positive P0 reconstruction; FV/DG integrate U through the actual SSPRK2 stages.
- SSPRK2 accounting is correct. If the first stage limiter changes energy by δU₁ and the final limiter by δU₂, the accumulated change is ½δU₁+δU₂. Initial limiting is reported separately, with both pre- and post-limit initial-energy references.
- The positivity obstruction is genuine. An empty cell receiving number q dt from its upper face receives energy E_R q dt. Endpoint-positive P1 forces mean energy at most E_R−d/3; the mean-preserving slope limiter therefore changes energy by −q dt d/3 in this example. The negative-mean rejection is explicit, and no density floor or residual repair is inserted.
- Initialization is fair to each declared representation: common GL8 photon weights and common analytic normalization, with no per-method renormalization. Stock and unlimited DG share the projected N and U; partial P0 and physical-E P0 legitimately have different initial U and must be compared using their separately recorded initial errors.

## Independent execution and traceability

`python budget.py reviewer_metrics python reviewer_check.py` exited 0, using 0.060112 CPU seconds and 0.064785 wall seconds. The owner explicitly released the numerical-process slot before this serial standard-library-only audit. It ran no PDE solve and introduced no new spatial resolutions.

`python budget.py reviewer_final python reviewer_finalize.py` also exited 0, using 0.037378 CPU seconds and 0.065119 wall seconds. It independently compared all 234 original and final rows: only four non-runtime numerical fields changed, with maximum scaled difference 1.783×10⁻¹⁶. It verified the nine-test green evidence, exact final hashes, byte-identical bounded oracle, preserved original resource failure, and final ledger gates. Final maxima are 8.882×10⁻¹⁶ for number residual, 1.900×10⁻¹⁵ for compatible energy residual, and 1.544×10⁻¹⁵ for pre-limit-baseline limiter accounting discrepancy. The first-pass check also tested the post-limit baseline, giving the slightly larger maximum in the table below.

The audit recomputed metrics from scalar stocks, rather than trusting the saved residual columns. It verified 26 cases × 9 common epochs, matching the declared spatial and temporal matrix.

| Check | Independent result |
|---|---:|
| Saved vs recomputed residual columns | Exactly identical |
| Sum of 32 bin masses vs N | ≤7.78×10⁻¹⁶ absolute |
| Limiter change vs physical-energy residual | ≤1.66×10⁻¹⁵ normalized |
| Every method's number residual | Below 5×10⁻¹² gate |
| Stock, partial, unlimited-DG energy residual | Below 5×10⁻¹² gate |
| Stock, partial, FV, limited-DG negative mass | Exactly zero in saved epochs |
| Independent adaptive-Simpson oracle vs mpmath oracle | ≤5.48×10⁻¹³ absolute across N, U, Nout, Eout, W |

The independent Simpson check uses direct trajectory-loss integrals for W, not ledger subtraction. It corroborates the oracle at floating-point precision; it does not independently certify 60 decimal digits. The separate mpmath 60→80 digit check does that selected-value consistency check, with discrepancies below 10⁻⁵⁰.

## Material interpretation findings

At n=256, c=0.075 for time-stepped methods, maxima over the nine saved epochs are:

| Method | Cumulative number-outflow error | Physical-energy residual, pre-limit baseline | Negative mass |
|---|---:|---:|---:|
| Whole-node stock | 4.500×10⁻⁴ | 1.900×10⁻¹⁵ | 0 |
| Partial panel | 1.514×10⁻⁴ | 2.714×10⁻¹⁶ | 0 |
| Physical-E P0 FV | 6.081×10⁻² | 5.786×10⁻³ | 0 |
| Unlimited P1 DG | 1.020×10⁻⁴ | 5.428×10⁻¹⁶ | 2.618×10⁻⁴ |
| Limited P1 DG | 1.114×10⁻⁵ | 3.951×10⁻⁶ | 0 |

1. **Unlimited DG is physically inadmissible despite excellent ledger closure.** At n=256, s=0.4 it reports Nout=−1.46726×10⁻⁵; at s=0.9 it reports N=−1.02045×10⁻⁴ and U=−1.39414×10⁻³. These are not roundoff-sized effects. Negative density can produce signed, nonmonotone threshold export.
2. **Limited DG trades energy for positivity.** The drift is fully accounted for, including initialization, but remains a real physical-energy defect. At n=128, decreasing c from 0.15 to 0.0375 raises the maximum pre-limit-baseline residual from 2.310×10⁻⁵ to 3.474×10⁻⁵. Smaller time steps do not remove the P1 representation obstruction.
3. **Continuous L1 is a quadrature estimate, not a certified high-precision norm.** GL8→GL16 differences are around 0.8% for partial/FV and reach 1.65% for unlimited DG at some epochs. These differences must not be rounded away or described as a proved error bound. The absolute-value integrand has interior cusps. The exact-in-reconstruction 32-bin coarse-mass diagnostic avoids this evaluation issue but is explicitly coarse-grained, not continuous L1.
4. **The stock method is atomic.** Continuous L1 and density minimum are correctly inapplicable. `stock_min_weight=0` is correct for this frozen initial bump because many GL8 nodes lie outside support. The final source computes this minimum from the actual initial weights; the earlier hard-coded fixed-case value was replaced before the final replay.
5. **The baseline comparison supports only a bounded next step.** Partial panels reduce the saved outflow error relative to whole nodes while preserving positivity and both ledgers for their declared reconstruction. Limited DG is more accurate in some diagnostics but fails exact energy compatibility. No fixed-energy baseline demonstrated every desired property simultaneously.

## Resource and evidence boundaries

`RESOURCE_ACCOUNTING.md` correctly includes the transient initialization clone, duplicated cell faces, both stage flux vectors, and the distinction between 2,048 quadrature sites and 4,096 node-pair scalar entries. Initial stock sites are dropped before SSP stages. Rust's conservative 2,064 concurrently live physical quadrature-site estimate is below the 4,096 cap. Timing includes diagnostic/output work and is too small for a production-speed ranking.

Original unit coverage was narrower than the contract's stated arbitrary-slope/independent-flux coverage, and did not directly exercise the stock exact-threshold event. The final source adds Simpson-exact polynomial moment checks over 15 mean/slope combinations and three independent face-flux pairs, and directly tests the same `node` helper used by the benchmark before, at, and after its crossing. Nine tests pass. The helper and final source were inspected independently. All earlier failures and the original oracle resource breach remain in the evidence, regardless of remediation.

## Reviewed snapshot

- Derivation SHA-256: `8b422ccdc9b125eb2132d90926765240d111321e218763b4081d6721db5c463f`
- Final benchmark source: `c29e1ad09ac7bb5cc58a68e9c06eee46296764c8ec82eaedd19a3233df7053ff`
- Final tests: `9176575add15fdfa58434177783f9b45949037695dba6f44dc06f9439a80b1c5`
- Final results CSV: `11f8dbd46ba6bd8c9f2ecfb5aaf6c08dbd59eb3c12ae84cf5e7fcdef74c5a7a7`
- Preserved original results CSV: `12f0a2b4a7176d1a5b178c409406e8540c70a338b0a531be0b8903f99937db1f`
- Cache-bounded oracle source: `4c17e39b8ab85e4da9635741fc98c9823c447e454758603285515db3270a73c2`
- Oracle JSON: `3bd8fe9a168a7f16f26a224677cdfdcec80d3e61300f0a01fa7ffaeb2018bbe9`

Full first-pass per-case metrics and input hashes are preserved in `INDEPENDENT_METRICS.json`. The final verification receipt and hashes are in `INDEPENDENT_REVIEW.json`. Review code is `reviewer_check.py` and `reviewer_finalize.py`. The independent review did not alter solver state, tests, production code, or external services. The subsequently added projection/transport split received the targeted review below.

## Addendum: initial-representation versus numerical-transport error

**Targeted source review: pass.** `projection_split.py` analytically transports each fixed initial reconstruction solely to form a diagnostic reference, at the existing 26 cases and nine saved epochs. No evolving solver state, spatial resolution, or physical method is changed. The saved run exited 0, consuming 0.045776 CPU seconds and 0.064995 wall seconds. This targeted review required no additional numerical process.

For physical-energy transport, E(s)=E₀ exp(−s) and h(s,E)=exp(s)h₀(E exp(s)). Therefore exited number at s is the integral of h₀ from 13.6 to 13.6 exp(s). In a cell [E_L,E_R], the implemented primitive between E_L and q=min(E_R,13.6 exp(s)) is

N_exited,cell = a(q−E_L) + b[(q−m)²−(E_L−m)²]/ΔE,

when q>E_L, and zero otherwise. Differentiating this primitive gives a+2b(E−m)/ΔE exactly. P0 sets b=0; initially limited DG uses sign(b) min(|b|,a), matching the solver's initial limiter. The stock crossing test x≤s and partial-panel clipping also match the benchmark's declared representations. The same GL8 construction is reproduced, with floating-point evaluation differences of roundoff size rather than a substituted continuum distribution.

At every epoch, total outflow error is split as

(exact propagation of initial reconstruction − analytic pulse) + (saved solver outflow − exact propagation of initial reconstruction).

This is an algebraic decomposition; its assertion alone is not evidence that a primitive is correct. The characteristic mapping and primitive above were checked separately by source inspection. Component maxima need not add because they may occur at different epochs and signed contributions can cancel. The second component includes spatial discretization, time integration, and subsequent limiting; it does **not** separately identify their contributions.

At n=256, the saved maxima are:

| Method | Initial-representation contribution | Subsequent numerical-transport contribution |
|---|---:|---:|
| Whole-node stock | 4.49972×10⁻⁴ | 2.78×10⁻¹⁶ |
| Partial panel | 1.51401×10⁻⁴ | 3.33×10⁻¹⁶ |
| Physical-E P0 FV | 1.64602×10⁻⁴ | 6.06415×10⁻² |
| Unlimited P1 DG | 1.00370×10⁻⁶ | 1.02045×10⁻⁴ |
| Limited P1 DG | 1.00370×10⁻⁶ | 1.15493×10⁻⁵ |

**Ledger closure relative to a method's own U₀ does not rank continuum accuracy.** At n=256, the partial-panel initial energy differs from the analytic pulse by 5.06134×10⁻⁶ relative to true U₀, despite its 2.714×10⁻¹⁶ own-U₀ ledger residual. This initial bias is comparable in magnitude to limited DG's 3.95146×10⁻⁶ ledger defect, but they describe different errors and cannot be substituted for each other. A fair interpretation must display initial energy errors, continuum outflow errors, and coarse-mass errors beside the conservation/positivity figure. This split further confirms that exact transport of a chosen initial reconstruction is not exact transport of the analytic bump.

The script releases each initial grid before constructing the next, retaining at most 2,048 initial GL8 sites. It uses only Python's standard library and the existing oracle file; no new quadrature refinement or PDE solve is performed. This addendum does not change the disclosed historical oracle-resource failure or the continuous-L1 quadrature caveat.

- Projection-split source SHA-256: `92d18dc4a34fbf6b2d309c791586b70a28d77413fc1fc500322f98fb2f7d46cf`
- Projection-split JSON SHA-256: `b236aac80c1c8eb0ed1f5c68fc28f58dff488dd1c817ab0bbd78dd71ae3bbe4f`
