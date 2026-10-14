# He RCT bounded independent review

판정: **confirmed**. 확인 범위는 명시적 provider 선택, scalar event ledger, 외부 평균 광자에너지로 닫은 조건부 escape closure와 기존 HHe local RHS의 opt-in 합성이다. 열린 blocker는 0개다. 새 물리적 원자율의 정확도나 production stepper를 승인한 판정은 아니다.

반응은 HI+HeIII → HII+HeII(1s)+γ이며 전자 재결합과 달리 free-electron collision source가 0이다. 핵수·전하 보존, 서로 다른 H/He 분율 분모, Q=χ_HeII−χ_HI, signed heat=(Q−Ebar)R 및 chemical+thermal+escape cancellation을 실제 코드와 독립 수치 기록에서 확인했다. CountOnly는 missing moment를 숫자 0으로 채우지 않으며, escape closure도 photon spectrum·recoil/momentum을 예측하지 않는다. 기존 전역 기본값은 OFF이고 기존 과학 소스는 변경되지 않았다.

실제 검증 증거는 변경영역 Rust 20개, 전체 작은 crate 104개(기존 84개 포함), Decimal70 독립 assertion 12,789개다. 독립 runner는 native를 422회 호출했고 96개 provider–state 조합에 네 모드를 적용한 384행을 기록했다(CountOnly 96행, closed 288행). event-rate scaled error 최대 2.924×10⁻¹⁶, fraction 3.438×10⁻¹⁶, closed-energy residual 1.068×10⁻¹⁶이며 사전 허용치는 2×10⁻¹²다. Assertion 수를 독립 물리 시나리오 수로 해석하면 안 된다.

초기 계약 불일치 두 개는 해결되었다. Ebar=0은 실제 단일광자의 에너지로 허용하지 않고 생성자와 시험에서 거절한다. Closure의 native origin class는 CALLER_SUPPLIED_NO_ATOMIC_MOMENT이며, 정확한 값과 synthetic scenario는 외부 run manifest/CSV가 기록한다. 값의 provenance와 물리적 정확도는 구별된다.

KF96/GM25의 17배 차이는 source alternative 간 미해결 차이다. 두 출처는 합산되지 않으며 범위 밖 온도는 clamp·자동 source switch 대신 error다. Native metadata의 supplier commit/blob identity, 실행한 네 source 파일·binary·oracle 여섯 SHA를 실제 byte와 대조했다. 전체 검토 파일 31개의 SHA는 FINAL_REVIEW.json에 고정했다.

처음 probe가 컴파일되지 않은 원인은 JSON 출력 format string의 닫는 중괄호였다. 수정 후 build/실행이 통과했고 실패 로그를 보존했다. 이는 구현 보조 코드 오류이며 물리 오류나 실행환경 장애로 분류하지 않는다. 첫 unresolved-import 로그는 구현 전 기능 부재의 예상 실패이며 별도로 기록되지 않은 exit code를 추정하지 않는다.

이번 검토는 scientific suite를 재실행하지 않고 실제 source, test, root execution log와 oracle를 읽어 한 번 닫았다. 미수행인 것은 RCT time stepper, integrated accepted event ledger, Jacobian/positivity, 실제 spectrum/heat moment, KF96–GM25 불일치 해소, F04와 실제 EoR history다. 해석 trajectory vector는 후속 검산용으로 준비된 값이며 이번에 trajectory 구현이 실행되었다는 뜻이 아니다. 원격 게시/백업 확인은 root의 별도 delivery receipt가 소유한다.
