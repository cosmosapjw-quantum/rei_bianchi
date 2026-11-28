# R10G: 첫 Coulomb 구간의 두 좌표 문제

## 판정

R10F의 경계 분할은 부분적으로 유효했다. 두 straight lane은 통과했지만 Coulomb 세 lane의 27성분은 첫 구간에 남았다. 따라서 R10F_BOUNDARY_SPLIT_GK_UNRESOLVED를 보존한다. 경계 분할만으로 해결된다는 앞선 전망은 충분하지 않았다.

이번 결과는 새 물리모델이나 전체 transport PASS가 아니다. 저장 R10F 자료, 같은 궤도의 회전 ODE 진단, 명시적인 epsilon=0 기하학적 제어, 독립 적분좌표의 비교를 통해 다음 후보를 준비했다. 새 contour/Delta=0, five-lane transport=0, Appendix 비교=0이다.

## 1. 원문과 입력

입력 PR17: 5efe052460e85f7e9785b9391d188ba394efee73.
원시 R10F archive 3105199 bytes, SHA256 082fd7ec94e2873ee218043828179e3c4db8d9f0d4ce28f9fa29f8c807207578. 실제 회수하여 ZIP CRC와 2014 payload의 크기/SHA256을 확인했다. 과거 receipt의 선언만을 새로운 restore 증거로 재사용하지 않았다.

첫 구간 밖16 interval의 error/tolerance는 매우 작다. 처음15 node에서 기존 rotation x1024/x2048를 비교한 최대 확률 차이는 1.919190140142746e-9다. 이 점검은 새 ODE 진단이지만 새 spectral solve는 아니다. 현재 192.34의 큰 GK 실패를 기존 노드의 회전 step 오차로 설명하기에는 이 차이가 작다. 단, 모든 기하학·수치 오차의 엄밀한 상계를 얻은 것은 아니다.

## 2. real-axis kink와 가까운 복소 특이점은 다르다

u=rho^2, a>0, Rc>2a에서 cos(phi_c)=(a+u/Rc)/sqrt(a^2+u)다. 동역학적 epsilon을 0으로 놓은 별도 제어에서 U_geo=exp(2i phi_c Lz)이고 l=1의 |mx=0>에서 |mx|=1로의 확률은

P_geo(u)=4u(a+u/Rc)^2(1-2a/Rc-u/Rc^2)/(a^2+u)^2.

이는 u=0에서 매끄럽고 P_geo(0)=0, 기울기는 4(1-2a/Rc)/a^2이다. 반면 complex u=-a^2에 double pole이 있다. 따라서 real axis의 불연속이 없어도 u~a^2 규모의 변화는 단일 polynomial GK panel로 해상되지 않을 수 있다.

중요한 제한: 이 rational 함수는 epsilon=0 제어이며 전체 회전확률의 정확한 식이나 전체 복소 singularity 구조를 주장하지 않는다. 그러나 Coulomb 궤도 자체가 도입하는 head-on scale을 분명하게 분리한다.

첫 구간 U=(0.5111982111775345)^2에 대해 U/a^2는 약57과5706이다. 기존 GK의 첫 rho는 약0.0334로, 특히 E=5 keV/u의 a≈0.00677보다 훨씬 크다. 이 해상도 문제는 upper activation boundary를 split하는 것과 별개다.

새 외부 좌표 후보는 tau=log1p(u/s), s=a(5 keV/u)^2이다. u=s*expm1(tau), du=s exp(tau)d tau이며 원래 measure 2pi rho d rho=pi du를 그대로 보존한다. 첫 구간의 네 동일 tau panel만 사용하고, 다른16구간은 바꾸지 않는다.

기하학 제어8개에 대해 60자리 mpmath 적분과 비교했다. 원래 한 u panel의 최대 실제 상대오차는 약3.9999e-3, log4의 최대는1.56e-15였다. 이 수치는 제어함수 적분의 결과이며 실제 BASS_HE 단면적 정확도가 아니다.

## 3. 새 quadrature node에는 예전 rotation PASS를 상속할 수 없다

새60 node의 최소rho≈0.00065197이다. 이 노드들에 기존 x-adapter를 그대로 적용하면 512->1024에서 E=5 keV/u의 세 조합이1e-7 gate를 넘었다. 1024->2048에서도 최악1.2822325023975623e-7가 남았고 unitarity 최대7.58e-13도 기존5e-13보다 컸다. 실패를 숨기거나 tol을 완화하지 않았다.

따라서 step 수를 계속 올리거나 외부 적분만 바꾼 계약은 채택하지 않았다. 입력rho 범위가 달라지면 integrator의 과거 accuracy 결과도 자동으로 따라오지 않는다는 실제 반례다.

## 4. 같은 물리식의 hyperbolic anomaly 표현

