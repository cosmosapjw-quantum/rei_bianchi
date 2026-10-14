# FT05: Bianchi-I 방향 수송과 에너지 회계

상태: SCOPED_TRANSPORT_INTERFACE_AND_LIGHT_REFERENCE_CLOSED__PRODUCTION_AND_PHYSICAL_ACCURACY_OPEN.
다음 ready node: REI-CHAT-FT06_PAIRED_SCIENCE_SPEC. FT04는 actual Rust residual/site/box parent가 있을 때만 연결한다.

읽기 HEAD: 64bc3aa0871bb324817afd3d36db018dd34181cf. 시작, 연구 단계 경계와 게시 직전 live ref 모두 동일했다. lib.rs, group_rates.rs, coverage.rs를 해당 commit에서 직접 읽었고 mounted archive 파일과 Git blob identity가 일치했다. 기존 4-group scalar-redshift API 및 fail-closed physical source gate는 수정하지 않았다.

## 재현 패키지

- REI_CHAT_FT05_20261004.zip: 93448 bytes, 57 entries, 55 manifest payload files.
- SHA-256: 910f6a54e0595b51338b32bbbc16e45f4d53a14d1f0b2bcf52d6cf5989585ece
- Drive: https://drive.google.com/file/d/1N8g5oDPLdxbBTe1oS91j_wzk12oO29gJ/view?usp=drivesdk
- Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FT05_20261004.zip
- 전체 REPORT_KO.md, TRANSPORT_CONTRACT.json, MODEL_POLICY.json, scripts, 입력과 상세 결과는 ZIP에 있다. 이 repository directory는 요약/반환/인터페이스 요약/동기화 정책/백업/인계의 6개 파일이다.
- 양쪽 업로드 완료 및 ID/path/size 확인. R1 metadata verification; remote full restore와 remote byte hash 확인은 하지 않았다.

## 새 연결식

metric ds^2=-c^2 dt^2+sum a_i^2 dx_i^2. H_i=dot(a_i)/a_i, Theta=sum H_i=3H. gas-comoving tetrad와 future momentum direction을 쓴다. r_i=a_i(t0)/a_i(t), V=prod a_i(t)/a_i(t0), D=sqrt(sum r_i^2 n0_i^2)일 때 E=D E0, n_i=r_i n0_i/D이고 dOmega=dOmega0/(V D^3). 이 Jacobian은 momentum-direction sphere의 값이지 optical angular-diameter distance가 아니다.

proper number spectrum Psi와 occupation의 관계는 Psi=2 E^2 f/[(2pi hbar)^3 c^3]. collisionless Psi=D^2 Psi0, 따라서 V Psi dE dOmega=Psi0 dE0 dOmega0. h_parallel=sum H_i n_i^2, dot E=-h_parallel E, dot n_i=(h_parallel-H_i)n_i, div_S2(dot n)=3 h_parallel-Theta.

보존형 식: partial_t Psi+Theta Psi+partial_E(dot E Psi)+div_Omega(dot n Psi)=S_N-c kappa Psi. photon count/H의 characteristic packet P에는 dot P=-c kappa P만 남으며 -3H P를 다시 더하지 않는다. kappa=sum n_s sigma_s(E)는 proper gas-frame opacity다. species event=c n_s sigma_s P와 heat=(E-chi_s)event는 같은 quadrature/owner를 쓴다. HomogeneousBoundFree와 기존 low-group effective HI/MFP를 섞지 않는다.

radiation: dot u_gamma+Theta u_gamma+sum H_i P_i=Q_gamma. gas thermal: dot u_th+5H u_th=Q_th. per-H thermal w는 dot w=-2H w+Q_th/n_H. binding/H에는 expansion term이 없다. work를 Wgas=int 2H w dt, Wprimary=int sum H_i P_i/n_H dt로 두면 w+b+e_primary+L_escape+Wgas+Wprimary=initial이다. 이는 cosmological global conserved matter energy가 아니라 work를 포함한 bookkeeping identity다.

