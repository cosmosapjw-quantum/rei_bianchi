# WU R58: 원본 REI F05에서 D/H charge exchange의 역사적 열수지

2026-11-02. Repository cosmosapjw-quantum/WU088_HH. Parent WU PR #197 immutable SHA 276da121638b2a024dad639a78dbb6fcbd6e01f1. Original REI source-owner PR #367 head b9cd64afee16dc4c0e74aa39b00c831df626c777, latest research V2 owner PR #369 head 645437697d915da45147071e266bc47937e76f6c. Official tick160/131072 remains the last accepted state, original tick161 nonauthoritative.

## Original physics sources and conventions

Actual original REI #367 46,080 H/He cells × four accepted material epochs 0/64/128/160 = 184,320 original 26-event H/He/OTS/thermal rows, SHA256 5a1fe901809c9df2ce2f42aac81583f1021589958ec1799b07bfff6307ee3913. REC #195 original 184,320 cell-epoch state rows SHA256 6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c. Actual conditional WU R57 historical D evolution SHA256 d6c7068ef6b07319a8c7b4715a0c681941d6a2c3dbb068ccceb53e5b98b3100e, source R57 result JSON SHA256 02c5b3f1baea972c6a0feb0d50e5c1162c739c5f8cbe4983ed9e4d47db3748d3. Published 47 Savin 2002 rate pairs SHA256 ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8. All source SHA values checked before producer execution.

Savin, Astrophysical Journal 566, 599-603 (2002), https://doi.org/10.1086/324218, forward ground-state charge transfer D + H+ → D+ + H endothermic by approximately 3.7 meV; forward/reverse kf, kr in cm^3/s. Hypothetical D/H number fraction etaD=2.5e-5. c, hbar, kB not set to unity. Original source proper clock, nH density in cm^-3, NH number of original H nuclei per cell, energy in erg, time in seconds. Parent WU interpolation of original accepted 0/64/128/160 H/He is explicitly a source-conditional approximation, not an accepted continuous REI orbit.

## Constructive equations

Let y=NDII/ND and C(t) be signed accumulated CX ionizations per D nucleus. With source H+ x(t), native nH, and a charge-compensating H donor xeff=x-etaD*C:

Rcx = nH [kf(T) xeff (1-y) - kr(T)(1-xeff)y], units s^-1 per D nucleus.

Original-cell reaction count flux Fcx=etaD NH Rcx, events/s per native original cell. For the atomic near-resonant swap:
dNHII/dt |CX = -Fcx, dNDII/dt |CX= +Fcx, dNe/dt |CX=0, dNgamma/dt |CX=0.

For Savin nominal reaction defect deltaE=0.0037 eV, binding-energy source is BdotCX=+deltaE Fcx and isolated gas thermal source UdotCX=-deltaE Fcx, hence BdotCX+UdotCX=0, with 1 eV=1.602176634e-12 erg. Integrated source energy on 0→160 is -etaD NH deltaE C160, and on 160→161 is -etaD NH deltaE(C161-C160). All terms are signed and per original source cell. Wolfram exact symbolic charge and energy identities reduce to zero.

These are CX-only owner-compatible source candidates, NOT full REI H/He/D/RT/OTS net energy. Electron count change from D photo/EII/recomb can be nonzero, but pure CX creates no net electrons and no photons.

## Original native physical results

Original accepted REI H/He thermal state difference between tick0 and tick160, from original REC source interval centers, is -4.134584382489446e51 erg. This is an accepted-state finite difference, not a certification of the original integrated continuum RHS.

For tick0 D initial H_MATCHED (assumed y0=xHII0), signed integrated 0→160 isolated CX gas heat is +4.267942194125675e42 erg, absolute ratio to accepted H/He thermal change 1.0322542241974836e-9. For tick0 ALL_NEUTRAL y0=0, -4.087132922533429e47 erg, ratio 9.885232817699934e-5.

