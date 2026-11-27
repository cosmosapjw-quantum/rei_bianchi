# WU R53 | Original REI F05 46,080-cell D photoionization and recombination, source-native photon-budget stress

2026-11-01. Completed scientific research unit in cosmosapjw-quantum/WU088_HH, contributing to the original Bianchi REI IGM. **Source-conditional physical radiation/chemistry only. NOT an admitted original REI native 26-event photon-conserving D kinetic solution.** Metric signature (-,+,+,+); original first-tick proper clock in seconds; particle densities proper cm^-3, atomic rates cm^3/s, E in erg.

## Exact authority and primary literature

Protected WU R52 Draft PR192 HEAD `0f45a3a13c8bbf277804eacc3a80e822a39a0b18`. Original REI 26-event source owner first interval F05 PR352 HEAD `ea8d6bf94197392c69f939f03c1673ed3afe349c`, SOURCE_TAR_SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted tick160 state SHA256 `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`. Original first F05 tick [160,161] remains HOLD/NOT_ACCEPTED.

Source input inherited WU R52: real REI original cell proper volumes and hydrogen nuclei (`initial_material_state_z6.npz`, SHA256 `7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d`), 85 original forcing nodes (`canonical_time_resolved_forcing_nodes.csv`, SHA256 `9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268`), 46,080 original H/He/T/electron preview source (`713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d`), REI native energy (`024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5`), R52 original 46,080-row CX-only real nH/time solution (`4b2fd9fd948bab9a6d3584092a33006225c1b3eb68e9c2047ee2ed7d4709bfce`).

Original HI recombination and photo coefficient recipes (both exact copied original source-code SHA):
- REI original `phase_space_kernel_b2c0.py` SHA256 `bd2c519a5ca9c1c8d0cfafa3050d6ead3e714b4d9e8ba97c4ac8f46567450ee5` (original case-B \(\alpha_{B,\mathrm{HII}}(T)=2.753e-14 \lambda^{1.5}/[1+(\lambda/2.740)^{.407}]^{2.242}\), \(\lambda=315614/T\) K).
- REI original `monolithic_model_b2a.py` SHA256 `4f5505e424d00cd4d7b96ff13ac0c3698d94286ae529040074ade6475762cb62` (original case-A \(\alpha_{A,\mathrm{HII}}(T)=1.269e-13 \lambda^{1.503}/[1+(\lambda/.522)^{.470}]^{1.923}\)).
- REI original `array_forcing.py` SHA256 `5c1df4c93d47198f9046e27bda3e029a7797f856fbd4dced0822efd688c557a1`: original 17 first-interval \(\Gamma_{\mathrm{HI}}\) PCHIP forcing, no substitute exponential radiation.
- Savin (2002), DOI https://doi.org/10.1086/324218, original Table1 47 paired published D+H+ ⇌ D++H rates SHA256 `ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8`. **Savin Eq (11)-(13)** explicitly says DI and HI photoionization, collisional ionization and radiative recombination rates are essentially identical to their respective H rates under the paper's model. This motivates, but does not establish precisely, \(\Gamma_D\simeq\Gamma_{\mathrm{HI}}\), \(\alpha_D\simeq\alpha_{\mathrm{HII}}\) in original 26-event photon transport. The source case B is an owner OTS effective prescription, and case A is alternative RR, **not one exact real DI recombination rate**. Full D photo cross-section and photoelectron heat require independent photon-group/level calculation.

## Finite-time isotope kinetics with exact reaction ledgers

Under source-native z_mid=5.95 throughout 17 first-interval forcing nodes, \(V_j=W_j (\mathrm{Mpc})^3/(1+z)^3\); \(n_{H,j}=N_{H,j}/V_j\). All 46,080 original source H nuclei and proper volumes match the input; first interval tick \(\Delta t=4871848749.16828\) s. The accepted parent tick160 H/He/electron/T and NONAUTHORITATIVE preview tick161 H/He/electron/T are independently read. Within the interval only, define x_HII(s) linear in endpoints, T(s) log-linear, and electron n_{e,HHe}(s) linear in endpoint source electron density. **Not source native continuous H/He trajectory.**

