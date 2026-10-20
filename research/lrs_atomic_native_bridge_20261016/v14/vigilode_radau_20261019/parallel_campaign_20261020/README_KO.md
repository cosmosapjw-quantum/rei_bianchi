# LRS 독립 이력의 bounded 병렬 실행

기존 V12/V13/SSPRK2의 NCP 재현 backlog를 여러 독립 process에 배정한다. source 복원과 build는 variant마다 한 번 수행하고 history 내부의 연산·합산 순서는 바꾸지 않는다. 새 rate cache나 solver는 도입하지 않는다. 기본 legacy, 현재 Radau의 성능 경로 cell-cache, borrowed의 명시적 실험 지위를 유지한다.

## NCP의 기존 checkout에서 한 명령

```bash
env -u CARGO_TARGET_DIR python3 research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/campaign_cli.py all \
  --input-root research/lrs_atomic_native_bridge_20261016 \
  --work-root /tmp/rei_lrs_parallel_20261020 \
  --cargo cargo --build-jobs 64 --max-workers 64 \
  --nominal-job-memory-mb 512
```

기존의 허가된 NCP 환경과 offline Cargo cache를 사용한다. 새 clone/worktree, 기존 checkout의 reset/clean, 파일 덮어쓰기는 하지 않는다. `--work-root`는 이 작업 전용 경로로 지정한다. 같은 manifest/source/input/executable와 검증된 완료 출력이면 같은 명령으로 재개할 수 있다. build jobs처럼 manifest를 바꾸는 옵션을 바꾸면 기존 결과를 보존한 채 identity mismatch로 거절한다. 자원 한도 `--max-workers`, `--memory-limit-mb`는 실행 자원이며 과학 입력을 바꾸지 않는다.

먼저 계획만 보려면 `all`을 `plan`으로 바꾼다. 기존 계획을 실행·재개하려면 `run --work-root ...`를 사용한다. `--reference-root`는 `v12/evidence`와 `v13/evidence`가 있는 이미 회수한 과거 자료의 상위 경로다. 없으면 input-root의 기존 자료를 확인하고, 없는 reference를 새로 적분해 만들지 않는다. 현재 sandbox에서는 NCP 연결 quota와 SSH key의 제한 때문에 이 명령의 실제 NCP full campaign을 실행하지 않았다.

선택적인 복구 toolchain을 쓸 때는 해당 환경의 CARGO_HOME과 필요한 동적 library 경로를 process 환경에 지정하고 `--cargo`에 실제 cargo invocation 경로를 준다. Rust 버전을 임의로 gate하지 않는다. 실제 실행의 compiler 버전·argv·환경과 결과로 호환성을 판단한다. 네트워크 install이나 source 다운로드는 이 runner가 자동으로 하지 않는다.

## 기본 backlog와 완료된 작업의 제외

| Variant | 고정 입력 | 실행 단위 | Native aggregate cap |
|---|---|---:|---:|
| V12 | 3 cases × 8 modes × N=8..256, cells8 | 144 histories | process wall 합180 s |
| V13 | X=1e-5/1e-4 × 7 modes × N=8..256, cells32, tol1e-15 | 84 histories | 각 X별 process wall 합180 s |
| SSPRK2 | 원본 transport 명령, fixed 명령, birth 명령 | transport52행 + coupled16 histories | 합300 s; 개별60/180/180 s |

원래 current Radau19, borrowed N2, original V14 84는 NCP 완료이므로 기본 backlog에서 제외한다. 이 재현 작업을 새 과학 모델로 집계하지 않는다. V12 photon-free clock에 current Radau seeded-disabled를 대입하지 않는다. V13의 cells32 설정을 과거 cells8 자료와 같은 설정으로 비교하지 않는다.

전체 DAG는 source prepare3, build3, targeted-test3, native command231, merge3, analysis3의 **246 jobs**다. V12/V13의 한 native command는 history 하나다. SSPRK의 두 coupled command 안에는 원래6+10 histories가 그대로 있다. tests는 V12의 기존 axbi_driver/axbi_covariant_transport/v12_thermal_clocks, V13에 v13_source_clocks 추가, SSPRK의 기존14개 tests를 사용한다. BASS fixture가 없는 전체 workspace test를 대신 실행하지 않는다.

## 원본 source와 shard

`shards.py`는 원본 example의 SHA256을 먼저 확인한다.

- V12: `2ec4ef9c9830dae400328f49e8bf343f23be4cae839e12b62a2a7f6cbd3fea27`
- V13: `70029e2b2ada5ba9f2a7fee01c5c346c5d69cafe49db813e7202a642363745d5`

원본 example 파일은 바꾸지 않고 새 `v12_clock_shard.rs` / `v13_clock_shard.rs`를 만든다. 필수 환경 입력 `LRS_SHARD_CASE`, `LRS_SHARD_MODE`, `LRS_SHARD_N`과 허용 집합 검사는 CSV 파일을 만들기 전에 수행한다. history body와 step loop는 원문 그대로다. V13 while-loop skip guard는 `n *= 2; continue;`를 수행한다. 삽입 부분을 역으로 제거한 bytes가 원문과 정확히 같은지 검사하고 selector diff/receipt를 남긴다. `derived_examples/`는 실제 bounded compile에 사용한 같은 source bytes다.

V13은 원래 `RESTORE_NATIVE.py`, SSPRK는 원래 `restore_ssprk2_native.py` → V14 → V13 restore chain을 사용한다. restore script/spec/patch/native payload의 실제 입력 closure와 V12 base를 identity에 포함한다. source 입력이 바뀌면 이미 남아 있는 derived output을 현재 작업의 성공으로 재사용하지 않는다.

