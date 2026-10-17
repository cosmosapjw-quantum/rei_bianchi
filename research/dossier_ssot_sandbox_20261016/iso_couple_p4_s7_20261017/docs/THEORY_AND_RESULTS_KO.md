# rei_bianchi P4/S7: 수치 오차축 분리와 D 문턱 진단

2026-10-17. Parent PR188 HEAD `9f9837c0587e616ec351980fdbaab6dea799d027`. 입력은 P4/S6 FULL ZIP, SHA256 `99eba3f035fbc08adc2fe6135d120a461d2579bc832fb2878d1a6a249f025c62`. 기존 source와 P6 계산 재사용 kernel을 바꾸지 않고, positive-only 해상도 생성자·관측 진단·독립 정적 참조 및 실행기를 추가했다.

## 1. 질문과 범위

P6의 bit parity는 같은 이산 map의 최적화 동치다. 이번에는 그 map의 시간/출생시각/스펙트럼/각도 오차를 구분한다. 시간축은 (a) gas/photon macrostep 수 Nt, (b) 각 macrostep 안의 출생 GL2/4, (c) 광학깊이 적분 substep m을 따로 기록한다. 분광축은 세 원본 문턱 구간 각각의 셀 수 NE 및 OriginalCellMean/SplitPositiveGauss3 표현을 구분한다. 각도는 원본 GL8/16/32다. GL2/4만으로 출생시각 축의 독립적인 수렴차수를 인증하지 않는다.

두 개의 큰 설정(time_split64, N16-angle32)은 실행 제한상 미완료로 보존했다. 대신 각도축은 Nt8에서 GL8/16/32 세 값을 모두 계산했다. 최종40개 계획 중38개 완료,2개 deferred다. 30개 native histories와8개 static spectral cases가 완료됐다. 이는 전체 EoR campaign이 아니다.

## 2. 가정과 관측량

Metric signature(-,+,+,+), proper t[s], ds²=-c²dt²+Σai²(dxi)², c=299792458m/s. Non-tilted homogeneous scalar absorption만 사용한다. Photon energy[eV], proper species density[m^-3], reference-comoving photon count[m^-3], energy ledger[J/comoving m³]. EV_J=1.602176634e-19J/eV.

기준 결합 사례: H=1.2e-16s^-1, shear s/H=+0.06(추가0,-0.06 대조), a(0)=1/21, Tspan=8e10s. 原 MD14_Z002_FESC_BB50K_13P6_100_V1, fesc0.2. 모든 coupled 행에서 CI/RR/CX/CE/free-free/CMB ON을 유지하고 RR,CX,FF,CMB budget이 비영인지 확인했다. 초기 H/He/D 조성, D defect0.0037eV와 CMB bath20K는 선행 regression fixture다. 원시 D/H 또는 관측적 z20 CMB를 맞춘 모델이 아니다. Einstein 제약을 푼 BASS on-shell 이력이 아니라 prescribed Bianchi-I다.

추가 관측 진단은 q2_E=ΣN E P2(mu_obs)/ΣN E와 mean_age=ΣN(t-tb)/ΣN이다. q2_E는 에너지로 가중한 P2 평균이며 CMB 온도의 a20 또는 표준 정규화된 power spectrum이 아니다. 관측 방향은 원본 Killing ray에서 계산하며 출생 방향 기록을 보존한다.

## 3. Positive 생성자와64-bin 제한

기존 SourceAgeBridge::with_groups는 grey projection이64-bin 이하인지 검사한다. 이는 P6 positive cohort 수 제한이 아니다. 새 private PositiveStudyBridge는 AxbiSource와 geometry/source domain, RetardedControls의 원래 검증을 수행한 뒤 positive operator에만 연결된다. Grey projection API를 내보내지 않는다. 원래 grey constructor/64-bin guard는 그대로이며 GL32를 여전히 거부하는 회귀 테스트를 유지했다. GL8에서는 P6와 전체 AgeStep/cohort bits가 동일하다. 새 GL32 positive 경로는 모든 원본 광자를 유지한다.

## 4. 비교와 차수의 의미

고정된 다른 오차축에서 Q(h)=Q*+C h^p+e_fixed를 가정하면

    (Q(h)-Q(h/2))/(Q(h/2)-Q(h/4)) = 2^p.