For initial deuterium ion fraction \(y_0\in\{0,1,y_{\rm CX,eq}(T160)\}\), assume \(\eta_D=2.5\times10^{-5}\) as a fiducial conditional abundance, and evolve **four physically distinct integrated quantities**: D+ fraction \(y(s)\), cumulative CX D ionization \(C(s)\), gross DI photoionizations \(P(s)\), gross DII recombinations \(R(s)\) per D nucleus. Let \(s=(t-t_{160})/\Delta t\), \(x_{\rm H,eff}=x_{\rm H,source}-\eta_D C\), \(n_{e,\rm eff}=n_{e,HHe,\rm source}+\eta_D n_H(y-C)\). Then
\[
\frac{dy}{ds}=\frac{dC}{ds}+\frac{dP}{ds}-\frac{dR}{ds},\quad
\frac{dC}{ds}=\Delta t\,n_H[k_f(T)x_{\rm H,eff}(1-y)-k_r(T)(1-x_{\rm H,eff})y],
\]
\[
\frac{dP}{ds}=\Delta t\,\Gamma_{\mathrm{HI,source}}(s)(1-y),\quad
\frac{dR}{ds}=\Delta t\,\alpha_{\mathrm{HII,A/B}}(T)n_{e,\rm eff}y .
\]
Exact algebraic conservation:
\(y-y_0=C+P-R\);
\(x_{\mathrm{H,eff}}+\eta_D y=x_{\mathrm{H,source}}+\eta_D[y_0+P-R]\).
Thus pure H/D CX produces zero NET new free electrons; only D photo/recomb does, per H \(\eta_D(P-R)\). The gross D photon consumption per cell is \(\eta_D N_H P\), and the total extra D electrons relative to original source H/He is \(\eta_D(y-C)\), including initial D ion electrons. The isolated **CX gas enthalpy candidate** is \(-\eta_D(3.7\,\mathrm{meV})C\) per H; no D photoelectron thermal heating, photon spectral subtraction, ionization-potential reservoir source or other gas heat is falsely inserted into REI. Inputs retain c, \(\hbar\), k_B as physical constants when needed; rate equations use no natural-unit setting.

## Real original F05 46,080-cell numerical results

With the user/source-consistent Savin original Table1 and native F05 first 17-node \(\Gamma_H(s)\) PCHIP, the integrated one-tick original HI radiation exposure is ~**0.001146964095**. New physically conditional D kinetic states:
- initial all neutral D, R52 CX-only final y median 0.0030584687963556524, R53 CX+photo+recomb case-B final y median **0.004201267915123652**, difference median **+0.0011427991187679999**. R53 final y range 0.0011539669498007712 to 0.7294392028711352.
- case B versus case A D+ final y difference median **1.2402336753078447e-10**, max 3.691301406372194e-6, within cloned-model systematic only.
- with Gamma_DI=alpha_DI=0, the R53 four-state code recovers **all 46,080 R52 y0-neutral results** with maximum absolute difference **2.220446049250313e-16** (original source/model cross-reproduction). The new response is not repackaged old data.

### Original photon owner photon-allocation stress test

Original source per-comoving-Mpc^3 native photon forcing is PCHIP-integrated over the **same source tick**. Original W_j sum 1 and original photon-rate units are s^-1 cMpc^-3. For initially all-neutral D under same frozen source gamma:
- predicted gross D photoionization demand **1.5687757586740555e59 photons**.
- original native total photon source emission over same tick **3.168714973104279e60**: DI demand / native emission = **0.04950826350712071 = 4.9508%**.
- original G1 source absorber channel **2.0716119443861184e60**: DI demand / native G1 absorption = **0.07572729839318104 = 7.5727%**.
- compare to *HI photoionizations at same original global HI Gamma*, source-native HI and HII endpoint interpolants: **7.80460735520551e59**; DI/H photocount ratio **0.20100636550635884 = 20.1006%**. In 14,256/46,080 nodes, local assumed extra DI photo demand exceeds the same gamma applied to original HI absorption. This is a genuine **self-consistency stress**, not an already-proved photon-conservation violation.
- Existing G1 instantaneous photon reservoir at t160 ~1.8070e65 and DI demand ratio 8.681566249040674e-7. Photon reservoir is not globally depleted by this one-tick DI gross demand, but the **source native allocation and absorption/current ledger** would change if an extra DI sink were physically introduced.
- If initially D is **fully ionized**, predicted gross DI photo demand ~6.247550109505182e53 and ratio to native emission **1.9716352409521632e-7**. The large contrast shows why an unsourced D ion initial state or a fixed photon field cannot by themselves support an observational EoR DI claim.
- **Not** a claim that all DI photon reactions occur in original G1 alone, nor that full original native group absorption is correctly partitioned for D threshold. No DI source photon rates were debited in the native owner. Need a full DI-specific cross section and conserving four-group photon allocation on the original source for a faithful production-level observable.
- An approximate DI PI rate cannot be treated as an *independent physical source measurement* simply because \(\Gamma_H\) was an original input. The approximation is literature-supported, while the numerical response is **derived/checked source-conditional**.

