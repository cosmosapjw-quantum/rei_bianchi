# REI: EOS–Jeans 보정 상자에 대한 2차원 UVB GLS support (2026-10-29)

## 실제 source와 변경하지 않는 전제

1. [Becker & Bolton (2013), Table 1/2](https://doi.org/10.1093/mnras/stt1610): z=(2.4,2.8,3.2,3.6,4.0,4.4,4.75), nominal log10(Γ_HI/10^-12 s^-1) 7개, 상관 통계 공분산 C (dex², Table2 original 100×C /100), γ_TDR=1.4 기준. γ=1.6의 인쇄 보정 v=[0.084, 0.086, 0.083, 0.077, 0.071, 0.066, 0.064] dex; Jeans smoothing asymmetric source shifts lower=[-0.016, -0.008, -0.003, -0.003, -0.004, -0.005, -0.014] and upper=[0.001, 0.006, 0.012, 0.016, 0.021, 0.023, 0.023] dex. Full original source Git blob 61c1ecdcb1be05d47bb59165fb4cac8bb14deb52.
2. Puchwein2019 저장 template 7개와 PR251 calibration blob abd45812fb38691bcc76b5bddd33c55e2e5e4be3는 기존 그대로. 이전 PR252 단일 redshift slope, PR253 단일 EOS response는 모두 **재사용**. 새 코어는 그 어느 저장소 source나 solver를 변경하지 않는다.
3. EOS의 θ=(γ_TDR−1.4)/0.2 ∈[-1,1], 고정 응답 벡터 v; Jeans 보정 j_i∈[l_i,u_i]를 7개의 **독립적인 결정론적 범위 좌표**로 허용한다. 이는 실재 물리의 독립 확률변수나 68% credible interval을 주장하지 않으며 실제 가능한 공동집합은 더 작을 수 있다. γ와 Jeans가 실제 공동물리에서 연관된 경우에도 이 직사각형을 **상위 집합**으로 사용하는 조건부 해석만 가능하다.
4. 모든 C/자료 값은 정확한 binary64 실수상(Fraction.from_float). Source projection file SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`. 원래 논문 PDF raw byte를 받았다고 주장하지 않는다. 고정 Puchwein template, EOS response의 선형 보간, C의 nuisance 비의존성을 유지한다.

## R4–R5: 핵심 정리와 증명

X=[1,z−3.6], W=C⁻¹, M=XᵀWX. 입력된 C는 정확 LDLᵀ에서 7개의 양의 pivot을 가지며 M은 rank2이고 det(M)>0이다. r=d−m으로 두면

**a(θ,j)= (β,κ)ᵀ = a₀ + A(θv+j), A=M⁻¹XᵀW, a₀=A r.**

c_i=(l_i+u_i)/2, h_i=(u_i−l_i)/2. ∣θ∣≤1, ∣q_i∣≤1인 독립 상자에서

a = a₀ + A c + (A v) θ + Σ_i (A_:i h_i) q_i.

즉 8개 생성자를 가진 2차원 **zonotope**의 정확한 선형상이다. 임의 쌍대방향 s∈R²의 support는

**h_Z(s) = s·(a₀+A c) + ∣s·A v∣ + Σ_i h_i∣s·A_:i∣.**

증명: 각 θ, q_i가 독립 구간 [-1,1]에 있으므로 s·a의 최대는 각 항의 계수 부호에 따라 각각 끝점에서 달성된다. 같은 원리로 최소는 −s에 대한 최대로 얻는다. 물리적 likelihood에서 독립이라는 가정은 사용하지 않았다. 정확히 2^(1+7)=256개 외곽 꼭짓점의 완전 확인은 수치 프로그램의 교차검사일 뿐, 위 해석적 증명에서 요구되지 않는다.

추가로 1열 진폭-only 잔차의 profile χ²와 2열 profile χ²의 차이는 

ΔQ(θ,j) = [x_⊥ᵀW(r+θv+j)]²/(x_⊥ᵀWx_⊥)≥0, x_⊥ = x−1(1ᵀWx)/(1ᵀW1),

C가 양정치이고 x_⊥≠0이므로 항상 비음수다. 256개 상자 꼭짓점에서 정확 유리수로도 확인. 이 항등식은 nuisance box를 확률적 marginalization으로 바꾸지 않는다.

## R7–R8: 실제 수치 정리

- 기존 nominal κ₀=0.068661739480590678 dex/z; β₀=-0.045918743031444754 dex.
- EOS 방향 dκ/dθ=-0.0093026302737762596 dex/z, 이전 PR253과 동일 (새 독자성 주장 없음).
- Jeans 중심 shift=0.007759682736426245 dex/z; Jeans half-width=0.013501287175325168; EOS half-width=0.0093026302737762596.
- **κ ∈ [0.053617504767915498, 0.099225339666118351] dex/redshift**, 끝점은 정확 유리수 연산과 명시적 꼭짓점 witness로 달성됨.
- β ∈ [-0.13087466565371772, 0.051206812137275709] dex (β와 κ 각각의 한계는 서로 다른 꼭짓점에서 달성될 수 있으므로 둘을 직교 신뢰상자로 오해하지 말 것).
- κ-min witness: θ=+1, γ=1.6; j=['0.001', '0.0060000000000000001', '-0.0030000000000000001', '-0.0030000000000000001', '-0.0040000000000000001', '-0.0050000000000000001', '-0.014'].
- κ-max witness: θ=−1, γ=1.2; j=['-0.016', '-0.0080000000000000002', '0.012', '0.016', '0.021000000000000001', '0.023', '0.023'].
- 256/256 exact corner supports 및 nested χ² identity 점검. 별도 NumPy Cholesky/solve 256-corner 결과와 각 4개 극값 차이 < 3×10^-17. 별도 Wolfram 선형대수 대조도 부호/숫자 일치. 표적 테스트 8/8 PASS.

이 결론은 **인쇄된 EOS 방향과 per-redshift Jeans 구간의 직사각형에서 κ의 0 교차가 없다는 조건부 support 정리**다. 실제 물리적 UVB slope 발견, 관측 원자료의 독립 선별, posterior, 모델 불확실성 전파, Bianchi global velocity tilt, 완결된 F4·L4·native25가 아니다. C에 Jeans를 임의로 quadrature 합성하지 않았다. 

## 다음 과학 및 코드 경계

Source-labelled 범위의 독립 모델 심사 R6/C9는 `NOT_RUN` (이 스레드에서 native child 도구 없음). 기존 PR253·254·255의 결과와 충돌하면 새 산출물은 observation-only 참고자료이며 owner source 결과를 자동 덮어쓰지 않는다. 새 실수치 IVP, heat, photo-rate, Li provider, 종 배열 및 중앙 DAG 갱신 없음. 실험 개시 전 resource: 새로운 bounded mathematical commands 5+5 CPU seconds target. 그림 작업은 실제 8 CPU-s process limit으로 별도 실행했지만 사전 budget ledger에 없는 보충 실행이므로 resource allocation은 CONCERN으로 보존한다. 측정값과 미측정 overhead 분리. `UNKNOWN_NOT_ZERO`, closed grants 유지. 원 DAG working33/88, central28/88, delta0.
