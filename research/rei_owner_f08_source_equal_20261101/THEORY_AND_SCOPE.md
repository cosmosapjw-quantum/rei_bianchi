# REI IGM F08: project-owner joint Sachs–H/He Thomson source-equal science
Date: 2026-11-01 | Unit: one real-source 10,752-ray observer model dataset, NOT a canonical DAG node.

## Authority / assumptions
- REI F08 PR349 immutable HEAD 58f7ffb685c3758f1fed1113ff8134a24478c3df, source pair 0a2bec874a5aa1b12f882033a08497b913b44447148b50b6082093bb354868e8.
- BASS PR315 immutable HEAD f92dd36a060e0ac8d1c592677beb9a12cb1a111f, full actual 10,752-ray source-matched Sachs/Thomson model; **head CI failed** in a strict CSV magnitude assertion, keep fail visible.
- BASS_HE PR145 immutable HEAD b659885192a8ead33431550b3eb4b073b649c6c2, original H/He proper electrons and species τ on the identical 10,752 original REI sky rays.
- Prescribed diagonal Bianchi I ds²=-c²dt²+Σ_i a_i²(t)dx_i²; H=(1.01,0.99,1)×10^-14 s^-1; matched FLRW 1×10^-14 s^-1; observer at t_o=10^13 seconds of original source proper time; no tilt, no Einstein self-consistency or present-day observer z=0.
- Fixed equal observer-relative-redshift and original electron history; original F08 source He/H=.083; **NOT** the separate F05 He/H=.079. Both redshift and H/He electron history are source-equal, not just descriptively similar.
- Prescribed conditional standard-candle attenuation uses no Thomson scattered gain, no host luminosity evolution. No new ionization IVP, photon occupation closure, observed CMB, or EoR likelihood.

## Derived exactly in the chosen physical model
Original BASS uses Sachs D_A and REI F08 τ; Etherington D_L=(1+z_rel)^2 D_A, at equal z_rel:
F_BI/F_FLRW = (D_A,FLRW/D_A,BI)² exp[-(τ_BI-τ_FLRW)].
Let Δτ_s=τ_s,BI-τ_s,FLRW, s ∈ {H,He}; species τ_s=cσ_T∫ n_{e,s}^{proper}dt along matched null ray.
Δm = 5 log10(D_A,BI/D_A,FLRW) + 2.5/ln(10) [Δτ_H+Δτ_He].
Denote the three terms G,H,E. Then for any equal-area angular sky at one redshift shell, Var(G+H+E) = Var(G)+Var(H)+Var(E)+2Cov(G,H)+2Cov(G,E)+2Cov(H,E). Cross covariance is a new physically useful geometry/electron-decomposition diagnostic, not an independent observational uncertainty. Diagonal PSTF diagnostic Q_ii(F)=angular_mean[(F-meanF)(n_i²-1/3)].

## Numerical result from original 10,752 source rays (all source hashes checked)
Finest nμ×nφ=32×64 and latest original relative z=0.09965885512610294:
- angular RMS G = 0.011238945437733761 mag
- angular RMS H = 9.716442701956435e-8 mag
- angular RMS He = 1.3030016645148201e-8 mag
- angular RMS H+He = 1.1019443999473308e-7 mag
- RMS G/RMS(H+He) = 101991.94658342966 (prescribed model only)
- mean He share of BI τ = 0.11548768141358604
- Cov(G, H+He) = 1.2384643538753691e-9 mag²
- Qxx(G,H,He) = (-0.002899477843315813, -2.504312770713974e-8, -3.35741157046444e-9) mag.
All 12 sky/time/angle groups with full covariance and Q tensor diagonal are in results/OWNER_F08_SACHS_H_HE_RESULT.json. New data are 10,752 source-based model rays, not independent observed samples.

## Source-bound validation boundary
Input triple SHA-256: BASS dbc1eaf53f04a6af765abe901b9747657ad5d9c9b17ef5157442d318c20f0d56; REI 41fb767cc6c826047abf3799164f9e5b6a970c9dc879566147ad036226e4588d; HE ef50d5670f78db66e300736cb2edf819d486263617e1b8e7fd68821b4b5afccf.
- Whole-space original first-30-column source identity is exact for all 10,752 rows; sky keys/source clock/direction match; no positional interpolator.
- max |τ_H+τ_He-τ_REI| BI =1.5924219408380846e-19; FLRW=1.0842021724855044e-19; emitter |n_e,H+n_e,He-n_e| max 1.3552527156068805e-20 cm^-3.
- max |m_new - m_BASS|=2.7755575615628914e-16 mag, BASS flux/mag algebra =0 within float output.
- 5/5 standard and 5/5 python -O targeted unit tests passed, 24 source rays 65-digit Decimal magnitudes; negative SHA tamper rejected.
- This cross-implementation check supports this **bounded downstream model output** despite BASS PR315 upstream GitHub Actions FAILURE (run 41294684156, row 2600 original strict assertion reported 0.00013066224292024504 vs 0.00013066224291976284). Do not convert CI FAILURE into PASS or edit tolerance retroactively.
- Full rigorous continuum/model error, original F08 admission, Einstein-constrained geometry and distinct-author referee NOT_RUN.

## Owner decision and canonical boundary
PROMOTE_FOR_SPECIFIED_USE: exploratory *source-conditional F08 joint scalar observer model* with exact upstream source snapshots; NOT production or canonical node admission. BASS PR315's upstream CI remains FAIL and must be repaired **in BASS**, no automatic cross-repo merge. Original F05: tick160/131072 accepted, V2 tick161 source-only shadow, V1 failure and 0→64 parity still live; original F09 provider domain blocker live.
At every listed stage: REI canonical 28/88; working 33/88 (nonadditive); Physical Fast 4/7; ΔDAG=0. NO_MERGE, NO_FORCE_PUSH, NO_OWNER_WORKER_MUTATION, NO_PRODUCTION, AUTO_NEXT=false.

Primary literature: Fleury, Pitrou & Uzan, Phys Rev D 91 (2015) 043511, doi:10.1103/PhysRevD.91.043511. Original source refs above define *code and data* authority, not this paper.