## Validation and blind-style hostile audit (same author, no subagent)

- All six original R52 inputs, R52 actual 46k CX data and three native H/He source-code files checked for exact SHA256. The new rate formulas reproduce native REI case-A and case-B source code, though no new native original 26-event transport is run.
- Normal Python 16/16, optimized -O 16/16 source/chemistry tests (scientific/implementation scoped).
- Independently inspected all 46,080 original source node H/He electron densities, per-cell nuclei/volume/clock, CX+PI+RR transition identity, gross D photon counts and CX energy; old source-compatible R52 identity PASS.
- Separate same-author 33 original REI node × 4 model/IC cases = **132 scalar DOP853 independent formulations** including source-native PCHIP, native case A/B donor, and real proper time/density. Maximum absolute y difference to producer RK4 solution **5.220207599521132e-10**, all 132 pass; full source electron/volume max rel error **2.1823963764960361e-16**, four-state isotope ledger max abs **7.758220403456841e-16**, extra D electron charge ledger max abs **0**. Different-author referee NOT_RUN, native subagents NOT_RUN.
- A naive claim "D photo demand must always be negligible because D/H small" is **not supported** for the neutral-D assumption; the owner source native first-tick 4.95% emitted photon budget requirement is nontrivial. But "D violates photon conservation" would be equally over-strong: the frozen photon source is a **conditional background**, not a photon-conserving simulation with modified source sinks. The owner must rerun allocations to establish that.
- A **strong no-go is not claimed**. All conclusions are for this one first tick with native start state, nonauthoritative end preview, source x_HII/logT/ne donor interpolation and adopted H→D photo/recombination coefficient clones. No global Bianchi null ray, CMB z0 inference, full D photo cross section, real DI spectral heating, full accepted cosmological reionization history or rigorous continuum error certification.

## Drift watchdog, promotion and next science

WU original canonical 34/49 (+0); REI central 28/88 (+0), working 33/88 (+0), Fast 4/7 (+0), accepted first F05 tick160/131072, 161 NOT ACCEPTED. This is one physical source-owned-scoped 46k-cell photon+chemistry unit **and a quantified original photon source-consumption stress**, NOT 20 newly admitted central DAG nodes. STOP further rate-sheet or simple H/D source proxy atlas work.

**Next actionable physical owner task** (not code optimization): Original REI four-group photon owner must (a) evaluate DI-specific state/source cross section or quantify the HI-clone precision, (b) allocate DI gross photo demand into source native photon absorption/current and recombination/OTS emission without double counting, (c) evolve actual D/H electron count and gas/ionization-potential/photon energy ledger jointly with the original H/He source and continuum clock, (d) accept/deny original F05 [160,161] V2 original owner rule separately. Only then can the WU R53 source-conditional DI changes be carried into central accepted observable. Current unrelated REI F08 Sachs sky PR358 is a distinct source/scenario and must not be conflated with this F05 EoR initial-state physics.

No main merge or force push, no original REI source or accepted state modifications, production HOLD, HH_R10 OFF, REI_L4=false, AUTO_NEXT_NODE false.


## Risk-justified native H electron-impact ionization extension (same R53 unit)

