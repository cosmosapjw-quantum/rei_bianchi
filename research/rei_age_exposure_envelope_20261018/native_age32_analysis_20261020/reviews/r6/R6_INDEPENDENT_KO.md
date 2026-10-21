# Native age32 반환 이후 독립 이론 검토

검토자는 구현 담당과 별개다. 이 기록은 새 native 적분을 수행하지 않고, 완료된 age32/age64 raw와 v8 source·출력을 읽어 독립 `Fraction` 산술 및 닫힌 scalar 해를 검토했다. 분석 스크립트는 기존 diagnosis module을 import하지 않는다.

## 1. 저장 photon residual의 정확한 event/interval 분해

Proper-time photon number의 단위는 photons/H다. Source inventory의 j번째 number를 S_j, 누적 photoevent를 P=sum_{s=HI,HeI,HeII} P_s라 하자. 저장 binary64는 정확한 dyadic 수로 해석한다. j번째 birth 직전·직후에

    C_j^- = N_j^- + P_j^- - sum_{k<j} S_k,
    C_j^+ = N_j^+ + P_j^+ - sum_{k<=j} S_k,
    J_j = C_j^+ - C_j^-.

초기 residual C_init=0이고, m births 사이의 저장 interval 변화는

    H_0=C_0^- - C_init,
    H_j=C_j^- - C_{j-1}^+  (1<=j<m),
    H_m=C_end-C_{m-1}^+.

따라서 중간 C 항의 소거로

    C_end = C_init + sum_j J_j + sum_{j=0}^m H_j

가 정확히 성립한다. 이 등식은 연속 미분방정식이나 solver 정확도를 전제로 하지 않으며, 저장된 항의 정확한 분해다. `source_jumps.json`의 각 pre N과 photo-ledger3개가 `solver_return.intervals[j]` 및 `accepted_coordinates_eventj.npy`의 같은 항과 일치하는지 별도로 확인했다. 최종 event32도 endpoint와 일치했다. 총33개 연결 모두 정확히 일치했다.

실제32birth 결과:

| 항 | 값 [photons/H] |
|---|---:|
| C_end | 1.659618835909691e-14 |
| sum J_j | 1.2770322873736215e-20 |
| sum abs(J_j) | 3.295557192216733e-20 |
| sum H_j | 1.6596175588774037e-14 |
| sum abs(H_j) | 1.6596175588774037e-14 |
| 저장 `photon_residual` − C_end | -7.549263860465207e-21 |

모든 H_j는 비음수였고 exact telescoping 잔차는0이다. C_end/sum(abs(J_j))=503592.7884453919다. 따라서 이 저장 자료에서는 source insertion 변화와 마지막 scalar 산술 차이가 endpoint residual의 주성분이 아니다. 주요 저장 변화는 birth 사이 interval에서 발생했다.

여기서 H는 적분된 ledgers, positive-coordinate decode, reconstruction과 physical number의 평가·합산을 함께 포함한다. H를 truncation error 또는 simulation roundoff 중 하나로 확정하지 않는다. 이를 분리하려면 accepted-step continuous residual과 physical reconstruction의 오차 enclosure가 추가로 필요하다. 원 photon gate1e-8는 변경하지 않는다.

`EXACT_TELESCOPING.json`에 모든 정확한 유리수,32jump,33interval, 연결 검사를 남겼다. `analyze_raw.py`가 재현 코드다.

## 2. v8 fixed node 모형과 실제 native32/64의 대응

### 유지되는 입력과 달라지는 입력

v8 `prepare_export.py`는 원 age64의64birth templates를 native64 endpoint geometry와 gas에 놓고 prepared node57,344개를 내보낸다. 같은 weight·energy·hazard를 유지한 채 birth clock만8/16/32/64로 묶는다. Native32는 source function을32개의 log(a) midpoint에서 새로 평가하고, 각 width/32/H(x)로 source packet을 만든다.

v8 clock32 proper-time 배열은 native32 `birth_times_s`와 정확히 같다. Native32의 source inventory는64의 연속 두 packet을 단순 합한 것과32개 모두 다르다. 총 source number는 각각

    S32 = 7.295271879161836e-5,
    S64 = 7.295271896418983e-5,
    S32-S64 = -1.7257147278937595e-13 photons/H.

짝별 source-number 상대 차이의 최대값은2.365529664960113e-9이다. 이 작은 총량 차이만으로 spectral shape 차이까지 제한할 수는 없다. 같은 native function/binary는 확인되지만, fixed label measure가 동일하다는 전제와 구분해야 한다.

Native는 각 RHS에서 현재 normalized two-moment state를 `prepare`한다. q/node weights가 재구성되고 geometry/gas가 변한다. 따라서 v8 export node의 `(cohort,cell,node)`는 해당 고정 모형의 label이며 원 native 전체 진화에서 유지되는 독립 입자 identity를 뜻하지 않는다.

### Passive의 의미

v8의4,096passive nodes는 endpoint에서 세 hazard가 모두0인 node다. 총mass는1.2963861367952044e-7 photons/H로 native64 endpoint 전체N의100.4241726198443배다. Endpoint energy 범위는13.5735745664..13.59999578083eV다. 원 transport의 FIT_THRESHOLDS_EV는[13.60,24.59,54.42]이며 gas binding_ev[13.598434599702,24.587389011,54.41776]와 다르다. 두 기존 계약을 바꾸지 않는다.

q=0인 현재 geometry의 redshift E_b=E_T exp(x_T-x_b)를 같은 fixed exported q에 적용하면 passive로 분류된 모든4,096node의 birth energy는13.6000042192..13.6264779236eV로13.60eV 위다. 따라서 terminal frozen hazard=0은 전체 경로 hazard=0을 함의하지 않는다. 이 비교는 원 native를 다시 적분하지 않은 kinematic mapping이다.

