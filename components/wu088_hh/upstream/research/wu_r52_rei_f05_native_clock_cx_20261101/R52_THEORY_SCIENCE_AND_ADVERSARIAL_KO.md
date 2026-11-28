# WU R52 | Original REI F05 proper-density and proper-clock source-conditioned deuterium transient

Date 2026-11-01. Task: one actual physical-data and time-evolving isotope model unit for cosmosapjw-quantum/WU088_HH, supplying original cosmosapjw-quantum/rei_bianchi 26-event IGM. Only source-conditional finite-time H/D **atomic charge exchange** is modeled, not whole real EoR chemistry or full Einstein-Boltzmann. The result is new because R51 computed stationary donor fractions only and lacked original proper gas density and clock.

## Source authority and exact identities

- WU immutable source parent: Draft PR #190 HEAD a42fa9113573a588ef2033ef6bbad2d9b3f87f94; PR #191 was closed duplicate.
- REI original accepted 160/131072; original F05 source tar SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b and accepted state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01.
- Immutable REI nonauthoritative tick161 physical preview PR #352 HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c; original H/He/T preview CSV SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d.
- Original F05 energy (REI PR347) SHA256 024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5. This comparison measures native integrated thermal change per H, not global gas/U production forecast.
- NEW source: original 46,080-node `initial_material_state_z6.npz` (SHA256 7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d), and original canonical 85-node first-five-interval forcing CSV (SHA256 9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268). REC→REI PR #191 independently confirms these exact original source volume/clock definitions, but it is another science consumer not the REI owner.
- Original published Savin (2002) 47 paired D+H+↔D++H rates, DOI 10.1086/324218. Table1 source CSV SHA256 ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8. Only author-published original tabulated rounded rates, 2.7–2e5K range and declared log-log interpolation; not unpublished raw quantum rates. Table2 fit source JSON SHA256 b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc.
- Correct time/density source identity: all 46,080 node source tick160 H nuclei N_H equal original initial_material_state_z6 arrays exactly. Original weights W_j>0, sum W_j≈1. Original first interval 17 forcing nodes all z_mid=5.95 EXACT; source code comoving_volume=W_j*MPC_CM^3, proper volume=that/(1+z)^3, MPC_CM=3.085677581491367e24 cm. Original forcing time duration=638562959250984.8 s; original first canonical tick length delta_t=4871848749.16828 proper seconds (duration/131072). We use the accepted tick160 to conditional tick161 *same interval*, t0=160 delta_t and t1=161 delta_t.
- Actual n_H,j=N_H,j / V_j in cm^-3. Distribution across source 46,080 nodes min 3.65044845917404e-7, median 7.218740716196057e-5, max 1.6298971317818243e-2; p05=6.394790161769437e-7, p95=9.375162770707378e-3. These values are not deduced by mistaking cell nuclei numbers for densities.

## Explicit conditional theoretical map, not yet a full REI physical isotope solution

Metric (-,+,+,+); original REI clock source in proper seconds; no c=1 or k_B=1 assumptions needed. Let s=(t-t160)/delta_t from 0 to1, y_j=n_D+/n_D, eta_D=2.5e-5 an explicitly assumed D/H nuclear scenario. Original H/He donor endpoints are accepted tick160 x0,T0 and PREVIEW tick161 x1,T1. Full native continuous original H/He 26-event material history is NOT in the current source. For a reproducible deliberately declared closure, use x_source(s)=(1-s)x0+s x1, ln T_source(s)=(1-s)ln T0+s ln T1, and n_H,j fixed by the original constant first-interval zmid. This is a piecewise donor interpolation across source endpoints, not a claim that original H/He solver followed a linear path.

The charge-exchange-only net reactions are
D(1s)+H+ → D++H(1s) with original Savin k_f(T) cm^3/s,
D++H(1s) → D(1s)+H+ with original Savin k_r(T) cm^3/s.
For constant nH within this actual original first tick and original frozen H/He donor x_source(s), retain the finite D/H charge compensation
x_H_eff(s)=x_source(s)-eta_D[y(s)-y0],
dy/ds=delta_t*nH*[k_f(T(s))*(1-y)*x_H_eff(s) - k_r(T(s))*y*(1-x_H_eff(s))].
Therefore (x_H_eff+eta_D*y) -(x_source+eta_D*y0)=0 exactly for every source cell. H and D nuclear numbers are each separately constant, and pure H/D charge exchange alone creates ZERO net new free electrons. The original H donor is not rerun with this isotope feedback; the above compensates exchange charge while treating original source photo/thermal H/He updates as externally prescribed.

Original source energy difference is 3.7 meV per *net* D0→D+ charge-exchange event, with forward reaction endothermic; net gas heat per H nucleus is q_CX=-eta_D*(3.7 meV)*[y_final-y0]. This is not included in original H/He thermal worker and is a candidate additional physical source only if original owner later binds complete H/D radiative and chemical energy.

We use **three independent physically explicit initial conditions** y0=0, y0=1 and y0=y_eq_CX(T160,x160). None is claimed the observed/reionization-epoch true D initial distribution. RK4 is run with 16,32,64 substeps, with 64 as output, and independently checked against 156 scalar high-accuracy DOP853 calculations at 52 distinct real source cells. Endpoint-frozen donor control profiles provide one measure of dependence on the chosen H/He intertick interpolation, NOT a validated global bound on unknown continuous source history.

