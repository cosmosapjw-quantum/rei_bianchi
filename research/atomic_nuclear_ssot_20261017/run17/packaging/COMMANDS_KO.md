# RUN17 archive 준비 및 동결 후 실행

이 디렉터리는 RUN16의 실제 create_archive.py와 verify_archive.py를 바탕으로 만든 RUN17 전달 도구다. 원래 파일은 수정하지 않았다. 최초 준비 시점에는 archive를 만들거나 복원하거나 업로드하지 않았다.

## 동결 입력

run17/SCIENCE_MANIFEST.json은 schema `rei.run17.complete-science-manifest.v1`을 사용한다. `files`의 각 항목은 path, bytes, sha256, git_blob, git_mode를 갖는다. Manifest 자체는 제외하며, file_count_excluding_this_manifest와 payload_bytes_excluding_this_manifest가 일치해야 한다. `excludes_itself`는 true다. Root가 최종 source/results 및 이 도구를 canonical run17에 넣은 다음 manifest를 만들고 science commit과 tree를 고정한다.

Archive에는 다음만 넣는다.

- Manifest를 포함한 frozen run17 전체 파일.
- 원래 gas_rhs_server, 571,904 bytes, SHA256 `3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`.
- RUN16 HEAD45ee7192, RUN15 HEADc875005e 및 기존 backup의 정확한 identity.
- 고정 science commit에서 시작하는 Git checkout·delta 복원 명령.
- 내부 ARCHIVE_IDENTITY.json 및 자기 자신을 제외한 ARCHIVE_MANIFEST.json.

기존 41 MB RUN15 archive나 toolchain은 중복하지 않는다. Native source는 pinned Git에 있다. Archive SHA, 실제 생성 시각·환경·명령, 업로드·다운로드 영수증은 archive 밖에 기록한다. ZIP timestamp는 1980-01-01의 고정 serialization 값으로 실행 날짜를 뜻하지 않는다. 동일 payload 및 zlib 구현에서 일관된 바이트를 만들며 별도 반복 압축 시험을 요구하지 않는다.

## 과학 결과 동결 후에만 실행

아래 task 전용 변수는 root가 실제 확인한 경로와 science commit/tree로 지정한다. 기존 파일을 덮어쓰지 않으므로 output과 receipt에는 새 이름을 사용한다.

```sh
mkdir -p /tmp/rei_run17_delivery
python3 -B /tmp/rei_run17_work/packaging/create_archive.py \
  --run17-root /tmp/rei_run17_repo/research/atomic_nuclear_ssot_20261017/run17 \
  --gas-binary "$RUN17_GAS_BINARY" \
  --science-commit "$RUN17_SCIENCE_COMMIT" \
  --science-tree "$RUN17_SCIENCE_TREE" \
  --output /tmp/rei_run17_delivery/REI_RUN17_DELTA.zip \
  --receipt /tmp/rei_run17_delivery/PACKAGING_RECEIPT.json
```

실제 archive SHA는 이 명령이 출력한 receipt에서 선택한다. 이후 필요한 로컬/원격 readback을 같은 검증기로 확인한다.

```sh
python3 -B /tmp/rei_run17_work/packaging/verify_archive.py \
  /tmp/rei_run17_delivery/REI_RUN17_DELTA.zip \
  --sha256 "$RUN17_ARCHIVE_SHA256" \
  --restore-to /tmp/rei_run17_delivery/restored \
  --output /tmp/rei_run17_delivery/RESTORE_RECEIPT.json
```

검증기는 모든 member를 읽어 CRC, 경로, 파일 유형, mode, manifest의 크기·SHA, science manifest의 Git blob, 원래 gas identity를 확인한 뒤에만 새 directory를 만든다. Symlink와 기존 destination을 거부하고, 전체 uncompressed 크기는 100 MiB로 제한한다. 복원된 각 파일의 실제 바이트와 mode도 확인한다. Archive verification과 restoration은 native binary·unit tests·과학 코드를 자동 실행하지 않는다.

## Clean Git 및 Python 범위

Archive 안의 RESTORE_COMMANDS.md는 게시된 science SHA와 RUN16 baseline45ee7192를 명시한 실제 git fetch/checkout 명령을 포함한다. 원래 RUN13의 두 lossless Git transport 파일은 다음의 명시적 destination을 사용해 복원한다.

```sh
python3 -B /tmp/rei_run17_clean_source/research/atomic_nuclear_ssot_20261017/run13/git_transport/restore.py \
  --destination-root /tmp/rei_run17_clean_source/research/atomic_nuclear_ssot_20261017/run13/recovered
```

RUN17 core-module/unit 검사와 저장 상태 postprocess의 정확한 명령은 science source의 이름과 CLI가 동결된 후 root 소유 REPRODUCE_KO.md에 둔다. 아직 없는 module 이름을 추정하지 않는다. 최종 archive에는 그 문서도 frozen science의 일부로 포함된다. Full native campaign이나 완료된 RUN13/RUN16 계산을 기본 복원 동작에 넣지 않는다.

## 이번 준비의 검증 지위

PREPARATION_RECEIPT.json은 실제 syntax parse 및 두 CLI --help 실행만 기록한다. 실제 payload의 archive 검증·복원·원격 Git readback은 source freeze와 게시 후 수행할 별도 전달 단계다.
