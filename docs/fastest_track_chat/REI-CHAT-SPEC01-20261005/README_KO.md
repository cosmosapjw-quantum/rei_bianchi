# SPEC01: spectral projection, threshold passage and absorption/heat bias

판정: FROZEN_BATH_SPECTRAL_BIAS_DERIVED_AND_CHECKED__COUPLED_PHYSICAL_HOLD.

원 T0_BI 첫 transaction이 없어 actual BI macro certificate는 계속 blocked다. 같은 요청이나 대규모 campaign을 반복하지 않고 별도로 열린 spectral error를 진행했다. 이 연구는 constant H와 외부에서 유지하는 frozen proper absorber bath다. 실제 F08의 gas feedback/history 오차를 측정하거나 physical admission을 승격하지 않았다.

## 핵심 유도

고정 에너지 node의 양의 재배치가 주는 continuous-time generator는 lambda_j=H E_j/(E_j-E_(j-1))다. 이는 수학적으로 pure-death Markov chain이며 실제 광자에 확률적 물리를 추가한 것이 아니다. L E=-H E지만 L E^2=-2H E^2+H E d_j다. 흡수와 truncating boundary가 없는 조건에서 Var(E)<=dmax Eb D(1-D), C2 observable error<=0.5 sup|phi''| Var(E)를 얻었다. Threshold indicator에는 그대로 적용하지 않는다.

Frozen bath에서 node j의 확률적 residence 동안 아래 이동과 흡수종 s가 경쟁한다. r_j=lambda_j/(lambda_j+sum k_sj)라 두면 P_sj=k_sj/(lambda_j+k_j)+r_j P_s,j-1, A_sj=E_j k_sj/(lambda_j+k_j)+r_j A_s,j-1, Q_sj=(E_j-chi_s)k_sj/(lambda_j+k_j)+r_j Q_s,j-1이다. A_s=chi_s P_s+Q_s와 number/energy/work 장부가 같은 사건 measure로 닫힌다.

a(E)=k(E)/(H E), x_j=a(E_j)d_j일 때 optical-depth error는 정확히 boundary log + right-Riemann quadrature error - sum[x_j-log(1+x_j)]다. 0<=x-log(1+x)<=x^2/2. 내부 waiting-time 항은 흡수를 줄이지만 활성 cutoff node 체류는 반대 부호이므로 일반적인 전체 bias 부호를 미리 단정하지 않는다.

## 독립 frozen-HI 진단

H=1e-14/s,n_HI=1e-5/cm3,c=29979245800cm/s,Ebirth=13.7eV,fitcutoff=13.6eV,binding=13.598434599702eV. Source-shaped exact-decimal grid와 factual Verner HI table를 사용했다. Native binary64 재현도, 실제 nHI(t)를 진화시킨 계산도 아니다. [13.6,13.7]을 m등분하고 cutoff 아래 ghost gap은 (13.6-binding)/m이며 cutoff는 활성이다. 모든 probability/reward는 입사광자 한 개당 값이다.

Continuum Pabs=0.7484717503561974, heat=0.04677886515161539eV/incident photon.
m=8: Pabs=0.7202945791422611, heat=0.04876364489777947. Absorption relative bias=-3.76462722%, heat bias=+4.24289845%다.
m=4,8,16,32,64의 Pabs는 .695082822665265,.720294579142261,.733978660932577,.741119364189371,.744768473294055다.

512개 exact-rational panel과 a(E)의 음의 도함수 interval을 써 continuum probability를 enclosure했다. m8 Pgrid-Pcontinuum은 [-0.02818634,-0.02816801] 내부이며0을제외한다. 이 interval은 inherited directed Decimal60/exp/ln primitive 의미에 조건부다. Heat는 high-precision 및 independent matrix comparison이며 interval heat certificate가 아니다.

정확 반례: Eb=2chi,k/H=1에서 continuum absorption1/2,heat chi/4. 한 gridcell의 matched boundary는 absorption1/3,heat chi/3. Cutoff도 활성이고ghost=chi/2면 absorption5/9,heat chi/3. 세 결과의 차이를 보존검사만으로 검출할 수 없다.

시간 의존 prescribed bath에 대해서 backward value u의 (partial_t-Hparallel E partial_E-k)u=-k_s q_s를 사용해 reward error=integral p_delta (L_delta-L)u를 유도했다. Matched boundary와 terminal/initial/source projection이 같다는 조건이 필요하며 cutoff mismatch는 별도항이다. Uniform cellwise u_EE를 확보해야 curvature bound를 실제 적용할 수 있다. Fully coupled F08에서는 gas feedback/adjoint-stability도 필요하다.

## 실제 검산과 범위

최종3명령exit0. Unit7, exact two-species chains60, symbolic6, log remainder8, weak-moment12, Erlang crossing5, frozenHI chains10, interval panels512. Independent forward-residence matrix 대비 최대relative difference1.1460689560739846e-14. Gauss32/64 고정밀 차이1.9746713121697322e-60. Native/IVP/MonteCarlo/old suite0. Tests-after이며 red-green이라고 주장하지 않는다.

Source-read HEAD756e1d4f833a1eec454e660b340d3424f3e5d768. paired_runtime blob70eed18b07b6dd4297d8ef8da6d7e1be8e44456e와 parameter JSON blob843b88294972399b3f02659e83002632502d6dd6를 고정했다. Original source,CODEX_SYNC,runtime returns,threshold flag와원자표변경0.

## 재현 및 후속

REI_CHAT_SPEC01_20261005.zip: 58885bytes,31entries,30hashedpayloads.
SHA256 d217c8d2167e91a16868e7ccb782bce9fce70edd92dc8a360779a9258e15ffb3.
Drive https://drive.google.com/file/d/1W5R_IyiK2ZFaXKyX4Irn8cl71mvLEjKT/view?usp=drivesdk
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_SPEC01_20261005.zip
전체REPORT,derivation,code,exact/interval/reference evidence는ZIP의rei_chat_spec01_20261005/에 있다. 재현 python research/run_checks.py --output NEW_DIRECTORY.

다음이론 SPEC02_NONAUTONOMOUS_REWARD_AND_FEEDBACK_BOUND. ActualBI transaction-dependent FLRW08은별도partial로유지. 기존local<2e-4,width<2e-3,[160,161]FAIL/tick160,auxiliaryescapeFAIL,physicalHOLD를보존한다. R1metadata백업과restore/physicalvalidation을구별한다.

문헌: Delarue-Lagoutiere arXiv0712.3217/DOI10.1007/s00205-010-0322-x는Markov/upwind의일반적배경. Haardt-Madau arXiv1105.2039 Eq1은cosmologicalRT convention. Verner author photo.html은원factualfit과table. 위특수energy/reward/error식은본직접유도이며문헌의주장으로대체하지않는다.
