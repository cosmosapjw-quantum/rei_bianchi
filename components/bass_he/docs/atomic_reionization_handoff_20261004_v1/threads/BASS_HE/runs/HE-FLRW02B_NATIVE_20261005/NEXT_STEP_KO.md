# HE-FLRW02B native 반환 수신

HE-FLRW02B_NATIVE_EXECUTION은 계약된 consumer3dceea7 전체 crate에서 두 native test를 통과했다. 준비 코드/test/GOLDEN/tolerance를 바꾸지 않았다. compiler 부재나 mixed runtime 결과 부재를 다시 blocker로 쓰지 않는다.

1. RETURN.json, EXECUTION_CONTRACT.json, evidence/NATIVE_COMMAND.json, NATIVE_RESULTS.json과 로그를 읽고 archive/manifest/test/GOLDEN identity를 확인한다.
2. 소비기는 현재 관련 source blob와 exact4개 의존성을 비교한다. 같으면 고정-input native evidence를 수신한다. 현재 lib/새 모듈 전체 build는 이 결과가 인증하지 않는다. 실제 live build-context 채택이 필요할 때만 같은 두 시험을 실행한다.
3. HE-F2 조건부 local-RHS 수락과 RCT-STEP01 대기, HE-F3/REI-F09, physical HOLD는 별도 유지한다. 이 광흡수 시험으로 RCT time stepper나 history를 닫지 않는다.

재현: bash run_native.sh /path/to/rust-1.94.1-prefix
명령은 source manifest를 먼저 확인하고 오프라인 cargo로 지정된 두 시험만 실행한다. 원 evidence를 덮어쓰지 않고 별도 replay 디렉터리에 출력한다. source/GOLDEN/허용오차 불일치 때 자동수정하지 않는다.
