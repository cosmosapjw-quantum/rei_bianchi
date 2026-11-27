# NCP local Codex 종합 실행 인계 | BASS_HE RCT03E8 → E9 이후의 heavy-runtime 작업

ROLE=NCP_LOCAL_CODEX_BASS_HE_BOUNDED_HEAVY_EXECUTOR
PROJECT=cosmosapjw-quantum/BASS_HE
RESEARCH_BRANCH=research/shared-c64-crossrepo-20260928
TASK_FAMILY=HE-RCT03E9_OWNER_NATIVE_OUTPUT_IDENTITY_AND_SOURCE_TRANSFER
REFERENCE_DATE=2026-10-08 (KST)
DEFAULT_SCIENCE=HOLD_UNTIL_SOURCE_AND_EXECUTION_GATES
RESPONSE_LANGUAGE=KOREAN

## 0. 목적과 역할 분담

너는 NAVER Cloud Platform(NCP)의 실제 실행 호스트에서 동작하는 local Codex다. ChatGPT 연구 스레드가 완료한 유도·코드·시험·정확한 입력계약을 다시 설계하는 것이 주임무가 아니다. 이미 구현된 결과를 cloud-first로 복구하고, 호스트/빌드/ABI 적합성을 검사한 뒤, 명시적으로 한정한 **native 무거운 계산만 실제 실행**하고, 원본·실패·출력 identity를 보존하며 GitHub 및 Google Drive+Dropbox에 영속적으로 전달하라.

이 인계가 지정한 BASS_HE 실행단위 전체를 DAG 순서대로 자율적으로 진행하라. 매 단계 불필요한 질문을 하지 마라. 다만 현재 소스가 필요한 입력·명확한 과학 정의·기존 authorization을 제공하지 않는 계산은 `PREPARED_NOT_AUTHORIZED` 또는 구체적인 `BLOCKED_*` 상태로 남기고, 가능하고 독립적인 작업은 완료하라. 사용자의 "모두 진행"을 **다른 세 owner의 science lane, 새 production default, 무한 기간·전수 campaign의 일괄 실행승인**으로 해석하지 마라.

원자 소스·가스 적분기·Thomson/BASS transport·수송 알고리즘의 substantive redesign은 본 스레드 소유다. NCP Codex는 source에 결속된 최소 입력/출력 adapter, native 빌드·smoke, 승인된 bounded campaign, 검증·백업을 우선한다. 미완성 물리식을 추측해 채우거나 성공한 동일 reference suite를 반복하지 마라.

## 1. immutable source authority 및 cloud-first 수신

### 1.1 최신 ref는 반드시 재조회

- BASS_HE branch `research/shared-c64-crossrepo-20260928`의 마지막 관측 HEAD: `558a10c64ace68bd2e7bd59f7c01cd659bc56005` (E8 Git 전달 영수증 포함). 이것은 옛 상태로 reset하라는 지시가 아니다. `git fetch` 후 실제 remote HEAD·commit·tree를 기록하고 successor가 있으면 우선 읽어라.
- E8 연구 경로: `docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/runs/HE-RCT03E8-PHOTO-SOURCE_20261008/`. `README_KO.md`, `NEXT_STEP_KO.md`, `RETURN.json`, `CLAIM_CONTRACT.json`, `INPUT_PIN.json`, `CROSS_THREAD_INTAKE.json`, `DELIVERY_RECEIPT.json`을 먼저 읽어라.
- 실제 receiver owner: `cosmosapjw-quantum/rei_bianchi`, branch `forward/rem-hhe-igm-20261006`, 마지막 확인 HEAD `39c39eab1cc2f1a215723680accc123e67ef13b6`. `research/transport_20261007/short-hhe-midpoint`의 owner와 실험 전용 staged integration을 구별하라. PR84/PR85를 포함한 진행 상황을 live 조회하고 예약된 owner branch에는 무단 push·merge하지 마라.
- owner의 원 `output.rs` 41열, 중간 staged E3/RCT03D 프로브의 40열, 실제 짧은 25행, E7/E8의 385행은 **자동 호환되지 않는다**. 이 차이를 처음부터 계약에 등록하라.

### 1.2 꼭 필요한 immutable ZIP (같은 SHA를 가진 파일은 한 번만 다운로드)

