# BASS_HE prepared revision: cloud Codex 점검·최소 수정·실행 handoff

## 역할과 목적

이전 대화 없이 실행한다. 코드 설계·수정·scoped tests는 ChatGPT 연구 스레드가 이미 수행했다. Codex는 전달된 수정본의 identity, 변경분, 호스트 조건을 점검하고 필요한 최소 수정과 승인된 실행만 맡는다. 전체 연구를 다시 설계하거나 동일 문헌조사·테스트·대형 replay를 자동 반복하지 않는다.

Repository: cosmosapjw-quantum/BASS_HE
Publication PR: #17
Branch: research/shared-c64-crossrepo-20260928
필독: root AGENTS.md, 이 폴더의 CHAT_FIRST_EXECUTION_POLICY_KO.md와 DELIVERY_CONTRACT.json.

사용자가 전달한 최종 commit/tree를 먼저 고정한다. 미지정이면 GitHub의 PR #17 HEAD/tree를 한 번 읽어 작업 기준으로 기록한다. 현재 로컬 main을 기준으로 계산하지 않는다. fetch 뒤 새 고유 detached worktree를 만들고 HEAD/tree/clean 상태를 확인한다. 기존 경로가 있으면 검증하거나 다른 경로를 사용하며 reset/clean/stash/rm -rf를 하지 않는다. 이후 evidence-only branch 이동은 실행 basis 변경이 아니다.

## 이미 완료되어 다시 돌리지 않을 작업

- HE PR #16의 `2c3812e390b91b89da1de30988b3933646b79f30`에 resume-004 원래 방법의 cloud evidence가 있다. 실행 basis는 `6ddc4ff821ab5d1397fbd08493dd3954a89750f1`, tree `e80a9218d9d275546132110605da35160a878bb0`. 해당 기록은 actions56/panel-pairs28/imported0/full216/cloud75를 보고한다. 같은 closure의 replay나 15-arm sweep을 반복하지 않는다.
- bass_cr `820b3e0a6da9f7a8c8ece8fcbd3afcf3fa9a6dc3`의 F1_R2/20260928T101921Z/RETURN_REPORT.json은 F1_ENGINE_ADMISSION_PASS를 보고한다. exactly-once 권한은 이미 소비됐으며 F1 retry/F2/F3/capture 실행 권한은 없다.
- HH PR #12 M3B는 자기 owner가 조정하는 별도 작업이다. 이 handoff로 다른 repo 수정·native 작업을 시작하거나 benchmark를 재승인하지 않는다.

## 기본 실행: 입력 사전점검만

이 폴더에서 다음 CLI가 실제 제공된다.

    python -S evaluate_r2.py --r1-root <검증된-R1-root> --verify-only --out <새-output-dir>/INPUT_IDENTITY.json

`<검증된-R1-root>` 아래에는 `results/*.json` 7개가 있어야 한다. 같은 폴더의 TRACE_INPUTS.json이 file-set/size/SHA256 authority다. 부모 archive authority는:

    BASS_HE_SHARED_C64_RESEARCH_20260928_v1.zip
    bytes 668774
    SHA256 b70fbd51736d6e3004c27793cb1c47e50878fc72bad090de83e2a57aa94522a2
    Drive object 1BYwBr102UtC8vHuvuS6BHOlkS74wlkCS
    Dropbox object id:BSpOijBcT10AAAAAADukRg

원본은 R2 archive 내부 inputs/에도 그대로 있다. 기존 host에 검증된 입력이 있으면 재다운로드하지 않는다. 없고 provider 접근도 없으면 BLOCKED_INPUT_ACCESS로 기록하고 새로운 spectral calculation으로 대체하지 않는다. archive를 해제할 때 absolute/../symlink 경로를 거부하고 새 고유 디렉터리를 쓴다.

출력 부모 디렉터리만 미리 만든다. 기존 INPUT_IDENTITY.json을 덮어쓰지 않는다. 성공은 byte identity 확인이며 과학 validation이나 pytest PASS가 아니다. 명령은 NumPy/SymPy import조차 하지 않고 spectral solve/cloud job/pytest를 실행하지 않는다.

