# BASS_HE: HE_EXFOR_DETECTOR_EVENT_SEMANTICS, 2026-10-29

## Authority and source limits

At start GitHub PR #107 was open/draft/unmerged at `9328ebc6f4601ec437054aeb1f60315abc8b00a4`. Read this exact HEAD's six nominated ROOT documents, extension DAG, original EXFOR `M0475.x4`, and the actual `src/reciprocity.py`. No existing file, scientific IVP or old suite was changed/replayed. The original EXFOR provenance is `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4`, blob `c49433293921dbb012d7f1b0387745732a598efa`, previously verified SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`. GitHub blob fetched and read this turn; a new whole-byte SHA check in the local runtime is **NOT_RUN** because remote bytes were not mounted. Do not claim new byte identity verification.

Arends et al., *Experimental investigation of the 4He(γ,d)d reaction*, Phys. Lett. B 62 (1976) 411–412, doi:10.1016/0370-2693(76)90671-7. Original article PDF/full text not obtained. EXFOR M0475001 records tagged bremsstrahlung, a cylindrical liquid-helium target, `METHOD=(COINC,TOF)`, `DETECTOR=(SCIN)` and **both deuterons detected in coincidence by separate TOF spectrometer arms**, each arm measuring mass, energy, angle. Kinematic overdetermination rejected accidental coincidence background. M0475002 is `(2-HE-4(G,D)1-H-2,,DA)` in `DATA-CM [nb/sr]`, `ERR-S` statistical. At 213 MeV, CM73°, `0.41±0.09 nb/sr`; at 330 MeV, CM73°, `0.07±0.05 nb/sr`. M0475003 has 201,225,253,285,320,359 MeV SIG, **no 330 MeV total SIG**. The EXFOR record does not supply a numerical 2-arm efficiency/acceptance correction, detector-response transfer, explicit single-D-inclusive vs one-event full-sphere DA normalization, or photon polarization density matrix.

Silverman et al., *d+d→4He+γ cross section measurement at 376 MeV*, Phys. Rev. C 29 (1984) 35, doi:10.1103/PhysRevC.29.35; INSPIRE report `UCLA-10-P25-79`, experiment `SATURNE-066`. The publisher abstract specifies deuteron kinetic beam energy 376 MeV, CM photon angles 73°,91°, and comparisons with Arends 2.0±0.9 and 1.7±0.9. **No original paper full text, raw inverse DA numeric row, efficiency correction, angular acceptance or beam-polarization definition was obtained.** Abstract comparison ratios are not raw DA and do not identify kappa.

A secondary Duke 1992 A=4 evaluation corroborates qualitative time-reversal compatibility. The 1985 d+p→3He+γ at Td600 MeV is an unrelated reaction and must never fill the missing `dd→4He+γ` slot. The 2000 Rice `(γ,dd)` experiment is not Arends 1976.

## Exact-s and datum-identity audit

Frozen masses from PR104: `M_alpha c²=3727.3794118 MeV`, `m_d c²=1875.61294500 MeV`. Photon on stationary alpha: `s_gamma=M²+2ME_gamma`. Deuteron incident on deuteron target at rest: `s_dd=4m²+2mT_d`. Derived exact values: Eγ213→Td375.750560607..., Eγ330→Td608.263026648..., Td376→Eγ213.125517610... MeV. Delta between Td376 and exact matched Eγ213 is +0.249439392992... MeV, `s_dd(376)-s_gamma(213)=+935.7035089781208 MeV²`. A measured point is not an exact invariant match even if its experimental energy resolution could ultimately allow a binned comparison. Published source-row identity must be checked separately from an arbitrarily specified energy argument: passing `Eγ330` to an `Eγ213` source record is forbidden even if a hypothetical inverse energy matches 330.

The unpolarized ordered ratio `(2/9)(k/q)^2` and hypothetical full-sphere event factor two are conditional mathematical branches. The detector's two-arm coincidence measurement by itself **does not** select one. Initial homogeneous gas identical-dd pair factor 1/2 is a different rate combinatorial factor. `kappa=null`, `R_event=null`.

## New actual coding work

