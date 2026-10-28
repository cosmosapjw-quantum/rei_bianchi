# 다음 이론 단위: 유한 비열적 전자 분포의 압력 모멘트

## 1. 목적과 현재 지위

선택 L1은 일차 전자의 수와 운동에너지 source를 명시적 비열적 저장고에 전달한다. L4에서 이 저장고를 Einstein/work 식에 넣으려면 압력 trace와 시간에 따른 분포 또는 명시적 closure가 추가로 필요하다. 여기서는 그 다음 의무를 유한 양의 측도에 대한 정확한 압력 구간으로 좁힌다.

이 문서는 해석적 유도이다. 저장된 HI source를 재적분하지 않았고 새로운 IVP, stopping, 온도 진화 또는 압력 수치 실행을 하지 않았다. 이 구간을 물리적 오차 막대나 선택된 equation of state로 채택하지 않는다. 독립 검토와 정적 코드 준비는 별도 기록한다.

## 2. 변수·단위·운동학

선택 bath-rest frame에서 전자 운동에너지를 k, 전자의 rest energy를 M=m_e c^2>0라 쓴다. 두 값은 같은 에너지 단위다. 양의 유한 측도 dν(k)는 0≤k≤L에 지지되고
N=∫dν, U=∫k dν
이다. 이는 입자 재고 또는 주입률 측도로 각각 사용할 수 있지만, 두 해석의 단위를 혼합하지 않는다.

물리 운동량 p_phys와 속도 v는
p_phys^2 c^2=k(k+2M), v=p_phys c^2/(k+M)
이므로
g(k)=p_phys v=k(k+2M)/(k+M)=k+M-M^2/(k+M).

등방적 분포의 압력 모멘트는
Π=(1/3)∫g(k)dν(k).
실제 재고 측도가 Href당이면 Π는 eV/Href이고 물리 압력은 n_Href eV_to_J Π이다. 주입률 측도라면 Π의 단위는 eV/(Href s)이며 해당 source의 instantaneous pressure-moment injection이다. 이것만으로 저장된 재고의 현재 압력을 주지 않는다.

운동학적 pressure integral은 Enßlin–Kaiser, arXiv:astro-ph/0001429v2, Appendix A Eq.(A.6)의 일반 p v 적분과 연결된다. 그 논문의 특정 power-law 적분과 전자 스펙트럼을 여기의 HI source로 대체하지 않는다.
Primary URL: https://arxiv.org/pdf/astro-ph/0001429

## 3. 양 끝이 달성되는 압력 구간

M>0, L>0, N>0, 0≤U≤NL를 가정한다. 미분하면
g'(k)=1+M^2/(k+M)^2>0,
g''(k)=-2M^2/(k+M)^3<0.
따라서 g는 엄격히 오목하고 g(0)=0이다. 오목성의 chord inequality는
g(k)≥(k/L)g(L)
를 주며, 적분하면
Π_min = U(L+2M)/[3(L+M)] ≤ Π.
확률측도 dν/N에 Jensen 부등식을 적용하면
Π ≤ Π_max = U(U+2MN)/[3(U+MN)].

최솟값은
dν_min=(N-U/L)δ_0+(U/L)δ_L,
최댓값은
dν_max=Nδ_(U/N)
으로 각각 달성된다. 두 측도는 동일한 N과 U를 갖는다. 구간 폭은
Π_max-Π_min = UM(NL-U)/[3(U+MN)(L+M)].
따라서 0<U<NL이면 양 끝의 차이는 양수다. 이것은 특정 유한 모멘트 문제의 구성적 결과이며 새로운 strong no-go나 문헌 신규성 주장이 아니다.

N=0이면 유효한 양의 측도는 U=0을 요구하고 Π=0이다. L=0이면 U=0이고 Π=0이다. U=0도 Π=0이다. 이 경계에서는 U/N 또는 U/L를 평가하지 않는다.

비상대론적 근사 Π_NR=2U/3의 정확한 차이는
Π_NR-Π=(1/3)∫k^2/(k+M)dν≥0.
그리고
0≤Π_NR-Π≤UL/[3(L+M)].
이는 주어진 support에서의 운동학적 근사 오차 경계다. 열화 또는 thermal temperature에 대한 진술은 포함하지 않는다.

## 4. 작은 정확한 구성