FT03 L_escape는 emission-time 누적 에너지이지 현재 radiation energy가 아니다. isotropic emission, no reabsorption, achromatic geometric optics 조건에서는 K(t,t')=<D>_emission, Ki=<D n_i^2>로 e_escape=int q_escape K dt', P_escape,i/nH=int q_escape Ki dt'를 구성할 수 있다. sum Ki=K, partial_t K=-sum H_i Ki, FLRW K=a(t')/a(t). emitted photon number/spectrum은 추론하지 않는다. 현재 e_escape를 쓸 때는 L_escape를 e_escape+Wescape로 대체하고 둘을 동시에 합하지 않는다.

고정 energy bin은 signed number edge flux와 edge-energy flux, 내부 redshift work가 필요하다. H>0만으로 모든 ray가 redshift하는 것은 아니다. a(s)=(exp(2s),exp(2s),exp(-s)), n0=(sqrt(3)/2,0,1/2), E0=16 eV에서 HI threshold 13.6 eV는 exact cubic 100x^3-289x^2+300=0, x=exp(2s)를 준다. 두 crossing s=.181212882936444232 및 .425922708864321075 사이에서 inactive이고 시작/끝은 active다. exact rational root bracket과 Sturm count를 기록했다. prescribed HI bath의 optical depth .31052603989017, survival .7330612353291748이며 고정밀 적분 상대차는 1.999e-15 이하다.

초기 isotropic collisionless radiation, a_i=a exp(beta_i), sum beta_i=0에서 K=(a0/a)[1+(4/15)sum Delta beta_i^2+O(beta^3)], P_i/[nH e_gamma0(a0/a)]=1/3-(8/15)Delta beta_i+O(beta^2). 이 차수 결과를 threshold가 있는 ionization observables에 무단 이전하지 않는다.

편광은 supplied unitary U에 대한 Fout=exp(-tau)U Fin Udagger algebra만 64점 검사했다. 실제 screen geodesic/BASS hierarchy는 실행하지 않았다. 비경사 gas에는 순복사력 0이 필요하며 새 coupled model의 antipodal symmetry가 이를 보장한다. 일반 directed flux는 tilt/momentum 방정식이 필요하다.

## 실제 경량 실행

- tangent Jacobian128점 최대 상대차6.662e-16 이하, 독립 geodesic ODE6점 최대 scaled차9.931e-14 이하.
- 각도 quadrature72/288/1152/4608 및 작은 spectral quadrature. Jacobian을 생략하면 proper number factor가 .72150072 대신 .80772745로 잘못된다. FLRW expansion2에서 count1/8, energy1/16.
- 36변수 새 discrete model: 6 antipodal axis directions, 18 packets, t_end=1e13s, a_i=exp((.02,.03,.04)s). FT03 rates/initial composition를 읽었으나 old suite는 재실행하지 않았다.
- 최종 fractions=(.9738894159353618,.3233053953535748,.6044256425592565), T=45526.68254858268 K.
- DOP853/Radau observable 차이3.542e-14 이하, 독립5population+lnT RHS 차이2.665e-14 이하.
- sampled energy+work residual1.670e-13 eV/H 이하. work를 빼면 끝점에서 -.8083725857624771 eV/H가 남으며 이는 geometric work다.
- FT03 coefficient ceiling만 계승하고 팽창 일을 새로 포함한 exact rational comparison: 31931.00662357358<=T<=106192.75165363487 K, guard[30000,110000] 내부. 이전 static T bound를 이전한 것이 아니다. continuous declared ODE에만 적용한다.
- 최종 runner: map4 tests, transport6 check groups, coupled integrators, input/JSON contract 4단계 exit0. production 또는 atomic accuracy PASS가 아니다.

Full Grackle/Rust build, self-consistent Einstein history, physical provider admission, canonical F00~F09 mutation은0. 과거 [160,161] FAIL, tick160, strict local<2e-4/public width<2e-3 보존. 새 연구 folder만 append한다.

참고: Fleury/Pitrou/Uzan arXiv:1410.8473v3의 알려진 geodesic; Moscibrodzka/Gammie MNRAS475,43의 invariant polarized transfer. 새 reservoir/threshold/domain 결과는 이 패키지에서 유도 및 검사했다.
