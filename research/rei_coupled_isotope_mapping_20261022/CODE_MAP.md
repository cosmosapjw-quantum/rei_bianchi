# C2: isotope-native formula, data and source map

Date: 2026-10-22. This is the source mapping for the selected C2 stage. The
completed C1 contract is reused. Numerical observations and admission belong to
this unit's finite diagnostic and report; this document does not assert that a
new coupled solver, physical branching provider or energy closure exists.

## 1. Immutable source anchors

All Git paths below are relative to `cosmosapjw-quantum/rei_bianchi`. Prefixes
resolve every shortened path in this document; line numbers refer to the pinned
file, irrespective of subsequent checkout HEAD changes.

| Prefix | Full commit | Repository-relative path |
|---|---|---|
| C1 | `9f621b684fedb9b71f2148022f6909d1760ba947` | `research/rei_coupled_isotope_contract_20261022` |
| N | `a7bff87fd7cb4c2bba1810ee8d6384ae208fb824` | `research/rei_tritium_production_audit_20261022` |
| E | `a7bff87fd7cb4c2bba1810ee8d6384ae208fb824` | `research/rei_bootstrap_energy_providers_20261022` |
| C | `8be7533cc97b3302bf42608699d6e8313ed6af8a` | `research/rei_hheli_compact_pilot_20261022` |
| A | `8be7533cc97b3302bf42608699d6e8313ed6af8a` | `research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli` |

The C2 starting checkout is `3e56bbd3d939ab235df2d47f9d012c95674d00fc` on
`research/rei-coupled-isotope-contract-20261022`. The a7 checkpoint's scientific
pilot parent is `5a1e5220b301a1c497f2863d6fd823e605faba80`. Nuclear and provider
files were read with `git show a7bff87fd7cb4c2bba1810ee8d6384ae208fb824:<path>`;
concurrent bootstrap/provider/DAG working-tree changes are not source authority
for this mapping. A historical unavailable-runtime entry in that checkpoint is
not a statement about the current runtime.

The recovered RR candidate, prefix **R**, is the exact ZIP member prefix
`recovered_local_unadmitted/providers/` in
`/workspace/scratch/d5baa30c266d/recovery_intake_c2/REI_RUNTIME_RECOVERY_CHECKPOINT_20261022.zip`,
archive SHA256
`d5efb39514fc22df573f81488c7b822500d724b2396b5bc4d8806e28e740e8ce`.
Its `code/rr_adapter.py`, `code/rr_rows.json` and `RR_ADAPTER_CONTRACT.md` are
candidate comparison inputs under this frozen C2 contract. Archived tests are
historical evidence, not new C2 results.

Concurrent publication: PR219 subsequently advanced to
`61e08967832363b611a8e5ba4167ba7b06c06b6b`, parent
`a7bff87fd7cb4c2bba1810ee8d6384ae208fb824`. Newer published scoped reviews are
available for bootstrap, supplied-moment thermal work, and scalar RR / DR
candidate work; their exact references and admission boundaries are recorded in
`CONCURRENT_UPDATE.md`. The a7 recovery/status descriptions above and below are
historical checkpoint facts. This concurrent publication does not change C2's
frozen input bytes, comparison-provider choice or prescribed finite tests.

## 2. Absolute state, initial data, time and units

`A/code/atomic_network.py:AtomicNetwork.__init__` (L75) and
`A/data/atomic_model.json:species_order` define this exact zero-based ordering.
Here A is the mass-number vector, Z the nuclear charge, and q the ionic charge.

| Slot | State | A | Z | q |
|---:|---|---:|---:|---:|
| 0 | n | 1 | 0 | 0 |
| 1 | H1I | 1 | 1 | 0 |
| 2 | H1II | 1 | 1 | 1 |
| 3 | DI | 2 | 1 | 0 |
| 4 | DII | 2 | 1 | 1 |
| 5 | TI | 3 | 1 | 0 |
| 6 | TII | 3 | 1 | 1 |
| 7 | He3I | 3 | 2 | 0 |
| 8 | He3II | 3 | 2 | 1 |
| 9 | He3III | 3 | 2 | 2 |
| 10 | He4I | 4 | 2 | 0 |
| 11 | He4II | 4 | 2 | 1 |
| 12 | He4III | 4 | 2 | 2 |
| 13 | Li6I | 6 | 3 | 0 |
| 14 | Li6II | 6 | 3 | 1 |
| 15 | Li6III | 6 | 3 | 2 |
| 16 | Li6IV | 6 | 3 | 3 |
| 17 | Li7I | 7 | 3 | 0 |
| 18 | Li7II | 7 | 3 | 1 |
| 19 | Li7III | 7 | 3 | 2 |
| 20 | Li7IV | 7 | 3 | 3 |

