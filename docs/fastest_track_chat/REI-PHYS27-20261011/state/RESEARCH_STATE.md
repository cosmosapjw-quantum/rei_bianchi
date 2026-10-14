# REI PHYS27 연구 상태

- 상태: **RESEARCH_CLOSED_PROMOTE_SCOPED**.
- 최종 판단: `PROMOTE_SCOPED`, 실제 권위는 `independent/DECISION_REVIEW.json`.
- Physical admission: **HOLD**.
- 이론: 동일 폭 유한 대역족의 정확한 전역 응답 구간과 등호/퇴화, 동일 실제 W의 엄격 포함, 수치 지원 끝값 부호에 조건부인 두 근과 부호지도.
- 수치: 새 첫 main1회, 405/405 PASS; 두 근 각각80반복, kernel3923회.
- 재현: 새 경로 main1회, 305521바이트 JSON이 첫 결과와 일치. 독립 물리 credit0.
- 전체 실제 PHYS27 main은2회이며 첫 과학1회와 재현1회로 구별.
- 표시: 161 W, scalar kernel5508개; 레이아웃 변경은 캐시 재사용.
- 과거 PHYS19–26 main/suite/근 탐색, 새 도함수 부호 campaign, native, gas IVP는 모두0.
- 보호: [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED; 생산 변경0.
- 다음: PHYS28_SMALL_WIDTH_THRESHOLD_SENSITIVITY — **PROPOSED / NOT_RUN**.
- 원래 후보 87개 바이트는 최종 gate 후에도 일치.
- 연구 종료 UTC: 2026-10-11T04:50:54.850195+00:00.

최종 묶음의 실제 복구 검증과 Git/전달 완료는 이 상태를 선제 근거로 삼지 않고 분리된 `PHYS27_PUBLICATION_RECEIPT.json`의 실제 ACK·readback을 따른다. 새 원격 전체 ZIP 복구를 주장하지 않는다. 이 상태는 실제 PHYS27 결과이며 하네스의 NOT_RUN 템플릿과 구별한다.
