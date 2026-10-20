# 관측량별 source-age 경계와 정규화된 survivor age

연구 단위: `OBSERVABLE_CERTIFICATES_20261020_V8`. 기준 PR199 HEAD: `cf00684741eb612e35f987713c28937513d44d57`.

## 1. 질문과 고정한 모형

기존 `vigilode_age_transport_20261019/THEORY_KO.md` §4, §7에서 유도한 energy·species event·age moment 경계를 실제 outward 수치로 평가한다. 평균 age에서는 분모와 분자의 상관관계를 보존하는 centered identity를 추가한다. 고정 입력의 57,344 labels, 원 source packet 64개, clocks 8/16/32/64를 재사용한다. 새 native trajectory나 새 물리 설정은 요구하지 않는다.

각 label의 비음수 weight `w_i` [photons/H], energy `E_i` [eV], species hazard `lambda_i,s` [s^-1]는 같은 값을 쓴다. 내보낸 binary64 값은 정확한 dyadic 실수다. `Lambda_i=sum_s lambda_i,s`는 정확한 합이며, age `a_Xi=T-b_Xi>=0`도 입력 binary64 값의 정확한 실수 차다. `s`는 HI, HeI, HeII다. 양성 선형 해와 누적 흡수량은

\[
n_{Xi}=w_i e^{-\Lambda_i a_{Xi}},\qquad
A_{Xi,s}=w_i p_{i,s}(1-e^{-\Lambda_i a_{Xi}}),
\quad p_{i,s}=\lambda_{i,s}/\Lambda_i.
\]

`Lambda_i=0`인 passive label에서는 `n_Xi=w_i`, `A_Xi,s=0`으로 정의한다. 관측량은 `N=sum n`, `U=sum E n`, `M1=sum a n`, `M2=sum a^2 n`, `A_s=sum A_i,s`다. 단위는 차례로 photons/H, eV/H, photon·s/H, photon·s²/H, events/H다. `mu=M1/N`의 단위는 s이며 `N>0`일 때 정의한다.

Population은 전체, `Lambda>0`인 sensitive 부분, `Lambda=0`인 passive 부분으로 나눈다. 각 부분의 평균은 자기 survivor mass로 정규화한다. 전체 분모로 sensitive 평균을 정의하지 않는다.

## 2. 두 age 사이의 안정적인 signed identity

한 label에서 `a=min(a_A,a_B)`, `delta=|a_A-a_B|`, `u=exp(-Lambda a)`, `v=exp(-Lambda delta)`, `h=1-v`라 두자. 먼저 older-minus-younger 차이를 쓰면

\[
\begin{aligned}
k_0&=-wu h,\\
k_1&=wu[\delta v-a h],\\
k_2&=wu[\delta(2a+\delta)v-a^2h],\\
k_c&=wu[\delta v-(a-c)h].
\end{aligned}
\]

각각 `n`, `a n`, `a² n`, `(a-c)n`의 차다. 예를 들어 `(a+delta)v-a=delta v-a(1-v)`를 곱하면 두 번째 식을 얻는다. 세 번째 식은 `(a+delta)^2-a^2=delta(2a+delta)`를 사용한다. A가 older이면 이 부호를 쓰고, B가 older이면 반대 부호를 쓴다. 같은 birth의 차이는 정확히 0이다.

이 식은 큰 두 moment를 각각 계산한 뒤 빼는 경로와 대수적으로 같다. 수치 구현은 공통 생존 인자 `u`를 먼저 분리해 interval 의존성에 따른 폭을 줄인다. `k1`, `k2`, `kc`는 음수가 될 수 있으므로 비음수 전용 multiplication/clamp로 계산하지 않는다.

Passive label의 식은 정확히 `k0=0`, `k1=w delta`, `k2=w delta(2a+delta)`, `kc=w delta`다. 이 경우 `N`의 변화가 0이어도 age moment는 변할 수 있다. 이 식을 직접 평가하면 수치적 `1-exp(0)`에서 불필요한 폭이 생기지 않는다.

Energy와 종별 event의 차이는

\[
\Delta U_i=E_i\Delta n_i,\qquad
\Delta A_{i,s}=-p_{i,s}\Delta n_i.
\]

흡수와 생존의 energy ledger에는 동일한 `E_i`를 사용한다. 따로 반올림된 threshold와 excess energy를 더해 원 `E_i`와 동일하다고 가정하지 않는다.

## 3. label별 절댓값 합과 전체 signed 차이

