# HE-ANG-DDCS20-WINDOW 연구 결과

2026-10-24. 이론 R1–R10과 구현·검증·독립 검토 C1–C9를 완료했다.
R6 PASS, C9 PASS_SCOPED를 근거로 과학 결과를 COMPLETE_SCOPED로 수용한다.
C10 게시·최종 인계의 실제 ACK는 delivery/의 후속 receipt에 기록한다.

## 1. 이번에 확보한 것

실제 측정 자료인 Childers et al. (2004), PRA 69, 022709의 Table IV에서
**입사 에너지 20 eV, 검출 전자 에너지 3–6 eV, 검출각 15–120 degree**의
DDCS window를 구성했다. 원전의 40개 수치와 8개 행별 오차를 보존하고,
주 계산에는 32개 값을 사용했다. E=2 eV의 추가 오차 각주는 해석을 덧붙이지
않고 원자료에 남겼다. 출처 DOI: https://doi.org/10.1103/PhysRevA.69.022709 .

선택한 window에서 mu=cos(theta)와 E에 대한 양의 선형 hat 보간을 정의하고,
검출 전자의 0·1·2차 각모멘트, 에너지·운동량·운동량 텐서를 직접 적분했다.
정규화 모멘트는 양의 분모를 가진 선형분수식이므로, 지정한 입력 box에서
각 scalar의 전역 최소·최대를 효율적으로 구하는 구성을 유도하고 구현했다.

HE-ANG parent의 상태는 **SOURCE_INPUT_PENDING**이다. 이번 결과는
source-qualified **부분 검출 window의 조건부 모멘트**이며, joint electron
event law, ion recoil, 전체 에너지·각도 support 또는 finite-mass provider의
완료를 뜻하지 않는다. HE-X1의 완료된 이론·32 fixtures·검토는 재사용했다.

## 2. 실제 수치 결과

주 보간 모델에서 부분 검출 적분은

    N_W = 1.918935932462322e-21 m^2

다. 원전 값의 단위 10^-19 cm^2/(sr eV)에 10^-4의 면적 변환과
2pi dmu dE를 적용했다. 별도의 factor 2를 넣지 않았다.
이 N_W를 전체 ionization event cross section으로 해석하지 않는다.

| 양 | 명목값 | 선택한 deterministic box 최소 | 최대 |
|---|---:|---:|---:|
| N_W [10^-21 m^2] | 1.918935932 | 1.524433402 | 2.313438463 |
| mean(mu) | 0.521595023 | 0.446327702 | 0.596305146 |
| mean(P2(mu)) | 0.179984690 | 0.092214328 | 0.267152675 |
| mean(E) [eV] | 4.581073269 | 4.431612713 | 4.725062230 |
| mean(sqrt(E) mu) [eV^1/2] | 1.111325457 | 0.949664419 | 1.271018556 |

표의 box는 각 셀을 y(1-u/100)부터 y(1+u/100)까지 허용하여 **정의한
민감도 집합**이다. u는 원전의 행별 quoted 1-sigma percent다. 원전의 covariance는
알려져 있지 않다. 따라서 이 극값을 confidence interval이나 동시 1-sigma
coverage로 부르지 않는다. 보간 오차, reference-DCS 오차와 window 밖 기여도
포함하지 않는다. 각 scalar의 끝값에는 별도의 32-cell witness가 저장되어 있다.

지정한 모델과 box 안에서는 mean(mu)와 mean(P2)가 모두 양수로 유지된다.
이는 이 검출 구간의 전방 성분과 양의 이차 angular moment에 관한 결과다.
검출 window 선택을 제거한 전 영역의 각분포에 관한 결론은 아니다.

각 검출 에너지에서의 angular-window 적분은 다음과 같다.

| E [eV] | J0(E) [10^-22 m^2/eV] |
|---:|---:|
| 3 | 5.329034340 |
| 4 | 6.066529321 |
| 5 | 6.755629293 |
| 6 | 7.405367083 |

### 에너지와 운동량 텐서

epsilon=1.602176634e-19 J/eV, 전자 질량을 m_e라 쓰면

    U_W = epsilon R_01,
    P_z = sqrt(2 m_e epsilon) R_(1,1/2),
    S/(2 m_e epsilon)
      = diag(2.3963485085, 2.3963485085, 3.9980890876) e-21 m^2 eV.

