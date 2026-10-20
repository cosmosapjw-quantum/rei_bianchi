# CODEX NCP 실행 인계 — 독립 이력 병렬 backlog

## 현재 판정과 남은 실행

기존 수치 source를 보존하는 자원 제한 process scheduler와 실행·재개·병합 경로를 구현했다. 독립 C9의 기본 판정은 `PASS_SCOPED_RESOURCE_AWARE_ORCHESTRATION`이며, root가 발견한 build concurrency 상한의1..4→1..64 교정은 별도 표적1건 PASS 후 같은 review episode의 `review/ROOT_REPAIR_ADDENDUM.json`에서 독립 PASS/residual blocking0으로 닫았다. Root가 최종 구현과 동일 episode의 build64 addendum을 ACCEPTED_SCOPED로 채택했다. 실제 게시·백업 상태는 FINAL_DELIVERY.json과 FINAL_PUBLICATION_ACK.json을 따른다.

| Identity/상태 | 값 |
|---|---|
| 기존 metadata 기준 HEAD | `96aaad584bbecded34485526a4bb53a49708ffc6` |
| 현재 Radau scientific source | `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf` |
| VigilODE pin | `8a8bd409b1d96c7b7421f496d229e119fd3d284e` |
| 새 병렬 구현의 게시 commit | `d234243a79e4e8e611aaf4ac61949c5ef9111468` |
| 새 병렬 구현의 archive/Drive/Dropbox/ACK | `ARCHIVE_AND_ACK_DUAL_FULL_GET_PASS — FINAL_PUBLICATION_ACK.json` |
| V12/V13/SSPRK 전체 backlog의 NCP 실행 | `NOT_RUN` — 현재 도구 quota0/SSH key 부재 |
| production | `NOT_ISSUED` |

현재 source524의19설정, borrowed N2 및 original V14 84는 이미 NCP에서 완료했다. 이번 기본 backlog는 이들을 제외한다. V13의84이력과 original V14의84는 서로 다른 실행 집합이다. 새 과학 모델 수는0이다.

## 복사해서 실행할 한 명령

기존 허가된 NCP checkout의 repository root에서 다음 명령을 실행한다. checkout의 미커밋 내용을 보존하고 clone/worktree/reset/clean을 수행하지 않는다. 실행 전 실제 HEAD, dirty 상태, 도구 버전과 현재 파일 hash를 기록한다. 게시된 병렬 구현이 기존 checkout에 없으면 root의 실제 게시/복구 receipt가 가리키는 파일을 작업 전용 경로에 준비하며 dirty 파일을 덮어쓰지 않는다.

```bash
env -u CARGO_TARGET_DIR python3 \
  research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/campaign_cli.py all \
  --input-root research/lrs_atomic_native_bridge_20261016 \
  --work-root /tmp/rei_lrs_parallel_20261020 \
  --cargo cargo --build-jobs 64 --max-workers 64 \
  --nominal-job-memory-mb 512
```

이 명령 자체는 추가 shell wrapper 없이 source 준비→variant별 build→표적 tests→native backlog→exact matrix 병합→기계 분석을 실행한다. offline Cargo cache와 기존 toolchain을 사용하며 runner가 설치·네트워크 source 회수를 자동 수행하지 않는다. 필요하면 해당 복구 runtime의 `CARGO_HOME`/동적 library 경로를 process 환경으로 지정하고 `--cargo`에 그 invocation 절대경로를 준다. compiler 버전은 실제 receipt로 기록한다.

먼저 계획만 보려면 동일 명령의 `all`만 `plan`으로 바꾼다. 동일 명령을 다시 실행하면 일치하는 manifest/source/input/executable/output/log에 묶인 완료 결과만 재사용한다. 기존 계획을 직접 재개하는 경로는 `campaign_cli.py run --work-root /tmp/rei_lrs_parallel_20261020 --max-workers 64 --nominal-job-memory-mb 512`다. build jobs는 manifest identity에 포함되므로 기존2-job 계획을64-job으로 덮어쓸 수 없다. 의도적으로 운영 계획을 바꾸면 기존 결과를 보존하고 새로운 work root를 명시한다.

## 정상 source 복원과 target 격리

입력 root는 `research/lrs_atomic_native_bridge_20261016`이다. V12는 그 아래 `v12/native_owner`를 작업 디렉터리로 복사한다. V13은 원래 `v13/RESTORE_NATIVE.py --base <input-root>/v12/native_owner --out <work-root>/variants/v13/native_owner` 경로를 사용한다. SSPRK2는 원래 `v14/time_centered_ssprk2_20261019/restore_ssprk2_native.py`와 V14→V13 복원 chain을 사용한다. script/spec/patch/native payload 및 V12 base의 실제 closure가 identity에 포함된다.

