# WU R55 | Original REI F05: source-conditional D I initial-chemistry sensitivity

Date: 2026-11-02. Project: cosmosapjw-quantum/WU088_HH. Single science unit: original REI F05 46,080-cell source-native D I photon and chemical response, not an accepted original REI state or new primordial HD coefficient atlas.

## Science contract and source identity

- WU immutable parent PR #194 HEAD \`5933f3fb4432bee7f2268c62873132a0d741f054\`; its R54 code original SHA256 \`ded9c2542d05d4734370d10819d544986c89c06ef57064ea7e376f3580770885\`.
- Original REI 26-event F05 owner PR #352 HEAD \`ea8d6bf94197392c69f939f03c1673ed3afe349c\`, original accepted tick160/131072; tick161 is an *unaccepted preview*. REI central PR #363 uses original 46k cells for first64 H/He energetics, NOT newly certified original tick161. BASS_HE PR #150 introduces OTS photon-energy accounting but does not make a DI-coupled H/He/RT owner solve.
- R54's 12 original-source input files pass its immutable SHA guard; original first F05 proper interval dt = 4,871,848,749.16828 s, source z=5.95, source 17 radiation knots, all four exact native photon groups, native G3 has N=absorption=0. Source HI Verner group opacity and native photon \(\Gamma_{\rm HI}\) reused. Source original H+ and electron donor/temperature are conditional interpolation from accepted tick160 to tick161 PREVIEW. Hypothetical \(\eta_D=2.5\times10^{-5}\) is not an observed or measured D/H.
- Original Savin (2002), ApJ 566, 599–603, DOI https://doi.org/10.1086/324218, original 47 temperature pairs for D(1s)+H+ <-> D+ + H(1s); approximate HI->DI photo, recombination, EII cloning is a model hypothesis, NOT a DI ab-initio photo cross section.

## Derived analytic initial-chemistry construction

Let \(x=n_{\rm H^+}/n_{\rm H}\), \(y=n_{\rm D^+}/n_{\rm D}\), \(n_{\rm D}=\eta_D n_{\rm H}\), proper time \(t\) (s), native source \(T(t)\), \(n_e^0(t)\) (cm^-3), \(n_{\rm H}(t)\) (cm^-3), original HI group photo rates \(\Gamma_g(t)\) (s^-1). Savin forward/reverse CX rates \(k_f,k_r\) (cm^3 s^-1) and original H Case-B recombination \(\alpha_B(T)\), electron-impact ionization \(\beta_{\rm HI}(T)\) (cm^3 s^-1).

For initial CX-only stationary:
\[
y_{\mathrm{CX},0}=\frac{k_f n_{\rm H}x}{k_f n_{\rm H}x+k_r n_{\rm H}(1-x)}.
\]
For instantaneous full-chemistry stationary with initial zero accumulated CX (\(C_0=0\)), \(n_e^{\rm eff}=n_e^0+\eta_Dn_{\rm H}y\), solve
\[
0=(k_f n_{\rm H}x+\Gamma+\beta_{\rm HI} n_e^{\rm eff})(1-y)-
(k_r n_{\rm H}(1-x)+\alpha_B n_e^{\rm eff})y.
\]
Define \(p=k_f n_{\rm H}x+\Gamma+\beta_{\rm HI}n_e^0\), \(b=k_fn_{\rm H}x+k_rn_{\rm H}(1-x)+\Gamma+(\beta_{\rm HI}+\alpha_B)n_e^0-\beta_{\rm HI}\eta_Dn_{\rm H}\), \(q=(\beta_{\rm HI}+\alpha_B)\eta_Dn_{\rm H}\); stationary equation \(q y^2+b y-p=0\), numerically stable positive root \(y_{\rm FULL,0}=2p/[b+\sqrt{b^2+4qp}]\). Direct CAS equality and residual checks PASS. These are **conditional initial states**, not reconstructed past-D evolution or evidence that the original tick160 cosmology was in isotope steady state.