## 조건부 작은 host 검사

전달본과 다른 Python/NumPy/SymPy 환경, 실제 import 문제, 로컬 최소 수정이 있을 때만 다음 scoped command를 한 번 실행한다. 미변경 환경의 기존 유효 receipt가 있으면 재사용 근거를 기록한다.

    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -m pytest -q -p no:cacheprovider test_error_envelopes.py test_prepared_delivery.py --junitxml=<새-output-dir>/SCOPED_TESTS.xml

기대 개수를 정답으로 맞추지 말고 실제 collected/passed/failed를 기록한다. 여기서 이미 확인한 결과는 12개 기존 research test와 16개 새 delivery regression을 합친 28 PASS다. 이는 전체 BASS_HE 216-test suite를 다시 실행했다는 뜻이 아니다.

같은 저장 trace의 수치 재분석이 명시적으로 필요할 때만, 기존 tolerance를 그대로 사용해 한 번 실행한다.

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python evaluate_r2.py --r1-root <검증된-R1-root> --out <새-output-dir>/RESULT_SUMMARY_NEW.json

이것도 새 spectral solver나 56-action cloud replay가 아니라 14개 저장 trace/7970 interior comparison/2000 synthetic chains의 분석이다. 테스트 count는 NOT_RUN_BY_THIS_COMMAND/null이며 pytest 증거와 구분한다. 변경 없는 데이터·코드에 대해 이 분석을 반복할 필요는 없다.

## 코드 수정 경계

scope가 작고 host-specific인 재현 가능한 실패만 최소 수정한다. 원인을 설명하고 변경 file/blob, command, exit code, 집중 GREEN을 보존한다. 새 설계·물리 가정·허용오차·certificate policy·다중 원인의 수선이 필요하면 현재 완료 증거와 함께 연구 스레드로 반환한다. 장시간 자율 연구/무한 fix-review loop를 시작하지 않는다.

Common-contour same-sheet homotopy와 CODE-I02 focused independent rereview는 여전히 별도 과학 gate다. 이 전달본의 작성/실행자는 자신을 독립 reviewer로 부르지 않는다. 현재 체크와 receipt 작성은 그 검수를 대신하지 않는다.

## 게시·백업 및 반환

자기 output/state만 다루고 다른 두 세션을 kill/migrate/restart하지 않는다. cgroup/systemd/mount/VM/ACG/credential 변경과 새 유료 자원 생성은 금지한다. /dev/vda는 root storage이므로 포맷하지 않는다.

실제 command/cwd/UTC/exit code, execution commit/tree, input_manifest SHA, code blob identity, 환경, 실행/재사용/미수행 항목을 RUN_RETURN.json과 append-only 로그에 남긴다. `prepared_delivery_only=true`, `production_execution=false`를 명시한다.

publication은 moving PR #17 branch의 새 `research/shared_c64/20260928/R2_followup/<UTC-id>/`에 평문 JSON/TXT/XML로 non-force push한다. GitHub 공유본과 execution code identity는 별도로 기록한다. 대형 ZIP만 남기지 않는다. conflict가 있으면 읽고 append-only reconcile하며 force push/merge하지 않는다.

새 산출물이 생기면 기존 Drive folder 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI 및 Dropbox /BASS_DERIVATION_DOSSIERS_20260912/에 create-only 백업한다. 이미 성공한 객체는 중복 업로드하지 않는다. 실제 ACK/object-id/size/checksum을 기록하고 remote restore와 구분한다.

마지막에는 PR/head/tree, 실제 실행 명령/결과, 최소 수정 유무, 미수행, backup 상태, 다음 최소 action만 반환한다. 원래 연구 전체를 다시 설명하지 않는다.

scientific_PROMOTE=HOLD; Eq55=NOT_RUN; full_Nmax4=NOT_ESTABLISHED; continuum=NOT_ADMITTED. 자동 production 실행이나 merge는 하지 않는다.