The helper consumes `Y_i=n_i/n_B`, not charge fractions. `n_B` is conserved
baryon-number density: `A.Y=1`, `dot n_B=-3H n_B`. Without positrons or negative
ions, `Y_e,total=q.Y`; the total includes thermal and fast free electrons.
For a resolved event, `nu=products-reactants`, `A.nu=0`, and its net free-electron
increment is `delta_e=q.nu`. The isotope-only nuclear vector has order
`n,H1,D,T,He3,He4,Li6,Li7`; `N/nuclear_network.py:inventory` (L187) sums saved
charge states into that vector and therefore discards charge-partition data.

`AtomicNetwork._prepare_inventory` (L95) uses ratios r to H1 and
`W=sum_isotopes A*r`, then sets isotope total `r/W`:

| Isotope | r | Initial charge allocation |
|---|---:|---|
| n | 0 | zero |
| H1 | 1 | neutral fraction 0.9998; singly ionized fraction 0.0002 |
| D | 2.5e-5 | neutral fraction 0.9998; singly ionized fraction 0.0002 |
| T | 0 | both slots zero |
| He3 | 1e-5 | neutral |
| He4 | 0.08112582781456953 | neutral |
| Li6 | 1e-14 | singly ionized |
| Li7 | 5e-10 | singly ionized |

These are inherited conditional initial data. Each positive isotope's numerical
scale is its initial `r/W`; n/T scales are `1e-20`. The latter is a coordinate
choice, not evidence of accuracy for newly produced trace populations. Evolve
absolute n/T abundances when their initial inventories vanish.

| Quantity | Source convention / conversion |
|---|---|
| Local time / source | Proper seconds; `dY/dt` is baryon-normalized nuclei per second; event extent R is events per conserved baryon per second |
| Density / temperature | Proper `n_B`, `n_e` in m^-3; T in K |
| Binary / unary coefficient | k in m^3/s; decay lambda or photo Gamma in s^-1 |
| Event rate density | `n_B R` in m^-3 s^-1 |
| Atomic units | RR/DR cm^3/s times 1e-6; photo Mb times 1e-22 gives m^2; eV times `1.602176634e-19` gives J |
| Nuclear input units | S0 in keV barn; sigma2200 in barn at relative speed 2200 m/s |
| Stored energies / sources | J per conserved baryon or explicitly J/m^3; volumetric power J m^-3 s^-1; RR kinetic coefficient J m^3/s |
| Outer clock | `x=ln(a/a_ref)`, `d/dx=H^-1 d/dt` where H>0; H in s^-1 |

This is a homogeneous local source problem. Its spectral boundary is the named
prescribed external field; there is no implemented spatial transport boundary.
The PR220 outer pilot uses `0<=x<=ln(7)`, `z=21 exp(-x)-1`, and prescribed
`T=100+11900 Q(z)` K with `Q=.5[1+tanh((7-z)/.8)]`. The nuclear pilot's
100–10000 K and 5–60 eV domain is distinct. C2's comparison window is
100–10000 K; donor formula controls at 1e6 K do not extend that pilot window.

## 3. Atomic operators and coefficient rows

All functions in the next table are in `A/code/atomic_network.py`.

