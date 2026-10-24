# Stock 실행 전 identity 확인

원본 stock leaf의 raw/와 raw/attempt.json은 존재하지 않았다. 동결 8개 파일은 기존 coding report·독립 정적 심사의 SHA256 및 크기와 일치하며, 전체 leaf 16개 파일을 새 root에 바이트 그대로 복사했다. 이전 ROOT_GO 또는 attempt는 복사하지 않았다.

실행 위치에 영향을 주는 runner 경로는 __file__에서 구한 HERE다. proposal·source·fixture 읽기, child 명령과 cwd, raw 쓰기는 모두 HERE를 사용한다. 기존 PROPOSED_EXECUTION.json의 command/cwd 및 계약·review의 절대경로는 역사적 준비 metadata이며 runner의 실제 실행 경로를 선택하지 않는다. 따라서 새 root 경로를 실제 실행 위치로 채택하려면 새 AUTHORIZATION_OVERLAY/ROOT_GO에 해당 명령과 위치를 명시하면 된다. 동결 파일을 수정할 필요는 없다는 정적 관찰이며, 현재 실행을 발행한 것은 아니다.

현재 import/compile/test/runner 실행은 모두 0이다. 별도 root GO와 Stage A 실제 백업을 기다린다. 기존 cap FAIL(초과 0.110448s), known partial CPU 10.238107s, whole L0 UNKNOWN_NOT_ZERO와 cumulative cap NOT_FROZEN을 유지한다.
