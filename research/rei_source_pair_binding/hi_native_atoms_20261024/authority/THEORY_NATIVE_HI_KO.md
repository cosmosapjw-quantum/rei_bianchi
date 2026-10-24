# HI 원자 측도에서 수·에너지 source를 직접 연결

## 연구 단위와 실제 입력

이번 단위는 `HI_NATIVE_ATOMS_20261024`다. 기존 HI summary, stock, work의 채택·원본을 재사용하며, 새로 확보한 원자 CSV의 z=2.479·HI 4,368행을 직접 소비한다. 전체 32,592행 CSV는 bass_cr@b8882d026887f375acf90768d4e3740eb03da226의 `research/cr_c23b_source_frame_20261023/source_providers/runs/c23b_pw19_spectral_source_20261023_v1/photoelectron_atoms.csv`, Git blob b01f4c94faffd9a44ca4dcf31231bd6b7da2b766, SHA256 f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3, 1,681,578 bytes다. 과거 execution identity는 277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955다.

공급자 원문은 CSV와 summary가 같은 order16 atoms에서 작성되었음을 보여 준다. 새 quadrature·공급자 suite·과거 REI suite는 실행하지 않는다. CSV에는 kinetic_eV와 number_weight_per_target_s만 있으며 각방향 열은 없다. 원자를 읽을 때 decimal spelling을 float로 복원한 뒤 exact represented Fraction을 취한다. 이것은 원 binary64의 round-trip 의미를 보존한다.

물리 조건은 elemental ground-state HI, bath-rest target, proper second, zero recoil, χ=represented float(13.6) eV, photon upper endpoint 50000 eV, no-deposition이다. 원자 k는 kinetic excess이고 공급자 물리식은 E=k+χ다. 현재 단위에서는 k를 원자료로 유지하고 이 식의 exact represented lift를 사용한다. 이전 independently rounded summary A/B/P/K는 그대로 별도 보존한다. `c, ħ, k_B`의 값·convention 변경은 없다. 서명은 (-,+,+,+)다.

## 1. 공통 양의 측도와 보존 source

유한한 k_j≥0, w_j>0에 대해 μ=Σ_j w_j δ_(k_j)를 정의한다. 단위는 target⁻¹ s⁻¹이며,

    A*=Σw_j,  K*=Σw_j k_j,  B*=χ A*,  P*=Σw_j(χ+k_j)=B*+K*.

각 항의 원자료 값과 모든 곱·합을 유리수로 해석하면 이 등식은 정확하다. A*>0, K*≥0이고 support 상한 L≥max k_j에 대해 0≤K*≤L A*다. 이는 실제 atom 좌표/가중치를 가진 source이며 순간 source rate다. 시간 적분된 particle stock과 구별한다.

m=a X_HI≥0, dm=a dX_HI+X_HI da라고 하자. energy owner 순서는 thermal,binding,UV,dynamic_escape,source_reservoir,primary_nonthermal이고,

    q=m(0,B*,-P*,0,0,K*),  Jv=dm(0,B*,-P*,0,0,K*).

입자 순서는 HI,HII,e_nt,e_th,photon이다.

    q_n=m A*(-1,+1,+1,0,-1),  Jv_n=dm A*(-1,+1,+1,0,-1).

따라서 exact energy sums는 0이고 HI+HII의 핵수, HII−e_nt−e_th의 전하 source는 0이다. 고정 μ에서의 JVP는 다항식 곱의 정확한 미분이다. 접선은 signed finite 값이며 m 또는 dm을 중간 float로 만들지 않는다. e_nt를 thermal pool에 자동 합치지 않는다. q_thermal=0은 선택 모델이며 actual secondary_heat=null을 유지한다.

이것은 기존 summary residual을 다른 owner에 분배하는 수리가 아니다. 새 atom-native 경로에서 같은 event measure의 서로 다른 모멘트를 계산한다. 이전 summary API와 저장값은 바꾸지 않으며 두 경로의 차이는 아래 정확한 항등식으로 설명한다.

## 2. 공급자 반올림과 exact native 모멘트의 차이

RN은 binary64 nearest rounding, F는 저장 summary의 fsum 단계다. 실제 source의 연산 순서는 다음과 같다.

    a_hat=F(w_j)
    k_hat=F(RN(k_j w_j))
    b_hat=RN(χ a_hat)
    p_hat=F(RN(w_j RN(k_j+χ))).

S_K=Σ RN(k_j w_j), S_P=Σ RN(w_j RN(k_j+χ))를 각 반올림 결과의 exact 합으로 정의한다. 원자료 summary와 exact 값의 차이는 다음처럼 완전히 분해된다.

    ΔA=a_hat−A*
    ΔK=(k_hat−S_K)+Σ[RN(k_j w_j)−k_j w_j]
    ΔB=[b_hat−χ a_hat]+χ ΔA
    ΔP=(p_hat−S_P)+Σ[RN(w_j RN(k_j+χ))−w_j RN(k_j+χ)]
                           +Σ w_j[RN(k_j+χ)−(k_j+χ)].