Original 26-event H/He instant thermal power at tick160 is -6.258030833149542e39 erg/s. Conditional CX instant thermal power is +1.0408006312701014e31 erg/s (H_MATCHED) or -1.9160249433201705e35 erg/s (ALL_NEUTRAL). Absolute summation ratios to original global magnitude 1.6663618954383128e-9 and 3.06179487259628e-5 respectively. At all 46,080 native cells, none exceeds 1% of the original local absolute instantaneous thermal RHS at accepted times 0,64,128,160 for either model initial condition. NOT a universal isotope heating bound, and the source denominator is the existing 26-event HHe RHS, not total HHeDI heat.

For unaccepted 160→161, source-conditional gross signed CX gas heat is +5.083685300857712e40 erg (H_MATCHED), -9.303704502913936e44 erg (ALL_NEUTRAL). These are NOT official accepted tick161 H/He/D states.

## Cross-model isotope energy convention issue

Original native REI #367 H chemical binding energy chiH=13.598434599702 eV, while historical WU R54 source model sets chiD=13.6017 eV from a coarser 13.598+0.0037-eV convention. To preserve the same REI native H reference and Savin nominal 0.0037-eV endothermic defect in the combined chemical bookkeeping, the conditional matched D threshold is 13.602134599702 eV. Relative to prior WU chiD the offset is +0.000434599702 eV, ~11.75% of the nominal CX defect. Savin 3.7 meV is approximate, so this is a model convention consistency proposal, NOT a high-precision experimental D ionization energy determination.

Under the fixed original R57 gross D photo-event counts, only the first-tick photoelectron candidate heat shifts by -1.2840144930735824e40 erg (H_MATCHED) or -4.309754465380885e43 erg (ALL_NEUTRAL). This is a fixed-event energy translation and does NOT incorporate a new isotope cross section, threshold-shifted PI event rate, thermal feedback or native photon redistribution.

## Actual implementation and adversarial audit

R58 producer reran original source-conditioned R57 D history and reproduced original first-tick photon counts. New original full 46,080-row history CX energy CSV.gz SHA256 fee16aef885556d87fde68af3f30c64edd703f000ed4c86a9db3861a5edeb205. Source results JSON SHA256 16dd2d039b5df5fccd36e3b7f9061ad59ecc7960287793c54d18928bee1c7c52.

A disjoint same-author standard-library audit reread original REI #367 all 184,320 source rows, original REC #195, Savin 47 published rate pairs and R58 all 46,080 source rows. Independent forward/reverse interpolation, signed thermal power, integrated CX events/heat, original owner thermal power, and parent R57 photon counts matched. Maximum rate residual normalized by gross forward+reverse rate 3.92e-15; maximum energy rate residual normalized by gross forward+reverse thermal rate 4.11e-15; integrated extensive quantities re-summed independently within 2.2e-16. Early reviewer-only comparison using near-zero net CX power as relative denominator produced a spurious 1.65e-10 worst discrepancy in cancellation cells; corrected auditor scale to gross reactant rates, without modifying the original physical model, outputs or gates.

Normal Python unittest 11/11 PASS and optimized Python -O 11/11 PASS. Same-author independent referee only. Native subagent NOT_RUN, different-author blind referee NOT_RUN. Source original 26-event HHeDI coupled chemistry+photon+OTS+thermal NOT_RUN. Actual D tick0 ionization and original dense-output continuous HHe source history unresolved. Avoid promotion to observation, CMB, or accepted source-owner tick161.

## Source governance and drift

WU 34/49 (+0), REI central 28/88 (+0), working 33/88 (+0), Physical Fast 4/7 (+0). Original accepted 160/131072; official 161 HOLD. No main merge, no force push, no original REI owner source/worker/history mutation, no production. STOP additional source-conditional isotope rate/IC/thermal atlases after this scoped unit. Next central science is original REI owner versioned 3-lane V2 full runtime/clock/14-ledger official tick161 ACCEPT/REJECT and real physical D initial data, then full joint source-coupled HHeD/photons/OTS thermal.

Disk 100% usage means R58 backup is incremental with parent WU R57 complete verified source archive as an immutable external dependency. Prior R57 full archive SHA256 ad3d9c99d14cfbd4d729c691d8766705812ff936cf15081a5870061f807d02ea already Dropbox cold restored under provider ID id:BSpOijBcT10AAAAAAEHcbg. New backup must not be falsely described as source-complete without this parent source.
