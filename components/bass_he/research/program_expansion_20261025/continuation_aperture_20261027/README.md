# HE-EXP-APERTURE-07

유한 lab 극각창의 CM 역상과 같은 사건의 두 딸입자 관측을 정확한 유리수 하한·상한으로 계산한다. γ,a와 양성 Bernstein 밀도를 고정한 조건부 reference이며, 실제 M0475 normalization·full angular law/flux·deuteron deposition은 계속 열린 물리 입력이다.

선택된 실행 범위는 이론 R1–R10과 구현 C1–C10의 한 번의 루프다. 단계별 새 source checkpoint를 백업·게시하고, 실제 결과와 비용을 기록한다. 기존 ANGULAR06 5개 완료 제품을 계승하고 새 제품 3개를 추가하여 시작은 **5/11**, 세 새 제품을 검증하면 **8/11**이다. 중앙 원 DAG는 **28/88**, 이번 HE delta는 0이다. 서로 다른 DAG의 수를 더하지 않는다.

## 기준과 주요 파일

- 기준 local delivery: `d0477e8c5459ff41ac54ccf37cefe9ced009c1b9`.
- 게시된 동일 tree source P06: `12702837bf3b2dd2af6439efe08ec4088e3adc90`.
- 선행 central publication: `8af3e56dcaa27a8362b2bf74d6fb3c8edd859413`, actual expected `74aff0740d1812c732466563a9c66108a3a4d8fd`, force=false.
- `CONTRACT_KO.md`: 가정, 식, 숫자 모델, 정확도·자원 및 소유권.
- `LOOP_PROGRESS.json`: 실제 단계별 완료 근거. source/backup의 post-commit ACK는 외부 단계 영수증에 있다.
- `preflight/`: 게시 후 조사와 선행 publication 확인.

PHOTON05의 24/24 PASS, plotCPU4.40726504>4s FAIL, workflowPARTIAL과 당시4complete+1partial+3physicalopen/8을 보존한다. HE101 C8PARTIAL_EXPORT19/20 reserve0 PASS/FAIL/FAIL도 유지한다. 선행 science/test/plot·백업 재실행과 예산 초기화는 없다. 입자수·열용량·rest/binding·비열적 에너지의 단일 소유권을 유지한다.


## S09 과학적 채택 — 체크포인트 기록

독립 실제 결과·그림 검토의 동일한 한 review pass가 PASS(실제 결과 검사 10개, 선행 정적 검사 18개 재사용, 결함 0)로 끝났으며, root는 `ACCEPT_SCOPED_CONDITIONAL_APERTURE_REFERENCE`를 채택했다. 현재 continuation DAG는 **8 complete + 0 pending + 3 physical open / 11**이다. 중앙 **28/88**, HE delta 0이며 물리적 전체 완료를 뜻하지 않는다. 채택 범위와 재사용 정리는 `ACCEPTANCE_KO.md`, 실제 독립 판정은 `review/RESULT_REVIEW.json`에 있다. 이 S09 시점에는 S10 인계 전이었다.

새 검증은 **32/32 PASS**, 1회, repair 0, CPU **0.235556515/4 s**, wall **0.24653371299791615/15 s**였다. Wolfram 1회에서 basis 질량·선형 weight·fold 잔차 **92개가 모두 0**이었다. 원격 실제 CPU는 제공되지 않아 null이다. 새 저장값 그림은 **PASS**, 1회, CPU **4.489548029/6 s**, wall **4.491183639998781/15 s**, 과학 함수 호출 0이었다. 기존 과학·검사·그림 재실행은 없다.

인증은 고정 저장 γ,a와 degree≤8 비음수 Bernstein 밀도의 연속 measure 및 방위각 전체를 받는 annular 창에 한정된다. 짝 사건 API는 대칭 밀도를 요구하며 atom/κ=0은 지원하지 않는다. 기본 API는 ε=σ_event·2^-40의 질량 폭을 보장하고, 수동 δ의 저장 예는 각 반환 구간의 실제 폭과 폭 경계를 적용한다. native12는 저장 γ,a와 합성 밀도만 사용하여 새 적분을 계산했으며 DCS 정규화나 실제 사건률을 채택하지 않는다. 질량·에너지 변환의 물리적 parameter 불확실성, 유한 방위각 3차원 검출기 기하와 세 열린 물리 입력은 이 채택 범위 밖이다.


## 최종 S10 작업 산출 상태

요청한 이론R1–R10과 코딩C1–C10의 작업 산출을 모두 완료했다. R10/C10은 **COMPLETE_WORK_PRODUCT**, 열 단계의 상태는 모두 COMPLETE, workflow는 **COMPLETE_SCOPED_CONDITIONAL**이다. 채택 결정은 **ACCEPT_SCOPED_CONDITIONAL_APERTURE_REFERENCE**, continuation DAG는 **8 complete +0 pending +3 physical open /11**, 중앙28/88·HE delta0다. 최종 재사용 인계는 `BASS_HE_APERTURE07_HANDOFF_KO_20261027.md`, 구조화 closeout은 `BASS_HE_APERTURE07_CLOSEOUT_20261027.json`에 있다.

이 commit-local 기록은 **PREPUBLICATION_S10_WORK_PRODUCT**다. `publication/STAGE_ACKS_THROUGH_S09.json`은 실제 source·양 provider 백업 ACK가 있는 **S01–S09 9/9, 전체10단계의9/10 prefix**이며 최종10/10 영수증이 아니다. S10 로컬 delivery는 이 파일의 containing commit을 가리킨다. 실제 자기 commit/tree와 원격 P10·두 backup ACK·APERTURE07 중앙 실제 ACK는 발생 후 root의 외부 최종 전달 영수증에 기록한다. 현재 사전 기록에서 **S10=PENDING_POST_COMMIT, central APERTURE07=PENDING**이다. 선행 ANGULAR06 중앙 게시8af3e56...와 현재 후보base42cc3a9...는 별개다.

이 루프를 완료한 뒤 자동으로 새 node·후속 loop·과학/검사/plot 재실행을 시작하지 않는다. 세 물리 입력, physical completion null, L4 false, production NOT_APPROVED 및 선행 PHOTON05/HE101 기록은 그대로다.
