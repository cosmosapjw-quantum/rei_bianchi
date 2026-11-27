# HERE_RUX03_EVENT_BRIDGE_02 — 최종 독립 판정

## 결론

**PROMOTE_SCOPED_CONDITIONAL_EVENT_BRIDGE.** 최종 CLAIMS.json의 C01–C05를 선택된 warm Case A conditional production 경로에 한정해 승격한다. C06은 올바르게 명시된 제한으로 받아들이고, 그 안의 전체 owner RUX03·implicit primary/root·물리 시나리오 과제는 **HOLD**로 유지한다. 이번에 검증한 범위에서 해결되지 않은 fatal 또는 material 오류는 발견하지 못했다.

완료한 것은 기존 production 조합의 원시 사건 bundle과 실제 AXI RHS 소비다. PR97에는 이미 warm Case A 조합이 있었고 PR101의 clean-build 보완도 반영되어 있었다. 이번 결과를 최초 물리 연결, 전체 receiver RUX03 완료 또는 과거 미결 실행의 소급 승인으로 읽지 않는다.

이 판정은 `FINAL_CLAIM_FREEZE.json`의 16개 고정 파일과 `REVIEWED_ARTIFACTS.json`의 실제 SHA256에 연결된다. 증거 색인 29개 항목과 최종 build receipt의 34개 소스 identity를 확인했으며, 중복을 제거한 직접 binding은 93개 파일이다. 미래 전달·행정 파일은 자동으로 과학적 판정 대상이 되지 않는다. 고정된 문서의 작성자 상태 `SUBMITTED_TO_INDEPENDENT_REVIEWER`는 원본으로 보존하고, 최종 판정은 DECISION.json이 소유한다.

## 검토자의 역할과 읽은 범위

검토자는 실제 별도 subagent `/root/dropbox_checkpoint`다. 직전 루프에서 source 복구를 담당했고 이번 루프의 후보 생성, 코드 작성, oracle·probe·test 설계 또는 acceptance threshold 설정에는 참여하지 않았다. 고정된 v1 소스, v2 formatting 차이, 실제 native 및 probe·interval 증거, 최종 주장·보고서·후속 DAG를 읽고 판정했다. 후보나 기준을 수정하지 않았고, native build·과학 계산·interval을 재실행하지 않았다.

같은 공동 작업 세션과 파일시스템을 사용하는 독립 decision review이며, 별도 연구기관의 실험 재현 또는 새로운 독립 구현의 실행이라는 뜻은 아니다. 원시 소스와 실행 로그의 검토, 문서 간 주장 범위 확인, 읽은 파일의 해시 결합을 수행했다. 초기 소스 검토는 `INTERIM_SOURCE_REVIEW_v2.json`에 남아 있고 최종 실행 증거를 아래에서 추가한다.

## 주장별 판정

| 주장 | 판정 | 직접 근거와 범위 |
|---|---|---|
| C01 | PROMOTE | 실제 production consumer가 private FT03 provider의 owned bundle을 AXI source/RHS로 소비한다. 제조된 HeIII RR 변화량의 소비 횟수 시험이 실제 native에서 통과했다. |
| C02 | PROMOTE | 기존 RR·DR kinetic moment, 사건·종·에너지 projection, proper/reference-volume 단위와 선택 guard를 보존한다. 코드 검토, 대상 및 전체 native tests, stage 검사가 함께 지지한다. |
| C03 | PROMOTE | 초기 22개 원시 성분의 Decimal60 대조와 두 callback의 선언된 79개 검증 항목이 통과했다. 후기 callback은 저장 상태의 진단이다. |
| C04 | PROMOTE | 변경된 source-bound binary로 초기값에서 시작한 새 단일 production IVP가 기존 유한 이산화의 결과를 보존했다. |
| C05 | PROMOTE | 최종 committed source, fresh clean build, binary, prelaunch validator와 실제 실행 증거가 연결된다. source hash만으로 과학적 타당성을 판단하지 않았다. |
| C06 | HOLD | 원문이 남긴 owner·implicit/root·scenario·physical admission의 미완료 상태를 유지한다. 이 제한 진술은 정확하며 현재 단계의 승격을 막지 않는다. |

## 사건·물리·코드 판단

실제 경로는 `ProductionInterval.rhs → NativeConsumer → ConditionalSession → SourceBoundConditional::evaluate_detailed → detailed_rhs → CaseAEventBundle::into_ledger → axisym_coupled_derivative`다. 공개 API는 기존 FT03 provider를 고정 선택한다. private test provider는 임의의 물리 provider를 승인하는 우회로가 아니다.

