# NCP 실행 및 다음 C2 인계

과학 STOP은 C1B_R2_REFERENCE_CONVERGENCE_CLOSED로 유지한다. 이 패키지는 새 물리 결과보다 같은 문제를 빨리 풀기 위한 구현 변경이다. 다음 과학 node는 여전히 C2_FINITE_R_COUPLING_NUMERICAL_AUDIT이며 실행 전 exact R-grid·허용오차·continuation 계약을 고정한다.

먼저 NCP에서 host를 확인하고 strict native binary를 그 호스트에서 빌드한다. 현재 패키지의 binary는 검증 증거이며 임의 호스트로 이식할 기본 실행물이 아니다. 아래 명령은 패키지 루트 기준이다. Python3.12 환경에서 requirements.txt의 NumPy/SciPy/mpi4py를 설치하고 GNU Fortran·OpenMPI runtime/development packages를 준비한다. MPI가 MPICH에 연결되면 실패로 처리한다.

```bash
python -m pip install -r requirements.txt
python native/build.py --mode strict --native
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python native/test_native.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tests/test_solver_equivalence.py
python code/host_probe.py
python code/launch_ncp.py --manifest configs/MPI_PARITY_TASKS.json --output-dir runs/parity3 --backend native --ranks 3 --threads 1 --execute
```

소규모 parity fixture는 실행 경계 확인용이며 64코어 처리량 평가용이 아니다. 최적화가 같은 입력으로 더 빨라지는지 tests/benchmark_solver.py와 operator benchmark를 기록한다. 과거 closed 과학 suite를 전부 반복하지 않는다.

C2의 승인된 충분한 독립 작업 목록이 준비되면 code/benchmark_layouts.py로 같은 manifest를 1×1, 8×1, 16×1, 32×1, 64×1, 32×2, 16×4에서 최소3회 측정한다. launcher가 host CPU·memory budget 초과 layout을 거부한다. rank0 controller를 제외한 worker 수와 부족한 task 수를 고려한다. --execute 없이 명령 검토, --execute로 실행한다. 메모리가 허용하지 않는 layout을 통과시키기 위해 task cap을 낮추지 않는다. 충분히 측정한 작업 범위별 RSS/가상주소 공간 envelope를 먼저 확정한다.

OpenMP는 rank 내부 Fortran kernel만 사용하고 BLAS는 기본1 thread다. 입력·코드·compiler·flags·binary와 topology를 함께 기록한다. 각 실행 디렉터리는 create-only이며 v1 resume는 제공하지 않는다. worker subprocess의 시작 비용이 작은 작업을 압도하면 이후 node에서 검증된 coarse task batching을 추가한다. 현재 eigenvalue routine 자체는 분산 구현이 아니며 독립 eigenstate 처리량을 MPI로 늘린다.

상태 연결은 완료 순서가 아닌 physical overlap으로 수행한다. L_O=L_B+z_B p_x, 독립 direct/force 식, norm/residual, spatial/domain/order/quadrature convergence를 유지한다. rank 병렬성·Fortran 구현은 연속계 오차 인증을 제공하지 않는다.

scientific_PROMOTE=HOLD; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.
