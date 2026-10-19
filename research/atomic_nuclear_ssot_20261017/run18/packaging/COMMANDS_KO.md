# RUN18 delta archive 준비 및 실행 계약

이 도구는 기존 RUN17 packaging의 path/CRC/SHA/Git blob/mode 검사와
create-only 복원 구조를 RUN18에 적용한다. 원본 RUN17 파일과 고정된
runtime/theory/inventory 과학 파일은 수정하지 않았다.

## Freeze 및 commit 선행 조건

Root가 최종 canonical `run18/`에 전달할 파일을 모은 뒤
`SCIENCE_MANIFEST.json`을 작성한다. Schema는
`rei.run18.complete-science-manifest.v1`이며 다음 필드가 필요하다.

- `excludes_itself: true`
- `files`: 각 항목은 `path`, `bytes`, `sha256`, `git_blob`, `git_mode`
- `file_count_excluding_this_manifest`: 위 목록의 실제 길이
- `payload_bytes_excluding_this_manifest`: 위 목록의 bytes 합계
- `git_mode`: 일반 파일 `100644` 또는 executable `100755`

Manifest 자체는 목록에서 제외하고 일반 파일 mode로 저장한다. 실행 시
source 디렉터리에 있는 모든 파일과 manifest 목록이 정확히 일치해야 한다.
따라서 작업용 target/cache/vendor 디렉터리는 source staging에 넣지 않는다.
보존할 crate 원본과 `runtime/bin/rei_exact_dense`는 manifest의 일반 payload다.
별도의 gas executable은 추가하지 않는다.

Manifest를 포함한 실제 source commit을 만든 뒤, 그 commit을 local Git에
확보해야 한다. Create는 `--science-commit` 실제 commit object의 SHA,
`--science-tree`, 단일 `--parent-commit`을 검사한다. 이어 canonical
`research/atomic_nuclear_ssot_20261017/run18/`의 모든 실제 committed path,
Git blob, mode를 source bytes와 대조한다. 도구에는 fetch 명령이 없고
local Git 읽기에 lazy-fetch 차단 환경을 지정한다. 필요한 객체가 없으면
root가 별도로 checkout을 준비한다.

`589ffbaff7b74a6cf1dbaf797285f15a58131dbd`는 **RUN17 science baseline**이다.
RUN17 delivery commit을 뒤에 추가할 수 있으므로 immediate parent로
강제하지 않는다. 실제 RUN18 parent는 root가 `--parent-commit`에 지정한다.

## Root freeze·publication 이후 실제 실행

아래 path와 SHA 변수는 최종 값을 지정한다. 출력 directory는 먼저 존재해야
하고, ZIP 및 receipt 경로는 아직 존재하지 않아야 한다.

```sh
rei_run18_frozen_root=/absolute/frozen/run18
rei_run18_checkout=/absolute/checkout/with-actual-science-commit
rei_run18_science_commit=ACTUAL_SCIENCE_COMMIT_40_HEX
rei_run18_science_tree=ACTUAL_SCIENCE_TREE_40_HEX
rei_run18_parent_commit=ACTUAL_IMMEDIATE_PARENT_40_HEX
rei_run18_archive=/absolute/new-output/REI_RUN18_DELTA.zip

python3 -B "$rei_run18_frozen_root/packaging/create_archive.py" \
  --run18-root "$rei_run18_frozen_root" \
  --git-checkout "$rei_run18_checkout" \
  --science-commit "$rei_run18_science_commit" \
  --science-tree "$rei_run18_science_tree" \
  --parent-commit "$rei_run18_parent_commit" \
  --output "$rei_run18_archive" \
  --receipt /absolute/new-output/PACKAGING_RECEIPT.json
```

Create는 임시 파일에서 모든 entry를 압축한 다음 verifier로 전체 바이트를
다시 읽어 CRC, manifest, SHA, Git blob과 mode를 대조한다. 원본 파일의
동시 변경이 없음을 재확인한 뒤 hard-link를 사용해 최종 ZIP을 create-only로
게시한다. Archive와 전체 uncompressed payload는 각각 **100 MiB 이하**,
entry 수는 **2,000 이하**여야 한다.

위 receipt의 `archive_sha256`을 읽어 별도 검증과 새 디렉터리 복원을 수행한다.

```sh
rei_run18_archive_sha256=ACTUAL_ARCHIVE_SHA256_64_HEX

python3 -B "$rei_run18_frozen_root/packaging/verify_archive.py" \
  "$rei_run18_archive" --sha256 "$rei_run18_archive_sha256" \
  --output /absolute/new-output/ARCHIVE_VERIFICATION.json

python3 -B "$rei_run18_frozen_root/packaging/verify_archive.py" \
  "$rei_run18_archive" --sha256 "$rei_run18_archive_sha256" \
  --restore-to /absolute/new-restore-directory \
  --output /absolute/new-output/LOCAL_RESTORE_RECEIPT.json
```

Verifier의 archive-only 검증은 실제 Git 원격이나 과거 archive를 조회하지
않는다. 내부 manifest의 Git blob을 실제 bytes에서 다시 계산하며, 생성자가
수행한 실제 commit gate는 archive identity와 외부 영수증에 구분해서 남긴다.
소스 SHA 일치, 실제 Git commit 대조, archive CRC/hash 검증, 업로드 응답,
원격 다운로드 일치는 서로 다른 단계다.

## Archive 구성과 자기참조 배제

- `run18/`: manifest를 포함한 고정 과학 source/results 전체.
- `BASELINE_IDENTITY.json`: RUN17 science commit/tree/manifest와 기존 ZIP 참조.
- `RESTORE_COMMANDS.md`: 공개 repository URL 및 명시적 재현 명령.
- `ARCHIVE_IDENTITY.json`: source commit/tree/parent, source manifest SHA,
  commit gate 결과와 고정 ZIP timestamp의 의미.
- `ARCHIVE_MANIFEST.json`: 자기 자신을 제외한 모든 payload의 path/bytes/SHA/mode.

Archive의 SHA, 실제 생성 시각/실행 명령/환경 및 upload/download receipt는
최종 ZIP 밖에 둔다. `ARCHIVE_IDENTITY.json` 안에 ZIP 자신의 SHA를 넣지 않는다.
토큰, 임시 signed URL 또는 인증 credential을 helper에 넣지 않았다.

고정 RUN17 참조는
`REI_RUN17_FIRST_BIRTH_RESIDUAL_20261019_125500Z.zip`, **4,247,502 bytes**,
SHA-256 `2392f298e8c93aaba0bd802a14c0b34c142bf2c848fbae83d6aa80302de1f523`이다.
이 helper 준비 작업에서는 기존 ZIP 재다운로드나 과학 재계산을 하지 않았다.

## 이번 준비 단계의 실제 검증

`PREPARATION_RECEIPT.json`에는 두 Python source를 메모리에서 syntax compile한
결과와 각 `--help`의 실제 exit code 0을 기록했다. 아직 RUN18 ZIP을 생성하거나
실제 archive의 CRC를 검사하지 않았다. Root의 최종 freeze·commit 이후 위
명령의 실행 영수증이 추가되어야 해당 단계의 완료를 표시할 수 있다.
