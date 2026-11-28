# BASS_HE E13C5 full finite budget

이 패키지는 `HE_E13C5_FULL_FINITE_BUDGET_AND_COMPLEMENT01`의 연구 결과, 고정 원자료, exact reducer 및 NCP 전달 계약을 함께 담고 있다.

1. 결과와 판단은 `REPORT_KO.md`를 읽는다.
2. 실행을 맡은 local Codex에는 `NCP_LOCAL_CODEX_HANDOFF_KO.md` 전체를 전달한다.
3. 단일 실행기는 `code/ncp_budget_continue.py`이며, `--execute`일 때 저장된 결과의 exact budget child만 한 번 실행한다.
4. `dependencies/`의 두 원 scientific archive가 필요한 입력을 모두 제공한다.
5. `FILE_MANIFEST.json`은 내부 payload의 크기와 SHA를 기록한다. 외부 NCP_READY의 `CORE_IDENTITY.json`이 이 scientific ZIP의 정확한 identity와 publication receipt를 연결한다.

PR20 전체 finite cover와 기존 두 OFF N512 결과는 완료되어 있다. 현재 분석은 전체 photon 폭 개선이 1.430233307 ppm, 열 폭 개선이 1.059316287 ppm임을 보여준다. 새 물리 solver나 실제 NCP 실행은 이 Chat 작업에서 수행하지 않았다.

독립 검토 결과와 실제 runtime evidence는 함께 보존되어 있으며, 원 복구 파일의 tail 누락 및 필수 null-field 검증 문제의 최초 증거와 수정도 포함한다.

