# BASS_HE: NAVER Cloud c64-g3 실행 재설계

문서 기준일: 2026-09-28. 상태: DESIGN_PROPOSED / NOT_DEPLOYED.

이 문서는 클라우드에서 수행할 실행 구조·이전 절차·검증 계약이다. 새 클라우드 runner의 구현 완료, 서버 생성, 클라우드 실측, CODE-I01의 독립 재승인을 뜻하지 않는다. 현재 제공하는 JSON profile 역시 기존 runner가 곧바로 읽는 설정 파일이 아니라 구현 목표 명세다.

## 1. 목표와 기준점

목표는 사용자의 Ryzen 5900X/96 GB에서 진행하던 BASS_HE DR11G를 c64-g3 64 vCPU/128 GB로 옮겨, 수학·물리적 판정은 유지하면서 대량의 독립 계산 case 처리량과 중단 복구성을 높이는 것이다. 먼저 한 VM을 사용한다. MPI, Kubernetes, Slurm, 다중 VM은 현재 범위에 넣지 않는다.

2026-09-28 원격 재조회에서 다음 correctness 수정 후보가 확인됐다.

- Repository: cosmosapjw-quantum/BASS_HE
- Branch: audit10/dr11g-pair-membership
- Commit: ac09160bae74f051e5e2e17d8a1cde4084576c16
- Tree: 43e6fb8a7bb88234031542de835fd1e2615974d5
- Parent: 85fcd7507bc9db0cdc06bf917b702d998abb43b3

이 commit은 pair-membership 검사와 adapter의 fail-closed 수정을 포함한다. commit 메시지는 correctness-only 132 tests 통과를 보고하지만 이번 설계 작업에서 그 suite를 새로 실행하지 않았다. 이 commit은 기존 PR10 원본과 구별해야 한다.

첨부 DR11G_STATE/DR11G_PERF_STATE에는 수정+Numba 후보의 136 tests와 Python/Numba 56-action 비교가 CLAIMED로 남아 있다. 그러나 확인한 원격 correctness commit에는 Numba 가속기가 없다. 현재 mounted dr11g_runtime/dr11g_correctness에서는 AGENTS.md 외 실제 수정·가속 source payload를 확인하지 못했다. 따라서:

1. 정확히 가져올 수 있는 Python 기준 경로는 위 ac09160...이다.
2. Numba 경로는 원래 source patch/module, 테스트, dependency lock을 복구하고 hash로 결합한 뒤에만 연다.
3. 원본 복구가 불가능하면 과거 코드의 재현이라고 부르지 말고 별도 가속 구현 후보로 개발·검증한다.
4. 성능 숫자나 상태 Markdown만으로 존재하지 않는 모듈을 생성해 원본이라고 주장하지 않는다.
5. main은 초기 기준 상태이므로 cloud clone 후 main을 그대로 실행하지 않는다. branch 이름만 믿지 않고 commit과 tree를 확인한다.

독립 검수의 CODE-I01은 'simple fold의 존재'와 'advertised pair가 그 fold의 두 sheet인지'의 구별에 관한 것이다. 하드웨어 변경은 이 문제를 해결하거나 재승인하지 않는다. 새 재검수 전 PROMOTE=HOLD, Eq55/P_rot/새 Eq50/새 Eq54/continuum admission은 닫힌 상태를 유지한다.

## 2. c64-g3 사양과 자원 제안

공식 사양의 c64-g3는 High CPU, 64 vCPU, 128 GB, KVM 기반 g3다. 사양 code에서 CPU suffix가 없는 것은 Intel을 뜻한다. 정확한 Xeon 모델, 실제 물리 코어 배치, NUMA/SMT 구조, 클럭이나 단일-thread 성능은 이 정보만으로 확정할 수 없다. VM 내 lscpu, affinity, cgroup limit로 확인한다.

공식 High CPU 64/128 QoS의 network 5 Gbps, storage throughput 1188 MB/s, 100000 IOPS는 최대치다. 실제 선택한 CB 볼륨의 기준·버스트 성능과 별개이며 애플리케이션 보장이 아니다. 따라서 이 상한을 100~200 GB 볼륨의 보장 성능으로 사용하지 않는다.

제안 환경:

