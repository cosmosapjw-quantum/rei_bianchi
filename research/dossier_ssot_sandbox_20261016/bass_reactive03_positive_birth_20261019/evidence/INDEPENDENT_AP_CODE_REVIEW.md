# Independent Rust review: BASS-REACTIVE-03

Date: 2026-10-19. Reviewer: independent rust_runtime agent. Decision: **PASS_SCOPED** for the source hashes recorded in `INDEPENDENT_AP_CODE_REVIEW.json`.

## Scope and evidence

All 97 inherited files match the recovered COMPLETE_SOURCE_SHA256 contract; this includes the 12 physical owner files and the BASS donor file (13 owner_src files total). The independent current execution of `cargo test --offline --locked --test ap_fitted_birth --test ap_bridge` passed 19 tests: 8 scalar and 11 bridge tests. Their final source/manifest hashes stayed fixed throughout execution. A formatting update to two files was detected after the first test run; the tests were actually rerun on the final bytes rather than inheriting the earlier PASS.

The tests cover positive quadrature, thin/thick constant opacity through tau=1e12, scalar zero-source and zero-opacity limits, species competition, native source geometry and Killing rays for both BASS shear signs, malformed-input and negative-population rejection, transactional behavior, native reaction ledgers, original OFF bit parity, four-corner controls, and original CX WorkLimit classification. Source-level exact-form comparisons are f64 tests; high-precision Python evidence remains independently necessary for numerical accuracy attribution.

The reviewer did not modify any numerical source, any original source, or the native/frozen study output directories. Evidence is in INDEPENDENT_AP_REVIEW_TESTS_FINAL.json/.log and INDEPENDENT_AP_SOURCE_DIFF.json. Native long-span convergence and upload/readback are outside this source approval.

## Construction and ownership

On a panel of width h and midpoint m, two ages m +/- delta have weights h/2. For z=tau*h/2 and tau*delta=acosh(sinh(z)/z), the analytic construction has exact mass h, exact first emitted-age moment h*m, and exact frozen survival h*exp(-tau*m)*sinh(z)/z. Positive z gives 1 <= sinh(z)/z < cosh(z), placing both nodes strictly inside the panel. The transparent limit is GL2. The implementation uses stable thin/thick evaluation branches and rejects unrepresentable nodes. The geometric-panel refinement separately controls the surviving-age approximation; exact scalar survival does not imply exact higher moments.

ApMidpointBridge::emit_births takes the original spectral/angular template, evaluates the source amplitude again at each represented birth geometry, and preserves emitted energy, direction, labels and the actual birth time. The amplitude ratio relative to the midpoint template is valid for this MD14/BB50k source, whose spectral/angular fractions are fixed while the common amplitude changes in time. Each cohort follows the existing Killing ray. The rule's midpoint opacity only selects quadrature nodes; propagation still evaluates the source-native opacity at actual ray energy and retains threshold splitting.

The source validation rejects malformed or unnormalized spectral/angular data. The generic zero-source mathematical limit is implemented without fabricating zero-output MD14 source objects; the native owner's positive-amplitude contract remains unchanged.

The entire photo method is identical to bound_midpoint modulo whitespace. The original competing HI/HeI/HeII/DI assignments, thermal excess, binding check and transactional photon/gas commit remain. The scalar reflection signature and exact-zero retirement also remain identical.

The JointCxSplit corrector preserves drift, first native CX half-flow, photo/non-CX correction, second native CX half-flow and final drift, including the same ownership flags and budget additions. The original drift photon-work subtraction and installation of transport work are retained. Exact ledger cancellation is accounting evidence, with the independent work quadrature kept separate.

The previous GL-predictor concern is closed: the temporary predictor now uses the same fitted births through OpacityOnly with predict=false. Its original first-order drift/photo/full_network sequence is retained and its whole ledger is discarded.

BirthMode::Off directly delegates to the original bridge/controller before new calculations. Both bridge state parity and controller raw-corner/scale/accepted-state parity passed.

## Controller wiring

ap_budget reuses the original public result/control types and calls the original read-only projections through a bridge adapter. config_at, projection, evaluate, absolute_tolerance, freeze, validate_controls, recoverable, physical_rejection and the complete four-corner decision tail are identical modulo whitespace. The adapter changes the solver type, adds direct OFF delegation, and records BirthMode in context identity. Thus the original controller files remain byte unchanged and the additive adapter retains their formulas and operation order.

The fitted four-corner test retained the initial state, used common scales for all four observations and committed the tight fine result. Cx(WorkLimit) retains its computational-budget meaning.

## Limits of this approval

- Exact AP survival applies to constant source and opacity. For a varying ray, birth-energy midpoint opacity is a quadrature-placement approximation. A birth energy with initially zero opacity can later cross a threshold under blueshift; original threshold transport remains, but a universal AP theorem for that case is not established.
- The unchanged four-corner projection does not directly monitor surviving-age moments; separate refinement comparisons are needed.
- Native varying-opacity, temporal, spectral and angular convergence, independent geometry-work accuracy and two-way Einstein feedback are not certified by this review.
- NoForwardProgress for an unrepresentable clock is a numerical-resolution limit, separate from CX WorkLimit and physical nonexistence.
- A root-reported native CSV/receipt persistence mismatch was not inspected by this source review and must keep its own artifact-recovery record.

No blocking implementation or ownership defect was found at the recorded revision. Scientific admission remains conditional on separately verified frozen-oracle and native-convergence artifacts.
