# HE29 공유 기준해 분해와 유한 후보 hull: 독립 이론 검토

검토 시점: 2026-10-20 06:20 UTC. 이 문서는 최신 반환 intake가 마감된 뒤 수행한 bounded 이론 검토다. 담당자는 root 구현 작성자와 분리되어 원래 분석 코드를 읽고 식을 유도했다.

**판정:** 저장된 수치에 대한 signed 분해, 공유 변수의 계수 합산, product 후보 hull과 동일 방법 후보 hull의 구별은 대수적으로 성립한다. 새 합성 검산 **20개 고유 사례 PASS**를 남겼다. HE29 기준해의 실행 완료 수는 이 검토로 증가하지 않는다. 새 native 실행, 기존 tests 실행, 기존 HE28/HE29 수치 재계산은 각각 **0**이다.

| 축 | 이 문서 작성 시점의 상태 |
|---|---|
| DAG | 이 단위의 정의·유도·후보 집합 구별·독립 합성 검산 완료. root 신규 구현의 코드 판독은 별도 후속 검토 대상으로 구분 |
| 게시 | Git 작업 트리에 이 문서와 evidence/THEORY_REVIEW.json 작성. commit·push·remote readback은 root 게시 receipt가 담당 |
| 백업 | 이 검토자가 새 업로드를 수행하지 않음. intake에서 재사용한 이전 백업과 이번 단위의 후속 백업 receipt를 구별 |
| 과학적 반환 | intake에서 확인된 새 HE29 기준해 0/4. 아래 합성 예시는 native 결과가 아님 |

적용 skill은 현재 standalone **physmath-research-loop 1.0.0**이다. 과거 1.3.0의 연구와 Schur 검산은 재사용 근거이며, 이번 활성 실행으로 다시 세지 않는다.

## 1. 실제 읽은 계약과 새 작업의 경계

원래 HE29의 다음 파일을 실제 읽었다. 파일별 SHA256은 동반 JSON에 있다.

| 원래 파일·함수 | 확인한 사실 | 새 분석에 주는 제약 |
|---|---|---|
| src/reference_runner.py의 parent_comparisons | table512에서만 원래 transport와 같은 model/table을 연결한다. 저장하는 온도 오차는 절댓값이다 | signed residual의 부호는 그 절댓값에서 복원할 수 없다. 저장된 transport와 reference 온도 원값을 사용해야 한다 |
| 같은 파일의 run_case | Radau와 DOP853 파일을 각각 방법 완료 직후 저장하고, 두 방법의 admission 뒤 최종 RESULT를 작성한다 | method 파일 하나의 존재는 pair 완료와 다르다 |
| src/analyze_references.py | case identity·owner·thread·table·6점 qualification과 pair gate를 확인한다. case 사이의 binary/source/input/thread identity도 대조한다 | 새 대수 분석은 이 admission을 재사용해야 한다 |
| src/reference_contract.py | 온도 method spread 1e-9 K와 절대 fraction 차 1e-11 gate를 적용하고 error_radius_certified=False를 유지한다 | 방법 간 일치를 참해의 오차반경으로 바꾸지 않는다 |
| src/analyze_return.py | time difference·strip difference·mixed difference·sign change를 이미 계산했다 | 기존 저장 mixed difference를 새 실행·새 물리 성과로 보고하지 않는다 |

고정 science/test revision은 1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f, native owner는 f7830e2f55e7a1938bc3c98f61b60651f8dae474다. VigilODE a21d573980f66fe02891bd216153443b5352f921과 완성된 최적화 구현을 바꾸는 작업은 이 검토에 포함되지 않는다.

## 2. 기호와 정확하게 주장할 수 있는 분해

혼동을 피하려고 r은 strip 수, n은 transport 시간 분할 수 32 또는 64, N은 table node 수 512 또는 1024로 구분한다. 모든 온도와 온도차의 단위는 K다.

- T_(r,n)은 원래 table512 transport 실행에 저장된 온도다.
- θ_(r,N)^m은 같은 finite model/table의 방법 m∈{Radau,DOP853}에 저장된 reference 온도다.
- θ를 정확한 ODE 참해의 기호로 쓰지 않는다. 아래 식에서는 저장된 후보를 선택한 값이다.
- reference key는 검증된 source/binary/input/thread batch와 case의 m=8, angles=4, q=0, r, N, 실제 table SHA에 연결되어야 한다. 같은 r이라는 이유만으로 다른 table이나 다른 identity를 같은 변수로 합치면 안 된다.

