# Strong matter-stress extension: scientific contract

The executable contract is `STRONG_PI_M_CONTRACT.json`. This extension answers the user's additional question: whether the previously unresolved matter-stress response persists at substantially larger physically admissible initial stress. It adds five bounded IVPs in a distinct component family and preserves the previous results.

## R1 — Correct the inference before extending the calculation

The old largest tested positive matter stress was Pi_m0=0.0010937748691794015. The old statement about an unresolved ionic response applies to that cold-component family and saved numerical accuracy. It does not establish that matter anisotropic stress generally has negligible effects. A larger-amplitude test must respect the distribution's positivity and distinguish changing quadrupole from changing the component's pressure or energy density.

## R2 — Inspect the actual physical closure

The pinned `canonical_fv.py` represents a homogeneous, reflection-even, axisymmetric collisionless nonbaryonic distribution in conserved canonical momenta. Its radial weight is the decoupled Fermi–Dirac shape q²/(exp(q)+1), with angular factor

    W(mu) = 1 + A_m P2(mu).

The model normalizes its initial energy density using the actual positive momentum quadrature. It evaluates evolving density and pressures directly from those conserved packets and the metric, rather than imposing a fluid anisotropic-pressure closure. `prepared_moments.py` changes the algebraic evaluator, not the distribution or quadrature. The massive component does not supply baryonic electrons or change the atomic reaction coefficients.

The current `CompactTransport` already supports configurable `mass_fraction`, `mass_over_Tref` and momentum quadrature. The old `Coupled` constructor and `amplitudes_to_axes` adapter hardcode the cold parameters. The new adapter must pass the desired physical initial P_m into the configurable transport and record its model identity. Altering old source files or passing the new targets through the old hardcoded amplitude map is excluded.

## R3 — Positivity and the old family's strict range

Since P2(mu) ranges from -1/2 to 1, W is nonnegative exactly when -1<=A_m<=2. At the isotropic initial metric, angular integration gives

    rho0 = 1,
    pbar0 = (2 P_perp0 + P_parallel0)/3,
    pi_s0 = (P_parallel0-P_perp0)/3 = A_m pbar0/5.

Both rho0 and pbar0 are independent of A_m. The same identities hold to rounding in the chosen angular Gauss quadrature because the relevant polynomials are integrated exactly. Reflection symmetry makes the bulk velocity zero; it does not imply a small velocity dispersion.

Let F_m = H0² Omega_m/(a_ref³ H_init²). At zero initial shear, F_m=0.9936721814803131 and the stored dimensionless signed stress is

    P_m0 = 3 sqrt(6) F_m f_m (pbar0/rho0) A_m / 5.

For the original f_m=.1, m/Tref=30 component, pbar0/rho0=.004680992559898818 and P_m0/A_m=.000683609293237126. Its positive-orientation maximum is therefore .001367218586474252. Targets .01,.05,.1 would require A_m approximately 14.63,73.14,146.28 and violate positivity. This is a bound on this angular/radial family, not a universal bound on matter stress or an arbitrary positive distribution.

## R4 — Construct a distinct physically admissible matched family

Freeze f_m=.3 and m/Tref=3. Here Tref labels the nonbaryonic momentum scale, not the prescribed baryonic gas temperature. This component is semi-relativistic: the initial energy-weighted v²/c²=3pbar/rho=.5245200754155104. It is not the original cold component at a larger quadrupole.

The initial equation-of-state ratio is .17484002513850347. The actual nominal quadrature yields P_m0/A_m=.07660059131801567. Targets Pi_m0=(0,.01,.05,.1), all in the positive orientation, require A_m approximately (0,.13054729510486304,.6527364755243152,1.3054729510486305). The largest amplitude has minimum W=1-A_m/2 approximately .3473, well within positivity. The allowed positive maximum for this family is .15320118263603133.

Across this new family, initial total energy density, H, massive energy density, massive isotropic pressure, dust and baryon densities, radiation monopoles, initial gas fractions, and prescribed UV/gas-temperature histories are fixed. Only the quadrupolar shape changes. All initial shears and radiation stresses are zero. Energy normalization makes rho0=1 in each actual discrete model; verify rather than assume this from continuous formulas.

The new family's own zero-stress history is the required reference. Its isotropic pressure and composition differ from the old cold family. Comparing a strong new case directly against the old zero anchor would conflate anisotropy with the changed background component. Subsequent massive density/pressure histories and H may differ dynamically within the new family; only the specified initial quantities are held fixed.

## R5 — Measured point checks and source identity

