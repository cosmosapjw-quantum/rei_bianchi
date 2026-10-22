# Thermal and radiation closure contracts
Date: 2026-10-22. Evidence: DERIVED under the assumptions below. Source baseline: 5a1e5220b301a1c497f2863d6fd823e605faba80, descendant of requested 215d5c33a9a6fc9940ead91c29128f2c6f20b5b2. This is an additive theory checkpoint; the preliminary atomic admission and production status are unchanged.

## Conventions and component ownership
Use (-,+,+,+), physical proper time in seconds, energy in J, number density in m^-3, c and k_B explicit. In non-tilted LRS Bianchi I with a geodesic nonrotating comoving tetrad,
H_perp=H-s, H_parallel=H+2s, sigma=diag(-s,-s,2s).
For pi_X=diag(-p_X,-p_X,2p_X), sigma:pi_X=6 s p_X.
Keep gas, massive nonbaryonic matter, and radiation stresses separate. Isotropic gas has pi_g=0; pi_m and pi_r need not vanish.

The homogeneous no-heat-flux energy equation is
d epsilon_X/dt + 3H(epsilon_X+p_X) + sigma:pi_X = Q_X.
Positive Q supplies component energy. The general projection with heat-flux and acceleration terms is Ellis & van Elst, Cosmological Models, section 2.2.2, equation (35):
https://arxiv.org/abs/gr-qc/9812046v5
https://arxiv.org/pdf/gr-qc/9812046
The source uses geometrized units; this note uses physical energy density and physical time.

## Changing particle number and temperature
For a nonrelativistic monatomic one-temperature mixture,
u=3 n_part k_B T/2, p_g=n_part k_B T,
dot n_part+3H n_part=S_part=S_heavy+S_e.
Atomic ionization changes S_e; nuclear reactions can change both sources. Substitution in
dot u+3H(u+p_g)+sigma:pi_g=Q_kin
gives
(3/2)k_B n_part dot T+3H n_part k_B T+(3/2)k_B T S_part=Q_kin-sigma:pi_g,
and therefore
dot T=-2HT-T S_part/n_part+2(Q_kin-sigma:pi_g)/(3k_B n_part).
Each term has units K/s. With zero particle source/heating/stress work, T scales as a^-2. A common temperature requires thermal equilibration; otherwise species energies must be evolved separately.

## Electronic, kinetic, photon, and nuclear energies
Define positive stored ionization energy relative to each neutral ground state:
B=sum_j n_j chi_j_cumulative, chi_j_cumulative=sum of successive thresholds.
Then dot B+3HB=sum_j chi_j_cumulative S_j=Q_B.
This is a positive ionization reservoir, not negative binding energy. Excited states require their own reservoir unless complete cascades are prompt. Rest-mass conventions must avoid counting the same electronic energy twice.

For photoionization with photon E, threshold chi, and event rate R:
Q_kin=(E-chi)R, Q_B=chi R, Q_r=-E R.
Their sum is zero. Nonthermal photoelectron energy initially belongs in a nonthermal reservoir and is transferred to gas only on deposition.

For a temperature-independent RR cross section with fixed target-state weighting:
alpha=A T^(-3/2) integral epsilon sigma(epsilon) exp[-epsilon/(k_B T)] d epsilon,
lambda=A T^(-3/2) integral epsilon^2 sigma(epsilon) exp[-epsilon/(k_B T)] d epsilon.
Differentiation under the integral, when the moments exist, gives
lambda=k_B T alpha [3/2+d ln(alpha)/d ln(T)].
This is a heavy-target/no-recoil electron kinetic-energy identity; temperature-dependent target populations require extra derivative terms and cannot be folded into it silently.

A differentiable fit does not transfer its rate error bound to the energy moment: for alpha_fit=alpha_true(1+delta), the bracket gains d ln(1+delta)/d ln(T). Moment accuracy remains a separate empirical question. Negative inferred moments require diagnosis, not clipping.

