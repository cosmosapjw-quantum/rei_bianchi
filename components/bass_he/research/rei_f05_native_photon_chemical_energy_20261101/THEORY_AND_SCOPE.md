# BASS_HE → original REI F05: source-native photon-driven chemical binding power

2026-11-01 | original accepted tick 160/131072 | theory scope R1–R5 | DRAFT/HOLD

## Original authority and constructive question
Immutable BASS_HE parent PR #148 HEAD 3e4713b83d097d26b7ed985d158d895b0408fd1a. Original REI source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b; accepted 46,080-cell tick160 state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; source RHS SHA256 b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36. Reuse exact four-group three-moment allocation from original REI PR #355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00 and original ReducedIntervalModel._explicit_photo_fields. This is not PW19 source replacement, a new IVP, or a new static opacity atlas.

Question: how much original four-group photoionization at accepted tick160 increases the H/He chemical ionization-potential reservoir per proper second; how much creates primary photoelectron excess heat; and how do these material source powers respond to three global original species moments? The output target is 12 source-conditional original photon group/species pairs and native 46,080-cell direct sums.

## Exact frozen native four-group energy functional
Conventions: metric (-,+,+,+), comoving proper time seconds, energy in eV/erg, epsilon_eV=1.602176634e-12 erg/eV. Original S_s=sum_i N_{s,i}, s=(HI,HeI,HeII). Group g=0..3. Let a_sg be exactly original source _explicit_photo_fields coefficients: HI has scale*sigma_HI/N_Htotal; HeI has YHe*scale*sigma_HeI/N_Hetotal; HeII has YHe*scale*sigma_HeII/N_Htotal; unsupported owner pairs exactly zero. scale=NH0_CM3*(1+z)^2*MPC_CM. Note the asymmetric HeI vs HeII denominator.

D_g = E_g + sum_s a_sg*S_s,
q_sg = a_sg*S_s / D_g,
q_ext,g = E_g/D_g,
sum_s q_sg + q_ext,g = 1.
E_g denotes *external opacity*, not photon energy. J_g is *native original photon current* photons/s.

R_sg=J_g*q_sg [ionizations/s],
Bdot_sg=epsilon_eV*chi_s*R_sg [erg/s],
Qdot_sg=epsilon_eV*DeltaE_sg*R_sg [erg/s].

Physical ionization potentials chi=(13.598434599702,24.587389011,54.41776) eV are original frozen BASS_HE species constants. DeltaE_sg are original REI model.excess_eV and NOT the PW19 external donor excess. Bdot is **photoionization-driven positive ionization-potential reservoir production**, not total dB/dt including OTS, recombination, collisional ionization, cooling and temperature. Qdot is source-model primary excess electron heat. P_material=Bdot+Qdot is resolved material electronic-energy deposition only. External photon absorption, photon escape, cosmological redshifting, emission and cooling are excluded; the original source does not provide a complete photon spectral energy measure here.

## Exact global three-moment derivative at fixed source forcing
For w_sg=chi_s+DeltaE_sg and P_g=epsilon_eV*J_g*sum_s w_sg*q_sg,
dP_g/dln(S_k) = epsilon_eV*J_g*q_kg*(w_kg-sum_s q_sg*w_sg).
Likewise w=chi or w=DeltaE gives Bdot or Qdot derivative. This follows by quotient differentiation at fixed J_g,E_g,a_sg on the positive three-moment cone. It is NOT a claimed physical thermochemical 46k Jacobian certification or continuous-time error enclosure. Wolfram independently simplified the three derivative residuals to {0,0,0}, and sum(q)+qext to one.

## Independent/hostile checks and stop
Check every source SHA, accepted state, original model source, 46k native species fields, species and group positivity, aggregate native primary photoheat, and central finite differences of the exact log-moment derivative. A source channel with J_g=0 deposits zero Bdot and Qdot regardless of high formal opacity share; the original G3 hard photon current has upper bound 1e-323 native photons/s. No claim that high external-PW19 HeII hard opacity means actual REI HeII photoheating.

Do not identify frozen Bdot(t160)*dt with native integrated tick160→161 delta-B, nor treat the unaccepted tick161 shadow as official. Central REI 28/88_REPORTED, working 33/88_REPORTED, fast 4/7_REPORTED, BASS_HE physical 14/18_REPORTED, canonical delta 0. Production HOLD, Draft only, no merge, no force push and no tolerance relaxation. Drift watchdog: STOP extra static PW19 opacity tables; one original photon-source energy partition only.

References: Verner et al. 1996 ApJ 465 487 https://www.pa.uky.edu/~verner/photo.html ; original REI PR #355 and BASS_HE PR #148 archived original source files.
