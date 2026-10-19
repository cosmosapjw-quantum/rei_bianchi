# 독립 source 복원과 재현 증거

새 디렉터리에 최종 source·donor·계약을 복사하고 빈 Cargo target에서 시작했다. `RESTORED_INPUT_MANIFEST.sha256`는 그 복원 입력 123개 파일의 바이트 manifest다. 그중 code, donor 및 원 source 계약 120개 파일은 본 unit과 각각 SHA-256이 일치한다. 이 기록은 독립 source 복원과 fresh build의 증거이며, 최종 ZIP의 cloud raw-download round trip을 대신하지 않는다.

`initial_all/`에는 실제 Rust 209개 테스트, strict Clippy, release build, 동결 16개 사례, 첫 단계 CX WorkLimit 재현, 실행 전후 manifest 확인 로그가 있다. `native_comparison/`에는 같은 fresh build에서 실행한 native 6개 사례가 있다.

완료된 5개 이력의 160개 행에서 50개 필드를 비교하여 8,000개 cell이 문자열 수준에서 정확히 일치했다. 제외한 필드는 `wall_s`, `hits`, `misses`, `cache_size`이며, 나머지 필드는 모두 비교했다. CX 사례는 exit code 2, `RESOURCE_LIMIT_CX`, 데이터 행 0개라는 판정이 원 기록과 일치했다.

`FRESH_COMPARATOR_INITIAL_FAILURE.json`은 최초 비교기가 이 예상된 zero-byte CSV를 header 누락으로 거부한 감사 하네스 문제를 기록한다. JSON의 `RESOURCE_LIMIT_CX`, `rows=0`, `exit_code=2`가 모두 확인될 때만 빈 CSV를 허용하도록 비교기를 수정했다. 실제 native 계산과 원자료는 변경하지 않았다.

원 source와 증거 경로를 명시하여 `compare_fresh_outputs.py --help`의 계약으로 다시 비교할 수 있다. 전체 결과는 `FRESH_RESTORE_COMPARISON.json`에 있다.
