# BASS_HE → REI IGM: Original F08 S0 H/He Thomson observer decomposition

2026-11-01 | owner cosmosapjw-quantum/BASS_HE | central receiver cosmosapjw-quantum/rei_bianchi | original immutable BASS_HE PR144 HEAD 8c70ae9b8c15dee21cfe8e3b29fa8c32a04298fb

## Original actual source and question
Source owner REI PR349 final HEAD 58f7ffb685c3758f1fed1113ff8134a24478c3df. Original F08 S0 BI/FLRW 16,001 proper-electron rows per history, actual 16,000 accepted original IVP intervals, source pair 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8; 10,752 original F08 observer sky rays, original sky gzip SHA256 41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d. Original source stays read-only, REI scientific admission HOLD.

Original *same F08 S0* 22-field BI/FLRW curves are retained from original physical source repository checkpoint, not reconstructed from the earlier F05 data. Curve SHA256 BI 3096dc923520ec98da8c2e1dd3f03605cbf0809e944eeb5e4ceb6f58eff58893, FLRW cab6e37e0f375e06dc03218067fa74fe3f14455e2dcf41a03051965008acb521. Original proper electron SHA BI 663911291bea564d314e1d46df9750c03a39fd5d9404eca6a7485776d894f723, FLRW 0b81cae87d6f90888d1d3def1995cd8d029625d1cc1dd11bffab94e8d30e7efa. Original scenario and sky pin checked. Original curve times match every source electron-density row exactly, including registered initial state. 32,002/32,002 original source points satisfy species electron density identity with maximum binary64 difference 0.0.

