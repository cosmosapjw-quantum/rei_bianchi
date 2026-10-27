# C5 independent implementation preexecution review

Date: 2026-10-27. Reviewer: `/root/normalization_review`.

**Decision: PASS_SCOPED_PREEXEC_IMPLEMENTATION. No blocking source or checker defect was found in the two files identified below.** This is a static review of the frozen conditional local source operator. It is not a numerical acceptance result and does not authorize execution before the controller's prescribed C5 checkpoint and GO.

## Reviewed artifacts

Paths are relative to `research/rei_expanded_event_consumer/thermal_assimilation_20261027/`.

| Artifact | SHA256 |
|---|---|
| `theory/ROOT_FROZEN_CONTRACT.md` | `d6db25daef4c89be9c85c268a5d21cb9aa8a3f34548068f2e76ee95bcd7019b3` |
| `implementation/thermal_join.py` | `a84f318d66c11166db080f0f4db64b48f82ea5bc09abb87671c2ca44b162bbb6` |
| `implementation/check_thermal_join.py` | `5832cb8062a0c8e46f7ca892ae3260328fedd89bd4dc74303bbc41e2a508acdb` |
| `implementation/run_bounded.py` — receipt amendment only | `e32add916b80df9e5e53933f50a29e5daa817701aa6b21e2b6ec3285ce946312` |
| `implementation/PREEXEC_MANIFEST.json` — final C5 input manifest | `8f55b02555bc2ef1797efa77f54ed7c185275a384985f01afd5b626dcb4544b2` |

The reviewer read the complete join and checker against the root contract and the previously inspected native provider interfaces. The reviewer contributed the preceding theory derivation but did **not** implement either reviewed code file. This therefore provides independence from the code author; it does not relabel the reviewer's own earlier theory work as a second independent derivation. No target import, scientific Python execution, provider suite, quadrature, IVP, spectral reconstruction, symbolic rerun or numerical test was performed for this review. Only source reads and metadata hashing were used.

## Findings

1. **Thermal population and native reuse are correctly separated.** The join uses `ne = nb*(q·Y-zeta)`, calls the actual `ThermalSources.coefficients(T)`, retains the native `Grr/Gdr` rate matrices, and forms their temperature derivatives from the native derivative coefficients. It does not call the native prompt-thermalization `evaluate()` method. The reused photo helper supplies the photo source/JVP; its all-electron RR/DR side diagnostics are not assembled into the new thermal source. The checker compares native matrix rates with the helper rates and preserves DR presence/zero masks.

2. **The conditional assimilation operator transfers both number and energy.** The assembled transfer is `j=nu*zeta`, `h=nu*w_nt`, with explicit independent `dnu`. Thermal particle count is `chi=(1+q)·Y-zeta` and its source is `count=q·R+j`. The log-temperature source is `(Q/(Cv*T)-count)/chi`, where `Q=h+qC-L`. Both the derivative of the caloric prefactor and the derivative of `chi` are present. The external photon ledger contains photo absorption once, the opposite Compton leg once, and each RR/DR escape term `L-I·R` once. Fast energy loses `h` exactly where the thermal ledger receives it. No empirical stopping rate, angular distribution or irreversible-assimilation provider is inferred.

3. **The actual HE caloric oracle is used with the intended pool.** Its rows contain 21 ion densities/sources and the thermal electron density/source only. Centered heat is `nb*Q`; expansion, shear and heat-flux-divergence inputs are zero for this source-only operator. Atomic binding, nonthermal kinetic energy and external transfer are listed as independent internal components rather than inserted again into the common-temperature heat capacity. The checker compares the returned HE `Tdot/T` and number/source totals with the new join.

4. **The Planck derivative has the correct density cancellation and scale-factor derivative.** The forward value calls the native `planck_reference_power`; the analytic JVP retains the thermal-charge derivative and the `Tr∝a^-1`, `Ur∝a^-4` terms. The independent oracle starts from physical `Qc` and differentiates `Qc/nb`, providing a distinct route for the density quotient cancellation. The `T=Tr` boundary is isolated to `compton_component`; it never evaluates REC coefficients at approximately 9.48 K.

5. **The mixed coordinate maps implement the frozen row distinction.** Physical and reference maps multiply only rows 0–23 by `nb` or `beta`, including the corresponding product derivative. Row 24 remains a log-temperature rate. The eta map divides all 25 proper-time rows by `H` and includes `-F*dH/H^2`. Reference-input tangents transform all 24 density-like coordinates and derive `beta`/`dbeta` from the baryon weights. The separate manufactured changing-reference control includes both `-x*Rr/r` and the complete differential, including `-F*dr/r`; it is explicitly labeled algebra rather than a new physical energy-work model.

6. **The planned checker is discriminating and bounded to the requested unit.** Its independent oracle assembles individual recombination transition fluxes rather than multiplying the new join's matrices, and derives the caloric differential from physical number and power. The FD path recomputes `r=r_star*(a_star/a)^3` and `nb=beta*r`, preserving the density relation throughout each perturbation. Both frozen step sizes use the same predeclared analytic contribution scales and the frozen `2e-8` tolerance. Algebra/native checks use `2e-14`; no unit floor or canceled signed total is used as a denominator, and zero scales require exactly zero operands. Controls expose all-electron rates, omitted assimilation count, wrong log-temperature density scaling, missing density/clock product derivatives and the limited validity of the constant-in-energy moment closure. Neutron/tritium state and tangent exclusions and the native 100–1e6 K joint domain are enforced.

## Receipt-only C5 amendment

After the complete operator/checker review, the controller requested inspection of the final runner's authoring-metadata amendment and binding to the final manifest. Both scientific file hashes above remained unchanged. The runner reads `preparation_metadata_process_CPU_s` from the frozen manifest and records it separately, then includes that subtotal once in the planning expression alongside the unchanged prior planning debit, vendor-copy debit and newly charged execution debit. The manifest and `AUTHORING_RECEIPT.json` agree on the two distinct observations `0.030587005` and `0.003790238` CPU seconds and their subtotal `0.034377243`; that subtotal is not present in the runner's separate prior-planning constant. Unknown historical/unmeasured work remains explicitly unknown. This receipt amendment does not change the scientific operator, checker, FD scales or tolerances. No blocking accounting defect was found in this inspected amendment; no additional execution or broad wrapper review was performed.

## Admission boundary

The reviewed source is ready for the one frozen new checker execution after the existing controller gate. No source repair or expanded test scope is requested. Runtime/resource enforcement remains the separate frozen wrapper/controller responsibility; this review does not claim to have executed or certified that wrapper. Numerical residuals, actual cost and outcome remain pending and must be reviewed from the preserved attempt output. A change to either reviewed scientific file requires identifying the changed bytes before treating this decision as applicable.

The intended result remains a selected conditional instantaneous source and directional derivative on the manufactured fast pool over the saved PW19 background. It neither establishes a measured finite-time stopping law nor admits a new integrated trajectory, whole-domain VigilODE property, original completion count, global physical completion or L4 completion.
