# REI coordinator — 2026-10-20 source-pinned NCP 인계

이 문서는 `cosmosapjw-quantum/rei_bianchi`의 현재 실행 준비가 끝난 작업만 조정한다. 사용자는 기존 허가된 NCP/local 환경에서 컴파일·필요한 작은 호환 수정·실제 실행, 결과 GitHub 게시와 Drive/Dropbox 백업을 요청했다. 사용자에게 파일 다운로드·압축해제·전달을 맡기지 말고 Codex가 기존 인증과 connector/rclone을 사용한다. 같은 source/config의 반환된 결과가 있으면 재실행보다 ingest를 우선한다.

## 0. 실제 실행 전 단일 coordinator 점검

1. `physmath-research-loop`, 실제 최신 repo `AGENTS.md`, 아래 고정 metadata와 해당 branch 최신 HEAD를 읽는다. source와 delivery metadata를 각각 기록한다. 최신 commit이 있으면 delta를 읽고 새 결과 여부를 먼저 판정한다.
2. 현재 checkout의 dirty 상태·작업 중인 process와 할당을 확인한다. 다른 thread/repo의 owner job을 변경하거나 같은 작업을 중복 시작하지 않는다. host가64cores/128GiB라도 각 lane은 자체 cap을 유지한다. age32의48transport workers는 BASS/HE/WU의48–64worker 실행과 동시에 자원을 초과 배정하지 않는다. 현재 실행 중인 작업을 종료하지 말고 가능한 자원 범위에서 순서를 정한다.
3. 기존 checkout을 사용하고 필요한 source는 task-owned 새 디렉터리에 `git archive`로 추출한다. 기존 checkout `reset/clean`, force-push, production merge는 하지 않는다. source archive 복원은 기존 제공자에서 자동 수행하고 SHA/manifest를 검증한다. 실제 toolchain/runtime은 receipt에 남긴다.
4. 아래 A/B 두 lane 외에 R9·RUN13·과거 age64·RUN19 benchmarks 등을 자동 재실행하지 않는다. 다음 연구방법이 아직 미구현인 branch에는 native campaign을 새로 만들지 않는다.
5. 단계 시작 시 source/config/cap을 고정하고, 단계 종료 시 stdout/stderr/exit/raw/receipt와 DAG를 남긴다. 오류·cap·NOT_STARTED를 성공으로 바꾸지 않는다. 같은 할당에서 자동 재시도하거나 원 deadline을 새로 잡지 않는다.

현재 read 기준: PR198 `91a65b33774d948d924c357ac4ad290918d8b9ee`, PR199 `5ef6766c66b319e48612f316ac1581bd12f6ebfc`, PR211 `c9deb933761a8d2593d1176aee028cd423bdbc05`, PR208 `54948439be7039c9b2b1f9580bee69bebeb80129`, PR151 `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`.

## A. LRS V14: 새 최적화 source NCP 실행

Branch: `research/rei-lrs-v14-physical-birth-20261018`.

최신 상세 인계와 원래 caps:
https://github.com/cosmosapjw-quantum/rei_bianchi/blob/91a65b33774d948d924c357ac4ad290918d8b9ee/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/continuation_20261020b/CODEX_NCP_EXECUTE_KO.md

실행 source는 `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`, VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`다. 과거 `d87ba9ca...` source19settings NCP 결과는 완료되어 있으나 새 source의 NCP 결과는 이 intake 시점에 NOT_RUN이다. 새 결과가 이미 생겼으면 아래 명령 대신 그 source-bound result를 회수한다.

현재 빠른 검증 경로는 `cell-cache`다. `cell-borrowed`는 clone 제거는 검증됐지만 가속은 입증되지 않았으므로 같은 binary에서 fixed RadauN2 하나만 호환 확인한다. 기존 default는 legacy로 유지한다.

```bash
set -euo pipefail
REI_REPO="$(git rev-parse --show-toplevel)"
REI_BRANCH='research/rei-lrs-v14-physical-birth-20261018'
REI_SOURCE_SHA='5248822167e3fbe374f4333f7f2efdcdbfdaeeaf'
git -C "$REI_REPO" status --short
git -C "$REI_REPO" fetch origin "+refs/heads/$REI_BRANCH:refs/remotes/origin/$REI_BRANCH"
git -C "$REI_REPO" cat-file -e "$REI_SOURCE_SHA^{commit}"
REI_JOB_ROOT="/tmp/rei_lrs_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$REI_JOB_ROOT/input"
printf '%s\n' "$REI_SOURCE_SHA" > "$REI_JOB_ROOT/EXEC_SOURCE_SHA.txt"
git -C "$REI_REPO" archive "$REI_SOURCE_SHA" research/lrs_atomic_native_bridge_20261016 |
  tar -x -C "$REI_JOB_ROOT/input"