`L_r=sum_i |Delta(a^r n)_i|`, `r=0,1,2`라 정의한다. `L_U=sum E_i |Delta n_i|`, `L_As=sum p_i,s |Delta n_i|`이다. 삼각부등식으로

\[
|\Delta N|\le L_0,\quad |\Delta U|\le L_U,\quad
|\Delta M_r|\le L_r,\quad |\Delta A_s|\le L_{A_s}.
\]

정확한 실수에서 `sum_s L_As=L0`가 성립한다. Passive label은 양쪽 모두 0이고 sensitive label은 `sum_s p_i,s=1`이기 때문이다. 각 항의 outward 상한을 독립적으로 더한 수치 결과의 endpoint까지 같은 비트여야 한다는 조건은 요구하지 않는다.

Signed 총차이와 `L_r`는 별도로 보고한다. 전자는 label 사이의 상쇄를 보존하고, 후자는 각 label의 변화 크기를 합한다. 각자의 실제 모형값을 포함하는 두 독립 interval은 endpoint 포함관계나 대소관계를 강제할 이유가 없다.

이전 이론의 전역 fallback도 유지한다. `C=sum w_i delta_i`, 모든 age를 덮는 `Amax`에 대해

\[
|\Delta M_1|\le C,\qquad
|\Delta M_2|\le 2A_{\max}C.
\]

증명은 `|(a e^-Lambda a)'|=|1-Lambda a|e^-Lambda a<=1` 및 `|(a² e^-Lambda a)'|=a|2-Lambda a|e^-Lambda a<=2Amax`와 평균값 정리다. `x>=0`에서 첫 절댓값 함수는 0에서 최대 1이고, 두 번째의 `|2-x|e^-x`는 2 이하이다. 두 유효한 상한의 최솟값도 유효한 상한이다.

## 4. 평균 age의 centered certificate

두 population의 survivor mass가 양수라고 하자. 임의의 고정 실수 `c`에 대해

\[
\mu_A-\mu_B=
\frac{\Delta M_1-c\Delta N+(c-\mu_B)\Delta N}{N_A}.
\]

`B(c)=sum_i |Delta(a n)_i-c Delta n_i|`라 놓으면 `kc`를 사용해 계산할 수 있다. `mu_B`를 포함하는 interval `I_B`, 양의 하한 `N_A,lo`, `E0>=|Delta N|`가 있으면

\[
|\mu_A-\mu_B|
\le \frac{B(c)+r_B(c)E_0}{N_{A,\mathrm{lo}}},\qquad
r_B(c)=\max_{x\in I_B}|c-x|.
\]

증명: 분자 첫 항의 절댓값은 `B(c)` 이하이고, 두 번째는 `r_B E0` 이하이다. 양의 분모를 아래에서 제한하면 부등식 방향이 보존된다. 코드에서는 `c`를 `I_B`의 유한 binary64 midpoint로 선택하고 `r_B`를 위쪽 반올림한다. `E0`에는 stable signed 총 `Delta N` interval의 절댓값 상한을 쓸 수 있다. 이 값은 label 절댓값 합보다 작을 수 있어 정규화 교정항의 상쇄를 보존한다.

A와 B를 바꾸어 얻는 상한도 계산한다. 기존

\[
\frac{C+A_{\max}L_0}{\min(N_{A,\mathrm{lo}},N_{B,\mathrm{lo}})}
\]

과 두 centered 상한의 최소를 최종 인증 상한으로 쓴다. 이것은 주어진 세 후보 중 선택이며 모든 center에 대한 최적화 주장이 아니다. 분모 interval의 하한이 0 이하이면 유한한 정규화 인증을 발행하지 않고 `UNRESOLVED_NONPOSITIVE_DENOMINATOR`를 반환한다. 실제 exact mass가 양수더라도 현재 interval이 이를 분리하지 못할 수 있다.

정확한 `mu_B`를 center로 쓸 수 있다면 첫 방향의 교정항은 사라진다. 그러나 일반적으로 그 실수를 finite float로 정확하게 저장할 수 없으므로 midpoint residual을 빼먹지 않는다. `N=0`인 부분집합의 평균도 임의로 0으로 정의하지 않는다.

## 5. 외부 근거의 실제 재사용

Catalano, Lijoi, Prünster (2020), *Approximation of Bayesian models for time-to-event data*, Electronic Journal of Statistics 14, 3366–3395, DOI `10.1214/20-EJS1746`의 Theorem 9와 §6.7 식(30)을 실제 읽었다. 그 논문의 exponential identity

