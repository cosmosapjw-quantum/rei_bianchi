# Compact RHS 전송: 승인된 단일 수정과 표적 검증

소유자의 `직접 수정·표적 검증 승인`을 적용했다. 기존 quota를 우회하지 않고 coordinator가 명시적 예외로 실행했다. 원래 무수정 30분 allocation을 재설정하지 않았으며 별도 180초 단위다.

Rust 서버에 RC 모드를 추가했다. 기존 R/P/D/S와 물리 `evaluate` 함수는 그대로다. RC는 이미 활성화된 cohort의 birth-encoded 상수를 복원하고 원 active_indices 값만 scatter한다. 구조적 제외 좌표를 임의 0으로 치환하지 않는다. 새 Python 사본은 같은 DOP853/rtol/atol/max_step/retry/600초/200000RHS 정책을 유지하며 compact RHS만 요청한다. `OBSERVED_DIFF.patch`에 전체 변경을 보존했다. production/native64 mesh는 변경하지 않았다.

기존 로컬 frozen rlib를 링크한 새 binary build는 exit0, 4.551259882초였다. NCP의 같은 경로를 찾는 첫 read-only ls는 exit2였고 retained artifact가 실제로 있는 로컬에서 진행했다. 이 실패도 보존했다. 별도 library 재빌드는 없다.

## 실제 검증

accepted event0/4/16/34와 기존 rejected event4/35의 총6쌍, helper RHS12회가 통과했다. 각 전체 입력 복원은 uint64-view bitwise 일치, 수락 상태의 선택된 formatted derivative는 문자열 일치, 두 실패 상태는 동일 오류 문자열이다. 원 trial 실패를 성공으로 바꾸지 않았다. 검증 command exit0, wall1.361335192초, CPU user0.436994/system0.077720초, waited-process peak RSS36440KiB, AS8GiB다. 새 trajectory/full solver run은0이다.

active34 한 쌍의 request+reply는 764340→235893bytes다. roundtrip은 0.091136154→0.079246102초였다. 원 모드를 먼저 실행한 단일 측정이므로 통계적 benchmark, 전체 solver ETA, NCP 가속률로 옮기지 않는다.

## 다음 전이

이 단위는 구현과 여섯 저장 상태 parity만 닫는다. 전체 solver에서의 수렴·성능과 독립 scientific admission은 NOT_ISSUED다. age64 첫 WALL_CAP, 원 provider32 trial rejection, native 공통mesh 제한, age/spectral/native-time 및 full EoR HOLD를 유지한다. 이 승인은 새 full solver 또는 mesh 수정 실행을 허가하지 않는다. 독립 reviewer가 복구되면 이 diff/raw 결과만 검토하고, 후속 bounded solver 측정을 새 계약으로 연결한다. 기존 공급자 검토는 반복하지 않는다.

Checkpoint PAUSED_RESUMABLE, GOAL_DONE=false.

## 전체 단위 시간 제한 초과

검증 계산은 시작 후109.333428초에 종료했다. 증거 정리 종료 당시3.25초가 남았으나 이후 Git staging/commit 및 closeout에서180초 전체 단위 한도를 넘겼다. 첫 사후 관측 경과시간은207.459747314초, 초과27.459748745초다. 전체 단위는 `HOLD_WHOLE_UNIT_WALL_CAP_AFTER_COMPLETED_PARITY`로 기록한다. 6쌍 parity 사실은 보존하지만 예산 준수 PASS나 과학 admission으로 승격하지 않는다. 이후 수치 계산/재시도는0이며 원시 BUILD.stderr의 EOF 공백 경고도 그대로 보존했다.