| Formula / object | Function anchor | Existing output and limitation |
|---|---|---|
| Input loading | `_verified_inputs`, L35 | Reads `A/provenance/atomic_sources.json`; checks its ten declared files; loads model and coefficient JSON |
| Cumulative ionic energy I_i | `AtomicNetwork._prepare_inventory`, L117 | Sums `photo_VF1996[Z:q].Eth_eV`; adopted electronic-equality thresholds, without precision isotope shifts |
| Photo sigma | `photo_cross_sections`, L132 | 21-by-energy total and LiI 1s partial arrays in m^2, finite 0–200 eV API |
| External Gamma and energy moments | `_prepare_spectrum`, L165; moments L187 | Fixed quadrature, `photo_s`, absorbed, primary-kinetic and unresolved-core powers per ion |
| RR / DR row assembly | `_prepare_recombination`, L197 | Incident-ion keys `Z:q`; signed DR amplitudes retained |
| Old beta matrix D | `_prepare_decay`, L213 | n→H1II, TI→He3II, TII→He3III using the old atomic lambda values |
| Gain/loss matrix | `_transition_matrix`, L226 | Column-Y convention, outgoing diagonal loss and adjacent-charge gain |
| Prepared coefficient API | `rates`, L233 | G0 and D in s^-1; Grr, Gdr, Gne=Grr+Gdr in m^3/s; runtime 100–1e6 K, nonnegative UV scale |
| Existing complete atomic RHS | `evaluate`, L265; assembly L282 | `(G0+D+n_e Gne)Y`; includes beta and abundance dependence of `n_e=n_B q.Y` |

### Thirteen photo edges and thirteen reverse RR edges

Photo keys use the lower-charge state; RR/DR keys use the incident upper-charge
state. A dash means the process is absent from this selected finite network,
not a measured physical zero. Six isotope-resolved DR edges are explicitly
present.

| Photo direction (slot→slot) | `photo_VF1996` key | RR reverse / `rr` key | DR reverse / `dr` key |
|---|---|---|---|
| H1I→H1II (1→2) | `1:0` | 2→1 / `1:1` | — |
| DI→DII (3→4) | `1:0` | 4→3 / `1:1` | — |
| TI→TII (5→6) | `1:0` | 6→5 / `1:1` | — |
| He3I→He3II (7→8) | `2:0` | 8→7 / `2:1` | 8→7 / `2:1` |
| He3II→He3III (8→9) | `2:1` | 9→8 / `2:2` | — |
| He4I→He4II (10→11) | `2:0` | 11→10 / `2:1` | 11→10 / `2:1` |
| He4II→He4III (11→12) | `2:1` | 12→11 / `2:2` | — |
| Li6I→Li6II (13→14) | `3:0` | 14→13 / `3:1` | 14→13 / `3:1` |
| Li6II→Li6III (14→15) | `3:1` | 15→14 / `3:2` | 15→14 / `3:2` |
| Li6III→Li6IV (15→16) | `3:2` | 16→15 / `3:3` | — |
| Li7I→Li7II (17→18) | `3:0` | 18→17 / `3:1` | 18→17 / `3:1` |
| Li7II→Li7III (18→19) | `3:1` | 19→18 / `3:2` | 19→18 / `3:2` |
| Li7III→Li7IV (19→20) | `3:2` | 20→19 / `3:3` | — |

All numerical rows are in `A/data/atomic_coefficients.json`. Photo keys
`1:0,2:0,2:1,3:0,3:1,3:2` map respectively to lines 3–8 of
`A/vendor/atomic_primary/selected_photo_rows.txt`, identified by `(Z,N_bound)`
`(1,1),(2,2),(2,1),(3,3),(3,2),(3,1)`. Thresholds are respectively
13.6, 24.59, 54.42, 5.392, 75.64, 122.5 eV. This extract records numerical
rows, not byte identity with the entire remote author table.

| RR key | Source / exact row identity | A [cm^3/s], B, T0 [K], T1 [K], C, T2 [K] |
|---|---|---|
| `1:1` | VF1996_RR product `H I`; selected HHe JSON `rr.1:1` (L4) | `7.982e-11, .748, 3.148, 703600, 0, 0` |
| `2:1` | VF1996_RR product `HeI a`; selected HHe JSON `rr.2:1` (L15) | `3.294e-11, .691, 15.54, 36760000, 0, 0` |
| `2:2` | VF1996_RR product `HeII`; selected HHe JSON `rr.2:2` (L26) | `1.891e-10, .7524, 9.37, 2774000, 0, 0` |
| `3:1` | Badnell_RR_20230511 `(Z,N,M,W)=(3,2,1,1)`, original line69; local Li RR extract L3 | `8.7e-12, .364, 147, 7153000, .1508, 715400` |
| `3:2` | Badnell_RR_20230511 `(3,1,1,2)`, original line38; local extract L2 | `9.349e-11, .6916, 34.7, 7329000, .0351, 629300` |
| `3:3` | Badnell_RR_20230511 `(3,0,1,1)`, original line6; local extract L1 | `2.867e-10, .7493, 21.08, 6268000, 0, 0` |

