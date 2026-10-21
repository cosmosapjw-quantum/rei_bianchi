# v9 — 실제 age32 반환, 출생 사건의 보존량 분해, source exposure 해상도

연구 단위 `NATIVE_AGE32_ANALYSIS_20261020_V9`. 이번 입력의 Git 기준은 `93aca4cc483080b802fa85c9c44e43b9c85db5b7`이며 그 부모는 v8 배송 `5ef6766c66b319e48612f316ac1581bd12f6ebfc`다. 기존 v8 source `02767dc5e6c4b47883f590834aee38530852568d`의 고정 모형 유도·612 Decimal 조건·1044 float parity·10 Rust fixtures와 native age64를 재사용한다.

## 1. 현재 질문과 근거 상태

새 native age32가 동일 B1 binary·computational solver base에서 완료됐다. 18개 공통 관측 시각에서 비교할 수 있고 endpoint 상대차는 N 약0.824886, U 약0.791606이다. 기존0.005 finite-neighbor target은 충족되지 않는다. 이번 과제는 저장된 출생32개의 전후 관측을 이용해 photon residual의 발생 위치를 분해하고, survivor의 실제 age 분포를 분석하며, 양성 scalar source 문제에서 출생 간격과 흡수시간의 관계를 정확히 유도·구현하는 것이다.