| 항목 | 초기 설계값 | 판정 성격 |
|---|---|---|
| VM | c64-g3 1대 | 사용자 지정 |
| OS | Ubuntu 24.04 LTS KVM 이미지 | 콘솔 지원 이미지 최종 확인 필요 |
| OS disk | 50~100 GB CB 계열 SSD | 운영 제안 |
| 결과·cache disk | 별도 200 GB CB2 SSD, 해당 존 미지원 시 CB1 | 운영 제안; 디스크 선택은 비용 확인 후 |
| filesystem | 로컬 block-volume ext4 | manifest/SQLite/atomic rename용 |
| initial worker cap | 32 | 성능 최적값 아님 |
| sweep candidates | 1, 8, 16, 24, 32, 48, 56, 64 | available CPU와 ready-task 수로 제한 |
| nested numerical threads | 모든 worker당 1 | BLAS/OMP/Numba 중첩 방지 |
| job memory soft/hard targets | 실제 할당 RAM의 65% / 75% | controller+workers 전체 cgroup 기준 |
| checkpoint archive | stage 종료 및 15분 경과 시 새 segment | 완료 파일만 포함 |
| pilot wall budget | 최대 1시간 dispatch, 종료 grace 별도 | 과금 상한 보장 아님 |
| worker calibration budget | 최대 15분 | 초과 시 best observed valid 설정으로 종료 |

128 GB와 128 GiB를 혼동하지 않는다. 실제 /proc/meminfo 및 memory.max의 작은 값을 예산 기준으로 삼는다. kernel page cache까지 포함하는 cgroup 사용량과 프로세스 RSS를 구별한다.

기존 sandbox 기록은 worker RSS 약 182 MiB였다. 동일 크기가 유지된다는 조건이면 64개는 약 11.4 GiB지만, 이는 c64-g3 측정값이 아니다. RAM을 인위적으로 채울 이유는 없다. 초기에는 pinned arrays를 복제하거나 gigantic shared-memory 구조를 만들지 않는다.

## 3. 선택한 구조와 제외한 대안

추천 구조는 단일 controller + 지속 실행 worker process + case별 immutable 결과 + 단일 writer metadata다.

- 단순 64-thread executor: 현재 Python CF 루프의 GIL 및 native thread 구성에 민감하고 코드별 차이가 크므로 기본값으로 채택하지 않는다.
- 단일 VM의 process workers: 기존 순차 수치 알고리즘을 유지한 채 독립 case를 분산할 수 있어 채택한다.
- Ray/Dask/MPI cluster: 현재 한 대의 작은 행렬·CF 작업에 비해 배포/복구 경계가 커진다. 여러 VM, 원격 task placement 또는 큰 분산 자료가 실제 필요해지면 재검토한다.

process 생성은 Python의 플랫폼 기본값에 의존하지 않고 spawn을 명시한다. 각 worker가 시작할 때 backend를 명시적으로 활성화하고 실제 활성 상태를 receipt로 반환한다. parent의 monkey patch나 JIT 상태가 child에 그대로 상속된다고 가정하지 않는다. worker를 case마다 재생성하지 않는다.

controller 역할: source/env binding 확인, ready-task 선택, timeout/worker 관측, 결과 검증·commit, append-only event 기록, deterministic reduction. worker 역할: 하나의 독립 numerical task 수행과 해당 task의 raw 결과 기록. worker에게 provider credential이나 Git write token을 제공하지 않는다.

## 4. 수학적 구조가 결정하는 병렬화 단위

straight-line/static-Coulomb 모델에서 한 branch b의 geometry는

A_b(rho) = integral [E_j(R(X,rho))-E_i(R(X,rho))] dX,
Delta_b(rho) = abs(Im A_b(rho))

이고 R(X,rho)^2 = X^2+rho^2다. 여기서 Delta의 물리 차원은 energy×length이며 코드에서는 E_h a_0로 무차원화한다. R 및 rho 자체의 코드 입력은 a_0 단위다.

고정된 potential/model에서는 이 geometry 계산이 collision velocity를 인자로 요구하지 않는다. 따라서 미래의 energy scan이 허용되더라도 geometry를 energy마다 반복하는 것은 피할 수 있다. 이는 현재 Eq55를 실행하거나 승인한다는 뜻이 아니다. trajectory가 energy-dependent하게 바뀌면 이 cache 공유 가정은 무효다.

반면 CF 깊이 방향의 재귀와 동일 contour 안의 predictor-corrector는 이전 상태에 의존한다. 이를 CPU별로 임의 분할하거나 panel 순서를 바꾸지 않는다. 특히 named-sheet continuation 경로는 과학 입력이다.

실행 DAG:

