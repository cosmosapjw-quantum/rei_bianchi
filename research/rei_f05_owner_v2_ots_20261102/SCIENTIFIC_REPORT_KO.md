# REI Bianchi IGM | F05 original 26-event OTS source and versioned V2 candidate physical consumption

2026-11-02 KST. Owner-scoped constructive physics unit, production HOLD. Branch `research/rei-f05-owner-v2-ots-reaction-closure-20261102` stacked on REI PR #365 immutable HEAD `fab9429140038974a98f3ad3212036b0227e600e`. Source preregistration published `7c4f8ed94231342349b0d326a0fdf4b65e157485`; real science source commit `913a305f3a9483af491b781023db0b04f4b63e3f`. Draft PR #366. Do not interpret this work as an official new accepted tick.

## Original scientific target and provenance

Original F05 cosmological IGM: 46,080 source cells, five H/He populations, four photon groups, 26-event MPRK22(1) plus Alexander SDIRK2 and native OTS/thermal source. Original accepted t160 remains 160/131072. Three original first [0,64] lane states were historically byte-exact in REI #365. REC #195 actual accepted [0,64,128,160] reconstructed historical source; BASS_HE #150 actual tick160 26-event photo/collisional/recombination/OTS chemistry and heat source. Reuse *both* from their actual original source instead of substituting unrelated photon donors.

- Original 35-member F05 source TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`; original tick160 46,080×5 raw accepted array SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`; original source map SHA256 `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644`.
- REC #195 HEAD `0f1f6dbd33a654a3dd49bc2d9dbe8854b572d235`: 184,320 accepted trajectory material source rows, compressed CSV SHA256 `6674ca16ebb40607a47bed9f2eb32ed587f6a770b20bb1af6b3a988ff510259c`; JSON `f015ff77dfdc2afc022360880030aa29f06c234cac146105edbbf291fce39429`.
- BASS_HE #150 HEAD `f2d26ef196b50e69c1793cc4c29e96a248fe6c0b`: actual 46,080 H/He original reaction cells, source CSV.gz SHA256 `f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c`; science JSON `202c422e7c23da3ea93b82e35429efe387b66225107e94248e28c6263facc5e2`.
- Original prior V2 shadow t161 candidate NPZ SHA256 `eb13b86f86dfdd37ba17a7007640263b7210397be31ead24a05c5d2dbf62f90b`; freshly recomputed original source full/half1/half2 V2-shadow from actual original t160 state has NPZ SHA256 `c12f339846894a721ad7c6ad810a6b4b90a738a3972f654cfb1f199e6960c823`. Fresh pinned NumPy2.3.5, Pandas2.2.3, SciPy1.17.0 and unpinned environment both produced byte-identical fresh NPZ but **do not match** the older NPZ byte identity.

## Derived original H/He physics

Let N_HII, N_HeII, N_HeIII be source cell particle numbers and NH,NHe conserved nuclear inventories, convention (-,+,+,+), k_B=1.380649×10^-16 erg K^-1, 1 eV=1.602176634×10^-12 erg. Source electron and H/He potential and gas kinetic reservoirs:
```
N_e = N_HII + N_HeII + 2 N_HeIII
B = eV_to_erg [χ_H N_HII + χ_HeI (N_HeII + N_HeIII) + χ_HeII N_HeIII]
U_gas = (3/2) k_B (NH + NHe + N_e) T
χ_H=13.598434599702 eV, χ_HeI=24.587389011 eV, χ_HeII=54.417760 eV
```
The original source-specific rates satisfy `dB/dt = Bdot_photo + Bdot_coll + Bdot_OTS_chemical`. The original OTS source defines an unresolved accounting residual `Bdot_OTS_chemical + Qdot_OTS_heat + Edot_OTS_unresolved + Edot_OTS_escaped = 0`. This residual is NOT an independently resolved physical photon spectrum, angular emissivity, or net gas heating. The V2 t160→161 finite difference is not necessarily equal to the instant t160 RHS.

## Actual full 46,080-source-cell experiment

One physical realization; consume *source-matched* REC t128/160 accepted physical history, BASS_HE t160 original 26-event local reaction source, and actual 46,080 V2 shadow candidate161 populations/T. The original source tick duration is `Δt = 4,871,848,749.16828 s`. No original source/worker/main/history mutation. Private 20-column true source data rows `ORIGINAL_REI_T160_161_V2_OTS_SOURCE_ALIGNED_46080.csv.gz` SHA256 `a27d8b0c4c98b112a42720570a8be77887d1170fb794383d525c7e2f10fa2176`, 8,825,662 bytes, kept off public Git. Public 24 actual-cell physics witnesses SHA256 `965f59f2bbf6dc889155bf3a4454167e69d30bea17fa7dda64ca4f2c3529805d`. Source-free physics JSON SHA256 `a073b4053e941fdb2a4a3dad2a3e1607af43904d78b460476c100e2f7a0675af`.

