# REI F4 passive transport: 제한적 적대적 물리·구현 감사

**검토 모드** 같은 작성 모델의 반례·한계 검사. `blind_referee_mode=SELF_ADVERSARIAL_ONLY`, 서로 다른 작성자 R6/C9 `NOT_RUN` 및 native agent `NOT_AVAILABLE`. 별도의 저자에 의한 동료심사 PASS로 부르지 않는다.

1. **확인된 defect: 구간 midpoint energy**. 처음 구현은 첫 흡수가 아주 이른 optically thick subcell에서도 중점 광자에너지로 흡수 에너지를 기록해 `W_redshift`를 과대평가했다. 광학적으로 일정한 subcell의 정확한 `λ/(λ+1)*(1-e^{-(λ+1)dx})` 흡수 에너지로 교체함. Wolfram 입자수·에너지·work 항등식 `{0,0,0}`. 테스트 `test_fixed_hazard_exact_toy_and_redshift`, `test_zero_opacity_expansion_only`.
2. **구현·입력 경계**. PR284 전체 ZIP 정확한 SHA, PR283 중첩 ZIP 정확한 SHA, 원래 BASS `H,n_b,Y,sigma_i` loader, 193×21 shape, 8492 original K event rows 및 `n_b∝a^-3` 확인. 비정상 음의 opacities reject. 방출 종료 시점 z=2에서 최초 흡수 확률이 0이어야 하며, 모든 193 source epoch `P0+P1+P2=1`, `S+∑P_i=2`, 출발 복사 에너지가 redshift+absorption+surviving 에너지로 분배됨.
3. **수치해석 우려: movable threshold**. 12개 원래 epoch에 대해 `Gauss16/time4`와 `Gauss32/time8`를 비교했을 때 최대 상대차는 He II 임계값 주변에서 약 1.642% (`z≈11.91`)였음. 그 시간의 절대차는 약 `7.98e-7` photon/pair이며 매우 작은 민감 채널이다. 따라서 He II 단일 에포크에서 고정밀 인증이나 전역 오차 ≤1%는 주장하지 않는다. 12점 검사는 전 193점 수렴 인증이 아님. 표의 1969 인쇄 OCR에 대한 체계적 미검증과 배경 보간 오차는 별도의 불확실성.
4. **대체 가설/반례: 잘못된 전역 스펙트럼 최적화**. 매 epoch마다 가장 극단적인 다른 스펙트럼을 선택한 후 적분하면 하나의 원자 2E1 스펙트럼이 전 시대에 적용되는 모델이 아니다. 실제 구현은 193 emission source weights를 더한 뒤 **하나의 공통** 20 generator family에서 최소/최대를 얻음. `positive` 조건은 `monotone`을 뜻하지 않으며 PR285의 양의 non-monotone hat가 단조성 도입에 대한 반례이다. Covariance와 TV는 비선형이므로 선형 generator extrema 판정에 사용하지 않는다.
5. **물리적 과장 반례: mean FLRW ≠ Bianchi I directional**. 광자 방향 redshift는 실제 비등방 shear에 의존할 수 있다. 현재 코드는 `E∝1/a`에 한정된다. 따라서 인과적 첫-flight kernel이더라도 full anisotropic radiation transport가 아니며 물리ical tau/CMB 검증이 아니다.
6. **source yield와 gas heating 부재**. `K_s=K−K_forced`를 100% singlet으로 놓은 조건은 비교 시나리오이지 실측 yield가 아니다. 새로 계산된 첫 흡수의 electron kinetic energy는 thermal deposition과 다르다. 실제 REI photo-heat port는 UNBOUND. Li 원자 복사 흡수로 발생한 이차적 ionization feedback 자체도 포함하지 않았다.
7. **보안/런타임 실패 분류**. parent PR285 원본 ZIP cloud `BACKUP_NOT_DONE`은 별도 source provenance blocker, 기존 full Rust `cargo fmt` 실패는 이 새 Python 연구 하위디렉터리의 과학 수치 검증과 별개. 이번 변경의 full repo CI 결과는 별도 원격 조회로 기록해야 한다.

**결론:** 조건부 고정배경 인과적 첫 광흡수 kernel과 그 시간/에너지 장부는 데이터 및 식 수준에서 구현·검산됨. Source-qualified full spin yield, original scan pixels, anisotropic angular ray, coupled thermal-ionization closure 부재로 F4/L4/production은 HOLD. R6/C9 different-author NOT_RUN.
