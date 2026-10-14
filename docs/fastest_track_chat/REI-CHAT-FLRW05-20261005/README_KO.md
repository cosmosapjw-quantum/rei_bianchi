# FLRW05: 공통 양의 스펙트럼 measure

연구 단위 REI-CHAT-FLRW05-20261005. 판정 COHERENT_SPECTRAL_REFERENCE_DERIVED_AND_TESTED__NATIVE_CONSUMER_OPEN.

## 선택과 실제 진전

BIN_EXPONENTIAL_NU_LEBESGUE_E_V1을 선택했다. 한 bin [L,R]에서 p=n_E/nH, N=integral p dE, U=integral E p dE. N은 photons/H, U는 eV/H다. x=(E-L)/(R-L)일 때 p=N*exp(lambda*x)/[(R-L)*Z(lambda)], Z=expm1(lambda)/lambda, Z(0)=1이다. 평균 조건 mu=(U/N-L)/(R-L)=1/(1-exp(-lambda))-1/lambda이며 dmu/dlambda=Var(x)>0이다. 내부 평균에 대해 유한 lambda가 유일하다. N=0이면 U=0, 경계 평균이면 별도 delta cohort를 요구하고 clip하지 않는다.

이것은 uniform dE 기준의 Shannon maximum-entropy reconstruction이며 Bose-Einstein/Planck entropy나 원 스펙트럼의 복원 증명이 아니다. numerical guard |lambda|<=10000, 실제 집중도 시험은 |lambda|<=1000의13개 profile이다. guard 전체의 uniform accuracy를 주장하지 않는다.

같은 양의 measure dJ_s=c*n_s*sigma_s(E)*p(E)dE에서 사건 J, 흡수 에너지 A=integral E*dJ, binding=chi*J, heat=integral(E-chi)*dJ를 함께 산출한다. pinned Verner HI/HeI/HeII thresholds13.6/24.59/54.42eV와 binding13.598434599702/24.587389011/54.41776eV를 구분한다. threshold에서 적분 구간을 나누고 weights를 사후 정규화하여 residual을 숨기지 않는다.

## Number/energy와 양의 substep

H>=0의 downward flux는 Phi_j=H*E_j*p(E_j+)이며 높은 에너지 donor trace를 사용한다. 상단 trace는 명시적 boundary다.
dN_g=S0_g-sumJ_g+Phi_upper-Phi_lower.
dU_g=S1_g-sumA_g-H*U_g+Eupper*Phi_upper-Elower*Phi_lower.
U를 독립 state로 두어 전체 energy ledger를 선형으로 만든다. 이것이 임의 시간적분의 positivity/time accuracy를 증명하지는 않는다.

g=aold/anew in(0,1], 상단 유입0인 remap는 donor와 target/g의 교집합을 적분해 Nnew와 g*Udonor를 만든다. 재구성된 양의 donor에 대해 N>=0,L*N<=U<=R*N과 전체 number/energy가 보존된다. 최저경계 유출 에너지는 crossing Emin*Nexit이고, work는 생존 photon의(1-g)Eold와 유출 photon의 Eold-Emin이다. 아래 photon을 retain하는 모드에 이 export를 다시 더하지 않는다. 정확 remap는 reconstructed donor에 대한 것이며 반복 projection의 모형오차까지 제거하지 않는다.

고정 밀도/에너지 attenuation pnew=p*exp(-h*k), dJ_s=p*(k_s/k)*[-expm1(-h*k)]dE도 양의 measure로 검증했다. k=0이면 사건0. quadrature가 표현한 Nq,Uq에 대한 수지와 analytical N,U의 quadrature 오차를 구분한다. 두 substep을 결합한 coupled history나 splitting order는 실행하지 않았다.

## 식별 한계와 실제 오차

N=1,U=20인 delta20과 .5delta16+.5delta24를 [14,26]bin에서 재구성하면 둘 다 uniform이다. (20/E)^3 kernel의 실제값은1 및4375/3456이지만 재구성은10000/8281=1.2075836251660428이다. 보존된 두 moment가 반응 kernel까지 식별하지 않는다.

