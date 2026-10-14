# 이번 게시 범위와 후속 PR 계획

이번 변경은 `docs/research_sync/REI-REC-BASS-SYNC03-20261007` 아래의 독립 연구 패킷이다. 기존 PR83에는 실행 코드·과학 반환·manifest·DAG를 추가하고 PR84에는 IGM에 맞춘 return pointer를 추가한다. BASS_HE17, bass_cr23, WU088_HH33, REC81, BASS132 및 현재 native BASS133에는 각 source/owner 범위에 맞춘 handoff를 추가한다. 기존 body는 보존하고 최신 cross-repo 요약을 추가한다. Merge, force push, main 변경은 없다. Moving branch update는 fresh head lease를 사용한다.

문제: 완료된 F08 proper-ne 공급물이 BASS에 실제 수신되지 않았고, 오래된 상태 문서들이 F08/CR/HH 진행도를 잘못 설명했다.

변경: exact BASS source 모듈의 bounded receiver, 독립 Decimal 및 rational 검산, 공급자 조건부 box의 positive quadrature 전파, 세 해상도 관측량 그림, 최신 스레드 상태와 병렬 DAG를 게시한다.

동작: 기존 baseline과 solver의 결과를 바꾸지 않고 실제 데이터에서 검증 가능한 finite-interval observable을 얻는다. Physical/continuum admission은 그대로 별도 gate다.

검증: 6 histories/112000 native cells; Decimal70 784054 checks; 독립 T2 rational integrals 및 box/subtraction; analytic zero/constant density; SHA/source module identity; 그림 시각 점검. 정확한 결과는 evidence에 저장한다. 두 runtime 실패도 보존한다.

후속 PR은 P-IGM-EXPORT, P-OBSERVER-SURFACE, P-OPTIONAL-NE/P-TIME-ERROR 계약처럼 독립된 write boundary로 나눈다. 기존 owner의 HE RCT03 receiver, CR import, HH ON06, REI transport/SPEC, BASS133를 동일 PR에서 대신 구현하지 않는다.
