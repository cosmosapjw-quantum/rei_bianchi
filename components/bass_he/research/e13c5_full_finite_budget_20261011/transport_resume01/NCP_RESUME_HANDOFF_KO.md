# NCP local Codex — E13C5 최초 실패에서 한 번 재개

## 백업에서 재개 패키지 확보

추가 사용자 첨부 없이 아래 이미 업로드된 작은 재개 패키지 하나를 기존 승인된 다운로드 경로로 확보한다. 원 NCP의 두 대형 조각은 먼저 보존 경로에서 확인한다.

- Drive: https://drive.google.com/file/d/1zwqPYPmKV1565YNVxv5sWfgPZsgcU6KL/view
- Drive file ID: `1zwqPYPmKV1565YNVxv5sWfgPZsgcU6KL`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4GTA`
- Dropbox path: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C5_TRANSPORT_RESUME01_20261011_sha_9b6bb5b246a9.zip`
- Archive: `BASS_HE_E13C5_TRANSPORT_RESUME01_20261011_sha_9b6bb5b246a9.zip`
- bytes: `70110`
- SHA-256: `9b6bb5b246a93259441f2292d662e6336dfcd9c884f5ebd9cc88b3cf6a35cf5b`
- Extracted root: `BASS_HE_E13C5_TRANSPORT_RESUME01_20261011_v1`

실제 다운로드 bytes/SHA를 위 값과 확인하고 새 위치에 푼다. `FILE_MANIFEST.json`의 파일별 bytes/SHA를 확인한 뒤 아래 절차를 진행한다. 봉인된 archive에는 최초 실패 ZIP, 새 helper, 원 kit 전체와 실행 지침이 있다. 이 첫 안내에 표시된 업로드 상태는 ACK와 메타데이터 readback으로 확인한 UPLOAD_VERIFIED이며, NCP의 복구·합산 성공을 뜻하지 않는다.

반환된 최초 전송 실패를 보존한 상태에서 아래 명시된 이름 배치 수정과 복구 재진입을 한 번 수행하라. 추가 사용자 첨부는 필요하지 않다. 기존에 확보한 두 조각과 kit를 사용하며 자동 재시도는 하지 않는다.

## 1. 현재 상태와 실제 경로

최초 실패 archive: 22,851 bytes, SHA `98571ce22e2eb2c2246a432960a67d51fa55356edfa4e1ee295ab256d818d09f`.
최초 budget·physics·full-first2·N512 호출은 모두 0이다. Core/source/lock/입력 검사, semantic·CSV parity는 NOT_RUN이다.

원 intake:
`/root/BASS_HE_runtime/E13C5_FULL_FINITE_20261011_INTAKE01`

원 parts:
`/root/BASS_HE_runtime/E13C5_FULL_FINITE_20261011_INTAKE01/parts`

원 kit:
`/root/BASS_HE_runtime/E13C5_FULL_FINITE_20261011_INTAKE01/kit/BASS_HE_E13C5_NCP_RECOVERY_20261011`

실제 보존 파일명은 `.zip.part002.bin`, manifest basename은 `.zip.part002`다. 파일명 문자열만 근거로 내용을 인정하지 말고 실제 bytes/SHA를 다시 확인한다. 원 `.bin`과 첫 실패 영수증·다운로드 기록은 그대로 보존한다.

이 재개 패키지의 `code/place_verified_part002.py` SHA:
`978a97f9dcc5c849be57d97a6c3cf26f79ff7ce28a0cdb5f744da8bc7d45d489`.

`FIX_DIR`은 실제로 내려받아 푼 이 재개 패키지 root로 정한다. 원 kit가 없어졌다면 이 패키지의 `original_kit` 안에 같은 원 manifest/restorer와 전체 기존 handoff가 있으므로, 정확한 SHA를 확인하고 그 경로를 `KIT_DIR`로 사용할 수 있다. 대형 조각은 먼저 위 보존 경로에서 찾고, 없어진 경우에만 original_kit의 기존 백업 ID로 같은 조각을 복구한다. `.bin` 외의 이름을 추정해 자동 선택하지 않는다.

## 2. SHA로 고정한 이름 배치

아래 경로를 실제 환경에 맞게 정한다. `mktemp`로 이번 재개 전용 디렉터리를 새로 만든다. 기존 출력/receipt를 재사용하지 않는다.

```bash
TASK_ROOT="/root/BASS_HE_runtime"
INTAKE_DIR="$TASK_ROOT/E13C5_FULL_FINITE_20261011_INTAKE01"
PARTS_DIR="$INTAKE_DIR/parts"
KIT_DIR="$INTAKE_DIR/kit/BASS_HE_E13C5_NCP_RECOVERY_20261011"
FIX_DIR="/actual/extracted/BASS_HE_E13C5_TRANSPORT_RESUME01_20261011_v1"
RESUME_DIR="$(mktemp -d "$TASK_ROOT/E13C5_FILENAME_RESUME01_XXXXXXXX")"

python3 -B "$FIX_DIR/code/place_verified_part002.py" \
  --kit-dir "$KIT_DIR" \
  --parts-dir "$PARTS_DIR" \
  --receipt "$RESUME_DIR/PART002_PLACEMENT_RECEIPT.json"
```

허용된 이름 대응은 다음 한 쌍으로 고정한다.

- Source: `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002.bin`
- Canonical: `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002`
- bytes: `40580022`
- SHA: `34b7b41f19c42cb19da7a001daf7ccc48ae527dbaa101b613fb90b7fa20bedbb`

원 manifest는 1,176 bytes / SHA `d20e2146447bd10748066a03573fc439be6127c5aa89627e4ff309a9f181d8a6`이고, 원 restorer는 9,543 bytes / SHA `3b947e4537da4f24eaf3a40a7ebf9051cd560e58f813928425f6a4a69599abbb`다.