각 식은 덧셈·뺄셈에 의한 exact identity다. 따라서 ΔB+ΔK−ΔP는 기존 represented r_E이고, ΔB−χΔA는 represented r_B다. 공급자 `energy_ledger_residual`의 실행 순서 P−B−K 및 그 저장값은 별도 필드로 보존한다. summary rounding이 존재해도 원자 측도의 양성·유한 support·보존 source를 직접 검사할 수 있다.

새 비교 기준은 물리 오차 허용치가 아니라 이 유한 artifact의 산술 결속이다. 모든 exact decomposition identities=0, 저장된 각 scalar RN operation은 direct binary64 operation과 같음, 실제 summary fsum 단계의 exact subtotal 차이는 해당 저장값의 1 ulp 이하라는 유한 certificate를 검사한다. 이 마지막 조건은 fsum의 보편 오차 정리가 아니며 실제 값의 관계를 검사한다. 기존 2e−12 L0 gate와 donor 2e−14/2e−11 기준은 그 원래 범위에서 그대로 둔다. 이번 결과는 공급자 quadrature의 새로운 전 구간 정확도나 데이터 불확실성의 bound를 만들지 않는다.

## 3. 구현의 반올림과 독립 참조

주 계산은 Fraction이며 최종 각 float component에서 한 번만 round한다. Exact component를 x_i, 반환 float를 y_i라 하면 sum y_i=sum(y_i−x_i)다. 각 y_i의 양쪽 이웃과의 간격의 절반 중 큰 값은 해당 RN 오차를 포함한다. zero/subnormal도 Fraction으로 처리하며 실제 ledger residual은 이 반올림 예산과 비교한다. final-underflow-to-zero는 exact zero와 별도 표시한다. 허용되지 않는 overflow/nonfinite는 명시적으로 거절한다.

독립 수치 참조는 원 float의 as_integer_ratio()를 사용해 공통 2의 거듭제곱 denominator로 정렬한 정수 accumulator다. Fraction accumulator를 호출하지 않고 A*, K*, B*, P*를 별도로 만들고 exact cross multiplication으로 비교한다. 합성 두 atom (k,w)=(0,1),(2,3), χ=4에서는 A=4,K=6,B=16,P=22, m=1/2에서 energy=(0,8,−11,0,0,3), particle=(−2,2,2,0,−2)다. 이 hand-derived 사례와 실제 4,368행이 서로 다른 검증 역할을 한다.

## 4. 이후 stock/work 연결과 남은 실제 입력

μ는 순간 per-target injection measure다. n_HI가 공급되면 I=a n_HI μ이며 Q_N=a n_HI A*, Q_U=a n_HI K*다. Href와 physical-density normalization은 한 경로에서 한 번 적용한다. 현재 실제 n_HI, 초기 ν0, geometry/time history, photon supply·stopping 구간은 아직 선언되지 않았다.

선언된 isotropic angular closure에서는 μ⊗dΩ/(4π)를 사용해 flux/STF source가 0이다. CSV 자체는 측정된 angular distribution을 제공하지 않는다. massive stress의 추적 모멘트는 향후 M=mc²가 결속되면 ∫k(k+2M)/(k+M)dμ로 얻는다. 소스율을 현재 stock N/U로 대체하거나 기존 자유각 sharpness를 isotropic 제약에 이전하지 않는다.

직전 stock/work의 유도와 실행은 재사용한다. 새 원자 결속은 six-row 입력표의 measure 행을 실제 원자료 수준으로 전진시킨다. 실제 시간·밀도·IC·geometry·transport가 필요한 다음 cohort는 그 입력이 있을 때 이어간다. L4_ready=false, whole-model completion=null이다.

## 근거·판정 규칙

- 원전: Puchwein et al., MNRAS485,47(2019), DOI10.1093/mnras/stz222; 실제 사용한 Taira2025 PW19 v1.0.0 release DOI10.5281/zenodo.15367103 및 위 donor 핀을 구별한다. arXiv1801.04931v1의 D1 table과 byte/model 동등성을 주장하지 않는다.
- Verner et al., ApJ465,487(1996), arXiv astro-ph/9601009v2의 ground-state fit과 donor χ/support를 대응시킨다. 원 fit·source normalization 재계산0.
- native independent R6/C9는 원 CSV·공급자 source·본 유도·새 code/raw를 읽고 한 pass에서 판정한다. CAS는 보조 exact identity 확인이며 독립 model review로 표시하지 않는다.
- 새로운 strong no-go 또는 문헌 최초성 주장은 없다. NG1–NG7은 그러한 신규 성과 채택에 적용하지 않는다.
