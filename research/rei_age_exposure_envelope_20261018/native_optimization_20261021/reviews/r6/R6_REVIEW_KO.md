# V10 R6 독립 이론 검토

## 판정

**PASS_SCOPED. 열린 지적 0개.** 양성 측도의 한 원자 구성, 유계 관측량 및 C2 경계, 실제 저장 분모를 사용하는 backward-Euler kernel, 순서 보존 cohort 병렬화의 수학적 계약을 확인했다. 누적 exposure의 대표값이 정의되지 않았던 한 문장은 root가 유효 분모와 두 잔차 비율을 명시하여 교정했다. 이 판정은 이론과 구현 계약에 대한 것이며, 새 구현의 compiled 검증과 C9 판정은 별도 근거다.

검토 파일의 정확한 SHA256은 `REVIEWED_SOURCE_IDENTITIES.json`에 보존했다. 이 판정이 직접 읽은 THEORY SHA256은 `fc780203aefab9b523d8eac755ca7db20dabcb13ba67dc71d33695af95edeb66`이다. root가 이후 문헌 목록만 추가하는 경우 수학 본문의 동일성을 확인해 이 검토를 재사용할 수 있다.

## 독립 유도와 실제 연산 연결

### 1. 한 원자 구성과 원래 gates

양성 유한 측도 mu가 [a,b]에 지지되고 정확한 질량 N>0, 일차 모멘트 U를 가지면, aN<=U<=bN이므로 m=U/N은 [a,b]에 속한다. N delta_m은 정확히 같은 두 모멘트를 갖는다. 이 존재성은 유한 binary64 후보 집합이 항상 성공한다는 명제가 아니다.

원 코드 `axbi_covariant_transport.rs::cell_quadrature`는 보상합으로 count defect와 energy defect를 구하고, 각각 `64*EPSILON*n`, `128*EPSILON*max(abs(u), n*(hi-lo))`와 비교한다. 새로운 표현은 이 원래 실패 분기에서 subnormal 양성 n에만 허용되며, 후보 q의 유한성/지지구간 및 두 원 gates를 그대로 다시 검사한다. 정상 입력 경로와 tolerances는 이 계약에서 바뀌지 않는다.

N4는 eta=2^-1074일 때 N=10 eta, U=245 eta, q=24.5로 정확히 표현된다. 독립 Fraction 계산에서도 q*N=U였다. 다른 입력 N=10 eta, U=246 eta에서는 q=fl(U/N)의 rounded energy defect가 0이어도 실제 q*N-U는 `(1/70368744177664)*eta`였다. 따라서 실수 일차 모멘트 잔차와 rounded gate를 구별한 본문이 필요하다.

또한 N=eta, [a,b]=[24.1,24.2], U=24 eta는 rounded a*N과 b*N이 모두 U이지만 정확한 m=24는 지지구간 밖이다. 원 코드의 rounded endpoint 조건만으로 정확한 측도 존재성을 추론하지 않는다. 구현은 q의 지지구간과 원래 gates로 자신의 유한 후보를 판정하며, 수학적 존재성/관측량 bound는 명시된 실제 양성 측도 조건 아래 적용한다.

### 2. 유계 관측량 및 C2 경계

동일한 정확한 질량 N을 갖는 두 양성 측도의 f 평균은 모두 [inf f,sup f] 안에 있으므로 차이는 N*osc(f) 이하이다. f가 threshold에서 불연속이어도 이 유계 조건을 만족하면 이 경계는 유효하다. C2 경계는 해당 전체 지지구간에서 C2 및 |f''|<=M2가 성립할 때에 적용한다.

mu의 평균을 m이라 쓰고 Taylor 나머지를 R(x)로 쓰면

`f(x)=f(m)+f'(m)*(x-m)+R(x)`, `|R(x)|<=M2*(x-m)^2/2`.

중심 일차 모멘트가 0이므로

`|integral f dmu-N*f(q)| <= |f'(m)|*N*|q-m| + M2/2*(integral(x-m)^2 dmu + N*(q-m)^2)`.

한편 `(x-a)*(b-x)>=0`을 적분하고 평균을 대입하면

`integral(x-m)^2 dmu <= N*(b-m)*(m-a)`.

두 식을 결합하면 THEORY의 식을 얻는다. 두 endpoint에 같은 질량을 둔 mu=(delta_0+delta_2)/2, f=x^2, q=m=1에서는 이차항 경계와 실제 차이가 모두 1이므로 이 분산 경계의 상수는 그 조건에서 달성된다.

이 same-mass 식을 원래 실패한 노드 벡터와의 차이에 사용할 때에는 그 벡터의 **정확한** 질량도 N인지 확인해야 한다. 원래 벡터의 질량이 M이면, 유계 |f|<=B 아래 `min(M,N)*osc(f)+|M-N|*B`가 직접 쓸 수 있는 충분한 교정이다. 현재 본문은 same-mass 조건을 명시하며 일반적인 실패 벡터에 무조건 적용한다고 주장하지 않는다. 이 로컬 경계는 nonlinear gas feedback의 전역 응답 경계를 제공하지 않는다.

### 3. 실제 native BE 연산과 observer

실제 원 소스의 `PreparedAbsorption::evaluate`는 각 고정 prepared node에서 보상합 opacity를 구한 후 `1.0 + dt_s * model.c_cm_s * opacity`를 계산하고, 유한 분모>=1 조건을 검사하며, `node.number/denominator`를 계산한다. Python binary64 대조에서 이를 `1+dt*(c*opacity)`로 재결합하면 실제로 한 ULP가 달라지는 입력을 얻었다. 저장 lambda만으로 분모를 재생성하지 않는 root의 refinement를 독립 확인했다.

