# BASS_HE → REI Bianchi IGM: 실제 원본 He II Lyα 광자의 causal-window 흡수 가능량
2026-11-02 KST | science-first physical calculation | DRAFT/HOLD | no false causal transfer admission

## 1. 원본과 새 질문
Immutable BASS_HE parent PR151 exact HEAD eed3b50d2985ec4fb562032f9473cf31495d945d; REI F05 source PR355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00; native source archive SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644. Immutable REC195 accepted-state archive SHA256 ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657 contains original genuine accepted REI F05 states at 0,64,128,160. PR151 actual source-accepted 138,240 HeII Lyα emission-time-integrated local escape events source CSV SHA256 13e05ff26adfb8eec5c2e0d0d028a1106f190771c642c2bb4306db79d9a80daf and JSON SHA256 545f363740a8533f643d1f26b9dd6fd0c30d42078800fc6dce0d3c604156a993.

New science target is NOT another static opacity atlas. Determine, from original **actual emitted line source bound and accepted H/He matter state**, whether a photon could have a first collision within the remaining source-clock interval in the explicitly prescribed *homogeneous, right-endpoint frozen absorbing-gas* conditional reference. No real null ray, source geometry, spatial transfer or observed sky is claimed. The 46,080 original F05 material nodes carry numerical integration weights and macro/micro indices but not certified physical coordinates, adjacency, individual photon source positions or transport distances; inferring ray path from W_node (source proper volume) is not supported.

## 2. Theory, conventions and conditional source/receiver split
Metric (-,+,+,+), proper source tetrad, c=2.99792458e10 cm s^-1 and εeV=1.602176634e-12 erg/eV. Original line Eα=40.81332 eV, H I χ=13.598434599702 eV, He I χ=24.587389011 eV, He II χ=54.417760 eV. Thus only H I and He I are potential recipients of THIS line's photoionization (not direct He II).

