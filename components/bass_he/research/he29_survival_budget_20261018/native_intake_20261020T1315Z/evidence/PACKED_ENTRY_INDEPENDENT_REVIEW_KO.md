# 새 packed entry 독립 검토(C9)

## 판정

**PASS_SCOPED — 새 wrapper와 NCP 인계에서 조치가 필요한 중대·경미 finding은 모두 0건이다.** 검토 범위는 이번 외부 entry 연결, 고정 source/import identity, 출력 경계, 실행 인계다. 앞서 완료한 네 native pair의 과학 검토나 기존 watchdog 검증을 반복하지 않았다.

## 연결과 실행 계약

새 `packed_entry.py`는 SHA를 확인한 a5 target의 `run_process` 이름만 ed5 `run_process_group`과 원래 execution helper로 연결한다. 실제 고정 Git 소스 네 파일을 읽어 wrapper의 SHA와 **4/4 일치**를 확인했다. ed5 함수의 세 위치 인자와 a5 두 target의 실제 호출 형태도 맞는다. target의 원래 `__file__`, sibling import 경로, worker argv와 원래 worker 소스는 유지된다.

고정 a5/ed5 HEAD, Git 최상위 경로와 tracked clean 상태, source의 경로·symlink·SHA 검사가 import보다 먼저 수행된다. 공개된 build/preflight/canary 인자만 허용하고 worker 직접 호출, 추가 case/물리 인자, 잘못된 pin과 비유한 예산을 거부한다. 경계와 target 출력은 서로 겹칠 수 없고 두 의존 checkout 밖에 있어야 한다. 이미 있는 출력은 덮어쓰지 않으며 예외와 비영 종료를 실패 영수증 뒤에 전파한다. 성공 영수증의 의미도 target 반환으로 한정한다.

wrapper가 a5/ed5의 기존 bytes를 수정하지 않는다. 기존 target이 원래 full state와 19개 ledger, full-state norm, 초기 상태, source/input/parent/binary/runtime/bridge qualification과 수치 gate를 그대로 담당한다. 새 solver나 수치 변환은 없다. 정확한 bridge를 재사용하거나 원래 builder를 호출한 다음 검증 DATA 22개를 복원하는 순서도 기존 clean-source 조건에 맞는다. a5의 manifest 수리와 복원기의 `--root` 지원은 실제 source read로 확인했으며 baseline1569용 patch를 다시 적용하지 않는다.

## 재사용한 검증

| 근거 | 이번 검토의 사용 범위 |
|---|---|
| 새 wrapper 첫 9개 test method PASS | 제조한 Git 응답·target·watchdog으로 새 연결과 경계를 검사한 원 실행 기록을 재사용 |
| 인계 bash 4개 block 구문 PASS | 명령을 실행하지 않은 원 구문 검사 기록을 재사용 |
| 고정 Git dependency 4개 실제 readback | 이번 독립 검토에서 원문·signature·import·호출 계약과 SHA 확인 |

리뷰어의 신규 test 실행, 기존 test 재실행, analyzer CLI, native 실행, build, NCP 제출·시작, RDC 호출은 모두 **0**이다. 제조한 9개 검사 결과를 실제 native 실행이나 기존 watchdog의 새 검증으로 확대 해석하지 않는다.

## 복원과 남은 조건

초기 경로 읽기에서 환경 전환에 따른 ENOENT가 관측됐다. 저자는 보존된 도구 기록에서 wrapper·test·인계 원문을 복원했고 세 원래 SHA가 일치했다. 첫 test와 구문 영수증도 재실행 없이 복원했다. 이 검토는 복원된 정확한 입력을 사용했다. `PINNED_DEPENDENCY_READBACK.json`은 리뷰어의 새 Git readback이며 과거 산출물 복원으로 분류하지 않는다.

네 reference pair의 기존 admission은 재사용한다. 다음 실제 실행은 게시된 정확한 wrapper pin을 사용하고, 허용된 NCP 실행자가 현재 프로세스·저장 결과를 먼저 관측하여 단일 r4/table512 packed canary가 여전히 필요한지 확인한 뒤 진행해야 한다. 현재 실행 상태가 미관측이면 HOLD다. 원 cohort와 binary/qualification, thread1, 900초 canary와 원 preflight gate를 유지하며 자동 확장은 없다. 아직 이 검토에서 native HE29 성능을 측정하지 않았다.

상세 식별자·판정 행렬·원 검사 영수증은 `PACKED_ENTRY_INDEPENDENT_REVIEW.json`에 있다. 이 판정은 새 연결에 대한 독립 정적 검토의 마감이며 실제 canary 완료 판정은 이후 반환 bytes와 원 gate 결과에 달려 있다.
