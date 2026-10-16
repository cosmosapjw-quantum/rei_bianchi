# FULL005 저장 PL 진단 재사용

고정 handoff를 읽고 C9 코드 e881b38951bc896c29d5ea57bb8fb1f2803873e1을 새 runtime에 자동 취득했다. 접수 시 최신 통합 branch에서 이미 완료된 actual_cached_001과 독립 검토를 발견하여 진단을 재실행하지 않았다.

두 저장 binary64 ln(a) PL 이력의 전체 겹침 구간에서 16개 관측량, 704041 union knots, 704040 segments를 비교한 기존 결과를 재사용한다. Tgas supremum은 0.24946455408644397 K, RMS는 0.1128202745602529 K다. 원래 실행 wall은 52.743859184 s, CPU 47.82 s, peak RSS 123044 KiB, exit 0이다.

NCP runs와 binding을 찾았다. 원래 12개 input descriptor의 기대 해시는 유지됐고 작은 metadata 8개는 일치한다. 대형 history/abundance 4개는 존재·크기·기존 identity 기록을 재사용하며 이번에 다시 해시하지 않았다. 현재 NCP 대형 파일의 새 byte 검증이나 새 metric 실행을 주장하지 않는다.

누적 debit은 156.5376037069618/300 s, 잔여 상한은 143.4623962930382 s다. 원래 deadline 2026-10-16T03:50:17.774070Z와 durable budget을 유지한다. 이번 analyzer/solver/render/ledger/checkpoint 실행은 0회다. 이전 9개 그림과 검산은 재사용한다.

허용 범위는 저장 PL 재구성 간 차이뿐이다. Solver 정확도·시간/각도 수렴·Bianchi·D/isotope 최종 승인은 HOLD로 남는다. 공개 패키지에는 비공개 원자료·checkpoint를 포함하지 않는다.