The HHe extract is
`A/vendor/atomic_primary/selected_HHe_RR_DR_rows.json`; Li rows are
`A/vendor/atomic_reused/badnell_lithium_rr_rows.txt`. Original source-line
numbers are the donor's recorded author-table identifiers.

| DR key | Source identity / row anchors | c [cm^3 s^-1 K^(3/2)] | E [K] |
|---|---|---|---|
| `2:1` | Badnell_DR_20230512 `(2,1,1,2)`; HHe extract `He_DR`, L38 | `[.001417,.0002235,-2.185e-5]` | `[463300,553200,888700]` |
| `3:1` | Badnell_DR_20230512 `(3,2,1,1)`; original c/E lines36/1357; local Li DR L2/L4 | `[2.941e-5,6.068e-5,-7.753e-7]` | `[634500,702400,827100]` |
| `3:2` | Badnell_DR_20230512 `(3,1,1,2)`; original c/E lines5/1326; local Li DR L1/L3 | `[.0001451,.005789,1.889e-5]` | `[852900,1056000,11700000]` |

The local Li DR file is `A/vendor/atomic_reused/badnell_lithium_dr_rows.txt`.
`rates` evaluates `alpha_DR=1e-6 T^(-3/2) sum c_j exp(-E_j/T)`; a negative
amplitude must not be clipped or interpreted as a negative reaction branch.
The total number coefficient is the object checked for finiteness/nonnegativity.

### Fixed spectrum and energy meaning

`_prepare_spectrum` uses 64 logarithmic base bins, split at active atomic
thresholds and 64.39 eV. Cross sections are sampled at geometric centers;
number weights integrate E^-2.5 over each bin. The field is normalized to
`Gamma_HI=1e-12 s^-1` at unit UV scale. It accepts `13.6<cutoff<=200` eV,
with lower bound 5 eV; cutoff 60 is a distinct named field.

For LiI, `photo_cross_sections` uses `LiI_partial.PH2_2s` below 64.39 eV and
`PH1_2s+PH1_1s` above it. The one-electron charge yield is a model assumption;
the partial absorption cross section does not supply Auger/final-charge yields.
At 60 eV, LiI 1s and LiII/LiIII external photo edges lack support. At 200 eV
they have support. Neither statement addresses generated nuclear photons.

The per-ion arrays satisfy the implemented partition
`absorbed = threshold*Gamma + primary + unresolved_core`, where
`core=Li1s_event_rate*(64.39-5.392) eV`. Multiplication by `n_B Y_i` gives
volumetric power. Primary or total absorbed power is not automatically thermal
deposition. The finite quadrature supplies neither a radiation evolution nor
an energy-resolved secondary-electron provider.

### VF versus Badnell RR and the conditional energy adapter

`E/PROVIDER_REGISTRY.json:providers[verner_ferland_1996_rr]` selects the six VF
product labels `H I,HeI a,HeII,LiI,LiII,LiIII` for its own source lane.
`R/code/rr_rows.json` L7–12 contains those six rows; its recorded parent table
is `research/rei_isotope_quotient_pilot_20261022/pilot/data/verner_ferland_rr_table1_original.dat`
in the PR219 lineage, SHA256
`2382f6896fe58ee1da58c9bd563fd7d02c0d94410dbd4150767eed26a54f5091`.
The label denotes the recombined product: incident q is `Z-N_bound+1`.

`R/code/rr_adapter.py:rr_rate` (L41) returns alpha, its logarithmic temperature
slope and `lambda=k_B T alpha(3/2+dln(alpha)/dln(T))` for 100–10000 K. Its
optional `chi_J` ledger (L80) is thermal `-lambda`, ionic `-chi*alpha`, complete
cascade `lambda+chi*alpha`, in J m^3/s. Its status is explicitly
`CONDITIONAL_DERIVATIVE_OF_FIT`.

H/He VF rows coincide with the donor rows; Li does not. Recovered VF Li A
values are `1.036e-11,1.112e-10,3.039e-10` cm^3/s, with different B/T0/T1
and no temperature-dependent B correction. The donor uses the three Badnell
rows above. A VF-derived kinetic moment must not be attached to a Badnell
number coefficient. For the donor, `b=B+C exp(-T2/T)` in `rates`; differentiating
it requires the `b_dot*log[(1+u)/(1+v)]` term in
`C2_EXECUTION_CONTRACT.md`, where `b_dot=C exp(-T2/T)T2/T`.

