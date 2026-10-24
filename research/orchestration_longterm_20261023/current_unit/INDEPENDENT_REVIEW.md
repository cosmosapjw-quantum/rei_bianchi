# X1 independent review

Reviewer: atomic_survey. Read-only independent mathematical and implementation review; no IVPs, old tests, or scientific execution by reviewer.

## R6 / PHYS-MATH — PASS_SCOPED

Read thermal/X1_FROZEN_CONTRACT.md, X1_THEORY.md and X1_WOLFRAM.json. Direct independent argument: positivity follows from v^T S v=integral epsilon(v.n)^2 dmu; trace follows from unit directions. The spectral measure has weights2lambda_i/K summing to2 and each energyK/2; its moment equalsS. AtK=0 positivity forces all eigenvalues0, and counttwo zero-energy support realizesS=0. Paired antipodal directions preserve second moment and cancel first moment. No eventwise electron/recoil correlation is supplied by this construction.

Rayleigh bound0<=a^TSa<=K gives -K/2<=D<=K. Both endpoints and the stated convex mixture are correct. The axial diagonal entries reproduce traceK and quadrupoleD. Sum lambda_i^2<=K^2 yields Frobenius norm squared<=2K^2/3; the stated K3,Tdiag(-1.1,.55,.55) counterexample obeys that norm bound while S has negative eigenvalue-.1. These are elementary exact implications within the unrestricted inclusive-measure class, with no novelty/strong-no-go claim.

The COM ledgerK+Kp=E-I is correct under the explicitly stated nonrelativistic additive-mass collision convention and common outgoing COM frame. Moving to lab energy or rate averages requires its separate map. D7 atE10,I2,Kp2 violates the finite-mass upper6 even though the heavy-target upper8 would allow it.

## C9 / PHYS-MATH-CODE — PASS_SCOPED

Read moment_cone.py and test_moment_cone.py before execution receipt. Exact principal-minor logic, independent fixture oracle, immutable JSON text, source nonmutation, finite domain/shape guards, tri-state distinction, cancellation ratio and source uncertainty separation are appropriate. Ordinary float equality cases remain indeterminate; this conservative behavior is intentional, not a defect requiring tolerance relaxation.

F1 concrete implementation issue: Frobenius norms using unscaled numpy.linalg.norm can overflow on finite input energies (e.g.1e200), yielding inf and causing strict JSON serialization to raise. Finite1e308 sums can also overflow. Requested one targeted changed-path repair from coder: scaled/robust norms or explicit finite numerical-domain guard returning INDETERMINATE with raw input preserved; no broad replay. Await final code and bounded receipt before admission.

## Final review addendum — authoritative FINAL API adopted

Read the final freeze addendum, final moment_cone.py and test receipt. It replaces proposed generic epsilon/eigensolver enclosures with exact Fraction certification of represented numbers; numpy eigenvalues are diagnostics only. The final API has PASS/FAIL/INDETERMINATE, represented_input_only=true, explicit exact_input versus default source_rounded mode, and separate uncertainty qualification. No automatic integer-mode switch remains. A positive source uncertainty conservatively yields INDETERMINATE. This is a justified clarification before first numerical invocation, not a post-failure threshold relaxation.

F1 CLOSED before first Python invocation: exact arithmetic governs acceptance, eigen diagnostics use scaled matrix, tensor norm uses normalized math.hypot, and unrepresentable optional magnitudes serialize as labelled JSON data. Two large-finite fixtures pass without exceptions or source mutation. The exact7-principal-minor method is necessary and sufficient for symmetric3x3 PSD; optional polynomial D, axis and energy identities use the same exact represented arithmetic.

Read raw_outcomes.json and raw_stdout.txt:32/32 fixture decisions and all recorded assertions PASS; CPU0.57530726s,wall0.575546264s, within CPU10s/wall30s. Independent explicit determinant/minor oracle agrees on7 exact fixtures. Overflow guards, nearzero source-rounded ambiguity, exact negative PSD rejection, finite-mass bound and cancellation are represented in actual outcomes. The first shell launch had missing /usr/bin/time exit127 before Python execution; its separate preserved log is environment/prelaunch failure. One successful Python invocation; no old-suite replay,IVP,benchmark or reviewer execution.

Opened moment_cone.png directly with view_image. Both plotted feasible wedges, isotropic/parallel/perpendicular points and finite-mass D6 versus rejectedD7 agree with formulas. Axes clearly declare common fixture energy; title states no eventwise momentum sufficiency. Labels/legend are readable, no material clipping. This is a formula-only illustrative figure, not a new empirical result or solver campaign.

Final decision: R6/PHYS-MATH PASS_SCOPED and C9/PHYS-MATH-CODE PASS_SCOPED for standalone represented-input cone gate. Empirical angular calibration, eventwise momentum correlations and HE runtime admission remain separate obligations. No additional test or repair requested.

Reviewed identity SHA256: moment_cone.py `27e12d543e9a985380a6c3e501933588d56541889a050a9f67504c952bb2a46a`; test_moment_cone.py `396cd676723e7d27e0b9b943c1df55b9b0972df279657294a937d1fd5367a970`; raw_outcomes.json `fb04fb877c5d2fb040f64f14b762351d58663e7a01c76735b26fec69ec18607c`; moment_cone.png `b8d0f97e8b01a629c6826f638b5b46d11e5b4830d3f4b2fc0a895a33502e2d7c`. Receipt records181 passed assertion predicates across32 fixtures; these are not181 independent scientific cases.
