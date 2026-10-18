# Unit 7 lane C: decay-source and observed-neutrino spectrum

Status: analytic contract frozen; numerical values are supplied by the bounded lower-tier execution of this contract. Authority requested: Astra; observed runtime identity: UNKNOWN. This lane uses the explicit lane-B three-state trajectory and the actual R5 Be7 donor abundance. It changes no product code.

## 1. Inputs and physical convention

Let `F(z)` be the fraction of the initial Be7 donor that has decayed by redshift z, excluding direct primordial Li7. Thus F increases with cosmic time, F'(z)<=0, and the positive decay measure on an ascending redshift interval is `dD=-dF`. The lane-B CSV is descending in z and supplies raw F, x_Be3, and dF_dz. Its normalized `p_z` is a conditional shape diagnostic and must not supply absolute normalization.

The initial comoving number density is N0=nb0*YBe7, using donor YBe7=3.784994236672219e-10 per baryon and nb0=2.47920954940649e-7 cm^-3. Direct donor YLi7=2.1819521581308123e-11 contributes no EC neutrinos. If abundances per hydrogen are used, XBe7=YBe7/YH and nH0=nb0*YH, so nH0*XBe7=N0 exactly. In particular XBe7 must not be multiplied by nb0, nor YBe7 by nH0. The paper's order-of-magnitude Be/H is not the donor amplitude.

For the numerical per-hydrogen equivalence check, take YH=0.7530965905693692 from the donor's `Y_final.p` and label it the donor protium convention. The same hydrogen reference must appear in both factors; no hydrogen mass-fraction approximation is needed.

Freeze the literal line approximation of Khatri & Sunyaev (2011), section 4 and Eq. (10): ground-state branch b_g=0.896 with E_g=861800 eV, excited-state branch b_x=0.104 with E_x=384200 eV, and excited nuclear photon energy E_gamma=477600 eV. Their section 2 quotes 10.44%; the present contract consistently uses Eq. (10)'s 10.4%, without mixing the two roundings. These are idealized paper line energies, not exact ion-state Q values.

## 2. Jacobian and conservative observable

In the freely streaming ultrarelativistic line approximation, E=E_j/(1+z). Therefore z_j(E)=E_j/E-1 and |dz/dE|=E_j/E^2=(1+z)^2/E_j. The present spectral number density is

`q_j(E)=dn_nu,j/dE=N0*b_j*(-F'(z_j(E)))*E_j/E^2` [cm^-3 eV^-1].

The same result follows from the source integral `N0*b_j*integral[-F'(z) delta(E-E_j/(1+z)) dz]`. This independent delta-function derivation fixes both the sign and the Jacobian. No extra (1+z)^3 belongs in the present comoving density. The physical source rate at emission instead contains that factor (section 5).

For an observed energy bin [L,U], intersect the corresponding redshift interval [E_j/U-1,E_j/L-1] with the computed history [z_min,z_max]. Call the resulting bounds a<=b. The exact count for that truncated history is

`N_j[L,U]=N0*b_j*(F(a)-F(b))`.

Empty intersections give zero. At L=0 the upper redshift bound is infinity; do not evaluate a division by zero. Constant continuation of F outside the computed interval is a definition of the *truncated export*, not an assertion about the real uncomputed history.

For each native redshift cell [a,b], use the piecewise-linear interpolant of raw F, with s=(F(a)-F(b))/(b-a)>=0. For any clipped subcell [l,h] within it, three exact moments of that interpolant are

`M0=N0*b_j*s*(h-l)`;

`M1=N0*b_j*s*E_j*log((1+h)/(1+l))`;

`M2=N0*b_j*s*E_j^2*(1/(1+l)-1/(1+h))`.

Use log1p((h-l)/(1+l)) for the logarithm when helpful. Bin energy is M1, not midpoint_energy*M0. Cumulative native-cell M0/M1/M2 plus boundary-cell corrections permit vectorized/bin-search export with no repeated O(number_of_cells*number_of_bins) sweep. The moments are exact for the chosen interpolant; accuracy against the differential kinetics is measured separately.

## 3. Normalization, shape, peaks, and tails

Write DeltaF=F(z_min)-F(z_max). The computed-window branch number is N0*b_j*DeltaF; the total is N0*DeltaF. Do not divide by DeltaF to manufacture a full-decay amplitude. Conditional statistics may divide by the actually exported number, with that denominator recorded. Mean energy=M1/M0 and variance=M2/M0-(M1/M0)^2. Report quantiles .05,.16,.50,.84,.95 by solving F(z)=F(z_max)+p*DeltaF and then E_j/(1+z).

