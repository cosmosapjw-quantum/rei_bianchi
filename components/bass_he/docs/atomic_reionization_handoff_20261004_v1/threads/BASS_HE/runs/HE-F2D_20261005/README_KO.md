# HE-F2D: 고정 S0 입력의 조건부 RCT exposure bound

상태: 새 bounded 연구 단위 완료. HE-F2/HE-F3 전역 완료, RCT activation, native mixed/stepper 실행은 아니다. 기준 S0는 RCT OFF를 유지한다. 원자율 변경과 source 재감사는 없다.

입력 BASS_HE be81c9587c15a976b1b0f42159e8680faf547cfb, 소비기 b553698a114fbff05640ab6ecb95d260410de492. 새 F07 scenario blob e97888b06c59d63acb0f35181163d256a6894ed6을 읽었다. nH0=1e-4 cm^-3, fHe=.083, t_end=1e13 s, FLRW H=(1,1,1)e-14와 Bianchi-I H=(1.01,.99,1)e-14는 동일한 trace lambda=3e-14 s^-1을 갖는다.

허용 fraction과 source-temperature domain을 유지하는 가상 KF96 상수 k=1e-14 cm^3/s 인스턴스에서

    J=integral R/nH dt=integral k*nH*fHe*(1-xHII)*yHeIII dt,
    0<=J<=fHe*Theta,
    Theta=k*nH0*t*phi(lambda*t), phi(z)=(1-exp(-z))/z.

Fraction 교대급수20/21차 enclosure와 위쪽 decimal 반올림으로 J<=7.17069589448e-7 events/H를 얻었다. 직접 He 분율 장부에는 J/fHe<=8.639392643943e-6이다. Q=40.819325400298 eV에서 직접 chemical 방출량은 <=0.000029270296906306 eV/H다. 이는 nominal prescription의 수학적 상한이지 실제 원자율 오차의 물리적 상한은 아니다.

두 배경은 같은 상한을 갖지만 실제 population/광자 궤적이 같은 것은 아니다. 직접 paired count에는 |JB-JF|<=Jmax만 따른다. 전체 ON/OFF 또는 FLRW/Bianchi 관측량 차이에 이 상한을 그대로 사용하지 않는다. baseline field의 실제 공통영역 안정성 상한이 추가로 필요하다. 직접 전자 forcing이0이어도 다른 반응의 되먹임을 통한 전자수 차이는0일 필요가 없다. 문서에는 bounded linear-feedback 반례를 포함했다.

정확 nH(t)를 사용하는 right endpoint 구적은 연속 exposure 이하, left endpoint는 이상이다. 임의의 양의 구적에는 연속 상한을 자동 이전하지 않는다. 실제 stage 장부는 Jdisc<=fHe*k*sum(weight*dt*nHstage)를 먼저 사용한다. 두-half 사건은 각 stage에서 정규화한 뒤 합한다.

고정 g=Q-Ebar의 직접 열 forcing만 분리하면 wR'+2Hmean*wR=g*j이고, |wR|<=|g|*6.46674018889e-7 eV/H이다. Ebar는 원자 모멘트로 공급되지 않았으며 source null은 유지한다. Ebar 상한 없이 escape energy 또는 냉각 절댓값의 유한한 상한은 없다. 이 forcing convolution도 전체 두 궤적의 온도 차이는 아니다.

이전 isolated RCT 함수 bytes를 그대로 재사용해 dimensionless reaction-clock Theta에 연결했다. 다른 반응/광자를 제거한 별도 기준계에서 Z_end=4.30241475263166e-8 events/H다. 합성 Ebar=Q에서 T_end=40936.53765 K이며 full S0 이력 실행은 아니다.

검증: 새6개 주 시험의 expected red 후 green, 최종13 tests PASS, 새 symbolic2식,80/120자리와 별도 구적/finite-node 합 대조. 최대 precision 상대차2.40237847336e-81. 유리수 상한은 exact Fraction 연산이고 mpmath 경로는 유한-input reference다. Rust0, 실제 S0/paired history0, consumer mutation0, 독립 과학검토 NOT_RUN.

F04는 이제 owner에서 completed이며 checker receipt는 SCOPED_STATIC_NUMERICAL_DOMAIN_PASS다. 과거 partial 문구를 현재 판정으로 재사용하지 않는다. 다만 fixed-density,20/35/70eV,dt1e9의 static map 인증은 expanding S0 또는 RCT 인증이 아니다. F04 전체를 재심사/재실행하지 않았다.

Git에는 이 요약, exposure_budget.py, 결과/입력/반환/다음지침을 보존한다. 전체 상세 유도, test_exposure.py, verify_exposure.py, 기존 함수의 정확 bytes, 유리수 분자·분모, source projection과 실제 red/green 로그는 BASS_HE_F2D_S0_EXPOSURE_20261005_v1.zip에 있다. 정확한 archive/cloud identity는 DELIVERY_RECEIPT.json을 따른다. source original JSON의 container 다운로드는 DNS 실패라 selected projection만 보존했으며 original bytes라고 부르지 않는다.

다음은 실제 RCT-STEP01/혼합 native 반환 또는 source/model/closure 변경이다. 이 상한만으로 RCT를 생략하거나 local/public-width gate를 통과 처리하지 않는다. 동일 상한을 다시 조이는 감사 루프는 새 과학적 필요가 없는 한 진행하지 않는다. HE-F3 WAIT_REI_F09_RESULT, HE-FLRW02B SEPARATE_PENDING, physical HOLD, Eq55 NOT_RUN, legacy PARKED_OPEN을 유지한다.