SOURCE/ENV admission
 -> CODE-I01 wrong-pair rejection + Q12 control
 -> EP(pair, seed, depth, model) 및 pair certificate
 -> D0 geometry(branch, rho=0, panels=32 또는 64)
 -> 기존 D0 gate
 -> finite-rho geometry(branch, rho, panels=32 또는 64)
 -> branch별 32/64 비교
 -> 전체 numerical report
 -> 독립 repair 재검수

기존 replay의 scientific stage barrier는 유지한다. 단, 같은 stage 안에서 독립 case를 분산한다. 현재 규격은 7 branches×4 rho×2 panels=56개 action이다. D0 stage에는 14개, finite-rho stage에는 42개가 있으므로 이 규격에서 64 workers가 동시에 모두 유효 작업을 받는다고 기대하지 않는다. EP stage도 7개라 최대 7 workers면 충분하다.

branch 전체를 한 task로 묶으면 병렬 폭이 최대 7이 된다. 새로운 scheduler의 단위는 `(branch, rho, panels, depth, backend, source/model identity)`이고 controller가 ready-task를 동적으로 배분한다. 미래의 더 큰 grid에서만 48~64 workers가 의미 있다.

현재 32/64 수렴검사는 각각 독립 continuation으로 수행한다. 64-panel trace에서 짝수 샘플만 뽑아 '독립 32-panel 실행'이라고 보고하지 않는다. 이것은 계산량 절감이 아니라 검증 방법의 변경이다.

순차 의존 부분을 분리하면 대략 T(p)=T_setup+T_serial+T_parallel(p)+T_io다. independent task i의 시간 t_i에 대해 T_parallel(p)는 max(max_i t_i, sum_i t_i/p)보다 작을 수 없다. 따라서 worker 증가만으로 긴 단일 case를 가속할 수는 없다. 소수 task에서는 CPU 숫자보다 compiled kernel과 시작 비용이 더 중요하다.

## 5. 두 계산 경로와 성능 연구 루프

### 5.1 정확성 기준 경로

ac09160...의 Python 경로를 reference로 유지한다. 클라우드에서는 package 환경을 먼저 고정하고 pair false-positive regression, Q12, 과거 두 blocker branch를 실행한다. 기존 결과의 SHA는 원본 byte identity 검사용이다. 서로 다른 CPU/BLAS의 numerical equality까지 byte identity로 요구하지 않는다.

기존 source의 CF depth, panel count, residual, pair membership tolerance를 그대로 유지한다. 허용오차를 완화해서 속도를 얻거나 실패를 0 action으로 처리하지 않는다.

### 5.2 가속 경로

Numba/LLVM source·lock 복구가 완료된 뒤 opt-in backend로 활성화한다. Python/Numba는 서로 다른 implementation identity와 cache namespace를 가진다. complex128/float64 유지, fastmath=False, CF 연산 순서 유지, 각 worker의 독립 활성화가 필수다.

Numba cache는 cloud CPU와 도구 체인에 맞게 새 디렉터리에서 구성한다. AMD workstation의 .nbc/.nbi 파일을 authoritative 계산 산출물로 취급하지 않는다. 우선 한 초기화 프로세스에서 대표 signature를 compile하고, worker를 점진적으로 시작해 import/JIT 폭주를 피한다. 실제 backend가 disk cache를 지원하지 않으면 worker별 compile 비용을 측정하고 보고한다. cache=True가 이미 구현됐다고 가정하지 않는다.

라이브 Python package/Numba/LLVM 업데이트는 금지한다. 원본 lock이 없으면 설치된 버전을 채택 전에 명시적으로 등록하고 compatibility gate를 수행한다. 의존성 없는 기존 correctness source에 Numba를 몰래 mandatory dependency로 넣지 않는다.

### 5.3 calibration

1. 먼저 1 worker에서 correctness를 통과시킨다.
2. persistent pool에서 [1,8,16,24,32,48,56,64] 중 CPU limit/ready-task에 맞는 후보만 측정한다.
3. 각 비교는 같은 입력·kernel·tolerance·thread 수·host에서 수행한다. worker 순서는 난수 seed를 고정해 섞고 최소 3회 반복한다.
4. PERF namespace에서는 result-cache hit로 계산을 생략하지 않는다. JIT cache 허용 여부, cold/warm을 별도 기록한다. benchmark용 반복은 과학 결과 개수로 세지 않는다.
5. 지금의 56-case 실제 batch latency와 미래의 큰 grid steady-state throughput을 별도 보고한다. 소규모 replay를 반복해 64 workers를 채웠다면 synthetic/performance workload임을 표시한다.
6. startup/JIT/I/O/검증까지 포함한 end-to-end 시간과 kernel-only 시간을 모두 남긴다. 실패 arm은 효율 경쟁에서 제외하되 실패 비용은 삭제하지 않는다.
7. peak throughput의 95% 이상인 후보 중 가장 작은 worker 수를 선택한다. 최종 후보와 차순위 후보를 재확인한다. CPU steal·I/O wait·RSS·worker death·잘못된 pair admission이 보이면 원인을 먼저 분리한다.
8. 15분 calibration budget을 초과하면 탐색을 종료하고 검증된 best-observed 설정을 채택하되 최적값 인증으로 부르지 않는다.

