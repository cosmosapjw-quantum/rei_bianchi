# REI IGM | 실제 F08 S0 source-matched FLRW vs Bianchi-I Thomson observer science

Date: 2026-11-01. Repo: cosmosapjw-quantum/rei_bianchi. Source baseline: Git main ae3402713c4b6530ab2b27f008f5f5d5c6a999ed; original historic F08 computation completed but scientific_admission HOLD, original F09 blocked external atom provider source-domain intersection. THIS UNIT IS F08 SOURCE_CONDITIONAL_OBSERVER PILOT, not original F09 completed, 26-event canonical first interval, self-consistent Einstein dynamics, an observed z0 CMB optical depth, or polarization.

## Original source and assumptions

The exact archived original paired S0_FLRW and S0_BI F08 proper electron histories each contain 16001 original source-time rows and 16000 accepted trial steps. Both share source identity SHA256 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8. Input exact CSV.gzip SHA256 are FLRW 0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa and Bianchi 663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723; original scenario sha c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1. The two original source-evolving calculation windows run t=[0,10^13] proper s with nH0=10^-4 cm^-3, nHe/nH=.083, Hbar=10^-14 s^-1, original original HBI=(1.01,0.99,1)*10^-14 s^-1, zero gas tilt and proper electron density. c=29979245800 cm/s and Thomson sigmaT=6.6524587051e-25 cm^2 are anchored to original repo source (exact file hash in SOURCE_PROVENANCE.json). Neither original S0 source nor owner code is replaced.

Our observer is at original source endpoint t_obs=1e13 s; z_rel below is the RELATIVE emitter-to-this-observer redshift, not an absolute cosmological observer at current z=0. All physics is conditional on the user-provided prescribed Bianchi scale factors, original F08 electron history and sampled-linear interpolation, NOT an observational fit or original 26-event F05 completion.

## Exact geometric result

In metric ds^2=-c^2dt^2+sum a_i(t)^2 dx_i^2, a_i(t)=exp(H_i t), the comoving observer's photon sky direction n determines exact energy ratio:
  1+z_rel = sqrt(sum_i n_i^2 exp(2 H_i (t_obs-t_emit))).

At fixed z_rel this implicitly gives different emitter times t_emit(n). The original comoving Thomson depth is tau_BI(n,z_rel)=c sigmaT integral from t_emit(n,z_rel) to t_obs of ne_BI(t) dt. Visibility per relative redshift is g_BI= c sigmaT ne_BI(t_emit) exp(-tau_BI)/[(1+z_rel) H_eff(n)], H_eff=weighted mean of H_i with photon energy weights n_i^2 exp(2 H_i Delta). FLRW uses actual paired ne_FLRW(t) and constant Hbar.

Let t_ref=t_obs-ln(1+z_rel)/Hbar. Then the exact difference tau_BI(n,z_rel)-tau_FLRW(z_rel) separates into (tau_BI(t_ref)-tau_FLRW(t_ref)) [material history] plus (tau_BI(t_emit(n))-tau_BI(t_ref)) [anisotropic geometry], using precisely the same S0 input pair. With shear sigma_i=H_i-Hbar, sum sigma_i=0, geometry at first order is -c sigmaT ne_BI(t_ref) [Delta_ref/Hbar] sum_i sigma_i n_i^2. Hence parity even, zero dipole and a sky quadrupole with first-order Q_ii=-(2/15)c sigmaT ne(t_ref)(Delta_ref/Hbar)sigma_i. The first-order emission-time shear formula and the analytic Thomson g(z) derivative were independently checked by Wolfram (zero residual).

## ACTUALLY NUMERICALLY CHECKED original S0 physical data

Two original F08 input histories are verified SHA exact; one new physics calculation generated 10,752 sky/time directions, 30 columns, 4 predeclared lookback fractions [0.25,0.5,0.75,0.95] times three equal-area angular grids [8x16,16x32,32x64]. Primary angular grid is 16x32; the 10,752 rows are NUMERICAL ANGLE SAMPLES, NOT independent cosmic source trials or real observations. Exact new sky CSV gzip SHA256 41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d.

