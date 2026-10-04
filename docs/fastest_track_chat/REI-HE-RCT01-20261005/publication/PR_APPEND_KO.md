
## He RCT 선택·provider·조건부 closure 연구 루프

현재 H/He baseline에는 RCT channel이 없고 HE atomic offer도 실제 소비기 계약을 기다리고 있었다. 이 묶음은 원래 OFF baseline을 보존하면서 KF96 nominal 또는 GM25 constant 중 하나를 명시적으로 선택하는 provider와 사건수 ledger, caller-supplied escaped mean photon energy에 따른 조건부 RHS 연결을 분리한다.

KF96 경로를 기본 bounded profile로 잡은 이유는 nominal temperature call window가 넓기 때문이다. 물리적 정확도가 더 좋다는 주장은 하지 않는다. GM25와의 sensitivity는 공통 1000–10000 K에서 별도 run으로만 비교하며, 두 source를 합산하거나 자동 전환하지 않는다. 원자 공급기의 unresolved spectrum/heat/recoil moment는 null로 남긴다.

Common provider record는 pinned HE exporter의 실제 thermal_rate view로 생성했고 event-count view와 분리했다. 조건부 closure는 chemical −QR, thermal (Q−Ebar)R, escape Ebar R이며 현재 tracked groups에는 RCT photon을 주입하지 않는다. 정확한 native/독립 검증 결과와 변경 source identity는 본 묶음의 실제 evidence 및 review receipt를 참조한다.

이번 범위는 local number/RHS/conditional energy ledger이다. 기존 production microstep, endpoint thermal solve, integrated event ledger는 후속 DAG의 RCT-STEP01에서 연결한다. 물리적 source admission, spectral transport, F04 certificate, REI-F09 cosmological application closeout은 완료 주장에 포함하지 않는다. 원래 atomic lanes와 기존 실패 gate를 유지한다.

검증: Rust full suite116개(기존84+수신FT03 8+RCT24), independent decimal70 검사12789개/422 native calls가 통과했다. 실제 source identity와 명령/종료코드는 evidence/FINAL_INTEGRATION.json, 세부 오차/음성 대조군은 evidence/INDEPENDENT_RESULT.json에 있다. 독립 semantic review는 confirmed, open blockers0이며 review/FINAL_REVIEW.json에 별도로 보존한다.

게시 직전 actual Ft03 successor가 추가되어 lib.rs exports와4개 upstream 파일을 보존했다. Typed combined_ft03_rhs는 actual HG RR/CI/DR baseline을 보존하며 RCT만 합성한다. E2X212 assertions/12native calls(9closed+3GM25거절) PASS, 추가 독립 검토 POST_FT03_REVIEW confirmed. 두 implicit stepper는 아직 RCT와 연결하지 않았다. Native code commit:41e4592aa494b48929dcd23fc8504c169a98a908.
