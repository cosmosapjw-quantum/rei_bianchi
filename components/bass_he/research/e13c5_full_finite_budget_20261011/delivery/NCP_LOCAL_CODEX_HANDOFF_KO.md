# 최종 백업 시작점 — 추가 첨부 없이 사용

기존 백업에서 아래 recovery kit를 찾는다. Kit 자체에 전체 실행 prompt, 두 조각의 실제 백업 위치, manifest, 복구 코드가 있다. 이미 완전한 NCP_READY ZIP을 내려받았다면 해당 ZIP의 identity를 확인하고 바로 core를 복구하면 된다.

- Recovery kit: `BASS_HE_E13C5_NCP_RECOVERY_KIT_20261011_sha_e01efec669d9.zip`
- bytes: `20753`
- SHA-256: `e01efec669d9db09a61479635b94396113462d99fe61fdef7f7b339c2495487e`
- Drive: https://drive.google.com/file/d/1EgHZ6MquyNrai63kqFrOB_mC24POjHKV/view?usp=drivesdk
- Drive file ID: `1EgHZ6MquyNrai63kqFrOB_mC24POjHKV`
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C5_NCP_RECOVERY_KIT_20261011_sha_e01efec669d9.zip`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4CQQ`
- Git PR21: https://github.com/cosmosapjw-quantum/BASS_HE/pull/21

두 백업에는 각각 전송 조각 2개와 recovery kit 1개가 실제 업로드되어 있다. 조각과 kit의 업로드 ACK 및 provider 메타데이터 크기를 확인했다. 원격 재다운로드 복구와 실제 NCP 호스트 실행은 아직 하지 않았다.

---

# NCP local Codex handoff — 백업만으로 복구하고 실행

## 0. 추가 사용자 첨부 없이 전달본 복구

이번 작업의 완전한 논리 전달본은 다음 ZIP이다.

- 파일명: `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip`
- bytes: `124466102`
- SHA-256: `5741b06b9a6199d593bb52f833a07cd834a67c41d958d589d70840b7144a0c49`

원격 업로드의 100 MiB 제한 때문에 기존 Drive와 Dropbox에 원본 ZIP의 byte-exact 두 전송 조각과 이 작은 recovery kit를 저장했다. Scientific core와 원본 NCP_READY ZIP은 바꾸지 않았다. 이 kit에는 전체 prompt, 각 조각의 실제 백업 ID/경로, part manifest, 재결합 코드와 로컬 복구 영수증이 들어 있다. 입력 파일을 사용자에게 다시 첨부해 달라고 요청하지 말고 다음 절차로 복구한다.

이미 위 완전한 ZIP이 로컬에 있으면 실제 파일 크기/SHA를 확인한 뒤 재결합을 생략한다. 없다면 기존에 인증된 백업 동기화 또는 연결 경로로 아래 두 조각을 같은 새 `PARTS_DIR`에 확보한다. Drive 또는 Dropbox 어느 한쪽의 완전한 세트면 충분하다. 접근 인증이 실제로 막히면 그 경계를 기록하며 성공을 꾸미지 않는다.

### Part 001

- 파일명: `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part001`
- bytes: `83886080`
- SHA-256: `88b6985e1d649d6afc3dfd20480bd7feffbdba036879642474228bd56d4f0cbe`
- Drive: https://drive.google.com/file/d/1e9zXnycX4fjqjoq5tP0rB3sTeZNms2CV/view?usp=drivesdk
- Drive file ID: `1e9zXnycX4fjqjoq5tP0rB3sTeZNms2CV`
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part001`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4CPw`
### Part 002

- 파일명: `BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002`
- bytes: `40580022`
- SHA-256: `34b7b41f19c42cb19da7a001daf7ccc48ae527dbaa101b613fb90b7fa20bedbb`
- Drive: https://drive.google.com/file/d/1grkS_qfqiBr2VoRKIdyM-9BysvtVy0Jq/view?usp=drivesdk
- Drive file ID: `1grkS_qfqiBr2VoRKIdyM-9BysvtVy0Jq`
- Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip.part002`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4CQA`


