# REI 중간 감사와 다음 실제 연구 단위 — 2026-10-25

중앙 `c5050305f84a051cb797cd84c84768c76bcb18b9`에는 REI-L0, native HI, massive stress, strain response의 실제 완료 자료가 있다. 기존 중앙 DAG의 REI-L0..L5 `PROPOSED` 표기는 원래 계획 snapshot이며 현재 과학 진행 상태를 그대로 나타내지 않는다. 이번 감사는 원 계약40개·통합 edge17개·authority7개를 보존하면서 새 관측을 추가하는 방식을 채택한다. 전체 모형 완료율은 null, L4 readiness는 false다.

## 직접 확인한 기준과 범위

GitHub PR222는 open/draft/unmerged, HEAD c5050305; historical fixed authority는0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17이다. Compare 응답은52commits ahead/0behind다. 실제 AGENTS blob429a5a13ee75b1222bc50627f8d5973d01dd21c4는 신뢰된 개인 연구 저장소, 과학 정확성·재현·예산 보존, tiered authority→coding→independent review, 새 clone 기본 금지를 명시한다. 현재 checkout은 없으므로 새 구현은 root 지정 staging leaf에 두고 기존 central tree에 additive publication한다.

원 DAG40개 status의 문자 그대로 집계는 PROPOSED34, COMPLETE_SCOPED2, PARTIAL2, OWNER_DELIVERY_PENDING1, SOURCE_INPUT_PENDING1이다. 이는 서로 다른 범위의 원 계획 상태이며34개 미착수 또는2/40완료라는 과학적 집계로 바꾸지 않는다. 특히 REC 분기 PR229 관측과 Library-only 후속 연구는 canonical DAG 밖에도 존재한다.

PR221 actual HEAD8d10231b1f0f788164d5eadbe1bcee0b802cceca와 PR229219fe60a3f069dda26e109f6e0cd1fd339c83701도 읽었다. 후자는 별도 branch 관측이므로 canonical에 자동 merge된 것으로 취급하지 않는다. 다른 모든 branch의 본문을 전수 읽었다고 주장하지 않는다. Root의 conversation_intake.json은 최신 결과 위치 단서로 사용했고 실제 Git/Library 자료와 대조했다. 이전 대화의 '미게시/미완료' 기록은 해당 시점 기록으로 보존한다.

## 완료 결과 재사용

| 단위 | 실제 근거·판정 | 현재 경계 |
|---|---|---|
| REI-L0 mixed UV repair | `uv_mixed_20261024/ADMISSION.json`: ADMITTED_SCOPED; source SHA c8dc1d8e…; 독립 source review 및 actual4before/4after 한 fixture | finite source/JVP·STF 대수; 원22/66/83 재생0 |
| Conditional Bianchi stock/work | STOCK_ADMISSION 및 WORK_ADMISSION 실제 파일 | 조건부 stock 적분산술/저장stock 기반 work; 실제 HI history 선택 아님 |
| HI native atoms | ADMITTED_SCOPED_NATIVE_HI_COMMON_MEASURE, science8d68dff35ca2bdc456049081132a7d2449b29143;4368atoms/13105scalar checks/13controls | HI,z2.479 per-target source; legacy aggregate와 common measure 구별 |
| HI massive stress | ADMITTED_SCOPED_NATIVE_HI_MASSIVE_STRESS; science42f5984a78f123ce26950cec0e0b8505da3e7ce4, deliveryecbb3124… | native radial measure의 M-dependent pressure; declared isotropy; heat 아님 |
| HI strain response | ADMITTED_SCOPED_NATIVE_HI_STRAIN_RESPONSE; science190e283…/deliveryb24a9da…; theory,source,raw,receipt,review 직접 읽음 | instantaneous symmetric Bianchi-I strain, birth-normalized source measure; actual stock/history/transport 미공급 |
| ANGTHERM01 | PR221 제공 기존10trajectory/21population→9fraction·192→24group | prescribed-background finite system; Einstein feedback 아님 |
| ANGTHERM02 | head8d10231…의 SCIENTIFIC_DECISION 실제 읽음; PASS_SCOPED_CONDITIONAL_LI_THRESHOLD_RESPONSE;10smallIVPs | late conditional trace-Li leaf 완료; full coupled continuum-angular2e-7 목표 OPEN |
| GRID044 continuous opacity | root가 실제 읽은 Library report libfile_53326da92a14819195233da5fbfea464/receipt libfile_15074de9d37c8191afe844ce33215a32 대조;18/18PASS_SCOPED | 두 source·여섯 electronic channel·21state instantaneous residual와25×23Jacobian; N6HOLD, externalGit0 |

Strain actual source는 `deltaP=-C*(tr(B)I+2B)/15`, C=5W−R, CM=5S−RM를 구현한다. 원 raw의4368rows, eightcontrols, normal/subnormal/signed-underflow tags 및 old_tests_replayed0을 읽었다. Source·raw·review를 재사용했으며 이번에 기존 과학 계산을 실행하지 않았다. 보고된 C=4.436150261042243e-11, Gamma=1.666654597903262는 원 scope에서 유지한다. 전체 cosmological 압력/점성/열화로 승격하지 않는다.

ANGTHERM02는 '현재 수행 중'으로 단정할 수 없다. 현재 관측은 conditional leaf 완료와 read-only owner reservation이다. Runtime/dirty checkout/별도 미게시 active worker는 UNOBSERVED다. 최신 GRID044도 N6HOLD이므로 completion이나 unused budget으로 추가 계산을 열지 않는다.

