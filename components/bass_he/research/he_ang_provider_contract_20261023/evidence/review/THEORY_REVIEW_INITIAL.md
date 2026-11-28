# HE-ANG independent theory review — initial

Reviewer: `/root/heang_independent_review`; no contribution to the theory author's derivation or the implementation. Workflow 1.0.0 / approval 0.2.

**Initial decision: analytic derivation accepted within scope; two interface clarifications remain open before final R6 PASS_SCOPED.** No scientific program was executed by this reviewer.

## Reviewed artifacts and method

Read `heang_theory_contract/ANGULAR_PROVIDER_DERIVATION.md`, `PROVIDER_CONTRACT_PROPOSAL.json`, and `WITNESS_SPEC.json`; read the root unit's `CONTRACT.json`, `BUDGET.json`, and `CLAIM_GATE.json`. Reused the HE38 finite-mass convention and HE-X1 final contract, independent review and stored 32-fixture results. The preparation input identities are recorded separately.

Independent checks used direct outer-product expansion, measure pushforward and elementary delta-function elimination. This is read-only mathematical review; it does not count as executing a fixture, empirical provider scan, or independent rerun of HE-X1/HE38.

## Accepted derivation

1. **Finite-mass shell and count convention.** The common COM shell has zero summed outgoing momentum and kinetic energy `E−I`. A count-one event measure gives a count-two inclusive electron measure and count-one proton measure. Ordered exchange bookkeeping preserves the event count. The derivation correctly distinguishes that bookkeeping from quantum exchange interference.

2. **Five-coordinate root and Jacobian.** After `qp=−q1−r n2`, the energy equation is `A r²+B r+C=0`, with `A=(1/m+1/M)/2`, `B=(q1·n2)/M`, and `C=A|q1|²−(E−I)`. Expanding the kinetic energy independently gives these coefficients. The radial delta integration contributes `r²/|2Ar+B|` for every physical nonnegative root; the stated degenerate-root obligation is appropriate. The separate momentum-to-energy measure factor is `m|q1|`.

3. **Pressure-type raw moments.** The draft uses `R_s=<sum qqᵀ/m_s>`, so `K_s=tr R_s/2`, `S_s=R_s/2`, and `J_s=STF(R_s)` have the correct factors and units. In this notation `R_p=(m/M)R_e+C12/M`. The review preparation document used the distinct unscaled momentum-square convention for its own independent calculation; no factor from that convention is transferred into this draft.

4. **What the inclusive electron distribution fixes.** At fixed incident energy and conditional event normalization, conservation gives `Pp=−Pe` and `Kp=E−I−Ke`. The missing pair correlation is the traceless part of `C12`. The draft explicitly makes this distinction, and it permits an equivalent same-law moment certificate rather than demanding event samples in every implementation.

5. **A/B witness.** Direct expansion gives `q1q1ᵀ+q2q2ᵀ=p²(aaᵀ+bbᵀ)` in both ensembles. Their full inclusive one-electron measures agree by sign/azimuth changes, not only by equality of second moments. The ion tensors are `2p² aaᵀ/M` for A and `p²(I−aaᵀ)/M` for B. Hence `Dp,A=Kp` and `Dp,B=−Kp/2`. Each event obeys the same energy and momentum shell. Exchange symmetry follows from `b→−b` in A and `s→−s` in B. Continuous axial symmetry and the fourfold exact quadrature are correctly distinguished. The latter is exact for the stated degree-two moments; it is not asserted to be a continuous angular distribution.

6. **Frame mapping.** Expanding `q'=O(q−m_s U)` gives the stated `P'` and pressure-type `R'`. In particular the quadratic term is `m_s N_s UUᵀ`, and this term remains in signed reaction-source transformations. The stationary-target relation `E=ζ E_lab` is consistent with the inherited reduced mass. A cross-section's incoming parameter relabeling has no energy-density Jacobian. The outgoing DDCS pushforward factor `|q'|/|q|` follows from `d³q=m|q| dε dΩ`; zero-momentum coordinates are correctly left to a measure/bin formulation.

7. **Uncertainty and partial support.** A missing event measure of mass bounded by `Δσ` at fixed available energy `W` gives `0≤ΔKs≤W Δσ` and `||ΔRs||op≤2W Δσ`, because the missing `R_s` is PSD and its trace equals twice the missing kinetic energy. This requires an actual missing-event-mass bound, as stated. Physical source uncertainty, covariance and coverage remain separate from numerical quadrature, represented-input arithmetic, and the historical HE38 model gate.

8. **Claim boundaries and reuse.** X1's exact PASS/FAIL/INDETERMINATE API is retained. The new result is a constructive contract with physical source selection pending. It does not claim a calibrated hydrogen law, a global exclusion theorem, or completion of the HE-CLOSURE/feedback dependencies. Historical scientific execution and budget records are not reset.

## Findings requiring a small clarification

### F1 — Normalize the machine-readable recoil reconstruction

- **Object:** `PROVIDER_CONTRACT_PROPOSAL.json` → `representation.normalization_allowed` and `moment_interface.ion_reconstruction`.
- **Evidence:** the representation permits `conditional_event` and `cross_section_weighted`, while `K_p` and `trace_C12` contain the conditional formulas without an explicit conditional-only tag. The prose derivation Eq. (10)/(12) is correct for its declared `dP` convention.
- **Impact:** a downstream consumer copying the machine formulas for sigma-weighted moments could subtract a cross-section-weighted `Ke` from a bare energy, creating a unit and normalization error.
- **Minimum correction:** introduce event-measure mass `Z`, equal to one for conditional events and `sigma` for cross-section-weighted moments, or separate the formulas by normalization. In the general convention use `Kp=Z(E−I)−Ke` and `tr C12=2M Z(E−I)−2(M+m)Ke`. The linear momentum and tensor reconstruction formulas keep their existing form, and counts become `Ne=2Z`, `Np=Z`.
- **Initial status:** OPEN; textual/machine-contract correction only. No scientific rerun needed for this algebraic clarification. Changed implementation should later carry a sigma-weighted control.

### F2 — Keep source preparation in the rate kernel's arguments

- **Object:** `ANGULAR_PROVIDER_DERIVATION.md` §2 versus Eq. (30).
- **Evidence:** §2 permits `sigma(E,a)` and explicitly allows polarization/preparation parameters; Eq. (30) displays only `sigma(E)` without stating rotational invariance at that formula.
- **Impact:** a downstream rate integrator could discard an admitted directional/preparation dependence.
- **Minimum correction:** use `sigma(E,a;preparation)` in the general rate formula, with `a=g0/|g0|`, or explicitly restrict the displayed `sigma(E)` formula to the admitted rotationally invariant preparation. The existing relative-speed factor and Galilean argument are correct.
- **Initial status:** OPEN; clarification of the declared generality, no numerical execution requested.

## Completion conditions for this review

Read the corrected files, record their immutable hashes, and close F1/F2 at the specific corrected formulas. With those changes the theory contract is ready for R6 PASS_SCOPED. Independent implementation review remains a later C9 obligation.