Self-adversarial readback exposed another source-supported D physics channel omitted from the photo+CX+RR primary calculation: native H electron-impact ionization (EII). The *original REI owner* `src/rei_bianchi/joint_sink_reservoir_history.py`, file SHA256 `4e995f9123bc98d27c65f9ca356d060225ac069acdc8bddc89335c581a3565bf`, explicitly defines
\[
\beta_{\rm HI}(T)=5.835\times10^{-11}\sqrt{T/\mathrm{K}}\,
\exp[-157804\,\mathrm{K}/T]\quad\mathrm{cm^3\,s^{-1}},
\]
with original HI collision-ionization threshold **13.598 eV**. Savin(2002) Eq12 provides the **model approximation** \(C_{\rm DI}\simeq C_{\rm HI}\), not a newly calculated D electron-impact cross section. Retain D isotope offset +3.7 meV, so the conditional EII ionization threshold is 13.6017 eV.

Add fifth distinct cumulative event ledger \(I(s)=\int n_{e,\rm eff}\beta_{\rm HI}(T)(1-y)\,dt\) per D nucleus. Source and charge-conserving D fraction satisfies \(y-y_0=C+P+I-R\), x_H,eff=x_H,source−η_D C and electron creation per H from D radiative+EII events \(η_D(P+I-R)\). The isolated **collisional ionization threshold thermal sink** (candidate original gas-energy additional term, not yet admitted) is
\(\Delta\epsilon_{\rm EII}/H=-\eta_D(13.6017\,\mathrm{eV}) I\). Do not confuse this with CX's 3.7meV endothermicity or with photoelectron gas heating, and do not double count either against the original REI H owner without a joint energy-ledger rerun.

On EXACT same original 46,080 real source cells and first F05 tick, native EII exposure \(\beta_{\rm HI} n_e\Delta t\) has median **2.692975184686726e-9**, p95 **0.010572064355401185**, maximum **0.11468493700335713**. In **5,436 cells**, EII exposure exceeds the native HI photo exposure ~0.0011469641; **2,370** have EII exposure >0.01. Under initially neutral D, five-state photo+RR+CX+EII D+ final median **0.004227477970855327**, max 0.7587505252350245; EII-ON minus OFF D+ fraction median **2.689655248305431e-9**, p95 **0.007765195857481719**, max **0.031169169024722443**. Thus the hot dense source tail requires EII.

**Energetic materiality:** candidate extra D electron-impact threshold cooling divided by absolute original native F05 integrated gas-thermal energy gain has max **0.035343612950789985 (3.534%)** and **7,062/46,080 source cells >1%**. This is **not actual source-integrated accepted gas heat**: it excludes correlated native H/He redirection, photon energy, D recombination cooling, and source-continuum uncertainties. It **falsifies a broad inference** from R52's small CX heat that all D atomic energetics are sub-percent on every source cell.

EII-on initial-neutral DI gross photo demand / original source photon emission **0.049507638306516014** versus EII-off **0.04950826350712071**; original photon-allocation stress remains qualitatively unchanged. Conditionally, photo-demand 4.95% of native emission and 7.57% of original G1 absorption are *diagnostic ratios*, not an actual added groupwise photon debit. Native 26-event photon system would need rerun to conserve source.

The producer's `r53_eii_sensitivity.py` has original-source exact SHA lock via `EII_SOURCE_CONTRACT.json`. Original 46,080-row EII-on source has 26 science columns. Programmatic no-EII limit reproduces all 46,080 original R53 source y to maximum absolute difference **0**. EII-specific tests: 10/10 normal, 10/10 Python -O. Separate same-author hostile reader checks **all 46,080** original-source rows and **45 real source nodes×3 initial scenarios =135 DOP853 five-state independent-formulation IVPs**, maximal D+ discrepancy **7.097167298297791e-10**, gross EII per-D discrepancy **5.721800810931654e-11**, 7,062 source-native >1%-thermal witnesses reproduced, stoichiometric max residual **6.561498374258075e-16**, dimensional threshold-energy source sign validated. No different author.

**One bounded stop:** R53 is now a single scientifically meaningful source-native D atom kinetics and photon-source stress result. There is no authorization to produce further WU coefficient atlases or to claim native photon-conserving REI D absorption without the owner revising the four-group photon transport and associated H/He/DI electron energy ledger.
