# v10 C9 독립 구현 심사

## 판정

**PASS_SCOPED, 열린 지적 0.** 하나의 정식 심사에서 제출한 네 지적의 수정 코드를 다시 읽고, 실제 마지막 10개 표적 fake/API 테스트 로그와 누적 실행 영수증을 확인했다. 본 심사자는 과학 구현·packaging helper를 작성하거나 수정하지 않았고 native 계산·과거 캠페인·추가 benchmark를 실행하지 않았다. 심사 중 수행한 계산은 기존 파일의 SHA/크기/동일성 및 영수증 합계 확인이다.

검토 기준은 `abbf71caf4bd45af5bdf8bc7744690d10b8715e7` 이후 새 `native_optimization_20261021` 구현이다. 정확한 9개 과학 source, 5개 delivery helper 및 원 evidence 해시는 `REVIEWED_SOURCE_IDENTITIES.json`에 기록했다. R6의 수학 심사를 반복하지 않고 구현의 해당 식·배치 위치·실제 결과와 연결되는 부분을 확인했다.

## 네 지적의 종결

| 지적 | 수정과 실제 근거 | 상태 |
|---|---|---|
| C9-01 timeout 출력·비용 | `verify.execute`가 build/light 양쪽 TimeoutExpired의 stdout/stderr prefix·exit124·wall·budget을 먼저 저장한다. 최종 테스트가 양쪽 경로를 실제 짧은 child로 확인한다. | CLOSED |
| C9-02 중단 child와 resume | preexec의 자기 `/proc/self` handoff로 local PID/procfs PID/PGID/start ticks/namespace를 저장한다. 살아 있거나 확인 불가이면 새 launch를 거부하며, 종료 확인 뒤만 INCOMPLETE/full-cap debit을 쓴다. 자기 child 종료·launch 예외도 raw prefix와 receipt를 남긴다. 실제 fake child가 살아 있을 때 거부·종료 뒤 debit을 검증했다. | CLOSED |
| C9-03 거부 결과 재승인 방지 | postprocess가 current identity와 출력 SHA를 다시 확인하고, 불일치 결과를 finite pair 또는 complete trace에 쓰지 않는다. cached age32는 원 archive SHA와 출력 파일 SHA를 재검증한다. 변경된 identity/output/reference fake 입력이 거부된다. | CLOSED |
| C9-04 B1 reference 구분 | 원 B1 build receipt·binary·prepared identity를 확인하고 current run identity에 연결한다. 새로운 BE binary는 별도 SHA이며 `V10_BE_BINARY_IS_DISTINCT`로 기록한다. | CLOSED |

PID 회귀 과정에서 `/proc`와 local PID namespace 차이를 실제로 만났다. 실패한 14번과 16번 로그를 보존했으며 각각 0.412263272999553s와 5.106057174998568s를 누적 light 비용에 포함한다. 최종 18번은 10/10 PASS이다. 저장된 특정 자기 child의 `/proc`만 읽으며 host process inventory나 다른 lane 종료는 추가하지 않았다.

## 과학 구현의 범위

Subnormal repair는 원 count/energy gate에서 실패한 finite positive subnormal mass에만 opt-in으로 적용된다. 후보는 support 안의 한 양의 atom과 인접 representable 값이며 원 compensated count·energy gate를 그대로 재사용한다. 통과한 기존 경로와 원 tolerance는 유지한다. 이는 제한된 복구 후보와 실제 N2/N3/N4 재현의 통과이며 모든 입력에 대한 성공 증명이 아니다.

Ordered worker pool은 결과를 원 cohort 순서로 줄인다. 실제 compiled core의 원 pool을 재사용하고 중첩 병렬 호출을 추가하지 않았다. Compact observation trace는 원 common8 출력 위치만 보존하며 solver stepping·birth schedule·final physics를 바꾸지 않는다.

BE observer는 accepted Newton chemistry와 원 local absorption ledger 이후에 배치된다. 원 코드의 저장 분모 연산 결합 순서와 compensated opacity를 따른다. Q_lo/Q_hi, S_lo/S_hi는 저장 양의 가중치와 저장 분모에 대한 discrete BE 산술 진단이다. Empty-node는 별도 count와 zero mass로 기록한다. 실패 prefix는 INCOMPLETE이며 continuous path 또는 nonlinear Grackle response certificate로 해석하지 않는다.

## 실제 검증 evidence의 재사용

원 offline build 10.046360894004465s와 kernel example build 0.32940484999562614s의 합은 **10.375765744000091/120s**이다. 저장된 18개 light command의 합은 **9.371467903998564/240s**이며 setup 거부·실패한 namespace 회귀·기존 20개 sample의 그림 생성도 포함한다. 수정 후 Rust/build/trajectory를 재실행하지 않았다.

