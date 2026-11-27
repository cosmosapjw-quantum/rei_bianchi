# HE29 packed canary 연결 검토

네 기준해 반환은 기존 canary의 입력 형식과 연결된다. 경로·runtime·binary·table을 아래 값에 결속하면 원 a5의 preflight가 네 pair를 읽는다. 새 solver나 물리식 변경은 필요 없다. 다만 PR79에서 이미 수정한 process-group watchdog이 a5 canary/build entrypoint에는 연결되지 않아, 그 수정 함수를 재사용하는 얇은 외부 wrapper가 필요하다.

## 실제 입력 대응

| 항목 | NCP 반환에 기록된 값 |
|---|---|
| 기준 work | `/root/HE29_REFERENCE_20261020T120000Z` |
| 기준 references | `/root/HE29_REFERENCE_20261020T120000Z/references` |
| 기존 binary | `/root/HE29_REFERENCE_20261020T120000Z/build/he29_owner_server` |
| binary SHA256 | `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9` |
| owner receipt | `/root/HE29_REFERENCE_20261020T120000Z/build/RECEIPT.json` |
| 기존 Python | `/root/HE29_REFERENCE_20261020T120000Z/venv/bin/python` |
| Python / NumPy / SciPy | `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]` / `2.3.5` / `1.17.0` |
| r4/table512 SHA | `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd` |
| 원 DATA archive | `/root/HE29_NCP_20261020T105630Z/incoming/BASS_HE_HE29_RESUME_COMPLETE_20261018_a70d320c.tar.gz` |

반환의 경로는 당시 실행 identity다. 이 환경에서는 현재 NCP 경로·canary process를 직접 관측하지 않았다. 접근 가능한 실행자가 현재 같은 canary 반환/실행이 있는지 확인해야 한다. RDC는 호출하지 않는다.

## 기존 코드가 유지하는 계약

`run_packed.baseline_contract`는 원 `analyze_references.analyze`를 내부 preflight로 사용해 네 pair admission을 확인하고, 네 case 모두의 Python/NumPy/SciPy cohort를 추가로 비교한다. 원 `check_sources`는 20 parent sources, 22 DATA, 여섯 HE29 source 및 실제 binary bytes와 receipt를 검증한다. 별도의 원 분석 CLI를 다시 돌릴 필요는 없다. canary 내부 preflight는 새 실행 입력을 결속하는 단계다.

`solve_packed`는 원 model의 initial state에서 시작해 각 기존 구간을 적분한다. 저장된 Radau/DOP853 endpoint는 비교 기준이다. 같은 r4/table512 모델을 구성한 뒤 table SHA가 같아야 solver가 시작한다. 전체 gas/photon/19 ledger 상태와 scaled-state norm, rtol1e-10/atol1e-12, VigilODE a21, packed thread1이 유지된다.

## 변경이 필요한 실행 연결

`run_packed.py`와 `build_bridge.py`는 모두 기존 he28 `execution.run_process`를 호출한다. 해당 helper의 SHA는 `876e43d76f0773a8d2c38e262902442c614a68334561f5e2a78024c659edb1c4`다. timeout 후 leader가 TERM에 종료되면 잔여 descendant에 KILL을 보내지 않는 조건문이 남아 있다. 이는 PR79의 HE29-WATCHDOG-01 원인이며, 이미 독립적으로 진단·수정된 근거를 재사용한다.

수정 함수는 `ed5adca43f474553a9bce7f5de45d464be5905cb`의 `research/he29_survival_budget_20261018/orchestration_20261020/src/continue_missing_references.py` 안에 있다. 전체 파일 SHA는 `70d38312c288533b829eadbab8037cc09b4218247ebd6262318fc25cb9f0baad`, signature는 `run_process_group(argv, destination, timeout_s, *, execution)`다.

새 외부 wrapper가 원 a5 모듈을 불러온 뒤 그 모듈의 `run_process` binding만 `functools.partial(corrected.run_process_group, execution=original_execution)`로 연결한다. 원 a5 `main`을 호출하므로 source pin과 worker argv, physics checks는 유지된다. worker는 그대로 a5 runner의 내부 `_worker`를 사용하며 외부 시간제어는 수정 함수가 담당한다. wrapper 자신의 identity와 target/controller SHA는 checkout 밖 새 evidence에 기록한다. a5 파일에 patch를 적용해 dirty tree를 만들지 않는다.

새 검증은 import·wiring·fixed pin·잘못된 mode/미수용 reference 거절·동일 worker argv 전달·create-only 실패보존 정도다. PR79의 watchdog14검사, 기존 a5빌드·커널 검증·과학 suite는 재사용한다. 이 검토에서는 소스 수정·시험·빌드·solver·NCP 실행을 하지 않았다.

## 실행 명령의 고정 입력

부모가 게시할 새 wrapper의 실제 source 위치를 확정한 뒤 기존 handoff의 빌드와 preflight/canary 명령을 그대로 연결한다. 실행 argument는 아래 범위를 유지한다.

```text
build:
  --source-revision a5d4711460c09b310b78c9692aa62534b7a843d3
  --out <새 checkout 외부 work>/build
preflight / canary:
  --source-revision a5d4711460c09b310b78c9692aa62534b7a843d3
  --baseline-campaign /root/HE29_REFERENCE_20261020T120000Z/references
  --binary /root/HE29_REFERENCE_20261020T120000Z/build/he29_owner_server
  --owner-receipt /root/HE29_REFERENCE_20261020T120000Z/build/RECEIPT.json
  --library <새 work>/build/target/release/libhe29_optimized_bridge.so
  --bridge-receipt <새 work>/build/BUILD_IDENTITY.json
  --out <새 work>/preflight 또는 <새 work>/canary
canary budget:
  --wall-s 900
```

새 build가 소비하는 a5 checkout에는 먼저 build를 끝낸 뒤, 동일 22 DATA만 고정 a70 archive에서 복원한다. 원 native binary와 기존 venv는 재사용한다. 원 baseline/transport 실행 명령은 없다. 원 a5 canary `_worker`를 직접 시작하지 않는다.

