# 다음 이론 단위: HE-RCT-THEORY08_SPECTRAL_FIRST_MOMENT_OPERATOR

현재 단위의 보고서 2–7절은 exact same-source kinetic assumptions 아래의 직접 유도다. 실제 source photon/heat/recoil 값은 미결이다. 같은 moment identity·합성12경우·기존 빌드/복구 suite를 단순 수신 때문에 반복하지 않는다.

다음은 West의 입사·출사 continuum Hamiltonian과 dipole로부터 energy-weighted radiative kernel 또는 sigma_1(E)를 정식화하는 이론 작업이다. 총 optical loss에서 자동으로 분광 first moment를 추론하지 않는다. Local Delta E(R) photon 가정은 별도 근사로 표시하고 completeness/continuum support/normalization과 오차를 확인한다. 실제 potentials/dipole/scattering payload가 부족하면 형식 유도와 numerical evaluation을 구별한다.

보고서의 상수율 표는 exact surrogate의 예시이지 KF96 physical slope를 인증한 것이 아니다. 실제 rate slope나 온도별 enclosure가 제공될 때에만 source-bound 수치 상계로 적용한다. GM25/KF96를 같은 cross-section law의 다른 온도 점처럼 혼합하지 않는다. 소스 모멘트 null,baseline OFF,physical HOLD와 기존 HE-F3/F09 차단을 유지한다.

재현은 패키지를 새 디렉터리에 풀고 `evidence/RESULTS.json`만 별도 새 위치로 옮긴 뒤 `python -B -W error research/verify_moments.py`를 실행한다. 원 정식 evidence를 덮어쓰지 않는다. SymPy1.14.0/mpmath1.3.0을 사용했고 Rust는 필요 없다. 기존 결과의 미소 quadrature 잔차를 interval certificate로 쓰지 않는다.

이 이론 연구는 기존 STEP01–06 add-on의 채택에 새 필수 gate를 추가하지 않는다. 실제 consumer/root/dispatcher는 이번에 변경하지 않았다.
