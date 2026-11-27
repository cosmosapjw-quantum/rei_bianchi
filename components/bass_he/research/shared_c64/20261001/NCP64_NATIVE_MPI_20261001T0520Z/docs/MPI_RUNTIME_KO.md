# NCP 실행 계층

`launch_ncp.py`는 단일 NCP 호스트의 실제 affinity, 가시적인 cgroup v2 CPU quota·메모리 한도, 현재 MemAvailable, Linux가 보고하는 core/package 번호를 읽는다. 광고된 64 CPU를 64 물리 코어로 가정하지 않는다. 가상 머신 안의 topology 역시 물리 장비의 증명은 아니다. cgroup v1이나 확인할 수 없는 core topology에서는 실행을 차단한다.

기본 동작은 검증된 명령의 JSON 출력이다. `--execute`를 명시하면 OpenMPI를 실행한다. 출력 디렉터리는 존재하지 않아야 한다.
PATH의 `mpirun` 대신 별도 설치본을 사용할 때는 `--mpirun /absolute/path/to/mpirun.openmpi`를 지정한다. root 실행 허용은 기본 명령에 포함하지 않는다.

```bash
python code/host_probe.py
python code/launch_ncp.py --manifest configs/tasks.json --output-dir results/new_run --backend native --ranks 16 --threads 4
python code/launch_ncp.py --manifest configs/tasks.json --output-dir results/new_run --backend native --ranks 16 --threads 4 --execute
```

위 `configs/tasks.json`은 사용자가 실행할 연구 노드에 맞춰 먼저 확정한 task manifest 경로다. performance_example.json은 배치 후보의 설명이며 task manifest가 아니다. 이 문서 자체는 새로운 R 격자나 연구 노드를 승인하지 않는다.

명령은 `--host localhost:S --map-by slot:PE=T --bind-to core --nooversubscribe --report-bindings`를 사용한다. 모든 rank의 예약 core 수 `ranks × threads`가 확인된 core budget 안에 들어야 한다. OpenMP는 T개, BLAS·NumExpr는 각각 1개 thread로 고정한다. 정확도에 관련된 solver tolerance·격자·quadrature는 manifest에 주어진 값 그대로 task worker에 전달한다. fast-math나 오차기준 완화는 실행 계층이 도입하지 않는다.

rank 수가 2 이상이면 rank 0은 controller이고 나머지 N−1개 rank가 작업 완료 순서에 따라 다음 task를 받는다. rank 1개 실행은 동일 task worker를 순차 호출한다. mpi4py 또는 OpenMPI가 없을 때 몰래 순차 모드로 대체하지 않는다. 작업은 subprocess로 분리되며 wall timeout 시 해당 process group을 종료한다. 새 Python wrapper에서 RLIMIT_AS를 설정한 뒤 task worker를 exec하므로 MPI 초기화 후 preexec_fn을 호출하지 않는다. RLIMIT_AS는 가상 주소 공간의 상한이며 RSS 예측값과 다르다.

메모리는 확인된 여유량의 최소 20%를 남긴다. worker당 limit은 **설정된 상한**으로 기록하며 측정한 peak RSS라고 부르지 않는다. 다중 rank에서 controller용 0.5 GiB도 예산에 넣는다. 예를 들어 여유 메모리가 정확히 128 GiB라도 worker 31개 × 4 GiB는 headroom 조건을 넘어서므로 차단한다. Python·MPI 관리 프로세스 자체의 메모리는 환경에 따라 다르며 20% 여유와 controller 예산은 OS 수준 예약을 보장하지 않는다. 메모리 snapshot 뒤 다른 작업이 시작될 가능성도 남는다.

manifest는 schema=1, tasks, limits만 허용한다. task는 안전한 고유 task_id와 solve kwargs인 parameters를 갖는다. limits는 양의 유한 `per_worker_memory_gib`, `task_wall_seconds`다. JSON 중복 key, NaN/Infinity, 중복 task_id, 경로 탈출 ID를 거부한다. 원본 manifest byte SHA와 Python float의 정확한 round-trip 표현을 포함한 task SHA를 모두 보존한다. 반올림한 R 값으로 cache key를 만들지 않는다.

모든 rank는 시작 시 전체 Python·Fortran 코드와 native shared library·빌드 JSON의 내용 hash, 입력 원문 hash, backend, Python 경로, MPI library 및 thread 설정이 같은지 확인한다. `BASS_NATIVE_LIBRARY`로 선택한 외부 library도 실제 byte hash와 대응 build manifest의 일치를 확인한다. shared filesystem을 전제로 하며 rank마다 다른 코드나 입력은 실행 전에 차단한다. 기존 결과 재사용은 이 버전에서 비활성화했다. 기존 output 폴더에는 쓰지 않으며 task별 원자적 create-only JSON, fsync, stdout/stderr, 실패 원인, 실제 결과 artifact hash를 남긴다. exit 0만으로 성공을 인정하지 않고 RESULT.json의 status=PASS와 task_id·backend·입력 byte SHA·parameters 일치를 요구한다. 이 PASS는 task worker의 수치·구현 검사이며 상위 과학적 승격을 뜻하지 않는다.