실제 복구 kit 위치를 `RECOVERY_DIR`, 조각이 있는 경로를 `PARTS_DIR`로 정한다. 원본 ZIP의 새 출력은 `PARTS_DIR` 밖에 둔다. 기존 파일을 덮어쓰지 않는다.

```bash
RECOVERY_DIR="/actual/recovery/BASS_HE_E13C5_NCP_RECOVERY_20261011"
PARTS_DIR="/actual/backup_download/parts"
RESTORED_ZIP="/actual/fresh_restore/BASS_HE_E13C5_FULL_FINITE_NCP_READY_20261011_sha_5741b06b9a61.zip"

python3 -B "$RECOVERY_DIR/restore_ncp_ready.py"   --manifest "$RECOVERY_DIR/TRANSPORT_PARTS.json"   --parts-dir "$PARTS_DIR"   --output "$RESTORED_ZIP"
```

`restore_ncp_ready.py`의 SHA는 `3b947e4537da4f24eaf3a40a7ebf9051cd560e58f813928425f6a4a69599abbb`, `TRANSPORT_PARTS.json`의 SHA는 `d20e2146447bd10748066a03573fc439be6127c5aa89627e4ff309a9f181d8a6`다. Linux/표준 라이브러리만 쓰며 각 조각과 완성된 실제 파일을 해시 검사한다. 로컬 전달본 생성 당시 한 번 재결합하여 위 원본 ZIP identity와 완전 일치를 확인했다. 이는 NCP에서의 실행 또는 원격 백업 재다운로드 검증 결과가 아니다.

수용되는 복구 상태는 `PASS_LOCAL_TRANSPORT_RESTORE`다. 완성된 ZIP을 새 staging에 풀고, 그 안의 `CORE_IDENTITY.json`에 고정된 scientific core ZIP을 실제 디스크에서 해시 확인한 뒤 푼다. Core ZIP은 124,456,592 bytes, SHA `1889e62086f1d5ea7cef2ebdfcc3bb734a12065b6c06f973080d89177d5358ac`다. Core root는 `BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1`이다.

아래는 봉인된 core에 들어 있는 전체 canonical 실행 지시다. 전송 복구 후 그대로 적용한다. NCP 실행 전에 현재 core의 계약과 lock을 읽고, 과거 dependency archive의 handoff와 구분한다.

---

# NCP local Codex handoff — BASS_HE E13C5 full finite budget

아래 지시를 NCP의 local Codex에서 실행한다. 이 문서와 모든 입력은 하나의 NCP_READY 백업본에 동봉된다.

## 목표와 현재 상태

BASS_HE의 `HE_E13C5_FULL_FINITE_BUDGET_AND_COMPLEMENT01`을 기록된 NCP 호스트에서 **저장 결과 exact postprocessing 1회**로 재현하라.

PR20은 OFF/KF/GM의 2,440개 finite captured node/mode, 총 7,320경로·14,652segment를 이미 처리했다. OFF 0·700의 N512 결과도 완료되어 있다. 이번 실행은 두 원 scientific archive를 복구하고 전체/selected4/complement2436/두 항 hybrid 예산과 순위를 정확하게 재현한다.

현재 Chat primary 결과는 전체 photon 폭 감소 1.430233307 ppm, 종별 합 열 1.059316287 ppm이다. 이번 handoff에서는 coefficient, ODE, native, gas, full-first2 또는 N512 solver를 실행하지 않는다. 후속 후보 OFF 101·102·410·413은 다음 연구 계약에 남겨진 후보이며 이 실행에 포함되지 않는다.

## 1. 한 파일로 복구

외부 안내에 적힌 NCP_READY archive의 이름·크기·SHA-256을 기존 백업 루트에서 찾아 확인하라. 로컬에 없으면 외부 안내의 정확한 Drive 파일 또는 Dropbox 경로에서 그 한 파일을 받는다. 추가 입력 파일을 사용자에게 요청하지 않는다.

