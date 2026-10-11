# NCP 단일 노드 cell 병렬 실행

이 경로는 기존 full-history 계산의 **실행 비용과 checkpoint 저장량**을 줄인다. 물리 provider, source/opacity 식, native gas RHS, Newton solver, step-doubling controller, 허용오차와 정규화는 유지한다. 실제 시간 이력은 순차적이다. 코어 수가 늘어도 필요한 시간 단계 수가 줄어들지는 않는다.

## 구현 범위

| 부분 | 실행 방식 |
|---|---|
| Source 적분, coarse → half1 → half2, Newton 반복 | 기존 순차 계산 |
| 각 map의 cell preparation·고정 gas에서의 absorption | 지속 process actor에 분배 |
| SIGMA 연결·refinement 임시 기록 | worker마다 독립 소유 |
| PreparedIncident | 해당 worker에 map 동안 보관, Newton마다 재전송하지 않음 |
| cell 결과 조립·native RHS·합산·ledger | 원래 cell 순서, 단일 coordinator |
| 승인 이력 | immutable seed + 승인된 두 경계의 append-only segment |
| 출력·journal·checkpoint 게시 | coordinator 한 개, create-only 원자적 게시 |

`ordered_cell_pool.py`는 `spawn`으로 worker를 만들며, 고정 순환 배치로 cell을 분배한다. Python pipe와 native SIGMA 연결을 공유하는 threading은 사용하지 않는다. worker 오류·timeout은 기록 후 종료하며 자동 재시도하지 않는다. worker가 죽은 경우에도 SIGMA 자식 process group을 정리한다. SIGMA subprocess는 별도 물리 trajectory가 아니다.

전체 prefix를 매 generation 재기록하던 저장 비용은 새 accepted pair와 manifest만 쓰도록 바꿨다. 기존 seed는 보존하고 각 segment는 이전 manifest hash에 연결된다. 원래 initial-state 기준 ledger·누적 extrema·출력 소유권을 유지한다. 빠른 restart는 seed/latest payload 및 과거 manifest chain·파일명·크기를 확인한다. 과거 모든 NPZ의 byte 검증은 별도 `verify_history()` 또는 `iter_states()`/export 시 수행된다. 빠른 restart를 전체 byte 재검증이라고 부르지 않는다.

## 환경과 비공개 입력

공개 branch에는 소스·제조 테스트·운영 문서만 추가한다. 실제 checkpoint, source payload, 실행 결과, 백업 위치·object ID 및 이전 비공개 커밋은 새 공개 변경에 넣지 않는다. 이전부터 공개되어 있던 저장소 이력 전체를 소급 정리하는 작업은 포함하지 않는다.

필요 환경은 Linux/POSIX, Python 3.12, NumPy 2.3.5 및 private seed에 담긴 **원래의 두 hash-pinned native 실행파일**이다. worker마다 BLAS/OpenMP thread는 1이다. 메모리 제한은 현재 cgroup-v2와 보이는 상위 cgroup의 남은 허용량, host available memory 중 작은 값으로 확인한다. CPU affinity와 명시한 여유 코어도 상한으로 사용한다. 지원하지 않는 cgroup layout 또는 부족한 자원은 실행 전에 실패한다.

별도 private handoff의 ZIP와 SHA-256을 사용한다. 공개 코드에 인증정보나 private locator를 쓰지 않는다.

```bash
export REI_REPO="$PWD"
export REI_PYTHON="$REI_REPO/.venv/bin/python"
export HPC="$REI_REPO/research/accel02_20261011/q1b/hpc"
python3.12 -m venv .venv
"$REI_PYTHON" -m pip install -r "$HPC/requirements-hpc.txt"

# REI_PRIVATE_SEED, REI_PRIVATE_SEED_SHA는 private handoff에서 설정한다.
"$REI_PYTHON" "$HPC/restore_private_seed.py" \
  --archive "$REI_PRIVATE_SEED" --sha256 "$REI_PRIVATE_SEED_SHA" --repo "$REI_REPO"
```

복구 helper는 모든 ZIP member와 기존 목적 파일을 먼저 확인한다. 다른 내용의 파일을 덮어쓰지 않으며, 기존 JSON의 절대경로를 고치지 않는다. preparer가 명시한 parent repository 안에서 역사적 경로를 해석한다. 공개 checkout 소스와 seed의 frozen 소스가 다르면 자동 덮어쓰기·hash 교체 없이 중단한다. 바이너리가 해당 노드에서 실행되지 않으면 기존 binary identity를 보존한 상태로 환경/ABI 문제를 분류한다. 임의 재빌드 후 기존 checkpoint가 같은 실행이라고 주장하면 안 된다.

