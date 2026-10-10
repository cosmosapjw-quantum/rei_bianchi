# Source-to-code 정적 검토

검토자는 작성자 자신이며 독립 review가 아니다. compilation, cargo fmt/test, JAX/Rust parity, Rust 테스트의 red-green은 미실행이다.

원문 두 blob 전체가 지정 SHA와 일치한다. source-to-code 행 대응은 SOURCE_CODE_MAP.json에 있다. Rust export는 whitelist의 일곱 함수이며 보조 작업은 typed state/error/table/protocol와 coverage refusal이다. residual, rate fit, SciPy 최적화는 Rust에 이식하지 않았다.

PCHIP: coefficient fitting 없이 degree-major 배열을 보존하며 right interval과 마지막 knot를 구분한다. finite closed domain 밖과 nonfinite 입력은 새 API 오류다. Python 경계 polynomial 외삽과의 차이를 checker에서 intentional_api_restriction으로 기록한다.

Opacity: HI effective G1/G2a를 소유한 lowgroup에 atomic HI를 더하지 않는다. G2a에는 HeI만 추가하고 G2b/G3의 explicit species 합은 원문 그대로다. atomic 항은 proper cm^-3 * cm^2 * Mpc_cm/(1+z), 출력은 cMpc^-1이다.

Photon/gamma: RHS에는 c(1+z)/Mpc_cm와 redshift outgoing/인접 incoming을 사용한다. gamma는 N에 (1+z)^3을 한 번 적용하며 opacity table이나 state GammaHI를 읽지 않는다. scalar emissivity는 adapter에서 4회 broadcast할 뿐 source fraction을 재정규화하지 않는다.

Lift: finite prior 검사, total 검사, nonnegative 검사, zero-total과 zero-support의 순서를 보존한다. signed는 zero rate에서도 양의 support를 요구한다. finite 양수 합의 overflow를 무단 보존량 재투영으로 수리하지 않는다. nested inputs는 typed slice/protocol 경계에서 별도로 거부한다.

독립성: kernel은 입력 참조만 사용하고 전역 mutable state/cache가 없다. 네 named source-site 호출은 서로 다른 입력과 역순 재실행으로 검사하도록 구성했다. 이는 원 four-site enclosure를 이 library가 재현했다는 증명이 아니다.

잔여 위험: 수기 Rust 형식/타입/빌드 오류, JAX logistic/exp subnormal 및 FTZ, NumPy/JAX reduction order, OS libm 차이는 local 검증 대상이다. public API 존재 의도와 컴파일 성공을 구별한다. nominal physical 입력 domain 밖의 group arithmetic에는 새 physical validator를 넣지 않았으므로 물리적 적격성을 보증하지 않는다.

W0 verifier의 A6 manifest './' prefix 처리 오류를 수정했고 이전 실패를 W0_RESTORE_ATTEMPT_1.json에 보존했다. source archive bytes는 변경하지 않았다.