`E/THERMAL_THEORY.md` derives the RR identity for a fixed temperature-independent
target/cross-section and heavy-target Maxwellian electron treatment. A fit
derivative carries no independent energy-moment accuracy or cascade-spectrum
validation. The donor supplies no RR/DR energy moment API. E's DR candidate
status and the donor's historical DR number-operator evidence belong to their
respective source lanes; neither supplies a new DR energy or spectral closure.

The donor manifest's ten dependencies are the two `data/atomic_*.json` files,
the two `vendor/atomic_primary/selected_*` extracts above, and six
`vendor/atomic_reused/` files: `LI_PHOTO_CONTRACT.json`, `SOURCE_MANIFEST.json`,
`badnell_lithium_dr_rows.txt`, `badnell_lithium_rr_rows.txt`,
`lithium_coefficients.json`, `provider_reconstruction.json`. Preserve their
relative paths when binding `_verified_inputs`.

## 4. Complete nuclear registry and saved event extraction

`N/NUCLEAR_NETWORK_CONTRACT.json:families` (L40; rows L41–58) is the complete
18-family authority. `N/nuclear_network.py:channels` (L44) reads
`nuclear_intake/RUN19_target_network.json` and merges dossier aliases (7,13),
(8,12), (11,19): it yields the original 13 families and omits the five declared
closure additions. Do not build the coupled mapping from `channels()` alone.

In this table S means constant S0 [keV barn], v means the thermal 1/v model
with sigma2200 [barn], and d means evaluated decay [s^-1]. Reverse status P
is `external_photo_zero`, B is `binary_detailed_balance`, and W is
`not_in_this_lowT_neutrino_free_model`. All non-decay forward coefficients are
binary m^3/s. B reverses are binary m^3/s. P is a named external-field unary
photo-rate support zero [s^-1]; W is an absent inverse weak bath, with no
admitted reverse coefficient. A stored reverse array name ending `m3_s` does
not turn P or W into binary rates.

| Saved family index / id | Nuclear reaction (gamma / beta products stated) | Dossier aliases | Forward input / provider | Reverse |
|---|---|---|---|---|
| 0 `he3_n_gamma` | He3+n→He4+gamma | 4 | v 0.00005402 / JENDL5_He3_MT102 | P |
| 1 `p_t_gamma` | H1+T→He4+gamma | 5 | S 0.00095 / Dubovichenko2019_pT_E1_model | P |
| 2 `d_d_gamma` | 2D→He4+gamma | 6 | S 0.0000058 / NACREII_section3.2 | P |
| 3 `p_d_gamma` | H1+D→He3+gamma | 7,13 | S 0.00021 / NACREII_section3.1 | P |
| 4 `p_n_gamma` | H1+n→D+gamma | 8,12 | v 0.3326 / NIST_1H_thermal_absorption_as_capture | P |
| 5 `t_beta` | T→He3+e+antineutrino | 9 | d / EVALUATED_DECAY_INPUTS.json:tritium | W |
| 6 `n_beta` | n→H1+e+antineutrino | 10 | d / EVALUATED_DECAY_INPUTS.json:neutron | W |
| 7 `t_alpha_gamma` | T+He4→Li7+gamma | 11,19 | S 0.098 / NACREII_section3.7 | P |
| 8 `d_d_p` | 2D→H1+T | 14 | S 50.8 / Viviani2023 | B |
| 9 `d_d_n` | 2D→He3+n | 15 | S 51 / Viviani2023 | B |
| 10 `d_t_n` | D+T→He4+n | 16 | S 11000 / NACREII_section3.6 | B |
| 11 `d_he3_p` | D+He3→He4+H1 | 17 | S 5900 / NACREII_section3.8 | B |
| 12 `n_he3_p` | n+He3→H1+T | 18 | v 5328 / JENDL5_He3_MT103 | B |
| 13 `d_alpha_gamma` | D+He4→Li6+gamma | closure | S 0.0000022 / NACREII_section3.5 | P |
| 14 `p_li6_alpha` | H1+Li6→He3+He4 | closure | S 3100 / NACREII_section3.12 | B |
| 15 `n_li6_alpha` | n+Li6→T+He4 | closure | v 940 / NIST_Li6_absorption_with_dominant_nalpha_channel_approximation | B |
| 16 `p_li7_alpha` | H1+Li7→2He4 | closure | S 52 / NACREII_section3.14 | B |
| 17 `d_n_gamma` | D+n→T+gamma | closure | v 0.000519 / NIST_D_thermal_absorption_as_capture | P |

