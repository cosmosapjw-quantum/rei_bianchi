# 다음 이론 단위: HE-RCT-THEORY09_PROJECTED_CONTINUUM_REALIZATION

이번 THEORY08은 E1/BO/lowest radiative order에서 sigma_1의 spectral operator와 flux/continuum normalization, local-gap 오차 분해를 닫았다. 실제 He moment 값은 null이다. 같은 39항등식이나 기존 빌드/복구/native/ODE를 단순 인계 때문에 반복하지 않는다.

읽기: REPORT_KO.md 2–7절 → THEOREM_CONTRACT.json → evidence/run01/RESULTS.json. 물리적 source 숫자가 없는 finite example을 실제 spectrum으로 승격하지 않는다. Bound final channel은 존재할 경우 association이며 RCT에 섞지 않는다. Final He+–H+ continuum의 repulsive Coulomb normalization을 지킨다.

다음은 실제 V_i(R),V_f(R),d(R),threshold/mass/source accuracy/유효구간을 기존 electronic lane 또는 원전 자료에서 결속하는 것이다. 입사 real scattering state와 최종 projected continuum overlap 또는 driven outgoing resolvent 중 한 경로를 선택한다. 동일 숫자가 다른 lane에 있어도 source/scenario identity가 맞기 전 자동 채택하지 않는다.

sigma_0와 sigma_1을 동일 state/channel/normalization에서 얻고, endpoint e=0,S,partial-wave tail,R matching,resonance와 spectral discretization/finite broadening 오차를 각각 기록한다. 실제 source-bound local error norm을 계산하기 전에는 A(R)*Delta(R) approximation의 정확도나 평균 열부호를 판정하지 않는다. 약한 방출 조건이 공명에서 깨지면 lowest-order 결과와 optical dressed calculation을 섞지 말고 필요한 확장을 별도 단위로 고정한다.

재현: `python -B -W error research/verify_spectral.py --output /absolute/new/results`.
Python/SymPy/mpmath만 사용하며 output은 반드시 새 경로다. 원 evidence를 덮어쓰지 않는다. 이것은 finite mathematical verifier이고 실제 He scattering 실행이 아니다.

기존 add-on의 owner 채택에는 추가 선행조건을 만들지 않는다. HE-F2 global false,HE-F3/F09 blocked,baseline RCT OFF,source moments null,physical HOLD,Eq55 NOT_RUN,legacy PARKED_OPEN은 유지한다.