## 경량 검증과 노드별 worker 선택

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1
"$REI_PYTHON" -m pytest "$HPC/tests" -q
"$REI_PYTHON" "$HPC/resource_plan.py" --workers 48
```

`resource_plan.py`의 기본 worker는 8, 상한은 48이다. 기본 메모리 계산은 coordinator 8 GiB + worker당 1 GiB + reserve 8 GiB이고, 두 CPU를 예약한다. 이는 보수적인 계획값이며 측정된 최대 RSS 보장이 아니다. prepare와 각 chunk 시작에서 같은 계획을 강제한다. 지정한 worker 수가 맞지 않으면 조용히 줄이지 않는다.

private handoff에 제공된 완료 baseline의 source/binary/parent identity와 RESULT·LAUNCH의 외부 SHA pin을 사용한다. `benchmark_workers.py`는 저장된 serial 결과를 재사용하고, 요청한 각 worker 수에 대해 새 candidate map만 한 번씩 실행한다. serial baseline이나 기존 전체 과학 캠페인, 초기 h=0 계산을 반복하지 않는다. 생산 cursor나 예산은 바뀌지 않는다.

8·16·32·48 중 실제 affinity와 메모리에 맞는 후보를 비교해 가장 짧은 측정 시간을 선택한다. 서로 다른 노드의 serial elapsed를 NCP speedup 계산에 사용하지 않는다. 구성당 단일 표본과 startup을 포함한 결과이므로 확정적인 scaling 법칙이나 ETA가 아니다. 상세 명령과 선택 절차는 `NCP_CODEX_HANDOFF_KO.md`에 있다. `validate_parallel_map.py`는 baseline을 처음 만드는 두-map 검증 helper이며, 이미 제공된 검증을 반복하기 위한 단계가 아니다.

```bash
export REI_PARENT=research/accel02_20261011/q1b/c13/evidence/C2_FULL005
```

## Production 준비와 실행

원래 parent가 소진된 상태에서 새 누적 할당을 만든다. 기본 신규 할당은 10,000회이며, 과거 완료·거부·외부 실패 debit을 유지한다. 첫 NCP 작업의 wall budget은 12시간을 제안한다. 할당량 증가는 별도 새 identity가 필요하며 현재 한도를 자동 연장하지 않는다.

```bash
# 측정으로 고른 정수값. 예시는 8이며 64를 기계적으로 넣지 않는다.
export REI_CELL_WORKERS=8
export REI_WORK="$REI_REPO/var/ncp_full_history_001"
"$REI_PYTHON" "$HPC/prepare_hpc_run.py" \
  --parent-repo "$REI_REPO" --parent-root "$REI_PARENT" --work-root "$REI_WORK" \
  --additional-attempts 10000 --cell-workers "$REI_CELL_WORKERS"
bash "$HPC/run_ncp.sh" --transition-bundle "$REI_WORK/HPCMETA/TRANSITION_RESULT.json" \
  --new-attempt-cap 32 --wall-s 1800
```

이 명령을 **완료된 chunk의 `RESULT.json`을 확인한 뒤** 같은 bundle로 이어서 호출한다. `CHUNK_ATTEMPT_BOUNDARY` 또는 `CHUNK_WALL_BOUNDARY`이면 새 시도만 진행할 수 있다. `REACHED_FULL_TARGET`, `ALLOCATION_EXHAUSTED`, signal stop, zero progress, 최초 실패 또는 reconciliation 필요 상태에서는 멈춘다. `CHUNK_RECOVERED_COMMIT_BOUNDARY`도 결과를 분류한 뒤 재개한다. 실제 전체 wall budget은 각 chunk의 elapsed와 준비/백업 시간을 포함해 관리한다.

SIGTERM/SIGINT와 wall limit은 cooperative stop이다. 이미 시작한 trial을 완료·기록하거나 실패를 보존하고 다음 trial을 시작하지 않는다. 강제 종료·노드 장애로 남은 미완료 journal은 자동 재실행하지 않는다. 원자적으로 완성된 checkpoint가 있으면 정확한 transaction만 계산 없이 reconcile할 수 있다. 계산 중에는 source/input tree, runtime config, dependency files를 수정하지 않는다.

NCP의 persistent volume에 `REI_WORK`와 원래 private seed를 보존한다. 각 승인 pair는 즉시 durable checkpoint가 된다. 외부 백업은 chunk 종료 후에 archive를 완성하고 별도 프로세스로 archive identity를 확인한 다음 기존 private 목적지에 올린다. 계산/패키징/업로드를 같은 작업 경로에서 겹치지 않는다. upload ACK와 실제 원격 복구 검증은 구별한다. 백업 metadata와 원시 결과는 공개 push 대상에서 제외한다.

이미 Slurm을 제공하는 환경에만 `ncp64.sbatch`를 쓸 수 있다. 일반 NCP VM에는 Slurm 설치를 가정하지 않으며 `run_ncp.sh`를 사용한다. Slurm 예시는 단일 task에 64 CPU, 120 GiB, 계산 12시간과 종료 여유를 요청한다. 서버 생성·과금·SSH 접속은 이 코드가 수행하지 않는다.

## 결과의 한계와 반환

현재 생산 범위는 기존 C2 history의 원래 끝시간과 exact 129 epochs까지다. `REACHED_FULL_TARGET`은 C2 history 도달이며, 전구간 Time9·C2/C3 spectral/angular 수렴의 통과가 아니다. 65/129 선택을 각각 유지하고 각 field own-fine 최대값으로 정규화하며 fine 진폭이 0이면 차이도 정확히 0이어야 한다. 기존 Time9 2e-6, spectral/angular24 1e-3, initial-origin energy/nH ledger 1e-9, geometry 1e-11 및 나머지 기준을 완화하지 않는다. Bianchi·BASS·CR/RCT의 별도 판정은 이 실행으로 승격하지 않는다.

반환물에는 code commit, binary/source/control identity, 새 binding, 마지막 cursor·manifest, 수행/수용/거부/실패·진단/생산 계수, 출력 epoch, 원래 ledger, 측정 시간·메모리·worker 설정, 종료 사유와 durable backup receipt를 넣는다. 실패가 있으면 원본 첫 실패를 유지한다. 원래 parent를 변경하지 않으므로 rollback은 새 child를 보존한 채 종료하는 것으로 충분하며 원래 checkpoint를 다시 계산할 필요가 없다.

기술 참고: [Python multiprocessing](https://docs.python.org/3.12/library/multiprocessing.html), [Slurm sbatch](https://slurm.schedmd.com/sbatch.html). 실제 Slurm 옵션 지원은 설치된 버전에서 확인한다.