그러나 이 식은 p를 **추정**할 때의 가정이지 오차 상한 정리가 아니다. 차분 부호가 바뀌거나 부동소수점 바닥에 닿으면 p=None으로 기록한다. 단순히 절댓값 로그를 취해 높은 차수라고 표시하지 않는다. 또 두 해상도를 동시에 바꾼 비교는 one-axis 검증에서 거부한다. Wolfram에서 위 ratio와 Q(h,k)의 c hk 혼합항에 대한 mixed difference=c h²/4를 검산했다. 교차오차가 있으므로 축별 차이의 합을 엄밀한 전체오차 bound로 승격하지 않는다.

### Coupled macrostep 결과

OriginalCellMean, NE16/각도8/출생GL2/m4를 고정한 Nt32,64,128의 observed order는 HI1.01186, HeII1.00668, DI1.01765, T1.00230이다. 총 생존 광자수는 Nt8~64에서 매우 빨리 안정되는 것처럼 보였지만64→128에서 차분 부호가 바뀌었다. 따라서 마지막 triplet의 광자수 차수는 NONMONOTONE_NO_ORDER_ADMITTED다.

Nt64→128의 DI 상대 차이는 약0.1143%인데 생존 광자수 상대 차이는 약4.39e-8이다. 총 photon inventory만으로 희귀 종의 사건수 또는 전체 coupled map의 차수를 판정할 수 없다. Nt128도 연속 참해가 아니며 이 상대 차이를 엄밀한 누적오차 상한으로 쓰지 않는다.

### 고정 Nt16에서 다른 오차축

SplitPositiveGauss3/NE16/GL8/m8을 고정한 출생 GL2 대비GL4 생존 광자수 상대 차이는 약-1.8566e-5, DI는+4.2427e-6이다. m4 대비m8의 가장 큰 종별 차이는 HeI 약-2.9814e-10이다. NE32 대비64의 split spectral 차이는 대부분 반올림 또는 높은 차수의 quadrature 영역이며 HeII 약5.8e-11 수준이다. 이 규모 비교는 짧은 fixed fixture의 결과만 말한다.

## 5. 독립 연속적분과 분광 문턱

별도 Python/SciPy 코드는 Rust 함수를 불러오지 않고 원 Verner 계수와 동일한 H-equality D threshold 모델의 식을 계산한다. Gas density 고정( HI1000,HeI300,HeII100,DI25 m^-3 ), 팽창 없음, 초기 광자0, 단위 누적 source photon1, Tspan8e10s의 정의된 문제다. 각 에너지에서

    phi(tau)=(1-exp(-tau))/tau, tau=Tspan Σj c nj sigma_j(E)
    survivor=phi, A_j=(1-phi) kappa_j/Σkappa.

50kK BB photon shape E²/(exp(E/kBT)-1)를13.6~100eV에서 정규화하고13.602134599702,24.59,54.42eV에서 적분을 나누었다. 이는 동일한 주어진 atomic fit에 대한 독립 수치 참조해이며 실제 원자물리 불확실성을 줄인 것이 아니다.

최대 종별 사건수 상대 차이(독립 연속 reference 대비):

| NE/segment | OriginalCellMean | D-edge split GL3 |
|---|---:|---:|
|16|3.71433e-4|4.28202e-9|
|32|3.55870e-4|5.81365e-11|
|64|3.51988e-4|3.55835e-13|
|128|3.51017e-4|2.41582e-14|

마지막 값들은 floating-point 및 quadrature uncertainty 수준이다. 14자리 정확도를 인증한 것이 아니다. Scalar conservation은 두 표현 모두 통과하므로 보존만으로 이 분광 오류를 탐지할 수 없다.

### 셀 수 증가만으로 D 오차가 잘 줄지 않은 이유

첫 H source 구간의 하한 a=13.6eV, 첫 셀 상한 b(n)=13.6(24.59/13.6)^(1/n)이고 평균은 M(b)=∫Ew/∫w다. 양의 w에 대해 M'(b)=w(b)(b-M)/∫w>0이다. b(n)은 n에 대해 감소하므로 가장 작은 첫 셀 평균은 허용하는 최대 n에서 나온다.

원 source constructor의 최대 n=1024에서도 독립 적분의 첫 셀 평균은13.603933688904986eV로 explicit D edge13.602134599702eV보다 높다. 평균이 문턱과 같아지는 연속 n은 약1886.91로 현재 owner cap 밖이다. 따라서 이 **특정 셀평균 표현**은 허용 해상도 안에서 D 아래 좁은 구간을 대표 node로 분리하지 못한다. 해당 band에 전체 출생 광자의 약2.77539e-4가 있다. 해결책은 source 정규화 guard를 완화하거나 임의 D rate를 바꾸는 것이 아니라, 이미 구현한 문턱 분할이다. 일반적인 spectral solver에 대한 no-go나 학술적 신규성을 주장하지 않는다.

