# Codex 재개 지점

- Branch: `research/rei-source-age-positive-native-intake-20261016`; stacked Draft PR #171, base PR #170.
- Original executed native: `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. Native production 파일은 수정하지 않았다. 이번 source와 blob은 `FINAL_SOURCE_IDENTITY.json`을 읽는다.
- 판정: `PASS_BOUNDED_POSITIVE_NATIVE_REFERENCE_IMPLEMENTATION`, `HOLD_SOURCE_AGE_SPECTRAL_AND_NATIVE_TIME_ACCURACY`, `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
- 가장 먼저 `C9_SCIENTIFIC_REPORT_KO.md`, `contracts/NEXT_DAG_v1.json`, `evidence/matrix/MATRIX_COMPARISON.json`, `evidence/matrix/MATRIX_EXECUTION.json`, `R6_BACKUP_RECEIPT.json`, 최종 `FINAL_BACKUP_RECEIPT.json`을 읽는다.
- Owner checkout과 PR150/R9 결과를 reset/clean/kill하지 않는다. 동일 isolated worktree가 사용 가능하면 먼저 status를 읽는다. 기존 matrix를 이유 없이 재실행하지 않는다.

현재 숫자를 읽는 정확한 명령:

```bash
cd /home/cosmosapjw/rei_worktrees/rei_source_age_positive_native_intake_20261016
git status --short
git rev-parse HEAD
python3 research/rei_source_age_positive_native_intake_20261016/compare_matrix.py research/rei_source_age_positive_native_intake_20261016/evidence/matrix
python3 -m json.tool research/rei_source_age_positive_native_intake_20261016/contracts/NEXT_DAG_v1.json
```

별도 빈 디렉터리에서 게시된 ZIP의 source·native build·좌표 및 q0/age16 과학 결과를 복원하는 명령은 다음과 같다. 이 명령은 후속 연구를 시작하기 전에 필요할 때만 사용한다.

```bash
mkdir -p /tmp/rei-positive-native-c9-restore
rclone copyto gdrv:rei_bianchi_research_backups/REI_POSITIVE_NATIVE_C9_20261016_v1.zip /tmp/rei-positive-native-c9-restore/archive.zip
cd /tmp/rei-positive-native-c9-restore
unzip -q archive.zip
bash research/rei_source_age_positive_native_intake_20261016/RESTORE_VERIFY.sh
```

Dropbox에서는 같은 archive 이름을 `dbx:bianchi/rei_bianchi/research/REI_POSITIVE_AGE_REFERENCE_BACKUPS/`에서 독립적으로 받는다. SHA·payload 수·각 제공자의 fresh replay exit는 최종 receipt가 authoritative하다.

다음 READY는 두 개의 독립 제한 실행이다. (1) age32→64와 고정 age의 native proper-time mesh를 분리해 마지막 출생 이후 stiff survivor 층을 검증한다. (2) q+0.1에서 transport spectral cell64 이후 HeI 누적 photo-event를 집중 refinement한다. 이번 완료된 native common mesh·MD14·Grackle source identity, ledger acceptance, 원시 실패 및 cumulative 판정은 그대로 상속한다. 또 다른 전체 FLRW production 실행은 이번 handoff의 명령이 아니다.
