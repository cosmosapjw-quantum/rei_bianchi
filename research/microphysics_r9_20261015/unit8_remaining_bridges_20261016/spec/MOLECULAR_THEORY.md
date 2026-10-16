# Unit 8 lane B: actual LiH nuclear motion and reused LTE emission

Authority requested Astra; observed model identity UNKNOWN. This contract consumes saved electronic results and actual public molecular data. It adds no electronic-structure rerun, NCP work, product integration, reaction coefficient, or unprovided continuum boundary condition.

## Two executable calculations

1. Solve low-lying nuclear motion on the existing neutral LiH X1Sigma+ counterpoise curves, and calculate allowed bound-bound E1 emission from their actual permanent dipoles. Report electronic-basis, interpolation, finite-domain and nuclear-mass-convention sensitivity separately. These are finite-curve predictions, not precision physical molecular constants.
2. Reuse the complete ExoMol CLT 7LiH state/transition files to recompute partition sums, optically thin LTE spontaneous emission per molecule and level lifetimes. Compare selected low levels and lines to calculation 1 without fitting or forcing agreement. This supplies a literature-conditioned radiative quantity now; no collider rates, LTE population evolution, chemical formation rate or cosmological cooling history is inferred.

## Actual inputs and electronic-model boundary

Saved source root is /workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/ncp_results/runs. Use molecular_v1/LiH_{cc-pvdz,aug-cc-pvdz}_R{2,2.5,3,3.2,3.5,4,5,6,8,12}, exactly ten points per basis. Each receipt must have finite_model_numerics_passed=true, molecule=LiH, the correct R and basis, and a matching data_sha256. Extract V_CP_Eh from receipt and dipole_ea0[2] from data.npz. Check atom charges [3,1] and positions [[0,0,-R/2],[0,0,R/2]]. Save a compact input table, source identities and raw checks; do not copy the large CI arrays into a new result. After this first verified extraction, portable reruns may consume inputs/laneB/lih_curve_inputs.csv and its extraction manifest, checking the compact table's exact recorded SHA256. In that mode record original_NPZ_recheck=NOT_AVAILABLE when absent and extraction_source_checks=historically_recorded; do not claim a fresh original check. An available but mismatched original must fail, never silently trigger portable fallback. These curves already contain nuclear repulsion and have a fragment-counterpoise zero, so add neither nuclear repulsion nor atomic energies a second time. The signed dipole uses the same molecular orientation at every point; do not take its absolute value before integration. A global sign reversal leaves intensities invariant, while pointwise sign changes do not.

The primary interpolant is PCHIP separately for V and dipole on [2,12] a0, with no extrapolation. The comparison interpolant is the ordinary not-a-knot cubic spline through the same ten values, with no smoothing or added point. Curvature is not resolved by this sparse grid; interpolant differences are a measured model sensitivity, not a confidence interval. In particular PCHIP flattens its slope at a sampled minimum. Preserve this limitation rather than claiming physical vibrational precision from a converged radial mesh. cc-DZ and aug-DZ are separate models; do not extrapolate them to a complete-basis answer. Existing cc-TZ points at R=3,3.2 and LiHe aug-DZ points remain diagnostic source evidence and do not define full additional potentials.

## Radial Hamiltonian and bound-state calculation

For X1Sigma+ (electronic Lambda=0), write the full nuclear wavefunction as u_vJ(R)Y_JM(Omega)/R. Normalize integral |u|^2 dR=1. In atomic units:

    H_J = -(1/(2*mu))*d2/dR2 + V(R) + J(J+1)/(2*mu*R^2).

Take mLi_atom=7.0160034366 u, mH_atom=1.00782503223 u, u/me=1822.888486209. Primary approximate nuclear masses in electron-mass units are mLi=mLi_atom*(u/me)-3 and mH=mH_atom*(u/me)-1. Electronic binding mass defects are omitted explicitly. mu=mLi*mH/(mLi+mH). This changes nuclear motion, not the clamped electronic curve, and supplies a genuine isotope-specific kinetic term. It does not include diagonal BO, nonadiabatic, relativistic, hyperfine or finite-size corrections. As a sensitivity run use atomic masses without subtracting electrons; do not call either convention a complete nonadiabatic treatment.

For J=0,1,2 compute the lowest three eigenpairs on [2,12] a0 with homogeneous Dirichlet endpoints. Let N equal intervals and h=10/N. On interior grid points the symmetric tridiagonal matrix has diagonal 1/(mu*h^2)+Veff(R_i) and offdiagonal -1/(2*mu*h^2). Use scipy.linalg.eigh_tridiagonal with select='i', select_range=(0,2), retaining normalized Euclidean eigenvectors q; radial u=q/sqrt(h). Primary N=4000, refinement N=2000. Require eigenvalue residual, orthonormality, ordering and mesh agreement. Set eigenvector signs only for reproducible output; all physical line strengths use squared matrix elements.

The boundary test is essential: no short-range repulsive continuation or asymptotic dispersion coefficient is invented. For every state report edge probability in [2,2.1] and [11.9,12], and probability outside [2.1,8]. Recompute the same lowest states on [2.05,12] and [2,8] with h<=0.0025 a0. A level is a localized bound candidate of the interpolated finite-curve model only if E<0, both edge probabilities<=1e-5 and both domain energy shifts<=1e-5 Eh. Failure does not erase the finite-box calculation: label that level DOMAIN_SENSITIVE and do not present it as a localized physical level. Even passing this diagnostic is not a rigorous bound on all possible unknown R<2 continuations. Do not count all negative finite-box states as the physical bound-state count or infer near-dissociation scattering information.