For recombination including the complete cascade to the final ground state:
Q_kin=-n_e n_ion lambda,
Q_B=-chi n_e n_ion alpha,
Q_r=n_e n_ion(lambda+chi alpha).
Total exchange cancels. This does not determine the free-bound spectrum, line spectrum, or fraction within the UV band. The particle-source term in the temperature equation remains separate. For alpha proportional to T^-beta, lambda/alpha=(3/2-beta)k_B T; if RR alone has S_e=-R and S_heavy=0, its temperature contribution is (2 beta/3) T R/n_part despite kinetic energy removal.

Nuclear mass defects require a separate consistently referenced m c^2 reservoir. Products allocate energy among thermal gas, nonthermal particles, photons, and neutrinos. Escaping neutrino energy is an explicit channel. Existing conditional all-bare 18-family postprocessing is reused without inferring daughter-charge or coupled energy closure.

## Directional radiation and fixed physical energy bands
Let mu be the photon direction cosine to the symmetry axis and E=c|p|. Conserved comoving momenta imply
dot p_perp=-(H-s)p_perp, dot p_parallel=-(H+2s)p_parallel,
dot E=-E[H+s(3mu^2-1)], dot mu=-3s mu(1-mu^2).

For photon number n_gamma per physical volume, energy and solid angle, with axisymmetric dOmega=2pi dmu:
partial_t n_gamma+3H n_gamma+partial_E(dot E n_gamma)+partial_mu(dot mu n_gamma)=C_gamma.
Regular distributions have zero angular endpoint flux since dot mu=0 at mu=+-1.

For fixed physical bounds E_l,E_h:
U=integral_band integral_Omega E n_gamma dOmega dE,
pi_r,ij=integral_band integral_Omega E(l_i l_j-delta_ij/3)n_gamma dOmega dE,
Q_band=integral_band integral_Omega E C_gamma dOmega dE,
J(E)=integral_Omega E dot E n_gamma dOmega.
Integration by parts gives
dot U+3HU=Q_band-[J]_lo^hi+integral_band integral_Omega dot E n_gamma,
hence
dot U+4HU+sigma:pi_r=Q_band-J(E_h)+J(E_l).

In an expanding redshifting direction J<0: the lower boundary removes energy and the upper boundary supplies inflow. The sign reverses where directional drift reverses. An outside-band radiation partner receives J(E_h)-J(E_l), with its own expansion work and anisotropic stress. A cumulative lost-energy counter is not a substitute for that physical state. Photons emitted outside the grid must be allocated directly to the partner. Shared internal interface transfers cancel in the combined ledger.

At nonzero shear initially isotropic collisionless radiation generally becomes anisotropic. A persistent pi_r=0 requires a collision/approximation closure and an explicit validity range.

## Independent manufactured targets and next implementation
Normalized test units, not astrophysical parameter choices:
* A=2,p=1,E_l=1,E_h=3,H=1/2 for n_E=A E^p gives U=52/3, dot U=-26/3, J_l=-1,J_h=-27 and dot U+4HU=26=-J_h+J_l.
* PI chi=3,E=11,R=2 gives (16,6,-22); RR chi=3,mean kinetic energy=2,R=5 gives (-10,-15,25).
* k_B=1,n=2,T=3,H=1/10,S=2/5,Q_kin=6,sigma:pi_g=1 gives dot n=-1/5,dot T=7/15,u=9,p=6,dot u=1/2. The energy equation returns 6.

The separate ledger_checks.js and LEDGER_CHECKS_RESULT.json record actual limited arithmetic checks in functions.exec V8. They do not validate provider accuracy, an ODE trajectory, general quadrature, or full closure. Their C1...C10 labels are test-group IDs, not research-loop stages.

Next coding obligations: recover and finish the Python bootstrap; then implement one energy-allocation record per reaction, particle-source/EOS coupling, RR kinetic moments plus explicit cascade spectral providers, conservative directional UV transport and outside-band partners. Positivity/convergence/combined-residual numerical validation awaits those changed dependencies.