Read exact original 26-event reduced RHS \`SIGMA_OTS_H41=2.884642817876362e-19 cm2\`, \`SIGMA_OTS_HEI41=3.0402144676144673e-18 cm2\`. At one accepted endpoint t_b use the nucleus-conserving original component-box interior representative state, not an alleged certified correlated realization:
κ_H=n_HI(t_b)σ_H, κ_He=n_HeI(t_b)σ_He, κ=κ_H+κ_He [cm^-1].
Original proper material volume V=W_node Mpc_cm³/(1+z)^3 is only used for number density, never to infer path geometry. Local mean free path λ=1/κ [cm] and absorption time λ/c [s] are valid microphysical scales.

If a photon escaped original OTS local approximation in [t_a,t_b], it can travel no more than c(t_b-t_a) in that time under a local proper-clock straight-flight reference. For the **separately postulated homogeneous fixed endpoint density along the ray**, p_abs(t)=1-exp[-c κ(t_b-t)]. For any nonnegative unknown photon birth-rate history within the interval and original source upper escaped count Nesc^+, conditionally:
0≤Nabs_frozen≤Nesc^+*(1-exp[-c κ Δt]).
Native f∈[0.1,1] makes the zero source escape lower bound genuine. This is NOT an unconditional upper on actual IGM absorption, which depends on unknown ray geometry/density and source emission-time distribution. A second source-endpoint BOX-κ upper is computed from accepted HI/HeI population interval upper endpoints to distinguish gas point selection from the source's allowed interval. The exact source emitter can be correlated with absorber, so multiplying independent upper bounds gives a conservative rectangular conditional reference, not an actual state realization.

At the same right-endpoint frozen point, hypothetical competition:
N_H,abs = Nabs κ_H/κ; N_He,abs=Nabs κ_He/κ. These are allocation to an unspecified hypothetical *receiver*, NOT modifications of emitting nodes. The extra photo-ionization energy reservoir potential E_bind=ε(χ_H N_H,abs+χ_HeI N_He,abs), primary electron heat potential E_heat=ε[(Eα−χ_H)N_H,abs+(Eα−χ_HeI)N_He,abs]. Identity E_bind+E_heat=ε Eα(N_H,abs+N_He,abs). No double count: the original OTS f-local absorption was ALREADY included in original F05 26-event chemistry; only original locally escaped line photons enter this conditional downstream reference.

**Separate, not original-source-owned sensitivity example:** for uniform photon emission in source proper interval with time-constant local κ, p_uniform=1−(1−e^{-τ})/τ, τ=cκΔt. Small τ series τ/2−τ²/6+τ³/24+O(τ^4). Wolfram symbolic τ→0 and species/energy identities produce zero residues. This is a comparison model only, not a recovered original time-resolved photon birth distribution.

## 3. Actually executed source-native physical data (138,240 conditional node×time rows)

Original z=5.95, source proper clock, real accepted original H/He material state for ticks 0,64,128,160, source native OTS cross-sections and PR151 line-escape source:

| Accepted source interval | source-upper Lyα photons | causal max proper distance | emission-weighted p_abs right-frozen | emission-weighted p_abs left-frozen | uniform-birth reference p_abs |
|---|---:|---:|---:|---:|---:|
| 0→64 | 1.1995953266017161e59 | 3.0293114646130475 kpc | 0.008425095300467466 | 0.0028006188330414843 | 0.0042375241444242845 |
| 64→128 | 1.1986574388975963e59 | 3.0293114646130475 kpc | 0.01342454868004163 | 0.008415497590874203 | 0.006779479710214905 |
| 128→160 | 5.991187781616674e58 | 1.5146557323065237 kpc | 0.008032352786047933 | 0.006812204319391035 | 0.004040421856275161 |

Source original total escaped photon envelope: [0,2.99737154366098e59]. *Conditional right-endpoint homogeneous reference*:
- at most 3.1010473474730165e57 first absorptions (source-weighted 0.010345889064141202);
- 1.5006201551465352e57 H I and 1.6004271923264813e57 He I potential photoionizations;
- corresponding positive H/He ionization binding gain 9.57403254363308e46 erg, primary photoelectron heat 1.0703761851547212e47 erg, sum absorbed original line energy 2.0277794395180296e47 erg, all a non-authoritative *reference*;
- accepted endpoint upper population box enhances source frozen-ray reference capacity slightly to 3.1068940056938305e57 (source-envelope fraction 0.01036539501505736);
- explicitly hypothetical uniform-in-time source photon births yield 1.5630280552306995e57 conditional absorptions (fraction 0.005214662354876507).

HeII Lyα emission-weighted *median local mean free path* at accepted t64 is 4.0523642992365976e24 cm, t128 2.7673712399867416e24 cm, t160 2.396636792798292e24 cm. These are proper absorption scales at real source gas densities, **NOT** ray lengths between original material nodes. Comparison with cΔt of 1.5–3.0 proper kpc motivates transfer on longer scales than the source microinterval under this conditional homogeneous model, but does not certify the *actual* photon survival probability.

The 0→64 start-frozen vs end-frozen absorption reference changes by a factor ~3 (0.00280→0.00843), demonstrating that using an unspecified time-dependent opacity as a fixed one is scientifically nontrivial. This is why the source's evolving geometry/density and emission-time distribution remain a real central IGM modeling obligation.

## 4. Original source and independent verification
Original accepted-state SHA: t64 aae4607ec1f0eff6669f1c1cb716ec6d6a4af8b789bba14abcd17f1733f83425, t128 bbb349102194c86fb39a720a6695d9cb5845782b154da3448a433959fcc7f6a6, t160 74c7cbb784c3a6fe25e53307f678ef23ab87263f56b314fbaa3ef696433d05f6. Original nucleus-conserving internal material point uses the existing \`edge.element_conserving_parent_candidate\` and stage/source H/He nucleus totals. Original source W_node and z are used ONLY for volume/density, not a fabricated spatial mesh.

Main original-source executable \`original_lya_causal_capacity.py\` ran against these unchanged original inputs and produced 138,240 physical conditional records. Original full numerical source optimized pinned NumPy2.3.5 cold replay CSV.gz and JSON were byte-identical. The original 26-event *time evolution itself* was not reexecuted in this bounded unit: accepted states are REI/REC source-locked and PR151 original HeII escape time integration is consumed unchanged. Do NOT claim a fresh full 14-ledger IVP admission. External libraries' optional NumPy1 C-extension ABI stderr warning was preserved as environment evidence; run exited 0.

Independent standard-library implementation \`audit_conditional_sourcefree.py\` read all 138,240 derived node/interval rows and independently recomputed κ·cΔt, expm1 survival, H/He allocation, binding/heat, and source interval totals. All PASS with max scaled row reconstruction 6.109874804411117e-16 and energy split 4.414492214242737e-16. Source-free unit tests normal 3/3 and -O 3/3 PASS; corrupted JSON negative test failed closed; compiled with py_compile; published source-free receipt verified normal and -O. Full pinned source producer -O replay CSV, JSON BYTE_IDENTICAL and second audit receipt BYTE_IDENTICAL. These are same-author independent algorithms. Different-author blind referee and native subagents NOT_RUN.

Output:
- \`results/REI_F05_LYA_FROZEN_CAUSAL_WINDOW_CAPACITY_138240.csv.gz\`, SHA256 7eca7c5f3e8188177496033cd3443b26eee12e0b87c04f53bb13f6c3294510f6.
- \`results/SCIENCE_RESULT.json\`, SHA256 9ee4a8039c937394ef89e2d2d0ac04f12baa80c35a941fc03c8037dfd9f62dbd.
- \`results/INDEPENDENT_AUDIT.json\`, SHA256 692c36366e5db0ed141643973b3a2d710229746a091dad22a4b0b72c36bbc5d2.

## 5. Science claim gate and next owner action
Key obstacle remains **spacetime geometry**: no source-owned x_i, adjacency, boundary/frequency directional rays, source-to-absorber photon arrival time or null Liouville evolution. Even with exactly the same original source Nesc and local κ at an emission node, two photon trajectories through different external density profiles have different ∫ray κ dl. Therefore the present local reference cannot uniquely determine actual REI photon transport or line-of-sight observer quantities. This constructive ambiguity is NOT a literature-novel strong no-go.

A source-causal radiation step next requires original REI RUX03/RUX04 to supply spatially assigned source emitters, direction, metric, proper path length, along-path H I/He I optical depth, time-dependent ionization and born photon energy/redshift while preserving the original source OTS f. Otherwise the mathematically correct result is only conditional capacity reference. STOP additional adjacent BASS_HE local-opacity tables.

Final frozen report progress: Central REI canonical 28/88_REPORTED; working 33/88_REPORTED; Physical Fast 4/7_REPORTED; BASS_HE physical 14/18_REPORTED, canonical delta0. Production HOLD, original tick161 NOT_ACCEPTED, no original source/worker change, no merge, no force push or tolerance change, no invented observed CMB.

Literature methodology: Mellema et al. (2006) C2-Ray, DOI 10.1016/j.newast.2005.09.004; Friedrich et al. (2012) H/He OTS transport, DOI 10.1111/j.1365-2966.2012.20449.x; Pawlik & Schaye (2011) TRAPHIC, DOI 10.1111/j.1365-2966.2010.18032.x. Original REI source determines the numerical model.