For each J=0 state, Bv=<1/(2*mu*R^2)> in Eh is also useful; compare 2Bv to the computed J=1 minus J=0 spacing, reporting the centrifugal-distortion difference rather than imposing equality. Energies for comparison to ExoMol are relative to E(v=0,J=0) within each model. Absolute negative E remains separately recorded against the model's CP fragment threshold.

## E1 emission and rotational factors

For all initial states v=0,1,2 and J=0,1, include every lower-energy final state with v'=0,1,2 and J'=J±1 (available final J up to2). In this selected low-v space these are all allowed downward X-state rovibrational final levels for those initial states. The electronic dipole function includes electronic and nuclear terms. Its radial matrix element is M_if=integral u_f(R) D(R) u_i(R) dR, approximated by q_f^T diag(D) q_i on a common mesh. The upper-M averaged, lower-M summed angular factor for Sigma–Sigma transitions is max(Ji,Jf)/(2Ji+1), with |Delta J|=1 and no J=0→0 line.

With DeltaE>0, d_if=M_if*e*a0 in SI and omega=DeltaE*Eh/hbar:

    A_if = omega^3 * |d_if|^2 /(3*pi*epsilon0*hbar*c^3)
           * max(Ji,Jf)/(2Ji+1).

The result has units s^-1. Derivation: the vacuum dipole-emission factor multiplies the squared radial matrix element and the rotational line-strength sum; averaging over the initial 2Ji+1 substates produces the denominator. Nuclear-spin degeneracy does not appear in a single level's A. Compute Gamma_i=sum_f A_if and tau_i=1/Gamma_i for Gamma>0; for the radiatively dark ground state store tau=null and dark_state=true, never numerical infinity. Report that these lifetimes omit radiation pumping, collisions and other electronic states. A sign-flipped entire D curve must give identical A, and forbidden transitions must not enter the sum.

## Public reference and LTE spontaneous emission

Actual downloaded inputs are under inputs/laneB/exomol_CLT. The current ExoMol CLT dataset page explicitly supplies levels, Einstein coefficients, partition and cooling tables, not a machine-readable PEC/DMC. The files contain 1086 states and 18982 transitions. State columns are id,E_cm-1,g_tot,J,v; transition columns are upper_id,lower_id,A_s-1,nu_cm-1. The definition file's max_energy=20000 is metadata, whereas the actual maximum level energy is 25822.962 cm^-1; record this discrepancy and use the actual rows. All rows have g_tot=8(2J+1). The constant nuclear-spin factor cancels from normalized populations and cooling; preserve it in the reported partition sum.

For betaE=hc*100*E_cm-1/(kB*T), w_i=g_i exp(-betaE), Q=sum_i w_i, p_i=w_i/Q. Define DeltaE_ul=hc*100*(E_u-E_l), using the state-energy difference as authoritative. Check it against the rounded transition wavenumber to2e-4 cm^-1. Group the spontaneous power by upper level, P_u=sum_l A_ul DeltaE_ul. Then

    L_LTE(T)=sum_u p_u P_u
            =sum_lines p_u A_ul DeltaE_ul.

Compute both orderings independently. L has units W per molecule; multiply by1e7 for erg/s per molecule. It is the all-direction spontaneous power, with no 4*pi factor. Report isotropic per-steradian power only if separately labeled L/(4*pi). Finite-density cooling needs an excitation model, abundance, optical escape and radiation field; none are inputs here. The ExoMol tables already include the physical literature model's corrections; do not relabel them as results of the saved R9 finite electronic basis.

Use T=[10,30,100,300,1000,3000,5000] K plus the reference cooling-table temperatures<=5000 K. Evaluate Q at integer .pf tabulation temperatures for the selected integer grid. Compare to supplied .pf (four decimal rounding) and .cf (four significant cooling digits and one-decimal T). The latter T rounding alone gives about0.95% difference at10.9K, so its formatting tolerance is2%; this is not a numerical integration tolerance. Primary line-sum vs grouped-sum agreement is1e-12 relative. Report the largest comparison residual and its T. The published dataset's finite state/line list is the exact computational object; the calculation cannot certify completeness beyond it. Quantify the fraction of partition population with E>15000 cm^-1 and its fraction of spontaneous power at each T, but do not treat that as a rigorous omitted-state bound.

Compute all reference state radiative lifetimes by summing the provided outgoing A, then extract the same low-v,J comparison set. Reference low levels include E(0,1)=14.8251, E(1,0)=1360.4770 and E(2,0)=2676.0667 cm^-1. These numbers are comparison outputs, not tuning targets or acceptance thresholds. The public CLT rotational A(0,1→0,0)=0.011787 s^-1 similarly provides a useful independent check of rotational normalization without requiring the coarse R9 potential to match it.

## Acceptance and stopping rule

Exact data/input identity and units are checked first. Nuclear solver gates: orthonormality<=1e-10, eigenvector Euclidean residual<=1e-9 Eh, energy refinement<=2e-6 Eh, and relative A refinement<=2e-3 for A>=1e-8 s^-1 (absolute1e-10 s^-1 below that). Domain localization is a per-state scientific qualification, not permission to suppress a result. The two interpolants, electronic bases and atomic/nuclear mass conventions are sensitivity comparisons with no forced agreement gate. Cooling gates: counts1086/18982; mapped unique state IDs; positive A and downward gaps; degeneracy8(2J+1); frequency residual<=2e-4 cm^-1; Q reference relative<=1e-4; .cf formatting relative<=0.02; independent power-sum relative<=1e-12; normalized populations within1e-13. Numerical wall budget30s, one BLAS thread, no external code build/install. Store raw failures and return once for theory interpretation; never relax a gate or invent a curve.

PASS→independent scientific review and release of finite-curve rovibrational/E1 results plus the literature-conditioned LTE table. Physical T3 reaction rates remain open for the explicit reasons in the dependency map.
