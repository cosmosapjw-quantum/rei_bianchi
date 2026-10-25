# HI 실제 원자 측도의 massive stress 주입률

## R1–R3: 고정 질문과 재사용

단위: HI_NATIVE_MASSIVE_STRESS_20261025. 같은 HI/z=2.479의 4,368개 원자 측도에 전자 rest-energy M을 결속했을 때 압력 trace W, isotropic pressure source W/3, 비상대론적 근사 2K의 오차, M에 대한 민감도를 계산한다. 과거 native-HI 수·에너지 및 stock/work 이론은 재사용한다. 이 작업은 실제 순간 source의 다음 모멘트이며 시간 진화된 stock 계산이 아니다.

불변 입력은 prior science 8d68dff35ca2bdc456049081132a7d2449b29143의 CSV SHA256 f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3와 raw SHA256 0335abad8879817b5e61b0f5ef7120009c2e18251be4fe82ea3e48c8e7aa5669다. CSV의 decimal spelling은 float round-trip 후 exact binary64 유리수 k_j,w_j로 읽는다. 저장 raw의 exact A,K,B,P를 재사용하며 이전 모멘트 실행을 반복하지 않는다.

NIST 2022 CODATA complete table의 electron mass energy equivalent는 0.51099895069 MeV, standard uncertainty 0.00000000016 MeV다. 이번 계산의 명목 입력을 decimal exact M0=510998.95069 eV로 정의하고 u=0.00016 eV의 M0±u를 민감도 탐색점으로 쓴다. 유한 입력 M0의 exact arithmetic과 물리 상수의 불확실성은 서로 다른 문제다. M0±u는 보장된 참값 구간/신뢰구간이라는 주장을 하지 않는다. 첨부14의 미사용 선언 _ME_EV=510998.95는 역사적 비교 자료이며 owner를 조용히 바꾸지 않는다.

문헌의 local-frame kinetic stress T^ij=∫ f v^i p^j d^3p(Sarbach–Zannias, arXiv:1303.2899v1, Eqs.52–58)를 사용한다. 이전 stock/work에서 유도한 massive trace kernel 자체는 재사용 결과다. 신규 기여는 실제 μ와 electron M의 결속, 유한 모멘트의 민감도/근사 오차, 효율적인 유리수 enclosure 구현 및 실제 검증이다. strong no-go/문헌 최초성 주장은 없다.

서명 (-,+,+,+), 에너지 단위 eV, 시간 proper second, target 기준을 유지한다. M=mc²로 c를 보존하며 c의 수치를 새로 넣지 않는다. χ=represented float(13.6) eV, bath-rest target, ground-state HI, zero recoil, no-deposition, photon upper endpoint 50000 eV는 변하지 않는다. CSV에는 angular data가 없으므로 μ⊗dΩ/(4π)는 별도로 선언한 isotropic closure다.

## R4–R5: 구성, 미분과 유한 support bound

μ=Σ w_j δ_(k_j), k_j≥0, w_j≥0, M>0라고 하자. 총에너지 E=k+M, p²c²=k(k+2M), v=pc²/E로부터

    g(k,M)=pv=k(k+2M)/(k+M)=k+Mk/(k+M)=2k−k²/(k+M).
    W(M)=∫g(k,M)dμ, p_inj(M)=W(M)/3.

source가 local rest frame에서 isotropic이면 momentum flux와 STF injection은 0이다. W/3의 단위는 eV target⁻¹ proper_s⁻¹다. 압력의 시간 주입 모멘트이며 현재 stock pressure나 thermal heat의 값이 아니다. 물리 n_HI와 시간 이력이 주어져야 실제 volume source/stock과 접합된다. Rest energy M A를 기존 kinetic/binding/UV ledger에 더하지 않는다.

직접 미분하면

    g_k=1+M²/(k+M)²,
    g_M=k²/(k+M)²,
    Hess(g)=−2/(k+M)³ [[M²,−Mk],[−Mk,k²]].

임의 벡터 (a,b)에 대한 Hessian quadratic form은 −2(Ma−kb)²/(k+M)³≤0이다. 따라서 g는 양의 영역에서 joint concave이고 k g_k+M g_M=g다. k=0에서는 g=g_M=0이다. M→0+에서 g→k, M→∞에서 g→2k이므로 K≤W≤2K다.

    S(M)=dW/dM=Σ w_j k_j²/(k_j+M)² ≥0.
    W''(M)=−2Σ w_j k_j²/(k_j+M)³ ≤0.

유한합이므로 미분과 합 교환은 즉시 정당하다. 0≤k≤L에서

    D(M)=2K−W(M)=Σ w_j k_j²/(k_j+M),
    0≤D≤ L K/(L+M),
    W≥ (L+2M)K/(L+M),
    D/W≤ L/(L+2M),       K>0.

첫 부등식은 k/(k+M)≤L/(L+M)를 k w로 적분한 것이다. 마지막 것은 앞선 W 하한을 이용한다. L은 같은 저장 raw maximum_kinetic을 재사용하며 CSV support를 이번 새 계산에서 확인한다. 이것은 유한 support의 근사 bound이며 spectral quadrature의 새로운 physical error bound가 아니다.