| Source-conditionally evaluated B channel | Native physics |
|---|---:|
| Accepted [128,160] finite B secant midpoint | -7.717829799572963e39 erg/s |
| Actual original instantaneous t160 26-event net Bdot | -7.693137946550566e39 erg/s |
| V2 shadow [160,161] finite B secant midpoint | -7.686621502985467e39 erg/s |
| Candidate V2 vs original instant Bdot | -0.0008470462391775291 relative |
| V2 candidate ΔN_e midpoint | -1.5598176774473775e60 electrons |
| V2 candidate ΔB midpoint | -3.744805735464975e49 erg |
| V2 candidate ΔU_gas midpoint | -3.0481395583221614e49 erg |

Breakdown of t160 source Bdot [erg/s]: photoionization +2.1319571036199573e38, collision ionization +3.3829377326171092e38, original OTS/recombination -8.244627430174272e39, net -7.693137946550566e39. OTS source bookkeeping unresolved +8.219684688991748e39, source-defined escaped +2.3520705627657136e37, OTS heat +1.42203555486775e36 and primary photoelectron excess heat +8.22713274931735e37. Do NOT add these to observed luminosity or CMB.

All original 230,400 population coordinate intervals and 46,080 logT intervals in newly recomputed and prior V2 candidate overlap; disjoint 0/276,480, max population midpoint relative difference 4.167442377861142e-16, max logT 2.1149082046919582e-16; the true parent arrays have exact byte equality. Semantic interval overlap does not imply independent *formal* MPFR global interval enclosure.

V2 source-scoped original post-map gate: source original historical V1 `logT upper = 2.1245050576368385e-4` > frozen local gate `2e-4`, FAIL; existing V2 common-parent source local logT `5.387144148931529e-6 < 2e-4`, PASS. Source 14 native conservation ledgers include zero, zero table events, frozen width gate 2e-3. **Owner cannot infer canonical acceptance from shadow pass**, nor equate one-tick candidate/instantaneous RHS difference 0.0847% to a physical/global error bound.

## Implementation and independent adversarial review

`consume_source_causal_energy.py` independently reads the original sources with full SHA gates, conserved nuclei source intervals and original time, verifies old-vs-new V2 interval intersection, reads all BASS original cells and compares event-photo/collision/OTS chemistry and energy identities, and generates real 46,080 row source-aligned physical output. `audit_independent_causal.py` has no dependency on the generating program and rereads the REC 184,320 rows, BASS 46,080, private new 46,080 and 24 witness rows. Independent max scaled 26-event Bdot chemistry residual **6.31928570757506e-16**, OTS source energy residual **1.0860779549515173e-16**, all checked; independent science audit receipt SHA256 `3ddab662d020dee650d79454d925d287a0d36aea5bdac8e451213fe33a42ab4d`.

46,050/46,080 local cells have the same sign for instantaneous t160 Bdot and candidate secant. Remaining 30 cells contribute only 2.795179180962394e-9 of the total sum of |original Bdot|. This is a quantitative global weight, not a guarantee of local state accuracy. Test `python3 -m unittest discover -s research/rei_f05_owner_v2_ots_20261102/tests -v` **5/5 PASS**, including explicit false official tick161 negative control. Both source-free GitHub CI runs at science commit `913a305f3a9483af491b781023db0b04f4b63e3f`: science #41362009222 SUCCESS; generic repo verify #41362009215 SUCCESS. Distinct-author blind referee / native subagent NOT_RUN; this is a same-author disjoint-implementation adversarial check.

A preserved failed pinned-env run with `PYTHONNOUSERSITE=1` accidentally selected ABI-incompatible system SciPy 1.x. After removing only that *run environment flag*, the existing pinned NumPy2.3.5/Pandas2.2.3/SciPy1.17.0 old source genuinely executed (with preexisting optional extension warnings) and produced the same candidate payload as new unpinned run. This is an environment-resolution failure/repair, NOT a source-physics modification or evidence of exact original historical complete worker fingerprint.

## R8 admission and drift watchdog

**PROMOTE_FOR_SPECIFIED_USE** original owner F05 true 26-event tick160 Bdot source and its source-aligned candidate161 H/He chemical/thermal/electron *derived physical diagnostics*, conditional on original t160 source, REC historical accepted state, and V2 shadow candidates. **HOLD** true original runtime job/worker/continuum ODE source authority, old historical V1 [160,161] failure and canonical F05 tick161; official accepted tick remains **160/131072**. This is no new canonical DAG node: CENTRAL 28/88; Working 33/88; Physical Fast 4/7, canonical Δ0 at every selected stage. Original Rust recovered EOS in REI #360/#363 is not misrepresented as the 26-event full production solver.

Original source/worker/main/history unchanged; no merge/force push or error gate reset. Read-only donor BASS_HE #150 OTS energy was actually adopted only into source-equivalent **diagnostics**, not inserted into the original worker as a new source. REC #195 time-resolved source is likewise consumed for the accepted secant. BASS_CR #162 excitation not double-added. Next original scientific gate is explicitly *versioned F05 V2 worker runtime-contract migration* with all three accepted predecessor lane states and actual original source-clock/14-ledger/2e-4 gates, followed by a real owner ACCEPT/REJECT for tick161. Stop other optional micro-rate atlases, process-only PR proliferation or external CMB proxies.
