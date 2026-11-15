# 원 IGM 목표에 대한 개발과정 교정

2026-11-16 KST. 이 검토는 [기존 PR318](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/318)의 적대적 감사를 재사용한 증분 교정이다. 현재 원본은 PR374의 `4554fc34765422f1c67e91c99ecac1bc9559fcce`이며, 그 저장 이력 소비 연구 R1–R10은 이미 완료됐다. 과거의 검토·실패·계산 예산은 그대로 보존한다.

**정체의 주원인은 물리 계산의 부재가 아니라, 공급자 성과와 실제 목표의 남은 의무 사이의 연결이 반복해서 끊어진 데 있다.** 지금 목표를 전진시키는 일은 AX08의 빠진 +0.01 전구간, AX11의 진화 수렴, AX12의 source/IC 민감도다. 새 그림·계약·PR·백업의 수는 이 진척을 대신하지 못한다.

## 같은 이름으로 다루어 온 서로 다른 목표

장기 D0는 자체 IGM thermochemistry에서 일반 Bianchi/finite tilt와 polarized CMB/LoS까지 이어지는 프로그램이다. 이를 유지하면서, 이번 실행은 [원 AX00–AX16 계약](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/1865fcec018ba0d2478321c9c2fac39490669697/docs/fastest_track_chat/REI-AXBI-GOAL-20261014/EXECUTION_DAG.json)에 있는 `REI-AXBI-GOAL-20261014`의 실제 H/He/electron abundance 산출물을 완결하는 데 집중한다. 이 원 산출물은 비기울어진 축대칭 Bianchi I와 일치하는 FLRW의 zbar20→4 진화다. AXBI 완료가 장기 D0 전체 완료를 뜻하지 않는다.

선택 시나리오는 `PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1`이다. MD14 연속 방출, 50,000 K 흑체, fesc=0.2, Case-A escape와 선언된 초기 상태를 사용한다. F05의 local OTS, F08의 constant-H S0, 별도의 17-state 모델과는 source·clock·IC·closure가 다르다. 최신 donor라는 이유만으로 상태를 합치면 모델을 바꾸게 된다. CR·HH·RCT·secondary electrons·분자는 이 baseline에서 OFF이며, 그 공급자 완성을 abundance 결과의 선행조건으로 만들지 않는다.

## 관측한 문제와 적용한 최소 교정

| 대상 | 관측 근거 | 영향 | 적용한 교정 |
|---|---|---|---|
| 진척 지표 | PR374가 보존한 2026-11-15 pre-loop 목록에서 PR129 뒤 244개 PR이 모두 open/draft다. 88개 중앙 ID 목록에는 AX ID가 없다. | 28/88이나 PR 수로 AXBI abundance 진행률을 알 수 없다. | 28/88은 보존하고, 원 17개 AX ID를 그대로 연결한 `GOAL_DAG.json`에서 4/5 실제 사례와 AX11/12 의무를 따로 보고한다. 새 완료 개수는 만들지 않는다. |
| 'original' source 혼합 | PR374 `OWNER_INTAKE.md`의 F05/AXBI/F08 불일치가 명시돼 있다. | 정확한 공급자 계산도 현재 상태에 결속되지 않으면 목표를 전진시키지 못한다. | `REPO_ROLES.json`과 시나리오별 intake 계약으로 동일 source 소비와 method-only 재사용을 구분한다. |
| 증명 의무의 전이 | 원 AX11은 경험적 수렴을 허용하고 'Do not require an old all-bound theorem as a global gate'라고 명시한다. AX05는 binary64 point 방식이다. | F05 continuum/Volterra 의무가 AXBI 실행을 막는 전역 gate로 변할 수 있다. | F05 의무는 해당 캠페인에 보존한다. AX11은 원 norm/floor와 dt/dE/dmu refinement로 판정한다. |
| 준비 예산의 오독 | 원 AX08/11/12는 coordinator의 finite measured allocation을 허용하며 preparation solver_runs=0과 구분한다. | 새 실행 계약을 세울 수 있는데도 준비·감사만 반복한다. | 실제 +0.01 checkpoint와 누적 비용을 복구하고 새 2700 s 단일-start 배정을 분리했다. 미확인 과거 비용은 0으로 바꾸지 않는다. |
| 고립된 정책 교정 | PR318은 비슷한 문제를 이미 지적했으나 별도 draft에 남아 현재 source branch에 전달되지 않았다. | 다음 스레드가 같은 문제를 다시 감사한다. | 기존 15-milestone projection을 복구하고 current_request_route만 덧붙였다. 원 D0 roster와 보고값은 유지한다. |
| 동시성 규칙 | 완료된 PR374 단위에는 'No subagents'가 있었지만 현재 사용자는 repo별 병렬 실행을 명시했다. | 과거 단위의 방식이 현재 실행 지시를 막을 수 있다. | 현재 독립 과제는 실제 agent로 나눈다. 과거 same-author, subagents=0 기록은 변경하지 않는다. |
| 범위 확대의 자기증식 | 확장 H–Li/분자/CR 공급자는 현재 고정 Case-A 모델에서 대부분 비활성이다. | 모든 repo에 새 단원을 주려는 방식이 불필요한 연구를 만든다. | 중앙 통합 하나와 실제 REC/HE 오류 교정만 게시한다. BASS/VigilODE 신규 작업은 AX11에서 측정된 필요가 있을 때 배정한다. |