각 variant의 Cargo target은 `<work-root>/targets/{v12,v13,ssprk}`다. inherited `CARGO_TARGET_DIR`는 제거하고 variant별 target만 설정한다. 같은 이름의 crate를 공유 target에 섞지 않는다. 원본152 native 파일, append hook, VigilODE477파일/pin/lock, provider/EoS/FD/GL2 birth/허용오차/기본 수치 동작은 변경하지 않는다. V12/V13의 원본 example은 보존하고 exact source SHA에 묶인 새 selector-only example만 컴파일한다. history 내부 계산 순서와 산술은 원문 그대로다.

이미 로컬에서 복구한 runtime의 참고 위치는 `lrs_parallel_20261020/runtime_recovery/restored/repo_payload/research/lrs_atomic_native_bridge_20261016`, toolchain은 `runtime_recovery/toolchain/bin/{cargo,rustc}`, Cargo cache는 `runtime_recovery/restored/cargo_home`이다. 이는 현재 scratch의 경로이며 NCP에 그 경로가 존재한다고 가정하지 않는다. NCP의 실제 복원 root/toolchain/cache 경로를 receipt에 남긴다.

## 246 DAG jobs와 자원 계약

| 실행 집합 | 고정 설정/수 | cap |
|---|---|---|
| V12 | 3cases×8modes×6N=144 native histories; cells8 | charged native process wall 합180s |
| V13 | X=1e-5/1e-4×7modes×6N=84 native histories; cells32/tol1e-15 | X별 합180s |
| SSPRK2 | 원본 transport1/fixed1/birth1 명령; transport52행, coupled6+10이력 | 합300s; 개별60/180/180s |

source prepare3 + build3 + targeted-test3 + native command231 + merge3 + analysis3 = **246 jobs**다.231 native commands는144+84+3이며 SSPRK의 세 명령을16개 개별 process로 바꾸지 않는다. 각 variant build는180s, V12/V13 표적 tests는240s, SSPRK tests는120s의 finite cap이다. cap 소진/실패는 실제 상태로 남기며 임의로 tolerance나 cap을 확대하지 않는다.

요청 사양은64 CPU/128GB다. 실제 실행 상한은 allowed affinity, 유한 cgroup CPU quota, 사용자 max64와 관측 메모리로 제한한다. 명령의 `--build-jobs 64`는 Cargo build/test에 `-j 64`,64개의 서로 겹치지 않는 CPU slot 및64GiB nominal reservation을 요청한다. native worker는 각각1slot/512MiB nominal이다. build/test와 native가 같은 자원 pool을 공유하고 기본 DAG는 variant 준비/build/tests를 먼저 끝낸다. OMP/OPENBLAS/MKL/RAYON/VECLIB/NUMEXPR와 transport threads는1이다.

메모리는 host MemAvailable, cgroup raw remaining, 관측 inactive_file만 더한 회수 가능 estimate, 선택적 사용자 cap을 구분하고 보수적인 상한의20%를 reserve한다. 따라서 전체128GB 사양만으로64GiB build admission을 보장하지 않는다. 실제64CPU/메모리 예약을 수용할 수 없으면 임의로 build concurrency를 줄이지 않고 `NOT_RUN_RESOURCE_ADMISSION`과 관측값을 남긴다. nominal reservation은 측정 peak RSS가 아니다.

과거 동일 설정 CSV 마지막 elapsed가 있으면 긴 job 우선 queue의 입력으로 재사용하고, 없으면 N 큰 순서 heuristic으로 표시한다. 과거 wall은 실제 NCP 소요 예측이나64CPU 가속비가 아니다. 완료 process wall과 active elapsed를 aggregate에 charge하며 timeout은 해당 child process group만 정리한다. 모든 실패/부분 attempt와 polling/teardown overshoot를 보존한다.

## 결과 판정과 반환물

실행 exit0은 모든 DAG node가 COMPLETED/검증된 REUSED_COMPLETED라는 운영 상태다. 전체 backlog의 과학적 수용은 exact matrix, 분석 결과와 기존 물리 기준을 root가 검토한 뒤 별도로 판정한다. 가짜 child tests나 원래 audit의 과거 reviewer 문자열을 새 과학 검증/독립 심사로 세지 않는다.