Cargo target은 **variant별 전용 경로 `work/targets/{v12,v13,ssprk}`**다. 외부 CARGO_TARGET_DIR를 상속하지 않는다. 실제 local 최초 공유 target 시도에서 V12 build는 성공했으나 V13 example이 V12 library artifact를 참조해 SourceClockConfig import 오류가 났다. 같은 V13 원문을 private target에서 다시 빌드하자 성공했다. 실패 기록은 보존했고 수치 source를 바꾸지 않았다.

## 자원과 재개

Linux allowed affinity, cgroup CPU quota, 사용자 상한64를 함께 적용한다. native job에는 서로 겹치지 않는 CPU slot 하나를 주고 transport/Rayon/OMP/BLAS threads는1이다. compiler job은 지정된 CPU slot 수와 같은 Cargo build concurrency를 쓰며 전체 실행 pool을 공유한다. 기본 DAG에서는 준비/build/test를 variant별로 차례로 완료한 뒤 native backlog가 시작된다. `--build-jobs`는1..64를 허용한다(default1). 위 명령은 build/test에64 CPU slot과64GiB nominal memory를 예약하며 Cargo `-j 64`를 사용한다. native worker는 각각512MiB nominal이다. 64 CPU/128GB는 요청 사양이고 관측된 자원이 아니다. 실제 CPU pool 또는20% reserve 뒤 memory가 이 예약보다 작으면 build를 임의 축소하지 않고 NOT_RUN_RESOURCE_ADMISSION으로 기록한다. 이때 출력 경로를 보존한 채 실제 자원과 명시적인 새 운영 계획을 검토한다.

메모리는 host MemAvailable, cgroup `memory.max - memory.current`, **관측된 inactive_file만 더한 회수 가능 estimate**, 사용자 memory limit을 구분해 기록한다. 이 중 보수적인 상한에20% 여유를 두고 nominal reservation으로 admission한다. active_file/kernel/slab를 막연히 가용 메모리에 더하지 않는다. nominal reservation은 실제 측정 peak RSS가 아니다. memory 부족으로 admission할 수 없으면 NOT_RUN_RESOURCE_ADMISSION과 관측값을 남긴다.

과거 CSV의 각 history 마지막 elapsed가 있으면 긴 job을 먼저 배정하는 입력으로 사용한다. 없으면 N 큰 순서 heuristic이며 초 단위 NCP 예측이 아니다. 동적 queue는 사용 가능한 CPU slot에 다음 ready job을 배정한다. 완료 process wall과 active elapsed의 합을 aggregate에 charge하고 cap에 닿으면 해당 active process group을 종료하고 새 launch를 중단한다. polling/teardown overshoot도 그대로 기록한다.

각 attempt는 별도 폴더이고 argv 배열, 실제 executable hash, source/input identity, affinity, stdout/stderr, exit, elapsed, output/log hash를 보존한다. timeout은 `start_new_session`으로 만든 해당 process group만 종료한다. 완료 상태·입력/executable·출력/log가 모두 일치한 경우에만 재사용한다. 실패/부분 attempt는 덮어쓰지 않는다. 복원 입력의 mismatch는 완료된 dependent까지 현재 DAG에서 BLOCKED로 전파하며 과거 결과는 보존한다.

## 병합과 분석

V12는 원래(case,mode,N,step) 순서로144keys/12,096rows/46columns, V13은 X별42keys/3,528rows/동일31열 header와 정확한step1..N을 검사한 뒤 병합한다. 누락/중복/예상 밖 key/header 오류는 분석 전에 실패한다. 여러 variant의 CSV를 하나의 물리 합으로 섞지 않는다.

V12 기본 분석은 표준 라이브러리만 사용한다. coverage, 원래 residual 진단과 electron/종별 normalization의 관측 잔차를 요약하고 기존 `evidence/analysis/NATIVE_ANALYSIS.json` 등 saved analysis/reference를 hash와 경로로 연결한다. 기존 SciPy/numpy analyzer의 세 reference IVP를 자동으로 다시 적분하지 않는다. reference가 없으면 그 의무를 absent로 기록한다. 새 tolerance나 science PASS를 만들지 않는다.

V13의 원래 stdlib analyzer는 exact matrix merge 뒤 실행한다. SSPRK는 fixed/birth 파일과 sidecar를 원본 bytes 그대로 별도 alias 디렉터리에 대응시켜 원래 Decimal audit를 실행한다. 그 프로그램의 과거 reviewer/sandbox metadata는 과거 문자열이며 새 독립 검토가 아니다. 현재 mechanical receipt는 이 구분과 alias mapping, 실제 새 데이터의16history/2488macro/6456segment/3968birth/2048cell coverage를 기록한다.

## 실제 경량 검증과 범위

`EXECUTION_REPORT_KO.md`와 `EXECUTION_SUMMARY.json`을 읽는다. local 검증은 대표 V12/V13 shard 각각1개와 기존 saved CSV 비교, process orchestration 표적 tests, current c93 binary의 기존3설정 serial/parallel3쌍이다. 전체144/84/SSPRK backlog의 NCP 성공을 미리 주장하지 않는다.

source-on 일반2차, uniform stiff, 일반 양수성, Case B/full EoR/signed Bianchi, 넓은 positive-CMB/비영 boundary, global certificate와 CSV에 없는 완전 photon ledger는 기존 HOLD다. production은 NOT_ISSUED다. 실행 exit0·coverage 통과와 과학적 승인, local 관측과 NCP64 scaling을 구분한다.
