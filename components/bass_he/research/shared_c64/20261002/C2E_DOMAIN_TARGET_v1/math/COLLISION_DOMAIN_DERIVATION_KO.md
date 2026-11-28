# C2e: 충돌 궤적에서 전자구조 검증 영역으로의 조건부 사상

근거 상태: 이 문서의 운동학·보존법칙 식은 **derived**다. 실제 채택된 에너지 frame, isotope/mass, 궤적 모형과 유한 적분 구간은 `source_notes/DOMAIN_AUTHORITY.json`의 source authority를 따른다. 여기서 유도한 식에 임의의 질량·cutoff를 넣어 production domain을 지정하지 않는다.

## 1. 전자 좌표와 핵 운동학을 분리한다

부모 A2의 전자 Hamiltonian은 한 전자, spinless, 비상대론적, clamped point-Coulomb 모형이다. A는 수소 핵(전하 +e), B는 헬륨 핵(전하 +2e), κ=e²/(4πε₀), a_A=ℏ²/(m_eκ), E_A=ℏ²/(m_e a_A²)다. 정적 전하중심 O에서는 z_A=−2R/3, z_B=R/3이다. 이 O는 질량으로 정해지는 핵 질량중심과 일반적으로 다르다. 전자 좌표 규약은 collision energy가 lab 또는 CM인지 결정하지 않는다.

핵 운동학에는 별도의 projectile/target 질량 M_P,M_T>0와 상대속도 v_rel을 둔다. μ=M_PM_T/(M_P+M_T), E_cm=μv_rel²/2다. 정지한 표적에 대한 비상대론적 projectile lab 에너지 E_lab=M_Pv_rel²/2라면

\[
 E_{\rm cm}=\frac{M_T}{M_P+M_T}E_{\rm lab}.
\]

`keV/u`가 정확히 질량 M_P/m_u로 나눈 에너지 q를 뜻한다면 E_lab=(M_P/m_u)q와 v_rel=√(2q/m_u)를 사용한다. 반면 자료가 정수 질량수 A_P를 사용한 per-nucleon convention이면 E_lab=A_Pq와 v_rel=√(2A_Pq/M_P)다. 둘의 수치적 근접성을 의미론적 동일성으로 바꾸지 않는다. 표적이 움직이면 두 속도의 차이로 v_rel을 다시 정의해야 한다. 차원은 [q]=energy, [κ]=energy×length, [μ]=mass이며 c는 비상대론 조건 v_rel/c≪1에서만 생략된 동역학 변수다. ℏ는 전자 Hamiltonian과 그 길이·에너지 단위에 남는다.

원요청의 0.5와 5 keV/u는 조사·비교해야 할 anchor이며, 모든 문헌의 E_cm, lab-keV, relative-velocity 행을 같은 에너지로 간주할 허가는 아니다. isotope, 질량 정규화, frame이 확인되기 전에는 고유한 v_rel 또는 수치적 최근접 거리를 계산하지 않는다.

## 2. 직선 등속 비교 모형

조건부로 상대 위치를 R⃗(t)=(b,0,vt), b≥0,v>0, 최근접 시각 t=0으로 정의한다. 이 정의에서만

\[
 R(t)=\sqrt{b^2+v^2t^2},\qquad R_{\min}=b,\qquad
 \dot R=\frac{v^2t}{R},\qquad |\dot\theta|=\frac{bv}{R^2}.
\]

θ를 +z축에서 +x축 방향으로 재면 b>0에서 θ=atan2(b,vt), θ̇=−bv/R²다. 회전 생성자 부호는 이 각도와 body/lab 변환 정의를 함께 고정한 다음 사용해야 한다. b=0에서는 R=v|t|이고 t=0의 축 방향이 정의되지 않으므로 θ̇=0을 그 점의 정칙성 주장으로 연장하지 않는다.

대칭 시간창 [−T,T]이면 I_R(b,v,T)=[b,√(b²+v²T²)]다. b∈[b_−,b_+], v∈[v_−,v_+]에서 동일 T를 쓰면 전체 반경 envelope는 [b_−,√(b_+²+v_+²T²)]이다. z=vt와 고정 z창 [−Z,Z]를 쓰는 경우에는 [b_−,√(b_+²+Z²)]가 되며 에너지에 따라 시간창 T=Z/v가 바뀐다. R cutoff와 고정 시간창은 같은 입력이 아니다.

전체 산란 t∈ℝ, b∈[0,∞)를 형식적으로 포함하면 R>0 전체와 R↓0, R→∞의 극한이 필요하다. b=0은 impact measure b db에서 측도 0이지만, small-b 적분 제어는 별도로 필요하다. 측도 0이라는 사실은 인접 small-b 수치·물리 오차를 제거하지 않는다.

## 3. 반발 Coulomb–Rutherford 비교 모형

중심 상대 퍼텐셜 U(R)=K/R, K>0, 입사 angular momentum J=μvb와 E=E_cm=μv²/2를 가정한다. 이는 전자 반응을 포함하는 실제 핵 퍼텐셜과 구별되는 비교 모형이다. 방사 운동의 보존법칙은

\[
 \frac{\mu}{2}\dot R^2+\frac{J^2}{2\mu R^2}+\frac{K}{R}=E,
 \qquad |\dot\theta|=\frac{J}{\mu R^2}=\frac{vb}{R^2}.
\]

Turning point에서 ER²−KR−Eb²=0이므로

\[
 \boxed{R_{\min}=\frac{K}{2E}+\sqrt{\left(\frac{K}{2E}\right)^2+b^2}}.
\]

