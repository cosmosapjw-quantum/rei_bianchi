# WU R51 | Savin(2002) original D/H atomic charge exchange on REI F05 46,080 physical cells

2026-11-01. Scope: WU088_HH owned isotope microphysics of the **original REI Bianchi IGM**, not an additional optional coefficient atlas. One source-conditional physical consumer on real existing H/He/T states, no original REI mutation.

## Exact authorities

**WU immutable parent** Draft PR #189 HEAD b711a6a7f6bfae257f0bcbcea44cad52b8086fc0.
**REI physical source owner** Draft PR #352 HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c: original 26-event four-photon-group 46,080-cell tick161 H/He/T **NONAUTHORITATIVE PREVIEW**, not accepted. Original PR347 accepted tick160 native source energy used as independent energy materiality comparator.

Frozen original REI source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, accepted array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01, native original H/He solver kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.

The original primary REI tick161 preview CSV.gz SHA256 713b46a0da8931cc6f5a355912cdd2efa790945c2539ad049c086fd995f3441d (46,080 rows, 27 model columns), native F05 46,080 energy CSV.gz SHA256 024e1d1bbef95d3e254b8c54b3d1134de54eebce7b82d082401c522f813637c5 (40 original columns). No equivalent-shape three-lane output triple-counting.

Microscopic original: Daniel Wolf Savin, **Rate Coefficients for D(1s)+H+ ⇌ D++H(1s) Charge Transfer and Some Astrophysical Implications**, ApJ 566 (2002) 599, DOI [10.1086/324218](https://doi.org/10.1086/324218), arXiv [astro-ph/0109356](https://arxiv.org/abs/astro-ph/0109356).
Exact retrieved original XHTML reprint SHA256 8d22b670d2225de7a1e81ac1440e06188318cb7703b19e3b9ad214d12cb85d29. Extracted exact **47 original calculated paired rate nodes**, not a synthetic dataset, CSV SHA256 ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8. Original Table2 independent 5-parameter fits source JSON SHA256 b178d89b858ae58ed1fe873fe831e02b737532a2f1fc20a82c920e76d2c3b1bc.

## Source-qualified reaction model, conservation, correct dimensions

Take spacetime signature (-,+,+,+). Let H/H+ source fractions be x_HII and 1-x_HII, T in K, proper hydrogen **number density** n_H [cm^-3], D nuclear density n_D=eta_D n_H, eta_D=2.5e-5 *assumed conditional maximum/fiducial scenario*, not a measured posterior. Let y=n_D+/n_D. Savin source rates [cm^3/s] are k_1(T) for endothermic D(1s)+H+→D++H and k_2(T) for reverse. Reproduced **published source Table1 47×2 values**; between printed points adopt explicit log(T)-log(k) interpolation, NOT author unpublished spline/precise quantum raw cross sections. Original Table2 fits only comparative diagnostics; their <6% forward and <4% reverse stated errors dominate the source sub-percent fractionation being sought.

For a **prescribed** original hydrogen donor and CX-only deuterium kinetics,
\[
\left.\frac{d y}{dt}\right|_{\rm CX}
=n_H\left[k_1(T)x_{\rm HII}(1-y)-k_2(T)(1-x_{\rm HII})y\right].
\]
Thus independent of unknown proper n_H, the **per-n_H generator** a=k1*x_HII and b=k2*(1-x_HII) [cm^3/s], stationary fraction y_*=a/(a+b), and stationary relaxation **coefficient** lambda/n_H=a+b [cm^3/s] are well-defined numerical science. Do not use source_H_nuclei_N (which is number of H nuclei per source cell, not cm^-3 density) to manufacture 1/s relaxation or a finite-time solution.

The stationary neutral isotope abundance ratio, in the model where H and D are only neutral/singly-ionized and radiative reactions of D are omitted, is
\[
\mathcal R_{D{\rm I}/H{\rm I}}
=\frac{1-y_*}{1-x_{\rm HII}}
=\frac{k_2}{k_1 x_{\rm HII}+k_2(1-x_{\rm HII})}.
\]
This is a **CX-only stationary donor** result, NOT an independently ionized real IGM abundance measurement.

For finite isotope fraction, external H+ may be allowed to respond to this ONE isolated exchange. Total nuclei H and D are independently conserved, and at every chemical CX event the **total ion/electron count** obeys
\[
x_{\rm HII}+\eta_D y
=x_{{\rm HII},0}+\eta_D y_0,
\]
so exact free-electron creation by CX is ZERO; the x_HII source must be compensated by D+ change. The 46,080 rows include monotone coupled conservation-equilibrium roots separately for the two explicit *basis ICs* y0=0 and y0=1, using no proper time clock, and the corresponding gas heat at net exchange
\[
\Delta \epsilon_{\rm gas}^{\rm CX}
=-\eta_D\Delta E\,(y_*-y_0),\qquad
\Delta E=3.7\,{\rm meV}=0.0037\ {\rm eV}>0.
\]
c and \(\hbar\) are not set to one; 1 eV=1.602176634e-12 erg, so \(\eta_D \Delta E=1.4820133864500002e-19\,{\rm erg/H}\). Forward reaction is endothermic, negative heat if D ionizes. This isolated net reaction energy is not in the original REI 26-event thermal budget and must never be added without owner and reaction-network energy balance.

**Crucial difference from R50**: pure near-resonant H/D charge exchange cannot generate **additional free electrons** in a charge-neutral plasma; it only redistributes which nucleus carries the charge. Thus a hypothetical passive D-electron Thomson upper cap in R50 must not be interpreted as an actual effect from CX alone. Other radiative/recombination reactions would be required.

## Actual full 46,080-node physical source results

All 46,080 original accepted-parent T/xHII centers cross-checked **inside** the original REI #352 tick160 source interval boxes. All tick160 & tick161 preview T are in original Savin fit / printed-table domain (2.7–2e5 K); tick160 median T=11828.327355 K and range 2096.669759–66261.759339 K. Compute original Table1 rates, Table2 fit ratios, actual per-n_H generator, stationary H/D isotope ratios and finite eta_D charge conserving endpoints on each source node. Output is one 46,080-row / 42-column CSV.gz, not a new cosmic IVP.

**Central findings from actual source data:**
- CX-only stationary f_DI/f_HI median **1.0048110147625477**, p95 **1.0192474318749314**, max **1.0204263448161621**; 10,854/46,080 REI nodes have |ratio-1|>1%.
- On all original Table1 interpolated REI sources, k1<=k2. **Independent Table2 fits** instead yield k1>k2 for **30,240/46,080** original nodes. The median fit/table *reaction-rate ratio* discrepancy is +0.01219365547092549; significant for a 0.5% tracer correction. This is **fit representation difference**, not a violation of the underlying original quantum reaction. Single-rate <6% / <4% author fit errors can obscure the fractionation effect, so do not use fits as point-truth for DI/HI.
- Original tick160→tick161 preview *stationary Dneutral/Hneutral* response (not physically evolved D) has observed range approximately [-3.0821e-6, +3.5574e-6], median zero within printed-table interpolation. Small for this single SOURCE preview but no statement about global EoR.
- Full-conversion energy ceiling eta_D ΔE / |original source-native F05 integrated thermal gain|: median **0.05005646034516048** (5.006%), max **0.8062339545011633** (80.623%), >1% on **36,990/46,080** nodes. This **potential budget ceiling** is NOT an actual predicted energy transfer and cannot prove the energy is unimportant nor that it materializes.
- Under the isolated charge-conserving exchange equilibrium with **all initial D neutral**, absolute net exchange energy |Δε|/|Δe_F05| median **0.05003309116049871**. With **all initial D ionized**, median **4.9071302748105795e-6** (0.0004907%). These incompatible conditionals show why initial ionization, true proper density/clock and full radiation reaction network must be source-owned before coupling.
- Finite eta_D CX-only H+ correction max **1.8268850965341699e-7**, not the same object as D+ additional electrons. Source-level H/D ion sum conserved to IEEE binary64 ≲1.11e-16 in independent audit, no original REI owner H/He state overwritten.

## One-pass hostile referee and scientific consequence

1. Do not infer n_H [cm^-3] from the 46,080 source source_H_nuclei_N (cell population counts). No real collisional \(n_H k\,dt\), reaction clock, finite-time D evolution, or equilibrium attainment has been established. Quasistatic stationarity is a mathematical conditional.
2. Published Table1 contains ~3-significant-digit rounded values. Log-log interpolation is declared model choice, not the original authors' Maxwellian integration; Table2 five-parameter fits differ in small ratio SIGN on many actual source temperatures. This is a **quantified scientific accuracy limit**, not a numerical software error.
3. Not all D may be atomic. D+, D, HD, D photoionization/recombination and radiative line opacity need other source owners. \(\eta_D=2.5e-5\) is an illustrative cap. The computed CX-only neutral D/H is not a forecast of real observed D I/H I or anisotropic EoR.
4. Full 26-event REI H/He and global photon/OTS thermal maps were not rerun. tick161 states are PR352 **unapproved physical PREVIEW**, no original accepted history or official tick changed. Comparisons to F05 native thermal gain are source-conditional *capacity ratios*, not 26-event chemistry reaction actual \(\Delta U\).
5. The 3.7 meV net reaction energy and charge conservation relate only to atomic ground-state ion swap; do not double-count it as extra electron Thomson opacity (R50), CMB tau or Bianchi geometry.
6. The independent same-author audit separately reads all 46,080 input/output rows, checks source identities and physically conserved quantities, and checks 39 published-rate interpolation points via 70-digit Decimal: maximum rate relative mismatch **3.671162021024458e-15**, stationary balance residual dimensionless **1.5787788387493385e-16**, H+D charge residual **1.1102230246251565e-16**. Normal Python tests14/14 and -O tests14/14. Wolfram symbolic invariants 3/3 True. No independent different author R6/C9, no rigorous original REI continuum IVP theorem, no strong no-go.
7. **Drift verdict**: This makes one new original-REI real spatial chemistry source-condition model and uncovers a specific physically relevant rate-fit discrepancy, not yet a canonical DAG completion. STOP further source-conditional isotope/table atlases after this unit. Next genuine REI action: owner decision on original F05 PR352 same-parent tick161 acceptance with original H/He/thermal/photons and source time/geometry, then only when named CX consumer exists source actual \(n_H(t)\), D initial/ionization/photo/energy closures.

## DAG status

WU 34/49 (+0), REI central 28/88 (+0), REI working 33/88 (+0), REI Fast 4/7 (+0). Accepted original tick160/131072; tick161 PREVIEW ONLY. HH_R10=OFF, REI_L4=false, PRODUCTION=HOLD, NO_MAIN_MERGE, NO_FORCE_PUSH, NO_AUTO_NEXT_NODE. One R51 scoped scientific unit; R/C stage receipts do not count as 20 scientific admissions.