trace(S)=2 m_e U_W가 성립한다. 정규화한 운동량 공분산은

    Cov(p)/(2 m_e epsilon)
      = diag(1.2487902634, 1.2487902634, 0.8484484696) eV

이며 모든 고유값이 양수다. 같은 양의 검출 측도에서 momentum과 second moment를
계산했기 때문에 Cauchy–Schwarz와 일치한다. 이 tensor는 outgoing 검출 전자의
모멘트다. Incident electron과 상대 전자, ion을 포함한 net collision source나
종별 에너지 전달률로 전환하려면 같은 사건 측도의 추가 입력이 필요하다.

## 3. 이론의 계산상 기여

비음수 hat L_i(mu), H_j(E)로 f_h=sum y_ij L_i H_j를 정의한다.
R_rq=2pi*10^-23 sum y_ij A_i^(r)B_j^(q)이며 r=0,1,2와 q=0,1/2,1이다.
A와 B는 hat의 affine segment를 가중 거듭제곱과 함께 정확히 적분하여 얻는다.
가중 함수를 단순히 node에서 곱한 뒤 trapezoid하는 연산과 구분했다.

정규화 scalar F(z)=(b.z)/(a.z), a>0, 0<l<=z<=h의 전역 극값은 다음 구조를
갖는다. q_k=b_k/a_k를 정렬하고, 작은 q 쪽을 upper endpoint로 올리는
threshold vertex를 n+1개 평가하면 최소를 찾는다. 최대는 endpoint 선택을
뒤집는다. Prefix sum을 사용하여 정렬 이후 O(n), 전체 O(n log n)이다.
이번 n=32에서는 scalar마다 33개 후보를 평가한다.

증명은 최적 r에 대해 (b-r a).z의 선형 최소/최대를 취하는 것이다.
계수 부호가 q-r의 부호와 같으므로 최적 endpoint 배치가 threshold 모양이다.
Signed numerator와 tie도 포함한다. THEORY_KO.md는 이 증명과 모멘트·tensor
차원, 양성성·PSD를 직접 유도한다. Nonlinear covariance의 exact box 극값이나
여러 scalar 극값의 동시 달성은 이 증명에서 주장하지 않는다.

## 4. 보간 선택과 수치 검증

동일한 source node, energy interpolation 및 window에서 각도만 linear-theta
보간으로 바꾸고 sin(theta) dtheta를 사용한 대조를 한 번 수행했다.

| 양 | 주 linear-mu | linear-theta 대조 | 대조 − 주 모델 |
|---|---:|---:|---:|
| N_W [10^-21 m^2] | 1.918935932 | 1.903933420 | -0.781814% |
| mean(mu) | 0.521595023 | 0.520149758 | -0.001445265 |
| mean(P2) | 0.179984690 | 0.179328118 | -0.000656572 |
| mean(E) [eV] | 4.581073269 | 4.581389450 | +0.000316182 |

이 차이는 두 보간 표현 사이의 민감도다. 연속 실험 DDCS의 오차 bound나
공간 해상도 수렴률로 해석하지 않는다. 관측 node에서 0인 positive bump를
더하면 같은 node 값으로도 적분이 달라지는 구성을 THEORY에 제시했다.
이를 새로운 strong no-go 성과로 내세우지 않는다.

실제 검증 근거는 다음과 같다.

- 독립 R6는 source convention, positive hats, tensor/PSD, ratio proof에 PASS.
- Wolfram 1회에서 left/right hat, sqrt(E) 적분, ratio derivative, variance
  항등식의 잔차가 모두 0. 실제 remote CPU는 UNKNOWN_NOT_ZERO다.
- 8 unittest PASS: closed-form constant/affine controls, cellwise Gaussian
  quadrature, n=1..6 전체 vertex oracle, signed/tie/scale, source/거부 조건.
- 실제 데이터의 11 physical/numerical checks가 모두 true.
- Analytic hats 대 독립 GL16/32 최대 scaled difference 1.8841299079e-15,
  고정 기준 5e-13 이내. Theta 대조의 GL16/32 최대 차이는 3.9513796893e-16.
- Root가 실제 PNG를 표시해 축·단위·window·오차 표기·잘림을 확인했다.
- C9 독립 검토 PASS_SCOPED: 현재 blocker 0개, 요구 repair 0개. 구현하지 않은
  검토자가 원표·코드·raw 결과·ledger를 확인했고 과학 재실행은 없었다.

