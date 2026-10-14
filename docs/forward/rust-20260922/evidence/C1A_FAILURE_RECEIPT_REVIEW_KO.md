# C1a: local 검증 인계의 실패 기록 수리

## 범위와 판정

Parent: `dd6253912645a2f3a245f7b68413f8c51f15eec5`.
이 변경은 `scripts/check_rust_forward_parity.py`의 실행/receipt 경로만 수리한다. 원 Rust kernel, Cargo pair, 84개 함수 fixture, 두 원 Python reference, source lock, parity policy는 변경하지 않았다. scientific state와 rec physical lock도 변경하지 않는다. Rust build/parity는 여전히 local Codex 담당이다.

Ruling: local 검증 결과가 아직 해당 branch에 없고, C1 checker의 실제 오류 기록 결함이 재현되어 최소 follow-up C1a를 게시한다. 이것을 local C2 완료나 새로운 연구단계로 세지 않는다. 이후 local은 최신 후보에서 검증한다.

## 재현과 원인

기존 main은 check_contract/execute가 정상 반환한 뒤에만 --output을 열었다. 따라서 reference import 실패, child nonzero exit, timeout 또는 malformed reply로 예외가 나면 요청한 JSON receipt가 만들어지지 않았다. output이 이미 존재할 때도 불필요하게 검증부터 진행했다.

기존 execute는 subprocess.run이 반환한 뒤에 stdout/stderr를 출력했다. timeout은 그 이전에 발생해 TimeoutExpired의 부분 stdout/stderr가 사라졌다. 정상 반환된 배치의 로그도 JSON에 포함되지 않았고, per-case mismatch에서는 실제 reference가 failure 행에 남지 않았다.

명시적 test double을 사용한 10개 Python 회귀 검사에서 C1은 8 failures + 1 error, exit 1; 같은 검사에 수정본은 10/10, exit 0이었다. 해당 테스트는 Rust 또는 JAX를 실행하지 않는다. 모의 child의 exit 101/timeout 및 모의 [2,6]/[2,7]은 실제 과학 실행 결과가 아니다. 별도의 2개 CPython child smoke에서는 실제 Python subprocess의 byte I/O와 nonzero exit 보존을 확인했다. 이것도 Rust 검증이 아니다.

## 수리

- 출력 경로를 배타적으로 먼저 열어 기존 evidence와 충돌하면 작업 전에 종료한다.
- controlled failure에도 소유한 새 JSON에 phase/error와 확보된 배치 기록을 저장한다.
- 각 child의 command/cwd/input SHA/timeout/status/실제 returncode를 남긴다. timeout 또는 launch failure에 exit 값을 지어내지 않는다.
- bytes를 먼저 회수하고 base64 원본과 가독용 문자열을 함께 보존한다. protocol decode 실패도 원로그를 제거하지 않는다.
- 두 번째 배치가 실패해도 첫 번째 배치 기록은 유지한다. mismatch에는 reference/forward/reverse 출력을 함께 남긴다.
- actual parity 실행 환경에는 JAX version뿐 아니라 x64/backend를 기록한다. 여기서 JAX를 실행했다는 뜻은 아니다.
- 추가 회귀 test 하나를 CODE_INPUT_MANIFEST에 포함하고 기존 코드 입력은 변경된 checker의 hash만 갱신했다. RTOL=5e-13, ATOL=0은 그대로다.

## 검토와 한계

직접 검토이며 독립 reviewer 수용으로 부르지 않는다. 자동 검사는 실패 기록과 계약 검사만 지지한다. f64 오차 정책, source ownership, 단위, 네 source site의 물리 의미에는 변경이 없다.

checker 자체의 SIGKILL, 전원 중단, 디스크 오류에는 완전한 JSON을 보장하지 않는다. 따라서 local handoff는 stdout/stderr와 exit를 별도 파일로 보존한다. source tree에는 원래 scientific PASS/HOLD와 모든 port parity 미실행 상태를 유지했다.

종료: 이 최소 기록 수리 뒤 local build/parity를 실행한다. 기록 검사를 추가 연구 루프로 반복하지 않는다.
