# 게시 직전 동시 업데이트와 RCT 영향

2026-10-05 KST에 진행 중인 RCT 구현 검증 뒤 moving branch가 전진했다. 이 단계는 changed source/docs의 읽기와 identity 확보만 수행했다. native 코드 mutation, 새 과학 계산·시험 및 원격 쓰기는 이 intake에서 수행하지 않았다.

| 저장소 | 새 commit | tree | 범위 |
|---|---|---|---|
| rei_bianchi | 6279036f06c9ba4d47574beab90b48fc2c6f9ba7 | 3e631a556dada073e6973dd3ae3b4ab3d37ec700 | FLRW03 chat reference, actual FT03 successor 및 F04 partial 반환 |
| BASS_HE | e4d2753ea45593ade6c3fd3a7fea81f92cfd1a15 | 3afc07c63e9a1f107fdc467387c5946d2af69526 | mixed-HHe absorption reference/late sync 문서6개; RCT provider source 불변 |

REI는 intake pin ccbc15019296b9128a90fa45b9c68c7daddc7b77 이후2 commits, HE는21d5b8075429903d195d6e0e0c24a10c00b21063 이후3 commits다. 전체 changed path는 `FINAL_DELTA.json`에 기록했다. 관련 파일15개를 exact source로 확보했고 `FINAL_DELTA_IDENTITY.json`에서15/15 Git blob 일치를 확인했다.

## 실제 Rust 변경

REI는 `src/ft03_controlled.rs`, `src/ft03_rates.rs`, `examples/ft03_fixture.rs`, `tests/ft03_controlled.rs`를 새로 추가하고 lib.rs에7줄의 module/export를 추가했다. `hhe_events.rs`, `atomic_provider.rs`, `microstep.rs`, `thermal.rs`와 FLRW pointwise source는 변경하지 않았다. 새 파일5개의 정확한 bytes는 `final_delta/rei_Rust/`에 crate-relative 경로로 제공했다. 이5개를 검색한 결과 include_str/include_bytes/File/read_to/env/CARGO_MANIFEST 등의 외부 입력 경로는 없고 새 FT03 tests는 inline reference literals를 사용한다.

게시할 때 최신 tree를 parent로 하고 기존 FT03 파일을 그대로 보존한다. RCT의 이전 lib.rs 전체를 덮으면 FT03 module/export를 잃는다. 최신 lib.rs에 RCT public module export를 추가하는 작은 병합이 필요하다. 병합 후 전체 crate build context가 달라지므로 root가 새 scope의 integration check와 source/binary binding을 별도 기록한다. 이전104-test receipt는 당시 source evidence로 보존하고 결과를 소급 변경하지 않는다.

## 새 Ft03Model의 중요 차이

`Ft03Model`은 public `gas: HHeModel`을 포함하지만 controlled constructor에서 gas.alpha_cm3_s와 gas.beta_cm3_s를0으로 둔다. 실제 `ft03_rhs`가 EOS 온도를 읽어 HG RR·CI 및 두 DR 항과 kinetic moments를 재계산한다. 따라서 **combined_hhe_rhs(&ft03.gas,...)는 Ft03 baseline을 계산하지 못하며 RR/CI/DR를 누락한다.** 현재 RCT 모듈이 원래 HHeModel local RHS와 연결됐다는 검증을 새 Ft03 integration 검증으로 옮기면 안 된다.

새 actual Ft03의 temperature guard는30000–110000 K다. 원래 HHeModel synthetic baseline에 과거 FT03 guard를 이월하지 않는 판단과, 새 Ft03Model에 guard가 실제 존재하는 사실은 양립한다. GM25의200–10000 K 창은 새 Ft03 guard와 겹치지 않는다. KF96 nominal 창은 덮지만 그 사실만으로 physical rate/moment admission은 없다.

다음 RCT-STEP01은 actual target stepper를 먼저 고정해야 한다. Ft03를 target으로 선택하면 `RctProvider.closed_events(&ft03.gas,state,closure)`의 RCT ledger를 **actual ft03_rhs**에 명시적으로 합성하고 FT03 stepper/thermal residual/accepted integrated event에 동일하게 연결한다. FT03의 RR kinetic·DR moments와 기존 closure는 보존한다. 원래 controlled HHe target이면 기존 local 검증과 같은 baseline임을 기록한다. 두 source sensitivity를 위해 새 Ft03의 온도를 임의로 낮추거나 GM25를 외삽하지 않는다.

## F04, FLRW03 및 HE 후속 상태

새 `runtime_inputs/ft03_successor_binding.json`은 actual controlled successor implemented를 선언하지만 interval certificate not completed를 함께 명시한다. `runtime_returns/REI-F04.json` state=partial, full_F04_completed=false, scientific admission=HOLD다. 새 pointwise/stepper implementation과 균일 parent/root/J/H/Taylor certificate를 구별한다. 기존 strict local<2e-4, public width<2e-3, [160,161] FAIL=2.1245050576368385e-4, tick160은 유지된다.

동시 FLRW03 연구는 팽창 중 사건수/H 적분에서 각 stage의 nH(t)를 써야 한다는 계약, source photon birth 시각과 redshifted energy, threshold exit·흡수·energy/work ledger를 제공했다. scoped reference 결과이며 해당 chat runtime의 native 실행은0이었다. 다음 chat task는 REI-CHAT-FLRW04_EVENT_WEIGHTED_CONSUMER_CONTRACT로 외부 F04 certificate와 별개다. 이번 local RCT 결과도 그 integrated cosmological gate를 닫지 않는다.

HE-FLRW02B는 finite mixed-HHe reference와 conservation projection의 nullspace를 검증했지만 owner mixed-native gate는 여전히 pending이다. 기존 pure-H/FLRW 전체 suite 수신을 이 mixed gate의 완료로 쓰지 않는다. HE의 최신 문서에서도 HE-F2는 WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT, HE-F3는 WAIT_REI_F09_RESULT, RCT는 기존 consumer scope에서 EXCLUDED다. 이번 새 RCT packet은 별도의 changed-contract intake 자료이며 HE state를 이 스레드가 대리로 완료 처리하지 않는다.

원자 provider core/packets에 변경이 없으므로 기존 선택·source identity·nominal-rate 검증은 재사용할 수 있다. publication/backup은 root의 새 immutable commit/receipt로 닫으며, 이 intake가 원격 게시 성공을 주장하지 않는다.

## Changed-input 구현 후 실제 반환

위 intake에서 찾은 Ft03Model.gas shortcut 문제를 해결하기 위해 root/native owner가 actual ft03_rhs를 부르는 typed combined_ft03_rhs를 추가했다. 이는 이 read-only intake의 실행이 아니라 별도 사전등록 `research/CONCURRENT_FT03_ADAPTER_PLAN.json`에 따른 구현이다. 최종116 native tests, E2 12789검사/422호출, E2X212검사/12호출이 PASS이며 추가 독립 review도 confirmed다. 기존104-test snapshot과 최초 review는 보존했다. 최신 native publication은41e4592aa494b48929dcd23fc8504c169a98a908이다. 두 implicit stepper의 RCT 연결과 FT03 underflow representability 계약의 RCT 계승은 여전히 미수행이다. 따라서 위의 local-composition 권고는 현재 구현되었고 다음 bounded node는 actual Ft03 time-stepper 결속이다.
