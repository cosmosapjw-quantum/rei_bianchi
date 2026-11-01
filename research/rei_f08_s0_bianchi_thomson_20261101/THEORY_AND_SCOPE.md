# REI IGM | original F08 S0-source electron screen to Bianchi-I observer Thomson sky

## Authority and scientific boundary

This study belongs to original cosmosapjw-quantum/rei_bianchi. Input is the Oct 2026 original F08 source-verified paired S0_FLRW and S0_BI proper electron histories, each with 16001 samples/16000 accepted steps, frozen identically sourced by the same source identity 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8. Exact source/input bytes and scenario plus original provider-owned Thomson cross section are locked in SOURCE_PROVENANCE.json. Original F08 computation state COMPLETED but SCIENTIFIC_ADMISSION=HOLD (prescribed matter/source/background, not self-consistent Einstein–Boltzmann or observational fit). Original REI-F09 remains BLOCKED on EXTERNAL_PROVIDER_DOMAIN_AND_BINDING_BLOCKED (S0 common atomic-domain intersection EMPTY); this independent Thomson consumer does NOT unblock it or change the atomic physics owner.

Original central REI DAG=28/88_REPORTED, Working=33/88, Fast=4/7, canonical increment ZERO. Original 26-event 46080-cell first canonical FLRW interval remains at tick160/131072 with old [160,161] local logT error 2.1245050576368385e-4 > strict 2e-4, original width gate 2e-3. Source electron histories here are from the earlier 1-cell prescribed F08 paired solver; they are NOT the original failed 26-event first interval. No owner substitution, merge, force push, production execution, new source IC, observed reionization measurement or new full IVP.

## Exact Bianchi-I null kinematics

Metric signature (-,+,+,+), ds²=-c²dt²+sum_i a_i²(t)(dx^i)², a_i(t)=exp(H_i t). Original S0 scenario has H=1e-14 s^-1, HI=(1.01,0.99,1)*1e-14 s^-1, a_i(0)=1 and tilt=0. These H_i are prescribed, not Einstein dynamical output. Let n_i be a unit sky direction in the orthonormal frame of the comoving observer at t_o=1e13 s. Conserved covariant spatial photon momenta imply the observer-relative emission redshift

  1+z_rel = [sum_i n_i² exp(2 H_i (t_o-t_e))]^(1/2).

This z_rel is NOT the scenario's background reference_z0=10 and NOT the redshift relative to Earth today. At fixed z_rel the emitter time t_e(n,z_rel) differs by direction, with unique lookback Delta because H_eff=sum_i H_i w_i>0 where w_i=n_i² exp(2 H_i Delta)/sum_j n_j² exp(2 H_j Delta).

## Actual Thomson optical depth and visibility

For comoving electrons with D_gas=1 and prescribed, source-owned proper density n_e(t),

  tau_BI(n,z_rel)=c sigma_T integral_[t_e(n,z_rel),t_o] n_e^BI(t) dt
  g_BI(n,z_rel)= c sigma_T n_e^BI(t_e) exp[-tau_BI] / [(1+z_rel) H_eff(n,Delta)].

Original source c=2.99792458e10 cm/s; exact REI thermal owner constant sigma_T=6.6524587051e-25 cm². Analogously tau_F and g_F use original S0_FLRW density and H=1e-14 s^-1. No extra photon-energy factor appears in comoving Thomson proper-time opacity. Both are actual model-observer quantities over the saved finite source interval, not CMB photons from z=1100 or complete polarized Thomson Boltzmann/LoS.

## Exact source-geometry split and first-order shear result

At fixed relative z_rel, define Delta_F=ln(1+z_rel)/H and t_*=t_o-Delta_F. Define
  M(z_rel)=tau_BI(t_*)-tau_FLRW(t_*)     (equal-comoving-time material history difference)
  G(n,z_rel)=tau_BI(t_e(n,z_rel))-tau_BI(t_*)   (anisotropic-emission-clock geometry).

Then tau_BI(n,z_rel)-tau_FLRW(z_rel)=M+G exactly by add-subtract, for the two archived source histories. At H_i=H+sigma_i with sum sigma_i=0 and |sigma_i|<<H, fixed z_rel gives
  delta_Delta=-(Delta_F/H) sum_i sigma_i n_i²,
  G_first_order=-(c sigma_T n_e^BI(t_*))*(Delta_F/H)*sum_i sigma_i n_i².
Thus first-order G is a trace-free even quadrupole, zero dipole and mean over sphere; exact higher multipoles are even. The continuum quadrupole tensor Q_ii=<G(n)(n_i²-1/3)> has first-order Q_ii=-(2/15)*c*sigma_T*n_e(t_*)*(Delta_F/H)*sigma_i.

This statement is DERIVED and its null-redshift first variation was verified symbolically using Wolfram. Supported Bianchi null-geodesic reference: Fleury, Pitrou & Uzan, Light propagation in a homogeneous and anisotropic universe, Phys Rev D 91 (2015) 043511, DOI 10.1103/PhysRevD.91.043511. The reference is NOT evidence that the original F08 solver is cosmologically self-consistent.

## Executable experiment and fail-closed conditions

Predefine lookback fractions 0.25,0.50,0.75,0.95 of original source 0..1e13 s, relative target z_rel=exp(H Delta_F)-1. Primary angular-grid (n_mu,n_phi)=(16,32), with convergence grids (8,16),(32,64), all equal-area positive weights in mu and phi. Verify original paired-source identities SHA256 and 16001 temporal rows, nH baryon volume law and nHe/nH=.083, positivity, conditional ne_lo<=ne<=ne_hi, D_gas=1, time monotonicity. Solve exact directional redshift via monotone bisection. Integrate actual source-ne history by sampled linear interpolation with cumulative trapezoid; repeat with sampled ne conditional lower/upper bands and time coarsening factor 2/4. Enforce exact geometry/material decomposition, n vs -n parity, zero-shear limit, sky dipole, trace-free quadrupole, angular-grid and time convergence, original photon source not substituted. Calculate real tau, transmission, relative-z visibility, observer emission time and q(n), and first-order shear control.

Sampled ne lower/upper time bands are CONDITIONAL SAMPLED bands only; without a proof on ne(t) between samples they are not rigorous continuum interval enclosures. The count of emitted numeric sky directions is not number of independent physical source trials. The 1-cell, prescribed exponential-Bianchi source is not the 46k 26-event central full history or self-consistent Einstein source. Original REI-F09 external provider remains BLOCKED. After a scoped PASS, next central work is an actual source-matched H/He late-IGM history joined to Einstein-constrained Bianchi transport and cosmological observable, not more adjacent photon source-Hessian or point-parent diagnostics.

Never promote REI 28/88 without canonical evidence. Native subagent and independent-author blind referee are NOT_RUN unless actual host evidence exists. Publish one distinct Draft GitHub PR plus actual source/input byte hashes, tests, CI and binary backup readback; no 20 empty docs, one R/C stage ledger.