기존 5-core sandbox에서 4 workers가 5 workers보다 빨랐다는 기록은 c64-g3의 최적값이 아니다. c64-g3가 5900X 대비 몇 배 빠르다고 사전에 주장하지 않는다.

## 6. CPU와 메모리 계약

환경변수는 NumPy/SciPy/Numba import 전에 설정한다.

```
OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
NUMBA_NUM_THREADS=1
```

SciPy/NumPy가 연결한 BLAS의 실제 thread 수를 threadpoolctl 같은 introspection으로 확인한다. 이름만 설정한 receipt로 충분하지 않다.

worker 수는 `min(selected_count, usable_cpu_limit, memory_limit_workers, ready_task_count)`로 정한다. usable CPU는 affinity/cpuset와 cgroup quota를 모두 확인한다. vCPU 64라는 콘솔 정보만으로 제한 없는 64 CPU라고 가정하지 않는다. NUMA pinning은 초기엔 하지 않는다. topology와 처리량 차이가 실제 확인될 때만 바꾼다.

R_mem = floor[(0.75*M_effective - M_controller - M_buffer)/RSS_worker_p95]를 보수적인 후보 상한으로 사용한다. RSS 합산은 공유 page 때문에 엄밀한 total과 다를 수 있으므로 실제 cgroup memory.current로 최종 보호한다. 65%를 넘으면 신규 dispatch를 멈추고 기존 task를 마친다. 75% hard limit는 host 전체가 아니라 연구 service cgroup에 적용한다. OOM은 환경 실패이며 모델의 0 결과가 아니다.

## 7. checkpoint, cache와 복구

### 7.1 디렉터리

```
/srv/bass-he/
  source/<commit>/                  # read-only scientific source
  env/<environment-id>/            # pinned environment or container reference
  manifests/
  runs/<run-id>/
    RUN_BINDING.json
    controller.sqlite              # local ext4, controller single-writer
    EVENTS.jsonl
    tasks/<task-id>/attempt-0001/
    results/<task-id>/result.json
    traces/<task-id>/
    exports/
  jit/<cpu-env-source-id>/           # disposable, not scientific authority
```

SQLite를 사용하면 WAL 등의 설정도 로컬 block filesystem을 전제로 한다. Object Storage, Dropbox, Drive 또는 FUSE mount를 live DB/lock/cache로 사용하지 않는다.

### 7.2 identity

과학적 task specification hash에는 source/module hashes, model/convention, pair labels, canonical endpoint coordinates와 certificate payload hash, continuation path, rho, depth, panels, tolerances, backend implementation hash, 관련 deterministic seed를 포함한다. elapsed time이나 PID는 scientific key에 넣지 않는다.

Execution binding은 별도로 Python/NumPy/SciPy/Numba/llvmlite/BLAS 버전, CPU features, thread policy, runner hash를 가진다. 다른 환경의 결과를 자동으로 fresh cloud result로 승격하지 않는다. worker 수는 task의 수학적 의미를 바꾸지 않지만 run receipt에 반드시 남긴다.

### 7.3 atomic commit

worker는 attempt 고유 temporary file에 결과를 쓰고 file fsync 후 준비 완료를 알린다. controller가 schema, finite values, identity, numerical gate, hash를 검사하고, 같은 filesystem에서 final result를 atomic publication한다. directory fsync까지 끝난 뒤 DB를 COMMITTED로 진행한다. 기존 final과 내용이 충돌하면 중단한다.

재시작 때 final result는 존재하지만 DB 갱신이 안 된 case는 hash/semantic validation을 통과하면 DB만 복구하고 재계산하지 않는다. DB가 COMMITTED인데 file이 없으면 PASS가 아니라 CORRUPT_OR_MISSING이다. temporary file만 있으면 INCOMPLETE다. 새 run epoch를 사용하고 오래된 worker가 뒤늦게 보낸 receipt는 수락하지 않는다.

