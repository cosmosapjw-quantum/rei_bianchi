# 구현 검증 runner 독립 검토

판정: **PASS_SCOPED** — 아래 세 완료 기록의 결과와 측정 구간에 한정한다. 전 과정의 CPU·wall·메모리 상한 준수나 물리 공급자 완성을 인증하는 판정은 아니다.

검토자: `/root/species_sources`. 검토 방식: `run_validation.py`, `VALIDATION_CONTRACT.json`, `evidence/validation/RESOURCE_LEDGER.json` 및 세 `stderr.txt`의 정적 대조. 자신의 species 구현 코드는 이 검토에서 제외했다. 새 테스트, 과학 실행, HE101 실행, 과거 suite 재실행은 수행하지 않았다.

## 관측된 실행 결과

| 완료 기록 | 테스트 | 반환 코드 | child CPU (s) | 해당 구간 parent CPU (s) | 해당 구간 wall (s) |
|---|---:|---:|---:|---:|---:|
| `01_exchange` | 13 PASS | 0 | 0.053907 | 0.0009599669999999991 | 0.05446167999980389 |
| `02_pair_source` | 5 PASS | 0 | 0.055496 | 0.0009870569999999995 | 0.05608908599970164 |
| `03_species` | 12 PASS | 0 | 0.06135999999999999 | 0.0009593769999999974 | 0.061955021003086586 |

ledger의 누계는 **CPU 0.17366940099999997 s / wall 0.17250578700259211 s**이다. 세 항목 모두 `timed_out=false`, `launch_error=null`, `cumulative_cap_overshoot=false`이며, 서로 다른 scope의 첫 시도다. `repair_used=0`, `HE101_START_count=0`, `historical_suite_replay_count=0`, `physical_campaign_START_count=0`이라는 기록과 모순되는 증거는 이 검토 범위에서 발견하지 못했다. 이 카운터들은 관측 범위를 나타내며 외부 활동 전체를 감시하는 장치라는 뜻은 아니다.

## 자원 측정의 정확한 경계

runner는 source 해시 작성, START 기록 저장, 환경변수 구성 이후에 `time.process_time()`, `time.monotonic()` 및 `RUSAGE_CHILDREN`의 기준값을 읽는다. 이후 `Popen`부터 child 회수 및 종료 후 자원값 읽기까지를 측정한다. **child Python interpreter 시작 비용은 이 구간 안에 있다. parent runner의 interpreter 시작 비용은 밖에 있다.**

측정에서 제외되는 부분은 parent interpreter·import 시작, 계약 및 기존 ledger 읽기, 디렉터리 생성, 입력 해시, START/ledger의 사전 쓰기와 fsync, 환경변수 구성, 그리고 측정 종료 후 stdout/stderr 저장, 로그 해시, FINISH/ledger 쓰기와 fsync 및 결과 출력이다. 서로 다른 runner 호출 사이의 대기시간도 합산 wall에 포함되지 않는다. source 획득·모델/원격 IO·별도 inventory build·검토·게시·백업 비용 역시 이 숫자로 측정한 것이 아니다. 이들의 미측정 비용은 **0으로 간주할 수 없다**.

따라서 정확한 결과 표현은 “세 child 실행과 그 실행 구간의 parent 비용을 합한 측정치가 별도 구현 검증 예산 CPU 8 s / wall 30 s 이내였음”이다. “전체 작업이 CPU 8 s / wall 30 s 이내에서 끝났음”은 이 증거로 뒷받침되지 않는다. ledger의 `end_to_end_cap_claimed=false` 및 `preparation_remote_model_IO_cost=UNKNOWN_NOT_ZERO; outside measured test envelope`는 이 구분과 일치한다. 계약의 `cap_scope`에 적힌 “parent test runner”는 이 문단의 **측정 구간 내 parent 비용**으로 읽어야 한다.

256 MiB는 child에 설정하는 `RLIMIT_AS` 값으로 확인된다. 이것은 전체 작업의 실측 peak RSS나 parent까지 합한 메모리 사용량 보고가 아니다. CPU의 child 정수 초 제한과 누적 overshoot 판정은 별개다. 후자는 측정 종료 후 판정하므로 runner 전체의 연속적인 hard cap을 보증하는 장치로 기술하면 안 된다. 현재 세 실행은 모두 남은 예산이 충분한 상태에서 시작했고 실제 측정치가 상한을 넘지 않았으므로, 이 제한은 이번 결과를 FAIL로 바꿀 근거가 되지 않는다.

## 실패 보존과 재실행 통제

현재 코드는 child 시작 전에 START를 ledger와 독립 START 파일에 저장한다. 완료 시 반환 코드·timeout·launch error·stdout/stderr 해시와 CPU/wall을 기록한다. 미완료 START가 하나라도 남으면 다음 실행을 차단한다. 같은 scope를 다시 실행하려면 이유 문자열과 남은 공통 repair reserve가 필요하고, 이미 소모한 누계 예산에서 차감한 잔여량을 사용한다. 이번 세 기록은 모두 첫 실행이며 repair가 소비되지 않았다. 기존 실패를 PASS로 덮어썼거나 예산을 초기화했다는 증거는 없다.

이유 문자열의 과학적 타당성이나 changed-code 진단은 문자열 존재만으로 자동 심사되지 않는다. 이는 controller의 진단 책임이며, 이번에는 반복 실행 자체가 없어 미충족 gate가 발생하지 않았다. `main_run_count=1`은 세 scope를 한 번씩 수행한 이번 main pass의 단위로 보고해야 한다. 실제 child 시작 횟수는 **3회**다.

## 실행 증거와 현재 runner 버전의 구분

현재 runner에는 `--test-name`, `selected_tests`, `command_cwd` 처리가 있다. 최초 세 기록에는 `selected_tests`와 `command_cwd` 필드가 없으며, 세 command는 모두 discovery 실행이다. 또한 기록의 `source_sha256`은 scope와 공통 sources를 묶고 runner 및 계약 자체는 포함하지 않는다. 따라서 이 세 PASS를 현재 runner의 추가 선택 실행 분기를 실제로 시험했다는 증거로 확대할 수 없다. 이번 검토는 그 분기의 정적 확인까지만 포함한다. 후속 변경/실행의 정체성은 별도 기록이나 최종 manifest로 보존해야 하며, 이 한계 때문에 완료된 세 suite를 재실행할 필요는 없다.

## 종결 판단

관측된 30개 테스트 결과, 해당 실행 구간의 누계, 실패 보존 및 이번 첫 실행들의 재실행 통제에 대해 **PASS_SCOPED**를 부여한다. 원본 runner·계약·ledger는 수정하지 않았다. 수치의 범위를 위와 같이 명시하면 이 검토로 요구되는 추가 코드 수정이나 재실행은 없다. HE101의 C8 미완료, 기존 실패와 소진 예산, 물리 캠페인 미할당 상태에 대한 재판정은 하지 않는다.