상태는 다음처럼 나눈다. 저장 binary64 항의 항등식은 **derived + implementation-verified**, native32/64 차이·분포는 **numerically checked**, constant-source scalar 결과는 명시한 가정에서 **derived**다. 원 nonlinear Grackle response bound는 **NOT_ESTABLISHED**, native age/time convergence는 **HOLD**, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`다. 이 상태는 문서 전체에 공통 적용한다.

광자 수는 photons/H, 누적 photoevent는 events/H, source inventory는 photons/H, 시간은 s, energy는 eV/H다. 시간 관련 식에는 proper time을 쓰며 native의 독립변수 log(a)와 구별한다. 여기서는 자연단위를 도입하지 않는다. 흡수율 lambda는 c n_s sigma_s의 합 [s^-1]을 포함하므로 source exposure lambda*h가 무차원이다.

## 2. 저장된 impulsive history의 정확한 photon 분해

출생 사건 j=0,...,B-1, 각 사건의 주입 광자 수를 S_j라 한다. N은 survivor number, A_s는 세 종의 누적 photoevent다. 출생 전후의 저장 항으로

\[
I_j^- = N_j^-+\sum_s A_{s,j}^- -\sum_{k<j}S_k,
\qquad
I_j^+ = N_j^++\sum_s A_{s,j}^+ -\sum_{k\le j}S_k
\]

를 정의한다. 계산에서는 각각의 binary64를 정확한 dyadic Fraction으로 바꾼 뒤 더하고 뺀다. Decimal 표시 정밀도는 이 항등식의 판정에 관여하지 않는다.

출생 순간의 변화는

\[
J_j=I_j^+-I_j^-
=N_j^+-N_j^-+\sum_s(A_{s,j}^+-A_{s,j}^-)-S_j.
\]

출생 사이의 변화는

\[
H_0=I_0^- -I_{\rm init},\qquad
H_j=I_j^- -I_{j-1}^+\quad(1\le j<B),\qquad
H_B=I_{\rm end}-I_{B-1}^+.
\]

중간 I의 항들이 한 번씩 상쇄되므로

\[
\boxed{I_{\rm end}-I_{\rm init}=\sum_{j=0}^{B}H_j+\sum_{j=0}^{B-1}J_j.}
\]

이는 정확한 저장 이력에 대한 유한 합 항등식이다. native 실행 source가 초기 y를0으로 만들고 gas 네 좌표만 대입한 사실을 실제 executed-source SHA와 연결한다. 그 결과 이 고정 입력의 초기 photon·photo counters는0이고 I_init=0이다. 다른 초기조건에는 임의로0을 대입하지 않는다.

기존 interval dump는 source 직전 상태다. 이제 실제 `source_jumps.json`의 pre/post를 연결하면 J와 H를 따로 계산할 수 있다. pre의 N·photo counters는 각 interval N와 `accepted_coordinates_eventj.npy`의 ledger 좌표에 대조한다. 마지막 interval과 endpoint도 대조한다. missing/duplicate/clock/source/active-count mismatch는 해당 분해를 INCOMPLETE 또는 INVALID로 남긴다.

독립 raw 계산에서 B=32, sum J=1.2770322873736215e-20, sum |J|=3.295557192216733e-20, sum H=1.6596175588774037e-14, I_end=1.659618835909691e-14였다. Exact telescope residual은0이다. 모든 출생 J가 정확히0은 아니지만 gas·nonbirth·ledger coordinate bits는 보존됐다. 이 데이터에서 endpoint residual을 출생 때의 저장 합 변화만으로 설명할 수 없다는 것은 위 수치 분해의 직접 귀결이다.

H에는 interval integration, RHS·reconstruction 연산, 출력 변환 등의 누적 영향이 들어간다. H를 순수 truncation error나 전체 floating-point roundoff bound로 분류하려면 별도 근거가 필요하다. 이 분해는 기존1e-8 보존 gate나 rtol/atol을 변경하지 않는다.

두 실행 a,b에 대해서도 같은 정의를 빼면

\[
\boxed{\Delta N=\Delta S-\sum_s\Delta A_s+\Delta I.}
\]

각 source를 따로 저장한 exact 합으로 이 관계를 검증한다. 이 결과는 저장된 endpoint 차이의 수지이며, absorbed response 자체의 continuum 정확도 추정은 별도다.

## 3. 실제 age 분포와 v8의 대응 조건

native cohort의 birth time b_i와 endpoint proper time T, 저장 number N_i에 대해 a_i=T-b_i, N=sum N_i이고

\[
\mu_N={\sum_i N_i a_i\over N},\qquad
\sigma^2_{a,N}={\sum_iN_i(a_i-\mu_N)^2\over N}.
\]

U_i로 같은 식을 쓰면 energy-weighted age다. 분모가0이면 평균·분산은 정의되지 않는다. 분산은 두 큰 raw moment의 차 대신 centered sum으로 계산한다. birth의 마지막1/2/4개에 속하는 N/U fraction과 가중 age quantile도 계산한다. 이는 finite saved cohorts의 통계로서 outward native certificate를 발행하지 않는다.

실제 마지막 cohort의 N fraction은 age32 약0.993397, age64 약0.982078이며 U fraction은 약0.991188, 0.975978이다. 현재 endpoint survivor는 최근 source에 집중되어 있다. 따라서 출생 간격을 바꿀 때 최근 cohort의 age가 달라지는 효과를 별도로 검토할 가치가 있다.

v8 모형과 native의 대응에는 다음 세 차이가 있다.

1. v8는 native64의 source templates를 고정하고32/16/8 clock으로 묶는다. native32는32 midpoint마다 source를 새로 계산한다. proper-time clock32 배열은 일치하지만 source weights는 pairwise64 합과 동일하지 않다.
2. v8의 hazard와 node energy는 age64 endpoint gas·geometry에서 고정한다. native는 진화하는 gas·geometry를 사용한다.
3. v8 node는 각 template를 endpoint에서 재구성한 quadrature node다. native는 RHS에서 현재 two-moment spectrum을 다시 재구성하므로 이 node 번호는 시간 전체의 영속적인 photon label이 아니다. endpoint에서 threshold 아래로 간 passive node를 native 경로 전체의 passive population으로 동일시하지 않는다.

예를 들어 v8 passive number 약1.2963861e-7은 native64 total survivor 약1.2909104e-9보다 크다. Native N에 v8 all-population 값을 직접 붙이면 서로 다른 관측량을 비교하게 된다. V8 sensitive32−64와 native32−64의 delta가 수치적으로 가까운 사실은 별도 empirical diagnostic으로 보존한다. 이 비교의 정확한 model gap은 source weight, time-varying opacity/energy, reconstruction의 세 항이다.

고정 export의4096 passive node는 endpoint energy13.5735745664–13.5999957808eV이며 원 transport의 HI fit threshold13.60eV 아래에 있다. q=0 redshift 관계에서 같은 spectral coordinate를 birth로 옮긴 E_birth=E_T exp(x_T-x_birth)는13.6000042192–13.6264779236eV로 계산된다. 이는 이 고정 source coordinate가 threshold를 지나가는 구체적인 진단이다. Native 재구성 node의 persistent path를 추적했다는 주장은 추가하지 않는다. 이 provider의 fit thresholds=[13.60,24.59,54.42]eV와 gas binding energies=[13.598434599702,24.587389011,54.41776]eV는 역할이 다르며 기존 계약을 유지한다.

## 4. Constant-source scalar 모델의 midpoint birth 오차

가정을 고정한다. dn/dt=q-lambda*n, q>=0와 lambda>=0는 상수, n(0)=0, T=m*h, m은 양의 정수다. 각 panel의 source량 q*h를 midpoint (j+1/2)h에서 순간 주입한 뒤 같은 정확한 absorption propagator를 사용한다. 연속 source의 정확한 해는 lambda>0에서

\[
n_*(T)={q\over\lambda}(1-e^{-\lambda T}).
\]

중점 source 표현의 해는 유한 geometric sum으로

\[
n_h(T)=qh\sum_{j=0}^{m-1}e^{-\lambda[T-(j+1/2)h]}
=qh\,e^{-x/2}{1-e^{-mx}\over1-e^{-x}},\qquad x=\lambda h.
\]

따라서 q>0, T>0에서

\[
R(x)={n_h\over n_*}={xe^{-x/2}\over1-e^{-x}}={x\over2\sinh(x/2)},
\qquad R(0)=1.
\]

같은 source law와 endpoint에서 h를 절반으로 줄이면

\[
{n_h\over n_{h/2}}={R(x)\over R(x/2)}=\operatorname{sech}(x/4).
\]

R은 x>0에서 엄밀히 감소한다. y=x/2라 놓으면 d log R/dx=1/x-(1/2)coth(x/2)<0이다. tanh y<y는 [y-tanh y]'=tanh^2 y>0 및0에서의 값으로 증명되므로 부호가 정해진다. R(0)=1, R(infinity)=0에서 epsilon in(0,1)에 대한 continuum exposure root는 유일하다.

작은 x 전개는

\[
1-R(x)={x^2\over24}-{7x^4\over5760}+{31x^6\over967680}+O(x^8),
\]

\[
1-\operatorname{sech}(x/4)={x^2\over32}-{5x^4\over6144}+{61x^6\over2949120}+O(x^8).
\]

즉 finite-neighbor와 continuum의 오차 정의가 서로 다르다. 같은 epsilon에 대해 neighbor condition은

\[
x\le4\operatorname{arcosh}{1\over1-\epsilon},
\]

continuum condition은 R(x)>=1-epsilon이다. epsilon=.005에서 각각 x<=0.400836030749612...와 x<=0.34701818109945...다. 첫 경계에서 coarse continuum error는 약0.00666332, fine continuum error는 약0.00167168이다. 원 native0.005 기준은 그대로 두고, 이 scalar 예제에서는 서로 다른 두 판정을 별도 출력한다.

큰 x에서 최근 midpoint birth가 endpoint로부터 h/2만큼 떨어져 있어 e^-x/2 suppression이 남는 반면, 연속 source에는 endpoint 바로 전의 photon도 포함된다. 이 정확한 구조가 stiff source quadrature의 판별 예제다. Native log(a) grid, 가변 opacity, heterogeneous spectrum에 하나의 aggregate effective x를 적용하여 native continuum 오차를 예측하지 않는다.

## 5. 양성 exponential source step과 계산식

고정 source·고정 absorption에서 임의의 n0>=0에 대해

\[
n_1=n_0e^{-x}+qh\varphi_1(-x),\qquad
\varphi_1(-x)={1-e^{-x}\over x},\quad\varphi_1(0)=1.
\]

동일 panel의 absorbed number는

\[
A=n_0(1-e^{-x})+qh[1-\varphi_1(-x)]\ge0,
\qquad n_1+A=n_0+qh.
\]

이 식은 source contribution을 panel 안에서 정확히 적분한 것이다. Phi1 표현은 Hochbruck–Ostermann(2010), *Acta Numerica*19,209–286, DOI10.1017/S0962492910000048의 식(1.5)–(1.6)을 scalar constant-source 문제에 특수화한 표준 결과다. 원문: https://na.math.kit.edu/download/papers/acta-final.pdf . 이 연구에서는 source-age 해상도 진단·안정적인 구현과 native 반환의 해석에 사용한다.

계산에서1-exp(-x)는 -expm1(-x)로 처리한다. 작은 x의1-phi1(-x)와1-R(x)는 각각의 급수를 사용하여 상쇄를 줄인다. 큰 x에서는 sinh 또는 exp(+x)를 직접 만들지 않는다. Lambda=0이면 n1=n0+qh, A=0이며 q=0이면 순수 흡수, h=0이면 항등 사상이다. 이 primitive는 원 native B1이나 source schedule에 자동 삽입하지 않는다.

## 6. 더 일반적인 source panel에서의 조건부 exposure 경계

시간가변 prescribed lambda(t)>=0, lambda in L1([0,T])와 양성 source q(s)>=0를 둔다. Panel B_j=[l_j,r_j]는[0,T] 안의 유한 구간이며 q in L1(B_j), b_j in B_j다. K_T(s)=exp[-integral_s^T lambda]와 유한 source량 W_j=integral_Bj q(s)ds를 정의한다. B_j의 source량을 b_j로 옮기고 유한한 D_j>=0에 대해 모든 s in B_j에서 |integral_bj^s lambda|<=D_j가 확보되었다면

\[
W_jK_T(b_j)e^{-D_j}\le\int_{B_j}q(s)K_T(s)\,ds
\le W_jK_T(b_j)e^{D_j}.
\]

증명은 K_T(s)/K_T(b_j)=exp[integral_bj^s lambda]의 양의 범위를 q(s)로 적분하는 것이다. 따라서 panel source를 바꾸지 않는 conditional enclosure가 생긴다. 다수 label에서도 양의 합을 취할 수 있다. Native 적용에는 실제 경로를 덮는 exposure D_j와 source/reconstruction 대응이 입력으로 필요하다. 저장 endpoint 하나나 두 시점의 hazard만으로 전체 path supremum이 확보되었다고 간주하지 않는다.

이 식은 열린 nonlinear response 과제의 다음 구현 입력을 특정한다. Rate-defect와 invariant-box 도구의 기존 별도 repo 결과는 해당 조건을 제공하는 후보로만 연결하며, manufactured grid의 상한을 native Grackle 상한으로 옮기지 않는다.

## 7. 검증·판정·다음 의무

독립 연구자는 원 진단 함수를 import하지 않고 raw Fraction telescoping, 모든33 interval의N/photo 저장값, native32/64 source·clock·population 대응을 계산했다. Wolfram은 scalar ratio와 source ledger 잔차0 및 급수를 확인했다. 단조성 계산의 CAS 출력은 x*coth(x/2)>2로 남았으며 위 tanh 보조정리가 그 조건을 닫는다. Root 값은 새로운 구현의 Decimal100 제어 예제로 검사한다.

새 구현은 실제 native raw의 postprocess와 scalar fixtures만 실행한다. 기존v8 전체 study, Decimal campaign, v7 benchmark, native32/64 trajectory를 재실행하지 않는다. PNG는 저장한 분석 JSON에서 생성한다. 실제 command/exit/wall, targeted finding과 closure는 results/reviews에 연결한다. Strong no-go를 새 성과로 채택하지 않으므로 NG1–NG7 no-go admission은 적용하지 않는다. 여기의 부정 결과는 원0.005 finite-neighbor target의 실제 미충족과 위 정확한 조건부 수학의 범위다.

다음 native 실행이 필요하면 새 workload의 질문·source law·representation·runtime cost를 이 결과에서 지정해야 한다. 이미 완료된 age32를 다시 READY로 남기지 않는다. 즉시 수행할 수 있는 저장 자료 분석은 이번 단위에서 닫고, 실제 nonlinear tube와 native time의 representation 의무는 별도 열린 상태로 유지한다.
