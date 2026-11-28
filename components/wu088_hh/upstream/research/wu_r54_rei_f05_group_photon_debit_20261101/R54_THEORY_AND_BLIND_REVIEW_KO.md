# WU R54 | 원래 REI F05 4군 광자와 D 흡수의 보존적 교란

2026-11-01. Role: WU088_HH contributes source-native photon chemistry to original rei_bianchi IGM. Status: derived / numerically checked / implementation-verified, ONLY a source-conditional perturbation. Original F05 26-event Einstein–Boltzmann/OTS/thermal joint photon-owner re-execution and official tick161 acceptance are NOT RUN.

## Frozen authoritative sources

Immutable WU parent Draft PR #193 HEAD 6f2f532b46ea153795d6aebeed7b73765b6482ac; original REI F05 owner PR #352 HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c, accepted history tick160/131072 and 161 NONAUTHORITATIVE preview. Original accepted state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; original source tar SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b.

Original 46,080-cell material NPZ SHA256 7855f8b5c072da7860e5b0404a5548114ef46a8713840d99e4efa1b009905d2d; original 85-row native photon forcing SHA256 9b33a16956d30d96576e7e189ab11ad67321fd6d2872b8ad68058f7aac3b5268; original R53 46,080-row non-equilibrium D photo/RR/CX/EII source result SHA256 17a6806ace5da5352e16f7a49c98ae0c3dbde3e142e06383db78a7a6dc1c080c. Source b2b photon Verner/grouping code SHA256 05f1b83a301ac0b883159e5232aa0db9c1e8ffea7e21ff12c419e40464ccc86d; source gamma formula code SHA256 4f5505e424d00cd4d7b96ff13ac0c3698d94286ae529040074ade6475762cb62. Published Savin (2002), DOI https://doi.org/10.1086/324218, states HI/DI PI approximate equality, not exact isotope photoionization cross sections. Original source 47 paired D-H CX rate table SHA256 ba98ec463903f3589c6c68cd7d9e3b3bc637188bb5d25616addb2fb71ab689e8.

Source original first 17 F05 time nodes all z_mid=5.95; original [160,161] tick has proper Δt=4,871,848,749.16828 seconds. Native source photon groups G1 [13.60,24.59] eV, G2a [24.59,39.50], G2b [39.50,54.42], G3 [54.42,100]. Native G3 source N and original absorption are EXACTLY ZERO in this interval. Native source photon number N_g^0 is photons/cMpc³ and native absorption A_g^0 photons/(s cMpc³). Native original HI Verner spectrum averaged with source E^-2.5 group shape, converted using proper units c=2.99792458e10 cm/s, 1Mpc=3.085677581491367e24 cm, reconstructs original source Γ_HI at all 17 native nodes with max relative error 2.1692270336845777e-16. Between nodes separate PCHIP fields differ relatively by at most 5.180429479652933e-9 within this original tick, so the actual saved Γ_HI is preserved as scalar authority and its exact group weights are inferred from sigma_g*N_g.

## Constructive photon/chemical conservation derivation

Use metric (-,+,+,+), proper t in seconds. Source-conditional DI photo group fractions:
w_g(t)=sigma_g*N_g^0(t)/sum_h sigma_h*N_h^0(t), with sum_g w_g=1, w_G3=0.
At preserved source Γ_HI(t), define Γ_DI,g(t)=Γ_HI^source(t)*w_g(t)*(1-D_g(t)/N_g^0(t)), N_g=N_g^0-D_g. The PI equality is Savin-supported approximation. No DI-specific ab-initio photo cross section is claimed. A translated 1.7-meV threshold HI→DI model is a separate spectral sensitivity (physical DI threshold 13.6017eV, native Verner H model edge 13.60eV), not used in primary kinetics.

Let y_j=N_D+,j/N_D,j, η_D=2.5e-5 assumed, N_D,j=η_D*N_H,j original 46,080-source cell nuclei. Photon rate per D nucleus:
 dP_g,j/dt= Γ_DI,g*(1-y_j).
At fixed original HI/He photon reference and its group absorption opacity λ_g^0=A_g^0/N_g^0, positive D photon deficit D_g and native absorption displacement B_g satisfy:
 dD_g/dt=η_D sum_j N_H,j dP_g,j/dt - λ_g^0 D_g,
 dB_g/dt= λ_g^0 D_g.
All P_g,j, D_g, B_g start at 0. Integrating yields EXACT:
 η_D sum_j N_H,j P_g,j(t) = D_g(t)+B_g(t) for each group.
This is true photon-number conservation of the limited perturbation system, NOT conservation certification of unmodified original 26-event Einstein–Boltzmann/OTS owner. Native external emission/front/current and H/He chemical owner are held fixed, with their direct absorption response λ_g^0*D_g included. Native G3 remains zero.

DI chemical 5-state source uses y,C (net H/D charge-exchange events), P_g (group photoionizations), R (recombinations), I (electron impact ionizations):
 dy/dt = dC/dt+sum_g dP_g/dt+dI/dt-dR/dt.