Original-source primary 16x32 sky physics:
window fraction 0.25: z_rel 0.0253151205244, tau_BI mean 4.181615743284481e-6, geometric RMS 2.2356910605818343e-8, same-time material tau difference 9.970980983963536e-13, source-conditional visibility mean 1.688903492663286e-4 per z_rel.
window fraction 0.50: z_rel 0.0512710963760, tau_BI mean 8.66269554351284e-6, geometric RMS 4.787136156420138e-8, same-time material difference 1.9641239098333726e-12, visibility mean 1.763513858445629e-4 per z_rel.
window fraction 0.75: z_rel 0.0778841508846, tau_BI mean 1.3454128725178408e-5, geometric RMS 7.666994101164532e-8, material difference 2.8858908349100676e-12, visibility mean 1.8364406784164675e-4 per z_rel.
window fraction 0.95: z_rel 0.0996588551261, tau_BI mean 1.751108493543702e-5, geometric RMS 1.0149346601644634e-7, material difference 3.3134242996091332e-12, visibility mean 1.881180421280219e-4 per z_rel.

At 0.95 of the source interval, Qxx=-2.615836400571423e-8, Qyy=+2.6252099709885708e-8 and Qzz=-9.373570417147798e-11 for the primary sky grid; Q has vanishing trace within test tolerance. Geometric RMS / mean tau ~5.8e-3, while geometric RMS / absolute equal-time material contrast ~30630.99. In THIS prescribed experiment the direction-dependent emitter clock is much more important than the difference between the matched S0 scalar electron histories; this is not a generic gravity theorem.

Time grid coarsening 2x and 4x changes tau by at most 2.5927502779654415e-9 relative (quadrature discretization witness only, NOT a source-model error bound). Primary 16x32 versus 32x64 quadrupole max relative component difference <=2.1957965697566502e-5. The original electron sample lower/upper arrays were also integrated and included as SAMPLE-CONDITIONAL bands, not certified continuum enclosures.

## Independent technical audit

Independent standalone stdlib readback audit over every 10752-row, 30-column source-defined output checked original input SHA, photon directional redshift equation, exact material+geometry splitting, positive sigmaT screen, exp[-tau] transmission, per-redshift Thomson visibility and 12 quadrupole groups. Original-source exact redshift log residual <=1.8041124150158794e-16; exact material+geometry decomposition difference 0; visibility formula max abs discrepancy 5.421010862427522e-20; max parity difference for n->-n 1.3552527156068805e-19. Independent quadrupole numeric readback within 2e-19. Unit tests 12/12 normal and 12/12 python -O before publication. Actual GitHub CI after publication must be read before claiming implementation-verification on the remote runner.

## Same-author hostile referee and drift watchdog

(A) The source background H_i is PRESCRIBED, not dynamically Einstein-matched; interpreting these signals as fitted cosmological shear/primordial anomalies is unjustified.
(B) The electron sample time band only bounds the original sample values and their chosen linear interpolation, not the continuous-time original solver or the actual astrophysical model error. Time-grid coarsening is not a rigorous error certificate.
(C) F09 external atomic provider reports empty S0/FT03 common source-valid domains. Thomson-only observer screen does not satisfy F09 external owner gate and no atomic source substitution was made.
(D) The relative redshift z_rel is defined against original F08 model endpoint t=10^13 s, not cosmic z=0 or observed CMB optical depth z1100.
(E) F08 source photons have 13.7 eV and a prescribed angular continuum, but this is an unpolarized, energy-independent Thomson scattering-screen probe. No radiative intensity, polarization, Klein-Nishina corrections, or Boltzmann angular collision term is computed.
(F) Numerical quadrature direction count is not 10752 physical radiation source realizations. S0_FLRW and S0_BI share original source identity but do not establish a self-consistent observational Einstein source.
(G) This unit genuinely creates a directional observable, rather than another static source Jacobian. Yet original F05 entire 46080-cell first canonical interval remains blocked at tick160/131072 and F09 provider remains blocked: REI central 28/88 reported, working 33/88, Fast 4/7; canonical delta zero.
(H) Source-owner readback and science values are one author + independent code/math, not independent-author blind review. Native subagents NOT_RUN.

## Publication/next

GitHub Draft PR, isolated branch, unmodified dirty original research tree; original source pair copied byte exact to a source-locked research subfolder. Original F08 raw multi-GB photon stage JSONL remains locally in its owner archive, NOT included here. Actual source sky CSV and independent witness can be replayed directly with Python 3.12 stdlib, no new IVP or production runs. After actual GHA execution, persist artifact checksums and ideally GitHub/Drive second-provider byte identity. Immediate central next: combine a *dynamically source-owned* 26-event REI H/He history with Einstein-compatible Bianchi geometry, polarized Thomson transport and real redshift/LoS observables. This F08 S0 screen is an expressly conditional consumer and not a new canonical node.