같은 후보를 모든 등장 위치에서 공유하여

\[
e_{r,n}^{(m)} := T_{r,n}-\theta_{r,512}^{(m)}
\]

를 **기준해 후보를 조건으로 한 signed residual**로 정의한다. b와 a 두 strip 설정에 대해서는

\[
\begin{aligned}
\Delta T_n
&:=T_{b,n}-T_{a,n},\\
\Delta\theta^{(m)}
&:=\theta_{b,512}^{(m)}-\theta_{a,512}^{(m)},\\
\Delta T_n
&=\Delta\theta^{(m)}
  +e_{b,n}^{(m)}-e_{a,n}^{(m)}.
\end{aligned}
\]

마지막 식은 양변을 전개하면 θ_b와 θ_a의 계수가 각각 0이 되므로 성립한다. product 후보 선택처럼 각 key에 다른 방법을 허용할 때도, 동일 key의 모든 위치에서 같은 후보를 사용하면 그대로 성립한다. 세 항을 별개의 interval로 바꿔 더하면 그 공유 관계를 잃는다.

이 residual을 참 시간 오차라고 부르기 위해서는 별도의 기준해 정확성 정보가 필요하다. 해당 finite ODE의 참 온도를 y_r^*라고 쓰면

\[
e_{r,n}^{(m)}
=(T_{r,n}-y_r^*)-(\theta_{r,512}^{(m)}-y_r^*)
\]

이기 때문이다. Radau와 DOP853이 가까워도 두 번째 항의 절댓값이 그 method spread 이하라는 결론은 주어지지 않는다. 이번 결과에는 해당 항의 검증된 enclosure가 추가되지 않았다.

table 효과는 θ_(r,1024)^m−θ_(r,512)^m로 구분한다. 이는 두 finite table model 사이의 경험적 차이다. 원래 parent_comparisons가 N≠512를 제외한 계약을 유지하며, table1024 기준 후보를 원래 table512 transport의 같은 모델 시간 기준해로 취급하지 않는다.

기존 mixed difference

\[
(T_{b,64}-T_{a,64})-(T_{b,32}-T_{a,32})
\]

에서도 공통 reference 항은 대수적으로 상쇄된다. 이 관계를 설명하는 것은 표현 의존성의 확인이다. 이미 저장된 mixed difference 값의 재발견이나 새 native 측정이 아니다.

## 3. 같은 key의 계수를 먼저 합쳐야 하는 이유

유한 후보를 갖는 선형식을

\[
F(\theta)=c+\sum_{j=1}^{p} b_j\theta_{k(j)}
\]

로 받았다고 하자. 동일 reference key별로

\[
a_k=\sum_{j:\,k(j)=k} b_j
\]

를 정확히 계산한 후

\[
F(\theta)=c+\sum_{k:\,a_k\ne0}a_k\theta_k
\]

로 정규화한다. 여기서 상수 c와 계수도 정확한 유리수다. θ의 후보를 보고 계수의 작은 값을 임의의 허용치로 0 처리하지 않는다. 정확히 0인 계수만 제거한다.

예를 들어 θ∈{100,101}이면 (7−θ)+θ의 결과는 항상 7이다. 등장 위치마다 서로 다른 θ를 허용한 interval 계산은 [6,8]을 만들 수 있다. 그것은 원래 같은 변수를 공유한 식의 정확한 hull이 아니다. 이 예시의 수치는 합성 대수 예시다.

이 key 공유는 문자열이 우연히 같다는 사실만으로 성립하지 않는다. 동일 key에 서로 모순되는 candidate registry나 table identity를 붙이는 입력은 먼저 거부해야 한다. 계수 상쇄가 존재하더라도 잘못된 native provenance를 유효한 실행으로 바꿀 수 없다.

값이 없는 reference의 θ−θ=0은 형식적인 대수 항등식으로 확인할 수 있다. 그러나 그러한 **symbolic constant** 판정으로 native case가 완료되었다고 표시하면 안 된다. 실제 후보 집합의 admission, method coverage, case 완료 상태를 따로 유지해야 한다.

## 4. 두 종류의 finite-candidate hull

### 4.1 각 key의 방법을 따로 선택하는 product hull

활성 key마다 저장된 후보 집합 S_k가 유한하고 비어 있지 않다고 하자. 완성된 HE29 pair에서는

