# BASS_HE E13C4 — NCP local Codex 실행 인계문

아래 내용을 NCP local Codex에 그대로 전달한다. 이 문서는 **이미 구현·검산한 E13C4의 N512/P60 enclosure를 바뀐 NCP host에서 한 번 실행하여 재현성을 확인하는 작업 계약**이다. 현재 이 패키지의 NCP 실행 상태는 `NOT_RUN`이다. ChatGPT에서 실행한 결과를 NCP 실행 결과라고 기록하지 않는다.

## 작업 지시

너는 BASS_HE의 NCP local 실행 담당이다. 먼저 전달된 immutable source와 실제 파일을 읽고, 기존 사용자 checkout과 수정 사항을 보존한 채 새 작업 위치를 확보하라. 필요한 host/input 검사를 수행한 뒤 같은 여섯 local control의 검증된 Decimal enclosure를 **정확히 한 번** 실행하고, 저장된 N512/P60 결과의 수치 부분과 새 실행 결과를 비교하라. 이론 설계, 기존 suite, 연속 reference를 처음부터 다시 만들지 말고 아래 완료 기준까지 진행하라.

### 1. 기준과 입력을 고정한다

저장소는 `cosmosapjw-quantum/BASS_HE`, branch는 `research/shared-c64-crossrepo-20260928`, draft PR은 #17이다. 이번 연구 시작점 `f9a34c8818c29d5e78a7bd2dafc0ef0adac2e62b`는 E13C3의 이전 상태를 나타낸다. **실제로 실행할 E13C4 commit은 최종 detached delivery receipt의 `scientific_core_commit`에서 읽어라.** 이동하는 branch HEAD나 이전 시작점을 그 commit 대신 쓰지 마라. 최종 전달의 archive·receipt 링크와 object ID를 사용하고, 문서 안에 아직 알 수 없는 commit/self hash를 만들어 넣지 마라.

현재 checkout의 `git status`와 적용되는 `AGENTS.md`를 읽는다. 사용자의 변경을 stash/reset/clean으로 치우거나 기존 branch를 checkout해서 작업을 덮지 않는다. 이미 연결된 원격과 인증을 이용하여 필요한 immutable commit을 확보하고, 새 경로에 detached worktree를 만든다. 새 commit을 읽기 위해 기존 작업 branch의 history를 바꾸지 않는다. 작업 디렉터리가 이미 있으면 새 경로를 고른다.

Git에는 검토에 필요한 compact projection이 게시될 수 있으므로 **완전한 실행 입력은 함께 전달한 봉인 archive**에서 복원한다. Archive의 SHA-256을 detached receipt와 비교하고, 새 디렉터리에 안전하게 해제한 뒤 `FILE_MANIFEST.json`에 기록된 payload hash와 크기를 확인한다. Archive가 없거나 손상되었을 때 예전 checkout의 비슷한 파일을 섞어서 채우지 않는다.

Package root에서 `PLAN.json`, `EXECUTION_LOCK.json`, `NCP_EXECUTION_CONTRACT.json`, `INDEPENDENT_REVIEW.json`, `state/CHAT_FIRST_EXECUTION_POLICY_KO.md`, `state/NCP_HPC_POLICY_KO.md`, `code/ncp_execute.py`를 읽는다. 수학적 질문이 실제로 생기는 경우에만 `THEORY.md` 또는 `evidence/theory/THEORY_CONTRIBUTION.md`의 해당 절을 더 읽는다. 이미 확인된 원 문헌과 전체 하네스를 매번 다시 조사하지 않는다. Chat-first policy의 예전 `evaluate_r2.py` 작업 설명은 E13C4 실행 명령이나 과학 scope가 아니다. 공통 책임·예산·증거 원칙을 현재 E13C4 계약에 적용한다.

`EXECUTION_LOCK.json`은 실제 실행 source, 여섯 입력, PLAN, 저장 N512/P60 scientific identity를 결속한다. 모든 hash를 과학 실행 전에 확인한다. 불일치를 발견하면 lock을 새로 만들어 통과시키지 말고, 관측한 경로·기대값·실제값을 남겨 원인을 밝힌다. 최종 independent review가 부여한 국소 claim ceiling을 그대로 상속하고 실행자가 그 판정을 대신 닫지 않는다.

