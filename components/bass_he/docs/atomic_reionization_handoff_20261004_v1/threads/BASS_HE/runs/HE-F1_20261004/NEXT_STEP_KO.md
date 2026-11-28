# 다음: HE-F2 소비기 계약 결속

HE-F1은 구현 범위에서 완료다. source 두 개는 자동 선택/합산하지 않는다. 기존 연구는 HE-L1/L2/L3 PARKED_OPEN.

다음 한 단위는 rei_bianchi가 실제로 저장한 REI_SCOPE_LOCK와 REI_PROVIDER_CONTRACT를 읽어
reaction_id, species_order, 단위, density multiplication 한 번, photon birth와 absorption의 구분을 결속하는 것이다.
이번 실행에서는 외부 두 계약의 최신 완료 여부를 판정하지 않았다. 외부 계약이 없으면 HE-F2만 blocked로 기록한다.
열·recoil·photonenergy null을0으로 바꾸지 않는다. MONO_Q_ZERO_PROMPT_HEAT_APPROX_V1 같은 closure는
rei_bianchi의 명시적 선택이고 scalar atomic rate의 파생결과가 아니다. 원자 API에 density/geometry/opacity를 넣지 않는다.

HE-F2 미완료는 optional REI-F09만 대기시킨다. REI-F08 baseline은 자기 scope에 따라 독립 진행한다.
HE-F3는 REI-F09의 같은-source paired FLRW/Bianchi 감도 결과를 한 번 소비·검토한다. HE에서 별도 campaign을 실행하지 않는다.
source-spread를 confidence interval로 바꾸지 않는다. 민감도/범위/필요 moment가 실제로 legacy trigger를 만들 때만 해당 경로를 연다.

현재 NCP64 scientific runtime는 필요 없다. 새이론설계·문헌전수검색·B5C3를 이 단계의 선행조건으로 만들지 않는다.
local Codex는 이 패키지와 고정 source/release를 소비할 수 있지만 미완료 과학 설계를 임의 완성하도록 맡기지 않는다.