물리 단위에서는 a=Z1 Z2 e^2/(4pi epsilon_0 mu v^2)이며 길이다. 코드의 수치는 기존 atomic-unit/legacy velocity convention을 유지한다. eta를 repulsive-Coulomb hyperbolic anomaly로 잡고 b=sqrt(a^2+rho^2)라 하면

R=a+b cosh(eta),
t=(a eta+b sinh(eta))/v,
cos(phi)=(b+a cosh(eta))/R,
sin(phi)=rho sinh(eta)/R.

여기서 dt/deta=R/v, dphi/deta=rho/R, theta=pi/2-phi다. J=hbar L인 dimensionless L 행렬을 쓰면 원래 회전방정식은

i dA/deta=[epsilon_phys R^3/(hbar v) Lx^2 - rho/R Lz] A.

실행 코드에서는 epsilon_phys/(hbar)를 atomic units로 표현한 기존 계수를 사용한다. 입출력 basis와 |mx| collapse는 기존 convention과 같다. eta 경계는 +/-acosh((Rc-a)/b), 진입 조건은 a+b<Rc다.

rho->0에서 R=a(1+cosh eta)>0, 각속도항은0으로 가므로 x표현의 큰 상쇄 계수를 피한다. a->0, rho>0에서 R=rho cosh eta, x=rho sinh eta이고 straight-line 식으로 돌아간다. 이는 궤적·정규화·cutoff 변경이 아니라 같은 ODE의 독립변수 변경이다.

Wolfram은 circle/orbit identity의 residual0, dphi/deta=rho/R, R^2 dphi/dt=rho v, head-on limit을 확인했다. wrapper는 undefined-symbol warning을 함께 반환했고 이를 evidence에 보존했다. warning을 과학 실패로 해석하지도, 없었다고 숨기지도 않는다. 핵심 등식은 직접 유도로도 재현 가능하다.

## 5. 실제 준비된 코드와 검산

eta_rotation.py는 research-only Magnus4 구현이며 production/source를 변경하지 않는다. 원래 x-gauge ODE를 full-matrix DOP853으로 따로 적분한 auditor와 비교한다. 같은 수학모델을 다른 방식으로 검산한 것이지 독립 물리증명은 아니다.

새60노드/12조합에서 eta128/256/512를 검사했다:
- 최대 |P256-P512|=4.200341185978118e-10.
- 같은 worst node의 관측차수는 약3.995~3.999.
- 최대 unitarity=2.5002222514558525e-13.
- 최대 collapsed stochasticity=1.5432100042289676e-13.
- 각조합 worst node에서 독립 x-gauge DOP853와 최대 확률차이=2.8135604956958105e-11.

TDD에서 eta skeleton은9개 행동실패, plan의 linear-u control은5개 실패였다. 구현 후 경계/sign/invalid-domain/measure/고정query/outer-reuse 테스트를 보강하여 최종22 PASS, compileall PASS를 확인했다. source snapshot으로 얻은 earlier diagnostics와 최종 standalone preflight는 evidence에서 구별한다.

## 6. 다음 numerical contract와 종료 조건

수리 후보의 별도 검토 및 preflight가 통과한 뒤에만 신규 Delta300개를 허용하는 R10G 후보 계약을 제공한다. 이 연구 세션은 그 Delta를 계산하지 않았다.

첫 구간은60개 새rho/300pair, 나머지는 기존240rho/960pair와16개의 interval high/error를 재사용한다. 합계300rho/1260pair/20panel이다. 매끄러운 다른16구간을 다시 계산하지 않으며 기존1035행을 버리지 않는다.

새 첫4panel의 high/error와 기존나머지16의 high/error를 각각 합한다. 모든90성분에 기존 atol=1e-10,rtol=2e-4를 적용한다. 실패하면 같은 실행에서 새 panel 수나 tol로 우회하지 않는다. PASS이어도 고정 규칙의 empirical numerical acceptance이며 global continuum bound나 physical production claim이 아니다.

이 설계는 결과를 보고 만든 outcome-informed 제안이다. full transport에서 head-on scale이 유일한 원인이라는 결론, R9 I2의 새 정량해석, Appendix 재현 향상은 아직 미결정이다.

## 문헌

SciSpace로 찾은 Gautschi의 Gauss-type quadrature for rational functions(arXiv:math/9307223) 저자 초록은 구간 밖 가까운 pole이 있는 적분 문제를 다룬다. Leimkuhler(1999), DOI10.1098/rsta.1999.0366의 원전 초록은 Sundman 계열 regularization과 classical atomic trajectories를 다룬다. 이 문헌들은 이번 rho 변환의 정확한 threshold나 eta512 PASS를 증명하지 않는다. 그 부분의 근거는 명시한 유도와 이번 직접 계산이다.

## Gate

CODE_I02_CLOSED=true; full_certificate_fail_closed=true;
scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN.
R10F 실패는 보존한다. R10G authoring/code/preflight는 준비됐고 새 transport 결과는 없다.
