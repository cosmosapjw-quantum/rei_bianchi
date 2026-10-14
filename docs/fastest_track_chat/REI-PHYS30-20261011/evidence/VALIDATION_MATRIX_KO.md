# PHYS30 검증 연결

이 매트릭스는 실제 증거의 연결이며 추가 과학 실행이 아니다.

| 위험 | 사전 방법 | 실제 근거 | 범위 |
|---|---|---|---|
| 실제 W/중심 V 혼동 | 모멘트 직접 유도, bivariate moment series | T30.7–12 및 raw physical moment groups | 고정 분포족 |
| 일반 측도에 대한 부당한 미분·극값 확대 | 유계 도함수, Hermite/Rolle | T30.14–27 | 조건부, 부호 상속 |
| 평균/분산 항 중복·누락 | G chain rule,11항 분해와 두 경로 | T30.32–43 및 raw | 새 물리 데이터 없음 |
| factor2 오류 | ordinary coefficient matching, quadratic limit | response_series, exact toy | d=Wsecond/2 |
| 비영 A 보정 누락 | A=1 exact toy 및 누락 대조 | T30.47–49, exact numerator groups | 작은 물리 A의 검출력 한계 공개 |
| 경로 독립성 과장 | 실제 소스/공유 입력 읽기 | NUMERICS_DESIGN, PROVENANCE, owner review | 구현 경로 차이, NONBLIND |
| 사후 tolerance 변경 | 입력·코드·protocol 먼저 동결 | PREEXECUTION_FROZEN, EXECUTION |14payload 무변경,56/56 |
| 불완전한 실행 closure | manifest 원경로 포함15파일 복원 | REPLAY_RECEIPT 전후 identity | rawbyte/JSON 동일,같은host/Python |
| 수치/이론/물리 승격 혼동 | claim ledger와 별도 reviewer | CLAIM_LEDGER, DECISION_REVIEW | 실제 final authority별도 |
| 과거·metadata 실행을 새physics로 집계 | 실제 main/counter/역할 기록 | EXECUTION_LEDGER,raw,provenance | first1+replay1,새physical0 |

384개 내부 비교 성분과17개 identity멤버를56개 그룹의 의미와 혼동하지 않는다. 과학 first/replay failure0. 문서·그림·수집의 metadata 실패는 원기록과 해결을 보존한다.
