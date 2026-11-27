# BASS_HE 최초 NCP 전송 실패의 제한적 독립 확인

반환 기록과 고정된 전송 코드를 대조한 결과, 최초 실패는 **manifest가 요구하는 part002 파일명과 실제 다운로드 파일명의 불일치**로 설명된다. 과학 합산은 시작되지 않았고, 실제 NCP 재현 상태는 **NOT_RUN**이다. 이 검토는 실패 원인과 최소 재개 조건만 다루며 새 이름 복사 helper의 구현 시험, 원본 ZIP 복구 또는 과학 실행은 수행하지 않았다.

## 직접 확인한 증거와 그 한계

고정 기준은 Git commit `3761cf183b043d648b2d0254fa318af3510fd849`의 `research/e13c5_full_finite_budget_20261011/delivery/`다. 해당 기준의 `restore_ncp_ready.py`, `TRANSPORT_PARTS.json`, 최종 handoff를 독립적으로 읽었다. 반환본에 포함된 restorer와 manifest의 실제 bytes/SHA 및 Git blob SHA는 고정 기준과 일치한다.

반환 archive의 actual saved bytes/SHA 확인은 root가 수행했다: 22,851 bytes, `98571ce22e2eb2c2246a432960a67d51fa55356edfa4e1ee295ab256d818d09f`. 이 검토에서는 안전하게 추출된 두 실패 기록을 직접 읽고 그 파일 identity를 기록했다. 약 124 MB의 실제 두 조각은 작은 반환 archive에 포함되어 있지 않다. 따라서 두 조각의 해시는 **반환된 수신 측 hash 기록과 manifest 사이의 일치**로 확인했으며, 이 검토자가 실제 NCP 조각을 재해시한 것으로 표현하지 않는다.

| 항목 | 확인 결과 |
|---|---|
| Manifest part002 | `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002` |
| 수신 측 inventory의 part002 | 위 이름에 `.bin`이 추가된 파일 |
| 기록된 part002 크기·SHA | 40,580,022 bytes; `34b7b41f19c42cb19da7a001daf7ccc48ae527dbaa101b613fb90b7fa20bedbb` — manifest와 일치 |
| 원 restore 결과 | `FAIL_LOCAL_TRANSPORT_RESTORE`, `FileNotFoundError`, exit 1 |
| 원 restore가 지적한 파일 | 정확한 manifest part002 basename |
| 원 restore의 부분/최종 출력 | 생성되지 않은 것으로 기록됨 |
| `verified_parts` | 빈 배열 |
| budget / physics / full-first2 / N512 | 모두 0으로 기록됨 |
| Core/source/lock/입력 및 semantic·CSV parity | 미수행 |

원 restorer는 모든 manifest 항목의 정확한 파일명·regular-file·size를 먼저 검사한 다음에야 partial output을 열고 조각별 해시를 계산한다. 따라서 part002 이름이 없으면 첫 번째 part가 정상이어도 `verified_parts=[]`로 실패한다. 별도로 기록된 다운로드 해시 확인과 모순되지 않는다. 이 자료로 Drive가 항상 `.bin`을 추가한다거나 provider 자체에 결함이 있다고 일반화할 수는 없다.

호스트 기록은 `s1a0e5abed09`, Linux kernel `6.8.0-124-generic`, glibc 2.39, Python 3.12.3, CPU affinity 0–63이다. Ubuntu 24.04.1은 사용자의 보고다. 별도의 provider attestation은 없다.

## 최소 재개 계약

기존 `PARTS_DIR`은 `/root/BASS_HE_runtime/E13C5_FULL_FINITE_20261011_INTAKE01/parts`이고, kit는 같은 intake의 `kit/BASS_HE_E13C5_NCP_RECOVERY_20261011`이다. 원 `.bin`과 최초 실패 영수증을 보존한 상태에서, 명시된 `.part002.bin` 파일만 고정된 `.part002` basename으로 새로 복사하면 된다. 실제 NCP source와 디스크에 저장된 복사본 모두 위 크기·SHA에 맞아야 하며, 이미 존재하는 대상이나 symlink는 덮어쓰지 않아야 한다. 임시 파일을 새로 독점 생성하여 완전 쓰기·fsync·persisted hash를 확인한 뒤 비덮어쓰기 방식으로 게시하는 것이 적합하다.

Manifest와 원 restorer는 그대로 유지한다. 임의의 glob 검색, 접미사 일괄 제거, 유사한 파일명 또는 부분 hash를 이용한 후보 선택은 필요하지 않다. 이름 복사 성공 후에 원 restorer를 **새 출력 및 새 명시적 receipt**로 한 번 호출한다. 출력은 `PARTS_DIR` 밖에 둔다. `PASS_LOCAL_TRANSPORT_RESTORE`와 원본 ZIP의 124,466,102 bytes 및 SHA `5741b06b9a6199d593bb52f833a07cd834a67c41d958d589d70840b7144a0c49`가 확인되어야 다음 단계로 갈 수 있다.

그 뒤에는 이미 봉인된 core/source/lock 계약에 따라 저장 결과 합산 wrapper를 한 번 실행한다. 이름 복사나 ZIP 복구만 성공한 상태를 NCP 합산 성공으로 표현하면 안 된다. 새로운 실패가 나면 해당 증거를 보존하고 정지하며, 자동 재시도나 source/P/N/tolerance 변경은 하지 않는다.

이번 검토 범위에서 재개 계약을 막는 구체적 결함은 없다. 실제 source의 사후 변경, 기존 canonical 파일 또는 동시 생성, 쓰기·fsync 실패는 새 helper가 다루어야 할 실제 경계다. 새로운 helper의 집중 대조 결과와 실제 NCP 재진입은 별도 기록이 필요하다.

## 기준 자료

- [원 restorer](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3761cf183b043d648b2d0254fa318af3510fd849/research/e13c5_full_finite_budget_20261011/delivery/restore_ncp_ready.py)
- [원 transport manifest](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3761cf183b043d648b2d0254fa318af3510fd849/research/e13c5_full_finite_budget_20261011/delivery/TRANSPORT_PARTS.json)
- [고정된 최종 handoff](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3761cf183b043d648b2d0254fa318af3510fd849/research/e13c5_full_finite_budget_20261011/delivery/NCP_LOCAL_CODEX_HANDOFF_KO.md)
- 반환 `EXECUTION_BOUNDARY_FAILURE.json`: SHA `b70ef9ae496963209be1aff567073b11a8c224b08c725bd519fdebaa8a2a3426`.
- 반환 최초 restore receipt: SHA `3a4c0721060faee58ddb99d265564f807febee494805b3a71fdf5a7f72b55fd1`.