동적 스케줄의 완료 순서는 달라질 수 있으나 BATCH_SUMMARY.json은 항상 원본 task 순서다. 각 task는 독립 subprocess에서 같은 입력을 계산하므로 task 사이의 MPI floating-point reduction이 없다. 병렬 Fortran kernel 내부의 부동소수점 순서는 해당 kernel의 검증 계약으로 관리한다. worker 프로세스 실패·timeout은 기록하고 나머지 task를 처리한 뒤 배치 exit code를 실패로 반환한다. MPI rank 자체 또는 호스트 전체의 강제 종료는 OpenMPI abort 영역이며 자동 재시작을 주장하지 않는다.

성능 후보는 1×1, 8×1, 16×1, 32×1, 64×1, 32×2, 16×4다. 같은 확정 task set과 같은 정확도 조건으로 실행하고 실제 worker 수, warmup 여부, 배치 wall time, task별 시간, peak RSS를 기록한다. rank 0 비용과 subprocess startup 비용을 포함한 throughput을 단일 계산 속도와 분리한다. 최소 세 번 측정한 중앙값과 범위를 비교하고 실제 CPU·메모리 gate를 통과한 후보만 선택한다. NCP 실제 host에서 측정하기 전 64-core speedup 수치를 주장하지 않는다.

`python -m unittest discover -s tests -p test_runtime.py -v`는 물리 계산 없이 실제 subprocess를 사용해 실패·timeout·결과누락·덮어쓰기 차단, atomic 경쟁 쓰기, 입력 identity와 자원 gate를 검사한다. 실제 MPI 다중 rank 및 native/reference 과학 계산의 검증은 별도 통합 증거에 기록한다.


초기 identity는 task 시작 전과 종료 후에 다시 대조한다. native 자식에는 초기 `BASS_NATIVE_LIBRARY`와 `BASS_NATIVE_EXPECTED_SHA256`을 강제로 전달한다. RESULT의 code/reference SHA 목록, native SHA·build metadata, STATE 파일의 크기·SHA도 초기 계약과 대조한다. 따라서 시작 시 rank 일치만 확인한 뒤 실행 중 변경을 놓치는 결과는 PASS로 받지 않는다. `--host localhost:S`에서 S=ranks×threads는 이미 CPU budget으로 검증한 slot 수다. OpenMPI 4.x가 localhost를 1 slot으로 해석하는 경우에도 검증된 slot 수를 명시하며 `--nooversubscribe`를 유지한다. 이 host 지정은 외부 scheduler host 목록이 이 단일-host 예산을 넘어 자동 배분되지 않게 한다.

## 동일 작업 배치의 자동 성능 비교

`benchmark_layouts.py`는 사용자가 확정한 동일 manifest를 각 layout에서 최소 3회 실행한다. 기본은 계획 출력이며 `--execute`가 있어야 계산한다. 각 실행에 새 폴더를 만들고 전체 MPI job timeout, launcher 로그, task 결과·실패 기록을 보존한다.

```bash
python code/benchmark_layouts.py --manifest configs/tasks.json --output-dir results/ncp_layout_sweep --backend native --layouts 1x1,8x1,16x1,32x1,64x1,32x2,16x4 --repeats 3 --job-timeout-seconds 1800
python code/benchmark_layouts.py --manifest configs/tasks.json --output-dir results/ncp_layout_sweep --backend native --layouts 1x1,8x1,16x1,32x1,64x1,32x2,16x4 --repeats 3 --job-timeout-seconds 1800 --mpirun /absolute/path/to/mpirun --execute
```

1×1 baseline은 필수이며 먼저 실행한다. 같은 task의 energy·residual·mass_norm 차이가 각각 절대값 2e−10 이하인지, 기존 residual≤1e−9와 norm error≤1e−10 조건을 만족하는지 확인한다. 시작된 layout에서 한 번이라도 실패하면 해당 layout을 거절한다. native library·코드 변경 역시 거절한다. 안정적인 물리 mass 행렬을 artifact에서 복원하는 인터페이스는 없으므로 state coefficient의 물리 L² 비교는 `NOT_CHECKED_NO_STABLE_MASS_IN_ARTIFACT`로 기록한다. 에너지·잔차 parity로 상태 norm parity까지 인증하지 않는다.

보고서는 같은 task set의 MPI batch wall time 중앙값·최솟값·최댓값, throughput, 1×1 대비 speedup을 산출한다. fresh subprocess startup은 batch time에 포함되며 launcher 전체 시간은 별도 기록한다. warmup 제외는 하지 않는다. 모든 반복을 통과한 layout 중 측정상 가장 빠른 것을 추천 데이터로 제시하고 production 기본값은 변경하지 않는다. 실제 NCP 접근 및 성능 sweep 실행 전에는 추천 layout과 64-core speedup이 확정되지 않는다.

Backend는 `native`, `numpy`, `reference` 중 하나를 명시한다. `numpy`는 최적화된 NumPy 구현, `reference`는 고정 기준 구현이다. 어느 backend도 다른 것으로 자동 대체하지 않는다. 같은 backend의 layout sweep을 먼저 비교하며 backend 간 비교가 필요하면 각각 새 output 폴더와 같은 task manifest를 사용한다. Fortran backend가 모든 작업에서 가장 빠르다고 가정하지 않는다.