\[
S_k=\{\theta_k^{\mathrm{Radau}},
      \theta_k^{\mathrm{DOP853}}\}.
\]

같은 값을 두 방법이 반환하더라도 method label과 identity는 유지한다. 값 집합의 중복 제거는 방법 둘의 증거를 하나로 합친다는 뜻이 아니다.

허용되는 joint 선택은

\[
\Omega_{\mathrm{prod}}=\prod_k S_k
\]

다. 이는 서로 다른 key에서 다른 방법 label을 고를 수 있다는 집합 정의이며, 통계적 독립성이나 확률분포를 뜻하지 않는다.

l_k=min S_k, u_k=max S_k라 놓으면 최소와 최대는

\[
\begin{aligned}
L_{\mathrm{prod}}
&=c+\sum_{a_k>0}a_kl_k+\sum_{a_k<0}a_ku_k,\\
U_{\mathrm{prod}}
&=c+\sum_{a_k>0}a_ku_k+\sum_{a_k<0}a_kl_k.
\end{aligned}
\]

각 좌표에서 계수 부호에 맞는 endpoint가 최소·최대를 주며, Cartesian product에는 이 선택들을 동시에 만족하는 원소가 있다. 따라서 두 경계는 실제 허용된 후보 조합에서 달성된다. [L_prod,U_prod]는 F(Ω_prod)를 포함하는 가장 작은 닫힌 interval이다. 유한 결과 집합의 내부 빈 구간까지 실제 후보가 채운다는 뜻은 아니다.

이 공식은 조합을 모두 나열하지 않고 O(K)번의 scalar 곱·합으로 hull을 계산한다. 여기서 K는 활성 reference key 수이고 HE29에서는 최대 네 case다. Fraction 정수의 비트 길이에 따른 비용은 이 산술 연산 횟수와 별개다. 새로운 수치 solver나 고성능 선형대수 패키지가 필요한 계산이 아니다.

### 4.2 모든 key에서 같은 방법을 고르는 coherent hull

공통으로 사용 가능한 method label 집합을 M_common이라 하면

\[
\Omega_{\mathrm{coh}}
=\{(\theta_k^{m})_k:m\in M_{\mathrm{common}}\}.
\]

완성된 pair 전체에서는 보통 Radau와 DOP853 두 joint 후보가 있다. 각각의 선형식 값을 먼저 계산하여

\[
L_{\mathrm{coh}}=\min_{m\in M_{\mathrm{common}}}
 \left(c+\sum_k a_k\theta_k^m\right),\qquad
U_{\mathrm{coh}}=\max_{m\in M_{\mathrm{common}}}
 \left(c+\sum_k a_k\theta_k^m\right)
\]

를 얻는다. Ω_coh⊆Ω_prod이므로 coherent hull은 product hull에 포함된다. 두 hull이 같을 수도 있고 엄격히 작을 수도 있다.

합성 예시에서 θ_a의 두 방법 값이 (100,101), θ_b가 (110,111)이면 θ_b−θ_a의 product hull은 [9,11]이고 coherent hull은 [10,10]이다. 이 차이는 선택 집합의 차이다. 후자를 더 정확한 참해 오차상한이라고 해석하지 않는다.

공통 method가 없으면 coherent 집합은 비어 있다. 이때 [0,0]을 반환하지 않고 UNAVAILABLE로 표시해야 한다. 한 방법만 공통으로 남았다면 그 방법의 진단값만 있을 뿐, 두 방법 pair admission이 완료된 것은 아니다.

## 5. 저장 binary64를 정확히 다루는 계약

