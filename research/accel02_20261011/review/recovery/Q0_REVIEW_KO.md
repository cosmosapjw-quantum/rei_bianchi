# Q0 source·초기 UVB 오차 귀속: 범위 한정 독립 검토

**Q0의 단위·정규화·native knot 처리와 source-only 오차 진단은 채택할 수 있다.** 완료된 EVENT003 spectral FAIL 판정을 변경하지 않는다. 새로운 물리 적분이나 native RHS/SIGMA를 실행하지 않았다.

proper source는 epsilon_nu (1+z)^3 / (Mpc^3 h), UVB photon density는 4 pi J_nu / (c h)이다. 각각 dlnE당 angle-integrated 값이다. E를 eV로 평가한 1차 moment에 1.602176634e-12를 곱하면 erg로 변환된다. FLRW에서는 R=1/a_rel이므로 reference-volume source는 proper source의 a_rel^3배다. 이때 comoving-to-proper 변환을 중복 적용하지 않았다. 초기 a_rel=1이므로 초기 UVB의 proper/reference density는 같다.

원 literal table을 독립 파싱했다. native log-E 구간의 0차 moment는 정확한 trapezoid로, 1차 moment는 각 구간의 별도 16점 Gauss로 평가했다. 중복 에너지의 zero-width jump 구간만 적분에서 제외하고 양쪽 ordinate를 평균하지 않았다. 초기 UVB 8개 moment와 4개의 source epoch에서 32개 moment를 대조했다. Q0와의 최대 상대차이는 초기 UVB 3.396e-15, 선택 source 7.803e-16이다. 이 검토는 4개 source epoch의 bounded arithmetic check이며, 129개를 모두 독립 재적분했다는 뜻이 아니다.

따라서 256-grid 초기 full-band photon-number의 +17.3215% 차이는 Q0 단위 오류로 설명되지 않는다. 이를 독립적인 disjoint band 합으로 분해하면 10–13.6 eV 부분의 차이가 exact full-band number의 +0.1732150이다. 다른 세 ionizing band의 기여는 합쳐 약 -3.05e-7이다. 즉 큰 full-number 오차는 대부분 HI threshold 아래 광자에 있다. 이를 17.3% ionizing-photon 오차나 같은 크기의 gas-heating 오차로 해석해서는 안 된다.

Q0에서는 max|sampled-exact| / max|exact|를 각 65/129 epoch 집합에서 별도로 사용한다. 공식 spectral 128/256 비교의 fine-grid amplitude 정규화와 교환하지 않았다. 이것은 고정된 table interpolation에 대한 source 및 initial-field quadrature 오차 귀속이며, 가스 피드백과 무관한 입력 quadrature 오차가 있음을 직접 보인다. evolved Gamma/ionic fraction/temperature 차이의 기여율이나 독점적 원인을 확정하지는 않는다.

다음 수정은 새 quadrature를 source·photon·gas·counter의 같은 operator에 반영해야 한다. 진단값만 수정하거나 누적 source counter만 정확한 moment로 갈아끼우는 것은 허용되지 않는다. 현재 Q0는 repair 구현이나 새 trajectory가 아니므로 보존·시간·spectral 허용 기준 및 CR/RCT 미완료 상태는 그대로 유지한다.
