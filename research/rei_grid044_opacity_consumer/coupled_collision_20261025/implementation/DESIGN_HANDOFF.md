# Static design handoff for the named implementation worker

This file is a design handoff, not execution authorization. The parent reassigned final code and execution to a named lower-tier worker under the current AGENTS route. No scientific import, numerical test, profiler, or attempt has been executed by this design worker. The final Astra contract and independent pre-execution review supersede provisional details here.

## Scope and ownership

Consume the existing thirteen photoionization edges and selected twenty-one target states. The generic species/event compiler belongs to WU under the newly observed central source; do not create a competing generic compiler. The completed previous opacity response and all its receipts remain unchanged. This unit advances the instantaneous N3/N4 collision primitive and does not complete a coupled cosmic trajectory, original N6, physical n/T sources, thermal evolution, or a release gate.

Use `NUMERICAL_DESIGN.json` for proposed dimensions, checks, tolerances, and budget caps. The intended state is `z=(N[16], y[21], B, K, Xext)`, dimension 40. All entries are per reference particle; B, K and Xext carry eV per reference particle. B is a redundant ionization-energy coordinate, K is a primary-electron injection ledger, and Xext is the external photon-energy injection ledger. K is not gas temperature or deposited heat.

## Exact constructive operator

For each existing edge e=(l,u,c), let `R_ej = c_light*nref*sigma_c(E_j)*y_l*N_j`. Its dimensions are events per reference particle per second. Sum over packets to get R_e. Then

```
F_Nj = sum_s alpha_s*S_sj - sum_e R_ej - Lambda*N_j
F_y  = existing_incidence*R - Lambda*y
F_B  = sum_ej chi_e*R_ej - Lambda*B
F_K  = sum_ej (E_j-chi_e)*R_ej - Lambda*K
F_Xext = sum_j E_j*sum_s alpha_s*S_sj - Lambda*Xext
```

The collision derivatives are analytic bilinear derivatives in N and the edge's lower-state y. Include both photon-to-target and target-to-photon blocks, energy rows, and all normalization terms. For externally supplied Lambda and gradient at fixed nref, add `-Lambda*I-outer(z,grad_Lambda)` to the collision Jacobian. The derivative-test residual must recompute the same affine `Lambda(z)=Lambda0+g·(z-z0)`; holding Lambda fixed while checking the outer product is inconsistent.

Source-amplitude columns have photon entries S_s and Xext entry `E·S_s`; every other source entry is zero. At fixed normalized z and per-reference source templates, the nref parameter partial is the collision-only vector divided by nref. Do not claim support for an algebraically state-dependent nref or a physical-volume source held fixed without its extra chain rule.

Derive charge q and cumulative ionization energy epsilon from the exact existing target order and edges. Do not confuse upstream isotope order (Li7 precedes Li6) with selected target order (Li6 precedes Li7). Initialize `B=epsilon·y` consistently.

## Provenance of the finite fixture

Use actual unchanged MODEL_CONFIG source formulas at z=2, the eight exact threshold/branch intervals and GL2 in each interval. This gives 16 angular-integrated energy packets; local atomic cross sections depend only on E. Use the previously accepted continuous source normalizers exactly, without a new normalization integral. The resulting finite source sum is deliberately not renormalized to one: the saved GL2/continuous ratios are about 0.9968941924505704 and 0.9863501584763724. Report them and make no continuum accuracy claim.

Set `N_j=(1 second)*sum_s S_sj` solely as a local operator fixture. It is not a recovered free-streaming radiation spectrum and not an evolved cosmological population. Do not invert the saved donor cell moments. The actual frozen donor endpoint gives `nHref=5.151254745827818e-6 cm^-3=5.151254745827818 m^-3`, H=`6.62278836209097e-18 s^-1`, eta=`1.9459101490553132`, physical scale factor 1/3. This supplies an actual density/time context, not an exposure duration.

Positive test isotope populations may use the actual donor abundance labels and arbitrary explicitly disclosed charge fractions. Positive n/T test abundances, if inserted to exercise coordinates, are synthetic derivative fixtures and must never be described as physical relic predictions. A second actual zero-n/T fixture can establish structural zero collision coupling.

Inputs:

| Input | Path | SHA256 |
|---|---|---|
| Selected registry | `pilot/opacity_response_20261025/implementation/opacity_response.py` | `923d267b9823cb9f1c97ceb9101412c8a8582d496ec33c0541be670447e3d302` |
| Source config | `pilot/theory/MODEL_CONFIG.json` | `c680eff7d1eb3c3a0c9a8414135fe506441a59a8dd102dc54be01f1507037d71` |
| Continuous normalizers | `pilot/threshold_response_20261025/implementation/AGGREGATE_PAYLOAD.json` | `480ecfb72613bebf12cb9cd63e2f0bc567adaa03cf4e6a454696d69f08398fb8` |
| Frozen donor/source data | `pilot/donor_projection_20261024/implementation/AGGREGATE_PAYLOAD.json` | `32a5ecb284eceffa98d900d8669148392388b1ce4166dafef8c0b9b2e04fbfd1` |
| Actual provider loader | `pilot/opacity_response_20261025/intake/provider/atomic_network.py` | `6730e3091de918f693e02e40b0bdf1fefc543a5dcc4de23efd885ca098e2ed5f` |

