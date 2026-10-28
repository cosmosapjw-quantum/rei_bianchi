# 이번 선택 단위의 연구·코딩 단계

Fresh Astra의 실제 결과 검토와 root admission은 PASS_SCOPED이다. 전체 목표는 87-node DAG이며 현재 위치는 N3/N4의 REI-L1 partial / REI-EXP-OPACITY-CONSUMER이다. N6 HOLD, L4_ready=false, 전역 완료율=null이다. 아래 단계의 진척으로 전체 목표 완료를 주장하지 않는다.

| 단계 | 이름 | 상태 | 근거 |
|---|---|---|---|
| R1 | 연구 위치·계약 | complete_scoped | `UNIT_START.json` |
| R2 | 근거·재사용 | complete_scoped | `intake/SOURCE_AUTHORITY.json`, `intake/SURVEY_SYNTHESIS_KO.md`, `runtime_inputs/PROVENANCE.json` |
| R3 | 주장·전제 정렬 | complete_scoped | `theory/DERIVATION.md`, `theory/IMPLEMENTATION_CONTRACT.json` |
| R4 | 가설·표현 탐색 | complete_scoped | `theory/DERIVATION.md`, `implementation/NUMERICAL_DESIGN.json` |
| R5 | 구성적 유도 | complete_scoped | `theory/DERIVATION.md`, `theory/WOLFRAM_CHECK.wl`, `theory/WOLFRAM_RESULT.json` |
| R6 | 독립 검증 | complete_scoped | `review/ASTRA_CONTRACT_REVIEW.md`, `review/INDEPENDENT_DERIVATION.md` |
| R7 | 판별 검증 | complete_scoped | `implementation/attempt01/test_results.json`, `implementation/attempt01/RECEIPT.json` |
| R8 | 결과 판정 | PASS_SCOPED | `review/ASTRA_FINAL_REVIEW.md`, `review/VALIDATION.json`, `ADMISSION.json` |
| R9 | 정식 결과·코딩 연결 | complete_scoped | `REPORT_KO.md`, `theory/DERIVATION.md`, `theory/IMPLEMENTATION_CONTRACT.json` |
| R10 | 종료·재개 | prepared_for_durable_delivery | `HANDOFF_KO.md`, `REPORT_KO.md`, `GLOBAL_DAG_STATUS.json` |
| C1 | 목표·baseline | complete_scoped | `UNIT_START.json`, `runtime_inputs/provider/PROVIDER_MANIFEST.json` |
| C2 | 식–데이터–코드 | complete_scoped | `implementation/coupled_collision.py`, `theory/IMPLEMENTATION_CONTRACT.json` |
| C3 | 수치 설계 | complete_scoped | `implementation/NUMERICAL_DESIGN.json` |
| C4 | 실행 DAG·자원 | complete_scoped | `implementation/RUN_AUTHORIZATION.json`, `implementation/run_bounded_tests.py` |
| C5 | 구현 | complete_scoped | `implementation/coupled_collision.py`, `implementation/test_coupled_collision.py`, `implementation/IMPLEMENTATION_HANDOFF.md` |
| C6 | 구현 검증 | complete_scoped | `implementation/attempt01/test_results.json`, `implementation/attempt01/RECEIPT.json` |
| C7 | 과학 검증 | complete_scoped | `implementation/attempt01/fixture_payload.json`, `implementation/attempt01/test_results.json` |
| C8 | 수치·재현성 | complete_scoped | `implementation/attempt01/test_results.json`, `implementation/attempt01/RECEIPT.json` |
| C9 | 독립 검토 | PASS_SCOPED | `review/ASTRA_FINAL_REVIEW.md`, `review/VALIDATION.json`, `ADMISSION.json` |
| C10 | 판정·인계 | prepared_for_durable_delivery | `HANDOFF_KO.md`, `REPORT_KO.md`, `GLOBAL_DAG_STATUS.json` |

Attempt01: exit 0, 19/19 true, child 0.200332 CPU s / 0.20596811699942918 wall s. Source 누적 8.201436/10 CPU s, 8.23558345200945/20 wall s. 재실행·새 IVP 없음.

실행 전 입력의 정확한 로컬 snapshot은 `implementation/attempt01/snapshot/`에 있다. Root가 FINAL byte-only archive 생성을 승인했으며, 이 파일의 동결 시점에 Drive/Dropbox durable 저장 ACK와 Git publication/draft PR은 아직 대기 중이다. 실제 provider/Git ID와 R10/C10의 전달 closure는 이후 `delivery/FINAL_DELIVERY_RECEIPT.json`에 별도 기록한다. 이미 동결된 archive를 자기참조 receipt 때문에 재포장하지 않는다.
