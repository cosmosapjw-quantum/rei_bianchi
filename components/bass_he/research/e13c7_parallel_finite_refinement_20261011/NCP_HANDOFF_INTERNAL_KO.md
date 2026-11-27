# BASS_HE E13C7 — NCP local codex 실행 인계

## 목표와 권한

ChatGPT 연구 스레드에서 준비·검토한 **새 OFF 2,331경로의 N1024/P60 정밀화 한 번**을 실행한다. 기존 사용자의 지시는 짧은 작업을 ChatGPT에서 마치고 길고 병렬화 가능한 부분만 NCP의64코어/128GB 장비에 넘기는 것이다. 이 archive는 소스·입력·로컬 증거·계약·실행기를 모두 포함하므로 추가 전달 파일이 필요 없다.

외부 사용자용 `NCP_LOCAL_CODEX_HANDOFF_KO.md`에 제공된 archive 실제 bytes/SHA를 먼저 검증하라. Drive 반환 파일명에 `.bin` 등이 붙어도 실제 반환된 경로를 사용한다. 이 인계에는 part001/part002 또는 recovery kit가 없다. 검증한 단일 ZIP을 새 directory에 복구하고 `PACKAGE_MANIFEST.json`의 모든 실제 파일 bytes/SHA를 확인하라. 경로 탈출·중복·symlink는 거부한다. 기존 실패/부분 작업을 덮어쓰지 않는다.

이 인계는 현재 사용자가 이미 승인한 계산과 승인 폴더로의 백업을 구체화한다. 실행을 다시 확인받거나 별도의 짧은 재현 작업을 추가할 필요는 없다. 과학 모델·kernel·mask·source·허용오차를 변경할 상황이면 원자료를 보존하고 이 연구 스레드에 반환한다.

## 고정 identity와 읽을 순서

- 패키지 root: `BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1`
- 연구 노드: `HE_E13C7_PARALLEL_FINITE_REFINEMENT01`
- 기준 Git head: `019dc4f6451b3076eb6c21f8836a6040b232e945` (PR22)
- **EXECUTION_LOCK.json: 10,078 bytes**
- **EXECUTION_LOCK SHA-256: `c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4`**
- SOURCE_LOCK SHA-256: `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`

`CURRENT_STATE.json`, `review/INDEPENDENT_DECISION.json`, `RESEARCH_CONTRACT.json`, `SCIENTIFIC_CONTRACT.md`, `OWNER_DECISIONS.md`, `inputs/WORK_PLAN.json`, `docs/PARALLEL_PROTOCOL.md`를 읽는다. 전체 REPORT는 이미 끝낸 일과 선택 이유를 설명한다. 문헌·유도·kernel 구현을 처음부터 다시 시작하지 않는다. Git의 compact publication은 완전한 실행 입력을 담지 않으므로 계산에는 이 ZIP의 root를 쓴다. 움직이는 branch HEAD를 immutable execution identity로 대체하지 않는다.

## 이미 완료하여 다시 실행하지 않을 것

- 기존 수용6경로: 0,101,102,410,413,700.
- 새 로컬8경로: 105,106,409,414,1162,1620,1976,2344. 네 경로는 N1024, 나머지는 N512로 이미 수용됐다.
- source-off exact-zero95경로: 2345–2439. 영임이 증명되어 quadrature가 필요 없다.
- precision/branch/N128 control, N512 benchmark, E13C6 OFF4 serial replay, full-first2, source CSV 재생성, native physics, gas advance, ODE solve.
- **전체 Fraction 예산 합산과 최종 과학 판정은 반환 후 ChatGPT 연구 스레드에서 한다. NCP에서 별도로 실행하지 않는다.**

## 실제 실행 한 번

`BASS_ROOT`는 복구한 실제 절대 root, `BASS_OUT`은 기존에 존재하지 않는 root 밖의 새 출력 절대 경로로 설정한다. 이 두 변수명은 예시이며 실제 경로를 쓴다. shell 출력과 exit code를 보존한다.

```bash
python3 "$BASS_ROOT/code/ncp_execute_batch.py" \
  --package "$BASS_ROOT" \
  --output-dir "$BASS_OUT" \
  --execution-lock-sha256 c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4 \
  --ranks auto
```

이 명령은 `parallel_batch.py launch --transport mpi --scope ncp`를 호출한다. 실제 Linux/CPython3.12.x/OpenMPI와 사용 가능한 affinity, 논리CPU/물리core topology, 관측 가능한 cgroup v1/v2 quota·memory 및 MemAvailable을 검사한다. 관측 가능한 더 강한 제한을 적용한다. root `cpu.max` 또는 memory 파일 부재는 `UNOBSERVED`이며, 무제한 또는64CPU 할당 증거가 아니다. Provider는 실제 별도 attestation이 없으면 `NOT_ASSERTED`다.