The differential line mode maximizes (-F'(z))*(1+z)^2, not simply -F'(z). Compute it from the provided rate-derived dF_dz, interpolate around the maximum, and find both half-height roots for FWHM. All branch energies, means, quantiles, standard deviations, and FWHM scale as E_x/E_g because the two branches share the same F. Their total counts instead scale as b_x/b_g. Define the quoted peak as the mode of dn/dE; a mode of E*dn/dE would differ.

There are two separate tail questions. For an energy export narrower than the computed support, report the known count below and above the export and verify inside+below+above=N0*b_j*DeltaF. For history outside [z_min,z_max], report F(z_max) (earlier decays present in the input initial condition), and 1-F(z_min) (surviving donor at the last computed epoch). The latter is not automatically a present-day neutrino tail: its conversion requires extending the kinetics or an explicit late-time assumption. If F(0) is supplied, the uncomputed late-decay fraction is F(0)-F(z_min). This contract makes no F(0)=1 assertion.

The default shared export grid is 0 to 100 eV in 0.025 eV bins, which covers both branches for the agreed z=100000 to 10000 history. Also perform a deliberately cropped [12,35] eV accounting check. Record finite-window statistics and any underflowed residual populations without endpoint replacement.

## 4. Independent checks and analytic toy

Use the direct kinetic derivative `-F'=lambda*x_Be3/((1+z)*H)` for an independent Jacobian quadrature. Its integral and first moment must agree with the cumulative-F export to the prescribed discretization tolerance; do not regenerate this comparator by differentiating the same F interpolant. Compare native and coarser history sampling to quantify interpolation sensitivity. The donor trajectory itself is governed by lane B's convergence criteria.

Analytic toy: N0=b=1, E_emit=12 eV, and uniform decay-redshift measure s=1/2 on 1<=z<=3. Then q(E)=6/E^2 on 3<=E<=6 eV, total number=1, mean energy=6*ln(2), and second moment=18 eV^2. Bins [3,4] and [4,6] each contain 1/2, with first moments 6*ln(4/3) and 6*ln(3/2). Outside-support bins are zero. A cropped [3.5,5] interval plus both omitted tails must still sum to one. This toy discriminates a missing Jacobian, wrong sign, midpoint energy assignment, and accidental normalization.

Acceptance: exact-interpolant bin count closure <=1e-11 relative to N0*DeltaF; first/second moment closure <=1e-10; toy analytic agreement <=1e-11; branch scaling <=1e-10; independent kinetic-Jacobian number and first moment <=3e-3 relative; coarsened/native CDF means and quantiles <=3e-3 relative. Small negative F-cell increments are reported as an input invariant failure, not clipped silently. A numerical violation returns to theory authority for one targeted interpretation/repair.

## 5. Emission bookkeeping and physical interpretation

The decay rate per physical volume is R_phys(z)=N0*(1+z)^3*lambda*x_Be3(z), in cm^-3 s^-1. Neutrino source energy rates are R_phys*b_j*E_j. The nuclear photon source rate is R_phys*b_x*E_gamma. Integrated per initial donor, the paper-line neutrino energy is 812129.6 eV and photon energy is 49670.4 eV; for the computed window multiply by DeltaF, and per cosmic baryon also multiply by YBe7. The present neutrino energy density instead is the redshifted sum of branch M1, and the mean per emitted neutrino is that sum divided by N0*DeltaF.

The paper quotes initial daughter recoil estimates 56.5 eV (ground branch) and 11.2 eV (excited branch), giving 51.7888 eV per donor with the selected branching. Keep this as a separate approximate recoil diagnostic. The rounded neutrino energies already sum with the photon to 861800 eV on each branch; adding the recoil estimates therefore does not form an exact closed Q-value budget. Exact closure would require consistent nuclear/ionic masses, captured-electron binding, neutrino recoil, and the subsequent gamma recoil. This task freezes the paper's line idealization and does not assign false exactness to those inputs.

Source photon/recoil energy is not an implemented deposited-heat rate. Compton redistribution, ionization/heating partition, and photon escape require a transfer/deposition model; no f_dep(z)=1 is introduced. A hypothetical freely redshifted photon energy would not describe the interacting nuclear photons.

The weak source emits electron-flavor neutrinos. The exported total number spectrum sums propagated flavors; it does not promise a present electron-flavor spectrum. An electron-flavor detection calculation needs oscillation/decoherence probabilities and any relevant matter effects. For nonzero neutrino mass, momentum redshifts exactly while energy follows sqrt(m_i^2*c^4+p_emit,i^2*c^2/(1+z)^2). The present implementation uses E proportional to (1+z)^-1 under the condition m_i*c^2 << E_obs (the principal lines are around tens of eV). It does not infer neutrino masses, a mass ordering, or an exact sub-eV line shift.

## 6. Scope and research result

The derived pushforward makes the abundance-to-observable bridge constructive: physical donor count -> explicit decay trajectory -> conserved branch spectra -> present energy moments and source bookkeeping. Khatri-Sunyaev reported line locations/widths are contextual comparisons only; no spectrum or trajectory is read from a figure, and no acceptance rule tunes the computation to those values. The new result is a donor-specific numerical realization of the cited mechanism and an independently checkable conservative export, not a new no-go theorem. NG1-NG7 new-no-go admission is therefore not invoked.

The numerical result file and spectrum tables are `evidence/DECAY_SPECTRUM_RESULT.json`, `evidence/decay_neutrino_spectrum.csv`, and `evidence/decay_neutrino_profile.csv`; their admission remains tied to the actual execution and independent review. This document supplies the full recipe, conventions, and finite stop criteria to the lower-tier executor.
