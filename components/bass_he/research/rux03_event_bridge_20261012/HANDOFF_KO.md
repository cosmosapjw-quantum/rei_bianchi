# 다음 최소 작업 — HERE_RUX03_PRIMARY_PROVIDER_03

## 출발점

`HERE_RUX03_EVENT_BRIDGE_02`의 실행은 PASS_SCOPED이며, 최종 채택 범위는 `review/DECISION.json`을 따른다. 정확한 receiver source는 `a5c958c414dea41216b445c05f58df837f05cacb`다. 그 부모 기준 PR97 `1400093cdd121d8e6adb51ffeb360102a48653bf`에는 PR101의 clean-build 수정이 이미 반영되어 있다. PR83은 별도의 owner/planning branch이므로 같은 source로 취급하지 않는다.

이번에는 기존 conditional production의 Case A event bundle과 실제 AXI RHS 소비를 닫았다. 현재 warm provider, threshold, kinetic moment, proper/comoving 단위, 외부 source와 geometry의 책임을 유지했다. 새 native build, 19개 대상 시험과 이를 포함한 전체176개 시험, 79개 probe check group, 초기값에서 시작한 단일 구간이 실제 통과했다. 완료된 이 경로의 추가 반복을 기본 다음 작업으로 삼지 않는다.

## 다음 질문

기존 **implicit primary**가 같은 사건·rate·thermal provider를 실제로 호출하도록 연결할 수 있는가? 그 point 평가와 root/interval 계산이 동일한 provider를 쓰는가? 다르면 어떤 주장 범위를 분리해야 하는가?

## 승인된 다음 루프의 최소 실행 단위

1. 기존 owner의 실제 implicit stage와 point/root/interval callsite를 필요한 부분만 읽고 provider seam을 특정한다. 이번 conditional adapter와 중복 구현이 생기지 않게 사건 담당을 맞춘다.
2. 현재 확정된 provider/event 계약으로 준비 가능한 adapter를 구현하고, source/time/geometry 및 부피 변환이 영향을 받는 실제 stage에 연결됐음을 확인한다. 고정 warm domain 밖을 입력하는 방식으로 가드를 넓히지 않는다.
3. 실제 stage 소비, 도함수/잔차, positivity와 핵수·전하·광자·에너지의 변경 위험을 판별하는 최소 시험을 실행한다. 새 point physics가 기존 FT03의 root/interval bound를 자동 상속한다고 하지 않는다.
4. RUX02의 source-backed physical input과 rate domain이 맞으면 RUX04의 scenario lock을 완성한다. 원래 의존성 `RUX02 + RUX03 → RUX04 → RUX05`를 충족한 뒤에만 물리적 첫 FLRW 구간을 실행한다. 필요한 필드가 없으면 정확한 필드와 한 개의 공급 작업을 기록하되, 가능한 adapter 준비·실행은 마친다.
5. 같은 author의 자체 확인과 별개로 최종 독립 판정을 받고 현재 상태를 갱신한다.

이 작업의 ID는 RUX03의 부분 준비를 나타내는 overlay다. 원 owner의 RUX02/RUX03 상태를 일괄 PASS로 바꾸거나 RUX04를 건너뛰는 RUX05 실행권을 의미하지 않는다.

## 유지하는 자산과 경계

- 직전 BASS He supplier/재결합 응답 결과, 이번 event bundle과 Decimal60 reference, source-bound 실행 receipt는 재사용한다.
- B1·기존 11-history·PR113·P03A의 변경 없는 캠페인을 반복하지 않는다. E13C11은 기존 PARKED_PENDING_OBSERVABLE_NEED다.
- 새 NCP work list는 `[]`다. 여기서 가벼운 actual probe/interval이 가능했다. 실제 무거운 독립 미완료 계산과 병렬 이득이 확인된 경우에만 별도 자원 packet을 만든다.
- 연구 기록과 격리된 source 변경은 draft PR로 게시한다. 병합은 이번 루프의 완료조건에 포함하지 않는다.

## 다시 열 파일

`REPORT_KO.md`, `CLAIMS.json`, `SCIENTIFIC_CONTRACT.md`, `NEXT_DAG.json`, `SOURCE_REVISION_FINAL.json`, `review/DECISION.json`, `EVIDENCE_INDEX.json`부터 읽는다. 원시 증거의 필요 범위를 선택해 `evidence/`에서 확인한다. 최초 실패는 `state/NEGATIVE_RESULTS.md`, format 수정과 입력 metadata 복원은 각각의 repair JSON에 남아 있다.