\[
|e^{-x}-e^{-y}|=e^{-\min(x,y)}(1-e^{-|x-y|})
\]

에 `x=Lambda(a+delta)`, `y=Lambda a`를 대입하고 `w_i`를 곱하면 여기의 `-k0`를 얻는다. 유한 label에 직접 적용하면, `M=sum w_i>0`일 때 Jensen 부등식에서

\[
L_0\le\sum_i w_i(1-e^{-\Lambda_i\delta_i})
\le M\left[1-\exp\left(-\frac{\sum_iw_i\Lambda_i\delta_i}{M}\right)\right]
\le\sum_iw_i\Lambda_i\delta_i
\]

를 얻는다. 이 부등식은 광학깊이 변화에 가중한 finite-label adaptation이다. Age marginal의 W1만으로 opacity 상관관계를 제거하는 명제가 아니다. 이번 구현의 채택 경계는 더 직접적인 `L0`, weighted bounds, centered moment 식이며 Jensen 상한의 별도 실행 완료를 주장하지 않는다.

Habeck, Rudolf, Sprungk (2020), *Stability of doubly-intractable distributions*, `arXiv:2004.07310`은 정규화 전후의 measure perturbation을 구분하는 관련 문헌으로 읽었다. 위 centered 식의 증명은 이 문서에서 직접 제시한다. 기존 문헌의 정리나 단순 대수식을 새 일반 정리로 주장하지 않는다. 이번 기여는 REI의 실제 고정 입력에 대해 관측량과 population별 경계를 안정적인 연산으로 연결하고 outward 결과를 평가한 것이다.

실제 재사용 코드는 원 VigilODE `directed.rs`, 검증된 `certified.rs`의 S18/S19 exponential enclosure, v7의 deterministic Rayon preload 패턴과 22 locked dependencies다. 원 upstream source와 완료된 benchmark는 변경하지 않는다.

## 6. 검증 계약과 이론·실행의 구분

Wolfram의 실제 evaluator에서 `k0/k1/k2/kc` 및 centered normalization 항등식의 잔차가 모두 0이고 passive `kc=w delta`임을 확인했다. 이 일반 유도와 별도로 새 Rust 구현은 경계 fixture와 실제 CSV 전체를 사용해 검사한다.

독립 Python 검산은 높은 정밀도의 Decimal에서 두 endpoint exponential과 moment를 직접 계산한다. Rust의 stable factorization을 복제하지 않는다. Binary64 입력을 먼저 정확히 해석하고 Decimal 비교값을 binary64로 축소하기 전에 enclosure 포함과 bound를 검사한다. Underflow cutoff의 해석, 종 합과 number/energy ledger, passive의 비영 moment, 두 부호 방향, stationary moment cancellation, 빈 population과 분모 조건을 검증한다.

기존 exponent 증명·vendor·native export·NCP 완료 결과는 입력과 source identity가 유지되므로 재사용한다. 새 검증 결과와 command/exit/wall/CPU는 `results/`에 기록한다. 새 연구의 실행 여부는 해당 receipt로 판정하며 과거 benchmark 실행을 신규 성과에 합산하지 않는다.

## 7. 범위와 다음 연구

이 모든 경계는 동일 source label과 고정 gas·geometry·내보낸 opacity를 갖는 모형에 성립한다. 실제 nonlinear gas 흐름에는 시간에 따른 opacity와 재구성 오차의 의존성이 남는다. Native age32 reference의 수치 결과는 별도 NCP 실행에서 얻어야 하며 기존 native age/time HOLD를 이 결과로 바꾸지 않는다.

연구 전 최신 GitHub·Drive·Dropbox intake에서 새 native age32 완료 근거는 발견되지 않았다. 다른 lane의 RUN19/LRS/HE29 가속과 VigilODE PR76 완료 결과는 별도 상태로 채택했다. 다른 대화 검색은 실제 오류를 반환했으므로 모든 대화를 읽었다고 보고하지 않는다.

현재 요청의 연구·코딩·게시·백업 범위를 따라 R1–R10/C1–C10을 진행한다. 첨부 구버전 protocol의 단일단계 종료·일괄 formalization 금지는 현재 스킬의 근거 재사용·요청 완결 규칙에 맞게 적용한다. 수학 검토, 구현 독립 검토, 직접 읽는 결과 plot은 유지한다. 원 rtol/atol·native source schedule·1e-8 gates·NCP cap은 변하지 않는다.

`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