For either y0, reuse R54 photon-conserving grouped perturbation with source native H/He optical opacity fixed. Let \(D_g\) be additional DI photon-group deficit, \(B_g\) displaced H/He source absorption, \(P_{g,j}\) DI photo events per D nucleus per original cell j, \(\lambda_g=A_g^0/N_g^0\) for N_g^0>0. Evolve
\[
\dot D_g=\eta_D\sum_jN_{{\rm H},j}\dot P_{g,j}-\lambda_gD_g,\quad
\dot B_g=\lambda_gD_g,\quad
\eta_D\sum_jN_{{\rm H},j}P_{g,j}=D_g+B_g.
\]
R54 source \(\dot P_{g,j}=\Gamma_{g,\mathrm{HI}}^0(1-D_g/N_g^0)(1-y_j)\). Full cell kinetic species rates use Savin charge exchange, H Case B RR, H-cloned EII and original source donors. Accounting exact \(y-y_0=C+\sum_g P_g+I-R\); independently created electrons per H nucleus after initial state \(\eta_D(\sum_g P_g+I-R)=\eta_D(y-y_0-C)\). \(G3\) is strictly zero.

Gross candidate DI photon energy is split using existing R54 native HI-group cross-section-weighted mean absorbed energies \(\bar E_g\): \(Q_{\rm photon}^{\rm gross}=\eta_D\sum_g P_g\bar E_g\), \(Q_{\rm latent}^{\rm gross}=\eta_D\chi_D\sum_gP_g\), \(Q_{\rm electron}^{\rm gross}=Q_{\rm photon}^{\rm gross}-Q_{\rm latent}^{\rm gross}\) in eV per H converted with 1 eV = 1.602176634e-12 erg. This is *gross*, not corrected net heating. It is explicitly NOT added to original source H/He energy.

## Real original-source 46,080-cell numerical data

- Original native tick160: \(T\) 2,096.67–66,261.76 K, median 11,828.33 K; \(x_{\rm HII}\) min 0.992756, median 0.999943724. Conditional \(y_{\rm CX,0}\) median 0.999943151712; \(y_{\rm FULL,0}\) median 0.999956488988. Full first-tick final \(y_{\rm D^+}\) median 0.999956488977.
- R55 FULL gross DI photoevents = **1.9698241102614884e55 photons/cMpc3**, 0.000621647616% of native original first-interval emitted photons (3.168714973104279e60). This is only 0.000125566048338 of R54 original all-neutral-D photoevents 1.568755357310495e59, which were 4.950761967% of emissions.
- R55 CX-only initial condition gross DI photoevents = **1.9554744937570015e55 photons/cMpc3**. The reasonable-looking equilibria differ but neither is proven actual history.
- R55 FULL additional native H/He absorption displaced = **1.081218615402179e50 photons/cMpc3**; max relative native photon-group deficit **1.007340974509698e-10**. Group G3 exactly zero.
- Gross candidate photoelectron heat per original H nucleus divided by \(|\Delta U_{\rm F05}|\) median **2.4842492197468618e-6** and max 3.479677463409087e-4; **0/46,080** cells exceed 1%. R54 all-neutral median 0.06185770097 and >1% in 37,470 cells. Neither gross scenario measures net source-corrected heat.
- Source FULL immediate relaxation exposure \((b+2qy_0)\Delta t\) median **0.0042370202574607465**, so an instantaneous steady initial condition is not justified by relaxation within this single original tick. Real cosmological D history since prior accepted ticks is required for an official prediction.
- FULL positive 46k cells, grouped photon number residual max relative 7.233829820967932e-17, FULL five-flux y ledger 3.137321650727116e-15, gross energy split max residual 1.128474576789396e-36 erg/H. Independent separate-stdlib CSV check over all 46k data gave 1.4955087417885e-16 maximum group relative residual, electron ledger 8.13e-20, energy ledger 1.88e-36 erg/H, 0 R54 extreme bracket violations. RK32 vs RK64 D+ max abs = 1.587618925213974e-14.
- Normal 8/8 and -O 8/8 Python unittest PASS. A separate same-author adversarial audit detected and repaired a **reviewer-only error**: double subtraction of CX when comparing the already compensated total-electron output. The original physics model and numerical arrays were not altered by this repair.
- Native distinct subagent: NOT_RUN (not available); independent author: NOT_RUN. Original 26-event HHeDI/RT/thermal worker: NOT_RUN; original 161 production acceptance: HOLD.