이는 accepted result를 한 번만 확정하는 설계다. 장애 때 계산 자체가 절대 두 번 실행되지 않는다는 보장은 아니다.

### 7.4 실패 분류

- NUMERICAL_REJECTED / WRONG_PAIR: 자동 retry 없이 과학적 실패 보존.
- TIME_BUDGET_EXCEEDED: wall clock 초과이며 root 부재로 해석하지 않음.
- WORKER_CRASH / ENVIRONMENT_ERROR: 원인·exit code·signal 보존. 초기 운용에서는 자동 retry 없음. 1회까지의 retry는 명시 설정과 기록이 있을 때만 허용.
- CANCELLED / PREEMPTED: 미완료 case만 resume 가능.
- PAYLOAD_OR_BINDING_MISMATCH: 검출 시점에 중단. 재계산으로 손상을 숨기지 않음.

현재 120초/수치 call stop rule은 몰래 늘리지 않는다. cloud pilot wall budget은 별도다. JIT warmup, case execution, I/O, 종료 grace의 시간을 구별하고 전체 비용은 모두 계상한다. future.result(timeout=...)으로 부모가 기다리지 않게 되는 것과 native worker가 실제로 종료되는 것은 다르다. supervisor가 worker PID/epoch와 현재 task를 추적하고 필요하면 worker process group을 종료·회수한다. 강제 종료로 공유 queue가 손상되지 않도록 worker별 전용 IPC와 결과 file을 사용하며 종료된 worker의 채널은 재사용하지 않는다.

## 8. SSH 단절·종료와 백업

계산을 SSH foreground나 대화형 AI session의 수명에 결합하지 않는다. non-root service user로 systemd service에서 controller를 실행한다. service는 cgroup 내부 worker 전체를 관리한다. 정상 종료나 과학적 거절은 자동 재시도하지 않는다. 무한 Restart=always는 금지한다. reboot 이후 자동 resume는 binding과 영속 ledger를 검사하는 preflight가 통과한 경우만 허용한다.

데이터 disk가 mount되지 않았다면 root disk에 빈 결과 directory를 만들고 계속하지 말고 중단한다. service에 mount dependency를 둔다. OOM/kill/reboot 검증은 짧은 fault-injection task에서 먼저 시행한다.

ACG inbound SSH 22는 접속 원점의 public IP /32 또는 기존 VPN/bastion으로 제한한다. monitor는 localhost bind와 SSH tunnel로 접근한다. private key, API token, Git credential을 manifest, trace, prompt에 넣지 않는다.

checkpoint의 hot path는 로컬 block volume이다. stage 종료와 15분 경과 시 완료 artifact만 create-only segment로 묶고 Google Drive+Dropbox로 이중 백업한다. 기존 폴더는 BASS_DERIVATION_DOSSIERS_20260912다. 각 provider의 실제 성공 ACK/object ID/size와 가능한 checksum을 receipt에 남긴다. upload verified와 restore verified를 구분한다. NCP Object Storage를 추가하면 세 번째 전송 대상이며 기존 이중 백업을 대체하지 않는다.

VM 정지·삭제 전 적어도 한 독립 download를 통한 restore check와 두 provider의 ACK를 확인한다. 프로세스 종료나 OS shutdown만으로 클라우드 과금이 종료했다고 추정하지 않는다. console/API의 server status를 따로 확인하고 남아 있는 disk, snapshot, public IP, 통신비도 확인한다. 이번에는 server stop/delete 자동화나 credential 설정을 실행하지 않는다.

## 9. 실행 순서와 acceptance

G0 SOURCE: ac09160.../tree 일치. Numba payload는 별도 hash로 복구. 잃어버린 코드를 새로 구현하면 별도 identity.

G1 ENV: source와 요구 dependency부터 읽는다. 클라우드에서 실제 사용하는 Python patch/BLAS/LLVM을 freeze한다. CPU/NUMA/cgroup/thread 수 receipt를 남긴다.

G2 TRACER: 새 환경에서 wrong-pair rejection, Q12, 과거 blocker 2개 branch의 D0/유한 rho를 reference backend로 검사한다.

G3 ACCEL: Numba candidate가 존재할 때만 동일 입력으로 Python과 비교한다. 기존 tolerance를 유지하고 backend별 오류/status/path를 기록한다.

G4 SCHEDULER: 1 worker와 multiworker에서 같은 task 집합·같은 acceptance를 적용한다. worker를 중단해 미완료 case만 다시 실행되는지와 tampering 거절을 확인한다.

