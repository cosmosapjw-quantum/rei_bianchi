# C2g 물리 참조 pilot 실행 계약

이 실행기는 C2f의 manufactured runner와 별도다. `physical_contract.py`가 닫힌 JSON schema를 검증하고, `launch_reference.py`가 현재 호스트 예산을 확인한 뒤 `run_reference.py`의 유한기저 전자 고유상태 계산만 실행한다. 기존 `runtime_support.py`, `launch_manufactured.py`의 process guard 함수는 수정하지 않았다.

## 실행 전 고정하는 입력

- Manifest는 task ID, R, 원자핵 전하, m, 각운동량 cutoff, box, 차수, quadrature, tol, maxiter, root 수 및 **해결된 모든 radial knot**를 명시한다. 경계는 0부터 rmax까지 엄격히 증가하고 두 핵의 radial 위치를 정확히 포함해야 한다. `elements`는 원래 mesh 인수이고, 실제 element 수는 `len(boundaries)-1`로 따로 기록한다.
- Preregistration 경로는 manifest 디렉터리 아래의 상대 경로다. 탈출하는 `..`, 절대 경로 및 symlink를 거부한다. 원본 바이트의 SHA256를 manifest가 지정한다.
- 별도의 review JSON은 `status=PASS`, reviewer, manifest SHA256, preregistration SHA256를 정확히 지정한다. Draft의 `physical_launch_enabled=false`로는 실행하지 않는다.
- `numpy / serial / 1 rank / 1 thread / binding none`, `native / OpenMPI / 2 ranks / 1 thread / binding none`만 허용한다. 이 제한과 함께 **읽어 들인 preregistration의 campaign.layouts**에 실제 조합이 존재하는지도 launcher와 worker가 각각 확인한다. 단순히 2×4 상한 이내라는 이유로 다른 조합을 허용하지 않는다.

Manifest hard ceiling은 12 task, 실제 요청 root 54개, 300초, sampled RSS 4 GiB, 최대 2 rank와 rank당 4 thread다. 현재 pilot의 실제 thread 수는 두 조합 모두 1이다. campaign의 2개 layout, 24 sector solve, 독립 root 108개 누계는 root의 실행 ledger가 관리한다. 이 실행기는 **각 launch의 상한**만 강제하며 다른 output 디렉터리까지 합한 전역 quota라고 주장하지 않는다.

Native backend는 명시적인 `--native-library`를 요구한다. Launcher는 상속된 `BASS_NATIVE_LIBRARY`와 `BASS_NATIVE_EXPECTED_SHA256`를 지우고 선택한 절대 경로와 측정한 hash만 worker에 전달한다. NumPy backend에는 두 변수가 전달되지 않는다. Import 이전부터 `.so` 바이트·build metadata·현재 `element_assembly.f90` hash·ABI 3·strict flags를 확인한다. 이 pilot의 strict flags는 `-O3 -std=f2008 -fPIC -shared -fopenmp -fno-fast-math -ffp-contract=off -fno-associative-math -Wall -Wextra`이다. Build metadata는 기록된 provenance이며 그 자체가 compiler를 다시 실행한 증명은 아니다. 실제 API의 ABI 검사와 provider의 실행 전후 identity 확인을 함께 사용한다.

## 호출

다음 명령의 경로는 실제 고정된 manifest·review·새 output으로 바꾼다. Native 실행에서는 환경에 해당 OpenMPI와 Fortran shared runtime이 이미 설정되어 있어야 한다. 사용할 수 없으면 실패하며 serial 또는 NumPy로 자동 전환하지 않는다.

```sh
python code/launch_reference.py \
  --manifest contract/PHYSICAL_TASKS.json \
  --review review/PHYSICAL_LAUNCH_APPROVAL.json \
  --execution serial --backend numpy --ranks 1 --threads 1 --binding none \
  --output /absolute/new_numpy_result.json

python code/launch_reference.py \
  --manifest contract/PHYSICAL_TASKS.json \
  --review review/PHYSICAL_LAUNCH_APPROVAL.json \
  --execution mpi --backend native --ranks 2 --threads 1 --binding none \
  --native-library /absolute/native/build/libbass_element.so \
  --mpiexec /absolute/orterun \
  --output /absolute/new_native_result.json
```

## 산출물과 실패 보존

Output은 새 파일이어야 하고 `OUTPUT.runtime` 디렉터리도 새로 만든다. `launch_context.json`은 입력, 전체 local Python와 native source/build script, 선택한 native binary/build metadata, 실제 CPU affinity·cgroup·메모리, MPI version과 command를 고정한다. 각 worker는 동일 identity, MPI size, 호스트, thread 환경, affinity 및 binding을 확인하고 `task_index % mpi_size` 순서로 task를 단독 소유한다.

각 task는 `OUTPUT.runtime/tasks/TASK_ID.npz`와 `TASK_ID.json`을 남긴다. NPZ는 provider가 임시 파일 fsync 및 create-only 방식으로 저장한다. Receipt도 독립적으로 즉시 atomic/create-only 저장한다. 성공 receipt는 원본 source ID·바이트 수·SHA256·상태 ID, 에너지, algebraic residual, 작은 projected operator와 mass Gram을 포함한다. 배열 전체는 MPI root로 gather하지 않는다. 작은 요약만 gather하며 provider 반환 요약은 64 KiB를 넘지 못한다. 실패한 task의 예외·traceback 및 존재하는 partial archive identity를 보존하고 후속 task를 처리한다. 이미 존재하는 파일은 덮어쓰지 않는다.

Worker 종료 후 입력·source·native identity를 다시 확인한다. Launcher도 재확인하고 stdout/stderr, task receipt 목록, worker 결과 identity와 process 상태를 저장한다. `attempted_task_count`와 `successful_sector_count`를 구별한다. 요청 root 수는 실패해도 `requested_eigenstate_count`이며 실제 완료 root 수라고 바꾸어 쓰지 않는다.

상속된 guard는 PID namespace/start-time과 unique token 또는 관찰된 ancestry로 소유 프로세스를 식별한다. 새 session으로 분리된 소유 자식도 유지 추적하고 pidfd 재확인 후 종료한다. 50 ms마다 소유 프로세스 RSS 합을 측정하므로 shared page 중복 계산이 가능하며 정확한 allocation cap이나 실제 peak 보장은 아니다. timeout 또는 메모리 상한 위반 때 이미 기록된 task receipt는 남는다. 이 pilot은 단일 현재 호스트 실행이고 NCP64 scaling 증거가 아니다.

Launch/worker의 `PASS`는 계약·실행·아카이브 보존 성공이다. 물리적 projector/guard gap/convergence 승인에는 별도의 사전등록된 분석이 필요하다. 유한 generalized matrix residual은 PDE 또는 continuum residual 증명으로 해석하지 않는다.

## 새 범위에 맞춘 검증

`tests/test_physical_runtime.py`의 17개 test는 실제 고유상태 계산 없이 닫힌 schema, 경계와 핵 위치, 중복 task와 budget, duplicate JSON key/NaN, review hash, 경로 탈출, 정확한 두 layout과 prereg binding, host ceiling, native strict flag/source/binary tampering, rank 소유권과 즉시 receipt, provider/import 실패, create-only/no-launch 동작을 검사한다. 기존 C2f process-guard test는 변경되지 않은 dependency이므로 다시 실행하지 않았다. 이 문서는 본 agent가 물리 계산을 실행했다는 기록이 아니다.