## Drift watchdog and blind referee

1. Physical question answered: \`IS_R54_ALL_NEUTRAL_DI_4p95pct_PHOTON_STRESS_IC_ROBUST?\` => **NO, not robust to source-consistent conditional D ionization initial states**, as a source-conditional numerical finding, NOT a quantified historical-D scenario or strong no-go.
2. The source shows >99% H ionization and conditional D near fully ionized, but the correct physical D initial state needs integrated prior D history. Median within-tick chemical relaxation exposure 0.00424 makes pretending local equilibrium is historically certain unjustified.
3. Photon deficit \(D_g/N_g^0\sim10^{-10}\) does not by itself bound net gas thermal feedback; net heating still requires original H/He photo/OTS/chemical/thermal repartition. Source group means clone HI; no DI ab-initio cross section.
4. No extra microscope coefficient atlas, rate-fit tuning, tolerance widening, additional governance loops or fake canonical DAG node completion. One physical sensitivity with actual original 46k source rows and publication.
5. WU **34/49 (+0)**; REI central **28/88 (+0)**; REI working **33/88 (+0)**; Physical Fast **4/7 (+0)**; original accepted history tick160/131072; tick161 HOLD. WU R55 standalone scientific contribution COMPLETE-SCOPED; canonical source-owner admission remains HOLD.
6. Minimal next science: original owner must evolve D from historical accepted trajectory and genuinely co-evolve H/He/DI four-group photons, OTS recombination and thermal reservoir with original proper continuum V2 source; then compare 160→161 source-defined solver acceptance. Repeated standalone frozen-original-opacity D projections are not the next critical path.

## Reproducibility

Original R54 source directory: \`/home/cosmosapjw/research_backups/WU088_HH/R54_REI_F05_DI_GROUP_PHOTON_DEBIT_20261101\`.
R55 directory: \`/home/cosmosapjw/research_backups/WU088_HH/R55_REI_F05_D_CX_PLAUSIBLE_IC_20261102\`.
Run \`python3 r55_source_conditioned_initialization.py --r54-root <R54_ABSOLUTE_PATH> --out results\`; then \`python3 audit_r55.py --out results --r54-root <R54_ABSOLUTE_PATH>\`; \`python3 -m unittest -v test_r55\`; \`python3 -O -m unittest -v test_r55\`.
Real full 46k-source-conditioned output \`results/R55_REI_F05_INITIAL_DI_PHYSICS_46080.csv.gz\` SHA256 \`e670a9ac41e68596d9007ab33d1ba49404c1fdcd75ed0d668fc545d6af280022\`; source-free GitHub publishes subset incl 24 original-cell witnesses and 4 original group records. R54 immutable original-source complete ZIP SHA256 \`23cbf0b3e91f7e17fc915c06c025a9e55c6aac8b0ebeca6df7039bfe5fbb32ab\`.

**Admission:** R55 source-conditional physics \`DERIVED + NUMERICALLY_CHECKED + IMPLEMENTATION_VERIFIED_SCOPED\`; source-owner production \`HOLD\`; \`NO_MAIN_MERGE\`, \`NO_FORCE_PUSH\`, \`AUTO_NEXT_NODE=false\`, \`REI_L4=false\`, \`HH_R10=OFF\`.
