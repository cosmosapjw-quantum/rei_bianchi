# RCT03E7: source-bound 소비자 후처리와 조건부 오차 계약

PINNED_OPT_IN_CONSUMER_EXPORT_AND_CONDITIONAL_ERROR_TRANSFER_VERIFIED__REMOTE_ADOPTION_AND_TRUE_ERROR_OPEN.

E6 다음 지침 중 consumer 후처리 경로를 구현했다. load_attachment/export_for_consumer/consume_export는 명시적 endpoint 선택 시 현재 locked E6 N384/P512/H4/Q4의 OFF/KF/GM 결과를 내보내고 수신 검증한다. 기본 disabled는 입출력 0이다. RCT mode와 observer opt-in은 별개이며 자동 활성화하지 않는다.

1155행을 실제 export/consume했고 3465 rate +2310 observer inventory binary64 값 및 1155 clock가 E6와 동일하다. 원 producer Gamma/N/E/누적 장부는 불변이다. 출력은 endpoint_rates.csv와 최종 READY.json이다. 예상 mode/history/config/rate product의 해시·행·시각을 검사하고, 미완성 READY, 다른 mode, 변경 source, 누락 시각을 거절한다. 자동 fallback/보간은 없다. 원 receiver나 live native API를 변경한 것은 아니다.

새 직접 유도는 고정 positive measure에서 n/sigma/f의 명시적 box를 Gamma 상하한으로 전달하는 식과, uniform cell rate/H 오차를 노출량 integral Gamma/H ds로 전달하는 식이다. 실제 source/fit/quadrature/uniform-time 오차는 null이다. E6 finite-refinement 비를 물리 오차반경으로 변환하지 않는다. 전제가 없으면 MissingPremise다.

합성 3-node box 4개/512 corner와 기호 6식을 확인했다. 실제 GM 최종 2440 node를 중심으로 가상의 relative radii f=1e-6, sigma=2e-6, n=3e-7을 대입하면 상향 relative bound=3.3000029000006e-6이다. 반경은 검산 가정이며 actual atomic uncertainty가 아니다. 노드 사이 sin² bump는 같은 endpoint 값에도 exposure가 달라질 수 있음을 보여준다. 같은 ODE의 또 다른 해라고 주장하지 않는다.

새 Python 22시험 통과. 초기 18 scaffold 오류와 수신단 4 scaffold 오류를 보존했다. 초기 파일닫기 warning은 수정했다. toolchain 추출의 45/120초 timeout 때문에 partial Rust는 실행 불가였으며 새 native/coupled 과학실행은 0이다. E7 Python 후처리와 합성 검산은 실제 성공했다. 원 E6 527 payload는 불변이다. 코드 게시의 빈 줄 하나는 AST 동일성과 최종 22시험을 확인한 형식 변경이다.

Git에는 실제 Python 두 core와 계약/입력/source identity를 보존한다. 전체 실행 데이터, 22시험, 유도, 소비자 출력과 실패/성공 로그는 DELIVERY_RECEIPT의 ZIP에 있다. Git checkout만으로 raw data가 있다고 가정하지 않는다. ZIP의 data 경로를 --data로 제공한다.

실행: python -B code/consumer_rates.py --data EXTRACTED/data --readout endpoint --mode GM --output NEW_DIRECTORY.
수신: consume_export(NEW_DIRECTORY, EXTRACTED/data, 'GM').

baseline RCT OFF, atomic moments null, physical HOLD, HE-F2/F09 global OPEN과 remote owner 채택 OPEN을 유지한다. 새 Gamma의 solver feedback과 새 모형은 별도 선택이다. 기존 source-free 조건부 수락에 새 원자이론을 선행 gate로 붙이지 않는다.
