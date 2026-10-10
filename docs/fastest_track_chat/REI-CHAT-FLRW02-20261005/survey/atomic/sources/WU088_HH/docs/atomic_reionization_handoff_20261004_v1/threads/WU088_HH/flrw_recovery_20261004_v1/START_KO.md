# FLRW01: 국소 이온화율·광자수·filling factor 환원

사용자 요청으로 수행한 이론/경량 검증이다. 상태는 FLRW_REDUCTION_THEORY_AND_30_CHECKS_COMPLETE__FULL_RUNTIME_AND_FILLING_CLOSURE_PENDING. 원자 provider/rei production 코드는 수정하지 않았다. Peebles PB01은 별도 소비자 연구이며 재증명하지 않았다.

## 전체 재현 패키지

- name: WU088_HH_FLRW_RESTORATION_DELIVERY_20261004_v1.zip
- bytes: 37752
- SHA256: d4df7f9d69c15d91b5585b11fd79191b6da499ea1f44e74481e9ba4fb8bd442c
- Drive object: 1gsLOLVk8W92JTrmdwdGvZ3O0IGuVAgoW
- Dropbox object: id:BSpOijBcT10AAAAAADyHDg
- Dropbox path: /BASS_DERIVATION_DOSSIERS_20260912/WU088_HH_R31S_NCP_REDESIGN_20260928/WU088_HH_FLRW_RESTORATION_DELIVERY_20261004_v1.zip
- root: WU088_HH_FLRW01_20261004_v1/
- 18 payload files plus manifest/checksums,20 ZIP entries. Local CRC/hash/size verified. Both providers completed ACK+name/size metadata. Output remote restore not performed.
- Report Drive: 1H4qSqDpgRzVMzGtXUEhyRZAugDpdnq70; Dropbox: id:BSpOijBcT10AAAAAADyHHw.

기존 cache 또는 인증된 provider 한 곳에서만 bytes를 회수한다. 사용자 재업로드를 요구하지 않는다. 전체 증명·30개 검산·원 source3개·계약은 ZIP이 정본이며 본 Git파일은 projection/index다.

## 일반 환원

서명(-,+,+,+), proper time t, n proper density, N=a^3 n, h=2pi hbar, 실제 c를 사용한다. Bianchi I에서 오는 극한은 spatially flat FLRW다. 전체 시간구간의 shear0/non-tilt와 초기·경계·source matching을 요구한다. 순간적인 equal axes나 H=0 시험만으로는 충분하지 않다.

1. dot(nH)+3H nH=0을 종 연속식에서 소거하면 dot x=(1-x)Gamma-alpha ne x다. Fraction에 -3H x를 추가하지 않는다. PureH에서 ne=nH x이므로 sink는 -alpha nH x^2이며 fixed-ne linear oracle와 다르다. Gamma=c integral sigma n_nu dnu=4pi integral J_nu sigma/(h nu)dnu.
2. Photon equation은 dt(n_nu)-H nu dnu(n_nu)+2H n_nu=emission-c kappa n_nu, 또는 dt(n_nu)+3H n_nu+dnu(-H nu n_nu)=RHS다. All-frequency collisionless a^3 n_gamma와 a^4 u_gamma는 각각 constant다. Fixed threshold 위에서는 dot N_gamma^>=a^3(E-A)-H nu0 N_nu(nu0). Moving bin에는 [(Hnu+dot nu_edge)N_nu]_lo^hi가 필요하다.
3. 동일 primary photon absorption은 sum_s n_s Gamma_s로 배분한다. 이미 bin-integrated/weighted N에 delta-nu/4pi를 다시 곱하지 않는다.
4. Explicit alphaA sink+ground recombination photon, OTS alphaB, CaseA escape는 별도 closure다. alphaB sink에 같은 recycled ground photon까지 더하면 double count다. Photon multiplicity와 escaped energy는 별개다.
5. General averaged ledger는 NbarH dot Q_M+dot N_gamma=E_star^c+I_coll^c-R_net^c-L^c. Sharp fronts에서 Q_M=Delta_I Q_V이므로 density weighting의 시간미분도 필요하다. Delta_I=1, negligible storage/loss, defined recombination moment Q/t_rec 등 추가 가정에서만 dot Q=E_star^c/NbarH-Q/t_rec가 나온다. Homogeneous x를 Q로 개명하는 것만으로는 불충분하다.

