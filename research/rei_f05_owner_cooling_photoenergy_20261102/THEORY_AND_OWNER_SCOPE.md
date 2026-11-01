# REI Physical Fast F05: original-group photoenergy × existing H-excitation cooling

Date: 2026-11-02 Asia/Seoul. Bounded next theory/coding unit: consume already-verified BASS_HE #149 and BASS-CR #162 **real original F05 tick160 source data** into one mathematically explicit thermal-source owner test. This is NOT a new source atlas, extra atomic process, simulation, or canonical DAG node. Single PR stacked on independent original Rust/source first64 owner PR #363 exact immutable HEAD `abf83d4d883d5f311426b7f02cb001e70138ceb4`. No main, worker, source, budgets, tolerances, or historical state edits.

## 1. Source authority, identity, units, clock

1. Original REI source F05 26-event TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; accepted tick160/131072 state SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`, N=46,080. PR #363 reproduced original [0,64] state SHA256 `aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425` byte-identically; this does NOT establish original runtime identity, nor authorize [160,161].
2. Four native original-group photochemical and primary excess-heat power envelopes from [BASS_HE #149](https://github.com/cosmosapjw-quantum/BASS_HE/pull/149) HEAD `64e121a1980358134e59b303414c2d54964360de`. Source 12-group×species CSV SHA256 `73f1c739ab1ea3d940abca44edacca4a54e94e3a937a25a98b63fd065bd8bfc3`, source science JSON `d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8`. Original REI #363 already independently consumed this; DO NOT re-claim an independent source-node contribution.
3. Source H-excitation cooling's 1s→2p physical partition from [BASS-CR #162](https://github.com/cosmosapjw-quantum/bass_cr/pull/162) HEAD `7c6c0c4a9d025dc72a80de6bddf2865cb68690b4`. Source-result JSON SHA256 `0ea4e8cb985f018ce35f69fa874638170e7a693d379f61da72935ed381a7a693`, 12,528-row physical subset CSV.gz SHA256 `0ba8549b289d5d3656afb7957fbc0e585fc6182f070e3ebe839bfc0d24c86e9c`. 12,528 cells in 5000–20000 K supported; 33,552 excluded and not extrapolated.
4. Same original REI reduced RHS Git/source SHA256 `b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36` explicitly shared by both supplier science JSONs. Same accepted state/time: BASS_HE native proper time `779495799866.9248 s`; BASS-CR native single-tick proper ∆t `4871848749.16828 s`, and 160∆t=779495799866.9248 s. **This is the actual equal-source-clock and rate-owner bridge**, not just matching project names.
5. All powers are physical proper-time **erg/s**, integrated over source proper cell volumes, not energy density, line photon escape, or observer luminosity. Photo binding-power is **gross positive photoionization-potential storage**, not net dB/dt or negative integrated prior [0,64] ∆B.

## 2. Constructive energy partition (R5)

At accepted tick160, for a species s and ionizing group g, original native-group allocated event current is R_sg = J_g q_sg [events/s]. BASS_HE native positive powers:
  P_bind = (1 eV to erg) Σ_sg chi_s R_sg,
  P_heat = (1 eV to erg) Σ_sg epsilon_sg R_sg.
Original group s=HeI normalization uses total helium, s=HeII uses total hydrogen as in REI #355; no external PW19 spectral replacement. Exact photon-origin local electronic input P_bind+P_heat, not full gas kinetic heating.

The original REI reduced_interval_rhs already includes hydrogen excitation cooling:
  Lambda_H,legacy(T) = 7.5×10^-19 exp(-118348 K/T) / [1+sqrt(T/(10^5 K))] erg cm³/s,
  P_Hexc,j = n_e,j n_HI,j V_j Lambda_H,legacy(T_j).
For supported temperatures 5000≤T≤20000 K, BASS-CR source 1s→2p candidate has P_2p,j = E_12 (n_e n_HI V)_j q_12(T_j) and exactly P_legacy,j=P_2p,j+P_remnant,j at frozen original local material state. P_remnant>0 for all supported interval enclosures. The **remnant is a phenomenological residual, not identified with concrete 2s/higher levels**.

Thus ADDING P_2p to original H excitation cooling is physical double-counting. REPLACING the whole original H excitation cooling with P_2p discards P_remnant. Neither is approved; no original solver changes.

## 3. New owner cross-repository source-conditional inequality

From original source raw physical inputs:
- Global original 4-group primary photoheat P_heat_all ∈[8.214929208940958e37,8.23934628923953e37] erg/s, across ALL 46,080 cells.
- Existing original H excitation cooling on ONLY the 12,528 source-supported cells P_legacy_subset(midpoint) = 1.4642738832064828e38 erg/s.
- Source 1s→2p partition P_2p_subset(midpoint)=8.216438058687765e37 erg/s; source phenomenological remnant P_rem_subset(midpoint)=6.426300773377064e37 erg/s.
- Consequently *conditional on the source-midpoint H cooling calculation*: P_legacy_subset / P_heat_all ∈[1.777172401551812,1.7824546578110467].
- The selected-channel partial kinetic term P_heat_all - P_legacy_subset lies in [-6.42780962312387e37,-6.403392542825297e37] erg/s, **not** the total gas heat balance and NOT a rigorously bounded full-source kinetic IVP derivative.
- P_2p_subset/P_legacy_subset = 0.5611271329032599, while P_2p_subset/P_heat_all ∈[0.9972196543575692,1.0001836716675738]. Therefore one cannot even definitively order *the 2p-only* cooling and all-space primary photoheat; do not turn a ~1 ratio into claimed thermal balance.
- Binding-power fraction P_bind/(P_bind+P_heat) ∈[0.720922713930227,0.7221861214092231] from original BASS_HE and REI #363. This is a gross photonic source partition, not a solved net chemical source.
- F05 rate-current group3 is subnormal (`J3≤1e-323 s^-1`); no significant HeII hard-photon energy injection is admitted despite nonzero formal opacity share.

The inequality is a *source-conditioned scale comparison* and is not a rigorous interval enclosure for P_legacy_subset: BASS-CR published summed P_legacy is from **original-cell midpoints**, while the BASS_HE primary heat is interval-valued. The positive original H excitation coefficient outside 5000–20000 K is not newly integrated here; no assertion about total all-cell cooling or observed sky is made.

## 4. R6 blind-referee self-check and owner admission

Falsification gates: strict published source byte SHA and source-clock/RHS equality; independent 12-row original native photon re-sum; independent 12,528-row source cooling re-sum and physical-positive remainder; verify H excitation exists in original RHS; positive chemical binding/heat sign and physical dimensions; exact source-only 2p partition; no unapproved 26-event map or native worker replacement; original V1 logT=2.1245050576368385e-4 > frozen 2e-4 failure preserved; original V2 scoped research cannot automatically revise official accepted tick160/131072. Distinguish midpoint/interval and supported 12,528 versus all-space 46,080.

**Proposed project-owner scoped admission:** BASS_HE #149 already admitted by REI #363; reuse directly. BASS-CR #162 ADMIT only as original H excitation overlap constraint / non-double-counting and as the measured subset source-based midpoint partition, NEVER as additional native term or replacement. REC #194 optional isotropic CMB Compton cooling is a DIFFERENT radiative bath and may not be inserted into original four-group source. BASS #326 20 native coupled F08 stage results remain donor-provisional until original source-inclusive data and independent validation are published. Native subagent and separate-author referee NOT_RUN; one same-author adversarial numerical pass planned, no recursive audit.

DAG each stage REI Central 28/88, Working 33/88 nonadditive, Physical Fast 4/7, delta 0; original F05 official tick160/131072, production HOLD. Next true canonical action: PR #363 original 0→64 historical state parity into original **versioned V2 worker runtime** with exact owner/source/policy identity and same old gates, then explicit original tick161 ACCEPT/REJECT; or source-equivalent full F08 photon/HHe/thermal evolution. Stop additional source-only atlas PRs and optional source adapters. 

Primary literature relevant to source physics: Abel et al. (1997), New Astronomy 2, 181, DOI 10.1016/S1384-1076(97)00010-9; Furlanetto & Stoever (2010), MNRAS 404, 1869, DOI 10.1111/j.1365-2966.2010.16401.x. The code/source identity above, not the papers, binds the actual F05 model.