Thus 18 forward + 8 B reverse + 8 P reverse = 34 directed physical entries,
including eight named external-photon support zeros. The two reverse-beta array
slots are not extra physical channels. The Li6 neutron row assigns rounded total
absorption to the dominant n-alpha channel; its conditional branch approximation
is explicit in the registry.

The registry's mode is
`instantaneously_thermalized_all_bare_nuclei_passive_reservoir_sensitivity`.
Every isotope nucleus enters the bare kernel regardless of atomic charge;
neutral fractions are not availability weights. Six bulk isotope reservoirs
are fixed in the T/n coefficient calculation. This is useful conditional rate
and event evidence, with no daughter-charge history or full 21-state evolution.

| Function in `N/nuclear_network.py` | Mapping / reuse boundary |
|---|---|
| `log_constant_s_rate`, L75 | Maxwellian constant-S quadrature; natural-log coefficient in m^3/s |
| `mass_table`, L178; `_q_j`, L209 | Bare n/p/d/t/helion/alpha masses from constants; Li atomic mass minus 3m_e, binding omitted; beta Q subtracts m_e c^2 |
| `_sym`, L205; `_logflux`, L266 | `R=n_B k product(Y_i^m_i)/product(m_i!)` for binary, `R=lambda Y` for unary; optional log T/n overrides |
| `rate_table`, L218; decay load L222 | Creates forward rates and binary inverse rates; evaluated decay source; not needed to read saved events |
| `_fast_coefficients`, L280; `propagate_fast`, L326 | Conditional 2-by-2 T/n source/hazard recurrence with fixed bulk reservoirs |
| `evaluate_case`, L366 | Forms both event directions using supplied coefficient tables, but also reruns the T/n recurrence; not a passive reader |
| `cumulative_log_events`, L146; `endpoint_ledger`, L386 | Proper-time log-linear event integration; signed stoichiometric ledger, direct positive T/n stock retained separately |
| `run`, L488; NPZ save L532 | Historical sweep/writer, not a C2 replay API |

`N/NUCLEAR_NETWORK_REPORT.json:constants` preserves actual masses, Q_J and
lambda values used in the existing result. Recomputing `mass_table()` with a
different constants installation is not a substitute for those saved values.

### Read the saved arrays directly

Both NPZ files below live under N. Logs are natural logarithms of the numerical
values in the stated SI units. The final direction axis has index 0=forward,
index 1=reverse.

| File / key | Shape | Interpretation |
|---|---|---|
| `NUCLEAR_NETWORK_LOG_RATE_TABLE.npz:T_K` | (257,) | Saved grid; approximately 100.000020405421–9998.507967455207 K |
| `...:family_ids` | (18,) | Registry order above |
| `...:log_forward_rate_m3_s_or_s_inv` | (257,18) | Binary or decay coefficients according to family |
| `...:log_reverse_rate_m3_s` | (257,18) | B inverse coefficients; P/W have status-labelled `-inf` entries |
| `NUCLEAR_NETWORK_HISTORIES.npz:case_names` | (82,) | Existing background cohort |
| `...:x,T_K` | (257,) each | Shared grids |
| `...:elapsed_s,nB_m3` | (82,257) each | Case-dependent proper clock and density |
| `...:log_T_n` | (82,257,2) | Direct stock in order T,n |
| `...:log_forward_reverse_flux` | (82,257,18,2) | Events per conserved baryon per second |
| `...:log_forward_reverse_cumulative` | (82,257,18,2) | Cumulative events per conserved baryon |

`np.load(..., allow_pickle=False)` can extract prior events without any rate
quadrature, event recomputation or propagation. `-inf` must travel with its
registry/process status: zero stock, external support zero and absent inverse
weak channel have different meanings; finite log values may underflow only
when converted to linear values. The C2 sample indices are specified in
`C2_EXECUTION_CONTRACT.md`; the observed sample belongs in the diagnostic output.