1. **E8 필수** `BASS_HE_RCT03E8_PHOTO_SOURCE_20261008_v1.zip` 1,260,738 bytes; SHA256 `0fbe599f9e1cd90c0b2363c10fb1bafca5cc6e63d6397db6dd66d75835d2680f`.
   Drive object `1PGq6TC5jK81wJDFcxtJFt7Fad_BOjxQE`; Dropbox `id:BSpOijBcT10AAAAAAD3cGw`.
   안의 `code/electron_transfer.py`, `code/consumer_rates.py`, `tests/test_source_transfer.py`, `inputs/OWNER_ORIGINAL_SHORT_OFF.csv`, `data/SOURCE_LOCK.json`, `REPORT_KO.md`, `NEXT_STEP_KO.md`, `MANIFEST.json`이 기준이다.
2. **E7 필수** `BASS_HE_RCT03E7_CONSUMER_ADOPTION_20261008_v1.zip` 879,563 bytes; SHA256 `020a58ebc4c57a89d973fde66fd1cd82cd5bc3e3f3bccf9f8dce8856cb8bfe2a`; Drive `1pCLtxukkwzMsEutFFj8UBngWHRvYHPI6`; Dropbox `id:BSpOijBcT10AAAAAAD3cCQ`.
   E7 `SOURCE_LOCK.json` SHA256 `1f6c1fbbdf487d64dae65fe690c92b9237d5b0cb6416d7d267a299288acd9b4b`; E7의 3모드 ×385행 source와 원본 `READY.json`을 변조하지 마라.
3. **native owner/staged 의존성이 없을 때만 추가 수신** `BASS_HE_RCT03E6_ALL_EPOCH_20261008_v1.zip` 16,698,784 bytes; SHA256 `56b743e220269dc3ca6b031b9009f67fe4a90ca2cdc8490c810dbea5997d045b`; Drive `14GgVb6Q3DaVQaDBLhNNCo8BJK7F1ZWDe`; Dropbox `id:BSpOijBcT10AAAAAAD3YMg`. 이 ZIP의 `native/`는 E6 출력기이고, `parent/base/staged/`는 실험용 결합 solver이며, `parent/base/owner/short-hhe-midpoint/`는 원 owner의 snapshot이다. 절대로 서로를 production owner로 바꿔 부르지 마라.

