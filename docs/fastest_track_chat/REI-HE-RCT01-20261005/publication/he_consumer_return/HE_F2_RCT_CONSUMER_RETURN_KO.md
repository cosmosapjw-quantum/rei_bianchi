# HE-F2: 구체적인 RCT 소비기 구현 반환

이 반환은 HE-F2가 기다리던 선택·provider·closure·실제 adapter를 제한된 연구 범위에서 제공한다. BASS_HE의 CURRENT_FASTEST_STATE/HE-F2/HE-F3를 대리로 완료 처리하지 않는다. 반환 JSON의 immutable REI publication commit/path를 확인한 뒤 그 changed contract만 intake하면 된다. 실제 소비기 code commit은 `41e4592aa494b48929dcd23fc8504c169a98a908`이며 packet 경로는 `docs/fastest_track_chat/REI-HE-RCT01-20261005/`다. 문서 commit은 별도 publication receipt로 결속한다.

원래 synthetic HHe baseline과 새 actual FT03 successor의 기본 RCT는 모두 OFF다. 명시적 연구 선택은 KF96 nominal을 primary profile로, GM25를 온도 공통구간의 대안으로 둔다. KF96의 더 넓은 nominal call window를 활용하는 코드 선택이며 물리적 우월성 또는 source 불일치 해소가 아니다. Common provider schema에 맞는 두 record는 pinned HE exporter 0.1.1에 실제 thermal_rate를 요청해 생성했다. Source scalar와 event-count view를 구분하며 동일 반응 대안을 합산하지 않는다.

실제 Rust API는 RctProvider 선택, events(count only), closed_events(Ebar 명시), combined_hhe_rhs, combined_ft03_rhs다. 새 typed FT03 wrapper는 actual ft03_rhs의 HG RR·CI 및 DR/kinetic baseline을 보존하고 별도 RCT 사건 ledger를 더한다. Ft03Model.gas의 alpha/beta=0을 원래 hhe_rhs에 넘기는 잘못된 shortcut을 사용하지 않는다. **이는 두 local RHS의 접속이며 두 implicit stepper에 RCT를 연결한 결과가 아니다.**

RCT는 HeIII+HI→HeII+HII+γ이며 proper event rate R=k nHI nHeIII를 소비기가 한 번 계산한다. 직접 자유전자 변화는0, 종 분율은 각 핵종 분모를 쓴다. CountOnly의 열·광자 에너지 moment는 미제공이다. 조건부 escape closure에는 caller-supplied finite positive Ebar를 요구하고 provenance class CALLER_SUPPLIED_NO_ATOMIC_MOMENT를 둔다. 정확한 값·시나리오 목적은 run manifest/CSV가 보존한다. Chemical −QR, thermal (Q−Ebar)R, escaped Ebar R이며 tracked primary groups에는 광자를 주입하지 않는다. Source spectrum/heat/recoil moment는 null, physical_admission=false다.

새 Ft03Model의 실제 guard는30000–110000 K다. 따라서 GM25는 해당 typed wrapper에서 source-domain error로 거절한다. KF96 범위가 덮더라도 physical/closure admission을 자동 부여하지 않는다. GM25/KF96 공통 sensitivity는 별도 1000–10000 K HHe 연구 모형에서만 수행한다. 이전 FT03 guard를 원래 synthetic HHe baseline에 적용하지 않는 것과 새 actual Ft03 guard를 지키는 것을 구별한다.

FT03의 원래 published representability 규칙인 nonzero-factor product-underflow 거절을 이번 RCT finite-point wrapper 검증이 전부 계승했다고 주장하지 않는다. RCT의 유한값 검사와 이번 표본 검증은 그 엄격한 binary64 표현가능성 계약의 인증이 아니다. 이 차이는 후속 실제 stepper 결속 시 affected numerical contract로 정해야 한다.

실제 native/Decimal70/독립 검토 판정과 source/binary identity는 반환 JSON의 evidence 경로를 읽는다. 초기104-test snapshot은 보존됐으며 concurrent FT03 추가 후 root의 final integration 결과가 최신이다. E2X는30001/50000/109999 K × Q−1/Q/Q+1의9개 조건부 사례와3개 GM25 거절을 수행했다. Synthetic Ebar는 원자 물리 예측이 아니다.

HE의 다음 행동은 이 explicit consumer implementation과 provider/closure records를 수신하여 **bounded local RHS binding**의 수락 범위를 기록하는 것이다. 미해결 physical source/moment, RCT time integration, 실제 cosmological sensitivity를 구별한다. 같은 원자율 suite나 cosmological campaign을 중복 실행하지 않는다. HE-F3는 여전히 REI-F09의 동일 paired campaign 반환을 기다린다. HE-L1/L2/L3, Eq55, HE-FLRW02B mixed-native gate는 이 반환과 별개로 보존한다.

최종 결속: Rust116개(기존84+동시FT03 8+RCT24), E2 12789 assertions/422calls, E2X212 assertions/12calls PASS. POST_FT03_REVIEW는 confirmed/open blockers0이다.