## 6. 각도축: 민감한 별도 대조군

짧은 coupled 이력에서는 H Tspan≈9.6e-6라 각도 변화가 대체로 roundoff 수준이다. 이것을 일반 Bianchi 각도 수렴의 증거로 삼지 않았다. 추가 transparent 대조군은 H=2e-15s^-1,Tspan1e14s,s/H=1.5, 모든 H/He/D 완전 이온화, collision/CX/CMB OFF다. 흡수0이므로 exact Killing map과 연속 source integral을 독립적으로 비교할 수 있다. 이 큰 비등방성은 물리적 관측 허용 모델이 아니라 numerical stress test다.

u=tb/T, g(E/Eb)=sqrt((1-mu_b²)e^-2(H-s)T(1-u)+mu_b²e^-2(H+2s)T(1-u)), mu_obs=mu_b e^-(H+2s)T(1-u)/g라 두면

    q2_E = [∫du j(u)∫dmu_b/2 g P2(mu_obs)]/[∫du j(u)∫dmu_b/2 g].

Python source-time adaptive quadrature와 angular GL128,256을 비교한 참조해는 약-0.1776970511295이다. Native Nt8/출생GL4에서 각도GL8/16/32의 q2 절대 차이는 각각1.28425e-5,4.11528e-9,5.91e-15이다. 출생GL2의 GL32 결과 차이는9.86412e-8이므로 각도만 늘려 해결되지 않는 출생시각 오차도 분리됐다. s/H=0과-1.5를 별도 검산했다. 이 stress 결과를 absorption/scattering/tilt 모델로 일반화하지 않는다.

## 7. 실행 및 다음 선택

Rust119/119(기존112+새7), Python 분석 검증5개 PASS. 최대 native photon ledger2.12916e-14, energy ledger8.10078e-16. 현재 루프는38개의 완료 행에만 근거한다. 세 번의 bounded 작업 중단과 출력 포맷 compile 수정은 evidence에 보존했다. 원 source/rate/geometry/P6 kernel은 변경하지 않았다.

판정: PASS_SCOPED_SEPARATED_RESOLUTION_AND_INDEPENDENT_ORACLES. FullP4 PARTIAL, SA01/02,FLRW-CONV,BI-SIGNED,FULL_EOR HOLD. BASS on-shell donor intake는 이번에 선택한 convergence unit 밖으로 남겼다. 다음 bounded unit의 우선순위는 gas midpoint 예측·보정과 원 full_network 시간 적분차수를 함께 검토하는 것이다. 기존 photon quadrature만 고차로 바꾸거나 외부에 Strang 순서를 붙이는 것만으로 full gas solver가2차가 된다고 가정하지 않는다.

## 문헌 근거

Mackey2012, A&A539 A147, DOI10.1051/0004-6361/201117984: 시간중심 opacity 및 multifrequency 정확도 비교를 참고했다. 이 논문은 다른 numerical implementation이며 이번 수치를 검증한 출처가 아니다. 원문 HTML을 Exa로 읽었고 web 직접 접근403은 별도 보존했다.
Pawlik & Schaye2011, MNRAS412,1943, DOI10.1111/j.1365-2966.2010.18032.x, arXiv1008.1071: photon conservation, thermochemical coupling 및 grey/multifrequency 비교의 배경 근거. 초록을 확인했다.
Verner et al.1996, ApJ465,487, DOI10.1086/177435 및 저자 photo.html: 원 cross-section fit의 source/모델 범위. 본문에서는 코드에 고정된 문턱과 바인딩 에너지를 구분했다.

## 8. 별도 ZIP 복원 검증

실제 seed ZIP의207 payload hash를 확인하고 새 디렉터리에서119 Rust tests와5 Python tests를 재실행했다. Strict Clippy, 신규3 Rust 파일 rustfmt 검사, release executable build를 통과했다. 대표 angle32_n8행은 모든 scientific column이 동일했고 wall_s는 비교에서 제외했다. 전체38행을 다시 실행한 것은 아니며, 완료된 원시38행의 분석과 독립 연속 reference 계산을 재수행해 JSON content가 같음을 확인했다. 최초 clean compile+tests 호출은20초 경계에서 중단됐고 뒤이은 전체 test command가119/119 exit0으로 완료됐다. 일괄 uninterrupted 전체 runtime을 만들지 않는다. 상세 로그는 CLEAN_RESTORE_VERIFICATION.json에 연결되어 있다.
