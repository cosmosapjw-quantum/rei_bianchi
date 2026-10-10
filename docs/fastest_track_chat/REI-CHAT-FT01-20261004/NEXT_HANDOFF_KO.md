# 다음 연구: REI-CHAT-FT02_PROVIDER_DOMAIN

rei_bianchi의 기존 forward/rust-reion-kernels-20260922 branch에서 계속한다. 새 branch, force push, 자동 merge를 하지 않는다. 이 폴더 RESEARCH_UPDATE_KO.md, RESULTS_AND_RETURN.json, PACKAGE_RECEIPT.json을 읽고 현재 HEAD의 추가 변경만 확인한다. 필요시 영수증의 ZIP에서 전체 report/source/results를 복원하고 manifest를 검사한다. 업로드 R1과 실제 restore/science validation은 구분한다.

## 경량 범위

무거운 실행 없이 선택 H/He 원자 함수의 source-equation/domain/unit/case/branch/threshold/derivative 계약을 닫는다. 이미 채택한 문헌이나 사건 회계의 전수 재감사는 하지 않는다. 신규 ab-initio 원자 계산, full Grackle build, JAX/Python production 부활, 46080-node/history/GPU/MPI 캠페인은 시작하지 않는다.

필요 입력은 docs/atomic_reionization_handoff_20261004_v1/ 아래 다음 네 개부터 읽는다:
- common/EXTERNAL_SOURCE_LOCK.json
- common/PROVIDER_CONTRACT.schema.json
- common/external_reference/grackle_3_4_1/rate_functions.c
- common/external_reference/VERNER96_HHE_PARAMETERS.json

관련 함수의 추가 원문이 실제로 필요한 경우에만 확장한다. 원문 함수별로 채택 process, 초기/최종 종, 단위, frame, 유효 T/E 범위, case selection, floor/branch/table event, 1/2차 도함수, 점값 reference, notice/license를 기록한다. 몇 개 독립 원문 점값/기호 검산은 허용한다. candidate와 admitted를 분리하며 metadata 추가만으로 admission하지 않는다.

이번 7D static toy는 실제 physical parent/site topology를 대신하지 않는다. T-independent toy의 독립 기준해는 완료됐지만 thermal feedback은 시험하지 않았다. 원 fixture를 변경하지 말고 별도 온도-의존 controlled test의 식과 입력을 후속 노드에 준비한다. 실제 residual이 미구현이면 그 residual의 remainder만 unresolved로 남긴다.

## 완료 조건

선택 함수별 machine-readable equation/domain/branch/derivative map과 실행한 제한 검산 receipt, 남은 불확실성, 한 개의 다음 ready 연구 노드를 반환한다. strict local error<2e-4, public width<2e-3, legacy [160,161] FAIL 및 tick160 prefix는 변경하지 않는다. canonical REI-F00~F09는 실제 acceptance가 충족된 경우에만 별도로 업데이트한다. 기존 REI-L01 휴면 확장 lane을 이번 chat 연구 ID로 사용하지 않는다.

계획된 후속 경량 노드: FT03 온도 feedback/closure/secondary adequacy; FT04 실제 residual에 조건부인 sparse derivative/remainder; FT05 Bianchi-I exact transport와 작은 보존 검산; FT06 source/IC/domain 사전등록과 공통 원자 realization 감도 설계. production first interval/paired history는 해당 선행 산출물과 resource contract가 닫힌 뒤 별도 runtime에서 이어간다.
