# Independent review: midpoint shared-owner theory

Date: 2026-10-07. Scope: source inspection and independent algebra. No new code, compilation, numerical probes or histories were run for this review.

## Archived original inspected versions

The following SHA-256 values identify archived originals inspected in this review, not the relocated publication bytes:

- METHOD_DERIVATION.md: `ee8ecfe79e61df962700ba48a077c3375b792ec9fd9d9349aed26bc329394f65`
- TEST_FIRST_CONTRACT.md: `624515044cc20396ea0f633a13bddc37868a0f7675374c0c9824a6b9062b15b1`
- ORACLE_FORMULAS.md: `6ac4d9b230f61ca8010be5d74de02c38207a2c87059c4447a8d830886acb3ac2`

Also inspected the frozen coupling contract/addendum, coupled.rs, radiation.rs, material.rs, event_anchor.rs, imported V2 primitives, original background/EOS/thermal/rate sources, and saved short-fixture temperature rows. All formulas in the hashed oracle supplement were independently checked, including its warning that a quadratic truncated oracle cannot isolate the candidate's cubic error coefficient.

## Verdict

**CONDITIONAL THEORY PASS.** The recommended four-unknown V1 residual, smooth coupled local-order derivation, shared number/species/energy identities, proper-time source conversion, and stated positivity/stiffness limitations are mathematically consistent. The focused tests correctly distinguish smooth local order 3, coupled-cutoff local order 2, fixed-finite-event global order 2, and unsplit jump-diagnostic local error O(h). They do not require every original field to converge at order 2 or every event-containing step to have local order 3.

**No outstanding theory blocker remains for the bounded V1 experiment.** The limited energy-oracle clarification identified during review is incorporated in these final versions. No numerical implementation, original-field acceptance, reference certification, Newton convergence, or actual new resource use is certified by this theory review.

## Confirmed qualifications

1. The radiation expansion includes both gas-dependent opacity feedback and within-step photon depletion/birth. Shared exact kernel owners are essential for the algebraic budget, independent of temporal accuracy.
2. The cutoff counterexample is correct: for the declared single-channel law, the global chord gives numerical-minus-exact x equal to `(k f0 v/2) alpha^2(1-alpha) h^2 + O(h^3)`. T6 properly treats this as a passing limitation test. Its m=1,4,16,64 fixed-event family keeps event phase 1/3; asymptotic factor-16 error reduction is conditional on a nonzero resolved leading coefficient.
3. The provider contains genuine jumps as well as continuous kinks. The saved fixture crosses the HeI CE diagnostic threshold near 190.785 K. T9 correctly excludes its indicator-valued cumulative diagnostic from an unconditional order-2 assertion while retaining every original absolute allowance. An instantaneous mask becoming zero does not imply the already accumulated diagnostic owner becomes zero; exact-zero checks apply only where the original contract requires them.
4. The energy defect from an inexact nonlinear root is `R_w + gradient(binding) dot R_fractions`, plus arithmetic/representation error. Fixed tolerances create a refinement floor. Conservation does not establish accuracy.
5. Midpoint q_s is a second-order approximation to the proper-time source. Exact continuous-source ledger replacement is forbidden unless the state and all owners are consistently changed. T4 preserves this distinction.
6. Positive radiation is conditional on admitted nonnegative frozen inputs; it does not ensure a physical gas root. Both the scalar midpoint sink and the purely photo-induced root-existence threshold are correct. Endpoint admission remains mandatory.
7. Inherited binary64 event anchoring and cross-transaction energy continuity remain explicit gates. Neither exact-real identities nor the within-transaction anchor establish bitwise cross-transaction continuity.

## Resolved test-oracle clarification

METHOD section 4 and T3 now correctly distinguish midpoint/count-energy replacements from a missing quadratic redshift term. In particular,

`B_mid = epsilon E_mid A`, with `E_mid = E0 exp(-h/2)`,

reproduces the stated B expansion through h^2 when A is correctly integrated. Therefore this forbidden replacement need not fail a quadratic-coefficient or order-2 test. It must fail the unchanged exact-kernel ownership/energy identity, using a resolved test interval. Start-energy weighting, by contrast, does lose the quadratic redshift contribution.

An exact frozen, q=0, single-channel check makes the distinction explicit:

- `A = lambda f0 j(lambda,h)`
- `B_kernel = epsilon E0 lambda f0 j(lambda+1,h)`
- `B_mid - B_kernel = -epsilon E0 lambda f0 (2 lambda+1) h^3/24 + O(h^4)`
- `j(k,h) = (1-exp(-k h))/k`, with its continuous k=0 limit.

The final contract requires rejection through the exact shared-owner tests rather than an incorrect Taylor-coefficient requirement. Keep the kernel's other owners unchanged when testing that replacement, and choose lambda, h and stock so this nonzero defect is above the existing identity tolerance. This clarification changes neither V1 nor the scientific acceptance gates.

## Execution conditions and remaining verification

- The bounded V1 experiment specifies a separate 120 CPU-second/180 wall-second numerical allowance.
- The new accounting cap counts at most 4096 distinct eta abscissae, with concurrent arrays recorded and the specified memory/output bounds. It does not retroactively cure the historical stored-values interpretation failure.
- All original 37-field, zero, spectral, nonlinear/domain, accepted-step number/energy, and resource gates remain mandatory.
- The saved admitted Radau result alone is not an admitted tightening pair. Reuse requires hash-verified identity of inputs, grid/nodes/weights, reference implementation and output coordinates, plus original admission evidence. Its new tighter companion and their mutual comparison must pass, or reference tightening remains UNVERIFIED.
- Any genuine physical-provider jump encountered by the new candidate requires the already specified narrowing of claims or a separately validated event-localization specification.

The reviewed theory can guide the bounded experiment. A failed gate remains PARTIAL/FAIL; no longer history or production conclusion follows.
