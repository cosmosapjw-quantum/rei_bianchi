# NCP 실제 접속 사전 확인

2026-10-15T12:40Z에 소유자 PC를 경유해 **실제 NCP** SSH 읽기 전용 확인을 완료했다. 소유자 PC는24CPU이고 NCP와 다른 장치다. 프로젝트 기존 접속 성공 기록의 identity를 재사용했으며 private key 내용은 읽지 않았다. 새 인증정보나 별도 사용자 승인은 필요하지 않다.

| 실제 관측 | 결과 |
|---|---|
| NCP host | s1a0e5abed09 |
| CPU | 64 logical / affinity0–63 / guest가 노출한 physical core pair64 |
| CPU model | Intel Xeon Gold5220 |
| RAM | 135,050,518,528 bytes total;132,983,582,720 available |
| Swap |0 |
| root disk free |42,965,680,128 bytes |
| OS / libc | Ubuntu24.04.1 / glibc2.39 |
| 부하 | loadavg .106/.050/.044 |
| 기존 REI task root의 실행 중 작업 |0 |
| axbi/reionization/rei_microphysics/cargo/rustc 프로세스 |0 |
| cgroup | 해당 session 및 부모 CPU quota=max, memory.max=max; cpuset0–63 |
| 기본 PATH Rust |cargo/rustc 없음 |
| 기존 별도 toolchain |cargo1.94.1/rustc1.94.1, 실제 --version exit0 |

상태는 **HOST_AVAILABLE_SOURCE_AND_REPRESENTATION_GATES_PENDING**이다. 8aa6cd081f218e3a4ff6180a547c790df234a073은 이번 조사 baseline이며 새 covariant 소스는 NCP의 과거 staging에 없다. 현재 transport worker의 최종 representation/refinement가 완료되면 이미 받은 승인으로 fresh 실행한다. 인프라 접속은 blocker가 아니다.

## 다음 실행에서 쓸 실제 경로

- 새 create-only task: `/root/REI_FLRW_COVARIANT_20261015_001` (이번 관측에서 미존재)
- source: 위 task의 `stage/`
- target: 위 task의 `target/`
- output: 위 task의 `runs/FLRW_DONOR_COVARIANT_FULL_001`
- 재사용 가능한 toolchain: `/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001/toolchain`

기존 `performance/*/run_ncp.sh`는 완료된 10월14일 부품 benchmark다. 이를 전구간 런처나 미사용 할당으로 해석하지 않는다. 과거 task, ZERO mirror, checkpoint와 queue는 보존한다.

최종 source archive에는 crate전체 src와 Cargo.toml/lock, example, 아래 include_str 의존성과 최종 config/source provenance를 포함한다:

- `docs/fastest_track_chat/REI-AXBI-GOAL-20261014/OUTPUT_CONTRACT.json`
- `research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json`
- `research/axbi_goal_20261014/scenario/AX05_NUMERICAL_CONTRACT.md`
- `research/flrw_production_integration_20261015/configs/hyrec_donor_full.cfg`
- 최종 worker가 추가한 covariant 파일 및 `SOURCE_SHA256SUMS.txt`

archive member는 이 repo-relative layout 그대로이며 상위 포장 directory는 없어야 한다. 전체2GB git clone을 옮길 필요가 없다. 현재 crate에는 외부 Cargo dependency가 없다.

## 비밀정보 없는 root용 전송 recipe

다음은 **실행하지 않은 recipe**다. `REI_FROZEN_ARCHIVE`와 `REI_FROZEN_SHA256`에는 root가 최종 검증 후 동결한 archive의 owner-PC 경로와 해시를 넣는다. owner repo 자체에는 쓰지 않는다. 원격 주소와 identity 경로는 이미 있는 프로젝트 접속 기록에서 읽어 연결 인수로만 사용하고 출력하지 않는다.