원 수치와 witness는 results/moments.json, 검증 값은 results/validation.json,
실제 명령·종료 상태·비용은 evidence/execution/에 있다. 동일 코드 재실행만으로
증거를 늘리지 않았고, 완료된 HE-X1/HE38/Hex 계산을 다시 실행하지 않았다.

## 5. 자원과 재현

새 단위에서 테스트·실제 분석·그림 세 child invocation을 수행했다.
실측 누적 비용은 **CPU 1.957005 s, wall 2.104758353 s**이며 20/60 s 한도 안이다.
Repair reserve 한 번은 사용하지 않았다. Single-thread 설정과 1 GiB memory
limit, 호출별 6 CPU/20 wall s cap을 적용했다. 32-cell 문제의 작은 Python
binary64 reference이며 HPC 성능 향상을 주장하지 않는다.

이전 HEANG-CONTRACT의 0.592202 CPU/0.516821 wall s, Hex의
18.434312 CPU/18.739399 wall s, HE-X1/HE38/D10의 보존해야 할 비용과
UNKNOWN_NOT_ZERO는 새 ledger에서 별도 nontransferable 항목으로 연결했다.
전체 과거 비용을 완전히 측정한 grand total은 만들지 않았다.
Wolfram 호출의 관측 tool wall 13.307 s도 local scientific ledger와 구분한다.

재현 entry point는 unit cwd에서 아래 순서다. 완료된 동일 단위를 재실행하는
요청으로 간주하지 않으며, 다음 실행자는 먼저 기존 ledger와 remaining cap을 읽는다.

    python -B code/run_bounded.py tests
    python -B code/run_bounded.py actual_analysis
    python -B code/run_bounded.py plot

실제 환경·dependency version은 evidence/survey/ENVIRONMENT_SUMMARY.json,
고정 입력·허용오차·실행 규칙은 CONTRACT.json을 따른다.

## 6. 전체 목표의 DAG와 다음 단계

| 순서/갈래 | 상태 | 다음에 필요한 입력 또는 결과 |
|---|---|---|
| HE-X1 | COMPLETE_SCOPED, 재사용 | 기존 moment-cone admission 유지 |
| HE-ANG-CONTRACT | COMPLETE_SCOPED, 재사용 | source/frame/count/event 의무 유지 |
| HE-ANG-SOURCE-HEX-INTAKE | COMPLETE_SCOPED, 재사용 | 실제 파일의 ionization payload 부재 범위를 유지 |
| HE-ANG-DDCS20-WINDOW | COMPLETE_SCOPED | 이번 원전 window 결과, R6/C9 수용; 게시·백업 receipt 별도 |
| HE-ANG-SOURCE-PAYLOAD → HE-ANG | SOURCE_INPUT_PENDING | 같은 source의 joint angles/momenta 또는 event/amplitude payload, count·spin·exchange·frame·support·recoil |
| HE-EXCHANGE / HE-RESERVOIR | 기존 PROPOSED | 각자의 source와 calibration/ownership 계약 |
| HE-CLOSURE | 앞 세 물리 공급자 의존 | 종별 momentum/heat/STF와 lift-commutator/timescale 검증 |
| HE-FEEDBACK | HE-CLOSURE 이후 | 고정 배경 control 이후 별도의 metric feedback 문제 |

새 수치 결과로 다른 저장소 owner의 hold나 물리 완료 상태를 바꾸지 않는다.
최신 저장소·대화·백업 조사와 그 열람 한계는 SURVEY_AND_SELECTION_KO.md에 있다.
이번 R/C 20단계 완료율과 전체 물리 목표의 완료율은 다르며 후자는 숫자로
추정하지 않는다. 단계별 근거·게시·backup ACK는 LOOP_PROGRESS.json에 기록한다.

다음 스레드는 완료된 source/table/유도/tests/리뷰를 재사용하고,
HE-ANG-SOURCE-PAYLOAD의 **공급자 convention이 명확한 joint 입력**에서
다시 시작한다. DDCS window만으로 pair correlation이나 ion recoil를 채우지 않는다.

C9의 비차단 기록 NB-01: 미래에 window_moments의 부분 mu_window API를
재사용한다면 theta_degrees metadata를 요청한 부분구간에 맞추는 교정이 필요하다.
이번 고정 full-window 결과에는 영향이 없다. 현재 숫자·그림의 재실행 사유가 아니다.
