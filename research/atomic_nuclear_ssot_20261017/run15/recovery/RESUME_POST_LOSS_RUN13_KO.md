# 환경 소실 이후 RUN13 Git 원본 복원 기록

## 현재 확인된 결과

`/tmp/rei_run15_recovered_repo`의 실제 HEAD `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`에서 원래 `run13/git_transport/restore.py`를 실행했다. 원본 RUN09/RUN11 ZIP 두 개의 분할 바이트를 add-only 방식으로 결합했고, 각 chunk 및 전체 파일의 SHA-256/Git blob SHA-1을 확인했다. 원래 `SHA256SUMS.txt`의 332개 항목과 이를 포함한 정확히 333개 payload 파일을 검산했다. `UNCHANGED_INPUT_CODE.json`의 113개 항목(91 code, 19 inputs, 3 core Python)도 모두 일치한다.

이 작업의 지위는 **IMPLEMENTATION_VERIFIED — Git 원본 payload와 manifest byte identity 범위**다. Drive에서 새로 다운로드한 전체 RUN13 archive와의 독립 비교는 이 단위에서 수행하지 않았다. 물리·수치 해의 수렴을 새로 검증한 결과도 아니다. Native 실행, ODE/IVP, 기존 test suite 재실행은 각각 0회다.

## 실제 명령과 기록

복원 도구 실행 명령은 성공 receipt의 `07_restore_original_transport.command.json`에 실제 Python 경로, cwd, 시간, exit code 및 로그 SHA와 함께 보존되어 있다. 다음 두 명령을 실행했으며 첫 실패를 삭제하지 않았다.

```bash
python -B /tmp/rei_run15_salvage/recovery/verify_post_loss_run13_git.py
python -B /tmp/rei_run15_salvage/recovery/verify_post_loss_run13_git_v02.py
```

첫 명령은 whole-repository `git status`가 sparse/promisor checkout의 없는 Git object `da5f434ad8a17b34e4508c67e724405363fcead2`를 가져오려다 `browser-proxy:8889` 연결 실패로 종료되었다. 이 시점에는 복원 도구를 아직 실행하지 않았다. 실패 기록은 `POST_LOSS_RUN13_GIT_ONLY_RESTORATION.json`, `02_git_status_initial.stderr.txt`에 남아 있다.

두 번째 새 검증 스크립트는 전체 저장소 status 대신 실제로 확보된 RUN13 tree 범위를 검사했다. 그 범위의 Git tracked 파일 342개를 실행 전후 실제 Git blob 및 파일 mode와 대조했고, Git index의 실제 바이트도 실행 전후 동일함을 확인했다. 원래 tracked 파일을 수정하거나 index를 갱신하지 않았다. 여기의 tracked 342개는 유실된 새 RUN15 case의 342개 파일과 별개다.

## 성공 evidence

- `attempt02/POST_LOSS_RUN13_GIT_ONLY_RESTORATION.json`: 실제 성공 receipt. SHA-256 `09f3312acac79a5194fe83f3bb9d080958d1a911f32c6524423e2972b746cf5e`.
- `attempt02/RUN13_GIT_PAYLOAD_332_HASHES.json`: 원본 manifest 항목별 새 검산.
- `attempt02/RUN13_SOURCE_INPUT_113_HASHES.json`: source/input 항목별 새 검산.
- `attempt02/02_scoped_tree_before.verified_files.json`, `attempt02/08_scoped_tree_after.verified_files.json`: 원래 RUN13 tracked 파일 범위의 실행 전후 비교.
- `attempt02/ORIGINAL_CONTRACT_COPY_RECEIPT.json`과 `original_contracts/`: 원래 복원기·transport manifest·checksum manifest·source map을 실제 Git 바이트 그대로 복사한 evidence.

복원된 `provenance/RUN09.zip`은 14,407,737 bytes, SHA-256 `039fbce620bfa90e43822727d01cb8a2734fbfa78ef894673c7de9a06aa16029`이다. `provenance/RUN11.zip`은 17,968,344 bytes, SHA-256 `cd9258a2b7ca6fee8f82155d4fa2bc016ac5d05a25b061f8fcf74db3c3e2d0a8`이다. 두 파일은 현재 Git checkout의 원래 recovered/provenance 위치에 있다.

## 새 RUN15 case evidence의 한계

네 RUN15 case archive에 들어 있던 342개 원본 case-file 바이트는 이 agent가 현재 접근한 surface에서는 **LOST_IN_CURRENT_SURFACE**다. 기존 수치나 hash 목록을 원본 state/ZIP으로 대체하지 않았다. 새 archive utility 및 CASE_ARCHIVE_INDEX의 원문도 이 agent에게 남아 있지 않았다. 해당 기대 hash와 이전 검증 사실의 대화 재기록은 `../archive/TRANSCRIPT_ARCHIVE_RECOVERY_20261019.json`에 **TRANSCRIPT_RECONSTRUCTION_ONLY**로 분리했다.

실제 대화 tool output에 온전히 남아 있던 `verify_clean_git_restore.py`와 `restore_inputs.py`는 `../runtime/exact_candidates/`로 복구했고, 각각 원래 SHA에 일치하여 **EXACT_BYTES_RECOVERED**로 admission 했다. 두 파일을 실행하지 않았다. 새 RUN15 case를 원본 source로 추측 재구성하거나 이전 IVP를 다시 실행하지 않았다.