N=2, U=2, L=2, M=1이라는 무차원화된 예제에서
Π_min=8/9, Π_max=1.
δ_0+δ_2와 2δ_1은 각각 두 끝을 달성한다. 이는 종이 위 정확한 분수 유도이며 이번 단위의 실행된 fixture 결과가 아니다.

## 5. 현재 HI source와의 연결

선택 source의 주입률 측도라면 N=A, U=K, L=E_max-χ이고 전체 Href당 주입률에는 m=a X_HI를 정확히 한 번 곱한다. A와 K는 독립 반올림된 저장 입력이므로 위 interval은 그 표현된 N/U/support를 갖는 가능한 양의 측도의 조건부 interval이다. donor의 원 quadrature나 물리 source uncertainty에 대한 검증 결과로 바꾸지 않는다. B, P, r_B, r_E와 원 donor residual은 기존 L1 그대로 둔다.

실제 원자별 dμ를 소비하면 같은 양의 weights와 k=E-χ로
A=Σw, K=Σwk, Π_inj=(1/3)Σw g(k)
를 함께 계산할 수 있다. 이 route는 실제 raw payload/schema와 byte identity, 적절한 실행 예산이 있을 때 별도 실행한다. 현재 summary route를 원자 route였다고 표시하지 않는다.

L1의 isotropic STF0는 이 선택 각분포 아래 trace-free 성분이 0이라는 뜻이다. 위 Π가 추가하는 것은 scalar pressure trace의 정확한 조건부 범위다. source의 moment injection을 state closure로 옮기려면 초기 분포와 redshift/transport/stopping 또는 명시적 approximation을 먼저 선택해야 한다.

## 6. 코딩 계약

별도 소형 stdlib 모듈을 research/rei_source_pair_binding/hi_pressure_next_20261024/ 아래 정적으로 준비한다. 기존 source_pair.py와 source_card.json은 변경하지 않는다.

- pressure_interval_from_moments(N,U,L,M): exact represented Fraction 구간과 폭, NR upper-error bound를 반환한다.
- pressure_moment_from_atoms([(weight,k),...],M,L): 비음수 유한 weights/support를 확인하고 exact represented N,U,Π를 반환한다. 외부 공급자를 자동 fetch하거나 qualifying하지 않는다.
- bool/nonfinite/negative/unsupported inputs는 명확히 거절한다. M>0; U≤NL를 exact 비교한다.
- 모든 계산은 공급된 int/Fraction/finite float의 정확한 표현으로 한다. 출력 Fraction은 조건부 수학적 결과이며 physical precision을 복원하지 않는다.
- 한 미래 focused fixture만 준비한다: 위 8/9와1 끝점, 중간 혼합, 0 경계, invalid U>NL 거절, 공통 scaling. donor 재적분과 IVP는 없다.
- 현재 새 모듈의 import/compile/run은 0이다. numerical admission은 실행 후 결정한다. 다음 prospective 단일 child CPU1s/wall5s/no retry를 제안하며 현재 승인된 L1 child의 잔여분을 전용하지 않는다.

## 7. 문헌·도구 관계

Furlanetto–Stoever arXiv:0910.4410은 전자 에너지와 배경 ionized fraction에 따른 energy deposition 분할을 다룬다. Pawlik–Schaye arXiv:1008.1071v2 Eqs.(14–17)은 excess-weighted rate와 complete thermalization 가정을 구별하는 근거다. 이번의 명시적 비열적 저장고는 그 구별을 유지한다.
https://arxiv.org/abs/0910.4410
https://arxiv.org/html/1008.1071v2

현재 SciSpace 검색은 10개 결과를 반환했다. Hoegy의 NASA-TM-85124 원문 메타데이터/초록에서 kinetic tail와 thermal population 경계에 관한 문맥을 확인했다. 이를 이 HI source의 새로운 stopping provider로 채택하지 않았다.
https://ntrs.nasa.gov/citations/19840007873

Wolfram context 호출은 이번에 성공했지만 이 압력 부등식의 검증 결과를 반환하지 않았다. 관련 없는 숫자/문서 제안은 모델에 반영하지 않았다. 새로운 Wolfram evaluator 실행은 0이며, 위 유도는 명시적 미분·Jensen·양 끝 측도 구성으로 검토한다. Native independent review와 CAS 상태는 별도로 기록한다.
