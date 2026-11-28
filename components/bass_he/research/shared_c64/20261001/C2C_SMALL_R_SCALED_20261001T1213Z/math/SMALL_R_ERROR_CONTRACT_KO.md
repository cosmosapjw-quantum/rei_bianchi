# C2c 작은 R: scaled 오차·상쇄·물리적 상자 계약의 유도

이 문서는 C2c 실행 전 독립 수학 설계다. 새 고유값 계산이나 Coulomb 공간 적분을 수행하지 않았다. 아래 수치는 **사전등록에 대한 제안**이며, 최종 실행 허용오차·작업 수는 루트 `CONTRACT.json`이 소유한다. A2의 직접 유도, 부모 C2a의 저장 결과, 이번 오차 전파 유도를 구분한다.

## 1. 정의와 단위

고정 핵, 비상대론적 한 전자 Hamiltonian, 전하수 `(1,2)`, 양의 meridional phase인 최저 `m=0` 및 real cosine bright `|m|=1` 상태를 유지한다. 핵 반발의 공통 scalar는 전자 Hamiltonian에 포함하지 않는다. 원점 O는 전하중심이며 `z_A=-2R/3`, `z_B=R/3`이다.

\[
a_A=\frac{\hbar^2}{m_e\kappa},\quad
E_A=\frac{\hbar^2}{m_ea_A^2},\quad
x=R/a_A,\quad
\ell_O=\frac{\langle g,L_y^Ob\rangle}{-i\hbar},\quad
S(x)=\frac{\ell_O(x)}{x^3}.
\]

이후 길이·에너지·운동량·dipole은 각각 `a_A`, `E_A`, `-i hbar/a_A`, `a_A`로 무차원화한다. `P=<g,p_x b>/(-i hbar/a_A)`, `D=<g,x_cart b>/a_A`, `Delta=(E_b-E_g)/E_A>0`이면 정확한 관계는

\[
\ell_O=\ell_B+\frac{x}{3}P,\qquad P=\Delta D.
\tag{1}
\]

두 번째 식은 수치 운동량의 정의로 사용하지 않는다. 직접 미분한 P와 별도로 계산한 Delta D를 비교한다. `x_cart`와 핵 거리 x를 혼동하지 않는다.

A2의 채택된 결과는

\[
\ell_O(x)=C x^3+O(x^{7/2}),\qquad
C=\frac{4\sqrt2}{15}=0.3771236166328254\ldots,
\quad S(x)=C+O(\sqrt{x}).
\tag{2}
\]

O 항의 상수와 유효 반경은 알려져 있지 않다. 따라서 이번 네 점이 점근 구간 안이라는 결론, 단계별 `1/sqrt(2)` contraction, 단조성, 특정 상대 정확도를 (2)에서 도출할 수 없다. C를 데이터에 맞추거나 고차 계수를 조절하여 acceptance를 통과시키지 않는다.

## 2. 수치 오차와 유한 R 효과의 분리

어떤 계산 lane의 값이 `ell_hat=ell+e_num`이라면

\[
\widehat S-C=\underbrace{[S(x)-C]}_{\text{유한 R 효과}}
+\underbrace{e_{\rm num}/x^3}_{\text{수치 오차}}.
\tag{3}
\]

그러므로 raw 허용오차만 유지하면 작은 x에서 scaled 정확도가 빠르게 악화된다. scaled 허용오차 `tau_S`는 raw 단위로 `|delta ell| <= tau_S*x^3`, 물리 단위로 `|delta L| <= hbar*tau_S*x^3`다. 부모 raw cap과 새 scaled cap을 둘 다 요구하여 실효 cap을 두 값의 minimum으로 둔다. dyadic 입력 `.25,.125,.0625,.03125`는 binary64에 정확히 표현되어 입력 거리의 추가 반올림은 없다.