## 명시적 반례와 검산

- Uniform x=1/5의 recombination moment는1/25, fully-ionized bubbles Q=1/5는1/5로5배 다르다.
- Q_V=1/4, phase density contrast2이면 적절한 neutral density에서 Q_M=1/2다.
- 초기 photon storage가0인 유한흡수 문제의 초기 ionization slope는0이며 instantaneous photon counting은 nonzero다.
- Absorption0이라도 threshold redshift loss는 남는다.
- alpha*nH=2,x0=.5,t=1에서 pureH recombination은 x=.25, frozen-ne oracle는 .18393972다.

30 unique symbolic/exact-counterexample/source-bound geometry checks PASS. Python3.13.5,SymPy1.14.0,NumPy2.3.5. FT06 원 geometry method만 AST로 분리해 epsilon0의3시각에서 호출했고 maximum absolute residual0. Constructor/RHS/history는 실행하지 않았다. TDD나 독립 과학 심사는 주장하지 않는다.

## 실제 소스 범위

읽기 기준 REI67957715cf3336b89c27c1e59c33ca23098f8934:
- homogeneous_rates.rs blob d5aedfd37485b33c82a4cf0ee1d854099a517842: bin-integrated comoving photon→proper absorber의 primary absorption 장부. 전체 emissivity/redshift evolution이 아니다.
- hydrogen_step.rs blob96f823371545a6aa70bb528a8ca804ec66c5a320: constant I,R scalar oracle. Evolving-ne thermochemistry 전체검증이 아니다.
- FT06 ZIP03e56d2844a767a840f3047361a2aab5e8e07d80ba9c6d3354c3f70037eceabe의 원geometry/closure/policy3파일 bytes보존.

Rust파일은 connector로 full-content read했으나 direct raw DNS실패로 bytes materialization은 하지 않았다. 해당 read/provenance와 실패를 구분한다. 현재 homogeneous CaseAescape를 추가 closure 없는 classicalQ/Peebles복원으로 승인하지 않는다. 전체runtime/source-bound top-level regression은 NOT_RUN이다.

## 다음

FLRW02_SOURCE_BOUND_REDUCTION_REGRESSION: 실제 consumer top-level RHS/transport source에 L_LOCAL_RATE,P_SPECTRAL_NUMBER,AB_RECOMBINATION_ACCOUNTING,Q_FILLING_FACTOR profile을 결속한다. Exact source, units, Case, emissivity/absorption owners, frequencyedges, Q averaging, matched IC/H/T와 numerical budget을 제공한다. 없는clumping/filling state를 외부주입하고 유도복원이라고 부르지 않는다. 30개완료검사나 legacy를 관례적으로 반복하지 않는다.

복원 후 python3 -B verify_delivery.py. 새host/변경부분 재검산 필요시 python3 -B research/verify_flrw.py --out /tmp/FLRW01_CHECKS_NEW.json.

원 HH24/289,missing265unbounded,epsilon_C/R=null,B22OPEN,consumedFD1/FD2/pilot불변. 원과학DB/다른repo수정0. HH-F1/REI-F07/physical/production승격없음. 같은HHbranch additive/nonforce,기존Drive/Dropboxcreate-only. 시작·게시전 liveHH는 b0fb3a7cdb0976330d48b97edaf77560ec121e8a, REI는67957715cf3336b89c27c1e59c33ca23098f8934였다. 최종commit/tree와receipt ACK는 detached delivery에 남긴다.

원전: Haardt&Madau2012 arXiv1105.2039 Eq1/18; Madau,Haardt&Rees1999 astro-ph/9809058 Eq20; Madau2017 arXiv1710.07636 §2. 원문식과 이번 직접연결/반례를 구분한다.