M0±u에서는 단조성으로 W(M0−u)≤W(M0)≤W(M0+u). Concavity로

    W(M0+u)−W(M0) ≤ u S(M0)
    W(M0)−W(M0−u) ≥ u S(M0).

직접 평가한 양 endpoint의 차이를 민감도로 기록한다. 이를 표준불확실성의 통계적 해석 이상으로 승격하지 않는다.

고정 μ에서 m=a X≥0, dm=a dX+X da라 두면

    q_pressure = m W(M)/3,
    Jv_pressure = dm W(M)/3 + m dM S(M)/3.

a,X≥0, da,dX,dM은 signed finite 방향이다. 질량 입력의 방향 dM은 모델 sensitivity이며 시간 변화하는 전자 질량을 가정하지 않는다. q_flux=0, q_STF=0은 선택 closure 아래 정확한 값이다. Existing public source APIs는 변경하지 않고 새 consumer API를 추가한다.

## 손으로 계산한 판별례

(k,w)=(0,1),(2,3), M=1에서 A=4,K=6,W=8,p_inj=8/3,D=4,S=4/3. a=2,X=3,da=−1,dX=2,dM=3이면 m=6,dm=1, q_pressure=16, Jv_pressure=32/3이다. 이는 실제 HI 입력과 구별되는 구현 control이다. Empty/zero measure에서는 W=S=D=0이고 D/W는 null이다.

## C3: 효율적인 exact enclosure

각 t_j=w_j g(k_j,M)는 exact rational이지만 서로 다른 k_j+M 때문에 전체 Fraction 합의 공통 denominator가 커질 수 있다. 비교한 표현은 (i) 전체 유리수 합, (ii) Decimal 고정정밀도 합, (iii) exact rational term + directed dyadic enclosure다. (iii)를 primary로, 다른 계산식의 Decimal100을 independent numerical reference로 고정한다.

각 유한 signed rational term 목록에서 T=max |t_j|>0, E=floor(log2 T)를 integer bit-length와 exact 비교로 구한다. P∈{128,160}, δ=2^(E−P)로 놓고

    l_j=floor(t_j/δ), u_j=ceil(t_j/δ),
    lo=δ Σl_j, hi=δ Σu_j.

floor/ceil와 합은 정수 연산이다. 각 t_j∈[δl_j,δu_j]이므로 정확한 합은 [lo,hi]에 있고 hi−lo≤Nδ. 음수에도 floor division 정의를 그대로 쓴다. T=0일 때 [0,0]. 같은 E에서 P160의 dyadic grid는 P128을 세분하므로 interval nesting이 성립한다. 이것은 실행 시 검사한다. 각 항만 Fraction으로 만들고 전체 서로 다른 denominator를 합하지 않는다.

Interval scalar multiplication은 부호에 따라 양 끝을 교환하고, 합/차/나눗셈(양의 3)은 exact endpoint arithmetic으로 한다. 따라서 W에서 W/3, q/Jv, D=2K−W를 계산하면서 enclosure를 보존한다. 두 endpoint의 nearest binary64 round 결과가 같을 때 그 값을 반환하면 monotonicity에 의해 정확한 합의 correctly rounded 값이 증명된다. 양 끝이 서로 다른 float이면 ROUNDING_UNRESOLVED를 반환한다. 자동 precision 확대/허용오차 확대는 하지 않는다. Overflow/nonfinite는 명시적으로 거절한다.

exact_zero는 [0,0]일 때만 확정한다. 비영 interval이 0을 포함하지 않으면서 반환 float가0이면 final_underflow_to_zero, 비영 subnormal이면 subnormal로 표시한다. 0을 걸치는 미해결 enclosure를 exact_zero로 표시하지 않는다. 심한 cancellation에서 고정 P가 불충분할 수 있으며 이것은 API의 명시된 unresolved 상태다.

Decimal100 참조는 각 binary64를 정수 ratio로 받은 뒤 Decimal numerator/denominator로 바꾸고 대체식 2k−k²/(k+M)를 사용한다. Primary enclosure와 알고리즘을 공유하지 않는다. Decimal은 보조 numerical comparison이며 exact interval proof나 fresh model review가 아니다.

## 판정·실행 경계

명목 W,S와 M± endpoint W에 대해 P128/P160 nesting, width bound, stable rounding, Decimal100 containment와 상대차≤2e−15를 고정한다. 원래 L0 gate 2e−12는 그대로다. 실제 μ에 대한 K≤W≤2K, D bound, mass monotonic/concavity를 interval arithmetic으로 확인한다. Hand controls는 exact rational expectations다. 과거22/66/83, ANGTHERM01/02, NCP, HI-summary, pressure/stock/work/native-HI 및 donor quadrature 재실행은0이다.

Fresh native reviewer는 본 유도/구현 diff/raw를 한 pass에서 읽고 현재-task finding만 낸다. CAS는 독립 model review로 표시하지 않는다. Root가 scope admission과 다음 행동을 판정한다. 실제 n_HI/history/IC/geometry/collision supply는 unresolved이며 L4_ready=false, whole_model_completion=null, C23E conditional D43K, HE94 partial window, PHYS85 historical state, ANGTHERM02 read-only를 유지한다.