Before any new IVP, bounded point evaluation verified the nominal coefficient and positivity range using the pinned source implementation. At m/Tref=3, A=0,1,2 all give rho0=1 and pbar0=.1748400251385035 to binary64 precision. The nominal 24x12-cell Gauss3 pressure differs from 48x24-cell Gauss4 by about 2.53e-10 relative. A 96x48-cell Gauss4 point value agrees with the 48x24 value at rounding scale. These are initial moment checks, not convergence evidence for an evolved trajectory.

The JSON records source hashes for the physical transport, finite-volume distribution, prepared evaluator, old coupled adapter, atomic coefficients/adapter source and background lock. The implementation receipt must add the new adapter identity and the actual source/rate identities inherited by execution. Preserve both target and measured initial physical axes; rounded amplitudes are not authoritative parameters.

## R6 — Bounded execution

Run four nominal histories with L16, the original 24x12 Gauss3 momentum quadrature, Radau rtol=2e-9 and atol=2e-12, max_step=.04, and 257 samples over z=20 to2. Run the Pi=.1 case once more with L24, 48x24 Gauss4, rtol=2e-10, atol=2e-13 and max_step=.02. Recompute its amplitude from the fine quadrature coefficient so the initial physical Pi is matched. This tiny quadrature-level pressure difference is measured and bounded, not hidden as exact equality.

The cap is five new background IVPs and 180 additional CPU seconds, including failed attempts. No old trajectory is rerun. No automatic sixth control, cloud-compute job or amplitude search follows a failure. Four new nominal histories may receive the already admitted conditional nuclear postprocessing; the control is for atomic/geometry comparison and need not receive a duplicate nuclear calculation.

## R7 — Physical and numerical acceptance

All actual initial fixed zero axes must agree within 1e-14, and target Pi within 1e-12. Within the nominal family, initial density, pressure and particle number agree relatively within 2e-12, as does H. Check continuous W and actual canonical packet/cell nonnegativity. Apply the existing finite-history, conservation, particle-number and angular-brightness checks unchanged.

The strongest-case control measures the response to a simultaneous increase in angular cutoff, momentum quadrature and solver precision. Its maximum absolute conditional-fraction discrepancy must be <=1e-7 for the stated numerical-agreement gate; geometry/time relative discrepancies and absolute signed stress/shear discrepancies have their separately specified 1e-7 gates. Passing these gates alone does not prove that a small physical effect is resolved.

## R8 — Answer the user's question through an observed scale comparison

For every nominal case, compute all nine conditional-fraction differences from the new hot zero anchor at common saved redshift. Report maximum absolute differences, their redshifts, endpoints, electron abundance and optical-depth differences. Preserve per-channel results rather than collapsing a dominant channel into a universal claim.

Let e_f be the maximum fraction discrepancy between the strongest nominal and control histories. Use e_ref=max(e_f,3.3929270504273745e-9) as a declared comparison scale, recording that the second number is an inherited different-family numerical-control discrepancy. It is not a mathematical error bound, confidence interval or probability of correctness.

A response at least ten times that observed scale can be described as separated from the observed control discrepancy within this conditional model. A response below the scale remains unresolved; intermediate cases are marginal. Also compare the strongest refined trajectory's effect against the same new zero anchor and verify the leading sign/profile agrees. If every new response remains unresolved, report that outcome only for the tested family, initial Pi<=.1 and numerical accuracy. If a larger response separates, explicitly withdraw any implication that the old cold-family finding was universal.

## R9 — Figures and dossier integration

Add seven PNG/PDF figure pairs: all nuclear totals and ionic groups on both redshift and elapsed-time axes, same-z ionic-fraction differences, signed geometry/stress context and the strongest-case control comparison. Retain the previous 28 figures. Use the earlier plot contract's absolute per-baryon abundance definitions and distinguish inherited ions from conditional nuclear totals. T charge partition remains unresolved.

The document must present the old positivity ceiling, the changed nonbaryonic component, the matched initial density/pressure, the new actual Pi range, the measured numerical comparison and the observed result. The hot zero versus cold zero comparison, if mentioned, is a composition/pressure comparison and not an anisotropy measurement. No observed-cosmology constraint is inferred from this exploratory distribution family.

## R10 — Finite stopping rule

Once the five runs, nominal postprocessing, seven figure pairs and one fresh scientific review are complete, update the dossier with the measured answer. A gate failure receives a concrete interpretation and raw-result preservation; it does not trigger an unlimited new verification campaign. One targeted non-IVP repair is permitted for implementation or presentation defects. Further IVPs require a new explicit scientific decision.