For changed Y at an exact saved T, `_logflux` can reuse cached k under the same
conditional kernels, but must form new event extents from the new populations.
Saved `R(Y_old)` is only a replay fixture for `Y_new`. Off-grid interpolation,
changed thermal domains or charge-dependent kernels need a new numerical/provider
contract. `N/nuclear_ledger_supplement.py:main` (L23) calls `rate_table` at L29
and rewrites the table; it must not be used for no-recomputation extraction.

## 5. Single beta owner and the minimal local adapter

Two existing lambda definitions must remain distinguishable:

| Definition | Exact owner |
|---|---|
| `lambda_T_old=ln(2)/(12.32*31557600)` | `A/data/atomic_model.json:weak_decay`; `A/code/atomic_network.py:_prepare_decay`, L213 |
| `lambda_T_eval=ln(2)/(12.312*365.24219878*86400)` | `N/EVALUATED_DECAY_INPUTS.json`; `N/nuclear_network.py:rate_table`, L222–225 |
| `lambda_n=1/878.4` | Both files; 878.4 s is mean lifetime, not half-life |

Their relative tritium difference is exactly
`lambda_T_eval/lambda_T_old-1=(12.32*31557600)/(12.312*365.24219878*86400)-1`
for the adopted inputs. C1 selects the nuclear evaluated JSON as the single
conditional beta-constant source in the new coupled mode. It does not alter
the historical atomic helper, model JSON or completed pilot.

The smallest beta-free atomic boundary reuses `rates(T,uv)` and deliberately
does not add its returned D:

```text
n_e = n_B * (q.Y)
F_atom = (G0 + n_e Gne) Y
J_atom = G0 + n_e Gne + n_B outer(Gne Y,q)
F_total = F_atom + sum_event nu_event R_event
```

This Jacobian holds at fixed T, UV, n_B for an all-thermal electron fixture.
Calling `evaluate` and then adding nuclear beta would double count beta.
Future thermal/fast electron partitions require `n_e,thermal` in bulk thermal
recombination and the corresponding new cross derivatives.

The three inherited spectator endpoint maps are 0→2, 5→8 and 6→9, respectively
`n→H1II+e`, `TI→He3II+e`, `TII→He3III+e`; antineutrinos are separately counted.
They are valid conditional endpoint fixtures. They do not establish physical
branch probabilities: excited, shake-off, continuum and bound-state beta
outcomes require providers. For example TI→He3III has `q.nu=2`, so a fixed
one-free-electron increment cannot represent all daughter branches.

A local adapter can accept `Y21,n_B,T,UV`, explicit thermal/fast partitions,
resolved event records and their energy allocations, and return atomic plus
nuclear `dY/dt`, `q.dY/dt`, `1.dY/dt`, and separate energy derivatives. Each
branch has a 21-component integer nu, direction/status, extent R, and source
identity. If `R_b=p_b R`, actual supplied branch weights satisfy nonnegativity
and unit sum. No isotope charge fractions are copied from hydrogen to fill
missing tritium or daughter data.

## 6. Required charge and energy provider inputs

| Required input / ownership | Existing material to reuse | Missing input for a physical coupled operator |
|---|---|---|
| Charge-resolved nuclear reactants and daughters | Complete 18-family nuclear stoichiometry and saved rates/events | Applicable charge-dependent availability/kernel and branch probabilities; isotope-only events do not select ionic products |
| Beta final states | Evaluated lambda owner; C1 spectator and shake-off endpoint algebra | Charge-state corrections, final excitation/continuum/bound-beta probabilities and spectra |
| Mass/binding reference | `mass_table`, `_q_j`, saved report constants; C1 §3 | One consistent selected neutral/ionic reference with binding convention; no silent correction of the legacy Li approximation |
| Photo energies | Absorbed / threshold / primary / unresolved-core arrays | Secondary kinetics, Li final-charge/Auger/fluorescence yields, deposition and excitation evolution |
| RR / DR energies | Number fits; conditional RR derivative identity and candidate adapter | Validated kinetic moments, target-state assumptions and cascade spectra/branching; DR energy API is absent |
| Nuclear release | Event extents and bare Q ledger | Recoil, charged-particle, photon and neutrino energy distributions/allocations |
| Thermal / fast pools | C1 common-T EOS; `E/THERMAL_THEORY.md` particle-source identity | Fast stopping, thermalization, transport/escape and any nonthermal stress closure |
| Retained / escaped radiation | E's fixed-band equation and outside-band partner derivation | Evolving photon field, spectral boundary exchange and reprocessing; prescribed UV is not that implementation |

