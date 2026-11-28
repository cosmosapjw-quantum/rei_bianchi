# BASS_HE → Original REI F05 26-event native [160,161] H/He ionization-potential storage

2026-11-01 | **Scientific contributor** cosmosapjw-quantum/BASS_HE | **Original central source-owner** cosmosapjw-quantum/rei_bianchi PR #352

## Original data identities and numerical inputs
Immutable parent BASS_HE PR #145 HEAD `b659885192a8ead33431550b3eb4b073b649c6c2`. REI PR #352 HEAD `ea8d6bf94197392c69f939f03c1673ed3afe349c`, original candidate state `160→161` from unmodified four-photon-group/OTS 26-event MPRK22(1)+Alexander SDIRK2, source TAR `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, original accepted tick160 population array `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`.

Read-only native 46,080-row PR #352 *candidate physical state and nuclei* CSV SHA256 `713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d` and the same original `half1+half2` native population-increment CSV SHA256 `11df439390209bd48742ca9f4303c8743c9e14900289805e13d1ed489450a5dd` (PR #350 revised M-matrix residual enclosure). Original REI #352 all three shape-lane outputs are one identical physical dataset, not independent astronomical data; source CSV and increment CSV are fully preserved in this BASS_HE research subtree. Original #352 25,139,325-byte source-inclusive ZIP SHA256 `dd49c751a9d28ef04b2171954591efd73fe0c7e8ebc11370dc65f98bdc5b5069` is an independent previously verified owner archive. No source/solver changes, no new original chemistry IVP.

## Derivation and physical interpretation
Use original `(-,+,+,+)` convention, H/He nucleus conservation, original helium nuclei ratio `N_He/N_H=0.079` (distinct from F08 S0's 0.083), original native H/He ionization energy thresholds (eV): `chi_HI=13.598434599702`, `chi_HeI=24.587389011`, `chi_HeII=54.41776`, original energy conversion `1 eV=1.602176634e-12 erg`.

Define the ionization-potential storage of each cell, relative to neutral H/He ground states,
`B=chi_HI N_HII + chi_HeI (N_HeII+N_HeIII) + chi_HeII N_HeIII`.
Then for the actual same-parent twohalf original F05 population increments,
`delta B_H=chi_HI N_H delta x_HII`,
`delta B_He_first=chi_HeI N_He(delta x_HeII + delta x_HeIII)`,
`delta B_He_second=chi_HeII N_He delta x_HeIII`.
Therefore `delta B_He=delta B_He_first+delta B_He_second`, `delta B_total=delta B_H+delta B_He`, and charge consistency is `delta N_e=N_H delta x_HII + N_He(delta x_HeII+2 delta x_HeIII)`. Wolfram independently simplified these two exact conservation identities to `{0,0}`.

The model evaluates original source 46,080-node interval bounds on the actual `half1+half2` candidate; no independent-output box subtraction or new interval estimator is introduced. Decimal(90) arithmetic on original 17-digit serialized binary64 endpoint strings and outward `nextafter` f64 output produce a conservative linear mapping within the **inherited** source-interval validity. It does not certify the underlying interval arithmetic with MPFR/CRlibm, and does not prove continuum IVP convergence.

**CRITICAL SEMANTICS:** A negative delta B means a decline in energy *stored in ionized states*. It is **not equal** by itself to net photon emission, net photoheating, escaping energy, recombination luminosity or the change in gas thermal energy. Those require the original OTS/recombination photon, transport, collisional and heat-source ledger, not just ion populations. No direct inference about observed CMB or EoR luminosity is made.

## Actual new physical results: original 46,080 cells
Original all-cell signed ionization potential changes in erg (interval endpoints, using same physical source nuclei and twohalf source):
- delta B_H = `[-2.995529221631617e49, -2.987127346670110e49]`.
- delta B_He first = `[-7.331282027877400e48, -7.100708346703789e48]`.
- delta B_He second = `[-4.462748903533336e47, -1.911175973441380e47]`.
- delta B_He total = `[-7.777556918230735e48, -7.291825944047927e48]`.
- delta B_total = `[-3.7732849134546904e49, -3.7163099410749026e49]`.
- Helium share of *global potential-energy decrease* = `[0.19324875039377243, 0.20928170797242923]` (19.32–20.93%). This is a safe interval bound on correlated unknowns, not a unique observed fraction.
- Original candidate B_161 global storage = `[1.3762061426570774e56, 1.3762062419907658e56]` erg; original PR352 gas thermal U_161 = `[3.372024144255893e55, 3.3720305043537067e55]` erg.
- `abs(delta B_total)/U_161` = `[1.1020985534610938e-6, 1.1189970035897664e-6]`. This merely compares scales of reservoirs, **not** a claim that a latent-energy decrement is deposited in gas.

Cellwise certainty: H potential decreases 42,510/46,080; He decreases 32,220; He increases 13,074; net potential decreases 41,448; net increases 3,534; 1,098 intervals contain zero. The 46,080-cell signed electron increments match/overlap PR352 native original candidate, with global electron delta `[-1.5661331419664917e60,-1.5534971180107401e60]`, same physical source, zero new IVP/observations. Source original Three lanes are physically one dataset, not 138,240 independent cells.

Generated 46,080×19 numerical compressed CSV `results/ORIGINAL_REI_F05_TICK161_H_HE_LATENT_ENERGY_46080.csv.gz` SHA256 `3e909db856366f6eec49c60cf0e105c98d0f04ab9bf59dd26720a6dcd7d26b70`, plus numerical summary JSON and independent audit.

## Adversarial audit and limitations
Separate Python author-context implementation without importing the primary model recomputed all 46,080 species/source energy rows, same unit/electron constraints, global `math.fsum` reductions. Independent max absolute-value-scaled per-cell relative disagreement `9.775756312494516e-13` and max global relative discrepancy `1.6689999549742895e-16`; strict 10/10 normal and 10/10 `python -O` unit/negative checks PASS. Initial independent audit comparison used relative errors against heavily cancelled net quantities, caused a spurious numerical FAIL; repaired by comparing with sum of absolute terms, then all-row audit PASS. Source physics and calculations unchanged.

Potential-energy decomposition is genuinely new for actual PR352 candidate; historical PR334 calculated fixed-parent temperature-edge **defect** in binding-eV/H but not this original tick161 global ΔB. REC PR186 and WU R49 studied other material energy/support, not a substitute for this source-native absolute 46k ionization-reservoir increment.

Science admit boundary: original REI [160,161] remains UNACCEPTED because the original worker retains an independent full-vs-twohalf endpoint error box `2.1245050576368385e-4>2e-4`; candidate correlated increment upper checks and all source 14/14 ledgers do not change that formal decision. No official signed tick161 state, no 131072-tick continuation, no Bianchi Einstein self-consistency, observed CMB tau or late-IGM astronomical reconstruction. Source He opacity/Jnu/heat owner RUX03 is still UNBOUND and RUX04 P19 current-only adapter NOT_ADMITTED. Do not rotate into an adjacent atomic-source-only atlas.

REI central **28/88_REPORTED**, Working **33/88_REPORTED**, Physical Fast **4/7_REPORTED**, BASS_HE Physical **14/18_REPORTED**, CANONICAL_DELTA=0; PRODUCTION HOLD, DRAFT, NO_MERGE, NO_FORCE_PUSH, NO_NEW_IVP, AUTO_NEXT=false. Independent distinct-author scientific referee NOT_RUN, native subagent NOT_RUN. Next truly central action is original REI-owner decision on PR350/351/352 first-tick acceptance contract and source-authentic late-IGM H/He+Einstein geometry, not an extra potential-energy table.
