# HE29 새 native 반환과 공유 reference budget 해석

## 1. 이번에 바뀐 판단

2026-10-20 07:23 UTC의 마지막 PR78 관측 뒤에 별도 PR79 controller와 PR80 실제 native 결과가 게시됐다. PR80의 5개 파일을 실제 Git blob에 대조했고, Dropbox의 `BASS_HE_HE29_NATIVE_RETURN_20261020_c1c4c061.tar.gz` 전체 raw bytes를 읽었다. 새 archive는 276,206,340 bytes이며 SHA256은 `c1c4c06149bf9561141bc0f6b6f39c280bd554a5e1252ed0825f0e950f1c10c6`이다. Archive 내부 manifest의 payload 292/292가 byte/SHA 기준으로 일치했다. 정규 member는 manifest 포함 293개다.

그 안에 이미 `09929b0a06a833f0c2497e72f074ec8694a264df`에서 실행한 `REFERENCE_BUDGET.json`이 있었다. 242,718-byte 파일의 SHA256 `582e59e8f6b43698b060b44cc17aa2496358ba0491b66e84215e0ed01dcd9f00`을 확인하고 결과를 재사용했다. 분석기 재실행은 0회다. 저장 상태는 `COMPLETE_CONDITIONAL_FINITE_CANDIDATE_ANALYSIS`, exit 0, 4/4 admitted, 1 cohort, 오류·missing·hold 배열은 비어 있다.

이전 `NATIVE_RETURN_AUDIT.json`의 1,934-byte 원본과 SHA256 `2bcd94edde08854599597ea8b962683a86cb5ca4af1ad0e1c3bec09b9e3c20cc`도 그대로 재사용했다. 기존 time/mixed/sign 계산을 다시 하지 않았다.

## 2. source / binary / table / runtime 계약

기준해 source는 science `1569f371…`, owner `f7830e2f…`다. 원래 두 canonical patch를 유지했고, 새 세 번째 patch는 준비된 fresh-only controller에 bootstrap을 연결한다. 실제 네 COMMAND는 기존 `reference_runner.py case`다. 기존 과학 source의 변경은 없다.

실제 server binary는 4,691,224 bytes, SHA256 `a82e540797322027deaab6e6bcb2bde746de737adeedbf144313598c65f5b7e9`이며 build receipt와 일치한다. rlib SHA256은 `bc61dcde88e704a581484258243cc7b002e275a6c78f100ae536548d540bcc6c`다. Build receipt의 `native_run:false`는 빌드 시점의 필드이고, 그 뒤 실행한 campaign의 호출 기록을 부정하지 않는다.

science 6개, input 22개, parent 20개의 identity map과 method/RESULT/binary/runtime/thread/qualification 계약을 독립 검토했다. 각 case의 TABLE metadata 내부 `source_table_sha256`은 RESULT와 일치한다. TABLE.json 자체의 파일 SHA와 source-table hash는 서로 다른 대상을 가리킨다. 생성된 table array 전체는 별도로 직렬화돼 있지 않으므로 이번 intake에서 그 배열 bytes를 독립 해싱했다고 주장하지 않는다.

| case | runtime source-table SHA256 |
|---|---|
| r2/table512 | `dbb8be0d7655c0ce44f63eb4008c2a63212e5a493dd47cd5d54fe34de9063256` |
| r4/table512 | `919ca6f42028bffc37cb208916ee5a9927356eb99344fe467f9b98e30e9fddcd` |
| r8/table512 | `813a95fd90b0a8b0586d2ec80cbc706f51d5660e0d234bdd8f69e8d1b01950be` |
| r4/table1024 | `ed68d6cc5aac8769d32c24afded9541248ff2c2f869e1b98cdc4fa8cd71fb315` |

네 pair의 cohort는 `db976cb58d3479cd1a1f67eb5f7498fff912dbb976bb30cf2b9cbdcfaa44076e` 하나다. Runtime은 Python `3.12.3 (main, Jun 19 2026, 12:46:00) [GCC 13.3.0]`, NumPy 2.3.5, SciPy 1.17.0이며 수치 thread는 1이다. 모든 method는 `rtol=1e-10`, scaled `atol=1e-12`, 19개 ledger를 유지한다.

기존 transport의 binary `c4…`와 새 native binary `a82…`는 byte identity가 다르다. 기존 저장점 qualification 6개가 일치하는 범위와 명시된 source/model/table/parent 계약에서 결과를 수용한다. 전체 binary 또는 모든 runtime의 동등성은 주장하지 않는다.