권고 scaled cap은 독립 h/p/tail 차이 각각 `2e-6`, direct–force 차이 `1e-7`, operator quadrature 증가량 `1e-8`다. 이것은 해석적 정리가 제공한 오차 상한이 아니라 계산 전에 선택하는 경험적 수렴 기준이다. 동일 x에서 같은 상태 정의와 위상으로 비교한다.

| x | x³ | h/p/tail raw cap | direct–force raw cap | quadrature raw cap |
|---:|---:|---:|---:|---:|
| 0.25 | 0.015625 | 3.125e-8 | 1.5625e-9 | 1.5625e-10 |
| 0.125 | 0.001953125 | 3.90625e-9 | 1.953125e-10 | 1.953125e-11 |
| 0.0625 | 0.000244140625 | 4.8828125e-10 | 2.44140625e-11 | 2.44140625e-12 |
| 0.03125 | 0.000030517578125 | 6.103515625e-11 | 3.0517578125e-12 | 3.0517578125e-13 |

권고는 기저 degree와 mesh 크기, eigensolve 조립 q, 관측량 적분 q, tail 확장을 서로 구별해 기록하는 것이다. 고차 적분의 연속 두 증가량과 direct–force의 terminal 값들이 모두 만족해야 quadrature plateau를 인정한다. 조립 q 증가를 관측량 q 증가와 동일시하지 않는다. tail은 내부 physical proxy mesh를 그대로 둔 채 바깥 셀만 추가한다.

기존 에너지·norm·algebraic residual 기준은 유지한다. 작은 algebraic residual은 continuum 또는 공간 이산화 오차의 상한이 아니다. 관측된 h/p/tail/q spread를 합한 값은 보수적인 **경험적 불확실성 지표**로 쓸 수 있지만 엄밀한 enclosure나 독립 확률 오차로 부르지 않는다. 각 축의 한 번 비교로 공통 bias가 제거됐다고 할 수 없다.

## 3. 원점 이동·운동량 상쇄의 오차

식 (1)의 불일치를 scaled 수준에서 확인하려면

\[
\epsilon_{\rm origin,S}
=\frac{|\ell_O-\ell_B-(x/3)P|}{x^3},\qquad
\epsilon_{p\to S}
=\frac{|P-\Delta D|}{3x^2}
\tag{4}
\]

를 기록한다. 뒤의 양은 운동량 discrepancy를 원점 관계로 전달했을 때의 scaled 오차다. direct LO를 운동량에서 재구성하라는 뜻이 아니다. 각 값에 `1e-7` cap과 부모 raw cap을 함께 권고한다. 특히 `x=.03125`에서 부모 raw 운동량 cap `1e-7`만 쓰면 `epsilon_(p->S)=3.41e-5`를 허용하므로 scaled 검산으로 충분하지 않다. 선택규칙 dark 값도 raw와 `/x^3` 값을 둘 다 기록하되 dark 영만으로 bright 정확도를 인증하지 않는다.

A2에서 `P -> 16sqrt(2)/27`, `ell_B = -16sqrt(2)*x/81+O(x^3)`이므로 원점 재구성의 subtraction condition indicator는

\[
\chi_O=\frac{|\ell_B|+|(x/3)P|}{|\ell_O|}
\sim\frac{40}{27x^2}.
\tag{5}
\]

`x=.03125`에서 이 leading 지표는 약 1517이다. 직접 LO lane은 두 최종 scalar의 합이 아니라 자체 integrand를 적분하므로 (5)가 그 integrand 전체의 condition number는 아니다. 실제 scalar 진단과 leading 예측을 구별한다. norm 오차나 P 오차를 무조건 같은 비율로 확대해 적용하지 않는다.

## 4. Force lane의 독립 오차 전파

무차원 `T_C=a_A^2<g,x_cart/r_C^3 b>`를 쓰면

\[
U=T_B-T_A,\qquad
S_F=\frac{2}{3x^2}\frac{U}{\Delta}.
\tag{6}
\]

아래는 임의의 유한 차분에 대한 항등식이다. `U_hat=U+delta U`, `Delta_hat=Delta+delta Delta`일 때

