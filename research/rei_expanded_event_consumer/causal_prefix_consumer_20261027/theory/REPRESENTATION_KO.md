# R4 표현 선택과 판별 예

초기 photon-moment 후보는 GRID044를 에너지 격자로 읽는 오류가 확인되어 중단했다. GRID044는 history 식별자다. 새로 게시된 CR108의 실제 cumulative intervals가 있으므로, 동일 prefix를 공통 변수로 보존하는 표현을 채택한다.

예를 들어 F_0=0, F_1∈[1,2], F_2∈[3,4]이면 독립적으로 만든 두 bin enclosure는[1,2]와[1,3]이다. 두 enclosure를 더하면[2,5]지만 동일 F_1가 telescoping하는 총량은 F_2−F_0∈[3,4]다. 원인은 내부 경계 F_1의 한 값을 감소항과 증가항에서 독립적으로 선택했기 때문이다. 실제 코드에서는 각 source마다 같은 latent chain을 유지한다.

정규화 endpoint 목표 F_b/b_b−F_a/b_a는 두 endpoint의 선형 함수다. 두 변수의 feasible rectangle과 x≤y를 교차시킨 polygon의 vertices로 범위를 구한다. [0,1]×[2,3]처럼 겹치지 않는 두 interval에는 diagonal vertex가 없다. 가짜(2,2)를 추가하면 최소 gap1을0으로 잘못 낮추므로 이 예를 판별 대조에 둔다.

공통 N/E의 선형 event map은 charge 및 energy 보존을 직접 강제한다. Reservoir별 marginal interval의 상충 corner를 선택하는 방식과 구별할 수 있다. scalar sharpness, source-free normalization fixture, actual source qualification을 각각 명확히 구분한다.

