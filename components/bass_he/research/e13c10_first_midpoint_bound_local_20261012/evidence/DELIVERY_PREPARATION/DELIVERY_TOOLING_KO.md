# E13C10 self-contained backup tooling — owner integration

## 완료 범위

이 준비 작업의 파일은 모두 `TASK/delivery_tools`에 있다. 실제 ROOT10의 code,
수치 결과, 계약은 변경하지 않았다. 실제 E13C10 COMPLETE ZIP·recovery kit를
아직 만들지 않았고 실제 E13C9 hydration도 수행하지 않았다. 아래 명령은
owner가 과학 결과·독립 판정·보고서를 확정한 뒤 실행하는 전달 절차다.

준비한 실행 파일은 다음 세 개다.

- `restore_transfer_e13c10.py`: E13C10 COMPLETE/parts를 확인하고, 요청할 때만
  포함된 고정 E13C9 helper를 1회 호출한다.
- `build_complete_e13c10.py`: 최종 package를 seal하고 actual archived bytes를
  검증한 뒤 complete ZIP, 64 MiB parts, external transfer manifest를 만든다.
- `build_recovery_kit_e13c10.py`: seal된 state·internal handoff, complete build
  기록 및 optional 실제 복구/원격 위치 증거에서 작은 kit를 만든다.

새 helper의 이름은 package에서는 `code/restore_transfer_e13c10.py`, kit에서는
`restore_transfer_e13c10.py`다. predecessor kit 내부의 원래 E13C9 helper 이름은
그대로 `restore_transfer.py`다. 이름을 서로 바꾸지 않는다.

## 원본과 변경

`RESTORE_E13C9_TO_E13C10.diff`와 `BUILD_E13C9_TO_E13C10.diff`에 원본 대비 변경이
있다. Restore의 12개 transport 함수는 AST 비교에서도 그대로다:
`utc_now`, `sha`, `pin`, `valid_pin`, `verify_file`, `save`, `unique_object`,
`load_json`, `safe_relative`, `select_parts`, `reassemble`, `extract_verified`.

바뀐 것은 root/schema, dependency pin, 새 helper 파일명, E13C9 hydration
경로·로그명, 그리고 predecessor receipt의 정확한 필드 연결이다.
E13C9 receipt에서 `hydrated_E13C8.returncode == 0`, predecessor restore invocation
1회, science/MPI/NCP execute/자동 재시도 0회를 요구한다. 새 receipt에는
`hydrated_E13C9`와 그 아래 `prior_hydrated_E13C8`를 기록한다.

기존 actual-byte part 선택, `.bin`을 포함한 suffix 무관 처리, exact SHA,
safe paths, member set, 중복 거부, fresh output, 첫 실패 보존, no retry는 유지했다.
기존 suffix/path 보안 suite를 다시 돌리지 않았다.

## 고정 predecessor identity

| 새 package 상대 경로 | bytes | SHA-256 |
|---|---:|---|
| `dependencies/E13C9_COMPLETE.zip` | 173671016 | `41b4bfeae3b6795adbe2e78f5f519ee835ee8921b54bebd7d6c88ab63aae9bcc` |
| `dependencies/E13C9_RECOVERY_KIT.zip` | 50071 | `722fb58d34f8d6eada3819ca4873bcb86f1c598984346fbce1c7ce855a2866bc` |

내장 E13C9 kit에서 실행할 실제 원본은 다음과 같다.

| kit 상대 파일 | bytes | SHA-256 |
|---|---:|---|
| `restore_transfer.py` | 19183 | `0588620bae490bc66ef8ba6daf2b4471627feeba3d5620dca6742cc224283fe9` |
| `BASS_HE_E13C9_TRANSFER_MANIFEST.json` | 2347 | `e93f1dbe430bf40147c3b06b3d2e43531db150c3df84763a1a4bb256db66bead` |

E13C9 COMPLETE는 원래 E13C8 COMPLETE/kit, 그 안의 E13C7 입력과 완료된 heavy
return까지 이미 포함한다. 따라서 사용자는 새 kit와 새 COMPLETE ZIP 또는 그
모든 parts만 받으면 된다. 별도의 과학 입력 첨부가 필요하지 않다.

## 최종 package에 넣을 파일

최종 package 이름은 정확히 다음이어야 한다.

`BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1`

owner는 seal 전에 세 실행 파일을 같은 bytes로 package의 `code/`에 복사하고,
위 두 predecessor ZIP을 `dependencies/`의 지정 이름으로 둔다. 실제 원본은
현재 다음 위치에 있다.

```text
/workspace/scratch/7fd51143e473/e13c10_research_20261012/recovered/BASS_HE_E13C9_COMPLETE_20261011T201515Z_sha_41b4bfeae3b6.zip
/workspace/scratch/7fd51143e473/e13c10_research_20261012/recovered/BASS_HE_E13C9_RECOVERY_KIT_20261011T202311Z_sha_722fb58d34f8.zip
```