\[
\widehat S_F-S_F
=\frac{2}{3x^2}
\left[\frac{\delta U}{\widehat\Delta}
-\frac{U\,\delta\Delta}{\Delta\widehat\Delta}\right].
\tag{7}
\]

만약 실제로 `|delta U|<=e_U`, `|delta Delta|<=e_Delta<Delta`인 상한을 가지고 있다면

\[
|\widehat S_F-S_F|
\le\frac{2}{3x^2}
\left[\frac{e_U}{\Delta-e_\Delta}
+\frac{|U|e_\Delta}{\Delta(\Delta-e_\Delta)}\right].
\tag{8}
\]

현재 h/p/q 차이는 (8)의 엄밀한 입력 상한이 아니다. 이 식은 각 discrepancy의 전파 크기를 추적하는 데 사용하며 인증으로 승격하지 않는다. gap은 UA에서 `27/8`로 접근하므로 물리적 영분모 문제는 없다. 작은 x에서 위험한 부분은 `U=O(x²)`의 차감과 상태·적분 오차다.

정규화 UA s–p 함수로 `T_A,T_B -> 4/(3sqrt(2))`; 식 (2),(6)과 `Delta ->27/8`에서

\[
U\sim\frac{27\sqrt2}{20}x^2,\qquad
\chi_F=\frac{|T_A|+|T_B|}{|T_B-T_A|}
\sim\frac{80}{81x^2}.
\tag{9}
\]

`x=.03125`에서 leading chi_F는 약 1011이다. `unit_roundoff*chi`는 최종 subtraction의 척도일 뿐 기저 함수 평가·다수 항 합산·eigensolve의 총 roundoff 상한이 아니다. 실제 T_A,T_B, gap, 두 chi, native/reference discrepancy, q increment를 저장한다. 낮은 정밀도, fast-math, 허용오차 완화로 plateau를 감추지 않는다. 사전등록한 depth 끝에서도 scaled 기준을 만족하지 못하면 수치 미해결로 종료한다.

## 5. Prolate 상자의 실제 물리적 크기

현재 solver의 `radial_extent=L`은 xi 값 자체가 아니다. 무차원 물리 길이 L에 대해

\[
\xi_{\max}=1+\frac{2L}{x},\quad
\rho=\frac{x}{2}\sqrt{(\xi^2-1)(1-\eta^2)},\quad
z=\frac{x}{2}\xi\eta-\frac{x}{6}.
\tag{10}
\]

경계는 midpoint `M=-x/6`에 중심을 둔 타원체이고 반장축·반단축은

\[
a=L+x/2,\qquad b=\sqrt{L(L+x)}.
\tag{11}
\]

따라서 `L=30` 고정이면 x가 작아져도 상자는 축소되지 않고 반지름 30의 구에 접근한다. xi_max는 x=.25,.125,.0625,.03125에서 각각 241,481,961,1921이다. z축 끝점은 `-L-2x/3`, `L+x/3`이며, 이 범위처럼 `L>=x`이면 O에서 경계까지 최소 거리는 `L+x/3`, 최대 거리는 `L+2x/3`다. 이산화 밖의 정확한 파동함수 tail이 0이라는 뜻은 아니다. 유한 바깥 Dirichlet 경계의 영향을 별도로 변화시켜야 한다.

기본 radial grading은

\[
\xi_j=1+\frac{2L}{x}(j/N)^2,\qquad
y_j=\frac{x}{2}(\xi_j-1)=L(j/N)^2.
\tag{12}
\]

따라서 y_j는 x에 무관한 물리적 길이 proxy다. 다만 y는 정확한 O-centered 구면 반지름이 아니며, 내부 핵 영역 `y~x`를 덮는 셀 수는 대략 `N*sqrt(x/L)`로 감소한다. `N=64,L=30,x=.03125`에서는 약 2.07이다. 물리 box를 고정했다는 이유만으로 내부 Coulomb 영역을 충분히 분해했다고 주장할 수 없다. h/p와 singular quadrature 검산이 이 위험을 담당한다. tail 확장은 기존 y<=30 셀을 보존하고 30<y<=40 셀만 추가해야 h/tail이 섞이지 않는다.

