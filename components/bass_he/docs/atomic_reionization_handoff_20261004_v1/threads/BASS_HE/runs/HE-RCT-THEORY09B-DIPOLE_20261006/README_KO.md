# THEORY09B1: same-channel electronic source binding

FINITE_SOURCE_BINDING_AND_COVARIANCE_CHECKS_PASS__CONTINUOUS_SOURCE_OPEN. 09B의 유한 electronic 입력과 source 표현 결속을 완료했다. 실제 q=d*u_i와 산란/광자모멘트는 아직 계산하지 않았다.

## 회수한 실제 입력

기존 B5A/B5B1/B5B2/B5C/B5C2에는 동일1s_sigma/2p_sigma 전자함수와 signed z_lu가 있었다. B5C2 Drive archive 12588189bytes/SHA256 5d3450b04234bdc0b65e770ebdb142114fae4ce89ab158391fe60854aa24f5b7의 중첩manifest를 확인하고 57개 고유R(.125..10 a0)와56개 원래 물리 cross-R links를 결속했다. 새 eigen/root solve0, 예전 scientific suites0이다. PDF나 private ancestor ZIP은 재배포하지 않는다.

R2를 root로 모든 링크가 연결되며 원(+1,+1) phase와 음의 signed coordinate dipole를 보존했다. 마지막 저장 quadrature에서 norm을 나눈 최소대각overlap=.9867038893553712다. finite graph 진단이지 연속gap/정확도 인증이 아니다. 원 R1->.75 실패와 이후 명시적 A1 경로도 보존한다. L angular coupling이나 다른 molecular dipole를 대신 쓰지 않았다.

## 새 이론적 결속

ZA1/ZB2 clamped one-electron Hamiltonian의 에너지는 핵반발을 제외한다. x=R/a0에서 V_i/Eh=e_u+1/2+2/x, V_f/Eh=e_l+2+2/x, Q_BO/Eh=3/2이므로 Q_BO+V_i-V_f=Eh(e_u-e_l)다. 57점에서 exact dyadic input 변환을 확인했다.

NIST2022 Eh/eV=27.211386245981(30)를 쓰면 Q_BO=40.8170793689715eV다. 소비기 threshold 차40.819325400298eV와의 차는 .0022460313265eV,relative5.50267525561223e-5다. 기존 V들을 두고 Q만 교체하면 상대표면 shift라는 별도 모형이다. 단순 공통 에너지 원점 변경이 아니다. 원소비기의 synthetic closure가 틀렸다고 판정하거나 threshold를 수정하지 않았다. finite-mass/QED 원인이나 보정도 이번에 확립하지 않았다.

물리전기쌍극자는 정확orthogonal상태에서 d=-e*z_lu다. midpoint total D=eR/2 I-ez, 원점b 이동에서는 D_new-D_old=-2eb I이므로 finite overlap O에서 transition차=-2ebO다. 원 norm/state계수를 유지한 R.125/2/10의128/160quadrature,3원점에서18결과를 확인했다. 최대변환잔차3.185737128569119e-17 e a0이며 true dipole error bound가 아니다.

phi_a->exp(i theta_a)phi_a일 때 u_a->exp(-i theta_a)u_a, d_fi->exp(i(theta_i-theta_f))d_fi, q_f->exp(-i theta_f)q_f다. tau_a=<phi_a|d_R phi_a>, nabla_a=d_R+tau_a와 nabla_fi d=d'+tau_f d-d tau_i를 사용하면 source Leibniz와 핵Hamiltonian의unitary covariance가 성립한다. H_f/P_E/q를같이변환해야spectralmoment가불변이다. 연결변화만을위해새비단열물리보정을삽입하지않는다.

H=[[1,-1],[-1,1]],S3,q=(1,1)의finite반례에서q만(1,-1)로바꾸면동일|q|²에도평균3->1이다. H도같이변환하면원모멘트가복원된다. 실제회수node의d는모두한부호라abs가node상globalphase와같다. 실제He에서부호bug가있다고주장하지않는다. node사이/꼬리의부호는미인증이다.

전자 full-H residual에는 Delta*z_lu-(hbar²/me)<l|d_z|u>=<r_l|z|u>-<l|z|r_u>가성립한다. 작은L/V차만으로unbounded-z참해오차를인증하지않는다. compactI에서 ||q-qtilde||<=||d-dtilde||inf||u||2+||dtilde||inf||u-utilde||2이고tail과potential-operator오차는별도다. 57node일치만으로uniforminterpolationerror를보장하지않는다.

## 실제 실행과 다음

새verifier1회exit0: SymPy19groups/21scalars,57exact input threshold checks,6physical-field quadratures/18origin cases,합성반례3개. tests-after이며independent scientific review/intervalcertificate아니다. recovery첫KeyError는rootpacket의R/convention이state아닌request수준에있던schema차이로,원bytes를고치지않고adapter만수정했다. 실패로그를보존했다.

전체report/raw57nodes와sourcehashes,원receivedreports,실행verifier는 BASS_HE_RCT_THEORY09B_DIPOLE_20261006_v1.zip에 있다. Git은요약/계약/결과/선택node와verifieridentity를보존한다. 다음THEORY09B2_CONTINUOUS_CURVE_AND_NUCLEAR_SOURCE_ERROR는이미회수한field를재사용해R구간/보간/inner-outertail와실제입사u_i를결속한다. 현재source photon/heat/recoil=null,baselineRCTOFF,HE-F2globalfalse,HE-F3/F09blocked,physicalHOLD를유지하고기존addon채택의새필수gate를만들지않는다.
