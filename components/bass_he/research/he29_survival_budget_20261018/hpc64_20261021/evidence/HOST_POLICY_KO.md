# HE29 host 자원·프로세스·lease 경계

이 파일은 새 `host_plan.py`의 실행 준비 정책이다. NCP native 실행이나 성능 측정 결과가 아니다. 실제 시작은 parent launcher가 같은 host lease 안에서 resource와 process 관측을 모두 통과한 뒤 수행한다.

## 공개 API와 시작 조건

`observe_host()`는 Linux의 실제 affinity, MemTotal/MemAvailable, cgroup v2 mount·membership·보이는 ancestor의 cpu.max/memory.max/memory.current, package/core/thread-sibling mapping을 읽는다. UTC·hostname·PID·kernel release를 기록한다. affinity를 바꾸지 않는다.

`choose_resources(host, max_table_workers=48, max_build_jobs=8, reserve_cpus=8, reserve_memory_gib=16, worker_estimate_gib=1)`은 JSON 가능한 계획을 돌려준다. 고정 필드는 `execution_allowed`, `hold_reasons`, `cpu_ids`, `table_workers`, `build_jobs`다. 프로세스 관측이 별도로 요구되는지는 `process_admission_required_separately`로 표시한다.

`active_he29_processes(binary, proc_root=Path('/proc'))`도 `execution_allowed`, `hold_reasons`를 돌려주며, `matches`, `other_scientific_matches`, `permission_denied`, `vanished_pids`, `read_errors`를 구분한다. Parent는 두 `execution_allowed`가 모두 참이어야 실행한다. 자원 계획만으로 process absence를 주장하지 않는다.

## CPU와 메모리 계산

- affinity에서 CPU55가 존재하면 제외한다. 보이는 모든 cgroup ancestor의 유한 quota 중 최솟값을 정확한 유리수로 비교하고 정수 CPU capacity를 내림한다.
- 유효 CPU capacity에서 기본 8 CPU를 남긴다. capacity가 8 이하라면 기본 계약으로는 HOLD다. 다른 reserve를 명시한 경우에는 그 값을 기록한다.
- 물리 core mapping을 읽을 수 있으면 같은 core의 SMT sibling보다 서로 다른 core를 먼저 선택한다. 선택된 affinity는 CPU 소유권이나 다른 프로세스의 배제를 뜻하지 않는다.
- 메모리 capacity는 MemTotal과 보이는 유한 cgroup memory.max의 최솟값이다. 가용량은 MemAvailable과 각 유한 ancestor의 `memory.max - memory.current` 중 최솟값이다.
- 기본 reserve는 `max(16 GiB, 유효 capacity의 20%)`다. 추가 2 GiB는 parent 고정 overhead estimate로 남긴다. table worker는 기본 1 GiB, build job은 2 GiB estimate를 사용한다. 실제 peak RSS를 측정하거나 상한을 보장한 수치가 아니다.
- build 최대 8 jobs와 source-table 최대 48 workers는 서로 다른 순차 phase다. 두 값을 동시에 실행하는 총 concurrency로 더하지 않는다.
- 필요한 quota·finite-memory headroom·MemAvailable를 읽지 못하면 HOLD다. 프로세스 관측에 다른 과학/build candidate가 있으면 parent도 HOLD하며 임의로 kill하지 않는다.

## 실제 global cgroup root의 누락 파일

C9에서 실제 global root에는 `cpu.max`와 `memory.max`가 원래 제공되지 않을 수 있음을 확인했다. mount path가 `/`라는 사실은 namespace root와 구별되지 않는다.

현재 구현은 mountpoint에서 다음 조건이 함께 관측된 경우에만 `ACTUAL_GLOBAL_ROOT_SIGNATURE`로 지정한다.

1. `cgroup.controllers`는 실제로 읽혔다.
2. `cgroup.type`은 NOT_FOUND다.
3. `cpu.max`와 `memory.max`가 모두 NOT_FOUND다.

이 경우에만 해당 실제 global root의 누락된 max를 unlimited로 해석한다. 아래에 있는 실제 descendant quota와 memory limit은 계속 적용한다. `cgroup.type`이 존재하면 `ACTUAL_NONROOT_NAMESPACE_OR_SUBTREE_MOUNT`, 그 외 증거가 불충분하면 `ROOT_KIND_UNPROVEN`이다. Permission denied와 read error를 NOT_FOUND로 바꾸지 않으며, namespace/subtree의 누락된 control file은 HOLD다.

