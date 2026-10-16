# REI-LRS V8 R5: 원본 Grackle Case-A RR/DR 4채널과 냉각 에너지의 독립 분리

출처: `rei_bianchi` PR #163, HEAD `a6fe0e8b1932ddf60496c5a9dbb68c19d6f0851f`; 실제 원본 native PR150 owner commit `6ea2b1b4b3875c9163cafc45efe720afded43fc4`. 이 연구는 원본 전체 native solver를 수정하지 않는다. 사용한 원본 `rust/rei_microphysics/src/igm_rates.rs` SHA256 `310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf`. Verner donor와 RR donor는 서로 다른 원자 물리 입력이다.

## 실험 도메인

서명 (-,+,+,+); `X = ln(a/a0)`, `a0=1/21`, flat FLRW q_ref=0, `H(a)=H0 sqrt(Om/a^3 + Or/a^4 + Ol)`. Grackle 원본 Case-A H II, He II, He III RR; He II DR (Case-B 재수송 없음), `Tgas`는 이 연구에서 `10000..24000 K` 안에 있을 때만 허용한다. 단위: `alpha` [cm^3 s^-1], `Lambda` [erg cm^3 s^-1], `n_H`, `n_e` [cm^-3], `w` [erg/H], `X` 무차원. 모든 온도·광원·농도는 `PR150 owner`의 실제 total-H nuclei 기준으로 사용한다.

초기 fraction `x = n_HII/n_H`, `y=n_HeII/n_He`, `z=n_HeIII/n_He`, `Y=n_He/n_H`, `e = x+Y(y+2z)`, `n_e=n_H e`. 에너지 density `w = (3/2) k_B T (1+Y+e)`, `k_B=1.380649e-16 erg/K`. 본 연구는 source-free RR/DR, recombination cooling 및 FLRW gas adiabatic work에만 한정한다. 광자 생성/흡수·CI/CE/free-free/CMB 및 active Bianchi shear는 **미포함**이다.

## 각 반응의 독립 사건률

채널 j=0,1,2,3을 순서대로 `[HII RR, HeII RR, HeIII RR, HeII DR]`로 고정한다. 동일 `HeII`를 제거하는 j=1,3은 결합에너지 `chi_HeI`를 공유하지만 원본 `alpha`, `Lambda`, 사건수 ledger는 따로 보관한다.

`(I_j, alpha_j, Lambda_j, chi_j) = (x, rrHII, coolHII, chi_HI), (Y*y, rrHeII, coolHeII, chi_HeI), (Y*z, rrHeIII, coolHeIII, chi_HeII), (Y*y, drHeII, coolDR, chi_HeI)`.

`A'_j = (n_H/H) e I_j alpha_j(T)`, `Q'_j = (n_H/H) e I_j Lambda_j(T)` [erg/H per dX]; electron decrease `e'=-sum_j A'_j`. `x'=-A'_0`, `y'=(-A'_1+A'_2-A'_3)/Y`, `z'=-A'_2/Y`.

Photon-free chemical binding store: `B = chi_H*x + Y*[chi_HeI*(y+z)+chi_HeII*z]`. Therefore `B'=-sum_j chi_j A'_j`. 

Thermal energy `w'=-2w-sum_j Q'_j`; escaped radiative energy, under this **declared, conditional Case-A escape convention**, obeys `E'_esc=sum_j (chi_j A'_j+Q'_j)`. Adiabatic work `W'_gas=2w`, and `d_X(w+B+E_esc+W_gas)=0` exactly. The escape treatment does **not** assert an actual ionizing diffuse photon spectrum; its photon momentum and Bianchi backreaction remain OPEN.

CAS in Wolfram Language: the full four-channel energy identity reduces exactly to 0. Independent single-channel mass-action positive solution `B(t) = b*d exp(-d*k*t)/(d+b*(1-exp(-d*k*t)))`, where `b=min(I,e)` and `d=|I-e|`, satisfies `dB/dt=-k B(B+d)` with exact residual 0, and `d→0` tends to `b/(1+b*k*t)`.

## Time integrator construction to test

1. Exact gas adiabatic half drift `w→w exp(-ΔX)`, store work exactly.
2. At midpoint `X_m`, freeze only geometry `n_H(X_m), H(X_m)`. Use all four **source-locked actual Grackle rates** at one self-consistent temperature `T_m`. Compose exact pair flows symmetrically forward half steps then reverse half steps. Use changing `e` within each pair for mass-action positivity. This preserves `x≥0`, `y,z≥0`, `y+z≤1`, and atomic nuclei within floating-point residuals.
3. For the completed composite chemistry step at trial `T_m`, calculate `Q_j = Σ A_j Lambda_j(T_m)/alpha_j(T_m)`. Solve `T_m=(w_before-ΣQ_j/2)/(1.5 k_B [1+Y+(e_before+e_after)/2])` within `[10000,24000] K` using safeguarded scalar Brent. If there is no positive physical bounded root, **reject the step** instead of clamping or loosening tolerances.
4. Update `w_after=w_before-ΣQ_j`, separate `E_esc,binding` ledgers (never close a residual by defining one column as remainder), and finish second adiabatic half step.
5. Direct continuous comparison: independently integrate RHS in Radau without reusing pair map or midpoint energy bookkeeping. Test thermal, ion fractions, cumulative **four** escaped/cooling channels, event counts, and energy with `ΔX` refinement, including source-owner physical density and declared higher-density multipliers.

This construction is formally second-order for smooth rates and unique midpoint root away from positivity/domain boundaries, but does not prove uniform second order in stiff regimes or full source-on native second order. Photon/source BE terms were unchanged in V7 and their measured ≈first-order global convergence is unaffected by improving this isolated RR/DR subset.

## Related primary research

- Grackle original source: https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c (actual production coefficients bound to pinned native Rust owner and table)
- Mackey (2012), *Accuracy and efficiency of raytracing photoionisation algorithms*, https://arxiv.org/abs/1201.5651 (first/second-order photon-conserving time integration)
- Norman et al., *Self-Consistent Solution of Cosmological Radiation-Hydrodynamics and Chemical Ionization*, https://arxiv.org/abs/0901.1110 (stiff coupled radiation/ionization/thermal implicit treatment)
- Pawlik & Schaye, *Multi-frequency, thermally coupled radiative transfer with TRAPHIC*, https://arxiv.org/abs/1008.1071 (coupled H/He and thermal tests)

## Scientific admission policy

Theory: **DERIVED, symbolic exact ledger PASS**. Python pair-map source-native numerical convergence: **NOT_RUN at R5**. Native Rust PR150 RR-only direct comparison: **NOT_RUN**. Whole source-on second order: **HOLD**. NCP physics history or actual Case-B photon retransport: **HOLD**.
