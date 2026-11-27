# HE36 kernel review and independent Cartesian controls

## Decision and role provenance

**PASS_SCOPED_KERNELS** for the pinned incoming-loss implementation and finite-source moment module. No blocking mathematical or implementation defect was found in their declared scopes.

Reviewer `/root/he_latest_synthesis` authored a separate derivation of the incoming-loss formulas and then independently reviewed implementations authored by other agents. The6D oracle integrates incoming velocity moments without using the derived2×2 coefficient formula. This is independent implementation verification plus an independent derivation relative to the root's provisional formulas. It is not described as a fresh non-author review of this agent's own DERIVATION.md. Root event/source assembly and final plots were not yet available at this review snapshot and are outside this kernel decision.

## Pinned implementations

- `maxwellian_moments.py`: SHA256 `644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c`.
- `reactive_moments.py`: SHA256 `49104bb9244af92f707f83b489f217a0573566b2d9f3e5154366b7d35eaaab89`.
- The frozen review contract precedes the new oracle execution and sets relative gate2e-11.

## Independent finite-mass verification

Six new controls use two finite mass/density ratios and K(E_rel)=K0(E_rel/θ)^q for q=0,1,2. Both species have non-diagonal, non-coaligned STF perturbation directions. The oracle directly constructs the two independent Maxwellian Cartesian velocities and integrates m_s vv times the incoming kernel and the Grad first variation. Each of six Cartesian dimensions has five Gauss–Hermite nodes, giving15625 joint nodes per control and93750 total joint nodes. Every integrand has polynomial degree at most8 in each coordinate; the ideal five-point rule is exact throughdegree9, leaving numerical arithmetic error in this manufactured control.

The oracle compares number source, each species' kinetic power, each species' STF source and full pressure source. The maximum relative difference is **7.46229818803753e-14**, below2e-11. The scalar number/energy contribution of the STF first variation is zero analytically; its largest normalized numerical residual is **8.700012365530878e-16**. All six controls pass. Measured wall after imports is0.16086018198984675s, with peakRSS28464KiB. This is one new finite algebra/quadrature process, no trajectory or benchmark.

The comparison uses physical-unit masses/densities/temperatures in the API but manufactured microscopic kernels. No physical nuclear or atomic rate is inferred from these controls. The raw reference tensors and individual errors are in CARTESIAN_LOSS_RESULT.json.

## Adversarial source/code inspection

1. **Finite-mass algebra passes.** Direct center-of-mass/relative-velocity contraction confirms the cross coefficient `C=ab(alpha−2k1+k2)`, including its possible negative sign. The code preserves that sign and does not treat it as a probability rate. The positive-term determinant identity and determinant/high-root eigenvalue evaluation agree with the exact derivation.

2. **Moment admissibility is necessary only.** The implementation checks positive moments and the scaled Cauchy inequality without forming overflowing alpha*gamma or beta². It retains roundoff-level input differences rather than clipping. These conditions do not establish a physical cross section or its domain/uncertainty. The code and docstrings preserve that qualification.

3. **Boundary and zero semantics are explicit.** The final code requires a declared reason for an all-zero supplied moment triple. Partial zero moments are rejected. A source provider's underflow is not such a reason. Zero-density species must have zero pressure perturbation; the weighted-symmetry/dissipation proof is stated only for positive densities, and boundary spectra are algebraic continuations.

4. **Frame conversion passes.** The centralization formula contains `+m*Rn*u*u^T`, required for variable particle number. Fixed-density elastic centralization from HE35 would omit this term; HE36 correctly retains it. Existing implementation receipts include a one-step algebra and Galilean-boost witness that distinguishes an omitted-number-term mutant. These existing checks were read, not rerun here.

5. **Finite source convolution passes within its stated numerical scope.** The separate MOMENT_SOURCE_REVIEW.md records the SI normalization, positive finite-bin quadrature, immutable source/domain identity, fixed-kernel moment derivatives, extreme-scale handling and the preserved conditional-mean correction. Existing CCC GL16/GL32/independent integral checks were reused by identity. They measure numerical convolution of a declared finite table, not physical omitted-tail or interpolation uncertainty.

6. **Linearization boundary is explicit.** The API requires `linear_response=True`. An optional Grad amplitude budget is identified as a caller diagnostic, not a truncation or positive-PDF guarantee. The cold finite CCC source selects suprathermal particles; a large κ2/alpha ratio is an event-selection derivative, not a calibrated full CI anisotropy relaxation rate. Finite-amplitude use would need validity control in the reaction-weighted velocity tail.

7. **No complete reaction operator is implied.** Each Q returned by binary_loss is removed-parent kinetic energy, including the center-of-mass share. Product birth, scattered survivors, photons, recoil, nuclear daughter energies and stopping are separate source inputs. Without them the net reactive Q/J and energy conservation of a full process remain unestablished. The implementation states this clearly.

## Actual execution and reused evidence

This review executed exactly one new6-control Cartesian quadrature process. It did not rerun the moment author's8-group baseline/affected mean fix or the pair author's10-group checks, and it did not run any old HE32/33/34/35 IVP, renderer or benchmark. Their preserved receipts and source hashes were inspected. The earlier independent exact-rational theory checks are separately owned by `/tmp/he36_theory_independent/CHECKS.json`; they are not counted again here.

## Remaining unit-level review boundary

The generic event ledger, nuclear particle-count/reservoir adapter, final actual source outputs and rendered figures are separate root deliverables. This kernel decision cannot certify files that were not yet available. Their final readback/review can be added without replaying these unchanged controls.
