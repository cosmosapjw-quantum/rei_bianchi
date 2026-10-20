# 다음 대화에 붙여넣을 실행 요청

$physmath-research-loop를 사용한다. 첫 행동은 다른 대화·PR198·research/rei-lrs 관련 branch·Google Drive REI_RESEARCH_BACKUPS/rei_bianchi/·Dropbox /bianchi/research_backups/rei_bianchi/의 새 실행 receipt 확인이다. 실제 source SHA, command, stdout/stderr, exit code, raw를 읽고 새 결과가 있으면 우선 분석한다. 검색 오류·404·목록 조회 범위를 전체 검색 성공으로 표현하지 않는다.

Repository: cosmosapjw-quantum/rei_bianchi; PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198; branch: research/rei-lrs-v14-physical-birth-20261018. 이 연구는 production v3/rux 및 BASS/rec/RUN19와 별개의 독립 LRS다.

기존 `cosmosapjw-quantum/rei_bianchi` checkout과 dirty 파일을 보존하며 독립 이력 병렬 backlog의 NCP 실행만 이어서 완료해 주세요. 새 clone/worktree/reset/clean이나 물리식·native 원문·provider/EoS/FD/tolerance/default 변경은 하지 마세요.

현재 scientific source는 `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`, VigilODE pin은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`입니다. 기준 metadata HEAD는 `96aaad584bbecded34485526a4bb53a49708ffc6`이며 새 구현의 실제 게시 commit/백업 IDs는 아래 최종 receipt로 닫혔습니다. 최종 metadata HEAD는 이 파일을 포함하는 commit입니다. metadata HEAD와 scientific source를 혼동하지 마세요.

- 새 구현 commit: `d234243a79e4e8e611aaf4ac61949c5ef9111468`
- 새 구현 archive/provider/ACK: `ARCHIVE_AND_ACK_DUAL_FULL_GET_PASS — FINAL_PUBLICATION_ACK.json`
- 독립 C9 기본 판정: `PASS_SCOPED_RESOURCE_AWARE_ORCHESTRATION`; build64 상한교정도 같은 episode의 ROOT_REPAIR_ADDENDUM에서 독립 PASS/residual blocking0.
- current source524의19설정, borrowed N2, original V14 84는 이미 NCP완료이며 기본 재실행 제외.
- 이번 미실행 집합: V12 144 histories, V13 84 histories(cells32/tol1e-15), SSPRK 원본3commands(transport52행/coupled16이력). 새 모델0.
- 현재 도구 경계: remote quota0/SSH key 부재로 실제 전체 backlog NCP는 NOT_RUN. 기존 허가된 NCP 연결이 사용 가능할 때 실행하고, 접근 실패 자체는 실제 오류로 반환.

기존 checkout root에서 실행할 명령은 다음과 같습니다.

```bash
env -u CARGO_TARGET_DIR python3 \
  research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/campaign_cli.py all \
  --input-root research/lrs_atomic_native_bridge_20261016 \
  --work-root /tmp/rei_lrs_parallel_20261020 \
  --cargo cargo --build-jobs 64 --max-workers 64 \
  --nominal-job-memory-mb 512