기존 결과나 작업 디렉터리를 덮어쓰지 말고 새 staging 디렉터리에 외부 archive를 푼다. 외부 archive의 `00_START_HERE_KO.md`와 `CORE_IDENTITY.json`에 고정된 내부 scientific ZIP의 크기·SHA를 확인한 후 같은 staging 아래 푼다.

완성된 패키지 루트 이름은 다음과 같다.

`BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1`

동봉한 과거 archive 안의 NCP 문서는 과거 단계의 기록이다. 이번 실행의 현재 계약은 위 패키지 루트의 `NCP_EXECUTION_CONTRACT.json`과 `RUN_LOCK.json`이다.

이미 같은 최종 source/lock/semantic projection으로 성공한 NCP receipt가 있다면 해당 receipt와 실제 결과 identity를 확인하여 반환하고 중복 실행하지 않는다. 그 외에는 아래 단일 실행을 진행한다.

## 2. 실행 전 고정값

- Linux, CPython 3.12.x, 표준 라이브러리만 사용.
- serial arithmetic worker 1개와 기다리는 parent; 병렬 worker/MPI 0.
- child 주소 공간 1 GiB, 내부 wall 300초, outer child 330초.
- 여유 disk 최소 2 GiB, 관측된 가용 memory 최소 1.2 GiB.
- 새 출력 디렉터리는 존재하지 않아야 하며 immutable package 밖이어야 한다.
- `RUN_LOCK.json` SHA: `cdfda6cd49eeb38518b2a41156a087f744e0985e0384bf628ca8b893dbec5b3a`.
- `code/ncp_budget_continue.py` SHA: `ab1b07c45136b77bf492148fa3e7560d2c2f02cb5650a6d0de5fc4fe00244a79`.
- `code/full_finite_budget.py` SHA: `a3f854bc3c175cdaed36c7f475ff594c59056855ea5236c2eba844570c2861ee`.
- `SCIENTIFIC_CONTRACT.json` SHA: `d0d96f4f729b32ddc1ff4465f3776dc5d66f811440a4313f304f549dae14d846`.

프로젝트의 AGENTS.md와 현재 실행 계약을 읽고 실제 환경을 기록하라. Source, P/N, tolerance, pinned input 또는 lock을 바꾸지 않는다. 시작 전에는 실행계획과 resource preflight를, 실행 뒤에는 실제 exit/wall/CPU/RSS와 source identity를 남긴다.

## 3. 한 번 실행

실제 복구된 절대경로로 `PACKAGE_DIR`과 `RUN_DIR`을 정한다. 아래의 두 경로 문자열은 local Codex가 실제 경로로 치환한다. `RUN_DIR`에는 기존 디렉터리를 사용하지 않는다.

```bash
PACKAGE_DIR="/actual/staging/BASS_HE_E13C5_FULL_FINITE_BUDGET_20261011_v1"
RUN_DIR="/actual/runs/BASS_HE_E13C5_NCP_BUDGET_EXEC01"

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
timeout --signal=TERM --kill-after=10s 390s \
python3 -B "$PACKAGE_DIR/code/ncp_budget_continue.py" \
  --package "$PACKAGE_DIR" \
  --out "$RUN_DIR" \
  --execute \
  --host-label NCP
```

실행기는 두 archive의 고정 SHA, 46개 PR20 member와 852개 PR19 member, 쓰기·fsync·atomic rename 뒤 persisted SHA, 실제 9개 입력의 실행 전후 identity를 검사한다. 한 child가 `full_finite_budget.py`를 실행한다. 기존 full-first2.py, cover.py, N512 solver 및 과거 ncp_continue.py를 별도 호출하지 않는다.

`--execute`를 생략한 `VERIFY_ONLY_READY`는 입력 확인만 수행한 상태다. 이를 실제 재현 완료로 보고하지 않는다.