V12 merge는144keys/12,096rows/46columns, V13은 각X42keys/3,528rows/31columns와 step1..N을 검사한다. V12 기본 분석은 stdlib coverage/관측 residual·normalization summary와 기존 `v12/evidence/analysis/NATIVE_ANALYSIS.json` 등 saved analysis/reference의 identity 연결이다. SciPy/numpy analyzer의3 reference IVP를 자동 재적분하지 않는다. reference가 없으면 absent로 남긴다. V13은 기존 stdlib analyzer, SSPRK는 원본 CSV/sidecar를 bytes 그대로 alias한 뒤 원래 Decimal audit를 실행한다. SSPRK coverage는16histories/2488macro/6456segments/3968births/2048cells다.

실행 후 다음을 원문과 hash로 반환한다.

1. 실제 checkout HEAD/dirty 상태, scientific/restored source·derived selector·pin/lock·binary hash, host/OS/toolchain/affinity/quota/memory 관측.
2. `MANIFEST.json`, `RESOURCE_PREVIEW.json`, `run/RESOURCE_PLAN.json`, `run/CAMPAIGN_RECEIPT.json`과 각 attempt의 inputs/argv/stdout/stderr/exit/outcome/raw CSV 및 sidecar.
3. exact matrix merge와 분석 원문, 기존 saved reference의 경로/hash·부재 상태, 실제 새 실행/reuse/실패/차단 수.
4. archive의 bytes/SHA256/manifest와 실제 provider 저장 IDs, 두 provider 전체 GET byte/hash 대조 및 실제 ACK receipt. 미수행 provider write나 readback을 완료라고 기록하지 않는다.

## 완료한 경량 근거와 승인 상한

로컬 실제 native는 profile3 + 대표 V12/V13 shard2 + 기존3설정 serial/parallel3쌍18 =23회다. Python 기존21 tests PASS 뒤 build64 표적1건만 추가 PASS했다. 대표 shard의576finite+24other, scheduler의9casepairs non-timing 결과는 차이0이다. profile-off 전체 scheduler phase의 local paired ratio 중앙값2.199360426은 이 host/세 기존 이력의 관측이며 NCP64 scaling이나 solver/RHS 가속을 뜻하지 않는다. 전체 backlog의 NCP 실행과 전체 기계 분석은 아직 NOT_RUN이다.

source-on 일반2차, uniform stiff accuracy, 일반 양수성, Case B/full EoR, signed Bianchi, 넓은 positive-CMB/비영 boundary, continuous global certificate 및 CSV에 없는 완전 photon ledger는 HOLD다. default legacy/성능 경로 cell-cache/borrowed 실험 지위를 유지한다. production은 NOT_ISSUED다.

## NCP 실행 agent에게 주어진 연결 권한

사용자가 지정한 연결은 `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`다. 이 명령을 사용자에게 수동 수행하도록 요구하지 않는다. 실제로 인증 가능한 실행 환경의 agent가 기존 checkout 상태를 먼저 읽고 작업한다. key가 없는 sandbox나 quota가 소진된 원격 도구에서 접속/실행을 수행했다고 기록하지 않는다.

## 최종 게시·백업 identity

- 구현·결과 source commit: `d234243a79e4e8e611aaf4ac61949c5ef9111468`. 최종 metadata HEAD는 이 파일을 포함하는 commit이다.
- Archive: `REI_LRS_PARALLEL_C10_20261020.tar.xz`, 7,654,920bytes, SHA256 `388ef80e25fef7905e44fcc1aaf6179c6332b41fdf7c7e07233f51b805e608ac`. Drive `1yK1fsc_-ybJ59l8VYDvIARrpZtTIWbc5`, Dropbox `id:BSpOijBcT10AAAAAAD_aKw`.
- ACK: `REI_LRS_PARALLEL_C10_ACK_20261020.json`, 6,391bytes, SHA256 `05c4bd684818cbc65b89a3f4091cdfb0c87a6902117ea954d0ded60f1774539e`. Drive `19mpts1yDKBtp02K6qOpG9C_dolyfDt4H`, Dropbox `id:BSpOijBcT10AAAAAAD_aLQ`.
- Archive와 ACK 각각 양쪽 전체 GET/bytes/SHA256 일치. Archive343 regular files/manifest342개+self1개 PASS. Drive origin HTTP NOT_EXPOSED/materialization200, Dropbox HTTP200, 실제 회수 process exit0.
- archive는 기존 검증된 dependency/base 위에 repo_payload를 overlay하는 delta이며 단독 복원본이 아니다. 포장 시점 PENDING은 별도 ACK와 FINAL_PUBLICATION_ACK.json이 닫는다.
- 실제 source524의 NCP19/borrowedN2/originalV14 84 완료를 유지한다. 이번 V12/V13/SSPRK backlog는 NOT_RUN_BLOCKED_EXECUTION_ACCESS다.
