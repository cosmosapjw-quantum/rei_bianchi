# REI BASS atomic-storage 최종 ZIP 비용 진단과 재개 계약 — 2026-10-28

## 현재 판정

기존 연구 판정은 `PASS_SCOPED_FINITE_BASS_ATOMIC_STORAGE_REPRESENTATION`이다. 이론 R1–R10과 코딩 C1–C10은 20/20 완료 상태를 재사용한다. 원래 DAG는 작업 33/88, 중앙 28/88이며 88 IDs와 17 edges, `L4_ready=false`, `global_physical_completion=null`을 유지한다. 이번 진단·포장 보조코드 준비는 원래 DAG 노드를 추가하거나 완료 상태를 바꾸지 않는다.

현재 사용자 지시가 새로 정량화된 승인 전 포장 재실행을 금지하므로, 새 보조코드는 **정적으로 준비한 미실행 코드**다. 현재 Python/C++ 실행 능력을 사용할 수 없다고 판정하지 않았다. 이전 체크포인트의 `PYTHON_PASS`는 당시 실행 기록이다.

## 먼저 읽을 고정 근거

저장소: `cosmosapjw-quantum/rei_bianchi`  
브랜치: `research/rei-causal-prefix-consumer-20261027`  
재개 시 확인한 HEAD: `57d5946832a8722848de4a063d5a2702693cdc74`  
Draft PR: #240

모든 아래 상대 경로의 기준은
`research/rei_expanded_event_consumer/bass_atomic_storage_consumer_20261027/`이다.

1. `delivery/APPROVED_FINAL_ZIP_ATTEMPT_20261028.json`
2. `handoff/FINAL_ZIP_RESOURCE_STOP_20261028.md`
3. `delivery/FINAL_ZIP_COST_DIAGNOSIS_20261028.json`
4. 이번에 추가한 `delivery/package_final_reuse_once_20261028.py`와 `delivery/measure_final_once_20261028.py`

첫 두 문서와 기존 `delivery/package_final_once.py`는 역사적 원본으로 보존한다. 새 helper는 후속 전달 코드이며 원래 116개 과학 payload에 넣지 않는다.

## 비용 진단

기존 복원과 포장은 `os.execv`로 이어진 같은 프로세스였다. Linux의 `RUSAGE_SELF` 계측은 exec 전 CPU 사용량을 보존한다. 기존 helper의 첫 `check()`는 누계가 0.48 CPU s 이상이면 중단했으며, 보호 타이머는 복원 뒤에 설치됐다. 실제 `BUDGET_STOP`은 ZIP 작성 이전에 발생했다.

보존된 1.931249 CPU s는 복원, exec 이후 Python 시작과 모듈 로딩, 진입 검사와 실패 처리 일부를 합한 **최종 직렬화 전 누계**다. 복원 단계만의 독립 측정값은 없다. ZIP 작성·CRC·전체 ZIP SHA-256 단계는 실행되지 않았으므로 그 작업의 완료 비용은 미측정이다.

`46.331767494 + 1.931249 = 48.263016494 CPU s`

누적값은 측정·예약 하한이다. cap 47 대비 초과 하한은 1.263016494 CPU s이고, 0.65 예약 대비 초과 하한은 1.281249 CPU s다. 외부 표시 user 1.36, system 0.56, wall 1.55, exit 1도 원문 그대로 보존한다. 측정 범위와 표시 정밀도의 불일치 원인을 이번 자료만으로 확정하지 않는다. 과거와 이번 진단에서 미계측인 비용은 `UNKNOWN_NOT_ZERO`이며 리셋·이관하지 않는다.

첫 검사보다 뒤에 `result_path`가 할당되어 실패 기록 파일이 생기지 않은 점, CRC 반환값을 확인하기 전에 성공 횟수가 증가하던 점은 새 helper에서만 교정한다. 과학 코드·결과는 수정하지 않는다.

## 복원본과 기존 백업 재사용

로컬 디렉터리 `/workspace/scratch/52cc495a5f0a/rei_bass_storage_unit`가 현재 존재한다. 파일 경로 목록은 147개이고 예전 단계 ZIP과 후속 문서가 포함되어 있다. **디렉터리 전체를 재귀 압축하지 말고 고정 manifest의 116개만 선택한다.**