```python
import hashlib, json, os, pathlib, shlex, subprocess
record = pathlib.Path("/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/research/axbi_goal_20261014/execution/NCP_ACCESS_RECOVERY_20261014.json")
saved = json.loads(record.read_text())
old = shlex.split(saved["command"])
identity = old[old.index("-i") + 1]
ssh = ["ssh", "-T", "-i", identity, "-o", "IdentitiesOnly=yes",
       "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
       "-o", "StrictHostKeyChecking=yes", "-o", "UpdateHostKeys=no",
       "-o", "ControlMaster=no", "-o", "ControlPath=none",
       "-p", "22", saved["user"] + "@" + saved["host"]]
archive = pathlib.Path(os.environ["REI_FROZEN_ARCHIVE"])
assert hashlib.sha256(archive.read_bytes()).hexdigest() == os.environ["REI_FROZEN_SHA256"]
task = "/root/REI_FLRW_COVARIANT_20261015_001"
command = ("umask 077; mkdir " + shlex.quote(task)
           + " && mkdir " + shlex.quote(task + "/stage")
           + " && tar -xzf - -C " + shlex.quote(task + "/stage")
           + " && cd " + shlex.quote(task + "/stage")
           + " && sha256sum -c SOURCE_SHA256SUMS.txt")
with archive.open("rb") as source:
    subprocess.run(ssh + [command], stdin=source, check=True)
```

이 전송은 새 task가 이미 있으면 mkdir에서 중단한다. 실패한 partial namespace를 덮거나 기존 source를 바꾸지 않는다. 실행 전에 archive 자체의 안전한 member path와 모든 member hash 검증은 root의 동결 과정에서 수행한다.

## 정확한 NCP build/native 명령

다음 build는 새 source가 위 위치에 동결·전송된 뒤 원격에서 실행한다. 현재 조사에서는 build도 시작하지 않았다.

```bash
REI_NCP_TASK=/root/REI_FLRW_COVARIANT_20261015_001
REI_NCP_TC=/root/REI_AXBI_GOAL_20261014_32d11e733155/performance/temperature_rate_table_001/ncp_validation_001/toolchain
env RUSTC="$REI_NCP_TC/bin/rustc" RUSTDOC="$REI_NCP_TC/bin/rustdoc" \
  LD_LIBRARY_PATH="$REI_NCP_TC/lib" CARGO_TARGET_DIR="$REI_NCP_TASK/target" \
  CARGO_BUILD_JOBS=4 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  "$REI_NCP_TC/bin/cargo" build --release --locked --offline \
  --manifest-path "$REI_NCP_TASK/stage/rust/rei_microphysics/Cargo.toml" \
  --example axbi_reionization
```

CLI의 실제 argv 계약은 확인했다. 최종 representation/refinement 통과와 binary/config/source 해시 동결 후 실행할 fresh native argv:

```bash
/root/REI_FLRW_COVARIANT_20261015_001/target/release/examples/axbi_reionization \
  --config /root/REI_FLRW_COVARIANT_20261015_001/stage/research/flrw_production_integration_20261015/configs/hyrec_donor_full.cfg \
  --output /root/REI_FLRW_COVARIANT_20261015_001/runs/FLRW_DONOR_COVARIANT_FULL_001 \
  --case FLRW_DONOR_COVARIANT_FULL_001
```

`--resume`는 넣지 않는다. 초기 xHII=.000210349192936/Tgas9.306042400380866 K의 새 상태이며 기존 checkpoint에 source/IC를 덮지 않는다. 위 cfg는 PR150의 전구간 후보로 아직 covariant admission을 뜻하지 않는다. worker가 config에 새 표현 필드를 추가하면 그 최종 bytes/hash를 전송해야 한다.

현재 config의 유한 상한은800000steps,2600000attempts,200M RHS,43200s cooperative wall,4096MiB 출력이다. 제안되는 host 계약은 전체64CPU 이하·전역 동시 과학 case최대2·합계112GiB 메모리(약13.8GiB reserved), 두 case면 case당 AS56GiB다. native가 현재 단일 스레드이면 기본 OMP/BLAS/Rayon1을 유지하고64-way 성능을 주장하지 않는다. 동시 case가 있으면 resource합계를 확인한다. toolchain4-worker build는 scientific case와 구분하되 총 사용량에 포함한다.

12h 시작시각/deadline은 최초 campaign에 지속 기록한다. 개별 `max_wall_s`는 cooperative 경계이므로 각 launch의 남은시간에서300s closeout reserve를 빼서 고정하고, 재개 때12h를 초기화하지 않는다. root는 실제 메모리·output cap과 남은 wall budget을 `prlimit/taskset/timeout` 및 final RUN_BINDING에 고정해야 한다. 이 제안은 현재 예약이나 실행이 아니다.

이번 수행은 SSH metadata/read-only version 조회뿐이며 원격 과학실행0, 원격 build0, owner repo 및 NCP 파일·git 변경0이다. 로컬에는 동반 JSON과 이 보고서만 작성했다.