Drive canonical parent: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`.
Dropbox canonical parent: `/BASS_DERIVATION_DOSSIERS_20260912/`.

첫 검색은 `git`, 현재 호스트의 `rclone listremotes`, 기존 sync/mount, 설치된 CLI/API, content-addressed local cache 순서다. 과거 `gdrv:`/`dbx:` remote 이름을 현재 사실로 가정하지 않는다. 모든 provider에서 ID/name/size metadata를 확인할 수 있으면 확인하되, 같은 SHA의 실제 bytes는 local cache가 없을 때 provider 한 곳에서만 다운로드한다. 기본 provider 실패·SHA mismatch일 때만 다른 provider를 사용한다. **네트워크·권한 장애가 있더라도 이미 받아 verified인 bytes를 다시 가져오지 말라.** 사용자에게 파일을 수동 업로드해 달라고 먼저 요구하지 말고 탐색 실패의 구체적인 receipt를 남겨라.

파일을 SHA256·byte length·ZIP CRC·manifest/payload SHA로 검증한 뒤 새 run namespace에 read-only로 복원하라. ZIP 루트의 상대경로를 유지하고 다른 archive를 덮어써 병합하지 마라. E6/E7/E8의 동일한 이름·서로 다른 SHA artifact는 반드시 독립 객체로 취급한다. 원 PDF/source PDF를 공개 Git에 재배포하지 마라.

## 2. NCP 호스트·자원·실행 충돌 inventory [H0]

NCP C64-g3는 과거 64 vCPU/128 GiB급으로 알려졌지만 **실행 가능한 CPU·메모리로 추정하지 말라**. 실제 호스트에서 다음을 read-only 관측한다: `date -Is`, hostname, uname, `/etc/os-release`, `lscpu`, NUMA, `nproc`, CPU affinity, cgroup ancestry의 `cpu.max`·`cpuset.cpus.effective`·`memory.max`·`memory.current`, `free -h`, disk free/inodes, compiler/`rustc`/`cargo`/Python/BLAS/OpenMPI version, `ulimit`, 현재 해당 checkout의 `git status`, 실행 중 동일 project 프로세스 및 예약된 job. credential/환경 전체 덤프 금지.

실행 중 같은 run의 PID·lock·checkpoint가 있으면 무단 kill·중복 launch하지 않는다. 오래된 워크스페이스가 dirty면 reset/clean/stash/rebase로 치우지 말고 새 디렉터리에 worktree/checkout을 마련한다. 시작 시 `RECOVERY_INVENTORY.json`에 path/tree/size/mtime/SHA, subprocess/PID, git ref, lock, provenance, 완료 단계·in-flight/UNKNOWN을 적는다. transcript-only 완료는 증거가 아니다.

Run ID는 UTC/KST timestamp와 입력 hash를 결합한 불변 고유명으로 만들며, 완료/실패 디렉터리와 같은 이름으로 재시도하거나 overwrite하지 마라. 각 단계에서 입력·출력·code·compiler identity와 process의 실제 exit를 기록하라. 시간제한 중단 시 모르는 종료코드는 `UNKNOWN`으로 남겨라.

성능실험은 1×(정확한 baseline work), 필요하면 2 또는 3개의 **독립 처방별 process**를 고려하되 실제 affinity/quota/RSS를 먼저 측정한다. 무작정 64 MPI rank나 64개 Rust 프로세스를 띄우지 말라. 20% 이상 메모리 여유를 확보하고, oversubscription(OMP/BLAS/MKL/MPI 혼합) 금지. 본 native Rust/IGM 작업을 근거 없이 Fortran으로 재작성하지 말라. 다른 BASS_HE atomic lane의 Fortran/OpenMP/SIMD/OpenMPI 정책은 그 레인에서만 source/parity 확인 뒤 사용한다.

절대 `-Ofast`, `fast-math`, `-ffast-math`, 재결합 float reduction, 숨은 mixed precision, 캐시 키 반올림, 자동 grid/tolerance downgrade를 사용하지 않는다. 원 manifest가 요구하는 Rust `1.94.1`과 Cargo lock을 고정한다. 과거 toolchain archive SHA256 `294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40`, **GPG_AUTHENTICITY=NOT_VERIFIED**이다. 실제 설치/컴파일/연계 사실만 PASS로 보고하라. 기존 toolchain이 없으면 verified archive 또는 승인된 offline vendor를 사용한다. 인터넷에서 제약 없는 최신 toolchain/라이브러리로 바꿔 실행했다고 동일 입력으로 승격하지 않는다.

## 3. 공통 유효범위와 기존 통과 범위 [H1]

원 E7/E8 제조문제: `z=12` FLRW, `T0=2000 K`, 최초 `(xHII,yHeII,zHeIII)=(0.1,0.05,0.9)`, 초기 photon 0, source `1e-15 photons/(H s)`, energy `[13.7,100] eV`, `Delta ln a=2e-4`, `N=384`, P512, Gauss4, ON의 명시적 RCT mean `35 eV`. 이는 **실제 원자 광자 평균 모멘트가 아니라 conditional escape closure**이다. baseline RCT OFF이고 ON은 별도 opt-in이다.

기존 E6: endpoint 관측기의 N384 전체385시각, 시간 N192 공통193시각, panel256/512, Gauss2/4의 선언된 finite rate allowance `absolute=1e-22 s^-1`, `relative=1e-6`에 대해 9개 rate target PASS, worst GM HI `0.9645971372`; 이는 참오차 bound/물리모형 정확도는 아니다. E7: Python consumer 3×385행, 22 tests, selected readout 기본 DISABLED. E8: 16 Python tests, 1,155행 source, 770 paired rows, 3,080 정확 대칭 identity + 2,310 종/전자 identity 및 75 Decimal controls PASS. 이미 종료된 E4/E5/E6/E7/E8 science·old atom/CR/HH/REI 검증을 새 이름으로 재실행하지 마라.

E8 광전자 생성률 per H per proper second의 정의:

`S_photo_e = (1-x_HII)*Gamma_HI + (nHe/nH)*[(1-y_HeII-z_HeIII)*Gamma_HeI + y_HeII*Gamma_HeII]`.

`Gamma_i`는 per absorber `s^-1`이므로 이 식에 target 밀도·추가 4π를 곱하거나 나누지 마라. 신호의 `delta(nu*Gamma) = average(nu)*deltaGamma + average(Gamma)*delta(nu)`는 **exact finite-data symmetric attribution**이고 고유 인과분해가 아니다. 직접 RCT 전자 생성=0, 총 전자 변화는 CI/RR/DR 등과 구분한다. E8의 최종 KF−OFF `5.438774410948304e-22`, GM−OFF `9.243278362850567e-21 electrons/(H s)`는 frozen endpoint diagnostic 결과이며 장기 관측 예측이 아니다.

**보존 필수**: original backend/CI/RR/DR/RCT owner·photon mass/energy ledger 및 escape/heat, native nonlinear/number/energy gates, event/cutoff subdivision, source front, base active spectral cap=4096, cache key cap=32768, original 24-anchor and endpoint extra boundaries, clocks/tolerances. E2 near-limit nonlinear `~0.994762`였던 예가 있으므로 pass 여유가 작아질 수 있다. clipping·자동 tolerance relaxation·implicit fallback 금지. 다른 archived E3 `2.5e-23` rate tolerance와 이 E7 계열 `1e-22`를 섞지 마라.

## 4. 실행 DAG (중복 없이 완료 가능한 모든 heavy 단위)

### H1. Native environment + affected smoke [필수]

- 최신 authoritative E8/E7/E6 ZIP, 원 receiver branch와 staged patch의 source/blob identity를 분리해 기록한다.
- `cargo --version`, `rustc --version`, relevant `Cargo.lock`, path deps 및 `--offline --locked` 가능 여부부터 확인한다. E6 `native/Cargo.toml`은 `parent/holdout`, `parent/base/observer`, `parent/base/staged`, `parent/base/vendor/rei_microphysics`에 의존한다. E8/E7 파일만으로 전체 Rust owner crate를 빌드할 수 있다고 가정하지 마라.
- 먼저 **변경한 adapter의 시험만** 실행한다. Python의 기존 sealed tests 16/22개를 인계만을 이유로 전수 다시 돌리지 않는다. 새 native adapter 테스트는 TDD RED→GREEN, 원본 source files와 baseline API regression smoke를 수행한다.
- `cargo test --offline --locked` 등은 해당 Cargo manifest가 있고 실제 local vendor/lock이 존재할 때만 사용한다. 시스템 compiler flags는 실제 기존 승인된 release/strict 설정과 parity를 유지한다.

### H2. E9 source-matched native output, pilot [필수/즉시]

1. E7/E8의 `SOURCE_LOCK.json` 및 세 history SHA를 기준으로 receiver에서 **실제 일치하는 385개 시각 또는 사전 정의된 bounded common window**를 생성할 수 있는지 소스와 런타임에서 확인한다. 원 owner 25행과 E7 385행을 보간·패딩·반복해 연결하면 `FAIL_OWNER_CLOCK_OR_ROW_COUNT`로 기록하고 중단한다.
2. 기존 `short-hhe-midpoint`의 `output.rs`와 staged RCT03D 쪽 출력 계약이 다르다. 각각 source SHA와 41/40열 위치, `s`, `x`, `y`, `z`, `w`, `ne`, `nH,nHe`, Γ, RCT 별도 사건수, producer ledger를 표준 source map에 명시적으로 매핑하라. 실제 owner source와 동일하지 않은 **synthetic schema projection**은 `SCHEMA_PROJECTION_ONLY`, native PASS 금지.
3. owner-side **read-only opt-in native observer/sidecar adapter**를 별도 worktree 또는 실험 파일에 구현한다. 기존 출력 CSV와 column bytes, `State` evolution, `Gamma` to RHS, photon stock와 누적 energy owner를 바꾸지 않는다. 상태·관측/clock source/hash를 `READY.json`에 기록한다. 실패 시 원 state/ledger 변화 없이 새 sidecar만 미완료(`NO_READY`)로 남긴다.
4. 처음에는 같은 **N384 경로의 첫 1~2 accepted steps + start**만 새로 실행해 cfg/rust flags/stage/order/source가 정확히 같은지 관측한다. 이것은 N=2의 다른 큰 step을 돌리는 것과 다르다. E8의 `check_owner_output` 및 수신단에 실제 native fixture를 입력한다. `SCHEMA_PROJECTION_ONLY` 성공을 이 검증으로 대체하지 않는다.
5. 성공해야만 제한된 3모드 ×384 accepted step (=최대1,152 step)으로 확대한다. 선택한 모드 순서를 OFF → KF96 → GM25로 고정하고 각 모드를 새 output 디렉터리에 실행한다. 이미 원 native 385시각 결과가 **내용 identity로 존재하는 경우는 다시 계산하지 않고 검사 후 수신**한다. 끊긴 run은 durable 마지막 checkpoint가 실제 존재하고 hash가 닫힌 경우에만 재개하며 그렇지 않으면 수치학적으로 정당한 새 full run 또는 BLOCKED를 명시한다.
6. 385×3 clock, mode, background, fractional state, Γ, nu_i, `photo_electron/H/s`를 E7/E8의 실제 표와 대조한다. 동일한 compiler/flags/input에서 bit-identical 예상되는 필드는 f64 bits까지 비교한다. 다른 호스트 반올림 차이가 있으면 원본과 exact difference를 기록하고 **기준 변경 없이** source/ABI/서멤순서 원인을 조사한다. `SOURCE_MISMATCH`, `CLOCK_MISMATCH`, `PHYSICAL_FORMULA_MISMATCH`, `ROUNDING_DIFFERENCE`, `OWNER_SCHEMA_ONLY`, `OWNER_NATIVE_MATCH`를 구분한다.
7. 원 `scaled_nonlinear_residual`, photon number/total energy allowed ratios, species positivity, EOS common T guard, branch/cutoff eligibility, RCT heat/escape/event/chemical ledgers, OLD OFF regression을 변경하지 않고 affected-only 검증한다. 일부 항목을 원 출력이 제공하지 않으면 `NOT_EVALUATED`, 0으로 채우지 마라.

**H2 admission:** `NATIVE_INPUT_SHA_LOCKED ∧ MATCHED_385_CLOCKS ∧ EXACT_MODE_HISTORY ∧ ORIGINAL_GATES_PASS ∧ SIDECAR_RECEIVE_PASS ∧ NO_BACKFEEDBACK ∧ OFF_UNCHANGED`. 원격 `rei_bianchi` owner가 채택한 상태와 로컬 staged pilot 성공은 별개다.

### H3. 필요하면 해당 시점의 absorption-energy moment 계산 [별도 opt-in, 정보가 있는 경우에만]

E8의 `Gamma`와 `Nactive/Eactive`만으로 흡수 열원을 추정하거나 `35 eV` RCT closure를 흡수 사건 평균 에너지로 대입하지 마라. 원 characteristic가 반환하는 **같은** `f_H(eta)`, 원 atomic provider `sigma_i(E)`, 실제 ionization energy chi_i 및 동일 cutoff/source partition을 확보한 경우에 한해 observer-only diagnostic으로 다음을 시험/실행할 수 있다:

`HeatRate_i[per absorber,eV/s] = c*nH*∑_nodes w*sigma_i(E)*f_H(eta)*(E-chi_i)` (반응이 활성인 E>=chi_i 영역; fit cutoff와 실제 chi_i 혼동 금지).

`HeatRate_per_H = (1-x)*Heat_HI + (nHe/nH)*[(1-y-z)*Heat_HeI + y*Heat_HeII]`.

양의 event measure, primary absorbed photon energy = binding + electron thermal deposition 항등식, cutoff-crossing을 보수적으로 분할하고 원래 source/energy ledger와 **직접 가중·중복 소유권을 구별**하라. `Gamma`-heat moment 동일 스펙트럼·시계·단위, zero-source/zero-photon, synthetic monochromatic `(E-chi)*event`, wrong cutoff, He bookkeeping, double deposit rejection을 새 시험에 포함한다. 원 owner photon stock·chemical/escape/heat ledger를 수정하거나 observer moment를 RHS에 결합하지 말라.

필요한 chi/provider/spectral-generation identity가 확인되지 않거나 충분한 source data가 없으면 `PHOTO_HEAT_MOMENT=OPEN_MISSING_INPUT`으로, **적법하게 계산해도 실제 atomic emission photon mean과 전체 physical certification은 여전히 null**로 둔다. H3 실행은 H2의 기존 source-only admission 필수 조건이 아니며 별도 선택형 진단으로만 취급한다.

### H4. 정확도/성능 대상별 짧은 검증과 독립 이식성 [필요한 변경에만]

- H2/H3에서 바뀐 관측기·export/source mapping의 smoke/negative/ledger 테스트와, 이미 입력이 있는 declared output의 diff만 재검증한다. E6 5,199 observer-row campaign, E4 108snapshot, E5 96snapshot, E7/E8 소비자 exact identities, 기존 reference ODE/full heavy suite는 무조건 반복하지 않는다.
- 동일 workload의 single-process vs small independent concurrency를 실제 elapsed/peakRSS/CPU affinity/cgroup memory로 측정한다. 실행 중인 타 프로세스를 선점하거나 종료하지 말라. 성능 최적화는 **bit identity 또는 기존 tolerance parity**가 닫힌 경우에만 수락한다. source/model/격자/criterion을 빠르게 하기 위해 바꾸지 않는다.
- `CACHE_CAP=32768`과 `ACTIVE_GRID_CAP=4096`을 따로 검사하고, 정확 `eta.to_bits` cache key 및 immutable `(cfg, gas trajectory, mode, grid)` owner를 지킨다. eviction/algorithm change는 새 plan과 시험이 없으면 도입하지 마라.
- 스펙트럼 원자 fit, 부재한 물리적 Gamma/source-radius, 시간구간 `C^4` remainder 또는 연속 time/spectral error certificate가 없을 때는 finite-grid 비교만 남기고 true error에 대한 `PASS`를 절대 주지 마라. REI BRIDGE12의 다른 고온 1cell 오차범위를 가져오지 마라.

### H5. 같은 프로젝트 내 다른 heavy lane의 현황 정렬 [read-only inventory / 별도 권한 gate]

다음은 E9 실험과 혼동하면 안 되는 독립 DAG다. 각 owner의 최신 PLAN/authorization/receipt를 실제 읽고 `CROSS_LANE_QUEUE.json`에 DONE/READY/PREPARED/BLOCKED를 매겨라. **이 지시만으로 전수 science dispatch를 하지 마라**.

- BASS_HE atomic C2h: 이전 C2g 독립수치 adapter 이후 `C2H_INDEPENDENT_DISCRETIZATION_AND_EXTERIOR_GUARD_AUDIT`이 한때 다음 node였다. 최신 atomic source/DAG를 확인하여 이미 수행된 작업을 재실행하지 않는다. 아직 미실행이면 독립 이산화/provider·|m|=2·Dirichlet box/fixed physical embedding의 bounded pilot 설계/실행계약까지만 복원한다. 실제 heavy pilot는 해당 원자 과학 node의 source/사전등록·authorization이 현재 유효할 때에만 수행한다. Eq55, full R-domain/production/long trajectory 및 과거 C2g 전체 replay는 자동 허용이 아니다.
- `WU088_HH`: Git last known `649ecb0…`이나 Library에는 ON06G total256/t=3.2e11 s와 XTHREAD01이 별도로 존재한다. 해당 고온 T0/FT03-LCS 및 원 source/proof family를 저온 E9 native와 섞지 않는다. 다음 256→... macro run은 HH owner의 새 승인·원 checkpoint·canonical state ledger로만 시행한다.
- `rei_bianchi` FT03 BRIDGE12: last noted `9e1bad4…`, 첫 [0,46757316.98818144] s cell의 조건부 연속 defect가 완료됐다. BRIDGE13 남은31cell/6birth, full F09, Bianchi geometry 및 장기과학연속해 인증은 **별도 source/domain/승인**을 필요로 한다. 이 HE 요청을 허가로 삼지 않는다.
- `bass_cr`: R12 `890916f…`는 저장된 96snapshot에서 exact symmetric photo moment/state attribution만 완료, 전체 nonphoto/true-error/owner adoption OPEN. CR 계산·HDT/b-grid·원자 근을 HE E9와 합쳐 재실행하지 않는다.

H5 기록은 다음 HE 연구의 물리 dependency를 구체화하기 위한 read-only 수행이다. 독립 owner의 결과를 합성해 `joint all ON`, `F09 global PASS`, `Bianchi admission`, `physical source calibration`이라고 주장하지 않는다.

### H6. 원 receiver의 opt-in source 측 실제 채택 [조건부]

H2/H3가 source-bound native gate를 닫고 owner reservation 상태를 확인한 경우, 코드/테스트/입력 PIN과 검증 receipt를 **owner 리뷰용 additive patch**로 준비한다. 사용자가 승인한 owned research branch의 ordinary non-force push/draft PR 범위만 지키고 main merge·owner 예약 PR 재작성·force-push·production default 변경을 하지 마라. Owner branch에 별도의 reservation/PR authority가 있으면 OWNER_ADOPTION_REQUESTED 또는 PREPARED_ONLY로 반환하라. 채택 확인이 없는데 `REMOTE_OWNER_ADOPTED`라 쓰지 마라.

## 5. 수행·중단 복구·영속적 증거 정책 [전 단위 적용]

원 데이터/성공 로그/실패 로그/checkpoint/부모 manifest를 절대 overwrite하지 않는다. 새 run의 파생 증거는 다음처럼 불변 단계별로 저장한다:

```
$WORK/RUN_ID/
  00_RECOVERY_INVENTORY.json
  01_HOST_RESOURCE_INVENTORY.json
  02_CLOUD_INPUT_RECEIPTS.json
  03_SOURCE_AND_TOOLCHAIN_LOCK.json
  04_EXECUTION_PLAN.json
  05_RUN_LEDGER.jsonl
  runtime/{off,kf,gm}/raw,stderr,stdout,exit,hashes
  tests/RED*,GREEN*,negative*,parity*
  analysis/{E9_STATE_COMPARISON.json,E8_SOURCE_RECEIPT.json,HEAT_DIAGNOSTIC.json}
  review/CLAIM_GATES.json
  delivery/{MANIFEST.json,SHA256SUMS,README_KO.md,RETURN_HANDOFF_KO.md}