### 2. 이번 host replay의 범위를 유지한다

고정 control ID는 아래 여섯 개다.

| mode | step | node | segment |
|---|---:|---:|---:|
| OFF | 1 | 0 | 0 |
| OFF | 1 | 1162 | 0 |
| OFF | 1 | 1976 | 0 |
| GM | 2 | 1727 | 0 |
| GM | 2 | 2333 | 0 |
| OFF | 2 | 700 | 1 |

각 local initial-value problem은 captured `f0`, incoming correction의 정확한 0, 상속된 affine gas path, source/종별 mask, `E0 exp(-h*t)` energy anchor를 사용한다. Precision은 60 decimal digits, subdivision은 512다. Source rate, binding energy, Verner fit, frozen coefficient, heat 정의, ledger 또는 acceptance를 바꾸지 않는다.

이 lane은 **outward Decimal interval와 interval 2차 derivative를 사용하는 검증 계산**이다. 일반 binary64 또는 real64 Fortran으로 바꾸면 같은 알고리즘의 단순 host 재현이 아니다. NCP HPC 정책의 정확도 우선 원칙을 지키고, 이 작업에서는 기존 Decimal arithmetic을 유지한다. MPI/OpenMP 병렬화, compiled backend, fast-math, precision 축소, N 축소를 새로 적용하지 않는다. 독립 항목이 여럿 있다는 이유만으로 64개의 process를 띄우지 않는다.

현재 기준 실행은 `evidence/N512_P60.json`에 기록되어 있다. 여섯 control에서 512 cell마다 interval·midpoint를 평가하므로 coefficient 평가는 (6\times512\times2=6144)회다. ChatGPT 환경의 실제 계산 시간은 약 35.915초, 기록된 peak RSS는 13,568 KiB였다. 이는 예산 판단의 참고이며 NCP 성능, speedup 또는 64-core scaling 결과가 아니다.

NCP처럼 실행 환경이 바뀌었기 때문에 이번 작은 replay를 한 번 수행한다. 입력·코드·환경이 바뀌지 않은 동일 host에서 같은 계산을 다시 반복할 근거가 되지는 않는다. 기존 32/128/512 refinement 전체, 32/P80 control, exact toy 및 independent control suite를 여기서 모두 재실행하지 않는다.

### 3. Host 검사와 실행 명령

기존 CPython **3.12.x** interpreter를 사용한다. 실제 Python implementation/version, Decimal libmpdec version, CPU/affinity/quota, cgroup memory와 thread/MPI 관련 허용된 비민감 환경값을 기록한다. `env` 전체나 인증정보를 로그에 덤프하지 않는다. 64라는 장비 설명을 실측 physical core 수, 현재 affinity 또는 CPU quota로 추정하지 않는다.

과학 계산은 serial process 하나로 실행하며 주소 공간 상한은 **1 GiB `RLIMIT_AS`**, wall timeout은 **180초**다. 주소 공간 cap과 실측 peak RSS를 구별해 보고한다. `mpirun`, 다중 task `srun`, 중첩 thread 확장을 사용하지 않는다. 호환 interpreter가 없다면 임의의 backend로 대체하지 말고 실제 blocker를 기록한다.

Package root에서 아래 명령을 실행한다. `<새_NCP_실행_디렉터리>`는 아직 존재하지 않는 경로로 바꾼다. 절대 경로를 권장한다.

```bash
python3 code/ncp_execute.py --out <새_NCP_실행_디렉터리> --execute --timeout 180
```

Package root를 별도로 지정해야 하면 `--package <패키지_절대경로>`를 추가한다. 이 옵션을 생략하면 runner의 기본 package root를 사용한다. `python3`가 다른 버전이면 확인한 CPython 3.12.x interpreter의 실제 경로를 사용한다.

`--execute`를 생략한 명령은 **source와 host 확인만 수행**한다. 과학 계산이나 새 numerical parity를 수행한 것으로 기록하지 않는다.

```bash
python3 code/ncp_execute.py --out <새_preflight_디렉터리> --timeout 180
```

