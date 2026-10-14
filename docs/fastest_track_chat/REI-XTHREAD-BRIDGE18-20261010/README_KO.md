# BRIDGE18: 원 V2 읽기 전용 사전검증과 격리된 V3-sidecar 원형

2026-10-10 KST. READ_ONLY_V2_PREFLIGHT_AND_ISOLATED_V3_SIDECAR_VERIFIED__OWNER_ADOPTION_OPEN.

BRIDGE17 원문에 남은 pending append-before-decode, valid-hex compensation tamper, NaN metrics 문제를 대상으로 외부 opt-in guard를 구현했다. 원 paired_history/paired_runtime/체크포인트/물리계수는 변경하지 않았다. 실제 T2_BI pilot accepted3/rejected0, time937500000s, offset35578, 4224 photon slots를 입력으로 사용했다. V2 bytes와 보상합6을 그대로 보존하며 V3는 신규 native 상태 포맷이 아니라 별도 해시 sidecar이다.

완료: 27단위시험(4실제 assertion RED/GREEN,23tests-after), 독립13469 f64 bit pattern/26source piece 검사, 109바이트 raw의110prefix×old/new checkpoint×old/new sidecar=440상태, 실제7개SIGKILL cut의 복구 및 중복방지. 최종 새폴더5명령 모두exit0. 개발 포함 실제SIGKILL20회, 고유cut7개. 전이는 실제 pilot에 제조한 거절 기록 한 건이며 물리 solver 실행이 아니다. 새로운 Rust/native/ODE/root/Cargo/부모 과학계산은0회.

중요 경계: SHA256은 독립적으로 신뢰한 receipt digest와 대조해야 하며 self-hash는 인증이 아니다. 원 native가 guard를 우회하지 못하도록 설치한 작업이 아니다. exclusive_owner=True는 외부 전제이지 다른 writer 배제의 증명이 아니다. 현재 파일당32MiB상한, checkpoint8MiB상한으로 긴 F08 GB로그는 지원하지 않는다. SIGKILL시험은 정전/장치캐시/I/O오류의 포괄적 인증이 아니다.

새 prototype에서도 stale temp conflict를 log append 후 검출하던 오류가 있었다. 전후 bytes 불변 assertion이 실제 실패했고, 모든 temp검사를 첫 쓰기 앞으로 옮긴 뒤 동일시험이 통과했다. 원 코드 오류로 포장하지 않는다.

Full source, tests, exact inputs, failures and final evidence: REI_XTHREAD_BRIDGE18_20261010.zip (210300 bytes,78 entries,77 payload hashes), SHA256 fb1e55b9f0fad509750084475d766cab35042496d0e24c8ef897dfd4d17032dc. Git에는 요약/계약/인계만 있으며 완전 실행패키지는 ZIP이다. 오프라인 python -B reproduce.py --verify-only; 실제 focused prototype 재현은 --output NEW_DIRECTORY.

Native 채택은 별도 owner 통합 과제로 남긴다. 다음 과학 후보는 실제 coupled birth-time response derivative bound이며 frozen-opacity 작은 오차를 이식하지 않는다. [160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD와 원 local/width 기준 불변.