244개 PR이라는 관측은 그 연구가 모두 무가치하다는 뜻이 아니다. 소스 복구, 보존량 검산과 수치 이론에는 실제 기여가 있다. 다만 해당 목록은 source inventory에 있는 metadata이며 모든 브랜치의 모든 파일을 다시 심사한 결과가 아니다. 미병합 자체보다, source-qualified 결과를 실제 목표의 consumer에 연결하고 다음 실행으로 넘어가는 과정이 끊어진 것이 핵심이다.

## 이번에 실제로 전진한 의무

새 물리 결과는 [approximation_validity/results/FULL_SUMMARY.json](approximation_validity/results/FULL_SUMMARY.json)에 있다. 네 원본 전구간의 1,248,952 native 상태에서 실제 ionizing J2, 열 상태와 배경복사 응력을 함께 적분했다. q=-0.01에서 저장 노드의 최대 |delta_s/H|는 1.0210497766163151e-5, source-defined extra-energy 비는 9.728861295902034e-8로, 원 1e-4 기준 아래다. 이는 **AX03/AX08의 근사 유효성 의무를 네 사례에서 해결한 결과**다. AX10 optional observable, 새 coupled trajectory, 진화 오차 상한 또는 전체 AX08 완료로 분류하지 않는다. 새 plot 재현도 아니다.

이 결과로 해당 네 사례에 새 feedback 모델을 즉시 도입할 이유는 생기지 않았다. 따라서 다음 우선순위를 원 AX11 진화 수렴과 AX12 민감도로 유지한다. 작은 abundance shift의 정확도가 해결됐다는 뜻은 아니다. +0.01 사례가 완료되면 같은 정의와 기준을 그 사례에 적용한다.

+0.01의 durable checkpoint는 a=0.10752752205956843, accepted=240480에서 확인됐다. 그 뒤 CSV 47개 행은 checkpoint가 아니므로 별도로 보존한다. 새 단일-start 배정은 2700 s, 1 thread, accepted 90000, attempts 360000, RHS 3000000 상한이며 원 상태와 누적 counter를 보존한다. 배정 문서는 실행 성공 영수증이 아니다. 실제 native preflight/launch/종료 상태는 `plus_recovery`의 해당 근거로만 갱신한다.

## 이미 있는 노드에서 마무리하기

- AX08: 정확한 checkpoint 복원 → 한 번의 유한 continuation → 실제 endpoint 여부 확인 → 경계 한 번만 포함해 구성 → 기존 abundance/milestone/근사 진단으로 소비.
- AX11: 기존 baseline에 적어도 두 refinement 수준을 더해 시간·에너지·각도 효과를 분리하고, paired response가 원 floor 및 오차 기준으로 해결되는지 판정한다. BE chemistry는 1차이므로 대칭 splitting만으로 2차 수렴을 가정하지 않는다. 해결된 null도 유효한 결과다.
- AX12: `FESC_025`와 `TGAS20K`를 다른 입력을 보존한 named sensitivity로 실행한다. 실제 REC donor 또는 posterior로 부르지 않는다.

매 턴은 기존 기록 안에서 **기존 목표/node → 동일 source 입력 → 기대하는 물리량·불확실성 변화 → 실제 변화 → 남은 한 의무**를 비교한다. 마지막에 달라진 것이 그림·메타데이터·재포장뿐이면 그 국소 경로를 종료하고 기존 미완료 계산으로 돌아간다. `DRIFT_WATCHDOG.json`은 이 판단을 기록하며 추가 승인·새 PR·반복 감사를 요구하지 않는다.

이 정책 문서와 구조 검사는 과학 완료로 세지 않는다. 이번 교정은 이 지점에서 끝내고, 지정된 실제 계산과 원 계약의 판정으로 이어간다.
