# C2f manufactured 실행 계약

이 실행기는 물리적 Coulomb 고유문제나 실제 궤적을 실행하지 않는다. 고정 schema의 manufactured case만 `manufactured_cases.run_case(case, *, backend, native_library)`에 전달한다. callback은 실패 시 예외를 내야 한다. 정상 반환은 64 KiB 이하의 유한 JSON 요약이어야 하며 배열을 MPI로 모으지 않는다.

```bash
python code/launch_manufactured.py \
  --manifest contract/MANUFACTURED_TASKS.json \
  --execution serial --backend reference \
  --ranks 1 --threads 1 --binding none \
  --output /absolute/create_only_result.json
```

OpenMPI native 경로는 `--execution mpi --backend native --native-library /absolute/libc2f.so --ranks 2 --threads 2 --binding none --mpiexec /absolute/mpiexec`처럼 명시한다. 설치된 OpenMPI 환경이 필요한 경우 기존 `ncp_build_deps/env.sh`를 먼저 source한다. 이 실행기는 도구체인을 설치하거나 reference/backend로 자동 전환하지 않는다. `auto` mpiexec는 PATH 탐색만 하며 MPI 실행 자체를 자동 선택하지 않는다.

- 최상위 exact keys: `schema`, `physical_launch_enabled`, `cases`, `limits`.
- schema는 `bass-he.c2f.manufactured.v1`, `physical_launch_enabled`는 literal false.
- case exact keys: `case_id`, `seed`, `n_rows`, `rank`, `angle`; 1–64개.
- case_id: ASCII 안전 basename `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}`, 중복 금지.
- seed: 정수 0–2^63−1; rank: 정수 1–6; n_rows: 정수 2 rank+1–65536; angle: 유한 실수 [0,1.2] rad.
- limits exact keys: `wall_seconds`, `memory_gib`, `max_ranks`, `max_threads_per_rank`. 양의 wall ≤86400 s, memory ≤128 GiB, 정수 max_ranks/max_threads 각각 1–64. 실제 수치 범위와 실행량은 별도의 현재 manifest에 의해 더 좁혀진다.
- Python bool을 정수 입력으로 허용하지 않는다. 중복 JSON key, 추가 key, NaN/Infinity, physical-launch 요청을 거절한다.

호스트 진입점은 pre-MPI affinity, 물리 core topology, cgroup v2의 현재 membership과 보이는 조상별 CPU/memory 제한 및 `/proc/meminfo`를 읽는다. ranks×threads가 quota와 affinity의 최소 CPU 예산을 넘으면 실행하지 않는다. 메모리 예산은 시작 시점 가용 RAM보다 작아야 한다. 보이지 않는 cgroup 또는 v1-only 제한은 자동 추정하지 않고 거절한다. 각 MPI rank는 부모의 고정 preflight 예산을 사용하되, 실제 affinity가 요청한 threads를 수용하고 부모 affinity 안에 있는지 확인한다. 따라서 정상적인 rank binding으로 affinity가 작아졌다는 이유만으로 전체 host를 작은 서버로 오인하지 않는다.

`--binding none`은 OMP_PROC_BIND=FALSE이고 `--binding core`는 OMP_PROC_BIND=close/OMP_PLACES=cores이다. 두 경우 모두 OMP_NUM_THREADS 명시, OMP_DYNAMIC=FALSE, BLAS/NumExpr 각 1 thread를 강제한다. core binding은 실제 물리 core 수와 rank간 affinity 비중첩까지 검사한다. serial은 정확히 1 rank; MPI는 실제 mpi4py/Open MPI 버전과 communicator 크기를 검사하고 localhost 하나에 no-oversubscribe로 실행한다. callback은 case_index % size의 결정적 rank-stride로 정확히 한 번 배정한다. 입력·Python 코드·native library의 SHA256과 크기를 모든 rank에서 대조하고 실행 후 변경도 거절한다.

출력은 create-only다. `result.json.runtime/`를 배타 생성한 뒤 manifest snapshot, launch context, command, stdout/stderr, worker result를 보존하고 최종 result.json은 fsync된 임시파일의 atomic link로 만든다. 기존 출력 또는 companion directory가 있으면 덮어쓰지 않는다. 실패나 timeout은 FAIL evidence이며 PASS로 승격하지 않는다. 선행 preflight가 실패해도 확보된 companion directory와 최종 failure JSON이 남는다.

watchdog는 50 ms 간격으로 소유 프로세스들의 RSS 합을 관찰한다. PID namespace, NSpid/NSpgid/NSsid, process start time을 사용하므로 outer procfs PID를 syscall PID로 오인하지 않는다. 소유성은 매 실행의 무작위 inherited token과 관찰된 자손 관계로 확정하며 이미 포착된 identity는 setsid/reparenting 뒤에도 유지한다. 따라서 OpenMPI rank나 별도 session 자손을 원래 process group 바깥이라는 이유로 누락하지 않는다. timeout/메모리 초과 후에는 identity를 다시 확인한 pidfd를 통해 해당 프로세스만 종료한다. 이 설계는 C2d `process_guard.py`의 namespace/start-time/pidfd 방식을 사용하고 세션 제한을 제거해 소유 자손 전체를 추적한다.

RSS 합은 공유 페이지를 중복 계산할 수 있으며 샘플 사이의 순간적 최고값이나 엄격한 allocation upper bound를 인증하지 않는다. 외부 프로세스의 RAM 사용량 변화도 전체 host의 제약을 바꿀 수 있다. 실행기가 생존하는 동안의 협력적 manufactured workload에 대한 watchdog이며, 악의적 코드가 token을 지우고 첫 관찰 전에 이중 fork로 탈출하는 것을 막는 보안 sandbox는 아니다. NCP64 scaling, 물리 정확도, 생산 성능은 이 실행기의 PASS가 뜻하는 바가 아니다.

런타임 단위/경계 테스트에는 exact schema, CPU/memory 초과 거절, backend fallback 부재, create-only, rank-strided 소유, callback 예외/NaN/과대 요약, 실제 subprocess timeout, 별도 session 자손의 RAM 집계·종료, 무관한 프로세스 생존을 포함한다. 실제 Fortran/OpenMPI callback 비교는 루트 통합 검증에서 별도로 수행한다.