b=0이면 R_min=K/E>0이며, K→0 또는 E→∞에서 R_min→b다. 따라서 straight-line head-on의 R_min=0과 bare repulsive Rutherford head-on의 양의 turning point를 같은 것으로 취급할 수 없다. 고정 K, b∈[b_−,b_+], E∈[E_−,E_+]에서 가능한 최소 반경은 위 식에 b=b_−, E=E_+를 넣은 값이다. 유한 시간창의 R_max는 해당 Rutherford 시간-반경 관계로 정해야 하며 직선식 √(b²+v²T²)를 재사용할 수 없다.

bare 핵 사이에는 K=Z_AZ_Bκ=2κ다. 그러나 He²⁺+H 입사 채널에서 H는 중성 원자다. H에 국소화된 전자의 타핵 퍼텐셜은 큰 R에서 −2κ/R의 monopole을 갖고, 핵 반발 +2κ/R과 선도차수에서 상쇄한다. 따라서 bare K/R 핵 궤적은 neutral-atom entrance의 전자적으로 screening된 에너지 표면과 동일하지 않다. 기존 proxy R_min 수치를 물리적 cutoff로 승격하지 않는 이유다. 여기서는 screening의 전역 보정이나 새로운 핵 force law를 도입하지 않는다.

## 4. 결합된 고전 핵 운동과 공통 전자 에너지 이동

전자 상태와 연동한 핵 운동은 힘의 정의, 전자 에너지/비단열 항 처리, 초기조건이 필요하다. 보존되는 단일 중심 U(R)가 실제 모형이면 turning point는 E=U(R)+J²/(2μR²)의 외부에서 접근 가능한 근으로 정의한다. 일반 시간의존·비중심·전자-핵 연동 모형에서 이 스칼라 방정식 또는 각운동량 보존을 가정하지 않는다. 이 궤적의 검증된 R(t) 범위가 전자구조 데이터의 요청 구간이 된다.

전자 H_e(R)에 공통 scalar V_NN(R)=2κ/R를 더하면 모든 전자 고유값과 essential-spectrum threshold가 함께 이동한다. H_e의 threshold 0은 H_e+V_NN에서는 V_NN이다. 고유벡터와 전자 gap은 변하지 않지만, 핵 운동에서 ∂_R V_NN은 힘에 기여하므로 무시할 수 없다. `전자 gap에서 소거`와 `핵 힘에서 제거`를 구별한다.

## 5. 전자구조 구간과 오차 예산의 연결

전자구조 solver의 입력은 독립적인 compact I=[R_−,R_+]⊂(0,∞), spectral target, observable, 수렴/인증 수준이다. C2d까지 검증한 finite points와 bridge는 그 점들에 대한 경험적 수렴 근거이며 I의 모든 점 또는 모든 collision 궤적의 coverage certificate가 아니다.

후속 finite-window collision 계산은 incoming/outgoing 시간 tail, impact tail, small-b 영역, 내부 electronic discretization, projector/truncation, time integration 오차를 구별해야 한다. 예를 들어 유한 채널에서 동일 Hilbert 공간의 Hermitian generators K(t), K̃(t)가 충분히 정칙하고 ΔK=K−K̃가 operator-norm 적분 가능하면 Duhamel identity로

\[
 \|U(t_1,t_0)-\widetilde U(t_1,t_0)\|
 \le\hbar^{-1}\int_{t_0}^{t_1}\|\Delta K(t)\|\,dt.
\]

증명은 U−Ũ=−(i/ℏ)∫U(t₁,s)ΔK(s)Ũ(s,t₀)ds와 양쪽 unitary norm=1이다. 동일 초기 단위벡터 및 동일 orthogonal channel projector Π에 대해 |P−P̃|≤2||U−Ũ||를 얻는다. 서로 다른 truncated spaces를 embedding하거나 unbounded full-Hamiltonian 차이에 이 bounded-generator 식을 바로 적용할 수 없다. 이 식은 필요한 certificate의 형태를 정할 뿐, 현재 검증되지 않은 ΔK bound나 Big-O 상수를 제공하지 않는다.

σ_f=2π∫₀∞ bP_f(b)db에서 unitarity가 주는 0≤P_f≤1만으로 ∫_B∞ bP_fdb의 유한 상한은 얻지 못한다. 따라서 support proxy, finite window plateau, coupling 두 점의 점근적 근접만으로 impact 또는 time tail을 닫지 않는다. 전자 박스 cutoff r_box와 핵 분리 R_max는 서로 다른 좌표의 경계다.

## 6. 다음 단계의 의존성

원래 DAG는 C2→D1→D2→E1→E2→F1 순서다. F1의 최종 궤적 비교 결과를 C2의 모든 구현 작업의 선행조건으로 만들면 순환 대기가 생긴다. 따라서 이 단계는 조건부 domain mapping과 target API를 확정하고, 궤적과 무관한 spectral-projector 구현을 다음 한 단계로 둔다. 실제 수치 실행에는 exact R 배열, basis/box 설정, 새 projector/gap acceptance와 resource budget을 먼저 등록해야 한다. physical full-C2 coverage와 D1의 기존 gate는 여전히 닫히지 않았다.

이번 단계의 종료는 조건부 수학·입력 의미의 확정이다. production 궤적·유한 b/time 범위, 전역 gap 하한, continuum/observable enclosure는 **unresolved**이고 새로운 eigensolve, scattering propagation, Eq55는 **NOT_RUN**이다.