## 3. 네 pair의 실제 수용 결과

| case | Radau T [K] | DOP853 T [K] | 두 method의 절대 ΔT [K] |
|---|---:|---:|---:|
| r2/table512 | 8.239220061680880 | 8.239220061680927 | 4.61852778e-14 |
| r4/table512 | 8.239220060997987 | 8.239220060997964 | 2.30926389e-14 |
| r8/table512 | 8.239220061040786 | 8.239220061040813 | 2.66453526e-14 |
| r4/table1024 | 8.239220060997908 | 8.239220060997969 | 6.03961325e-14 |

8개 method에서 최대 absolute number defect는 `2.71050543e-20/H`, energy defect는 `6.28837260e-18 eV/H`, species defect는 `1.29172524e-19`다. 최대 method fraction 차는 `1.57548128e-19`다. 원래 abs-fraction `1e-11`, method ΔT `1e-9 K`, number `3e-15/H`, energy `3e-12 eV/H`, species `3e-12`와 원래 양성성 gate를 만족한다. 정확한 원값과 수용 검사는 `evidence/INDEPENDENT_NATIVE_RETURN_REVIEW.json` 및 원래 RESULT에 있다.

독립 심사의 중대 finding은 0개다. 비차단 RPT1은 producer DAG에 새 4/4와 상속된 `NATIVE_HOLD`·`BASELINE_4_OF_4_REQUIRED` 표기가 섞인 보고 문제다. 이번 current DAG에서 현재 상태를 바로잡고 원본 snapshot은 보존한다.

## 4. 저장된 transport residual과 strip/table 대비

아래 값은 저장된 transport 온도에서 같은 case의 Radau 후보 θ를 뺀 signed residual이다. DOP853 후보를 선택해도 여섯 residual은 모두 음수다. 이는 저장된 후보와의 차이이며 참 ODE 해에 대한 오차반경은 아니다.

| strips | n32, Ttransport − θ [K] | n64, Ttransport − θ [K] |
|---|---:|---:|
| r2 | −1.6060344165680362e-9 | −4.313687185231174e-10 |
| r4 | −6.729692358931061e-10 | −4.1820946705684037e-10 |
| r8 | −5.052829266105618e-10 | −2.1322854593108787e-10 |

r2/n32의 transport residual이 1e-9 K보다 큰 것은 Radau–DOP853 pair gate 실패가 아니다. 그 gate는 두 기준 method의 차이에 적용한다.

| 대비 (뒤 − 앞) | Radau [K] | DOP853 [K] | finite 후보 해석 |
|---|---:|---:|---|
| r2→r4, table512 | −6.828937415548353e-10 | −6.829630194715719e-10 | 두 후보에서 음수 |
| r4→r8, table512 | +4.2799541688509635e-11 | +4.284927968001284e-11 | 두 후보에서 양수 |
| r4, table512→1024 | −7.815970093361102e-14 | +5.329070518200751e-15 | 후보 hull이 0을 포함 |

두 strip 대비의 부호가 다르므로 단조 수렴이나 Richardson 차수를 선언하지 않는다. r4의 table 대비는 현재 후보 수준에서 작고 부호가 결정되지 않는다. 단일 table512 canary를 준비된 범위 그대로 진행할 근거는 되지만 table512의 참 table-error 상한이나 전역 온도 오차상한을 인증하지 않는다. 전체 격자를 확대할 이유를 새로 만들지 않는다.

`linear_budget.py`는 binary64 입력을 먼저 정확한 Fraction으로 바꾸고 같은 reference key의 계수를 합쳐 소거한다. `product_hull`은 key별 독립 method 선택이고 `coherent_hull`은 모든 key에 같은 method를 선택한다. 이번 세 대비의 endpoint는 우연히 같지만 정의를 합치지 않는다. 정확한 유리수 폭과 outward binary64 표시 폭을 계속 구별한다.

## 5. r2→r4 transport 부호가 달랐던 이유

공유 reference를 유지한 저장 분해는 다음과 같다.

`T_b − T_a = (θ_b − θ_a) + (T_b − θ_b) − (T_a − θ_a)`