로컬 `delivery/PENDING_SOURCE_ZIP_INPUT.json`은 메타데이터상 4,699,240 bytes다. 이번 진단은 116개 원본의 전체 byte/hash 재검사를 수행하지 않았다. 다음 승인된 단일 실행이 원본 identity를 확인한다. 누락·불일치가 나오면 종료하며, 이번 재사용 작업 안에서 재복원하거나 백업을 재생성하지 않는다.

고정 입력:

- Source pin: `d9a1c4c4252f1b7b4c868fb2cb817a879f503cd5`
- Payload: 116 original files
- Source JSON bytes: 4,699,240
- Source JSON Git blob: `713ac1d7c89b53028f6d63b3051c774f5a621546`
- Source JSON SHA-256: `d77ea863ad2730f6ef0be27a3f3a93c8b5c864f3d863b4b1b5950fd61a6ef63e`

기존 완료 ACK는 `delivery/FULL_SOURCE_TEXT_RECEIPT.json`에서 재사용하고, 이번에는 두 provider의 동일 ID와 4,699,240-byte 메타데이터를 확인했다.

- Drive: `1M2W7SEk-rqwJTvOr9PbLc6jMGNXpBPEu`
- Dropbox: `id:BSpOijBcT10AAAAAAEDIIA`
- Dropbox revision: `65ed3da7ee48f0af03d47`
- Dropbox path: `/bianchi/research_backups/rei_bianchi/REI_BASS_STORAGE_SOURCE_TEXT_20261027_d9a1c4c4252f.json`

새 다운로드·복원·기존 source ZIP 생성·단계 백업 재생성은 수행하지 않았다. 현재 remote 원본의 SHA를 새로 계산했다는 주장은 하지 않는다.

## 보조코드 검토 상태

새 worker와 supervisor는 별도 구현자가 작성했고, 독립 검토자가 소스를 읽었다. supervisor의 SIGXCPU 처리 누락과 큰 내부 CPU 관측값의 기록 순서 문제 두 항목을 한 번의 제한된 수정으로 교정했다. 마지막 정적 확인에서 해당 차단 지적은 0개다. 최초 CPU 신호 뒤의 cleanup은 중복 인터럽트를 억제하되 갱신하지 않는 1초 wall 제한을 적용하고, 실제 초과 가능성을 기록한다. 원래 worker·supervisor의 실행 성공을 확인한 것은 아니며 문법 검사·테스트·포장 실행은 모두 NOT_RUN이다.

## 다음 단일 실행의 제안 — 승인되지 않음

**Presentation 누적 known/reserved 상한 60 CPU s, 이번 단일 시도 예약 8 CPU s**를 제안한다. 이는 실측 완료시간 예측이 아니라 한 번의 시도를 위한 허용 소비량이다. 기존 하한과 예약의 합은 56.263016494 CPU s이고 nominal 여유는 3.736983506 CPU s다. 미계측 비용은 그대로 남는다.

범위는 기존 cache identity 검사, ZIP_STORED 작성, CRC 전체 검사 1회, ZIP 전체 SHA-256 1회, 종료 계측·기록이다. worker 작업 중단선은 CPU 5.5 s, 고정 최종 기록 deadline은 6.0 s이며 제어·기록에는 2.0 s를 예약한다. 복원은 이번 범위에서 제외한다. 단일 worker 시도 1회, 자동 재시도 0회다.

worker의 실제 종료 후 `wait4`로 전체 user/system CPU를 취득하고 단계별 누계 차이를 함께 남긴다. 제어 프로세스의 직렬화 전 CPU와 나머지 기록 예약은 별도 필드로 관리한다. 실제 실행 때에는 외부에서 전체 supervisor 명령을 계측한 종료 기록도 남긴다. 직렬화 전 내부 숫자를 최종 전체 CPU라고 표시하지 않는다. 신호·주기적 검사는 엄밀한 무초과 상한 보장이 아니므로 실제 초과가 관측되면 그대로 과금·보존하고 중단한다.

출력은 새 쓰기 가능한 경로에 create-only로 만든다. 원본 cache에 쓰지 않는다. 최종 ZIP에는 원본 116개와 내부 `SOURCE_MANIFEST.json` 1개, 총 117개 entry가 들어가야 한다. 성공한 ZIP은 Drive와 Dropbox에 각각 업로드하고 양쪽 완료 ACK와 크기·object identity를 확인한 뒤 전달 완료로 판정한다. ZIP 성공과 provider ACK 성공은 별도 상태다.