REI_INPUT_ROOT="$REI_JOB_ROOT/input/research/lrs_atomic_native_bridge_20261016"
REI_ADAPTER_ROOT="$REI_INPUT_ROOT/v14/vigilode_radau_20261019"
set +e
env -u CARGO_TARGET_DIR python3 "$REI_ADAPTER_ROOT/prepare_and_run.py" \
  --input-root "$REI_INPUT_ROOT" --output-root "$REI_JOB_ROOT/run" \
  --cargo cargo --all --native-eval cell-cache \
  > "$REI_JOB_ROOT/launcher.stdout" 2> "$REI_JOB_ROOT/launcher.stderr"
REI_EXIT=$?
set -e
printf '%s\n' "$REI_EXIT" > "$REI_JOB_ROOT/EXIT_CODE.txt"
test "$REI_EXIT" -eq 0
```

4unit+6integration 표적시험,10Radau+9SSPRK 설정, case40s/native합180s를 유지한다. runner가 pin과 manifest를 회수한 뒤 offline/locked build한다. 기존 source/cache가 있으면 상세 인계의 `--vigilode-source`, `--cargo-home`, `--offline`을 사용한다. 환경 `CARGO_TARGET_DIR`가 runner 경로를 바꾸지 않도록 제거한다. 결과가0이 아닐 때 아래 dependent 명령은 실행하지 말고 raw와 실패 상태를 보존한다.

```bash
REI_CASE_BINARY="$REI_JOB_ROOT/run/adapter/target/release/rei-vigilode-radau-research"
REI_CPU="$(python3 -c 'import os; print(min(os.sched_getaffinity(0)))')"
set +e
timeout -k 2s 40s taskset -c "$REI_CPU" "$REI_CASE_BINARY" \
  "$REI_JOB_ROOT/borrowed_fixed_n2.json" fixed radau 2 --native-eval cell-borrowed \
  > "$REI_JOB_ROOT/borrowed.stdout" 2> "$REI_JOB_ROOT/borrowed.stderr"