`src/experiment_semantics.py` introduces an exact-rational source/kinematics verifier, immutable source-evidence records, separate original-publication/efficiency/acceptance/normalization/polarization requirements, source-row energy match, and a downstream bridge inventory. The gate never accepts a caller-supplied kappa or physical activation. It never transforms an abstract comparison ratio into a measured cross section. Any field present only as a string hint is marked not independently verified. This is **new scoped code**, not a production reaction model.

`tests/test_experiment_semantics.py`: 26/26 fresh focused Python unittest tests PASS, compileall PASS. Cases include Eγ213/330 vs Td376 mismatch, exact matched-s with wrong original source-energy row, detector/polarization absent, full source hint inventory still HOLD, and explicit override rejection. No pre-existing BASS_HE science suite or IVP rerun. No new independent native R6/C9 reviewer was run. Tests prove only the fail-closed behavior of the new adapter.

## Physical bridge contract (derived, NOT_IMPLEMENTED)

With alpha-target-rest photon number density `n_gamma^(alpha)(x,t,E,Omega)` in `m^-3 J^-1 sr^-1`, alpha number density `n_alpha [m^-3]`, event cross section `sigma_event [m²]` and speed `c`, a formal local event rate is

`R_event = n_alpha c ∫ dE dOmega n_gamma^(alpha)(E,Omega) sigma_event(E,Omega; beam polarization, detector-independent nuclear event convention) [m^-3 s^-1]`.

The frame energy is `E_gamma^(alpha)=-p_gamma^mu U_alpha_mu` under metric `(-,+,+,+)`. Moving sources require the full phase-space/frame Jacobian; a cold-target cross-section table cannot be evaluated directly on cosmological-frame energies. The event angular kernel yields two correlated daughter deuterons after the exact Lorentz boost, but their individual injection distribution, nonthermal transport, stopping, thermal deposition and material heat capacity `C_V` are distinct unfilled providers. An energy injection identity does **not** imply instantaneous deposited heat. A source in units of photons per H nucleus per `ln(a)` is not a verified `330 MeV` target-frame photon spectrum.

The existing `HE-FAST-IGM-RCT03C` photon-stage contract explicitly reports `COUPLED_HISTORY_OPEN`, `source_moments=null`, `full_newton_or_history=false` and a frozen single-cell scope; it is not the missing source. `HE23` density contract is per total H and makes the proper distinction from frozen neutral HI, but it does not supply the high-energy alpha-target state. `BRIDGE_CONTRACT.json` records these no-substitution interfaces without wiring them.

## Dual audit and claim gate

- PHYS-MATH: PASS for exact-s definitions, immutable spin-state/angle uncertainty and dimensionally consistent *formal* volume-rate expression. Source DA conversion/normalization remains unresolved; no polarization claim.
- PHYS-MATH-CODE: PASS_SCOPED for new pure-Python guards (26 tests); `R6_native_independent_review=NOT_RUN`, `C9_native_independent_review=NOT_RUN`, no physically calibrated cross section, no running physical source.
- P0: full text efficiency/event normalization/polarization unresolved; exact-s inverse measured numerical DA unavailable; actual target-rest photon history absent.
- P1: photon target state, D_fast slowing/thermalization kernel and `C_V` unavailable. No old full suite/IVP reruns and no numerical fit.
- P2: EXFOR errors statistical only, not a joint CI; energy/angle resolution and experiment covariance unknown.
- Physical-state invariant: `R_event=null`, `physical_activation=false`, `L4=false`, `production=HOLD`.

## DAG state and exact stopping point

Central `28/88`, HE `14/18`, PR105 `2/2`, PR106 `1/2`, reciprocity local `1/2`, previous R/C workflow `18/20`: **unchanged**. This unit is **EVIDENCE_CAPTURE_AND_FAIL_CLOSED_CONTRACT_PASS_SCOPED**, not physical event-semantics node admission. New physically completed nodes: **0**. Distinct R6/C9 remain NOT_RUN. Need obtain Arends and Silverman original full-text normalization/acceptance/efficiency, beam polarization, numerical inverse DA at the exact same invariant `s` and appropriate angle or a source-qualified energy/angle interpolation with uncertainty; then separately attach the target-frame photon and D_fast providers. Until that evidence arrives, physically meaningful event rate remains blocked.
