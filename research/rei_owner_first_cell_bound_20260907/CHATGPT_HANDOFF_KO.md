# REI 첫 forcing cell — 실제 입력에 결합한 owner 부분 경계

STATUS: **ANALYTIC_G2A_STATE_PARTIAL_BOUND_DERIVED / FULL_OWNER_TUBE_UNKNOWN**
RETURN_TO: MAIN_CONVERSATION
WORK_THREAD_REQUIRED: false

## 이어받은 결과

PR #77의 고정 head `1244fa97b8e854ae0ced40f306cb41f28232800d`, tree
`581e304bd0aaefe784d88d5ac4f1f9494780eeed`에서 시작했다. handoff, 실제
O01--O10 stderr와 EXECUTION.json을 읽었다. 원래 실행 source는
`12d64833419651a532451ad4c9a180aa65a0a70b`이며 10/10, 1회, exit0,
timeout/failure/error/skip0이다. 기존 시험과 Python 후보는 재실행·수정하지 않았다.

## 이번에 실제로 전진한 부분

source-input tube 전체를 기다리는 대신, 실제 첫 보간 cell의 forcing 표와
resolved-owner support를 결합했다. source의 z는 owner표의 z_snapshot이 아니라
forcing z_mid=5.95다. e는 conditioned opacity가 아니라 raw subgrid response다.

첫 cell은 [0,6134904103445.532] s이며, 보존 microstep 끝
638562959250984.8/2048 ≈311798319946.7699 s를 포함한다.
실수 PCHIP의 shape preservation으로 표 양 끝의 hull을 연속 cell 전체의
경계로 사용할 수 있다. 이는 표본 최대값을 인증된 최대값으로 바꾼 것이 아니다.
단, 이 정리는 binary64 SciPy 또는 source의 잔차 보정 실행 인증이 아니다.

- G1: resolved owner가 없으므로 resolved current 및 상태 미분 0.
- G3: 첫 cell 양 끝 J=0이므로 그 cell의 J와 상태 미분 0. 일반 delta-J,
  다른 cell, OTS/충돌 반응의 HeII 항까지 0이라고 하지 않는다.
- G2a: resolved HeI 하나와 양수 external e가 있다. 실제 e>=0.0165719948704725가
  R의 하한을 제공하므로, 추가 neutral-state 하한 없이 상태 부분미분을 bound한다.
- G2b: external e=0, J>0이다. HI/HeI weighted-neutral sum의 양의 하한이 여전히 필요하다.

고정 global He total에 대한 share u_i=N_HeI,i/H_He, s=sum(u_i)를 쓰면

    j_i=J*p*u_i/(e+p*s),
    ||D_u j_resolved||_1 <= J*p/e.

실제 p≈11.891029169582541 cMpc^-1이며, endpoint-hull bound 표현은
약5.544995259880935e52 normalized-box photons/s다. 출력에는 느슨하지만
정확한 유리수 비교로 확보한 **L_G2a<5.7e52 s^-1**를 사용한다.
이는 dimensionless global-He share의 l1 차이에 곱하는 상수다. 실제값이나
관측된 최대 민감도, count 좌표에서 그대로 쓰는 상수, thermal/step 전체
Lipschitz 상수가 아니다. 다른 forcing/time/table 방향은 포함하지 않는다.

증명은 [PROOF_AND_SCOPE.md](PROOF_AND_SCOPE.md), 실제 입력 literals/소스 blob/
계산기 검산은 [RESULT_AND_INPUTS.json](RESULT_AND_INPUTS.json)에 보존했다.
종전 generic denominator 유도는 반복하지 않았고, 이미 존재하던
reduced_interval_rhs의 primal species-sum cancellation도 새 성과로 세지 않는다.

## 발견한 rounding 주의점

기존 pchip_bounds.py는 중간 binary64 산술 뒤 마지막 nextafter만 적용한다.
coeff=[0,1,2^53,-2^53], lower=upper=1이면 exact polynomial=1이지만
round-to-nearest ties-to-even의 Horner는0이고, 최종 nextafter는1을 포함하지 못한다.
이것은 **정적 산술 반례**이며 helper 실행이나 실제 표에서 발생한 실패는 아니다.
기존 helper/endpoint가 이미 엄밀한 rounding oracle이라는 주장은 사용하지 않는다.
이번 G2a 실수식 경계는 그 helper를 호출하지 않아 이 문제와 분리돼 있다.

## 실행·검토 상태

새로 수행한 수치 작업은 계산기의 명시적 산술 검산이다. 현재 container와
Python은 각각 process 시작 전 ClientError였다. 새 project test/CAS/plot은
NOT_RUN/NOT_GENERATED다. GitHub Actions로 대체하거나 과거 성공을 재실행하지 않았다.
검토는 같은 assistant의 수학 검토 다음 소스/수치 검토이며 독립 심사 인증이 아니다.

FULL_PHYSICAL_OWNER_TUBE=UNKNOWN. G2b endpoint의 실제 배열 경계도 이번에는
평가하지 않았다. binary64 rounding, OTS/원자율 전체 미분, thermal coupled
inverse, exact-flow rho와 production은 그대로 미완료다. 그룹 3개를 분리했다는
이유로 전체 완료율을75%라고 하지 않는다.

## 다음 한 단계

[LOCAL_CODEX_HANDOFF_KO.md](LOCAL_CODEX_HANDOFF_KO.md)의
REI_G2B_SAVED_ENDPOINT_OWNER_BOUND를 수행한다. 기존 primary endpoint와
fixed node totals만 읽어 G2b weighted-neutral lower bound를 계산한다.
성립하면 **second-half thermal_t1_final endpoint에 한정한** current/JVP
경계를 반환하고, 성립하지 않으면 어떤 public-box correlation/하한이 부족한지
실제 계산으로 반환한다. 전체 producer나 canonical interval은 재실행하지 않는다.

이번 기록은 새 research 디렉터리만 추가한다. PR #77의 원본 증거, 물리식,
production 코드/허용오차/lock, 네 source site, y0/yp와 half-weight 규약,
기존 one-shot budget는 불변이다. 게시에는 [skip ci]를 사용하고 Draft를 유지한다.
Local Codex 자동 dispatch는 없었다. 관련 REI Jira에는 결과 링크만 append하고
provider/first-interval/의존성 상태는 승격하지 않는다.
