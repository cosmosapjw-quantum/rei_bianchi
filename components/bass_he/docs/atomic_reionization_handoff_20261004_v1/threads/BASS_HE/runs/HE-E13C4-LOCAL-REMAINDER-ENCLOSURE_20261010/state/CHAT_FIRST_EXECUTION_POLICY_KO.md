# Chat-first 코드 작성 / Codex cloud 점검·수정·실행 계약

사용자 승인일: 2026-09-28. 이 계약은 BASS_HE의 이후 handoff 기본값이다. 다른 저장소나 사용자 전역 설정을 변경했다고 주장하지 않는다.

## 책임 분리

ChatGPT 연구 스레드에서 수학·물리 정의, 설계, 실제 코드 수정, 관련 테스트, 작은 수치 검산, 실행 계약 및 패키징을 마친다. 코드는 게시 전에 여기에서 가능한 범위까지 실행하고, exact file identity·실행 증거와 함께 GitHub에 올린다. 클라우드에 미완성 설계를 넘겨 처음부터 구현하도록 하지 않는다.

클라우드 Codex는 전달된 commit/tree와 변경분을 읽고, host 환경·dependency·입력·명령을 점검하고, 필요한 최소 수정과 승인된 실행에 집중한다. 이미 설명된 이론·문헌·설계를 매번 재작성하거나 같은 checkpoint를 반복 감사하지 않는다. 코드를 읽기 전에 현재 상태를 추정하지 않는다.

최소 수정이란 호스트 경로·dependency·CLI·작은 실행 경계 오류를 재현한 뒤, 영향 범위를 고정하고 한 원인에 대해 한 번의 수정/집중검사를 수행하는 것이다. 기본 branch의 정의·허용오차·certificate policy·수치 알고리즘을 바꾸어야 하거나 다른 원인이 이어지면 증거를 보존해 이 연구 스레드로 반환한다. 비용 절감 때문에 gate를 생략하거나 실패를 숨기지 않는다.

독립 과학 검수는 별도 역할이다. 코드 작성자나 실행자가 스스로 independent review를 닫지 않는다. 작업자 수를 늘리는 것은 기본값이 아니다.

## 검증 예산

이전 PASS는 exact dependency와 입력/환경 계약이 변하지 않으면 재사용 근거를 기록한다. 전체 suite를 매 handoff마다 반복하지 않는다. 새 코드의 focused tests는 여기서 실행한다. 클라우드 환경이 바뀌면 같은 작은 scoped 검사를 한 번 실행하고 새 host 결과로 기록한다. 필요한 full scientific replay는 해당 승인 node에만 수행한다.

업로드는 ACK·object identity·size/checksum으로 선택적 확인하고, 기존 성공한 업로드를 재시도하지 않는다. 실제 복원검사 없이 RESTORE_VERIFIED라고 하지 않는다.

## 이번 전달 범위

`evaluate_r2.py`의 연구용 입출력과 상태 보고만 수정했다. `prepared_io.py`와 입력 manifest, 새 회귀 테스트를 추가했다. `error_envelopes.py`, R1의 spectral traces, production `src/`, cloud runner, numerical tolerance는 그대로다.

1. `--verify-only`는 표준 라이브러리만 사용하며 입력 7개를 고정 SHA256/크기로 확인한다. NumPy/SymPy import, 저장 trace 분석, spectral solve, native/cloud job, pytest는 실행하지 않는다.
2. 실제 분석을 요청하면 검증한 bytes를 그대로 사용한다. 검증 뒤 파일을 다시 읽어 다른 payload를 소비하지 않는다.
3. `--out`은 새 경로여야 한다. 기존 파일/심볼릭 링크는 계산 전에 거부하고, 완성된 JSON만 file-fsync 후 create-only atomic link, directory-fsync로 게시한다. 실패 시 기존 결과를 덮어쓰는 fallback은 없다.
4. 이 명령은 pytest를 실행하지 않으므로 `tests.status=NOT_RUN_BY_THIS_COMMAND`, counts=null을 기록한다. 실제 pytest 수는 별도 JUnit/명령로그가 소유한다. 과거 12-test 기록은 삭제하거나 허위로 재분류하지 않는다.

이번 변경은 연구 adapter의 실행·기록 개선이지 common-contour production 승격이 아니다. CODE-I02의 정상 cloud resume-004와 CR exactly-once F1-R2는 재실행하지 않는다.

scientific_PROMOTE=HOLD; Eq55=NOT_RUN; continuum_ionization=NOT_ADMITTED.