## 4. 수용 기준

정상 종료에는 다음이 모두 필요하다.

- outer receipt: `PASS_SCOPED_SAVED_FULL_FINITE_BUDGET_PARITY`.
- `budget_invocations=1`; `physics_invocations=0`, `full_first2_invocations=0`, `N512_invocations=0`.
- fresh child: `PASS_SCOPED_SAVED_FULL_FINITE_BUDGET`, 경로 7,320/segment 14,652, 실패 0.
- 정확한 의미 projection SHA:
  `770a11a13a73ff3305ab62eb27a7abb0ca99860ffc56fc6384e6aead68d8e7c3`.
- 압축을 푼 순위 CSV: **51,718,536 bytes**,
  SHA `ce053b71a6b9aeb8bc5c8d1d9e9be3911c4a7aeba60779151a8af9d5bad3f8f4`.
- Fresh gzip의 bytes/SHA가 fresh projection과 일치.
- Fresh RESULTS가 projection의 **모든 key를 실제로 포함**하고 각 값과 일치. null-valued key의 누락도 실패.
- Source·contract·입력·실제 RUN_LOCK bytes가 실행 전후 동일.

원 Chat projection은 3,401,613 bytes,
SHA `0dba21fa1d7bfc8dc5894630efef0864c73e69a7f2ce1fe8a3712a940a2e3618`,
canonical object SHA `e70107da8072cafec33b650db258391825662eabdd2798b90b86a01bca9ddb53`다.

원 projection의 gzip 전송 bytes/SHA 두 필드만 semantic 비교에서 제외한다. 다른 zlib의 동일 CSV 압축 표현은 허용하지만 모든 과학값·source·input·contract·분할·부호·순위는 정확히 같아야 한다. Raw projection byte parity는 별도로 기록하며, 달랐다면 같았다고 표현하지 않는다.

실패 시 자동 재시도하거나 source/P/N/tolerance를 고치지 않는다. START, stdout/stderr, checkpoint, failure, partial output과 WORK를 보존하고 실제 최초 실패와 필요한 최소 조건을 보고하라.

## 5. 반환과 closeout

성공 또는 실패의 실제 `RUN_RECEIPT.json`과 fresh child 결과를 봉인한 반환 archive를 만들고 bytes/SHA-256을 기록하라. 최소 포함 항목:

- outer START/RUN_RECEIPT/CHECKPOINT, stdout/stderr.
- BUDGET의 START/RESULTS/NUMERICAL_PROJECTION/NUMERICAL_IDENTITY/CONTROLS/RESOURCE_RECEIPT.
- BUDGET의 WIDTH_RANKINGS.csv.gz.
- 실패가 있었다면 원 failure와 partial evidence.

WORK의 원 복구 입력은 이미 NCP_READY 안에 있으므로 정상 반환에서는 그대로 재첨부할 필요가 없다. 실패의 원인을 입증하는 입력이면 해당 부분을 추가 보존한다.

기존 승인된 백업 목적지에 반환본을 새 이름으로 올리고 provider ACK와 파일 name/path/size/identity를 기록한다. 실제 수신·실행 ACK, 업로드 확인, 복구 확인을 구별하라. Git 기록이 가능하면 이 task의 새 evidence 경로만 expected-head/non-force로 게시하고 자동 merge하지 않는다.

최종 보고에는 실제 실행 명령, hostname/OS/Python/CPU affinity, exit/wall/CPU/RSS, invocation 수, source/lock/입력 SHA, normalized projection와 CSV parity, 반환 archive identity를 넣는다. `--host-label NCP`는 operator 선언이다. Cloud provider 증거가 별도로 없으면 provider attestation을 만들어 쓰지 않는다.

Full finite captured cover는 상속 완료다. Continuum quadrature/시간 수렴, 새 gas, 실제 photon·heat·recoil, physical/global/production 및 receiver adoption을 이 재현으로 승인하지 않는다.

