# HE-ANG independent implementation review — preliminary

Reviewer: `/root/heang_independent_review`. Workflow 1.0.0 / approval 0.2. Review method: full read-only source and prepared-control inspection, independent hand evaluation of nontrivial expected values, and content identity checks. No implementation import, test run, old-suite replay, provider scan or scientific execution was performed by this reviewer. The reviewer role is observed from the team assignment; no separate model identity is asserted.

**Preliminary decision: no blocking defect found in the declared contract implementation scope. Final C9 PASS_SCOPED awaits root's actual bounded C6 control output and execution receipt.**

## Reviewed source

Source directory: `heang_code/`. Manifest SHA256:

`d1ab2796ef737f95de7e6e5d176b6f8336f51b3f2ec96c198feedd953136bac9`

Read all ten manifest-listed files: exact event/moment algebra, metadata precheck, CLI and package entry points, controls, manufactured payload/metadata, README and source version. The manifest verification is packaging evidence only; it is not a scientific execution receipt.

## Equation-to-code audit

| Target | Independent review result |
|---|---|
| `exact`, `vector`, `matrix`, `Event` | Explicit exact-number domain; binary floats and bool are refused; exact dimensions and nonnegative weights enforced without clipping. |
| `integrate_events` | Checks normalized event weights and each finite-mass COM momentum/energy shell before accumulating all particles. Electron sum has count two, ion count one. Pressure-type `R=sum(qqᵀ/m_s)` and `C12` factors agree with the reviewed derivation. |
| `EventMoments` | Enforces shared normalization, counts `2Z/Z`, COM momentum, the `Z(E−I)` energy ledger, and `Rp=(m/M)Re+C12/M`. This constructor is expressly an algebraic ledger check; finite-event support comes from the integrator. |
| `cross_section_weighted` | Applies sigma once to every moment, count and cross tensor; refuses double weighting. The corrected F1 normalization is implemented directly. |
| `zero_cross_section` | Constructs zero unconditioned moments directly, including below threshold, without manufacturing a conditional event probability. |
| `transform_raw` | Implements boost followed by orthogonal basis change using the pressure-type convention and signed reactive number term. It preserves normalization and kind, and refuses a nonorthogonal matrix without repairing it. |
| Serialization | Keeps rational values as strings, normalization and SI units explicit, with empirical admission and activation false. `C12` has units kg·J or m²·kg·J. |

The raw-moment container deliberately does not certify PSD or realizability of arbitrary tensors. This is stated in both code and README, and it avoids relabelling the raw transform as an HE-X1 gate. The event integrator's positive supported finite measure supplies its own direct algebraic support evidence.

## Independent expected-value inspection

The code's two manufactured eight-event ensembles have `m=1`, `M=3`, `kappa=1`, `E−I=8/3`. Direct outer-product summation gives `Re=diag(1,1,2)`, `Ke=2`, `Kp=2/3`, and `De=1/2`. The ion tensors are `Rp,A=diag(0,0,4/3)` and `Rp,B=diag(2/3,2/3,0)`, giving the listed STF tensors. The complete discrete electron histograms agree with eight support points of inclusive mass `1/4` each.

The prepared sigma-weighted example at `sigma=3/2` gives `Z=3/2`, `Ne=3`, `Ke=3`, `Kp=1`. The separate collinear example with `m=1`, `M=2`, `E=3`, `I=1`, `sigma=3` has `Ke=Kp=3` and `tr C12=6`, so the corrected cross-section formula is tested away from the witness's zero cross-trace special case.

For the prepared nontrivial boost `U=(1,2,0)` and 90-degree z rotation, independent matrix multiplication gives `P'=(4,−2,0)`, `R'=[[9,−4,0],[−4,3,0],[0,0,2]]`, `K'=7`. The one-particle signed loss with `m=2,N=−1,P=(−2,0,0),R=diag(−2,0,0)` transforms at `U=(1,0,0)` to zero first and second moment; this exercises the signed number term. These are prepared expectations, not executed outcomes in this report.

## Provenance and admission audit

- Four components bind to a common source, event law, preparation and angular-source identity, with actual byte SHA256 comparisons. This protects consistency and stale-input handling; it is not treated as source authentication or proof of empirical truth.
- The inherited X1 algorithm pin/evidence is distinct from the current candidate's moment digest and its analytic or separately recorded certificate. The example's candidate PASS is identified as a new analytic application to positive supported events, with no X1 execution. The old 32-fixture receipt is not relabelled as execution on this candidate.
- X1 PASS/FAIL/INDETERMINATE and `represented_input_only`/source-uncertainty qualifications are retained as records. FAIL rejects; INDETERMINATE remains deferred.
- Metadata returns structural readiness only. Missing actual bytes, uncertain error calibration, frame/root/Jacobian dependencies, partial coverage and missing correlations remain visible. Every status has `empirical_admission=false` and `runtime_activation=false`.
- Rate metadata retains `sigma(E,a;preparation)` except under an explicit declared unpolarized isotropic preparation. This implements corrected F2 at the contract level.
- Metadata reference strings are checked for presence/form, not for scientific content. Exchange, physical domain, source masses/threshold, missing-domain uncertainty and root evidence still require independent physical source review. A metadata-ready declaration therefore cannot activate a physical provider.
- The CLI reads bounded files/events, rejects duplicate JSON keys/nonfinite constants, confines bound paths to the declared payload root, and executes only the manufactured COM discrete-event schema. It matches its known payload identities, units, mass/threshold, normalization and energy-domain declarations before integration. Physical data formats remain outside this fixture executor.

## Prepared affected-control coverage

The source supplies new controls for event support, expected first/second moments, full discrete marginal equality, normalization, nonzero cross-trace, boost/rotation, signed reaction counts, zero cross section, malformed exact values, frame and payload metadata mismatches, digest/source identity corruption, missing data, partial coverage, X1 candidate binding, and CLI return behavior. Their expected values use direct declared contracts and hand-computed rational results. They import no HE-X1 or HE38 module or suite.

No additional broad suite or old-science rerun is requested. Root's C6 output should preserve actual per-case expected/actual values, exit status, the executed source identity, and the charged fresh cumulative CPU/wall ledger. Final C9 will read those results and any failure-specific correction, if one is required.

## Scope held open

This implementation is an executable exact fixture and structural supplier contract. It does not numerically reconstruct a real DDCS, solve five-coordinate coalescing roots, validate the scientific content of citation strings, or calibrate a physical angular law. Those are explicit source-input dependencies in the current unit, rather than claims of this preliminary code review.

Open code findings: none identified. Actual C6 execution and final C9 verdict: pending.