## Physics/derivation
Metric (-,+,+,+), comoving gas, no tilt, prescribed Bianchi I a_i(t)=exp(H_i t), H=(1.01,.99,1)*1e-14 s^-1, matched FLRW Hbar=1e-14 s^-1; original t_obs=1e13 proper seconds. Original S0 compact 13.7 eV photons per hydrogen, source He nuclei to H ratio **0.083** (NOT earlier F05's 0.079). Original c=29979245800 cm/s, sigma_T=6.6524587051e-25 cm². This is a verification/prescribed model, NOT Einstein-constrained physical EoR or observed CMB.

From original HII/HeII/HeIII ion fractions, define n_e,H=n_H*x_HII and n_e,He=n_He*(x_HeII+2*x_HeIII); nuclei are conserved. Then n_e,H+n_e,He=n_e,original pointwise. For species s=H,He, each **same original PR349** photon sky-ray direction n and emitted time te(n,z_rel) has
   tau_s^BI(n,z_rel) = c sigma_T integral_[te(n,z_rel),t_obs] n_e,s^BI(t) dt
   tau_s^FLRW(z_rel) = c sigma_T integral_[tref(z_rel),t_obs] n_e,s^FLRW(t) dt.
The time-dependent density is sampled piecewise linearly as the original observer source specifies. The physical sky visibility contribution is
   g_s = c sigma_T n_e,s(te)*exp[-(tau_H+tau_He)] / [(1+z_rel)*H_parallel(n,te)].
**Both species share the TOTAL attenuation.** Computing exp(-tau_s) separately would be physically wrong for the component of a common-scattering visibility. Hence tau_H+tau_He=tau_original and g_H+g_He=g_original on the same ray. The equal-proper-time material and fixed-relative-z geometric terms likewise add by linearity. Wolfram symbolic charge-conservation and common-attenuation identities gave exact {0,0}.

## Actual new physical results
Original source-history two trajectories ×16,001 times = **32,002** new species-resolved proper-electron physical rows. Source matched 10,752 original ray/time/direction rows × multiple H/He Thomson moments. All four windows use original observer-relative redshift and original 8×16,16×32,32×64 equal-area angular grids.

Primary grid 16×32, longest relative-redshift shell z_rel=0.09965885512610294, source observer t_obs=1e13 s:
  mean tau_H(BI) = 1.548876871564537e-5;
  mean tau_He(BI) = 2.0223162197915122e-6;
  He fraction of mean tau = 0.1154877740155886 (11.54877740155886%);
  He fraction of geometry Qxx = 0.11821662512385875 (11.821662512385875%);
  Qxx_He = -3.0923535115167768e-9; Qyy_He = +3.104930644292223e-9;
  mean He contribution to common-attenuation visibility fraction = 0.11824718935165879.

At shorter windows fractions of mean tau_He: z_rel 0.02531512 -> 0.1142251176183478; z_rel 0.05127110 -> 0.11457173388792004; z_rel 0.07788415 -> 0.1150159798839584.
Original start He free-electron fraction 0.12152269399707175, original BI endpoint 0.11394824741902065. Both original HeI and HeII *direct photoionization rates* gamma_HeI and gamma_HeII are identically 0 in this 13.7 eV S0 history; nonzero He Thomson signal is due to actual existing He ionized fractions and their native plasma evolution, NOT newly absorbed He-ionizing UV photons.

Actual output gzip history 32,002 rows SHA256 08eb3499824d5f4bdb453e18faf5dd7f27279542f9432ac29e0ee24b1931d533. Ray 10,752 rows SHA256 ef50d5670f78db66e300736cb2edf819d486263617e1b8e7fd68821b4b5afccf. All original rows came from original source, no synthetic substitution or new cosmological IVP.

## Scientific and implementation validation
12/12 ordinary and 12/12 optimized Python source, identity, conservation, total visibility, invalid-hash and timing tests PASS. A separate audit script that DOES NOT IMPORT the main science implementation uses independent direct math.fsum per-step trapezoid integration: 72 independent species-ray integral checks maximum abs discrepancy 5.421010862427522e-20, original 10,752 ray-level complete H+He closure max absolute discrepancy 1.5924219408380846e-19, original native density reconstruction max abs 0.0. Original F08 angular/time quadrature accuracy remains inherited, not re-proven continuum RT.

Primary reference: Fleury, Pitrou & Uzan, Phys Rev D 91 043511 (2015), doi:10.1103/PhysRevD.91.043511, for exact Bianchi I photon redshift and Jacobi geometry. Original S0 source state is authoritative for the chemistry; Puchwein et al. 2019 Table D1 effective homogeneous UVB MUST NOT substitute local S0 photons.

## Same-author hostile audit and claim boundaries
1. Real species H/He composition of original F08 was found via ORIGINAL 22-field physical curves. It is NOT inferred by assuming full ionization or borrowing F05. The F05 helium fraction .079 and F08 .083 conflict as donor identities: keep separate.
2. The original S0 test photon energy 13.7eV is below native HeI/HeII ionization thresholds, so photo-absorption attribution to helium would be false. Thomson scattering by retained helium electrons remains real within the model.
3. Pointwise H+He optical depths sum exactly up to numerical source interpolation/integration error. Component visibility uses common total attenuation; exp(-tau_He) alone is not a correct component.
4. Source H/He fractions are nominal original history outputs. Original external provider F09 remains blocked; global admitted cosmology, Einstein-consistent Bianchi metric, polarization and real CMB observational tau are not established. Repeated angular rays do NOT count as independent astronomical observations.
5. This unit is an original F08 **observable composition** result. It does NOT close original F05 tick160->[161] or replace REI source/atomic worker. Stop further adjacent S0 source-only maps. Next REAL central advancement must replace source-conditional S0 with a source-admitted late IGM helium history and Einstein-compatible geometry, or original owner actually admit the F05 first interval.

REI CENTRAL 28/88_REPORTED; Working33/88; PhysicalFast4/7; BASS_HE Physical14/18; canonical delta 0; PRODUCTION HOLD; no merge, force push or new IVP; distinct-author referee NOT_RUN; native subagent NOT_RUN.
