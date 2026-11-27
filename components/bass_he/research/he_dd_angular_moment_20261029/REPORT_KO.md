# BASS_HE: HE-DD conditional angular second-moment enclosure (2026-10-29)

## Authority
Parent BASS_HE [Draft PR108](https://github.com/cosmosapjw-quantum/BASS_HE/pull/108) immutable HEAD \`e1587adb8fc515384014dd0838b93e5961308bfd\`; original PR105–108 theory/IVP/science suite unchanged. This is an additive source-conditional analysis, not a nuclear production rate. Source transcript derives from IAEA-NDS/exfor_master at commit \`939a14d7bba1ddce51975cb5e8711ce96b3b0871\`, file \`exforall/M04/M0475.x4\`, Git blob \`c49433293921dbb012d7f1b0387745732a598efa\`, previous source SHA256 \`b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f\`. In this run the 330 MeV four rows were source-transcribed from the pinned PR105 evidence; a fresh byte hash of the original EXFOR file was NOT_RUN.

## Source/data assumptions and new theorem
At Eγ=330 MeV, EXFOR M0475002 center-of-mass polar DA [nb/sr] and statistical ERR-S are (46°, 0.14±0.03), (61°, 0.16±0.05), (73°, 0.07±0.05), (87°, 0.19±0.05). The uncertainty boxes are pointwise sensitivities, NOT a simultaneous confidence region.

Assume a nonnegative azimuthally averaged angular density symmetric under d-exchange θ↦180°−θ, with an externally declared global Lipschitz constant L≥L_min=1/700 [nb/(sr degree)]. Define θ∈[0,90°],
f_-(θ)=max(0,max_i[DA_i−ERR_i−L|θ−θ_i|]), and
f_+(θ)=min_i[DA_i+ERR_i+L|θ−θ_i|].
Both are feasible Lipschitz functions and bound any feasible f.

For v(θ)=cos²θ, w(θ)=sinθ, b(f)=N(f)/D(f), D=∫fw, N=∫vfw, define for t∈[0,1]:
ℓ(t)=∫_{v≥t}(v−t)wf_- − ∫_{v<t}(t−v)wf_+,
u(t)=∫_{v≥t}(v−t)wf_+ − ∫_{v<t}(t−v)wf_-.
Then ℓ(t)≤N−tD≤u(t). Consequently the unique zeros of ℓ and u give **valid OUTER bounds** b_low≤b≤b_high. They are **not claimed sharp**, because stitched pointwise choices can violate global Lipschitz regularity. b(f_-), b(f_+) supply distinct feasible **inner witnesses**. A global positive multiplicity factor cancels from b; angle-varying acceptance/unknown polarization does not.

Frozen PR104 rest energies M_alpha c²=3727.3794118 MeV, m_d c²=1875.61294500 MeV. In α-rest frame s=M²+2ME, Δ²=E²(s−4m²)/(4s) and K_±=(M+E−2m)/2±Δ cosθ. Single-D marginal variance: Var(K_D)=Δ² b. At 330MeV Δ²=3798.60144551708985MeV².

| L [nb/(sr degree)] | b outer lower | b outer upper | Var_D [MeV²] outer |
|---|---:|---:|---:|
| 1/700 | 0.279238681235 | 0.386397436244 | 1060.716458–1467.769860 |
| 1/200 | 0.186315404014 | 0.472747698143 | 707.737963–1795.780090 |
| 1/100 | 0.133108297140 | 0.573194162276 | 505.625370–2177.336173 |

All printed transcendental endpoints are numerical approximations, **not certified outward-rounded interval endpoints**. At L=1/200 the old PR105 conditional full-sphere I=[1.0068860482429433,2.4235391725370239]nb is recovered.

## Conditional stopping/deposition theorem
For an eventually supplied medium/time-window-specific per-D deposition channel h(K) measured in MeV with |h''|≤H MeV⁻¹ on [K0−Δ,K0+Δ], the correlated pair satisfies:
|E[h(K+)+h(K−)]−2h(K0)|≤H Δ² b≤H Δ² b_high.
The pair cancels all first-order terms exactly. A manufactured h(K)=K²/K* validates the angular dependence but is not a physical D_fast stopping kernel. No physical thermal power, heat capacity C_V, transport or primary nuclear rate has been computed.

## Actual implementation checks
New \`src/angular_moments.py\`: exact rational source rows, affine cone breakpoints; mpmath trigonometric antiderivatives and sign-split root bisection, explicit physical HOLD; manufactured deposition only.
New \`tests/test_angular_moments.py\`: current Python3.13.5 21/21 targeted PASS, exit 0, 3.6 sec; eight analytic primitive vs independent SciPy quad differences <2e-12. Independent C++20 Simpson 32768 panels (six roots across three L) compared to Python max observed abs difference 8.28e-10. Wolfram 4 symbolic identities exactly zero. The first two local Python errors were Fraction/mpmath type comparisons and were repaired; initial figure mathtext escape/legend overlap also repaired and figure inspected. Original IVPs / prior science suite NOT_RUN, real native distinct-author R6 and C9 NOT_RUN. No numerical outward-rounded certificate.

## Latest related repo intake
BASS #246/#247: only source/time certification methodology, no nuclear rate; bass_cr #122: atomic-He event flow, not γ+⁴He→dd; rei_bianchi #264: UVB/charge complement, not MeV photon phase space; rec_bianchi #156: HD line energy ledger, distinct radiation channel; WU088_HH #160: 105K ionic HD Q remains HOLD, not D_fast stopping; vigilode #109: numerical error controls only. Current repo/PR heads and selected reports verified; no claim of full private local-repo absence.

## Claim gate and DAG
Central 28/88; HE 14/18; PR105 2/2; PR106 1/2; reciprocity 1/2; birth ledger 1/2; **new conditional angular moment 1/2**, physical delta=0; theory 9/10, coding 9/10 with nonauthor R6/C9 NOT_RUN.
\`kappa=null\`, \`R_event=null\`, \`heat_rate=null\`, \`physical_activation=false\`, \`L4=false\`, \`production=HOLD\`.

## Next precise science action
Obtain original Arends1976 and Silverman1984 full angular acceptance/efficiency, spin-polarization and event-vs-particle normalization; actual same-s inverse DA and event-total σ; source-qualified 330MeV photon phase-space and target rest distribution; named D_fast stopping/deposition operator and a source-qualified |h''| envelope. If using numerical bounds as rigorous certificates, obtain **outward-rounded interval trig integration/root isolation** separately. Existing completed IVPs, full suites and old checkpoints must not be replayed.