## Quantitative original-source science (all 46,080)

Proper hydrogen density min 3.65044845917404e-7, median 7.218740716196057e-5, max 0.016298971317818243 cm^-3. Native first tick dt=4871848749.16828 s. Actual one-tick CX exposure theta=int nH [k_f*x + k_r*(1-x)]dt has min 7.670715781706362e-6, median 0.003063287419894245, p95 0.4378585319116079 and max 1.3062208687657195. **26,976 of 46,080** source cells have theta<0.01, while 9,918 have theta>0.1, and theta>1 only in densest original cells. Most one-tick source cells cannot relax from arbitrary D initial state to the formal stationary ratio derived in R51.

For initially all-neutral D: y_Dplus final median=0.0030584687963556524, p95=0.35217110415021874, max=0.7291298780436827. For initially all-ionized D: y_Dplus final median=0.9999997765930001, min=0.9972268655390162. For initial CX-equilibrium D: y_Dplus final median=0.9999431515689168. This large initial-condition memory is **actual time-dependent conditional chemistry driven by original nH and delta_t**.

Original source F05 discrete thermal increment per H is compared to net isolated CX energy:
- Initially D neutral: median q_CX/abs(native thermal gain) = -0.00013936625090356242 = -0.0139366%, maximum absolute ratio 0.0026421259619293334 = 0.2642126%.
- Initially D ionized: median = +7.939154060533681e-9 = +0.000000793915%.
- Initially CX-stationary D: median = +1.2287696025936959e-12.
For ALL 46,080 cells and all THREE initial scenarios, there are ZERO cells with |q_CX| greater than 1% of |native original F05 thermal gain|. This is **source/one-tick/D-CX-only** conditional materiality, not an admitted no-go for HD cooling or D radiative chemistry.

Source original HI photoionization exposure comparator Gamma_HI(t160)*delta_t=0.001146964327678511 (source time interpolation of first-interval 17 nodes); 19,872 original cells have theta_CX below that **hydrogen** photo diagnostic. D photo cross-sections and D photons have NOT been evaluated and Gamma_HI does NOT equal Gamma_DI; this diagnostic underscores an important omitted process of potentially similar scale, not a D photo chemical prediction.

## Numerics, signed conservation, and adverse self review

- Normal and Python -O 15/15 full source-specified software/science tests. Original six source SHA256 checked at every source construction. Exact 46,080 original tick160 H-nuclei array equality with source z6 NPZ and correct actual proper volumes.
- Source original full state input, output y and charge/energy identities re-read independently across **all 46,080** original rows; finite proper density and source times verified. Same-author independent SciPy DOP853 at **52 original nodes × three initial D scenarios = 156 scalar IVPs**, max y absolute difference compared with vectorized RK64 **5.203432129619046e-10**. RK32 vs RK64 max abs y diff for initial neutral **7.948325886353302e-9** (not a formal global bound).
- Source interpolation sensitivity: frozen-left/right donor vs endpoint-log-linear source, neutral initial maximum |delta y| **7.0437647269328e-6**, median max |delta y| 2.812420118840364e-10. This probes one family of approximations only and cannot certify a continuum H/He owner trajectory. No separate neutron/HD/He isotope source beyond Savin data.
- The original source-native H/He endpoint tick161 preview is still NONAUTHORITATIVE and cannot be called a newly accepted REI history, even if V2 shadow physical map has passed. Latest original owner F05 PR356 was Draft/HOLD with central DAG28/88 when checked. The older R51 source-conditional stationary ratios did not include proper nH and should not be promoted to real one-tick reaction histories.
- The strongest hostile attack: original D neutral can be very far from H ionization in the no-photo CX-only model, while original H photons are strongly ionizing; the neglected deuterium photoionization and recombination could change y substantially. An original D-specific photo/recombination source owner is needed before physical reionization claims or adding the q_CX term to REI thermal equations. The original 26-event H/He photosource, energy/power ledger, Einstein geometry, actual observed polarization and continuum error remain untouched.
- Second hostile attack: adopting 46,080 native proper cell densities does not produce a Bianchi null ray or observer redshift; no LOS tau or CMB likelihood prediction is issued. No physical tick161 admission, production or main merge. No native subagent or distinct-author referee; only bounded same-author alternative algorithm check. No strong no-go claim.

## Drift watchdog and stop

The R51 blocker "no proper nH and clock" is actually CLOSED for this exact first-tick original source by reading its genuine geometry and forcing, not by fabricating input. One actual new 46,080-cell non-equilibrium source physical dataset is obtained; no additional adjacent rate-coefficient/proxy atlas needed. Once independently tested and backed up, **STOP WU speculative isotope closures** until original REI owner provides D-specific photoionization/recombination plus source-matched photon energy and an accepted H/He/geometry trajectory.

WU canonical 34/49 (+0), REI central 28/88 (+0), working 33/88 (+0), Fast 4/7 (+0). Original official accepted tick160/131072, first [160,161] HOLD. WU HH_R10=OFF, REI_L4=false, PRODUCTION=HOLD, NO_MAIN_MERGE, AUTO_NEXT_NODE=false. The 20 R/C stage evidence entries are ONE model construction, not 20 central scientific node admissions.
