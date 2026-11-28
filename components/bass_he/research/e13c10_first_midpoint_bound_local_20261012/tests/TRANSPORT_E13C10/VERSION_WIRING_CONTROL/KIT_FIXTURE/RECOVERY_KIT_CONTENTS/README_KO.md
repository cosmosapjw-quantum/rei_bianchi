# BASS_HE E13C10 recovery kit

이 kit와 E13C10 COMPLETE ZIP 하나 또는 manifest의 모든 조각을 받으면
추가 과학 입력 첨부 없이 predecessor 전체를 복구할 수 있다.
새 NCP 중량 작업은 **0개**다. 완료·채택·미실행의 정확한 범위는 함께 들어 있는
`CURRENT_STATE.json`, `NCP_HANDOFF_INTERNAL_KO.md`, `NEXT_DAG.json`을 따른다.
복구 도구는 과학 코드, MPI, benchmark, 서버 확보를 실행하지 않는다.

## 외부 handoff에서 먼저 확인할 identity

이 kit ZIP 자체의 bytes/SHA는 외부 최종 handoff가 제공한다. kit 내부에
자기 ZIP hash를 넣지 않는다. 외부 handoff의 pin과 다운로드한 실제 bytes를
확인한 뒤 압축을 푼다. 내부 파일의 주요 pin은 다음과 같다.

| 파일 | Bytes | SHA-256 |
|---|---:|---|
| `restore_transfer_e13c10.py` | 19525 | `c2b38592e8ff701de0f7de17fc569d9ac4bc47414a0449d32631d2c7ee3d0ee8` |
| `BASS_HE_E13C10_TRANSFER_MANIFEST.json` | 1875 | `ca5eea717c7279cd439e2834e7dc4b58d834b3bc6a2e3d45d97cdfb0e46f160e` |
| `BASS_HE_E13C10_COMPLETE_20261012T000000Z_sha_0f08040da0bd.zip` | 20763 | `0f08040da0bdc5fd5ba871246b7299a67b71f1e94370d51dddd54cb0d5368d9e` |

실제 원격 위치는 제공된 `BACKUP_LOCATIONS.json` 또는 외부 owner handoff를 따른다.
이 builder는 업로드나 원격 재다운로드를 수행하지 않았다.

## Drive 조각

| 순서 | Bytes | Canonical name | SHA-256 |
|---:|---:|---|---|
| 1 | 20763 | `BASS_HE_E13C10_COMPLETE_20261012T000000Z_sha_0f08040da0bd.zip.part001` | `0f08040da0bdc5fd5ba871246b7299a67b71f1e94370d51dddd54cb0d5368d9e` |

파일명에 `.bin`이 붙어도 변경할 필요가 없다. Helper는 실제 bytes/SHA로 조각을
찾고 manifest 순서로 결합한다. 원본 다운로드 이름과 파일은 보존한다.

## 복구 명령

실제 파일 소실 또는 복구 필요가 있을 때 아래 두 source mode 중 하나만 실행한다.
현재 디렉터리는 압축을 푼 kit, 다운로드 디렉터리는 `../downloads`, 출력은 아직
존재하지 않는 `../RESTORED_E13C10_ATTEMPT01`이라고 가정한다.

```bash
python3 -B ./restore_transfer_e13c10.py \
  --manifest ./BASS_HE_E13C10_TRANSFER_MANIFEST.json \
  --manifest-sha256 ca5eea717c7279cd439e2834e7dc4b58d834b3bc6a2e3d45d97cdfb0e46f160e \
  --parts-dir ../downloads \
  --output-dir ../RESTORED_E13C10_ATTEMPT01 \
  --hydrate
```

COMPLETE ZIP을 받은 경우 위 `--parts-dir ../downloads` 대신 다음 인자를 사용한다.

```bash
--archive ../downloads/BASS_HE_E13C10_COMPLETE_20261012T000000Z_sha_0f08040da0bd.zip
```

출력은 `<output>/package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1`이며, 이전 E13C9 복구는
`<output>/runtime/E13C9`다. 그 아래의 `runtime/E13C8`에 E13C8이 복구되고,
원래 E13C7 입력과 완료된 heavy return은 그 E13C8 출력의
`runtime/E13C7_INPUT`, `runtime/E13C7_NCP_RETURN`에 있다.

이 COMPLETE ZIP은 `dependencies/E13C9_COMPLETE.zip`과
`dependencies/E13C9_RECOVERY_KIT.zip`을 이미 포함한다. E13C9의 고정 helper가
그 안에 포함된 E13C8과 더 오래된 입력/반환을 한 번씩 펼친다.
새 과학 계산은 수행하지 않는다.

성공 상태는 `RESTORE_RECEIPT.json`의 `PASS_COMPLETE_RESTORE`다.
실패하면 `FIRST_FAILURE.json`, stdout/stderr, 기존 다운로드와 부분 출력을
보존한다. 자동 재시도나 기존 출력 덮어쓰기는 없다. 원인을 수정한 후 새 출력
디렉터리로 재개한다. `--hydrate`를 생략하면 E13C10의 모든 outer payload만
검증·추출하며 predecessor ZIP을 펼치지 않는다.

복구 경로 검증의 고정 제한은 ZIP당 50,000 members, expanded bytes 2 GiB,
embedded manifest 16 MiB다. Traversal·symlink·중복 member/JSON key 등은 거부한다.
해시는 byte identity 근거이며 과학적 승격, provider attestation 또는 새 실행
권한의 근거가 아니다. 포함된 영수증을 실제 수행 범위와 함께 읽는다.

## 이 kit에 포함된 확인 범위

- 원격 위치: `COPIED_OWNER_LOCATION_RECORD; no remote readback or redownload by this builder`
- 실제 복구 기록: `COPIED_ACTUAL_BYTE_MATCHED_E13C10_HYDRATION_RECEIPT; no repeat restoration`
- kit 조립: 작은 파일 복사와 실제 kit payload bytes 검증만 수행한다.
- COMPLETE archive 재해시, 대용량 복구 반복, science/MPI/NCP 실행은 0이다.
