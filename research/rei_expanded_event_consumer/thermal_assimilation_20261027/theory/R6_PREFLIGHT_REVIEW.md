# R6/R8 pre-execution review of the root-selected thermal join

Date: 2026-10-27. Decision: **PASS_WITH_SCOPE**, incorporating the clarifications below in the execution freeze.

Review target: the root's accepted Planck-reference branch, independent prescribed \(\nu_*=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\), manufactured \(\zeta=q^TY/4,\ w=\zeta K_J/\Gamma\), native Mao-hybrid/DR cooling join, and the root's five preflight corrections. Method: read-only equation/source/interface review; no new symbolic or numerical execution. Reviewer is the theory author reviewing the root's amendments and is independent of the forthcoming implementation; this document does not relabel self-review as a second independent proof. Existing Wolfram exact checks and separately recovered supplier/source evidence are reused.

## Findings

1. **Nuclear and coefficient domain.** Require zero neutron and both tritium populations in the accepted state and every controlled perturbation; corresponding tangent entries are zero. Assemble only photo + thermal RR/DR. Native decay matrices or whole native dY/dt must not introduce weak processes. The inherited REC coefficient domain100..10^6K remains enforced. The actual14919.8638K snapshot and proposed tiny temperature variations lie in that domain.

2. **CMB equilibrium control.** At actual a, the selected Planck temperature is about9.48K, below the REC coefficient domain. The T=T_rad zero-power/nonzero-temperature-derivative test is therefore a **Compton-helper-only limit test**. It must not call the joint REC/Mao coefficient evaluation and must not be reported as another admitted actual joint state. At fixed bath, the native power is zero there while its temperature derivative remains finite and nonzero for positive thermal electron density.

3. **Normalization of a nonzero thermal row.** Multiply only the first24 density-like source coordinates by n_b or beta. The log-temperature row is unchanged under those output maps; divide every row by H for the eta clock. This differs materially from the old photo-only zero thermal row. For reference-state input directions, transform all reservoir directions as well as Y:
   \[
   \delta Y=(\delta x-Y\delta\beta)/\beta,\quad
   \delta\zeta=(\delta\xi-\zeta\delta\beta)/\beta,\quad
   \delta w=(\delta\omega-w\delta\beta)/\beta,
   \quad\delta\beta=A^T\delta x.
   \]
   The external ledger has the same density-coordinate transformation, although its value does not affect this source. A coherent physical reference direction uses \(\delta n_b=r\delta\beta+\beta\delta r\); for fixed r0, \(\delta r=-3r\,\delta a/a\). Independently declared API parameter derivatives may be tested separately, but their coordinate meaning must remain explicit.

4. **Changing reference.** If selected, apply the reference-source correction and its derivative only to normalized density-like rows:
   \[
   F_x=(S-xR_r)/r,\qquad
   \delta F_x=(\delta S-R_r\delta x-x\delta R_r)/r-F_x\delta r/r.
   \]
   There is no \(-\ell R_r/r\) term. The fast-energy pressure-work term belongs to its physical evolution owner; the source-only quotient exercise must not infer that work. The external radiation coordinate is a signed transfer ledger, not an evolved photon density with an assumed redshift law.

5. **Native supplier ownership.** Call ThermalSources.coefficients() and actual Grr/Gdr with \(n_{e,\rm th}=n_b(q^TY-\zeta)\). Preserve signed DR fit amplitudes and numerical-zero/structural-zero masks. Do not use ThermalSources.evaluate(), which includes prompt primary heat and the all-thermal count. The reused photo helper's native RR/DR side outputs still use total charge-electron density; they must not become the new thermal RR/DR components. For the unchanged HE caloric sink, the electron source is \(n_b(q^TR+\nu\zeta)\), while ion rows use \(n_b(P+R)\). The photoelectron birth is not also added to the thermal-electron row. Report photo, RR, DR, relaxation and Compton energy partners separately before their single aggregate ledger sum.

6. **Finite-difference step and failure interpretation.** Freeze the one mixed direction with dimensionless normalized magnitudes<=0.1 and h=2e-4, giving perturbations<=2e-5 in those coordinates. Preserve isotope/baryon constraints and zero n/T entries, and keep the declared \(\nu\) variation independent from the clock H variation. Preserve the inherited2e-8 criterion. Direction size alone is not a rigorous bound on FD truncation for steep rate fits, so a failed comparison is an observation to diagnose, not grounds to loosen tolerance. The authorized h=1e-4 repeat should use the same direction/inputs and retain both results. Approximate fourfold reduction is informative only when truncation dominates; rounding or cancellation can change that ratio. Two tested steps establish directional FD consistency within the frozen scope, not full physical/trajectory convergence.

7. **Residual scales.** Define analytic/JVP identity scales using the sum of absolute contributing terms with matching units, including separate event/power contributions. Do not normalize by a nearly cancelled signed total or max(1,tiny). If all contributing terms are exactly zero, test that structural zero explicitly. Define the FD source/JVP row scale before execution and retain it for both steps. This is particularly necessary for the thermal-count/energy cancellation and the changing-reference/H controls.

## Scientific conclusion and positive next action

The selected equations conserve ionic nuclei/baryon count, total free-electron partition and binding + fast + thermal + external-radiation energy, with the same ownership in their derivatives. The finite relaxation is a stated conditional operator on arbitrary energy measures, and the current native thermal bath/cooling assumptions are explicit. The positive nonthermal fixture makes the thermal-density and caloric corrections distinguishable.

**Next action:** root incorporates the coordinate/JVP-scale clarifications into the frozen bounded contract, then the mechanical executor implements the actual joint source and native HE/REC calls and performs the authorized changed checks. No additional theory search or symbolic rerun is needed before that action. C9 review should inspect the implementation, raw outcomes, source bytes and figure together.

This is pre-execution approval of the conditional construction, not numerical admission, calibrated physical stopping, continuous evolution, a new parent-node completion or L4 closure. Working canonical count remains32/88. Root retains the cumulative budget ledger, exact job limit and restoration policy; this review creates no execution allowance.