```

`04_EXECUTION_PLAN.json`에는 task_id/parent/run_hash/bounded exact commands/expected outputs/number of native histories and steps/resource ceiling/timeout/retries(기본0)/science gate/abort condition을 실제 시행 전에 기록하라. 모델·수치 tolerance·representation·source closure를 바꿔야 하면 새 명시적 science amendment를 만들어 연구 스레드에 반환하고 기존 결과를 덮어쓰지 마라.

프로세스 중단/툴 장애는 `RUNTIME_INTERRUPTION_RECOVERY`로 기록한다. 먼저 running process, PID/cgroup/lock, durable last-accepted step, file tree·bytes·mtime·SHA, subprocess exit/raw stderr, scheduler/checkpoint/manifest를 조사한 다음 **미완료부분만** 실행하라. 죽지 않은 worker를 중복 start하지 마라. 마지막 checkpoint가 완료되지 않았으면 그 prefix를 닫힌 결과라고 가정하지 마라. 모르는 subprocess exit를0으로 꾸미거나 append만으로 restore-verified를 주장하지 마라.

예상 실패를 PASS로 바꾸지 마라. 최소 실패분류: `INPUT_RETRIEVAL_BLOCKED`, `HASH_MISMATCH`, `SOURCE_LINEAGE_CONFLICT`, `TOOLCHAIN_UNVERIFIED`, `COMPILER_BUILD_FAIL`, `OWNER_CLOCK_OR_ROW_COUNT`, `OWNER_SCHEMA_ONLY`, `BITWISE_PARITY_FAIL`, `ORIGINAL_GATE_FAIL`, `ENERGY_OWNER_CONFLICT`, `MISSING_PHOTON_MOMENT`, `CAP_EXCEEDED`, `TIMEOUT_INTERRUPTED`, `CLOUD_UPLOAD_FAIL`, `REMOTE_REF_CONFLICT`, `UNAUTHORIZED_PHYSICS_SCOPE`.

## 6. Git 게시와 Drive/Dropbox create-only 이중 백업

현재 작업 브랜치 HEAD/로컬 dirty를 먼저 확인한 뒤 기존 BASS_HE 연구 브랜치에 소규모 source/adapter/계약/요약/영수증만 **additive + non-force fast-forward** 게시하라. Git original science root와 receiver 타인 전용 브랜치 변경 금지. GitHub의 remote commit/tree/blob/readback를 검증하라. 다른 writer가 HEAD를 바꾸면 lease 실패로 분류하고 새 HEAD부터 재조정하라. reset/rebase/force 금지. Credentials, tokens, raw 개인 데이터, source PDF는 공개 Git에 포함하지 않는다.

대형 runtime code+raw 결과는 새 `BASS_HE_E9_NCP_RUNTIME_<UTC>_<shortSHA>.zip` 등 버전 고유한 **create-only** 파일로 두 provider에 백업하라. 위 Drive parent와 Dropbox parent를 사용한다. 두 provider의 이름, full destination, byte size, object ID, provider ACK, checksum metadata(있는 경우), 생성시각을 분리 기록한다. 이미 동일이름/객체가 존재하면 byte identity로 확인 후 재사용하거나 새 고유 revision명을 사용하며 무단 overwrite하지 않는다. Provider ACK/size 확인은 `UPLOAD_VERIFIED=R1`, 실제 다시 받아 SHA가 검증된 개별 object에만 `RESTORE_VERIFIED`를 부여한다. 정상 R1 뒤 관례적으로 모든 bytes를 즉시 두 번 다운로드할 필요는 없다. 다른 provider의 remote metadata는 확인하라.

## 7. 필수 종료 패키지와 복사 가능한 return handoff

반드시 다음을 생성하라:

- `REPORT_KO.md`: 새 수행 내용, 물리 정의/근사, 적용 domain, 소스 pin, 실제 테스트, 가장 큰 원 오차/ratio, 코드 변경 범위, 실패/부재, 완료·미완료 범위, 다음 node.
- `RETURN.json`: machine-readable task DAG 각 H0-H6 node별 `DONE`, `PARTIAL`, `FAIL`, `BLOCKED`, `NOT_RUN`; 실제 command/exit/test count, source/build hash, 완료 owner output 수/행/clock identity, original numerical gates, binary64 equalities/차이, E8 rate-state sidecar readback, H3 heat source scope, RAM/시간 측정, next.
- `RECOVERY_INVENTORY.json`, `CLOUD_INPUT_RECEIPTS.json`, `EXECUTION_LEDGER.jsonl`, affected-only tests, raw stdout/stderr/exit, full payload SHA256 manifest, code diff/patch, `CLAIM_GATES.json`, `DELIVERY_RECEIPT.json`, `RETURN_HANDOFF_KO.md`.
- Git commit/branch/tree와 Drive/Dropbox 실제 provider 영수증. 한 provider만 성공하면 이중 백업 성공을 주장하지 마라.
- 마지막 보고는 한국어로 (1) H0-H6 상태, (2) native 시계·원 receiver 일치 여부, (3) 종료된 정확한 과학 범위, (4) source/physics/GPG/owner permission blockers, (5) 다음 작업자가 그대로 붙여 실행할 bounded start command 및 hashes를 포함하라.

전역 claim ceiling은 기본 `baseline RCT OFF`, `actual atomic photon/heat/recoil null`, `HE-F2/F09 global OPEN`, `physical HOLD`, `continuous/true-error not certified`, `other three owner science unchanged`이다. 특정 한정 scope가 새 evidence로 닫혀도 독립된 상위 gate를 자동으로 승격하지 마라.

## 8. 시작 지시

지금 즉시 최신 remote refs와 기존 cloud cache를 read-only 조사하고 H0→H1을 수행하라. H1이 닫힌 경우 H2의 **N384 처음 1~2 step pilot**을 실행하고, 통과 시 세 모드 최대1,152 accepted steps 및 E7/E8 source 수신 검증까지 자동으로 이어가라. H3는 실제 단면적/에너지 모멘트 입력과 source contract가 있는 경우에만 read-only 진단을 수행하라. H4 affected-only numerical/performance checks, H5 owner-state read-only queue, H6 승인 범위 내 release 및 두 provider 백업을 진행하라. 이미 완료된 결과가 있으면 identity 확인만 하고 중복 실행하지 마라. 진짜 blockers가 있을 때에는 멈춘 node와 가능한 후속 독립작업을 구분해 durable evidence와 함께 반환하라.