Python 공식 문서는 float에서 만든 Fraction이 해당 float의 정확한 값을 보존하며, 예를 들어 Fraction.from_float(0.3)이 십진 유리수 3/10과 다르다고 명시한다. 이 단위는 그 계약을 사용한다. [Python fractions 문서](https://docs.python.org/3.12/library/fractions.html)

핵심은 변환의 순서다.

\[
\operatorname{Fraction}(T_b)
-\operatorname{Fraction}(T_a)
\]

를 사용해야 한다. 먼저 binary64로 T_b−T_a를 계산하고 그 결과를 Fraction으로 바꾸면 중간 반올림이 이미 들어간다. 독립 검산은 1.0과 0.1의 예로 두 결과가 실제로 다름을 확인했다. Fraction("0.1")이나 limit_denominator()로 저장값을 보기 좋은 십진수로 바꾸는 처리도 이 정확성 계약과 다르다.

정확한 계수 합산과 hull 계산을 마칠 때까지 float로 돌아가지 않는다. 결과에는 exact numerator/denominator를 남긴다. 이는 저장 수치에 대한 정확한 산술이며 원래 solver의 내부 오차, 입력 table 오차, 측정 오차를 제거하는 연산이 아니다. JSON에서 정수·문자열·boolean을 허용하는지는 별도 입력 계약으로 정하고 boolean을 수치로 오인하지 않아야 한다.

### 최종 표시 경계만 바깥쪽으로 반올림

유한한 정확한 유리수 q를 binary64 f로 변환한 뒤 정확한 비교를 한다. 아래 down/up은 한 번의 nextafter다.

\[
\begin{aligned}
\operatorname{lo}(q)&=
\begin{cases}
\operatorname{nextafter}(f,-\infty),&\operatorname{Fraction}(f)>q,\\
f,&\text{그 외},
\end{cases}\\
\operatorname{hi}(q)&=
\begin{cases}
\operatorname{nextafter}(f,+\infty),&\operatorname{Fraction}(f)<q,\\
f,&\text{그 외}.
\end{cases}
\end{aligned}
\]

Python의 nextafter는 지정 방향의 다음 float를 반환한다. 이번 검산 환경은 CPython 3.12.14, radix2, mantissa53이었다. [Python math 문서](https://docs.python.org/3.12/library/math.html#math.nextafter)

L의 표시에는 lo(L), U의 표시에는 hi(U)를 사용한다. 매 연산이나 매 계수에 nextafter를 적용하지 않는다. 정확히 표현 가능한 값은 이동하지 않는다. 특히 정확한 0의 경계는 그대로 0이다.

**exact hull width와 display enclosure width는 구분한다.** 모든 변수 계수가 상쇄된 정확한 점은 exact width=0이다. 그 점 자체가 binary64로 표현되지 않으면 표시 경계는 인접한 두 float가 될 수 있다. 이는 후보 변화에 의한 폭이 아니다. 반대로 q=0이나 저장 binary64 하나는 동일한 float 경계 두 개로 표시할 수 있다.

정확한 유리수는 유한하지만 float 변환이 overflow할 수도 있다. 검토용 구현은 해당 표시를 FINITE_FLOAT_DISPLAY_UNAVAILABLE로 거부하고 exact 유리수를 보존한다. NaN·Infinity·잘못된 차원이나 비수치 입력을 수치 결과로 조용히 통과시키지 않는 별도 admission이 필요하다.

## 6. 부분 반환·timeout을 읽을 때의 판정 경계

원래 runner의 저장 순서를 고려하면 다음 구별이 필요하다.

| 관측 증거 | 허용되는 설명 | 아직 주장할 수 없는 것 |
|---|---|---|
| 두 method와 최종 identity/RESULT가 원래 gate를 모두 통과 | 완료된 pair를 새 signed 분석에 사용 | 참해 enclosure가 검증되었다는 주장 |
| Radau.json만 존재하고 최종 RESULT가 없음 | 한 방법의 저장 결과 또는 부분 반환 | DOP853 완료, pair 안정성, 전체 case 완료 |
| 명시적 timeout receipt와 method 일부가 있음 | timeout과 이미 저장된 method 증거를 동시에 표시 | 계산된 method를 NOT_RUN으로 지우거나, 미실행 방법을 0으로 채우는 처리 |
| 실패 receipt만 존재 | 기록된 실패 종류와 관측 시점을 표시 | 해당 실패가 특정 물리 모델의 보편적 불가능성을 증명한다는 주장 |
| 파일이 없거나 원격 진행 중인 프로세스를 관측하지 못함 | 현재 조회에서 자료 없음·미관측 | 숨은 프로세스까지 실행되지 않았다는 단정 |

선형식의 형식적 상쇄와 partial method 진단이 native admission을 대체하지 않는다. method별 wall time도 실제 저장 field가 있을 때만 수치로 쓰며, 누락된 시간은 0초가 아니다. 기존 완료 case를 재실행할 이유가 되는 분류 변경을 만들지 않는다.

## 7. 선행방법과 이번 적용의 구별

**SciSpace를 실제로 두 번 검색했다.** 첫 질의는 interval dependency와 반복 변수 보존을 물었으며 Krämer의 원 논문을 찾았다. 두 번째 질의는 Stolfi·de Figueiredo의 2003/2004 논문을 명시하여 2003 TEMA 논문과 DOI를 확인했다. Exa로 저자 출판목록과 원문을 찾고, 저자 IMPA PDF와 Wuppertal 대학 preprint를 실제 읽었다. 검색 질의와 선택한 메타데이터를 동반 JSON에 보존한다.

1. **J. Stolfi and L. H. de Figueiredo (2003), “An Introduction to Affine Arithmetic,” TEMA 4(3), 297–312.** DOI [10.5540/TEMA.2003.04.03.0297](https://doi.org/10.5540/TEMA.2003.04.03.0297). [저자 IMPA 원문](https://lhf.impa.br/ftp/papers/tema.pdf), [저자 출판목록](https://lhf.impa.br/publications.html). §3.2는 공유 noise symbol의 의존성, §3.3.1은 계수별 affine 연산과 상쇄, §3.3.2는 중간 반올림이 공유 관계에 미치는 영향을 설명한다.

2. **W. Krämer (2006), “Generalized Intervals and the Dependency Problem,” PAMM.** DOI [10.1002/PAMM.200610322](https://doi.org/10.1002/PAMM.200610322). [저자 소속 대학 preprint BUW-WRSWT 2006/4](http://www2.math.uni-wuppertal.de/~xsc/preprints/prep_06_4.pdf). 반복된 변수의 interval 대체가 정보를 잃는 현상과 generalized interval 표현을 다룬다. 이 모델을 HE29 코드에 구현했다고 주장하지 않는다.

2004 Numerical Algorithms 논문도 SciSpace·저자 목록에서 확인했다. 그러나 해당 웹 도구의 저널 PDF 클릭은 실패했으므로 본 검토의 핵심 원문 근거는 실제 읽은 위 두 문헌이다. SCAN2002 슬라이드와 2004 저널 논문을 같은 파일로 취급하지 않았다.

이번 코드는 일반 affine arithmetic의 새 발명이나 전체 구현이 아니다. 알려진 공유 변수 보존 원리를, 원래 HE29 admission을 통과한 **유한 개 저장 후보의 선형식**에 제한해 적용한다. 비선형 affine approximation, ODE truncation enclosure, 연속 noise model은 이번 단위의 범위 밖이다.

## 8. 새 독립 검산과 판독 완료 조건

evidence/THEORY_REVIEW.json에 표준 라이브러리만 쓰는 검산 소스와 최종 결과를 함께 보존했다. 원래 HE29 물리 모듈을 import하지 않았다. product hull은 계수 부호 공식으로 계산하고, 별도 oracle은 합치기 전 원래 항들을 같은 key의 동일 후보 할당으로 평가하여 가능한 조합을 열거했다.

새 고유 사례는 총 20개다.

- 반복 변수 상쇄, 전체 ΔT 분해의 상쇄, 계수 부호, 중복 계수, 값이 필요 없는 symbolic constant.
- product/coherent hull의 엄격한 포함과 일치, 공통 method 부재.
- 저장 binary64의 세 key 조합, 변환 순서에 따른 실제 차이.
- 정확한 0·저장 float·양음 유리수·subnormal 절반·최대 finite·비표현 점의 최종 경계.
- float 표시 overflow와 NaN/Infinity/boolean/string 입력 거부.

검산 중 oracle을 원래 미합산 항의 열거로 분리했고 동일 고유 사례의 최종 PASS를 receipt에 남겼다. 반복 확인을 새로운 고유 test 수로 합산하지 않았다. 이것은 이론식과 표시 규칙에 대한 합성 검산이며 root의 신규 분류기·분해 구현을 실행 검증한 것으로 보고하지 않는다.

root의 실제 구현 후속 검토에서는 다음 항목을 확인해야 한다.

1. 원래 admission의 재사용과 source/binary/table identity 연결.
2. signed 값의 원래 endpoint 출처 및 Fraction 변환 순서.
3. shared key별 정확한 계수 합산과 product/coherent 선택 집합의 명시.
4. exact width와 display width의 분리, 표시 overflow와 비유한 입력의 처리.
5. pair 완료·partial method·timeout·자료 부재의 독립된 상태 및 누락 시간 처리.
6. 기존 mixed difference가 새 수치 성과로 다시 집계되지 않는지 여부.

연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 범위 검증 전까지 HOLD를 유지한다.