### 실제 finite difference와 수치적 연관

Native endpoint32−64의 상대 차이는 N82.4886121142%, U79.1605953540%다. Native 마지막 cohort가 endpoint의 대부분을 차지한다.

| endpoint 기여 | age32 | age64 |
|---|---:|---:|
| 마지막 cohort N/전체N |0.9933973814166516|0.9820776025622571|
| 마지막 cohort U/전체U |0.991188198189693|0.9759776575158278|

v8 sensitive 부분의 차이는 native difference와 가깝다.

| 관측량 | native32−64 | v8 sensitive32−64 | 차이의 상대 mismatch |
|---|---:|---:|---:|
| N [photons/H] | -1.0648541122975657e-9 | -1.067277844595226e-9 |0.002276116765357494|
| U [eV/H] | -4.7493108843455916e-8 | -4.751013573005532e-8 |0.00035851278246553313|

이 결과는 survivor가 최신 birth에 집중될 때 source-age quadrature가 중요하다는 진단을 지지한다. v8 sensitive certificate를 native bound로 재명명하지 않는다. Actual nonlinear opacity/closure transfer는 여전히 미구성이다. v8의all population은 큰 frozen passive 질량 때문에 native total과 직접 대응하지 않는다.

## 3. Constant-hazard midpoint source의 독립 검토

Native 원 설정을 바꾸지 않는 분석용 제어모형을 명확히 둔다. Proper time t∈[0,T], zero initial photons, 일정한 q>0 [photons/H/s], 일정한 lambda>=0 [s^-1], m∈N, h=T/m, midpoint births t_j=(j+1/2)h, 각 source mass qh다. Scalar loss는 dN/dt=-lambda N+q다. lambda>0이면

    N_exact(T) = q/lambda * (1-exp(-lambda T)),
    N_h(T) = qh exp(-lambda h/2) * (1-exp(-lambda T))/(1-exp(-lambda h)).

기하급수의 직접 합이며, x=lambda h를 두면

    N_h/N_exact = R(x) = x/(2 sinh(x/2)),
    N_h/N_{h/2} = sech(x/4).

lambda=0의 연속 극한은 두 비율1이며 N=qT다. q=0이면 비율은 정의하지 않고 두 number가0인 별도 case다. 부호와 양성은 q>0,lambda>=0에서 유지된다. h는proper seconds이므로 x는무차원이다. 중간 발산/near-zero 수치처리는 expm1 또는 급수 형태가 필요하다.

R(x)<1 for x>0이며 source integrand의 convexity 때문에 midpoint가 continuum source contribution을 과소평가한다. 작은 x에서

    R(x)=1-x^2/24+7x^4/5760+O(x^6),
    1-sech(x/4)=x^2/32-5x^4/6144+O(x^6).

Finite-neighbor relative target epsilon∈(0,1)에 대해 정확히

    |N_h-N_{h/2}|/N_{h/2}<=epsilon
    iff x<=4 acosh(1/(1-epsilon)).

epsilon=.005이면 경계x≈0.4008360307496088다. 이 경계의 coarse continuum error는0.006663323781662678이고 fine continuum error는0.001671682192625812다. 따라서 finite-neighbor0.5%를 coarse continuum0.5%로 해석할 수 없다. Coarse continuum0.5%를 별도로 요구하면 R(x)>=.995의 유일한 양의 근 x≈0.34701818109945304가 필요하다. 이 수치 평가는 일반 수학식 검산이고 원 native tolerance 조정이 아니다.

비음수 가중치와 여러 constant hazards를 갖는 independent channel에서는 aggregate N_h/N_h/2가 각 sech(lambda_i h/4)의 fine-survivor 가중평균이다. 모든 channel이 같은 exposure 상한을 만족하면 전체 nonnegative observable도 같은 finite-neighbor 상한을 만족한다. 가중치가 음수인 signed observable, time-varying hazard, nonlinear feedback 또는 node reconstruction에 이 결론을 자동 확대할 수 없다.

Native는 log(a) 균등 clock이고 proper-time 간격, source, geometry, gas, closure가 변한다. 따라서 위 scalar 식은 원래 큰 finite-neighbor 차이에 대한 계산 가능한 source-exposure 진단 및 후속 source rule 연구의 제어 기준이다. Native 결과에서 하나의lambda를 역추정하고 실제 native의 새 discretization을 승인하는 근거로 쓰지 않는다.

## 4. 최소 구현 제안과 R6 판정

1. 기존 `source_jump_diagnosis`의 검증된32pre/post와 interval snapshots를 연결하는 read-only exact telescoping analyzer를 추가한다. Event 중복/누락, wrong clock, source inventory mismatch, snapshot mismatch를 fail-closed한다. H/J/final arithmetic을 별도로 반환하고 원1e-8gate는 유지한다.
2. Native/fixed correspondence report에 clock match, source-pair mismatch, passive 정의와 위 sensitive comparison을 저장한다. 완료된v8 exponential 계산은 재실행하지 않는다.
3. Constant-source midpoint exposure module에 exact finite-neighbor식과 continuum식의 별도 API를 두고 lambda=0,q=0,small/large x, multichannel positive weight와 target inversion을 검산한다. 이 모듈은 source quadrature 설계의 제어 기준으로 닫는다.

R6 판정: **PASS_SCOPED_DERIVATION_AND_STORED_RAW_ANALYSIS**. 위 세 산출물 범위의 유도와 실제32/64 자료 대응은 확인했다. Native nonlinear continuum/response bound, native age/time convergence 및 production admission은 이 검토의 완료 범위 밖이다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED` 유지.