## 예산과 저장 사실

L0 historical10.110448s/10s 초과0.110448s는 FAIL_PRESERVED다. Strain 이후 known partial11.449628s, whole L0 UNKNOWN_NOT_ZERO, original cumulative cap NOT_FROZEN을 유지한다. Strain child0.288967CPU/0.291284354wall, cap6/8, 실제1child/exit0, 재생0을 receipt에서 읽었다. ANGTHERM02 charged105.71851917/120CPU와135.995204254/180wall에는 conservative failure60/90가 포함된다. 이 수치와 다른 lineage를 더해 단일 cost로 만들지 않는다.

GRID044 main595.225063/600CPU는 NO_MORE_IVPs. Continuation8.001104/10CPU,8.029615335/20wall; 이번 opacity child1.239806CPU/1.244051371wall. 최종ZIP2,926,650bytes/SHA b12cc903a9d1d813416b2b77c2f7a8c74c1b657c5c85cf5a683e5e5c64001d9f, Library libfile_11624a776d6481918c3dfc0c92b51d72. Receipt는 실제 provider ACK 기록이며 본 감사는 전체 ZIP 복원·수치 재검증을 하지 않았다. 외부 Git 미게시 결과를 Git완료로 표시하지 않는다.

## 사용자 확장 목표와 소유권

현재 실제 전하 사다리는 n,H1,D,T,He3,He4,Li6,Li7의21population이다. Atomic authority는 CR105b1aed878…의 실제 C23C atomic_contract.py(blob e308ceef315e9f40f96fa62c2667253a1283523e)를 읽어 single-nuclide, q0..Z와39CI/PI/RRdirections를 확인했다. 이21상태를 모든 원자핵·동위원소·음이온·분자 coverage로 부르지 않는다.

확장 목표는 유한하지만 확장 가능한 nucleus key(Z,A,isomer), molecule composition, ion charge, state/channel catalog로 구현한다. 실제 target 목록을 producer가 공급하며 unsupported cell은 UNQUALIFIED, supported zero와 구별한다. All-target mandate는 schema의 보편성 및 owner inventory 의무로 반영하고, 물리율을 없는 상태에서 자동 완성하지 않는다.

- WU088_HH: 원자·동위원소·분자 threshold/rate/branch/nuclear injection microphysics 및 target catalog.
- BASS_HE: source-consistent angular/finite-mass collision amplitudes와 moment/recoil/transport.
- bass_cr: electron/photon distribution, stopping/secondary deposition, selected PI/RR/CI/CX/elastic consumer.
- REC: recombination line/continuum·retarded history/opacity/Compton와 native provider.
- BASS: geometry/frame/clock·external baryonic/nonbaryonic/radiation component·four-force mapping.
- VigilODE: numerical solver/error/restart evidence.
- REI: source event assembly, exact species/charge/energy/owner interface와 후속 selected coupled model.

천체/IGM/stellar/galactic/beta/nuclear/CR/ν 또는 외부 photon/baryon 공급은 위 provider 입력에 실제 소유자를 배정하고 source history·normalization·domain·uncertainty를 공급해야 한다. 같은 event를 여러 repo에서 중복 가산하지 않는다. 기존 개별 owner 결과/failed raw/미완료영역과 source별 물리 ceiling은 보존한다.

## 다음 실행 단위

Root가 REI-CHEM-LEDGER-01을 선택했다. 새 nucleus-composition/negative-ion/molecule/electron-pool/reversible-signature/exclusive-owner compiler는 현재 확인한 C23C/L0/nativeHI 구현과 중복되지 않는다. 기존 exact energy bookkeeping은 재사용하고 신규성을 과장하지 않는다.

`THEORY.md`는 chemical isotope invariance, explicit electron-rest-reference cancellation, independent reservoir-column energy balance, reverse orientation, same-net spectator ambiguity를 실제 유도한다. `FROZEN_COMPILER_CONTRACT.md`는12양성 synthetic cases, exact-rational controls, source conventions, allowedpaths, onechild30CPU/120wall/512MiB 및 source/raw review를 동결했다. 이 예산은 새 분리된 단위이며 과거 cap/reset이나 GRID044 잔여 allowance가 아니다. 새 구현이 PASS하면 생산자들이 molecule/isotope source를 수신 가능한 정확한 interface를 얻는다. 실제 물리율·source history·전체 결합은 다음 의무다.

검증 종료: 이번 감사의 direct-source 부분은 완료, 새 compiler 구현/실행/독립 결정은 별도 현재 작업이다. Fresh reviewer는 이번 이론/구현을 작성하지 않은 역할이어야 한다. 새 review는 현재 diff/raw에 한정하고 이미 완료한83cohort와 donor를 재실행하지 않는다.

## Root 확장 소유권 후속 교정

ROOT_SCOPE_AND_ASSEMBLY_CONTRACT.md가 확정한 lead는 WU088_HH의 공통species/elementaryreaction compiler다. REI-CHEM-LEDGER-01은 역사적 중앙 staging 이름을 유지하며, REI는 scenario-specific event assembly 소비자다. 위의 초기 후보 선택·감사 기록과 THEORY/FROZEN_CONTRACT의 수학·scope·acceptance는 보존한다. 새 perrepo REPO_CHARTER/TASK_ASSIGNMENT/HANDOFF는 root 역할분담을 따르고 네 개의 구체REIexpanded PR contracts를 추가한다. 향후 실행budget은 모두null/unallocated이며 currentcompiler 별도승인만 유지한다.