## 6. 독립 앵커와 유한 수열 판정

새 작은 R 중 가장 큰 `x=.125`에 독립 구면 앵커를 두는 것이 예산상 합리적이다. 부모의 B-centered spherical 기저와 O 원점 환산을 유지하고 두 개 이상의 사전등록 기저 수준을 비교한다. 부모 raw LO 비교 cap `1e-5`만 쓰면 x=.125에서 scaled 차이 0.00512를 허용하므로 별도 scaled cap이 필요하다. 독립 앵커의 권고 scaled cap은 prolate 내부 수렴 기준과 구별하여 agreement `1e-4`, 마지막 기저 증가량 `2e-5`다. 부모 raw cap도 유지한다. 이 숫자는 실행 전 선택이며 결과를 본 뒤 변경하지 않는다.

부모 R=.5에서 구면 l72→96의 raw LO 변화는 `9.968188244280363e-8`, 마지막 prolate 차이는 `7.589044732220218e-8`였다. 이것은 x=.125에서 같은 수준이 충분하다는 증거가 아니다. l 증가와 radial/degree 증가를 구별하고, 필요하면 실행 전 등록한 fallback만 허용한다. 새 구간의 공통 O physical overlaps, 양방향과 자기 norm, 연속 두 q increment를 확인하고 기존 .25 상태에서 phase를 연결한다. signed LO를 비교하며 절댓값으로 잘못된 위상을 가리지 않는다.

판정은 세 층으로 나눈다.

1. `numerical_sequence_convergence`: 각 x에서 등록한 raw+scaled 기저/적분/정체성/앵커 gate의 통과 여부. 통과해도 유한 격자의 경험적 안정성이다.
2. `finite_R_approach_diagnostic`: `D_i=|S(x_i)-C|`, 상대 차이, `D_i/sqrt(x_i)`, 관측 차수 `log(D_i/D_(i+1))/log(2)`를 기록한다. 마지막 비율은 두 D가 수치 spread보다 분명히 클 때만 해석한다. 감소 또는 단조성을 관측하면 그 네 점의 사실로 보고한다. 예상 contraction을 강제하지 않는다.
3. `asymptotic_certificate`: 미지 Big-O 상수·적용 반경·continuum enclosure가 없어 이번 계산으로 닫히지 않는다. full C2, hidden crossing, rank-five cluster, collision propagation, Eq55는 이 결과로 승격하지 않는다.

부모 .25 저장 결과는 direct S≈0.2288956021988902, force S≈0.22889560220098468로 C와 약 0.14823 다르지만, 같은 점의 direct–force scaled 차이는 약 `2.1e-12`였다. 이는 기존 유한 R 편차를 수치 오차로 오인하면 안 된다는 구체적 예다. 새 점 결과는 이 문서에서 계산하거나 예단하지 않았다.

## 근거 상태와 입력

- A2 analytic input: `BASS_HE_A2_ASYMPTOTIC_STRUCTURE_20261001_v1/A2_ASYMPTOTIC_DERIVATION_KO.md`, 특히 A2.1–8, A2.16–17. 채택된 derived asymptotics이며 numerical constants/radius는 없음.
- 수치 정의: 부모 C2a `math/OPERATOR_DERIVATION_KO.md`, `reference/spheroidal_tail.py`, `code/prolate_fast.py`를 직접 읽었다.
- 기존 값 재사용: 부모 C2a `evidence/PROLATE_MPI/R0p25_{base,h,p,tail}/RESULT.json`, `evidence/ANCHOR_COMPARISON.json`. 원 결과 재계산 없이 JSON 수치의 나눗셈·비교만 수행했다.
- 인계 범위: C2b `NEXT_HANDOFF_KO.md`. 이 문서의 작성 과정에서 신규 물리 eigensolve와 공간 적분은 0회다.