G5 CALIBRATION: worker sweep과 cold/warm 측정을 수행한다. production result cache를 읽는 시간만 benchmark하지 않는다.

G6 CLOUD_REPLAY: 새 CPU/환경으로의 이전 검증으로 control+7EP+56actions를 한 번 fresh 실행한다. 이후 동일 binding의 성공 case는 반복하지 않는다. 재개할 때마다 바뀌지 않은 과거 scientific suite를 재실행하지 않는다.

G7 BACKUP_RETURN: archive/manifest, 두 provider ACK, restore receipt, 독립 검수용 return을 작성한다.

기존 DR11D acceptance:
- Q12 source relative error <=1e-4.
- EP reference distance <=1e-8, simple-fold와 pair-membership gate를 모두 통과.
- 32/64 상대변화: rho=0에서 <=1e-4, 나머지에서 <=5e-4.
- complex spectral residual <=5e-9, normalized sheet gap >1e-6.
- 모든 case가 finite positive Delta. 예외·누락을 0으로 치환하지 않음.

추가 cloud acceptance는 source-specific 기준을 약화하지 않는다. Python/Numba/worker 수 비교의 numerical tolerance는 기존 accelerator 시험을 우선한다. 복구할 수 없어 새로 정하는 경우 결과를 보기 전에 등록하고, root/state/membership 일치를 스칼라 근사 일치와 별도로 요구한다.

Fault-injection acceptance:
1. worker 하나를 kill해도 이미 COMMITTED인 결과의 hash/실행 횟수가 바뀌지 않는다.
2. controller 재개 후 이전 epoch worker의 결과가 혼입되지 않는다.
3. file publication 뒤 DB 갱신 전의 crash는 결과 재계산 없이 회복한다.
4. stale source/environment와 payload 변조를 거절한다.
5. SSH 단절 후에도 service가 계속되며, service 종료 시 worker가 남지 않는다.
6. 32/64가 독립 계산임을 task identity로 입증한다.
7. 모든 stage가 완료돼도 PROMOTE/physical gates는 자동으로 바뀌지 않는다.

## 10. 코드 변경의 분리

새 구현은 다음 책임 분리를 권한다. 구체적인 path는 repository 지침을 확인한 뒤 결정한다.

A: correctness baseline/accelerator의 source recovery. 기존 CODE-I01 수정을 임의로 다시 구현하지 않는다.
B: pure single-case adapter. 기존 BRANCHES, numerical constants, source convention을 복제해 두 번째 권위를 만들지 않는다.
C: durable dispatcher/worker lifecycle/result validation. 과학 solver 내부는 바꾸지 않는다.
D: cloud host inventory, service template, worker benchmark.
E: fault-injection tests와 독립 재검수 packet.

Numba kernel rewrite와 scheduler rewrite를 한 diff에 섞지 않는다. scientific validation, runner implementation tests, remote publication verification, backup verification을 별도로 기록한다. 이번 산출물은 설계와 handoff이며 A~E의 구현·실행 완료를 뜻하지 않는다.

## 11. 비용 판정

c64-g3의 실제 region/OS/요금제/VAT/할인이 반영된 가격은 console 견적을 사용한다. 이 문서에는 확인되지 않은 시간당 가격을 넣지 않는다.

C_job = hourly_instance_price * elapsed_instance_hours + storage + transfer + snapshots + other_resources.

worker 효율은 CPU 사용률 하나가 아니라 accepted scientific cases / billed wall time으로 평가한다. 작은 test/replay만 돌리면 setup 비용이 지배할 수 있다. c64-g3를 오래 사용할 가치는 독립적인 대규모 branch/grid workload를 지속해서 공급할 수 있는지에 달려 있다. 검수 대기 시간에는 VM을 불필요하게 계속 실행하지 않는 운영을 명시한다.

## 12. 이번에 실제 수행한 범위

수행: mounted durable state 확인, 현재 GitHub branch/commit/tree/관련 source 읽기, 공식 NCP/Python/SciPy/Numba 문서 조사, 설계서·profile·handoff 작성.

미수행: c64-g3 생성, NCP login/SSH, 의존 환경 설치, Numba source 복구, cloud runner 구현, cloud benchmark, 재검수, default 변경, merge, Eq55 이후 계산.

출처 URL·조회일·뒷받침하는 주장은 SOURCES.json에 남긴다. source_context의 DR11G 기록은 이전 CLAIMED evidence이며 이번의 fresh 실행 결과가 아니다.