별도의 preflight 명령은 선택 사항이다. `--execute` 명령 자체가 필요한 선행 검사를 수행하므로 확인을 위해 같은 작업을 두 번 돌릴 필요는 없다. Preflight를 별도로 했다면 실제 실행에는 또 다른 새 출력 디렉터리를 사용한다. Output 충돌·심볼릭 링크·기존 결과를 덮어쓰는 fallback을 만들지 않는다.

Runner가 실제로 생성한 파일을 출력 디렉터리째 보존한다.

| 파일 | 기록 범위 |
|---|---|
| `IDENTITY_CHECK.json` | 실행 lock과 source/input byte identity |
| `HOST.json` | 실제 interpreter, CPU/affinity/quota, memory 등 host 정보 |
| `ARITHMETIC_SMOKE.json` | 바뀐 host의 작은 arithmetic 진단. 기존 interval proof를 대체하지 않음 |
| `NCP_RESULT.json` | 실행 요청 여부, 진행/종료 상태, actual exit 및 parity 요약 |
| `RESULTS_START.json`, `RESULTS_CHECKPOINT.json` | 실제 과학 실행의 시작과 control 진행 |
| `RESULTS.json` | 이번 NCP에서 실제 생성한 N512/P60 enclosure |
| `stdout.txt`, `stderr.txt` | 과학 child process의 원 로그 |
| `PARITY.json` | 저장 baseline과 새 numerical projection의 비교 |

`RESULTS_START.json`부터 `PARITY.json`까지의 과학 실행 파일은 `--execute` 경로에서 생성된다. Failure 발생 단계에 따라 일부가 없을 수 있으므로 생성된 파일과 누락 상태를 그대로 남긴다. 파일을 만들어 넣어 완료처럼 보이게 하지 않는다. 결과 파일이 생겼다는 사실과 child process가 정상 종료했다는 사실을 각각 확인한다. Child failure, timeout, incomplete checkpoint 또는 parity failure가 있으면 PASS가 아니다.

### 4. 새 결과를 판정한다

검사 대상은 **이번 NCP에서 실제로 생성한 수치 결과**다. 기존 `evidence/N512_P60.json`만 다시 읽고 hash가 맞는지 확인하는 것을 fresh parity라고 부르지 않는다. Runner가 정의한 scientific projection에 대해 baseline과 정확한 동등성을 확인한다. `PARITY.json`의 `bitwise_numerical_json_parity`는 canonical scientific JSON projection의 동등성을 뜻하며, 시간·host를 포함한 원본 output 파일 전체의 byte equality를 뜻하지 않는다.

위치·명령 경로·환경·시간과 같은 실행 metadata는 수치 projection에서 분리한다. 그러나 interval endpoint와 upper bound, domain 판정, control ID, N/precision, elementary rounding count, source identity, saved-evidence compatibility 결과를 제외하여 차이를 숨기지 않는다. 새 수치 tolerance를 만들거나 문자열을 반올림·정규화하여 다른 결과를 같게 만들지 않는다. 불일치하면 첫 차이의 JSON path, 저장값, 새 값과 관련 raw evidence를 남긴다.

다음 상태를 분리해 보고한다.

- **Execution:** 실제 실행 여부, child exit/signal, timeout, 누락 output.
- **Fresh numerical parity:** 저장된 scientific projection과 이번 결과의 비교.
- **Scientific scope:** exact-lift 여섯 local 문제의 기존 enclosure claim.
- **Physical/production scope:** 아래 보호 상태를 유지.

Source/host 확인만 통과하면 `NCP_RESULT.status=VERIFY_ONLY_PASS`, `scientific_execution=NOT_RUN`, `new_result_accuracy=NOT_EVALUATED`다. 실제 실행과 새 수치 대조가 모두 통과한 경우에만 `PASS_SCOPED_HOST_PARITY`, `scientific_execution=ACTUALLY_EXECUTED`, `new_result_accuracy=SCOPED_PARITY_PASS`, `new_output_parity_checked=true`를 보고한다.

`baseline_RCT=OFF`, actual atomic photon/heat/recoil `null`, physical/production `HOLD`, HE-F2/F09 `OPEN`, receiver adoption `SEPARATE`, Gamma alias `3.543295 FAIL`, uniform full-path certificate 미확립 상태를 유지한다. Host parity PASS는 물리적 budget, receiver admission 또는 production 승격이 아니다.