bundle은 CI, RR, 두 DR 사건률과 이미 계산한 RR·DR captured kinetic powers를 받는다. native thermal 평가의 photon 입력은 0이며 node별 primary PI 사건을 별도로 생성한다. 소비 시 기존 aggregate thermal/escape 출력을 다시 더하지 않는다. diagnostic summary는 해당 소비로부터 나오고, `EVENTS` 자체가 두 번째 provider 평가를 추가하지 않는다. probe의 RHS와 EVENTS는 동일 상태에 대한 별도 두 호출이며 실행 횟수도 그렇게 기록되어 있다.

세 순 이온화 edge를 CI−RR+PI로 구성하고 HeI edge에서 두 DR을 빼면 H/He 핵수와 전하가 보존된다. 전자 source는 세 순 edge의 합이고, binding power는 각 edge에 해당 binding energy를 곱한 합이다. 열에는 CI threshold work와 RR/DR captured kinetic cooling을 빼고 primary excess energy를 더한다. Case A escape에는 RR/DR의 binding과 captured kinetic energy를 한 번 더한다. 같은 photo event가 광자 loss, 이온·전자 변화, binding과 heat를 연결하므로 전체 상호작용 에너지 항등식과 부호가 맞다.

단면적 fit cutoff와 binding energy의 차이를 유지했다. 사건률은 proper cm^-3 s^-1, power는 proper erg cm^-3 s^-1이고, AXI 경계에서 각각 10^6과 0.1로 SI 변환한다. reference photon loss에는 a_rel^3을 한 번 적용한다. 기존 stage의 clock·density·외부 HM12 source와 geometry·expansion work를 중복 계산하지 않는다. 기존 guard를 넓히거나 CR/RCT/HH를 켜지 않았으며, 재결합 photon count·spectrum은 계속 정의하지 않는다.

선형 보존식은 보존적인 사건을 두 번 소비한 오류도 통과시킬 수 있다. 이번 HeIII RR 시험은 별도로 주입한 사건 수와 kinetic power의 예상 변화를 실제 species·electron·binding·thermal·escape 및 RHS에서 확인하고 provider 호출 횟수 1을 검사한다. 원래 광자와 외부 source가 그대로라는 항목도 실제로 통과했다. 이것은 선택된 채널과 seam에서의 판별 증거이며 모든 가능한 provider에 대한 형식 증명이 아니다.

## 실제 실행과 수치 판정

| 증거 | 확인한 결과 | 해석 |
|---|---:|---|
| 최종 clean release build | fresh target, exit 0 | 정확한 최종 source revision에 연결됨 |
| conditional native tests | 11 passed, 0 failed | 실제 주입 witness와 기존 stage·domain·volume·work 검사 포함 |
| FT03 native tests | 8 passed, 0 failed | 기존 event·thermal moment·guard 검사 포함 |
| 전체 workspace verify | 176 passed, 0 failed | 대상 19개와 중복되므로 합산하지 않음 |
| Decimal60 초기 원시 성분 | 최대 상대차이 1.0942794551292369e-12 | 사전 3e-11 기준 통과 |
| 초기 gross-normalized source | 최대 5.464134883124979e-13 | 사전 3e-11 기준 통과 |
| 두 callback의 invariants | 최대 6.059918126088299e-15 | 사전 1e-12 기준 통과 |
| 성공 probe | BIND 1, RHS 2, EVENTS 2, exit 0 | initial 및 retained-final state에 대한 48+31개 항목 |
| 새 production interval | 257 RHS, 17 epochs, 2.8773785139928805 s | DOP853, 0..1e11 s, 2904 nodes |
| 저장 기준 대조 | state_scaled_max=0; 22개 출력 오차 모두 0 | 선택된 이산화와 solver에서 default 보존 |
| interval local ledger | photon 7.000969126733937e-15; energy 1.7556755934167118e-16 | 기존 1e-9 ceiling 통과 |

Decimal oracle의 보존된 생성기를 읽었다. 후보나 native module을 import하지 않고 고정된 FT03/Verner 식과 초기 weighted photon nodes에서 직접 60자리 연산을 구성한다. 원계산은 stdin으로 실행되었으며 현재 보존된 script 자체가 원실행 진입점이었다고 주장하지 않는 수정이 최종 문서에 반영되어 있다. source 식·단위·채널 대응은 맞고, 외부 source는 0으로 대체하지 않는다.

초기 상태가 거의 평형이므로 decimal 전사와 binary64 중성 분율 뺄셈의 작은 차이가 tiny net rate의 상대오차를 크게 만들 수 있다. 검증은 원시 성분별 상대차이와 gross event/energy 규모로 정규화한 순 source 절대차이를 구별한다. 이 기준은 미리 선언되었고 실행 후 완화되지 않았다. 결과를 tiny net rate의 상대 정확도, fit의 물리 정확도 또는 전 영역의 수치 상한으로 확대하지 않는다.