N와평균m가 같은 양의 measure 사이에 smooth kernel |K''|<=M2를 알면 |integral K(dP-dPtilde)|<=N*M2*(m-L)*(R-m)<=N*M2*(R-L)^2/4다. threshold jump를 가로질러 이 bound를 쓰지 않는다. 이번에 Verner 전체의 엄밀한 M2 enclosure를 만든 것은 아니다.

더 강하게, [0,1]의 양끝에 폭delta, 높이1/delta인 대칭 삼각 spike를 두면 N=1,mean=.5를 유지하면서 edge trace는 무한히 커진다. 따라서 N,U만으로 edge flux의 finite uniform model-error bound는 얻을 수 없다. 재구성 coherence와 실제 edge 정확도를 별도로 검증한다.

## 최종 실행 결과

최종5명령 exit0. unit8,symbolic9,inversion13,Verner20profiles*3species*3moments=180 comparisons, remap5, frozen absorption9,FV4, spectral refinement5levels. 60자리 적분과 J/A/Q 최대상대차9.243051688235665e-15. Remap independent 최대상대차2.949549402253977e-16, number residual6.938893903907228e-18/H, energy residual3.1086244689504383e-15eV/H.

별도 실제 spectrum C*E^-2.3,13.6~100eV,N=.1/H에서 threshold-aligned3/6/12/24/48bins의 J/A/Q 최대상대오차는.008131250229032673,.0005835535183522648,3.7485369409568965e-5,2.3579854131326014e-6,1.4760844656394854e-7이다. 이는 한 smooth family의 projection-error 시험이며 보편적 차수/물리오차 증명이 아니다.

원 public homogeneous_photo_rates에 넣을3bin/96positive-node 입력과 Python expected output을 준비했다. Rust/cargo/ODE/history 실행은0회, 과거 전체suite 반복0회다. 기대값은 native 결과가 아니다. 초기 count-only baseline의 U mismatch를 red로 기록한 뒤 같은 assertion을 통과시켰고, 추가 검증 전체를 TDD라고 부르지 않았다. 독립 reviewer dispatch는 없었다.

## 실제 소스와 동시 진행

752e360a80e8622bcbaffae54183258b2e67b810의 기존 photo API는 arbitrary node slice를 받는다. 한 bin의 모든 quadrature nodes를 보내고 임의로 한 에너지로 압축하지 않는다. old API의 node는 P*nHc*MPC_CM^3 per cMpc3, 새 PhotonInput/PhotonPacket은 P*nHc per reference comoving cm3다. 현재 photon_balance는 number만 다루며 독립 U/edge-energy/work caller는 아직 필요하다.

후반7e1e590a67885efe7966f0d140efc8d136b39eab의 외부REI-F06을 수신했다. collisionless Bianchi-I ray/positive packet remap와 merged124tests는 외부 증거로 읽었으며 여기서 재실행하지 않았다. 이번 closure는 그 geometry를 중복하지 않는다. scalarN/U로 occupation/각도분포를 추정하지 않는다. 외부nextF07, F04/F05/F08/F09와physicalHOLD는 그대로다.

## 재현·다음 단계

전체 보고서/코드/results/manifest는 REI_CHAT_FLRW05_20261005.zip의 rei_chat_flrw05_20261005/ 아래다. 재현: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/run_all.py. 저장소에는 이 요약과 계약/수신/결과/인계/반환/백업 파일8개만 추가했다.
ZIP65281bytes,49entries,SHA256=c57010a6252694d537642987ac5fb0746787aadb70c9c020027f65548caa737c.
Drive https://drive.google.com/file/d/1uCMnGlj3vzxviZ5lbMwTofyjbbNSvX2z/view?usp=drivesdk
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW05_20261005.zip.
양쪽 저장과ID/path/size확인,R1metadata. 원격 전체restore/bytehash검증은없음.

다음chat: REI-CHAT-FLRW06_NATIVE_SPECTRAL_STAGE_REGRESSION. 실제 public API에96node를 연결하고 독립 U및acceptedstage return을 검증한다. compiler나 actualreturn이 없으면 그 상태를 유지하며 expected값으로 대체하지 않는다. 기존 local<2e-4/publicwidth<2e-3,[160,161]FAIL=2.1245050576368385e-4,tick160,PB02/FT07 deferred보존. 기존코드/runtime/source lock 변경없음; 새branch/merge/forcepush없음.
