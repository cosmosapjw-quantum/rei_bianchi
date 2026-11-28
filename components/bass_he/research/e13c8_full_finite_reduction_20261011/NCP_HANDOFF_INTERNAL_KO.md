# BASS_HE E13C8 — NCP local Codex handoff

현재 상태를 아래와 같이 적용하라. 이번 인계는 완료된 중량 작업을 새 연구 상태와
연결하는 인계이며, **지금 시작할 새 NCP 계산은 0개**다.

## 확인된 완료 상태

- E13C7 OFF N1024/P60의 2,331경로·4,662구간·9,547,776 coefficient evaluations는
  실제 64개 computing rank로 완료되었다. 재사용·미완료·자동 재시도 0.
- 반환 archive는 124,152,692 bytes,
  SHA-256 `a7a0fd6e58a88140071a1b623897efbd35748c86c4eda6956a937171eefe6c8f`이다.
- Execution lock:
  `c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4`.
- Source lock:
  `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`.
- Ordered path collection semantic:
  `00b2d0133fb71f82d4994d340ca0a342bf8490c4bde2b24ab47ae84645ac8de4`.
- ChatGPT에서 전체 Fraction 합산·34개 직접 predecessor bridge·모든 raw nesting·
  독립 원시 경로 검토·CSV parity를 끝냈다. 합산 semantic:
  `d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1`.
- 최종 과학 결정: `PROMOTE_SCOPED_FULL_FINITE_CAPTURED_OFF`.
  독립 결정 SHA:
  `d555458ad40b92005d6968897ce2dd21e5bbb91acbc77a58029e19d66f8ed551`.

## 이번 NCP 행동

`NCP_ACTION.json`의 `new_heavy_tasks=0`을 적용하라. 기존 N1024 배치, global
Fraction 합산, 예전 budget/full-first2/N512, benchmark, P80 sweep, 전체 N2048을
시작하지 말라. 여기서 끝난 경량 분석·이론·리뷰를 NCP에서 다시 할 필요가 없다.
이미 보존된 완료 결과와 과거 실패 영수증은 각각 그대로 유지하라.

별도 host 관측·파일 검증을 이번 인계에서 새로 요구하지 않는다. 이미 알고 있는
상태를 인지하고 다음과 같이 답하면 된다. 수신 확인 외에 명령을 실행한 것처럼
보고하지 말라.

```text
ACK_E13C8_FULL_FINITE_ADMITTED
new_heavy_tasks = 0
new_scientific_invocations = 0
new_MPI_invocations = 0
completed_E13C7_paths = 2331
next_action = WAIT_FOR_A_NEW_SCIENTIFICALLY_JUSTIFIED_HEAVY_EXECUTION_CONTRACT
```

## 다음 heavy 계약이 생기는 조건

다음 signed Volterra 보정은 아직 구현·수치 적분하지 않은 방법 후보다. ChatGPT가
먼저 계산 그래프, incoming uncertainty, species moments, signed seam, precision·
resolution control을 포함한 짧은 pilot을 완료한다. 이어 독립 검토를 받고 실제
원시 구간 개선과 경로별 wall/RSS를 보고한다. 필요한 정확도 목표와 남은 작업량이
새 중량 실행을 정당화할 때 별도의 immutable source/execution lock과 정확한
work list를 발행한다. 이 문서를 미래 NCP 실행에 대한 포괄적 허가로 사용하지 말라.

그때는 실제 가용 CPU·RAM을 확인해 최대 64개 계산 rank, thread 1, 고유 CPU
고정을 사용하고 이미 완료된 같은 작업은 제외한다. 실제 CPU-time·메모리 계측은
그 새 과학 실행에 붙인다. 이미 끝난 배치를 계측 목적으로 다시 실행하지 않는다.

## 백업만 복구해야 할 경우

현재 인계에는 복구 실행도 요구하지 않는다. 나중에 작업 파일이 없는 환경에서
복구가 필요하면 외부 인계문의 검증된 전체 ZIP 또는 조각/manifest/복구 kit를
사용하라. 입력 파일의 별도 첨부는 필요 없다.

`code/restore_transfer.py`는 외부 manifest SHA와 원본 bytes/SHA를 필수로
검사한다. 다운로드 반환명이 `.bin` 등으로 바뀌어도 같은 bytes를 식별하며,
조각이 빠지면 새 `FIRST_FAILURE.json`을 남긴다. 복구·파일 확인은 새 과학 실행과
구분한다. 원본 입력과 실제 반환은 `dependencies/E13C7_INPUT.zip`,
`dependencies/E13C7_NCP_RETURN.zip`에 포함된다.

## 주장 범위

채택한 것은 같은 고정 캡처 OFF 유한 문제의 포함 구간이다. Physical,
continuum, production, receiver는 HOLD다. Provider attestation은 NOT_ASSERTED,
실제 CPU 이용률은 NOT_MEASURED, 동일 작업 직렬 대비 speedup은 NOT_ESTABLISHED다.
Rank wall의 균형이나 개별 최대 RSS의 합을 이 지표로 바꾸어 보고하지 말라.

이전 전송 실패의 NOT_RUN은 당시 실패 기록이다. 새 검증된 완료 상태로 연구를
재개하되 그 실패 영수증을 덮어쓰지 말라.