The continuous normalizers are `[72.51288724958997,30.53311568359463]`. Bind the seven vendor files and their attribution/license as the prior opacity unit did. The provider loader imports NumPy and its own original provider; it avoids SciPy. The old opacity module imports SciPy, so extract its literal SPECIES/BLOCKS/EDGES statically or preserve an exact name-keyed registry binding instead of importing the whole old numerical module. This remains a fixed selected-edge consumer.

## Independent identities and derivative checks

For fixed packet energies, the energy functional is `E·N+B+K-Xext`, with no duplicate count of epsilon·y. Its residual plus Lambda times itself is zero. If the caller supplies E_dot, the total time derivative gains `E_dot·N`; this is geometry work, not a second collision source. The current 16-packet angle-integrated fixture does not reconstruct anisotropic transport or infer shear work from packet energy alone.

Each isotope sum obeys `sum(F_y_block)+Lambda*sum(y_block)=0`. The normalized electron derivative is `q·F_y=sum_e R_e-Lambda*q·y`; the physical reaction-source rate per reference is just sum_e R_e. The combined photon/electron number functional obeys `sum(F_N)+q·F_y+Lambda*(sum(N)+q·y)=sum(source)`. The redundant binding discrepancy obeys `F_B-epsilon·F_y=-Lambda*(B-epsilon·y)` including an intentionally off-constraint test.

The full coupled Jacobian is **not** Metzler: photon depletion differentiated by target abundance is negative. The fixed-radiation target block alone has the generator sign pattern. Nonnegative boundary preservation follows because all loss terms are proportional to the coordinate being lost and sources/gains are nonnegative. Test those statements separately.

The unit-exposure photons make absorption tiny compared with the injection source. For centered finite differences of the collision Jacobian, turn injection off, keep photons on, and set Lambda/gradient to zero. This preserves the desired Jacobian and avoids catastrophic source subtraction. Use complex-step with source on as a separate check. Check source columns separately; source-off with existing photons does not mean zero response. Recompute affine Lambda in every perturbed evaluation of the quotient test.

Do not normalize physical errors by `max(1,|value|)`. Scale Jacobian columns by frozen positive coordinate scales; scale each row by the sum of absolute analytic column contributions. Structural zero rows get their own explicit checks. Report photon-target, target-photon, target-target, and energy/source rows separately, so a missing tiny rare-isotope block fails. Identity residuals use positive gross event/power scales. Include an independent scalar edge/packet event loop, reference-density rescaling (`nref→k*nref`, `z→z/k`, `S→S/k`), and invalid-domain checks with no silent clipping. Complex-step input support must preserve imaginary perturbations.

## Execution and receipt requirements

For the final portable package, put runtime code and all small runtime inputs under the new unit with package-relative paths. Copy the exact fixed registry literals and selected provider/source inputs with their upstream byte bindings; avoid requiring the bulky prior tree or importing transitive old numerical modules. Preserve prior receipts/bindings as evidence. Root's current permitted Git addition is `research/rei_grid044_opacity_consumer/coupled_collision_20261025` against source `78f7ac5864d5817ceb79b48cb5e298cc30006510`; no existing file under that destination was observed by root. The eventual archive must include the small runtime inputs necessary to reproduce this check.

Five historical ledgers carry forward unchanged: donor_projection_20261024, birth_history_20261024, resolved_transport_20261025, threshold_response_20261025, opacity_response_20261025, each under implementation/TEST_BUDGET_LEDGER.json. Their exact cumulative totals are CPU 8.001104 s and wall 8.029615335010021 s; total source caps remain CPU 10 s / wall 20 s. No reset or fresh heavy budget exists.

Parent selected one CPU 1.0 s / wall 5 s attempt, integer RLIMIT_CPU 1 s, ITIMER_PROF 0.8 s, one process, all BLAS thread counts 1, 1 GiB address cap. All imports and numerical checks belong inside the measured child. Preserve raw wait4 rusage and exact pre/post byte snapshots. The old runner can be adapted with the explicit soft timer and carried fifth ledger; do not copy its automatic `attempt_cpu-.5` policy unnoticed. No profiler, unmetered smoke test, repeated historical integral, or auto retry is allowed.

Write authorization false initially. Root must freeze exact input bindings and authorize after Astra contract and independent pre-execution review. If an attempt fails, retain its output and charge it before considering a separately reviewed remaining-budget repair. Record actual global DAG progress and only claim the gates this operator fixture establishes.
