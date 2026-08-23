# PHASE 6 PHYSICS AND MATHEMATICS VALIDATION LEDGER

Only the two serious candidates are evaluated. Status refers to the proposed research architecture, not the currently failing implementation. `CONCERN`/`NOT_YET_TESTABLE` permit verification design but prohibit solver/science promotion.

## H-001 — Active-face, verified, hybrid structure-preserving solver

| Check | Status | Validation result | Minimal repair / new assumption |
|---|---|---|---|
| Definitions and notation | CONCERN | “Closed cone,” “structural zero,” “trace,” “vacuum,” branch, event, and QoI are conceptually distinct but lack frozen quantitative ownership in the repository. | Freeze species inventories, carrier/vacuum criteria, event functions, branch priority, and QoIs before code design. |
| Units and dimensions | CONCERN | Opacity must be `n_s σ_s` (`1/length`); absorber shares are dimensionless; per-H/per-He rates require exactly one declared abundance conversion. Photon number, energy, ionization potential, heating/cooling/work, internal energy, and temperature cannot share one residual without unit conversions. | Produce a units table for every primitive flux/reservoir and dimensional tests for each ledger term. |
| Signs and normalization | CONCERN | Direct nonnegative shares can remove complement cancellation and must sum to one only when total opacity is positive. Current extra-`YHE` and tautological ledgers fail this check; proposed correction is algebraically plausible but unexecuted. | Specify zero-total-opacity behavior and compute all shares from one qualified nonnegative opacity vector; independent ledger path must not reuse its complements. |
| Symmetry/covariance | NOT_APPLICABLE | No spatial symmetry, gauge, or coordinate covariance claim drives this local thermochemistry solver. Species relabeling is not a physical symmetry because thresholds/cross-sections differ. | None. |
| H/He conservation | CONCERN | Stoichiometric left-nullspace/content-vector conservation is valid only after every closed reaction/source is bound. Open radiative energy/photon reservoirs require boundary terms; charge is signed and not automatically covered by nonnegative elemental content. | Derive and machine-check H/He content vectors branch by branch; separately specify charge/electron closure and open reservoir terms. |
| Known physical limits | CONCERN | Required: pure H, pure He I, pure He II, mixed opacity, zero opacity/emissivity, optically thin/thick, vanishing reaction, equilibrium, trace→0, and vacuum. Current pure-He II limit fails. Candidate predictions are coherent but untested. | Treat every limit as an independent oracle, including approach direction and expected scaling/order. |
| Boundary/initial conditions | CONCERN | Exact-zero faces are physical, but an absent species remains on a face only when all production into it vanishes. A generic implicit inverse or Patankar ratio can fill/stick zeros. | Derive invariant-face conditions and explicit activation/deactivation maps; forbid floors as physical states. |
| Convergence and regularity | NOT_YET_TESTABLE | Smooth-branch nonautonomous second order, face-transition order, defect stability, and event-time convergence are not established. Table knots and active-set changes break differentiability. | Prove/test smooth branch first; use separate jump/saltation/restart analysis and report order per regime rather than one global claim. |
| Positivity/realizability | CONCERN | Standard MPRK positivity applies to strictly positive states with qualifying rates/denominators; it is not exact-zero safety. Population simplex realizability also requires inventory preservation and finite thermal state. | Prove PDS, denominator asymptotics, content invariants, and each face system; adversarially test near-zero sticking/order reduction. |
| Algebraic certificate validity | CONCERN | Krawczyk theory can certify a root under outward operations, whole-box Jacobian inclusion, and strict self-inclusion. Current stack has signed-sum and two false-certificate witnesses. | Replace the entire arithmetic-to-consumer path; retain exact witnesses as permanent kill tests. Failure must be inconclusive, never success. |
| Continuous trajectory validity | NOT_YET_TESTABLE | An algebraic stage/root enclosure does not enclose the ODE trajectory or bound truncation error. Current full/two-half discrepancy supplies neither a defect nor stability/QoI propagation. | Construct a branch-correct differentiable/enclosed path and independently evaluate defect; derive stability/adjoint weights for named QoIs. |
| Event topology/restart | CONCERN | Simple isolated root theory is insufficient for double crossing, grazing, repeated, simultaneous, and near-knot roots. Polynomial-root completeness is not true-trajectory completeness without enclosed reconstruction error. | Combine true-path enclosure, all-simple-root isolation, explicit tangency/repeated-root falsifiers, authorized priority, rollback, rebuild, event iteration, and conservative reservoir custody. |
| Low-rank structure | CONCERN | Fixed smooth-branch nonlocal photo feedback factors through three global absorber sums, so rank `<=3` is supported. Full Jacobian factorization, nonsingularity, interval dependency, conditioning, and benefit are not. | Prove exact full factorization; verify base/Schur systems and use a dense certified fallback whenever thresholds fail. |
| Approximation ordering | CONCERN | PDS discretization, interval widening, continuous reconstruction, event localization, adjoint/QoI estimation, and asymptotic branch logic introduce different errors that cannot be hidden in one tolerance. | Allocate separate algebraic, truncation/defect, event-time, data/interpolation, and QoI budgets with a declared composition rule. |
| Regime of validity | CONCERN | Candidate is only coherent branch-by-branch under positive denominators, qualified arithmetic, valid PDS decomposition, and finite physical state. Vacuum/trace and table knots require explicit regimes. | Publish an admission-domain table and fail closed outside it. |