probe의 후기 상태는 원래 저장된 마지막 상태를 읽은 진단이다. 반면 production runner의 `integrate()`는 NPZ의 initial_state만으로 새 적분을 수행하고, `compare_reference()`가 적분 후 저장 이력을 연다. 코드에서 이 순서를 확인했다. 따라서 새 구간의 저장 기준 차이 0은 기존 결과를 적분 결과로 복사한 증거가 아니다. 동일 이산화와 조건에서 이번 변경이 결과를 보존했다는 실행 증거다. 새로운 refinement·continuum certificate를 주장하지 않는다.

3패널 그림도 실제 파일로 확인했다. gross reaction rates, 22개 primitive의 8개 그룹별 최대차이, 이번 새 구간의 온도 변화가 해당 자료와 맞고 조건·범위가 표시되어 있다.

## 실패·수정 및 provenance의 한계

첫 native 후보는 build와 대상 tests가 통과했으나 format check가 exit 1이었다. 정확한 rustfmt 출력은 chain 줄바꿈과 동등한 single-expression closure 표기만 바꿨다. 최종 commit으로 clean build를 다시 했고 format도 통과했다. V1/V2 binary bytes가 같다는 사실과 별도로 V2 source의 독립적인 build receipt를 확인했다. 첫 실패를 지우지 않았다.

첫 local probe는 원래 `sources/acquisition.json`이 local materialization에 없어서 BIND 1회 후, RHS/EVENTS 전에 멈췄다. 최종 입력 복구 기록은 PR97의 정확한 metadata SHA와 Git blob을 보존한다. `load_hm12()`가 실제로 이 파일에서 table 크기·hash·source URL을 읽는 것을 확인했다. source·binary·rate·guard·threshold를 바꾸거나 hash 검사를 우회한 것이 아니다. native capture의 일곱 고정 입력이 완전한 provider snapshot은 아니라는 제한과 재현 시 보조 metadata 필요가 최종 안내에 반영되었다.

기존 interval runner는 numerical JSON을 native close보다 먼저 기록한다. 그러므로 JSON의 PASS만으로 outer exit 0을 추론하지 않았다. `OUTER_EXECUTION_RECEIPT.json`은 실제 terminal completion을 본 owner가 사후 작성한 기록이며, session 34628의 exit 0 관측과 저장 stdout/stderr/result hashes를 명시한다. 해당 stdout는 metadata·validation JSON이고 stderr는 빈 파일이며 identity가 맞다. 이 사후 기록은 자동 instrumentation이나 raw tool export도 아니고 검토자가 직접 관측한 process completion도 아니다. 이 증거의 수준을 그대로 유지하며 새로운 실행으로 보강했다고 주장하지 않는다.

## 고정 identity와 최종 종료

| 대상 | identity |
|---|---|
| 최종 source commit | a5c958c414dea41216b445c05f58df837f05cacb |
| 최종 source tree | 2e96362102caa69c814d477bae5d1c0177b502f9 |
| 실행 binary SHA256 | 1edf5660e0d451ce0ae066750981c3cf3038fa376a24fed4ec1f378304d6a1e0 |
| 최종 build receipt SHA256 | 91f5621c6dd630c758af0a85280af32ba7f9eb3f96b27246550e7eba23d3999d |
| 최종 claim freeze SHA256 | 5a1214f7a58b6b1a9d9cc547bcee2508045b113f9a76f6d171500ed229e07db4 |

증거, 물리·수학 유효성, 검증 가능성, 수치적 견고함, 실행 비용, 가정과 원래 동기를 각각 평가했다. 현재 scope의 실제 완료 기준은 충족했다. 새로운 원자 정확도·novelty·model 성능은 주장하지 않는다. 추가 unchanged test/interval이나 재귀적 review는 요구하지 않는다.

다음 작업은 `HERE_RUX03_PRIMARY_PROVIDER_03`이다. 기존 implicit primary의 실제 point와 root/interval 경로에서 같은 provider를 쓰는지 확인해야 한다. 원 owner DAG의 17개 ID와 의존성, RUX02/RUX03의 병렬 준비 및 RUX04 이후에만 물리 RUX05로 넘어가는 조건을 유지한다. 현재의 `scientific_admission: HOLD`, Case A escape, CR/RCT/HH OFF, 기존 B1·11-history·PR113·P03A 계승 및 E13C11 parked 상태도 유지한다. 이번 독립 판정으로 전체 owner node를 닫지 않는다.