Charge correction H+_eff = H+_source -η_D C, electron density n_e,eff=n_e,HHe,source+η_D n_H(y-C). Thus CX transfers charge and creates ZERO total electrons, while photon+EII new electrons per H=η_D(sum_g P_g+I-R). Source H/He/T/electron donor between accepted tick160 and UNAPPROVED tick161 is declared endpoint interpolation (HII/ne linear, T log-linear). Case B RR and native H EII cloned to DI under Savin Eq12-13. No photons, H/He, Einstein metric or original REI worker are mutated.

## Actual original-source physical numerical results

46,080 cells, two initial D ion scenarios y0=0 and y0=1, true original nH proper and first-tick clock. Initial neutral D:
- G1 gross DI photon events 1.4496669535433337e59.
- G2a gross DI events 1.0755515685974254e58.
- G2b gross DI events 1.1533246907418878e57.
- G3 exactly zero.
- Total 1.568755357310495e59.
- Total native absorption DISPLACED by photon deficit B_g 8.637708285717152e53; almost all new DI photons appear as a small deficit in the giant native group photon reservoir during the first tick.
- Max native group photon reservoir relative depletion 8.022398936974899e-7.
- Native R53 frozen-photon D+ final versus R54 group-coupled D+ final: max abs change 4.327691041899201e-10, median change -4.3143736369946617e-10; R54 initial-neutral final D+ median 0.004227477539417964.
- Mean original HI-Verner-weighted photo photon energy available to DI source under the cloned cross section: 17.59447931594912 eV, above conditional DI ionization energy 13.6017eV.
- GROSS DI photoelectron excess energy is median 1.8304389535914564e-19 erg per H nucleus. This corresponds to median 0.06185770097038562 or 6.18577% of the absolute original native F05 discrete gas-thermal increment. It exceeds 1% in 37,470/46,080 cells. The largest such gross conditional ratio is 0.997177157246157. IMPORTANT: This is NOT NET heating or accepted extra thermal source. It has NOT subtracted the source-native H/He electron/photoheat and latent/OTS redistribution displaced or affected by DI photons. Source owner must reconcile the joint thermal and photon-energy budget before using it for physics claims.

## Verification and blind referee (same-author)

- 16/16 original-source physical/unit tests in ordinary Python, 16/16 optimized -O. Original input SHA and all 17 native source HI gamma via independent Verner calculation PASS.
- Independently audited all 46,080 H/He source real cells and DI grouped photon events, nuclear counts, H/D charge ledger, and DI chemical latent plus gross photoelectron energy. Group number ledger |P-D-B|/P max 1.6113850401496607e-16. Source photon energy ledger residual max 1.6851887013388314e-34 erg/H. Five reaction D population ledger max abs 7.068149014075866e-16.
- Alternate SciPy DOP853 integrated the original 3 nonzero group DI photon deficit equations with archived 64-stage neutral-D source trajectory; max relative final deficit difference from original production RK4 2.8863959897770824e-12. This is a different numerical formulation but SAME author; not independent researcher, not native REI full photon RT validation.
- Remove source photon feedback exactly and recover all 46,080 original R53 non-equilibrium D+ states to max abs 2.220446049250313e-16. RK32 versus RK64 original source state max D+ difference 1.0859382282291108e-8. No spectral source-support reweighting beyond native E^-2.5 and Verner MFP model.
- Blind hostile finding: A 4.95%-of-emission DI photon demand need NOT produce a similarly large fractional photon field response because the original source has an enormous photon reservoir. This model finds max depleted reservoir fraction 8e-7. It does not imply DI photoelectron heat is negligible, because gross event energy may compare strongly with the small first-tick gas thermal increment. Conversely gross DI heating cannot be added to original HI/He heat without full photon and potential-energy double-count protection.
- Original photon G1 spectral support, allocation and ionizations still frozen in native owner. No DI frequency-dependent ab-initio photo cross section, full H/He trajectory, original Bianchi observer null geodesic, real observational CMB, production solver admission or general strong no-go proven. The source perturbation is a separate experiment only.

## Stop and original-owner next physics

One WU-owned original-source group-photon perturbation data unit. Stop extra isotope microphysical coefficient atlases or formal governance loops. For actual original REI IGM DAG promotion, REI original photon owner must take native source group N_g, HI/He/G1 opacity/current and DI real group events, rerun full 26-event H/He+DI photon/OTS/thermal with original source continuum, reconcile photon/binding/thermal energy, then adjudicate F05 first [160,161] official acceptance.

WU canonical 34/49, REI central 28/88, working 33/88, Physical Fast 4/7, all Δ0. Original accepted tick160/131072, proposed tick161 HOLD. HH_R10=OFF, REI_L4=false, PRODUCTION=HOLD, NO_MAIN_MERGE, NO_FORCE_PUSH, AUTO_NEXT_NODE=false. R1–R10+C1–C10 are evidence stage receipts for one real scientific unit, not 20 new DAG nodes.
