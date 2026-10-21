# V10: subnormal 지지점 완화와 이산 BE exposure

## 문제와 실제 경로

V9에서 age32 기준해는 완료했다. 이번 미완료 time8/16/32는 다른 적분 경로다. `matrix_owner::chemistry`는 준비한 각 cohort의 이산 노드에 backward-Euler 감쇠를 적용하고, 모든 cohort의 광입력을 더한 뒤 하나의 공유 gas Newton 식을 푼다. 완료 age 기준해의 logarithmic DOP853 경로 및 v8 고정 exponential 연구를 이 식으로 대체 해석하지 않는다.

## R2–R5: 양성 두 모멘트의 구성적 지지점 완화

양성 측도 mu가 [a,b]에 지지되고 질량 N>0, 일차 모멘트 U를 갖는다고 하자. 정확한 실수 평균 m=U/N은 [a,b]에 있고, N delta_m은 같은 두 모멘트를 갖는다. 이는 존재성 구성이다. Binary64 구현은 q=fl(U/N) 등 유한 후보를 검사하고, q가 지지구간 안에 있으며 원래 count 및 energy gates를 모두 통과할 때만 받아들인다. 실수 구성 정리를 부동소수점 알고리즘의 무조건 성공으로 바꾸지 않는다.

N4의10 eta 질량,245 eta 에너지는 q=24.5, N=10 eta인 한 원자로 표현할 수 있다. eta=2^-1074다. 기존16개 고정 노드 중10개의 양성1-tick 가중치를 고정한 제한과는 다른 표현이다. 이 변경은 원래 gate 실패 및 subnormal 질량에만 적용한다. 정상 질량의 원 quadrature는 그대로다.

같은 질량 N의 임의 양성 측도 mu,nu에 대해 유계 f이면

`|integral f dmu-integral f dnu| <= N*(sup_[a,b] f-inf_[a,b] f)`.

이는 두 기대값이 같은 값 범위에 속한다는 사실로 따른다. 임계값을 가로질러 f가 매끄럽지 않아도 유계이면 성립한다. f가 C2이고 |f''|<=M2이면 m=U/N을 중심으로 Taylor 전개해

`|integral f dmu-N*f(q)| <= |f'(m)|*N*|q-m| + M2/2*(N*(b-m)*(m-a)+N*(q-m)^2)`.

첫 항은 실제 실수 first-moment residual이며 rounded machine-energy gate가0이어도 자동으로0은 아니다. 이 로컬 관측량 통제는 nonlinear gas feedback의 전역 오차 상한이 아니다. 실제 repair mass/count를 반환해 범위를 확인한다.

## R4–R5: 실제 native BE 단계에서 관측할 exposure

한 accepted chemistry 단계의 준비 노드에 w_i>=0, lambda_i>=0와 dt>=0가 주어지면

`Q=sum w_i`, `N_next_exact=sum w_i/(1+dt*lambda_i)`.

양의 노드에서 lambda_min<=lambda_i<=lambda_max이므로

`Q/(1+dt*lambda_max) <= N_next_exact <= Q/(1+dt*lambda_min)`.

여러 노드가 있는 cohort에 한 노드의 lambda를 대표값처럼 지정하지 않는다. Q_j>0이고 `S_j=sum_i w_ji/d_ji>0`이면 `D_eff,j=Q_j/S_j`, `E_j=log(D_eff,j)`로 정의한다. 그러면 `log(d_min,j)<=E_j<=log(d_max,j)`다. 저장 입력 N_before,j>0일 때 `kappa_j=Q_j/N_before,j`, `rho_j=N_after,j/S_j`를 정의하면

`N_after,j/N_before,j = kappa_j*rho_j*exp(-E_j)`.

이 항등식은 재구성 질량 비율 kappa, 출력 반올림·집계 비율 rho, 이산 유효 exposure E를 분리한다. 동일 cohort의 실제 상태 전달을 확인한 연결에 한해서만 단계별 식을 곱할 수 있다. N_after=0이면 rho=0은 허용하지만 출력 생존 비율의 로그를 정의하지 않는다. Q=0이거나 입력 N=0일 때 이 양의 비율 공식을 적용하지 않는다. 현재 구현의 인증 범위는 per-step 저장 분모 kernel이며, 전체 연속 물리 경로의 인증을 발행하지 않는다.

이 양끝값은 accepted gas와 frozen prepared nodes에 관한 이산 식이다. 재구성 때 노드 정체성이 바뀌므로 영속 photon label 경로가 아니다. 연속 nonlinear Grackle 해의 hazard supremum이나 response bound는 여전히 NOT_ESTABLISHED다.

실제 연산 순서는 `d_i=fl(1+fl(fl(dt*c)*opacity_i))`다. `lambda_i=fl(c*opacity_i)`를 저장하고 `1+dt*lambda_i`로 다시 만들면 연산 결합이 달라진다. 따라서 구현 observer는 원 식으로 계산한 d_i의 min/max와 저장 w_i의 정확한 합을 포함하는 outward 구간 [Q_lo,Q_hi]를 기록한다. 그러면 정확한 유리수에서 `Q_lo/d_max <= sum(w_i/d_i) <= Q_hi/d_min`이다. 이것은 **저장 분모를 갖는 이산 BE kernel**의 경계이며 unrounded 물리 계수에 대한 인증이 아니다. Per-node division을 outward 감싸 더하면 더 직접적인 [S_lo,S_hi]도 얻는다. 비어 있는 양성 support에는 Q=0을 쓰고 양의 분모 극값/질량 비율을 정의하지 않는다.

## C1 수학적 성능 계약

독립 cohort의 준비된 absorption 평가를 병렬로 계산하되, 결과를 index 순서대로 회수하고 기존 cohort 순서로 광입력을 더한다. 각 cohort 연산과 reduction association이 같으면 유효한 동일 입력에서 floating-point 결과도 같다. 작업자의 완료 순서는 합 순서가 아니다. 같은 persistent pool 안에서 중첩 작업을 제출하지 않는다.

native trace에서 기존 최종 출력이 소비하는 공통8 관측시각의 pre/post 상태만 보존하면 물리 stepping은 바뀌지 않는다. 모든 time mesh 지점에서 cohort 전체를 복제하던 메모리 비용을 필요한 관측 snapshot 수에 비례하게 줄인다. Path observer는 accepted-step compact scalar rows를 따로 streaming하며 solver에 되먹임하지 않는다.

## 현재 주장 범위

구성적 수식과 코드 계약을 만들었으며 구현/compiled verification/독립 review는 별도 receipt를 따른다. 64core128GB는 사용자 목표 host이며 이번 sandbox에서 관측된 하드웨어가 아니다. NCP 실제 속도향상, time endpoints 및 원0.005 accuracy 목표는 실제 반환 전 NOT_MEASURED/NOT_RUN이다. PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED.