package에는 owner가 확정한 `CURRENT_STATE.json`, `NEXT_DAG.json`,
`NCP_HANDOFF_INTERNAL_KO.md`도 있어야 한다. `CURRENT_STATE.json`에는 새 중량
작업이 없다는 사실을 `"new_NCP_work_units": []`로 명시한다. Kit builder는
특정 PROMOTE 문자열을 만들어 내거나 강제하지 않고 이 sealed state를 복사한다.
external final handoff는 actual COMPLETE/kit hash와 remote ID를 나중에 담을 수
있으므로 seal된 내부 handoff와 별개의 파일로 둔다.

완료된 이 준비 작업의 diff, 문서, control receipt를 보존하려면 package의
`tests/TRANSPORT_E13C10/` 또는 `evidence/DELIVERY_PREPARATION/`에 복사하면 된다.
`VERSION_WIRING_CONTROL` 안의 ZIP과 predecessor는 명시적인 **가짜 fixture**다.
그것들을 실제 `dependencies/` 입력으로 사용하면 안 된다. Production helper의
고정 pin은 해당 fixture bytes를 거부한다.

## COMPLETE build

이 명령은 package에 최초 `PACKAGE_MANIFEST.json`을 생성한다. 따라서 먼저
과학 결과·review·최종 문서·source lock을 끝낸다. 출력은 반드시 새 디렉터리다.
다음은 실제 현재 경로를 사용하는 명령이다. `--stamp`는 owner가 정한 실제
UTC 시각으로 변경한다.

```bash
python3 -B /workspace/scratch/7fd51143e473/e13c10_research_20261012/delivery_tools/build_complete_e13c10.py \
  --package /workspace/scratch/7fd51143e473/e13c10_research_20261012/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1 \
  --output-dir /workspace/scratch/7fd51143e473/e13c10_research_20261012/DELIVERY_E13C10_FINAL \
  --stamp YYYYMMDDTHHMMSSZ
```

`--stamp`를 생략하면 현재 UTC를 사용한다. ZIP member timestamps는 고정이고
경로는 정렬되며 파일 mode와 compression policy도 고정이다. 동일 payload와
동일 compression runtime에서 ZIP content는 결정적이다. dependency ZIP은
재압축하지 않는다. 여러 빌드를 반복하여 이 성질을 별도 검증하지 않았다.

출력은 COMPLETE ZIP, 64 MiB parts와 마지막 작은 part,
`BASS_HE_E13C10_TRANSFER_MANIFEST.json`, `BUILD_RECEIPT.json`이다. 각 archived
payload의 실제 bytes를 embedded manifest와 비교한다. Archive bytes/SHA,
part bytes/SHA, helper pin, package-manifest pin은 실제 생성값만 기록한다.

기존 package manifest 또는 기존 output은 거부한다. Seal 이후 실패하면
`FIRST_FAILURE.json`과 부분 출력을 보존한다. 동일 package를 조용히 unseal하거나
덮어쓰는 자동 복구 경로는 없다.

## 실제 restore는 확정된 backup에 한 번

owner가 필요하다고 결정한 actual restore는 다음 형태다. `--manifest-sha256`와
archive 경로에는 위 실제 build가 만든 값을 사용한다. Helper 준비 작업은 이
actual large restore를 실행하지 않았다.

```bash
python3 -B /workspace/scratch/7fd51143e473/e13c10_research_20261012/delivery_tools/restore_transfer_e13c10.py \
  --manifest /absolute/delivery/BASS_HE_E13C10_TRANSFER_MANIFEST.json \
  --manifest-sha256 ACTUAL_EXTERNAL_MANIFEST_SHA256 \
  --archive /absolute/delivery/ACTUAL_COMPLETE_FILENAME.zip \
  --output-dir /absolute/fresh/RESTORED_E13C10_ATTEMPT01 \
  --hydrate
```

이미 다운로드한 parts가 source이면 `--archive` 대신 `--parts-dir`을 쓴다.
양쪽 모드를 연달아 실행할 필요는 없다. 실제 외부 manifest SHA를 확인해야 하며
다운로드에서 계산한 hash 자체를 기대값의 독립 출처로 취급하지 않는다.

복구 경로는 다음과 같다.

| 내용 | fresh output 아래 경로 |
|---|---|
| E13C10 package | `package/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1` |
| E13C9 restore output | `runtime/E13C9` |
| E13C9 package | `runtime/E13C9/package/BASS_HE_E13C9_SIGNED_VOLTERRA_LOCAL_20261012_v1` |
| E13C8 restore output | `runtime/E13C9/runtime/E13C8` |
| 원래 E13C7 input | `runtime/E13C9/runtime/E13C8/runtime/E13C7_INPUT` |
| 완료된 heavy return | `runtime/E13C9/runtime/E13C8/runtime/E13C7_NCP_RETURN` |

