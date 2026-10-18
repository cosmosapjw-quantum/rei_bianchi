NCP에 연결된 Codex에서 아래 작업을 직접 완료하라. 사용자는 이 프롬프트만 붙여넣으며 다운로드·설정·명령 실행을 사용자에게 요구하지 말라.
CODE_COMMIT=571459763fd3b6ae31ef4b0ce9c4a3144add1cd4
ZIP_URL=https://raw.githubusercontent.com/cosmosapjw-quantum/rei_bianchi/571459763fd3b6ae31ef4b0ce9c4a3144add1cd4/research/flrw_full005_zip_recovery_20261016/REI_FULL005_ZIP_RECOVERY_20261016_v2.zip
ZIP_SHA256=e63b12b5f16bc19259906cc9a3acd55d04f879c7cd2a9083ff92dfb757145520
위 immutable URL에서 ZIP을 직접 내려받고 SHA256을 한 번 비교한 뒤, 새 비어 있는 code 디렉터리에 풀어라. 기존 checkout·dirty/untracked 파일을 보존하고 clone/worktree를 만들지 말라.
압축을 푼 rei_bianchi의 AGENTS.md와 research/flrw_full005_zip_recovery_20261016/{CONTRACT.json,HANDOFF.json,NEXT_DAG.json,RUNBOOK_KO.md,IMPLEMENTATION.json,INDEPENDENT_REVIEW.json}을 읽고 따르라.
새 packaging 집중 테스트 8개 PASS(0.119초), 독립 코드 검토 PASS_IN_SCOPE를 재사용하라. 예전 28 physics·3 renderer CLI·8 wrapper 검증과 profile/source006 시험·빌드·run은 반복하지 말라.
사용자의 v1 실행은 REQUEST_FAILED: ZIP does not support timestamps before 1980, solver_runs=0이었다. 기존 wrapper는 ZIP 전에 FINAL_STATUS.json을 쓰므로 이것만으로 render 실패라고 판단하지 말라.
/root/rei-post-*/results와 이미 확인된 wrapper 출력 경로를 유한한 일회성 읽기 전용 검색으로 찾아라. suffix나 성공 여부를 추측하지 말라.
후보별 FINAL_STATUS.json, figures_and_diagnostics/POSTPROCESS_RECEIPT.json, bind.log, render.log, full_pair_manifest.json과 파일 목록을 먼저 읽고 이번 full005 Q512/Q1024 결과를 식별하라.
후보가 모호하거나 status를 해석할 수 없으면 evidence를 보존하고 정확한 UNKNOWN/HOLD 원인을 보고하라. 성공으로 보정하거나 무조건 render를 재실행하지 말라.
OLD는 확인한 기존 results, NEW는 OLD와 campaign 밖의 사용하지 않은 새 경로로 정하고, 새 코드 루트에서 다음 package-only 동작을 단 한 번 직접 실행하라.
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py repackage --existing-output OLD --output NEW
필요하면 --campaign을 실제 기존 /root/REI_FLRW_COVARIANT_20261015_005/full_campaign001로, --renderer-root를 새 배포본의 research/flrw_full005_postprocess_20261015로 지정하라.
이 복구에서는 bind/render/solver/watcher를 실행하지 말라. 기존 raw·native checkpoint·과학 status·로그·그림·파일 mtime·부분 ZIP을 그대로 보존하라.
packaging-only는 만료된 science 마감과 무관하게 허용된다. 별도 후속 science는 원래 합계300초·AS8GiB·절대마감1792122617.77407(2026-10-16T03:50:17.774070Z)을 재설정하지 않으며, 이번 복구는 새 render를 허가하지 않는다.
NEW/RECOVERY_RECEIPT.json과 NEW/POSTPROCESS_REPORT_WITH_RUNNABLE_CODE_EXTERNAL_INPUTS.zip을 확인하라. stdout scientific_status와 packaging_status를 분리해 보고하고 exit0을 과학 성공으로 읽지 말라.
기존 render 실패는 실제 receipt/log 원인을 진단해 보존·보고하라. 기존 그림이 있으면 실제 파일을 살펴 관측 내용을 보고하고 과학 admission은 독립 검토 대기로 둔다.
복구 후 기존 승인된 Git/cloud 접근과 도구를 사용해 공개 가능한 report/code만 게시하고, private raw는 접근 가능한 기존 private backup 목적지에 보존하라. 공개 저장소에 private raw를 넣지 말라.
업로드 acknowledgment/readback으로 확인한 범위만 기록하라. 접근이 없으면 미완료 항목을 보고하고 사용자에게 수동 다운로드를 요구하거나 백업 완료를 주장하지 말라.
마지막에는 OLD/NEW, 원래 scientific_status, packaging_status, 실제 그림/receipt/ZIP 경로, solver 실행0회와 남은 미완료 항목을 간결히 보고하라. D activation/곡선·whole-history time/angular convergence·Bianchi/isotope 최종결과·과학 완료를 주장하지 말라.