The bare-Q convention is material: `Q_bare=-sum M_A c^2 nu_A-m_e c^2 sum Z_A nu_A`.
For consistent binding energies, C1 gives `Q_0=Q_bare+sum B_A0 nu_A` and
`Q_available=Q_0-Delta I`. One event extent must feed the single ledger
`Q_0+W=Delta I+Delta E_th+Delta E_fast+Delta E_exc+Delta E_gamma,ret+E_gamma,esc+E_nu`.
Neither assigning all Q to heat nor assigning an unresolved partition zero is
justified by the existing source functions. Subsequent fast-to-thermal exchange
subtracts from fast and adds to thermal once.

In an all-thermal diagnostic `C_th=(1+q).Y` and
`dot C_th=(1+q).dot Y`; capture changes the heavy-particle term. With fast
products, `C_th=sum Y_i,thermal+Y_e,thermal`, whereas charge neutrality uses
`Y_e,total`. `E/THERMAL_THEORY.md` calls its positive ionic energy density B;
that B is the ionization reservoir, not C1's positive bound-electron binding
energy `B_Aq`. Preserve the distinction when translating formulas.

The geometry convention remains C1's non-tilted LRS, signature (-,+,+,+),
isotropic thermal baryonic `pi_b=0`, separate nonbaryonic `pi_m`, and
`pi_r=pi_gamma+pi_nu`. Nuclear heating does not replace either shear-stress
work term. Applicable CI/CX providers remain separate required inputs if those
processes are added; their omission is not a derived low-temperature bound.

## 7. Outer adapter and compact-coordinate nonapplicability

| Source anchor | Mapping / consequence |
|---|---|
| `A/code/coupled.py:thermal_uv`, L49 | Prescribed clock/thermal/UV path above |
| `CoupledSystem.__init__`, L65; `point`, L78 | 40 geometry + 21 scaled population + tau slots; physical helper input is `Y=state[40:61]*scale`; `n_B` from geometry |
| `CoupledSystem.rhs`, L85 (chemical block L97) | `d(Y/scale)/dx=F/(scale H)`; divide by H and scale exactly once at the outer boundary |
| `CoupledSystem.jac`, L101 (chemical block L116) | `J_scaled,ij=J_phys,ij*scale_j/(scale_i H)` plus geometry/H and opacity derivatives; new thermal/radiation dependencies require new cross blocks |
| `CoupledSystem.diagnostics`, L121 (power L133) | Old prescribed-T diagnostic uses electron source because atomic heavy count is constant; new capture requires heavy plus electron particle sources |
| `C/code/compact_system.py:GEOMETRY,ATOMIC,SELECT,R,P`, L19–26 | Fixed 23 even-geometry + 9 electronic fractions + tau coordinates |
| `restrict`, L43; `lift`, L48 | Duplicates scaled isotope representatives and fixes n/T slots to zero |
| `require_eligible`, L59 | Rejects nonzero n/T and unequal initial isotope fractions; checks equality of the inherited input/rate blocks |
| `CompactSystem.rhs`, L105; `jac`, L107 | Implements R f(Pv) and R J P only on the frozen invariant subspace |

A positive n/T nuclear source lies outside the old fixed lift's image. More
generally, for isotope total Y_A>0 and charge fraction f_Aq,
`dot f_Aq=(G_Z f_A)_q+(S_Aq-f_Aq S_A)/Y_A`; equal electronic rates do not remove
the source term. Shared fractions survive only under compatible normalized
injection, such as `S_Aq=f_q S_A`. At zero isotope inventory that fraction
formula is undefined; absolute abundances remain valid.

Consequently the 21-state atomic helper is a reusable donor, while the old
compact chemistry lift cannot implement general nuclear injection. A separate
even-geometry reduction may survive parity-preserving sources. Tiny-stock
representation, off-grid rates, new thermal Jacobians and numerical solver
design belong to the next C3 work identified by this C2 mapping.
