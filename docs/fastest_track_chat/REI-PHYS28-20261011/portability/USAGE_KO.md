# PHYS28 별도 경로 재현

이 runner의 목적은 PHYS28의 첫 계산에 사용한 코드·고정 입력을 새 경로로 복원하고 같은 새 프로그램을 한 번 실행했을 때 결과의 바이트 및 JSON 내용이 같은지 확인하는 것이다. 같은 알고리즘과 입력을 쓰므로 독립 물리 검증 credit은 0이다. PHYS19–27의 프로그램을 실행하거나 새로운 물리 영점을 탐색하지 않는다.

## 경로와 실행

`repro.py`는 Python 표준 라이브러리만 사용한다. 먼저 외부 `NOTE_KO.md` 또는 상위 최종 산출물의 manifest에서 `PHYS28_PORTABLE_STAGE.zip`의 실제 SHA256을 확인한다. 복원할 목적지와 기록 prefix는 존재하지 않는 새 경로여야 한다. 기록 prefix는 복원 트리 밖에 둔다. 기존 목적지와 기록 파일을 덮어쓰지 않는다.

```bash
python3 -B portability/repro.py \
  --archive portability/PHYS28_PORTABLE_STAGE.zip \
  --archive-sha256 '<관측한 ZIP SHA256>' \
  --destination '/absolute/new_restore_directory' \
  --record-prefix '/absolute/new_record_prefix' \
  --verify-only
```

`--verify-only`는 ZIP 전체의 파일 목록·SHA256·크기와 복원된 파일을 검사하며 과학 프로그램을 호출하지 않는다. 새 경로에서 실행하려면 위 명령의 모드를 `--replay`로 바꾼다. 검증에 사용한 기존 복원 경로를 재사용하지 않고 또 다른 새 목적지를 지정해야 한다. 이 연구 루프에서 이미 사용한 replay 예산을 이 사용법이 갱신하거나 추가하지 않는다.

`--replay`는 복원 트리의 `contributions/numerics/small_width_sensitivity.py --output <prefix>_RESULT.json`만 실행한다. 새 프로그램의 `ROOT`는 해당 복원 트리를 가리킨다. 하위 프로세스 시간 상한은 30초이며 실패·timeout에 대한 자동 재시도는 없다. `-B`와 `PYTHONDONTWRITEBYTECODE=1`을 적용하고 원 코드·입력을 수정하지 않는다.

## 실제 기록

`--replay`는 `<prefix>_INVOCATION.json`, `<prefix>_STDOUT.txt`, `<prefix>_STDERR.txt`, `<prefix>_RESULT.json`, `<prefix>_RECEIPT.json`을 생성한다. 실행이 결과 파일을 만들지 못했으면 그 부재와 실제 exit 또는 timeout을 기록한다. receipt는 UTC 시작·종료, wall seconds, 명령·환경, 입력과 출력 identity, 복원 전후 검사, 첫 결과와의 바이트 및 parsed JSON 비교, 실제 호출 ledger를 분리한다.

first result 안의 모든 유한 점 검산이 다시 PASS하더라도 정확한 정리·전체 에너지 구간·J나 원자율의 불확실성·native 동등성·물리 emitter 승인을 추가로 증명하지 않는다. 다른 Python/Decimal 구현에서도 바이트 동일함을 보장한다는 주장을 하지 않는다. 현재 관측 환경과 다른 실행은 그 자체의 환경·횟수·실패를 새로 기록해야 한다.

Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED, production source/default/runtime changes 0을 보존한다.