아래 명령은 **승인 뒤에만 실행할 준비 명령**이다. 출력 디렉터리는 이미 존재하는 현재 writable 경로를 사용하고 모든 출력 이름은 새 이름이어야 한다. 이 실행 봉투의 stdout/stderr·종료코드와 외부 time 결과를 함께 보존한다. 외부 계측이 worker를 포함한 집계이면 worker CPU를 다시 더하지 않는다.

```bash
/usr/bin/time \
  -f '{"user_cpu_display_s":"%U","system_cpu_display_s":"%S","wall_display_s":"%e","exit":"%x"}' \
  -o /workspace/scratch/16129359d31f/REI_BASS_FINAL_REUSE_OUTER_20261028.json \
  python3 /workspace/scratch/16129359d31f/delivery_repair/measure_final_once_20261028.py \
  --explicit-approved-launch --approved-absolute-cap 60 --approved-reservation 8 \
  --output-root /workspace/scratch/16129359d31f \
  --manifest /workspace/scratch/52cc495a5f0a/rei_bass_storage_unit/delivery/PENDING_SOURCE_ZIP_INPUT.json \
  /workspace/scratch/16129359d31f/REI_BASS_ATOMIC_STORAGE_SOURCE_20261027_d9a1c4c4252f_REUSE.zip \
  /workspace/scratch/16129359d31f/REI_BASS_FINAL_REUSE_WORKER_20261028.json \
  /workspace/scratch/16129359d31f/REI_BASS_FINAL_REUSE_SUPERVISOR_20261028.json
```

위 외부 time 로그 경로도 실행 전에 존재하지 않는지 확인한다. 새 세션에서는 실제 helper 위치와 writable 출력 경로만 조정하며, 입력 cache가 없어졌으면 자동 복원하지 않는다. time의 원문 출력 정밀도를 보존하고 microsecond 정밀도 전체계측으로 승격하지 않는다. 승인 플래그 자체가 사용자 승인을 대신하지 않는다. 이 문서만으로 실행을 승인하지 않는다.

## 다음 스레드에 복사할 지시

```text
$physmath-research-loop로 cosmosapjw-quantum/rei_bianchi의
BASS atomic-storage final ZIP 전달 작업만 이어가라.

branch research/rei-causal-prefix-consumer-20261027, Draft PR #240.
먼저 현재 HEAD와 이번 diagnostic commit을 확인하고 다음 경로를 읽어라:
research/rei_expanded_event_consumer/bass_atomic_storage_consumer_20261027/
  delivery/APPROVED_FINAL_ZIP_ATTEMPT_20261028.json
  handoff/FINAL_ZIP_RESOURCE_STOP_20261028.md
  delivery/FINAL_ZIP_COST_DIAGNOSIS_20261028.json
  handoff/FINAL_ZIP_REUSE_HANDOFF_20261028.md

과학 R/C20/20, 작업 DAG33/88·중앙28/88, L4_ready=false,
global_physical_completion=null 및 PASS_SCOPED 판정은 그대로 유지한다.
실패 분류 runtime_environment/resource_budget을 유지한다.

이월 누적 측정·예약 하한48.263016494 CPU s와 UNKNOWN_NOT_ZERO를 보존한다.
새 제안은 presentation상한60/단일예약8 CPU s이며 아직 승인되지 않았다.
현재 대화에 명시적 새 승인이 없으면 포장·복원·테스트를 실행하지 않는다.

기존 cache /workspace/scratch/52cc495a5f0a/rei_bass_storage_unit를
읽기 전용으로 재사용한다. metadata상147개 파일 중 manifest116개만 선택한다.
sourcepin d9a1c4c4252f1b7b4c868fb2cb817a879f503cd5,
JSON4699240bytes,
SHA256 d77ea863ad2730f6ef0be27a3f3a93c8b5c864f3d863b4b1b5950fd61a6ef63e.
cache가 없거나 identity가 다르면 자동복원하지 말고 종료한다.

승인 뒤 새 reuse worker와 supervisor로 한 번만 실행한다.
기존 source ZIP·단계 백업은 재생성하지 않는다.
전체CPU 실제 종료계측, 단계별 비용,116원본,ZIP117entries,
CRC1회와전체ZIP SHA2561회,Drive·Dropbox완료ACK를 보존한다.
과학·기존테스트·IVP/provider rerun0,자동재시도0.
```

참고 원전: [Linux getrusage](https://man7.org/linux/man-pages/man2/getrusage.2.html), [Linux setitimer](https://man7.org/linux/man-pages/man2/setitimer.2.html).