Valid tiny config는 2 births/n_mu8/source8/transport8, 11 mesh steps/89 RHS이다. serial off, parallel off, parallel observer, full observer 네 변형의 endpoint·observations·native return 파일을 직접 읽어 byte equality를 확인했다. 두 observer trace도 11행 전체가 동일했다. 초기 transport4, n_mu2, source1 setup 거부는 guard를 완화하지 않고 로그에 보존되어 있다.

| 재확인 파일 | SHA256 |
|---|---|
| tiny endpoint.json | `cca0b16cba9053b4b88b7a1803ded4ca47dae3e2a965fdf83e68be61447ce6a0` |
| tiny observations.json | `e734b3791a3ee8561d429c9057f167c2067dadc84c122f6fa10187ab1d1a5a6e` |
| tiny native_return.json | `d8e0ecf2ac7d6d9faf77ccb4a6f5b7665c1f0adfcccefaf2a55261a4130a1039` |
| observer be_trace.jsonl | `942b89c28dc6c2c7753ab8e2abb2ab38ad1f6d1c9ed702d554e03d240a432fd2` |
| 실제 새 BE binary | `af3d431589f033b45f8aa1376e25dc58917c9d9b38b4b30a8802019626494f8d` |
| compiled PREPARED_IDENTITY.json | `2328685f7c37d65eb8c275fef7f1c8f568d02bc344bbf4e4f807f9f5e8fbae84` |

현재 prepare source로 fresh generation한 3개 Rust 파일과 실제 compiled source의 SHA가 각각 일치한다. prepare.py의 이후 offline Git 연결 수정은 generated native Rust를 바꾸지 않았다. NCP에서는 current overlay hashes→PREPARED outputs→build receipt binary hash→preflight identity를 다시 묶으므로 sandbox artifact를 무조건 재사용하지 않는다.

Kernel microbenchmark의 실제 20 JSON rows를 MICROBENCH.raw와 대조했다. 32 cohort jobs×832 nodes, fixed absorber/dt, sample당20 iterations, mode당5회이다. 중앙 wall은 original serial .009680326s, ordered pool1 .009681998s, pool2 .006849993s, pool4 .004608712s이다. 출력 bits는 동일하다. 이것은 한 process의 고정 순서·짧은 kernel 측정이며 whole IVP 또는 64core host speedup 주장이 아니다. KERNEL_TIMINGS.png는 이 기존 표본을 그린 것이다.

## 자원·자동 인계·delivery 검토

Current host allocation은 affinity/cpu.max와 현재 `memory.max - memory.current` headroom을 사용한다. Shared host에서는 사용자에게 파일 처리를 요구하지 않고 agent가 실제 배정 CPU/memory를 명시한다. 가정상 idle64/128의 jobs3/workers20/63slots, 24GiB per case와 reserve16GiB 계산은 코드와 일치한다. 실제 NCP64/128 hardware는 이번 대화에서 NOT_OBSERVED이다.

`HANDOFF_CODEX_CURRENT_KO.md`의 plan-only/실행 명령, 단일 --c10 또는 --repo 선택, rust-prefix, time8/16/32 fixed args, case1800/aggregate5400, jobs별 elapsed2000/3800/5600, compile300, light240, zero automatic retry는 현재 CLI와 일치한다. 원 B1·native153·computational base와 새 BE binary의 역할도 구별한다. 원 age32 reference는 자동 tar restore이며 positive DOP853와 native BE 사이 cross-operator 비교라고 명시한다.

C8/C10/confirmation builders와 두 provider readback helpers 5개를 정적으로 읽었다. 실제 frozen Git source와 parent/tree를 입력받아 count를 유도한다. v9 C10의 원 native153/B1/deduplicated161/vendor22·865/native32 raw는 유지한다. Whole bytes/SHA/CRC/payload/source blob+mode/tree 및 네 provider readbacks를 확인하며 confirmation은 실제 source→delivery A/M UTF-8 exact delta를 복원한다. Confirmation 자체 SHA/own provider IDs는 외부 영수증으로 남겨 순환 참조를 만들지 않는다. **이 C9는 helper 정적 심사이며 아직 생성되지 않은 v10 archive/provider readback을 PASS로 대신하지 않는다.** 게시·백업의 실제 영수증은 root가 별도로 완성한다.

## 종료 범위

이번 네 항목의 직접 의존과 수정 증거 확인으로 정식 심사를 종료한다. Native time8/16/32 full cases는 NOT_RUN_LOCALLY이며 NCP 실제 실행이 남는다. Native age/time 수렴 HOLD, nonlinear_response_bound=NOT_ESTABLISHED, PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED를 유지한다. Root 전체 CI 상태와 여기 scoped build·fixtures·fake controller checks는 별개다.
