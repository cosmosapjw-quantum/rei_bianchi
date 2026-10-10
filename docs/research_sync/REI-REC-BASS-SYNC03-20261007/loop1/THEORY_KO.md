# 실제 F08 → BASS 가시도 소비 계약

원본 F08 exporter가 제공한 고유 전자밀도 `ne_proper_cm3`를 사용한다. 단위 변환은 `ne_m3=10^6 ne_cm3` 한 번이며 이미 proper인 밀도에 `a^-3`를 다시 곱하지 않는다. 실제 BASS `ElectronState::scattering_rate_per_normal_second`는 `q=c sigma_T ne D`를 반환한다. 이 입력은 normal-time, zero-tilt이고 `D=1`이 확인된다. BASS 상수는 `c=299792458 m/s`, `sigma_T=6.6524587e-29 m^2`이다.

종별 분율은 이 export에 없으므로 `ElectronState(ne_m3,0,1,0,0)`를 aggregate density의 대수적 용기로만 쓴다. 실제 기체가 순수 수소라는 해석이나 원본 분율 재구성은 하지 않는다. 실제 코드가 반환하는 q를 별도 Decimal 식과 대조한다.

각 endpoint q 사이를 선형으로 보간한 *명시적 이산 함수*의 셀 적분은 `delta_tau_i = (t_(i+1)-t_i)(q_i+q_(i+1))/2`이다. 이를 BASS의 상수 셀 `qbar_i`에 전달한다. 두 표현의 endpoint 광학깊이와 셀 전체 probability는 같지만 셀 내부 순간 가시도 높이는 같다고 주장하지 않는다.

유한 구간 뒤의 observer tail을 `b`라 하면 `tau_i=b+sum_(j>=i) delta_tau_j`, `S_i=exp(-tau_i)`, `P_i=S_(i+1)-S_i`이다. 따라서 `S_0+sum(P_i)=exp(-b)`이며 유한 구간 확률을 1로 재정규화하지 않는다. 기본 `b=0`은 선언한 유한구간 benchmark 경계이며 실제 우주 observer tail을 추정한 값이 아니다. 추가 `b=0.1`은 공통 tail에 따른 `exp(-0.1)` 비례성을 확인하는 별도 진단이다.

Decimal 70자리 검산은 native 구현을 호출하지 않고 원본 시간·밀도의 binary64 값을 정확히 올린 뒤 위 식을 계산한다. 따라서 독립적인 산술·수신 계약 검증이지만 원본 REI 화학의 독립 검증은 아니다. endpoint conditional enclosure도 이산 endpoint 함수에 대해서만 사용하며, 시간 사이 궤적이나 연속체 해의 bound로 승격하지 않는다.

동일 normal-time 구간의 BI–FLRW 차이는 두 화학/팽창 이력의 차이다. zero tilt의 국소 scalar opacity만으로 fixed-redshift 방향별 이방성을 만들 수 없으며 실제 ray/redshift mapping은 별도 필요하다. finite-temperature electron tail, polarized redistribution, full BASS build, 생산 solver 배선은 이 연구의 완료 범위 밖이다.