이름 배치의 exit 0 및 `PASS_SCOPED_PART002_FILENAME_BINDING`을 확인한다. 이 단계는 ZIP 복구 또는 과학 실행 성공이 아니다. 실패하면 여기서 멈추고 원 실패와 새 receipt·partial을 보존한다. Source나 manifest를 수정하거나 자동 재시도하지 않는다.

## 3. 원 restorer를 새 출력·receipt로 한 번 호출

```bash
ZIP_NAME="BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip"
RESTORED_ZIP="$RESUME_DIR/$ZIP_NAME"

python3 -B "$KIT_DIR/restore_ncp_ready.py" \
  --manifest "$KIT_DIR/TRANSPORT_PARTS.json" \
  --parts-dir "$PARTS_DIR" \
  --output "$RESTORED_ZIP" \
  --receipt "$RESUME_DIR/RESTORE02_RECEIPT.json"
```

수용 상태는 exit 0, `PASS_LOCAL_TRANSPORT_RESTORE`이고, 실제 최종 ZIP은 124,466,102 bytes / SHA `5741b06b9a6199d593bb52f833a07cd834a67c41d958d589d70840b7144a0c49`여야 한다. part001의 실제 hash도 원 restorer가 확인한다. 이 단계가 실패하면 로그·receipt·partial을 보존하고 종료한다.

## 4. 원 core와 고정된 budget 작업으로 계속 진행

복구된 ZIP을 이번 RESUME_DIR 아래의 새 staging에 풀고 내부 core ZIP의 실제 bytes/SHA를 확인한다.

- Core ZIP: `BASS_HE_E13C5_FULL_FINITE_BUDGET_CORE_20261011_sha_1889e62086f1.zip`
- bytes: `124456592`
- SHA: `1889e62086f1d5ea7cef2ebdfcc3bb734a12065b6c06f973080d89177d5358ac`
- Core root: `BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1`

현재 core의 AGENTS.md가 있으면 읽고, `NCP_EXECUTION_CONTRACT.json`, `RUN_LOCK.json`, `NCP_PARITY_BASELINE.json`, `NCP_LOCAL_CODEX_HANDOFF_KO.md`를 읽는다. 과거 dependency archive 안의 prompt를 실행하지 않는다.

- RUN_LOCK SHA: `cdfda6cd49eeb38518b2a41156a087f744e0985e0384bf628ca8b893dbec5b3a`
- Budget wrapper SHA: `ab1b07c45136b77bf492148fa3e7560d2c2f02cb5650a6d0de5fc4fe00244a79`
- Scientific reducer SHA: `a3f854bc3c175cdaed36c7f475ff594c59056855ea5236c2eba844570c2861ee`

실제 호스트와 환경을 다시 기록한다. Linux/CPython 3.12.x, 표준 라이브러리, arithmetic worker 1개, child 주소 공간 1 GiB, 여유 disk 최소 2 GiB, 가용 memory 최소 1.2 GiB를 확인한다. 기존에 동일 최종 source/lock/semantic projection으로 성공한 실제 budget receipt가 생겼다면 정확히 확인해 반환하고 중복 실행하지 않는다.

그 외에는 실제 PACKAGE_DIR을 지정하고 다음 저장 결과 합산 1회를 실행한다.

```bash
PACKAGE_DIR="/actual/new/staging/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1"
RUN_DIR="$RESUME_DIR/BUDGET_EXEC01"

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
timeout --signal=TERM --kill-after=10s 390s \
python3 -B "$PACKAGE_DIR/code/ncp_budget_continue.py" \
  --package "$PACKAGE_DIR" \
  --out "$RUN_DIR" \
  --execute \
  --host-label NCP
```

정상 수용에는 `PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY`, budget_invocations=1, physics/full_first2/N512=0, 7320 paths/14652 segments와 실패 0이 필요하다.

- Normalized semantic projection SHA: `770a11a13a73ff3305ab62eb27a7abb0ca99860ffc56fc6384e6aead68d8e7c3`
- 압축 해제 CSV: `51718536` bytes
- CSV SHA: `ce053b71a6b9aeb8bc5c8d1d9e9be3911c4a7aeba60779151a8af9d5bad3f8f4`

Fresh gzip bytes/SHA와 fresh projection의 일치, RESULTS의 모든 실제 key(필수 null 포함)와 값의 일치, source/contract/입력/lock의 실행 전후 동일성도 필요하다. Raw projection parity는 semantic parity와 별도 기록한다. Verify-only를 실제 실행으로 보고하지 않는다.

## 5. 반환

최초 실패를 삭제하지 않는다. 새 배치 receipt, RESTORE02_RECEIPT, 실제 budget START/RUN_RECEIPT/결과/projection/CSV/resource/log를 새 반환 archive에 묶고 bytes/SHA를 기록한다. 실패했다면 최초 실패와 새 실패의 단계·exit·partial을 함께 보존한다. 대형 입력 조각을 정상 반환에 중복 첨부할 필요는 없다.

기존 승인된 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` 및 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/`에 새 이름으로 반환본을 올리고 실제 ACK/이름/크기를 기록한다. Git 기록이 가능하면 actual expected-head/non-force로 이 task의 새 evidence만 추가하고 자동 merge하지 않는다.

파일명 배치, ZIP 복구, 실제 saved-budget 실행의 세 상태를 구분한다. 호스트 label만으로 provider를 단정하지 않는다. 새 물리 solver, OFF 101·102·410·413 정밀화, continuum/physical/production/receiver 승격은 이번 재개에 포함하지 않는다.