저장된 유한 양성 분모 d_i와 비음수 w_i에 대해 Q=sum w_i, S=sum(w_i/d_i)를 정확한 실수/유리수로 정의한다. 양의 가중치 노드에서 d_min<=d_i<=d_max이므로 Q/d_max<=S<=Q/d_min이다. 저장 가중치의 정확한 합을 포함하는 [Q_lo,Q_hi]가 있으면 Q_lo/d_max<=S<=Q_hi/d_min이다. 음수 lower endpoint를 쓰지 않는 outward 비음수 합, 원 연산의 실제 분모 extrema, 유한성/빈 support 처리가 전제다. per-node division과 addition을 outward 감싼 [S_lo,S_hi]도 같은 저장값 kernel을 포함한다.

Q=0/양성 노드 없음에는 빈 상태를 기록하고 extrema나 양성 ratio를 만들지 않는다. Q>0, d_i 유한 양수이면 S>0이다. D_eff=Q/S와 E=log D_eff를 정의하면 log d_min<=E<=log d_max이다. N_before>0일 때 kappa=Q/N_before, rho=N_after/S이면 N_after/N_before=kappa*rho*exp(-E)가 대수적으로 정확하다. N_after=0은 rho=0으로 처리하되 출력 생존비의 로그는 정의하지 않는다. 단계별 곱은 동일 cohort/상태의 실제 handoff를 확인한 연결만 포함한다.

실제 `donors/pr171/matrix_owner.rs`에서 prepared 목록은 chemistry 시작 때 동결되고, 각각 동일한 trial gas x로 평가된다. 광입력을 cohort 순서대로 합한 뒤 단일 공유 gas RHS를 평가한다. Newton norm<=1e-11인 바로 그 x와 stocks를 사용해 next를 만들고 absorption ledger를 확인한다. 따라서 observer는 그 최종 x/prepared/stocks에 결합되어야 하고, trial Newton 평가를 accepted step으로 기록하면 안 된다. 이후 전체 transaction의 number/energy gate 또는 geometry가 실패하면 파일은 accepted chemistry prefix를 포함한 INCOMPLETE로 해석한다. 저장 N_before/N_after는 지정된 합 방식의 rounded 관측값이며 S 자체와 혼동하지 않는다.

### 4. 순서 보존 병렬화와 자원 계약

원 `PreparedAbsorption::evaluate`는 입력 prepared 자료와 scalar gas에서 독립된 결과를 계산하고 cohort 공유 mutable 합을 갱신하지 않는다. 원 `OrderedWorkerPool::map_ordered`는 indexed slot으로 결과를 회수하며 최종 순서를 보존한다. 따라서 per-cohort 연산을 동일하게 유지하고 원 cohort 순서로 광입력을 더하면 같은 유효 입력에서 부동소수점 association을 보존한다. 같은 pool 안에 다시 일을 제출하지 않는 계약은 중첩 대기를 배제한다. 이에 대한 실제 구현 및 width1/2/4 비교는 C9/compiled control의 대상이다.

기존 전체 trace의 clone을 출력이 소비하는 공통8 pre/post 관측과 final state로 줄이는 것은 물리 stepping 자체를 바꾸지 않는 조건 아래 유효하다. full/compact trace와 observer off/on의 작은 실제 출력 비교가 그 연결을 확인한다.

검증된 64-core/128GB 유휴 host라는 조건에서 3*(20 workers+1 controller)=63 CPU slots, 3*24GiB+16GiB reserve=88GiB이므로 명시된 상한 안에 든다. 각 case 1800s의 할당 상한은 3*21*1800=113400 core-s다. 작은/shared host에서는 실제 affinity/cgroup/메모리에 맞춰 concurrency를 낮추며, 2000s elapsed cap은 계약에 적힌 3-way 구성에 해당한다. 성능 개선량과 NCP time8/16/32 endpoints는 실행 전 측정치가 아니다.

## 지적 및 교정

| ID | 대상과 관측 근거 | 영향 | 최소 교정과 상태 |
|---|---|---|---|
| R6-01 | 초기 누적 exposure 문장의 `sum log1p(dt_j*lambda_j)`에는 여러 노드를 가진 cohort의 scalar lambda_j가 정의되지 않았다. | 한 노드의 hazard를 cohort 전체 또는 reconstruction 이후 경로의 대표값으로 잘못 쓸 수 있었다. | root가 S, D_eff, E, kappa, rho를 정의하고 양성 조건·동일 cohort handoff·N_after=0 처리를 명시했다. 교정된 본문을 읽고 **CLOSED**. |

실제 분모 association 및 exact-cone 조건은 root가 보낸 precision refinement를 원 소스와 독립 Fraction 사례로 확인했다. 위 same-mass/C2/저장값/순서 조건은 해당 정리와 구현의 적용 조건이며 새로운 범위 밖 승인 절차가 아니다.

## 검산 기록과 현재 범위

`algebra_controls.py`의 7개 독립 control이 PASS했다. 실제 명령은 `python -B native_optimization_20261021/reviews/r6/algebra_controls.py`, exit 0, wall 0.023791467989212833s, timeout 5s였다. argv, 출력, stderr 및 SHA는 `ALGEBRA_CONTROL_RECEIPT.json`과 인접 파일에 있다. 표본 control은 위 일반 유도의 대체물이 아니라 edge condition 및 표현 차이의 확인이다.

원 AGENTS와 physmath 공통 정책/R6를 읽었으며 구현을 작성하거나 수정하지 않았다. native trajectory, 완료 age32/age64/v8 연구, 전체 과거 suite는 실행하지 않았다. finite candidate search의 완전성을 주장하지 않는다. continuous nonlinear Grackle response bound는 NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED다. 사용자 승인 탐색 실행은 구현과 필요한 bounded controls가 준비되면 진행할 수 있다.