| r2→r4 | 기준해 차 Δθ [K] | residual 차 Δe [K] | 실제 transport 차 [K] |
|---|---:|---:|---:|
| n32 | −6.828937415548353e-10 | +9.330651806749302e-10 | +2.5017143912009487e-10 |
| n64 | −6.828937415548353e-10 | +1.3159251466277055e-11 | −6.697344900885582e-10 |

n32에서는 양의 residual 차가 음의 기준해 차보다 크다. n64에서는 그 보정이 작아져 음의 부호가 남는다. 이는 같은 reference를 쓴 유한 후보 분해의 구체적 설명이다. r4→r8의 두 분해도 원본 분석에서 보존돼 있다. 네 assembled closure는 exact Fraction에서 모두 0이다. 이 0은 대수적 소거를 뜻하며 물리 오차가 0이라는 뜻은 아니다.

## 6. 실행 비용과 남은 canary

| case | table build [s] | Radau [s] | DOP853 [s] | 전체 case [s] | native calls |
|---|---:|---:|---:|---:|---:|
| r2/table512 | 22.598 | 410.610 | 241.666 | 675.036 | 144450 |
| r4/table512 | 45.139 | 736.460 | 408.557 | 1190.318 | 249782 |
| r8/table512 | 98.487 | 1310.392 | 702.067 | 2111.132 | 407634 |
| r4/table1024 | 89.463 | 980.159 | 619.999 | 1689.787 | 359580 |

Controller 전체 wall은 `5672.090418861015 s`, serial concurrency 1, case cap 3600 s, timeout 0이다. Peak RSS는 측정되지 않았다. 기존 CSR 조립 8.35–8.78배와 제조 IVP 1.38–1.53배는 서로 다른 과거 측정이며 곱하지 않는다. **실제 HE29 packed 속도는 아직 미측정**이다.

네 pair를 다시 실행할 필요가 없다. 기존 a5 packed r4/table512 canary의 baseline 선행조건이 충족됐고, 실제 bridge·owner binary·동일 runtime·thread1·table hash·현지 중복 실행 확인이 남았다. 연결 검토에서 a5 builder/runner가 오래된 process-group 종료 helper를 쓰는 문제를 확인했다. PR79의 이미 검증된 `run_process_group`을 외부 wrapper의 alias로 재사용한다. 원래 a5 tracked source bytes와 original worker entrypoint는 그대로 유지한다. 새 검증은 wrapper의 source guard·인자 전달·실패/receipt 경계에 한정한다.

## 7. 연구 루프와 관측 범위

현재 요청의 standalone physmath-research-loop 1.0.0을 적용한다. 초기 standalone1.0.0과 이전 통합·보존 plugin1.3.0의 실제 적용 이력은 그대로 둔다. 버전 전환은 완료 단계를 다시 실행할 이유가 아니다.

이번 이론 작업은 새 native 수치와 저장된 분석의 계약/해석 심사다. 새 solver·물리 유도·허용치 변경·새 CAS 소거식은 필요하지 않다. 기존 SciSpace/Exa/Wolfram 근거, Wolfram 소거식 2개, 독립 제조 이론 20개와 analyzer 28개 tests를 재사용한다. 새 coding 범위는 위 실행 연결이며 기존 watchdog 14개 검증을 재사용한다. 다른 완료군 HE28 pilot/transport6, HE29 finite-donor90/720·50tests, VigilODE96Python/3Rust, Schur23, ABI2/benchmark/clean build도 재실행 0이다.

다른 대화 검색은 실제 서비스 오류다. GitHub/백업의 구체적 delta 범위와 이전 실패는 `evidence/GITHUB_DELTA_INTAKE.json`, `BACKUP_DELTA_20261020T1305Z.json`, `CONTEXT_EXECUTOR_DELTA.json`에 있다. 미게시 실행의 전체 부재는 주장하지 않는다. 현재 NCP 프로세스는 UNOBSERVED다. Remote Desktop Commander는 기존 월간 quota 정책에 따라 호출·재시도·재접속하지 않았다.

연속 스펙트럼, 전역 gas-temperature 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 HOLD다. finite-donor survival 및 GL256/512 안정성의 이전 근거도 그 범위에서만 재사용한다. 백업 성공은 새로운 과학적 동등성이나 수치 결과가 아니다.


## 8. 새 wrapper 연결 검증과 실행 작업공간 복구