실제 production restoration인지 tiny fixture인지 구분한 상태에서 receipt를
해석한다. 새 helper는 원본 E13C9 helper를 1회 호출하고, 그 원본이 자신의 고정
E13C8 복구를 처리한다. 새 science/MPI/NCP 실행은 없다.

## Recovery-kit build

```bash
python3 -B /workspace/scratch/7fd51143e473/e13c10_research_20261012/delivery_tools/build_recovery_kit_e13c10.py \
  --package /workspace/scratch/7fd51143e473/e13c10_research_20261012/BASS_HE_E13C10_FIRST_MIDPOINT_BOUND_LOCAL_20261012_v1 \
  --delivery-dir /workspace/scratch/7fd51143e473/e13c10_research_20261012/DELIVERY_E13C10_FINAL \
  --output-dir /workspace/scratch/7fd51143e473/e13c10_research_20261012/RECOVERY_KIT_E13C10_FINAL \
  --stamp YYYYMMDDTHHMMSSZ
```

`--stamp`는 required다. Optional 인자는 실제 해당 증거가 있을 때만 추가한다.

| 인자 | 용도·조건 |
|---|---|
| `--backup-locations PATH` | owner가 이미 확인한 실제 위치 JSON. `archive`의 bytes/SHA가 transfer와 같아야 하며, `parts`가 있으면 index/order/bytes/SHA가 일치해야 한다. builder가 ACK나 원격 readback을 수행한 것으로 기록하지 않는다. |
| `--restore-output PATH` | 이미 완료된 실제 E13C10 restore output. 성공 receipt, external manifest SHA, archive, invocation 0/1을 대조하고 작은 receipts/logs만 복사한다. 복구를 반복하지 않는다. |
| `--handoff PATH` | package 내부에 seal된 다른 internal handoff 경로. 기본값은 `NCP_HANDOFF_INTERNAL_KO.md`다. Seal되지 않은 외부 final handoff를 집어넣는 옵션이 아니다. |
| `--extra-file RELATIVE=PATH` | 작은 기존 증거를 kit에 추가. 파일당 최대 16 MiB, canonical relative path, 중복/reserved 이름 거부. 필요 없으면 생략한다. |

kit에는 versioned helper, transfer manifest, COMPLETE build receipt, current state,
next DAG, sealed internal handoff, 두 builder, generated readme/provenance 및
`KIT_MANIFEST.json`이 들어간다. Optional evidence는 지정한 것만 추가한다.
kit manifest는 자기 자신을 제외한 모든 payload를 pin한다. Actual kit bytes/SHA는
외부 `RECOVERY_KIT_BUILD_RECEIPT.json` 및 최종 owner handoff에 둔다.

kit 조립은 COMPLETE를 다시 해시하거나 large restore를 호출하지 않는다.
동일 source bytes와 동일 `--stamp`에 대해 metadata/ZIP member ordering은 고정된다.
업로드는 수행하지 않는다. 원격 backup 기록은 owner가 생성한 근거로 분리한다.

## 이번에 실제 수행한 최소 제어

`test_version_wiring_e13c10.py`를 1회 실행했다. 작고 명시적으로 가짜인
predecessor와 in-memory fixture pins로 COMPLETE builder → new restore → kit
builder의 바뀐 연결만 확인했다. Production code bytes는 변경하지 않았다.

- **16 checks / 0 failures**, elapsed **0.06805034800345311 s**.
- actual large complete build 0, actual pinned predecessor invocation 0.
- fake predecessor subprocess 1, tiny fixture COMPLETE/restore/kit invocation 각각 1.
- scientific kernel/MPI/NCP execute/external mutation/자동 재시도 0.
- 이름·schema·E13C9 dependency·새 receipt nesting·optional kit evidence·transfer pin 확인.
- unchanged restore 함수 12개는 AST로 확인. 옛 security suite를 반복하지 않음.

원 결과는 `VERSION_WIRING_CONTROL/VERSION_WIRING_CONTROL_RECEIPT.json`과
각 entry stdout/stderr에 있다. 실제 archive chain의 복구 완료를 뜻하지 않는다.
최종 패키지 승격은 owner의 science와 실제 독립 decision에 의존한다.

## 고정 제한

각 추출당 ZIP member 최대 50,000개, expanded bytes 최대 2 GiB,
embedded manifest 최대 16 MiB다. 모든 실제 output은 새 경로이며 자동 재시도는
없다. 물리/continuum/production/receiver는 이 transport tooling에서 승격하지
않는다. Hash는 bytes identity이며 provider attestation이나 실행 권한이 아니다.