### 5. 실패와 최소 수정

최초 실패의 stdout/stderr, START/checkpoint와 실제 exit를 보존한다. 기존 호환 interpreter 선택, package 경로 수정, 새 output 경로 지정처럼 과학 payload를 바꾸지 않는 host 문제는 관측 원인을 해결한다. 실패한 preflight를 성공한 기록으로 덮지 않는다.

Source byte를 수정해야 하는 경우에는 lock을 임의로 다시 결속하지 않는다. 최소 diff, 최초 실패, 원인과 필요한 수정 범위를 연구 스레드로 반환하라. 정의·approximation·arithmetic·수치 알고리즘·tolerance·certificate policy를 바꾸어야 하는 문제는 여기서 재설계하지 않는다. 과학 process가 이미 시작된 뒤 실패하거나 timeout이면 자동으로 같은 명령을 반복하지 말고 현재 증거와 상태를 반환한다.

E13C2 continuous reference/oracle, old native/full3×384, gas/Newton 계산, 새 RCT source, nonzero outflow, first2/full-path replay는 이번 작업에 포함되지 않는다. 실패를 해결한다는 이유로 이 계산들을 시작하지 않는다.

### 6. 반환 산출물과 게시

실행 담당자가 **`NCP_REPORT_KO.md`를 직접 작성**하고 runner의 실제 output directory 전체를 함께 반환한다. 이 보고서는 runner가 자동 생성하지 않는다. 보고서는 실행·parity 결론을 먼저 쓰고 다음을 담아라.

1. 사용한 immutable E13C4 scientific core commit, archive/manifest와 실행 lock identity.
2. 실제 source/input/PLAN/N512 baseline hash, N512/P60, 여섯 control ID, 실제 과학 실행 횟수.
3. Host/CPU affinity/quota/memory/interpreter 및 허용된 환경 기록, 실제 argv와 start/finish/elapsed/exit 또는 signal.
4. Fresh numerical projection identity와 parity verdict. 불일치하면 첫 차이와 실제 raw evidence 경로.
5. 최초 실패·수정·미실행 항목과 claim ceiling. Source/host 검사만 했다면 과학 실행 `NOT_RUN`을 명시.
6. 필요할 때만 다음 최소 행동과 실행을 재개할 조건.

Machine-readable 결과에는 같은 구분을 보존한다. 실제 runner 파일명과 schema를 그대로 사용하고 보고서에 연결한다. stdout가 비었거나 checkpoint가 끝나지 않은 경우 그 사실을 숨기지 않는다. 산출물을 반출할 때 고정 입력이나 인증정보를 무분별하게 추가하지 말고, 필요한 실행 evidence와 연결 가능한 identity를 포함한다.

기존 승인 범위에서 결과 게시가 필요하면 같은 branch의 **새 run 경로에 additive commit**으로 추가한다. 게시 직전 remote HEAD를 다시 읽고 non-force expected-head 보호를 사용한다. 봉인된 E13C4 baseline과 사용자의 기존 파일은 덮지 않고 merge도 수행하지 않는다. 다른 사람에게 메시지를 보내지 않는다.

백업이 필요하면 최종 delivery receipt와 기존 context에 지정된 Drive/Dropbox 대상에 새로운 고유 이름으로 create-only 업로드한다. 실제 ACK, object ID, name/path/size를 기록한다. Metadata readback은 R1이며, 실제 내려받아 확인하지 않은 백업을 `RESTORE_VERIFIED`라고 쓰지 않는다. 성공한 업로드를 이유 없이 반복하지 않는다.

### 7. 다음 물리 연구는 별도로 남긴다

후속 과학 node는 `E13C5_FIXED_PATH_INCOMING_AND_ANCHOR_ENCLOSURE`, 상태는 `CHAT_RESEARCH_PENDING`이다. 먼저 ChatGPT 연구 스레드에서 incoming uncertainty와 energy-anchor representation의 전파식을 설계·구현하고 작은 판별 계산을 마쳐야 한다. 이번 NCP host parity 작업에 그 full-path 구현을 묵시적으로 추가하지 않는다. 승인된 NCP 실행과 결과 반환이 끝나면 해당 node의 필요한 입력과 남은 질문만 연구 스레드에 전달하라.