REI_BORROWED_EXIT=$?
set -e
printf '%s\n' "$REI_BORROWED_EXIT" > "$REI_JOB_ROOT/BORROWED_EXIT_CODE.txt"
```

Cache/borrowed의 physical fields, charged_rhs_attempts, occupied_cell_preparations, node_visits를 대조한다. timing·mode·clone counters는 별도다. 실제 NCP binary SHA를 저장하고 sandbox binary SHA `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`와 동일해야 한다고 가정하지 않는다. 숫자 동등성이 signed-zero bit identity나 full EoR 정확도 승인이 아니다.

자동 복원 가능한 archive:

- Base: Drive `1TV56tJoJXkK4XyFTXTrnTgCtfDDOTJzT`, Dropbox `id:BSpOijBcT10AAAAAAD_SPg`, `REI_LRS_OPTIMIZATION_C10_20261020.tar.gz`,53269577bytes, SHA256 `623797d7a8b83b078f10ffaad780c7b2c223247e8b5593110c8d5f52286991b0`.
- Delta: Drive `1Dxj_adZQR4QEuxxatozwG10AMtvQw0z5`, Dropbox `id:BSpOijBcT10AAAAAAD_SWQ`, `REI_LRS_BORROWED_C10_20261020B.tar.xz`,7540740bytes, SHA256 `492681e5ed7f1f53820b3bdcf24f397cfedbb6dac20a1d6dd917c7a9e2aa866e`.
- Dropbox parent `/bianchi/research_backups/rei_bianchi/`. Delta만으로 base source를 대체하지 않는다.

## B. Age32: 기존 age64 기준에 한 사례 추가

Branch: `research/rei-age-exposure-envelope-20261018`; task `research/rei_age_exposure_envelope_20261018/`.

https://github.com/cosmosapjw-quantum/rei_bianchi/blob/5ef6766c66b319e48612f316ac1581bd12f6ebfc/research/rei_age_exposure_envelope_20261018/HANDOFF_CODEX_CURRENT_KO.md

위 CURRENT handoff·README_CURRENT·contracts/NEXT_DAG_CURRENT.json·DELIVERY_RECEIPT_CURRENT.json을 먼저 읽는다. v8 source `02767dc5e6c4b47883f590834aee38530852568d`의 고정 모형612checks와 mean-age bounds는 완료다. native age32 결과를 대신하지 않는다.

원래 native physics `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`; B1 binary SHA `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`; computational SHA `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`; prepared SHA `e376b58ee3ef2b14cda70bc8d966d686db52aabc0a832cab0b8cc0ea8a430bfd`를 preflight한다.

기존 task-owned repo `/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/repo`, 기준 run `/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/run`, venv `/root/REI_AGE_ENVELOPE_20261018T132700Z/venv`를 우선 사용한다. 새 code는 git archive로 새 `/root/REI_AGE32_REFERENCE_<UTC>/code`에 추출한다. Python3.12.3/NumPy2.3.5/SciPy1.17.0, Rust1.99.0, transport48/BLAS1와 원 binary binding을 확인한다. runtime/source/binary mismatch를 receipt 변경으로 숨기지 않는다.

기준이 없으면 사용자에게 복원을 요구하지 않고 아래 archive를 자동 회수한다:

- `REI_AGE64_BLOCKMAX_NCP_20261019T084150Z.zip`,3894245bytes, SHA256 `d1a1166de0426c660d6edda4e66df50c87bc7a93267d3b78ea07d0e85e3a2178`.
- Drive `1xHJ0mUeQL-REI3v5NvP07NToqqKDNFFn`, Drive folder `rei_bianchi_research_backups`.
- Dropbox `id:BSpOijBcT10AAAAAAD_QgQ`, parent `/bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`.
- v8실행 준비 ZIP: Drive `11C9PLnezdbwa2bF85lk6d8rG3msW0uJB`, Dropbox `id:BSpOijBcT10AAAAAAD_SVA`,23247707bytes, SHA256 `ffb281631fdc14c683ac1e51f43112c2a4e2766cbf7519564e5e2369d073ea03`.

connector 또는 기존 rclone `gdrv:`/`dbx:`를 사용하고 실제 SHA/CRC/payload를 확인한 뒤 새 task에 해제한다. compactB1 reference_base.py가 원 준비 source 복원과 binary binding을 처리한다. 기존 run은 읽기 전용이다.

정확한 단일 mode는 `age32-block-max-diagnostics`: q0 age32/source8/n_mu8/transport16/time1, block-max/binary64, diagnostics ON, original RK/rtol/atol/source schedule, photon/energy1e−8, case/total cap1800s다. task code의 `scripts/`와 `src/`를 사용하고 다음 인자들을 CURRENT 인계에 맞게 실제 절대경로로 정한다.

```bash
export REI_PREPARED_BASE="$BASE_RUN/native"
export REI_TRANSPORT_THREADS=48
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age32-block-max-diagnostics
```

성공한 attempt만 source_jump_diagnosis.py, photon_ledger_diagnosis.py, compare_age_references.py로 원 age64 attempt001과 비교한다. source-jump32/32 coverage, nonbirth/gas/ledger bits, accepted/discarded/rejected telemetry, 저장 잔차를 보고한다. 기존 age64 source jumps는 계속MISSING_DATA다. age64/spectral128/time8/16/32를 다시 실행하지 않는다. PR171에서600s cap으로 중단된 별도age64와 이 완료 block-max age64를 혼동하지 않는다.

## C. 다른 현재 lane의 대기·재사용 계약

| Owner | 현재 조치 | 실행하지 않을 중복 |
|---|---|---|
| PR151 R9 Unit5/T4 | recovery 결과와128checkpoint 재사용; residual 알고리즘 비용/representation 방법검토 | 원 allocation의 expired deadline 재설정, 이미 회수한 terminal 재회수, 미정의 새 residual 실행 |
| RUN13–18 | 완료 M2, fixed-gas sensitivity, C0 polynomial/residual 자료를 다음 continuous tube 구성에 입력 | M2standard/tight 재적분, 소실 raw를 존재하는 것처럼 보고, finite pair를continuum certificate로변환 |
| PR211 RUN19 | guarded cubic/direct fallback, source-bound cache, prepared-T workspace 재사용; root가 게시한 새 조건부 defect 계약이 있으면 읽기 | 이전264states/9216states/benchmark/SIMD를 단순재개 이유로 전부반복, Li/Be를productionnetwork에 무조건활성화 |
| PR208 BR06 | frozen operator quadrature/reference를 BR07native moment-energy admission에 설계입력으로 사용 | frozen gas와 evolving gas를 동일정확도승인, 준비되지 않은 longspancampaign |
| PR210 BRPERF01 | PERF00 source/runtime checkpoint 확인; RUN19를 재사용하는 adapter계약·작은code개발은 이론/구현/독립검토순서로 | PR제목만 보고 rate-table/pool/catalog가완료되었다고가정 |
| BASS shared-Q | sourceID·단위·시간축·proper density를 cross-repo 계약에 맞춤 | donorpressure/reservoir없이 Einstein reactionfeedback활성화 |

RUN19 complete archive: Drive `1pRPhitdAFfEU8HrSC02uXXVXwRI1U8wk`, Dropbox `id:BSpOijBcT10AAAAAAD_SVw`,25344988bytes, SHA256 `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62`; file `REI_RUN19_FINAL_T_RATE_ACCELERATION_LI_BE_20261020.zip` under `/BASS_DERIVATION_DOSSIERS_20260912/`. Current final handoff Drive `14jn8FzryiPiFRTK4mAmgwsrl5Rtk4CpF`도 읽을 수 있다.

BR06 complete archive: Drive `1WYxYUVBTK039uFca1jtQ7VmUQ1ZZlrZy`, Dropbox `id:BSpOijBcT10AAAAAAD_SHA`,70567867bytes, SHA256 `3137ad8903ef62073485a18e78b84966d3a9d09b9a60698dddfd492876432135`, `/bianchi/rei_bianchi/research/REI_BASS_HIERARCHY_BACKUPS/REI_BASS_REACTIVE06_VIGILODE_REFERENCE_RECOVERY_20261020_3137ad89_FULL.zip`.

Unit5 terminal recovery: Drive `1ue0Aj9BzNOCNXfF6uPu4ynGDXBzumFvi`, Dropbox `id:BSpOijBcT10AAAAAAD_IgA`,248799bytes, SHA256 `19dfbaf5ffcc6fc19e11fe0afdd0635da19e9881a3a7d1d9b7084b70b3872ffe`; Git path `research/microphysics_r9_20261015/unit5_t4_resume_20261016/actual_ncp_20261016/RECOVERY_RESULT_KO.md`. 새 실행은이인계범위에없다.

## D. 결과를 닫는 방법

각 lane 실제 source SHA, 실행환경, binary hash, input/config identity, command, stdout/stderr, exit, wall/RSS/RHS 또는 해당 H-action counts, 결과 raw와 독립 분석을 task-owned 파일로 보존한다. 측정하지 못한 값은UNKNOWN이다. 소규모 호환 수정을 했다면 source delta와 해당 회귀 근거를 남긴다.

결과는 원 owner branch의 현재 HEAD를 다시 읽은 뒤 expected-head fast-forward로 추가 게시한다. 다른 thread가 앞서 push했으면 그 delta를 읽고 보존하며 통합한다. 강제 push/merge는 하지 않는다. 큰 raw는 원 Drive/Dropbox 연구 폴더의 새 archive 이름에 저장하고 양쪽 actual download SHA/CRC/payload 검증 수준을 별도로 기록한다. Git에는 manifest·결과요약·exactsource·실행/검토/DAG·provider IDs를 게시한다. raw에 공개범위 제한이 있으면 그 제한을 그대로 지킨다.

시작/컴파일·검증/실제실행/독립검토/게시·백업각단계에 DAG를갱신한다. 중단되면 마지막실제결과까지 게시·백업하고 정확한미완료상태를남긴다. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`, fullEoR/FLRW-CONV/BI-SIGNED/continuum/physicalcontinuum/Hamiltonianclosure의남은HOLD를유지한다.