근거는 독립 C9 reviewer가 실제 읽은 kernel primary source다. Linux cgroup v2 문서는 resource control file의 root 예외와 `cgroup.type`의 non-root 범위를 설명한다. Linux v6.8 `kernel/cgroup/cgroup.c`에서 `cgroup.type`의 `CFTYPE_NOT_ON_ROOT`는 namespace 상대 경로가 아닌 실제 `cgroup_parent(cgrp)` 유무로 필터된다. 읽은 Git blob은 `a66c088c851cfb87036ccc93317f7357769cb268`이다. NCP의 실제 kernel release는 실행 전에 관측해야 한다.

- https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
- https://github.com/torvalds/linux/blob/v6.8/kernel/cgroup/cgroup.c

관측 범위는 보이는 mount와 ancestor다. 이 결과를 모든 namespace 밖의 host 상태를 읽었다는 주장으로 확대하지 않는다.

## 중복·다른 모델 process 관측

HE29 script 이름과 지정한 owner binary의 실제 cmdline token 및 필요한 exe link를 읽는다. 자기 자신과 읽을 수 있는 조상 PID는 제외하며 zombie는 실행 중 job으로 세지 않는다. 다른 BASS_HE/VigilODE/REI/REC/HH/BASS/bass_cr namespace의 scientific/build candidate는 별도 목록으로 남긴다.

`python campaign.py`처럼 argv가 상대 경로일 때에는 실제 `/proc/<pid>/cwd`를 보조로 읽는다. namespace가 cwd에서 확인됐는지 cmdline token에서 확인됐는지 필드를 구분한다. `BASS_HE83` 같은 숫자 suffix와 `bass_cr`의 구체 namespace도 유지한다. 일반 read-only utility를 scientific job으로 분류하지 않는다.

프로세스가 읽는 사이 사라진 경우와 permission denied는 별도다. Permission/read error로 잠재 실행자의 가시성이 부족하면 HOLD다. 관측한 local `/proc` 범위 외의 다른 대화·미게시 원격 job·과거 실행의 완전한 부재를 주장하지 않는다. signal/kill 호출은 없다.

## Host lease

`host_execution_lease(path)`는 context manager다. 기본 경로는 `/tmp/BASS_HE_HE29_NATIVE.lock`이다. `flock(LOCK_EX|LOCK_NB)`를 잡은 뒤에만 기존 bytes를 갱신한다. symlink와 여러 link를 가진 inode를 거부하고, lock 후에도 visible path가 같은 regular inode인지 확인한다.

ACTIVE/RELEASED, hostname, PID, UTC, inode/device를 기록한다. 정상 종료와 예외 종료에서 lock을 풀며 파일을 삭제하지 않는다. 별도 실행자가 같은 고정 경로를 사용해야 host 전체 중복 방지에 참여한다. lease가 있더라도 legacy process 관측은 별도로 필요하다.

## 실제 새 검증과 재사용

- 최초 host/proc/lease 12 methods: 첫 실행 PASS. `HOST_TESTS_FIRST/`.
- 상대 cwd namespace 누락의 구체 수정: 새 2 methods만 첫 실행 PASS. `HOST_CWD_TARGETED_FIRST/`.
- C9 root compatibility 수정: 새 4 methods만 첫 실행 PASS. `HOST_ROOT_TARGETED_FIRST/`.
- 합계는 서로 다른 새 18 test methods다. 기존 methods 재실행은 0이다.
- 실제 local sandbox의 read-only 관측은 처음 구현에서 1회 수행했다. affinity9, quota8, memory.max8 GiB, 당시 headroom562,143,232 bytes로 resource HOLD였다. NCP 관측이 아니다. 해당 raw receipt는 수정 전 source SHA와 범위를 그대로 보존했고 재관측하지 않았다.
- native/physical solver, network, affinity 변경, signal 호출은 모두 0이다. 실제 flock 검증은 임시 fixture 경로에서만 했다.

Git publication·backup·DAG 통합은 parent의 후속 게시 영수증을 기준으로 한다.