Open MPI 실행기를 요구하며 local transport나 다른 수치 backend로 조용히 전환하지 않는다. 이미 승인된 계산 호스트에서 실제 effective uid가0이면 wrapper가 명시적으로 `--allow-openmpi-root`를 선택하고 mpiexec argv의 `--allow-run-as-root`를 기록한다. 새로운 OS 사용자나 provider 자원을 만들지 않는다. Open MPI 미설치 등 preflight 차단 시 실제 실패 영수증을 보존한다. 기존 권한 안의 최소 환경 조정은 가능하지만 과학 입력·kernel·허용오차·identity를 바꿔 실행을 강행하지 않는다.

`auto`는 실제 자원 안에서 최대64개의 **계산 rank**를 선택한다. 모든 rank가 경로를 계산하고 MPI controller rank는 없다. 허용 CPU 하나마다 rank 하나를 고정하며 thread 환경은1이다. deterministic LPT는 실제 로컬 mask별 비용을 사용한다.64개의 허용 CPU와 충분한 실제 메모리가 없으면 감축된 rank 수와 이유를 기록한다.

N=1024, Decimal P=60, 2,331경로, 4,662구간, 새 coefficient evaluation9,547,776회다. 각 경로180초, rank당 주소공간1GiB, batch7,200초, 실제 가용 메모리20% reserve를 적용한다. 약31–50분이라는 시간은64 rank 효율80–50%를 가정한 추정이며 runtime 보장이 아니다.128GB를 일부러 채우는 할당을 추가하지 않는다.

## 완료·실패·재개

성공 상태는 `COMPLETE_HEAVY_PATHS_PENDING_CHAT_REDUCTION_AND_REVIEW`다. `BATCH_COMPLETE.json`의 상태와 정확히2,331경로 coverage, 새 호출/재사용 수, coefficient 수, 실제 source/input before-after identity를 확인한다. 병렬 collection은 수치 최종 수용이 아니며 physical·continuum·production·receiver는 HOLD다. Raw enclosure가 nesting gate를 통과하지 않아도 원결과를 보존하여 반환한다. 오래된 값으로 대체하거나 intersection하지 않는다.

실패하면 출력·stdout/stderr·reservation·partial/complete 경로와 첫 failure receipt를 보존한다. wrapper는 launcher를 정지시킨 뒤 archive를 만든다. cleanup을 확정하지 못하면 `CLEANUP_FAILURE.json`을 남기고 파일이 변할 수 있는 상태에서 return ZIP을 만들지 않는다. 그 경우 실제 남은 프로세스와 출력 경로를 보고하고 계산을 다시 호출하지 않는다.

**자동 retry는0이다. 실패 뒤 동일 명령을 자동으로 다시 실행하지 않는다.** 명시적으로 재개를 요청받으면 새 출력 경로에 `--resume-from`으로 이전 **BATCH directory**를 전달한다. 실제 시도된 미완료 경로를 다시 돌리려면 정확한 node 목록을 `--retry-incomplete-nodes`에 명시해야 한다. 동일 lock·work·N/P·입력·실제 saved bytes/semantic을 통과한 완료 경로만 재사용한다. 미확정 호출 수를0이나 완료로 보고하지 않는다.

## 반환과 승인된 백업

wrapper가 실제 결과 ZIP과 `.RECEIPT.json`을 생성하고 archive 절대 경로·bytes·SHA를 stdout으로 출력한다. Return ZIP은 실제 payload bytes/SHA를 검사한 결과다. 전역 Fraction reduction은 `NOT_RUN_PENDING_CHAT_INTAKE`여야 한다. 반환 파일명에 suffix가 붙어도 실제 bytes/SHA가 기준이다.

완성 또는 실패 return ZIP 및 필요 delivery receipt를 다음 승인 폴더에 새 이름으로 업로드한다.

- Drive folder ID: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox folder: `/BASS_DERIVATION_DOSSIERS_20260912/`

현재 연결된 업로드 도구와 실제 파일 경로를 사용하며, ACK와 이름·크기 readback을 확인한다. tool이 unavailable이면 결과와 receipt를 보존해 접근 가능한 파일 경로를 반환하고, 이 이유로 과학 계산을 다시 실행하지 않는다. 업로드 확인을 원격 전체 restore 검증이라고 표현하지 않는다. 기존 파일 overwrite, public source PDF 재배포, Git merge/force-push는 하지 않는다.

사용자에게는 다음을 한 번에 돌려준다.

1. 실제 성공/실패 상태 및 최초 실패 원인(있으면).
2. 기록된 host/Python/OpenMPI/CPU topology·affinity·quota·rank 수·thread 수·memory, provider attestation 상태.
3. 새 경로 호출·검증된 완료·재사용·미확정 수, 실제 coefficient 수, 총 경과시간과 peak RSS. ODE/gas/native/prior replay/global-budget invocation은 실제 값을 분리한다.
4. 원본 return ZIP 링크/절대 경로·actual bytes·SHA-256 및 backup ACK/readback.
5. `전역 합산과 최종 과학 admission은 ChatGPT 연구 스레드에서 이어서 진행`이라는 다음 상태.