```

246 DAG jobs=prepare3+build3+targeted-test3+native231+merge3+analysis3입니다. 명령은 정상 V12 base→V13 RESTORE_NATIVE와 SSPRK→V14→V13 restore chain, variant별 private target을 사용합니다. offline Cargo cache가 필요하며 자동 install/source download는 하지 않습니다. `--build-jobs 64`는64 CPU slot·64GiB nominal build/test memory를 요구합니다. native는1slot/512MiB nominal/thread1입니다. 실제 affinity/cgroup quota/available memory에20% reserve를 적용하므로 사양이64CPU/128GB여도 부족하면 `NOT_RUN_RESOURCE_ADMISSION`으로 남기며 concurrency를 몰래 바꾸지 마세요. 준비만 보려면 `all`을 `plan`으로 바꾸세요. 동일 명령의 재개는 검증된 완료 identity만 재사용하고 실패/부분 raw를 보존합니다.

실제 source/binary/toolchain/host/resource identity, argv·stdout·stderr·exit·raw·outcome, MANIFEST/RESOURCE_PLAN/CAMPAIGN_RECEIPT, exact matrix merge/분석과 실제 provider archive/dual-full-GET/ACK receipt를 반환해 주세요. 기존 C5–C8 검증 전체나 완료된19/borrowed/original84를 의무적으로 반복하지 마세요. 로컬23 native/21tests+build64표적1건 근거는 기존 execution/review receipt를 재사용하세요.

exit0·coverage 통과와 전체 backlog의 과학적 수용은 구분하세요. V12는 stdlib summary와 saved `evidence/analysis/NATIVE_ANALYSIS.json` 등 과거 reference/분석 identity를 연결하며3 SciPy/numpy reference IVP를 새로 적분하지 않습니다. V13 기존 stdlib analyzer, SSPRK 원래 Decimal audit는 exact coverage 뒤 실행하고 과거 reviewer 문자열은 새 독립 검토로 세지 마세요. 결과 차이/실패/부재는 실제 상태로 보고하고 새 tolerance를 발명하지 마세요.

일반2차 source-on/uniform stiff/일반 양수성/Case B/full EoR/signed Bianchi/넓은 positive-CMB·비영 boundary/global certificate/완전 photon ledger의 기존 HOLD와 production NOT_ISSUED를 유지하세요. NCP64 가속은 아직 측정하지 않았습니다. 다음 유한 작업은 이 backlog의 실제 host 재현과 원시 결과에 대한 root 판정입니다.

사용자가 승인한 연결은 ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22 이다. 실제 인증 수단이 있을 때 agent가 실행한다. 사용자의 수동 SSH/SCP나 파일 다운로드를 요구하지 않는다. 단계별 Git게시·Drive/Dropbox 백업과 DAG, 실제 구현하지 않은 Astra의 독립 검토를 유지한다.

처음 읽을 현재 단위는 research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/이며 RESEARCH_REPORT_KO.md, SOURCE_DELTA.json, ROOT_ADMISSION.json, FINAL_DELIVERY.json, FINAL_PUBLICATION_ACK.json, DAG_FINAL.json, CURRENT_SOURCE_CI.json, CODEX_NCP_EXECUTE_KO.md를 읽는다.

## 최종 게시·백업 identity

- 구현·결과 source commit: `d234243a79e4e8e611aaf4ac61949c5ef9111468`. 최종 metadata HEAD는 이 파일을 포함하는 commit이다.
- Archive: `REI_LRS_PARALLEL_C10_20261020.tar.xz`, 7,654,920bytes, SHA256 `388ef80e25fef7905e44fcc1aaf6179c6332b41fdf7c7e07233f51b805e608ac`. Drive `1yK1fsc_-ybJ59l8VYDvIARrpZtTIWbc5`, Dropbox `id:BSpOijBcT10AAAAAAD_aKw`.
- ACK: `REI_LRS_PARALLEL_C10_ACK_20261020.json`, 6,391bytes, SHA256 `05c4bd684818cbc65b89a3f4091cdfb0c87a6902117ea954d0ded60f1774539e`. Drive `19mpts1yDKBtp02K6qOpG9C_dolyfDt4H`, Dropbox `id:BSpOijBcT10AAAAAAD_aLQ`.
- Archive와 ACK 각각 양쪽 전체 GET/bytes/SHA256 일치. Archive343 regular files/manifest342개+self1개 PASS. Drive origin HTTP NOT_EXPOSED/materialization200, Dropbox HTTP200, 실제 회수 process exit0.
- archive는 기존 검증된 dependency/base 위에 repo_payload를 overlay하는 delta이며 단독 복원본이 아니다. 포장 시점 PENDING은 별도 ACK와 FINAL_PUBLICATION_ACK.json이 닫는다.
- 실제 source524의 NCP19/borrowedN2/originalV14 84 완료를 유지한다. 이번 V12/V13/SSPRK backlog는 NOT_RUN_BLOCKED_EXECUTION_ACCESS다.
