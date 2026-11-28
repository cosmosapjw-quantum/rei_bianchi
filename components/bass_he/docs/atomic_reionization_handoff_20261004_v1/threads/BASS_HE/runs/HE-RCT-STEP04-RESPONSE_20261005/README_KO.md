# HE-RCT-STEP04-RESPONSE

FINITE_SECOND_ORDER_RESPONSE_PASS__OWNER_ADOPTION_UNCHANGED. 기존 static FT03+KF96,Ebar=Q,0..1e11s에서 매우 작은 electron ON–OFF signal을 두 큰 전체이력 차감 없이 계산하는1차/2차 sensitivity를 구현했다. STEP03 ledger 감사/원자/native suites와 기존ON/OFF기준계를 재실행하지 않았다. 원소스/addon/consumer/root/TASKS 변경0,새native실행0이다.

## 새 직접 유도와 코드

U=(x,y,z,w,p0,p1,p2,escaped),w=u/(nH*eV_erg),p=n_gamma/nH,f=nHe/nH,tau=t/t_star,epsilon=k0*nH*t_star≈1e-7,theta=lambda*epsilon이다. lambda는 형식적미분 파라미터이지 다른 공급자/온도영역의 승인이 아니다.

    U'=B(U)+theta*H(U), h=f*(1-x)*z,
    H=h*(1,1/f,-1/f,Q-Ebar,0,0,0,Ebar),
    U=U0+theta*S1+theta^2*S2+O(theta^3),
    S1'=DB*S1+H,
    S2'=DB*S2+0.5*D2B[S1,S1]+DH*S1.

S2는2차미분/2다. 같은 jet arithmetic으로 기존 equations 산술 본문을 평가한다. AST의 유일한 관측변경은 기존 ph/CI/RR/DR 전자율을 return tuple에 추가하는 것이다. 원 source SHA2565d4c5a30e2e6c0ccd08ca727c84c25d54fb7783bdcbdbabfba274dd3e55cc491는 불변이다. Native AD가 아니라 source-bound 저자 oracle의 미분 경로다.

ell=(1,f,2f,0,0,0,0,0),ell*H=0이고 ell*B=b_photo+b_CI+b_RR+b_DR다. 각A_i'=Db_i*S1을 적분하면 ell*S1=sumA_i이며2차도 같은 방식으로 분리한다.1차 전자반응 perH는 photo -7.64090003187145e-12,CI -1.54382019832385e-12,RR +1.16664263452492e-15,DR -3.74710815002554e-17이다. 음의총신호에 대한 signed비율은83.20165808%,16.81063746%,-0.01270356%,0.00040802%다. 이 모형의1차 기여이며 실제 재이온화의 보편적 분율이 아니다.

## 실제 수치 결과

    linear electron response=-9.1835910586422823748748886433e-12
    quadratic correction=+4.4801048722701361323457316223e-20
    second-order total=-9.1835910138412336521735273198e-12
    stored prior ON-OFF=-9.1835910138412303203616602884e-12.

저장된 값과의2차 상대차3.62800550e-16,1차 상대차4.87838058e-9다.2차count도 이전reference와 상대1.23134356e-16차다. 두 reference에 시간오차가 있으므로 이 잔차를 엄밀한3차나머지라 부르지 않는다.

새canonical4solve는 DOP853두tolerance와mpmath45자리RK4 128/256이다. 개발pilotDOP8531회는 별도 기록하며 독립milestone으로 합산하지 않는다. 원ON/OFF기준계/native 재실행0.14tests통과이며 primitive6+변조checker2만 실제RED/GREEN,나머지6은 tests-after다.7상태의1/2차 계수를 별도mpmath.diff로 대조했다. 신규independent scientific review와interval proof는 없다.

종분율 민감도의 electron projection에도 조건수211.67의 상쇄가 남는다. 같은 binary64 solve에서 종분율조합의 고정밀 상대차는약9.0e-14이지만, 네채널적분을 직접합하면1.75435e-15다. 전체이력차감은 피했으나 모든 cancellation을 없앴다고 하지 않는다.

## 최신 consumer 및 claim 경계

REI e63ca0735a3e3e7eebbf4498c697d806d375e191의 EXECUTION_STATE/F09/SUCCESSOR_DAG_STATE를 읽었다. F08은 prescribed discrete pair의 scoped완료, F09는 empty common source-domain/external binding차단이다. 이를 다시 계산하거나 재심사하지 않았다. ft03/he_rct관련blob는 기존과같다. 본lambda 미분은 GM25를 유효온도밖에서 사용하는 우회가 아니다.

owner의 기존STEP01/02/03 채택대기는 그대로이며 이response를 새필수gate로 추가하지 않는다. baseline RCT OFF,momentsnull,HE-F2globalfalse,HE-F3/F09blocked,physicalHOLD,Eq55NOT_RUN,legacyPARKED_OPEN을 유지한다.

Git에는 요약/계약과 실제실행한jets.py,response.py를 둔다. 전체모델loader,ODErunner,tests,원equation/initial/reference,실패/성공로그 및고정밀계수는 BASS_HE_RCT_STEP04_RESPONSE_20261005_v1.zip에 있다. Gitprojection만으로 전체runnable source가 checkout됐다고 하지 않는다. archive/cloudidentity는 DELIVERY_RECEIPT.json을 따른다.
