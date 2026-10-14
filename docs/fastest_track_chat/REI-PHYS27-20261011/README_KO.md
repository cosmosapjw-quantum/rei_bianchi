# PHYS27 — 유한 폭 스펙트럼 응답

반폭 0.05 eV, 평균 18 eV의 동일 폭 균일 대역혼합에서 모든 실제 광자 분산의 정확한 초기 HeIII 응답 구간을 구했다. PHYS26보다 비음수 응답의 존재 문턱은 올라가고, 모든 응답이 비음수인 문턱은 내려간다. 현재 수치 근사는 **16.6294590240**, **23.3008661823 eV²**다. 두 응답의 공존 구간은 약 **5.7747%** 좁아진다.

## 읽는 순서

1. [통합 한국어 보고서](report/PHYS27_REPORT_KO.md): 질문·정리·물리 해석·수치 결과와 한계.
2. [독립 최종 판정](independent/DECISION_REVIEW_KO.md), [판정 JSON](independent/DECISION_REVIEW.json): 실제 승격 권위와 범위.
3. [기계 판독 요약](report/PHYS27_RESULTS_SUMMARY.json), [주장 의존표](claims/CLAIM_DAG.json).
4. [원 이론](contributions/theory/FINITE_WIDTH_DERIVATION_KO.md), [수치 설명](contributions/numerics/NUMERICS_NOTE_KO.md), [첫 결과](contributions/numerics/FINITE_WIDTH_FIRST.json).
5. [재현 사용법](portability/NOTE_KO.md), [실제 재현 영수증](portability/REPLAY_RECEIPT.json).
6. [다음 PHYS28 단일 질문](next/PHYS28_NEXT_HANDOFF_KO.md): 작은 폭의 문턱 이동계수, 제안만 있고 미실행.

첫 계산은 사전 동결 후 1회, 405/405 PASS다. 새 경로의 별도 재현 1회가 305521바이트 첫 결과와 일치했다. 실제 main 총 2회를 첫 과학과 재현으로 구별한다. 재현은 독립 물리 근거로 세지 않는다.

대역 분산은 실제 광자 분산 W=중심 분산 V+δ²/3이다. 정확 정리·정확근 정의와 유한 수치 근사를 구별한다. 긴 소수는 재현용이며 물리적 정확도나 directed interval enclosure가 아니다. 이 연구는 명시적인 동일 폭 대역족과 동결된 source-real 상수·직렬화 수치 J에 조건부다.

**Physical HOLD; [160,161] FAIL; tick160; auxiliary escape FAIL; HH/RCT/CR OFF; precision atomic PARKED.** 생산 source/default/runtime 변경 0, native 0, gas IVP 0, 과거 PHYS19–26 main/suite 재실행 0이다.

최종 연구 종료 상태는 `state/RESEARCH_STATE.md`, 전체 묶음 정체성은 `MANIFEST.json`에서 읽는다. 최종 게시 및 전달 영수증 `PHYS27_PUBLICATION_RECEIPT.json`은 ZIP 바깥에 분리하여 순환 해시를 피한다. 그 영수증의 실제 ACK·선택적 원격 readback 범위를 확인하며 새 원격 전체 ZIP 복구를 수행했다고 해석하지 않는다.