OVERALL_STATUS: `CONCERN — survives to decisive verification design only`.

FATAL_VALIDATION_STATE: No internal mathematical contradiction in the corrected architecture has yet been proved, but none of the composition assumptions is validated. Any false enclosure, ambiguous face transition, missed topology event, or independently over-budget QoI kills H-001.

## H-002 — Dual-lane independent physical admission and custody

| Check | Status | Validation result | Minimal repair / new assumption |
|---|---|---|---|
| Definitions and claim tiers | CONCERN | Forensic compatibility, code verification, numerical/solution validation, empirical physical validation, and scientific promotion must be distinct types, not prose labels. | Define non-coercible artifact/result types and an allowed-consumer matrix. |
| Units and dimensions | CONCERN | Admission predicates need explicit units/scales for residuals, photon number, energy reservoirs, event time, populations, temperature, and QoIs. Hashes/booleans cannot replace dimensional acceptance. | Bind unit schema and owner-authorized budgets to the exact model/version. |
| Signs and normalization | CONCERN | Independent reference/ledger construction must reproduce nonnegative share and reservoir sign conventions without importing candidate complements. | Freeze primitive sign/normalization equations and independently derive expected limiting values. |
| Conservation/physical validity | CONCERN | An admitted result must demonstrate H/He realizability and independent population/photon balances; full independent energy closure remains a gap. | Build separately accumulated reservoirs/quadrature and specify open boundary/source terms. |
| Known limits and special cases | CONCERN | Analytic pure-absorber/zero-rate/linearized/manufactured cases can verify code, but cannot establish empirical validity. | Require blind detection of known defects and preserve the claim-tier distinction in every output. |
| Boundary/initial/status conditions | CONCERN | Terminal statuses must be absorbing; event restart, resume, new generation, crash, partial result, and quota termination are distinct. Current source does not demonstrate the full matrix. | Specify and test a complete typed transition table with atomic writes/admission. |
| Regularity/convergence | NOT_APPLICABLE | Admission architecture itself has no discretization convergence order. Its referenced numerical evidence must carry method-specific convergence/uncertainty. | Do not aggregate verification levels into one score. |
| Positivity/realizability | CONCERN | These must be enforced as semantic predicates, not assumed from success/parity; exact-zero admissibility must match the corrected model. | Bind candidate-independent simplex/finite/domain checks and face/event custody. |
| Independence | CONCERN | Separate files/processes are insufficient; shared equations, constants, tables, generators, authors, and reviewers create correlated error. | Publish an independence graph; blind expected values; independently re-derive shared roots; forbid candidate-output-derived references. |
| Robustness/security semantics | CONCERN | Identity receipts authenticate only what consumers bind and enforce. Current runtime mismatch, passive parity, unbounded buffering, custody, terminal resume, and resource gaps remain. | Authenticated atomic fail-closed admission; descriptor-safe allowlists; dynamic library/tool/input binding; streaming quotas and quarantine. |
| Theorem assumptions | NOT_APPLICABLE | No single theorem validates custody architecture. Individual cryptographic, filesystem, process, and numerical predicates each need explicit contracts/tests. | Treat composition/consumer enforcement as the object under test. |
| Regime of validity | CONCERN | H-002 can prevent over-admission but cannot make H-001 correct or turn manufactured/reproduction evidence into physical validation. | State the ceiling on every admitted artifact and require separate physical-validation authority. |

OVERALL_STATUS: `CONCERN — survives as a verification/admission architecture only`.

FATAL_VALIDATION_STATE: Epistemic independence and fail-closed consumption are not demonstrated. Shared candidate algebra, lane coercion, passive/unconsumed receipts, or any partial/failure artifact admitted as success kills H-002.

## Phase-6 outcome

- Serious candidates validated: exactly 2.
- `PASS`: none.
- `CONCERN`: H-001, H-002.
- `FAIL`: none as abstract architectures; current implementation nonetheless contains fatal evidence and is not admitted.
- Both proceed only to minimal decisive verification design. This is not formalization or promotion.
