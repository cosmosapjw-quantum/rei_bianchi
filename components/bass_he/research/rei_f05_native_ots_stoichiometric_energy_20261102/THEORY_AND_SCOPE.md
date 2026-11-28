# BASS_HE → original REI F05 26-event H/He OTS stoichiometric energy closure

2026-11-02 KST | New source-native R theory unit, not a new original IVP | DRAFT/HOLD.

## Authority and nonduplication
Immutable parent: BASS_HE PR149 HEAD 64e121a1980358134e59b303414c2d54964360de. Native REI PR355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00, accepted original tick160/131072, 46,080 cells. Original source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b; accepted array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; native kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644; source RHS SHA256 b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36.

Original REI source is authority for native photo currents, 26-event rates, H/He collisional ionization, recombination, on-the-spot (OTS) branching, excess heat and source proper time. BASS_HE PR149 already computed positive photo-only binding energy; this new unit connects it with *original full 26-event net chemical energy* and explicit OTS radiation residual/escape. Do not duplicate REC194 Compton, BASS_CR162 excitation cooling, BASS326 F08 Rust first-stage, or REI fast347 full-vs-twohalf thermal-root integration.

## Physical definitions and exact algebra
Conventions: metric (-,+,+,+), source gas proper frame, original proper time seconds, per-cell particle counts and cgs erg/s. EV=1.602176634e-12 erg/eV, chi_H=13.598434599702 eV, chi_HeI=24.587389011 eV, chi_HeII=54.41776 eV. Ionization-potential energy:
B=EV [chi_H*N_HII + chi_HeI*(N_HeII+N_HeIII)+chi_HeII*N_HeIII].
Its exact source derivative from original net population RHS is
Bdot_net=EV[chi_H*dN_HII+chi_HeI*(dN_HeII+dN_HeIII)+chi_HeII*dN_HeIII].
Native source three ionization event rates: r_HI=r_HI_photo+N_HI*n_e*beta_HI(T), r_HeI=r_HeI_photo+N_HeI*n_e*beta_HeI(T), r_HeII=r_HeII_photo+N_HeII*n_e*beta_HeII(T), n_e=(N_HII+N_HeII+2N_HeIII)/V_proper. The originally source-defined reaction graph has 9 event categories: HI/HeI/HeII ionization, HII caseB recombination, HeII ground/caseB recombinations, HeIII ground/n2/cascade recombinations.

Define P_photo=EV sum_s chi_s*r_s_photo; P_coll=EV sum_s chi_s*r_s_coll. The original REI recombination/OTS chemical rate C_OTS obeys a stoichiometric equation that can be checked independently against the original event operator:
Bdot_net=P_photo+P_coll+C_OTS.
Original source defines resolved OTS heat Q_OTS, escaped Ly-alpha E_escape, and a **residual** E_unresolved=-C_OTS-Q_OTS-E_escape. Thus exact SOURCE energy ledger identity:
Bdot_net + Q_OTS + E_escape + E_unresolved = P_photo + P_coll.
This is NOT full radiation+gas energy conservation. The original residual is defined to close this event graph; it does not specify a spectral, angular, spatial or escaped-photon transfer emissivity. Gas thermal cooling, expansion, recombination thermal losses, primary photo-electron heating and electron-collisional kinetic sinks require separate source terms and cannot be appended twice.

## Experimental contract and uncertainty
- Source-realized representative point: use immutable original accepted 46,080-cell population intervals with original edge.element_conserving_parent_candidate and midpoint log-temperature. This produces one nuclei-conserving interior *component-box* point, not a certified point in the full correlated history set; evaluate exactly the original source event operator, and output real native 46k-cell source data.
- Independently use original continuous RHS rhs_details on interval-coordinate original accepted source and its prescribed Hummer-Seaton v(T) policy (strict sub-10^4 K v∈[0,1]; f=0.1). Do not invent a smooth OTS table extrapolation. Compare numerical point and interval bounds, especially chemical/OTS unresolved/escape. The original source accepted state is at 160/131072 only.
- Cross-check event stoichiometry, signs, electron/nuclei balances and exact original source rate identity; Wolfram symbolic recombination identity independently, with arbitrary P_EXC coefficient. Test native 12 group/species photo receipt against parent PR149 (no P19 incident photons).
- Compare a hypothetical constant frozen derivative step against original *NONAUTHORITATIVE tick161 preview* only as a diagnostic; not an integrated prediction or acceptance gate. No real full-F05 V2 admission, no Bianchi geodesic or observer CMB.
- Runtime env optional NumPy1 ABI import warnings under NumPy2: separate from failed execution. Output success only from real command/exit, SHA and cold replay.

## Preservation and stop
No original chemistry, solver, worker, parent, production, main, source acceptance thresholds or photon groups changed. Exact F05 frozen local error 2e-4 remains untouched; historical tick161 not accepted. Canonical REI=28/88_REPORTED, working=33/88_REPORTED, fast=4/7_REPORTED, BASS_HE physical=14/18_REPORTED; canonical delta 0. BASS_HE may publish one isolated Draft/HOLD with source-native event/energy data and a compact R1-R10/C1-C10 ledger; this is one scientific output, not 20 canonical DAG nodes. After the bounded experiment stop auxiliary source-atlas work; next central IGM owner needs causal spectral-angular photon/OTS emission and full source-matched evolution or versioned original F05 acceptance.

Literature methods: Mellema et al. 2006 C2-Ray doi:10.1016/j.newast.2005.09.004 and Friedrich et al. 2012 helium coupled OTS doi:10.1111/j.1365-2966.2012.20449.x. Literature is not local source authority.