새 `ncp/packed_entry.py`는 고정 a5 target와 ed5 controller, 원래 execution module의 실제 Git root/HEAD/tracked-clean/SHA를 검사한다. Build/preflight/canary만 노출하며 원래 인자와 worker argv를 유지한다. 출력은 checkout 밖의 서로 분리된 새 경로이고 기존 partial/실패를 보존한다. 원래 a5 scientific code bytes는 수정하지 않았다.

새 연결 범위의 **9 test method가 2026-10-20 13:26 UTC 첫 실행에서 PASS**했다. Fake target/watchdog/Git 응답으로 source 거절, target/worker 인자 전달, binding, 기존 결과 보호, 실패 전파를 확인했다. 기존14 watchdog tests, scientific import, solver/native/build 실행은 모두0이다. 새 NCP handoff의 Bash4블록 syntax도 PASS이며 명령은 실행하지 않았다. 증거는 `evidence/PACKED_ENTRY_TESTS_FIRST.json`, `NCP_HANDOFF_SYNTAX.json`이다.

이 연결에 필요한 API 근거는 Exa로 Python3.12 공식 subprocess/os 문서의 `start_new_session`, `wait`, `killpg` section을 실제 읽어 확인했다. 첫 fetch의 section 이전 truncation과 검색된 최신3.15 문서 제외를 기록했다. 기존 watchdog 알고리즘과14 tests를 다시 검증하는 작업으로 확대하지 않았다. 새로운 과학 질문이나 소거식이 없어 SciSpace/Wolfram은 이전 근거를 재사용했다. `EXA_PACKED_ENTRY_API.json`과 exact raw 반환 두 파일이 근거다.

작업 중 runtime 전환에서 scratch의 파일이 사라진 것을 root와 reviewer가 실제 ENOENT로 관측했다. 게시된 intake는 Git25f4aea4에서 새 checkout으로73/73 bytes를 복원했고, 원래 선택 증거68/68 SHA도 일치했다. Wrapper/tests/handoff는 보존된 tool 원문으로 복원해 유실 전 SHA가3/3 일치했으므로 첫9PASS와syntax를 재사용했다. 파생 Exa 요약의 유실된 원래 생성시각만 복구하지 못해 새 재구성 표지를 달았고 원bytes 복원이라고 주장하지 않았다. 그 과정에서 수치·검사·Exa 반복실행은0이다. `RUNTIME_RECOVERY.json`, `PACKED_ENTRY_RECOVERY.json`에 상세 범위를 보존한다.

실제 clock가13시대에서17시대로 바뀐 시간공백 뒤 PR79/80과 최근 PR 목록 및 한정된 backup delta를 새로 관측했다. 두 결과/controller HEAD는 그대로였고, 관측된13:10이후 backup 범위에서는 추가HE29 반환0이었다. 이 관측은 미게시 remote process의 부재를 뜻하지 않는다.

새 wrapper의 독립 C9는 중대/경미 finding **0/0, PASS_SCOPED**로 마감했다. a5 target2·ed5 watchdog·legacy execution의 실제 Git source SHA4/4가 wrapper 상수와 일치했다. 그 심사는 첫9검사와Bash4syntax를 재사용했고 추가test·solver·build를 실행하지 않았다. 새 wrapper 실행 pin은 `dd844bc7a1103127198ee2e0343b130f73faa9a4`, tree `02fd29d3c2a9e428fb4ff28307b45f0e23da471e`이며 변경18파일을 실제 Git에서 다시 읽어 모두 일치했다. 후속문서는 이 code pin을 바꾸지 않는다.

## 9. 종료와 재개

새 반환 수용, 저장 분석 해석, wrapper 연결에 해당하는 R1–R10/C1–C10 범위를 마감한다. 단계별 재사용과 새 수행은 `LOOP_STATUS.json`에 있다. Native 기준해 4/4는 수용됐고 packed canary는 NOT_RUN이다. 문서16cd646a를 보존한 401265-byte 통합 archive77324b4c는 Dropbox의 실제 raw readback에서 100/100 payload가 PASS다. 후속 최종 metadata와 두 canonical prompt는 별도 closeout에 보존한다.

Stage1 Drive는 581.9초 동안 ACK 없이 대기한 호출을 parent agent가 중단한 UNKNOWN이며, 추가 쓰기는 0이다. 이 보존 한계를 과학 실패나 완료된 native 결과의 부재로 해석하지 않는다. 다음 단계는 현재 host의 프로세스와 저장 결과를 관측할 수 있는 실행자에게 준비된 단일 canary를 연결하는 것이다.
