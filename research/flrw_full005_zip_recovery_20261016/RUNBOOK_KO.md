# full005 기존 출력의 ZIP 복구

이번 실제 실패는 v1 wrapper의 `REQUEST_FAILED: ZIP does not support timestamps before 1980`이다. solver 실행은 0회였지만 render의 실제 최종 상태는 아직 확인되지 않았다. 예전 wrapper는 `FINAL_STATUS.json`과 renderer 결과를 먼저 만들고 ZIP 단계에서 실패할 수 있다. 따라서 ZIP 오류를 render 실패로 바꾸거나 무조건 render를 다시 실행하지 않는다.

NCP Codex가 최종 프롬프트의 pinned `CODE_COMMIT`에서 sibling `PACKAGE_RECEIPT.json`과 v2 ZIP을 직접 가져오고 SHA256을 한 번 비교한 뒤, 새 비어 있는 디렉터리에 압축을 푼다. 사용자의 기존 checkout·dirty 파일을 보존하며 clone/worktree를 만들지 않는다. 새 코드 루트는 압축을 푼 디렉터리의 `rei_bianchi`다. 사용자에게 다운로드나 사전 설정을 요구하지 않는다.

기존 작업 디렉터리는 `/root/rei-post-XXXXXX` 형식이며 suffix는 알려져 있지 않다. `/root/rei-post-*/results`와 이미 명시된 wrapper 출력 경로를 유한한 일회성 읽기 전용 검색으로 찾고 `FINAL_STATUS.json`, `figures_and_diagnostics/POSTPROCESS_RECEIPT.json`, `bind.log`, `render.log`, `full_pair_manifest.json`을 우선 확인한다. 관측한 실제 status와 Q512/Q1024 campaign 경로를 근거로 OLD를 고른다. 파일이 없으면 없다는 사실을 기록하고 성공·실패를 추측하지 않는다. 기존 부분 ZIP을 포함해 OLD의 모든 파일과 mtime을 보존한다.

Codex가 새 코드 루트에서 다음 동작을 직접 실행한다. 아래 `OLD`와 `NEW`는 사용자가 채우는 설정이 아니라 Codex가 실제 evidence를 확인해 정하는 경로다.

```bash
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py repackage \
  --existing-output OLD --output NEW
```

NEW는 기존에 없는 경로이며 OLD와 기존 campaign 바깥에 둔다. 필요한 경우 `--campaign`과 `--renderer-root`는 관측한 기존 campaign과 새 배포본 renderer의 절대경로로 지정한다. canonical campaign은 `/root/REI_FLRW_COVARIANT_20261015_005/full_campaign001`이다. repackage는 기존 evidence를 복사하고 새 package를 만드는 경로다. 원래 과학 상태가 실패이면 그 실패가 그대로 남아야 하고, 원래 성공이면 독립 과학 검토 대기라는 의미를 그대로 유지한다. bind·render·solver를 호출하지 않는다.

packaging-only는 science 마감과 분리되어 있으므로 원래 마감이 지났어도 실행할 수 있다. science 실행이 정말 필요한 경우에는 원래 총 300초, AS 8 GiB, 절대마감 `1792122617.77407` (`2026-10-16T03:50:17.774070Z`)을 유지한다. 소비한 시간을 초기화하지 않는다. 이번 기존 결과 복구에서는 render를 재실행하지 않는다. 실제 render 실패 원인은 로그·receipt로 확인해 보고한다. 별도로 정당화된 후속 render도 남은 예산을 입증할 수 없거나 마감이 지났으면 중단한다. 새 render 예산을 만들어내지 않는다.

repackage exit code 0은 packaging 성공만 뜻하며 과학 성공을 뜻하지 않는다. `scientific_status`와 `packaging_status`를 별도로 보고한다. 기존 status가 없거나 해석 불가능하면 UNKNOWN/HOLD를 유지하고 성공으로 보정하지 않는다.

새 결과의 `RECOVERY_RECEIPT.json`과 `POSTPROCESS_REPORT_WITH_RUNNABLE_CODE_EXTERNAL_INPUTS.zip`을 확인한다. 마지막 보고에는 기존 과학 status, renderer receipt/로그 관측값, OLD/NEW 경로, 새 ZIP·package receipt 경로 및 CRC 결과를 넣는다. solver 실행은 0회다. 완료된 28 checks·profile·source006 test/build/run은 재사용한다. native source/config/checkpoint/campaign epoch는 수정하지 않는다. 실제 그림의 과학 admission은 독립 검토 전까지 대기이며 D activation·D 곡선·전구간 수렴·Bianchi 최종결과를 주장하지 않는다. 대용량 scientific raw는 외부에 보존된다.

복구 후 이미 승인된 Git/cloud 접근과 기존 백업 경로를 사용한다. 공개 저장소에는 공개 가능한 report/code만 게시하고 private raw는 포함하지 않는다. private scientific raw는 접근 가능한 기존 private backup 목적지에 보존한다. 실제 업로드 acknowledgment/readback으로 확인한 범위만 기록한다. 접근이 없으면 미완료 항목을 정확히 보고하며 사용자에게 수동 다운로드를 요구하지 않는다.

배포 코드의 새 synthetic packaging 집중 테스트는 8개 PASS(0.119초)다. 기존 28 physics·3 renderer CLI·8 wrapper 검증은 반복하지 않고 재사용했다. 이것은 실제 NCP 복구·render·과학 admission의 증거가 아니다. 구현 상세는 `IMPLEMENTATION.json`, 최종 독립 코드 검토 판단은 `INDEPENDENT_REVIEW.json`을 따른다.

새 독립 코드 검토는 `INDEPENDENT_REVIEW.json`의 `PASS_IN_SCOPE`로 완료됐다. 이는 packaging 복구 구현·지침에 대한 판단이며 실제 NCP 결과의 과학 승인이 아니다. 추가 선택적 검토나 기존 검증 재실행 없이 이 인계의 기존 결과 복구로 진행한다.
