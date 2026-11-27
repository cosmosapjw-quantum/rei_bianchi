# C1b 수학 사전검토: B 중심 spherical reference와 물리 원점 O

검토 범위는 기존 C1 계약의 R=2 a_A, Z_A=1, Z_B=2, fixed m=0 ground g와 real-cosφ |m|=1 ground b다. 물리 Hamiltonian, 상태와 L_y의 원점 O는 바꾸지 않는다. 변경은 독립 spherical hp-FEM의 수치 전개 중심을 B로 옮기는 것이다. 이 문서는 수학적 사전검토이며 새 물리 eigensolve 또는 수렴 판정을 수행하지 않았다.

읽은 근거는 C1b CONTRACT.json 및 NUMERICAL_CONTRACT.json, C1 C1_ELECTRONIC_DERIVATION_KO.md, code/partialwave.py, source_notes/C1_PRIMARY_SOURCES_KO.md, root AGENTS.md다. 아래 식은 문헌의 숫자를 전사한 것이 아니라 그 convention에서 직접 유도했다. C1의 기존 원전·hash provenance를 재사용하며 새 문헌 또는 PDF를 추가하지 않았다.

## 1. 단위와 좌표의 분리

H=−ℏ²∇²/(2m_e)−κ_A/r_A−κ_B/r_B, a_A=ℏ²/(m_eκ_A), E_A=ℏ²/(m_ea_A²)다. 이후 r,R,E 및 ∂r는 각각 a_A,E_A 단위의 무차원 변수다. 계산식에서 Z_A=1,Z_B=2이며 핵 반발항은 없다. ℏ를 포함한 물리량은 ℒ=L_y/(−iℏ), P=p_x/(−iℏ/a_A), D=d_x/a_A로 표시한다.

O의 핵 위치는 z_A=−Z_B R/(Z_A+Z_B), z_B=Z_A R/(Z_A+Z_B)다. B 중심 좌표 s=(x,y,z−z_B), r=|s|, η=s_z/r에서는 A가 a_Acenter=−R, B가 a_Bcenter=0에 있다. 여기의 signed center a_C는 보어길이 a_A와 다른 기호다. 아래 force 식에서는 혼동을 피하려고 signed center를 a라고 쓴다.

축방향 평행이동이므로 azimuth φ와 m sector가 변하지 않는다. 표적은 여전히 같은 물리 fixed-sector ground pair다. 무한공간에서 두 좌표 선택은 unitary translation으로 동등하지만, 유한 ℓ 및 서로 다른 중심의 유한 구는 동일한 trial subspace가 아니다. 따라서 O-centered와 B-centered finite 결과의 차이를 순수 연산자 좌표변환 오차라고 부르면 안 된다.

물리 각운동량의 정확한 관계는

L_y(O)=(z_B+s_z)p_x−x p_z=L_y(B)+z_B p_x,

따라서 ℒ_O=ℒ_B+z_B P다. 부호는 **+**다. 한 물리 상태를 두 방식으로 평가하는 이 identity와, 각각 다른 유한 basis에서 재계산한 상태들의 수렴 비교는 별개의 검사다.

## 2. Independent projected momentum과 dipole

기존 no-Condon–Shortley convention을 그대로 사용한다:

A_{ℓ0}=√[(2ℓ+1)/2]P_ℓ(η),
A_{k1}=√[(2k+1)/(2k(k+1))]√(1−η²)P'_k(η).

G=Σu_{gℓ}(r)A_{ℓ0}/r, B=Σu_{bk}(r)A_{k1}/r,
ψ_g=G/√(2π), ψ_b=B cosφ/√π, Σ∫u²dr=1.

φ를 적분하면

P=(1/√2)∫r²dr dη G[√(1−η²)∂r B−η√(1−η²)∂η B/r+B/(r√(1−η²))].

q=1−η²와 Legendre equation qP''_k−2ηP'_k+k(k+1)P_k=0을 쓰면 radial derivative의 angular 계수는 ∫A_{ℓ0}qN_{k1}P'_k이고, 나머지 radial u/r 계수는 ∫A_{ℓ0}N_{k1}ηk(k+1)P_k다. qP'_k=k(k+1)(P_{k−1}−P_{k+1})/(2k+1) 및 ηP_k=[(k+1)P_{k+1}+kP_{k−1}]/(2k+1)로

α_k=√[k(k+1)/((2k−1)(2k+1))],
β_k=√[k(k+1)/((2k+1)(2k+3))]

를 정의하면

P=(1/√2)Σ_{k≥1}{α_k∫u_{g,k−1}(u'_{bk}+k u_{bk}/r)dr−β_k∫u_{g,k+1}(u'_{bk}−(k+1)u_{bk}/r)dr},

D=(1/√2)Σ_{k≥1}{α_k∫r u_{g,k−1}u_{bk}dr−β_k∫r u_{g,k+1}u_{bk}dr}.

누락된 ℓ 계수는 0으로 해석한다. 서로 다른 radial mesh이면 element 경계의 합집합에서 적분한다. P를 ΔD로 **정의하지 않는다**. 별도 미분식으로 계산해야 momentum commutator를 검사할 수 있다. 정확한 bound eigenstates에는 P=ΔD이며 Δ=(E_b−E_g)/E_A>0이다.

기존 angular action은 B 중심에서

ℒ_B=Σ_{ℓ≥1}√[ℓ(ℓ+1)/2]∫u_{gℓ}u_{bℓ}dr

로 유지한다. 이 세 lane은 force 또는 Δ를 입력으로 사용하지 않는다. 연산자 구조는 L_B가 Δℓ=0, p_x와 x가 Δℓ=±1이라는 독립 selection check를 제공한다.

## 3. Singular force의 exact finite angular projection

수치 중심에서 signed axial displacement a에 있는 핵의 potential은 V_C=−Z_C/√(r²+a²−2arη)다. 원래 force integral은

T_C=(1/√2)∫r²drdη [r√(1−η²)]G B/r_C³.

Q_{ℓk}(η)=A_{ℓ0}A_{k1}√(1−η²)=N_{ℓ0}N_{k1}(1−η²)P_ℓP'_k로 놓는다. a≠0이면

∂ηV_C=−Z_C a r/r_C³,

T_C=(1/(√2 Z_C a))Σ_{ℓk}∫u_{gℓ}u_{bk}[∫_{−1}^{1}Q'_{ℓk}(η)V_C(r,η)dη]dr.

원래 T_C의 radial r와 potential derivative의 r가 상쇄된다. 특히 A의 a=−R에서는 prefactor가 −1/(√2 Z_A R)다. 적분 부분의 부호와 함께 사용해야 한다.

경계항 QV_C는 r≠|a|에서 0이다. r=|a|의 핵 endpoint에서도 Q=O(δ), V_C=O(δ^{−1/2})이므로 QV_C=O(δ^{1/2})→0이다. Q'V_C는 O(δ^{−1/2})로 적분 가능하다. 따라서 cusp를 임의 smoothing하거나 endpoint를 제외할 필요가 없다.

Q'의 차수는 최대 ℓ+k이므로 Legendre moments n≤ℓ+k만 필요하다. V_C=Σv_n(r)P_n(η), v_n=−Z_C sign(a)^n min(r,|a|)^n/max(r,|a|)^{n+1}를 사용하면 이 finite-state force angular integral은 **정확한 유한 합**이다. r=|a|에서 무한 potential series를 pointwise 수렴한다고 가정할 필요가 없다. 각 polynomial moment를 적분 가능한 Coulomb potential의 moment 또는 내부/외부 극한으로 정의하면 된다. Radial integral은 r=|a|에서 나누며 quadrature와 h/p 오차는 별도로 남는다.

a=0은 위 식에서 수치적으로 a→0 극한을 취하지 않는다. 별도 식

T_0=(1/√2)Σ_{ℓk}[∫Q_{ℓk}dη]∫u_{gℓ}u_{bk}/r² dr

을 사용한다. ∫Q는 ℓ=k−1에서 α_k, ℓ=k+1에서 −β_k다. Endpoint u(0)=0인 conforming piecewise polynomial이면 이 적분은 유한하다. 첫 element의 u_g u_b/r² cancellation을 안정적으로 구현해야 한다.

물리 torque 변환은

ℒ_B^{force}=−Z_A R T_A/Δ,
ℒ_O^{force}=[Z_AZ_B R/(Z_A+Z_B)](T_B−T_A)/Δ.

Force assembly 자체에는 E, Δ, direct L 또는 direct P가 들어가지 않아야 한다. Δ는 마지막 commutator 변환에만 쓴다. 이 방법은 potential multipole moments를 Hamiltonian과 공유하므로 완전히 독립된 Coulomb assembly는 아니다. 독립 derivative-polynomial kernel과 별도 spatial quadrature spot-check가 구현상의 공통 오류를 줄인다.

또한 같은 ℓ_max 및 radial space에서 B-origin L_y는 해당 angular trial space를 보존한다. 따라서 projected H와 projected L_B의 commutator가 이미 finite space에서 정확히 닫힐 수 있다. **B direct/force 일치만으로 ℓ 수렴을 주장하면 안 된다.** O-origin의 momentum 이동항은 Δℓ=±1이어서 finite angular boundary를 만나지만, 그 consistency도 독립 prolate 크기 비교와 refinement를 대신하지 않는다.

## 4. 유한 Dirichlet 구의 boundary stress

앞의 continuum torque equality를 B 중심 유한 구에 무조건 적용하면 안 된다. D_B=s_z∂x−x∂s_z는 경계에 접하지만 D_O=D_B+z_B∂x는 그렇지 않다. **정확한 finite-box eigenstates**에 Green identity를 적용하면

ℒ_O−ℒ_O^{force}=z_B/(2Δ)∮_{r=r_max}n_x(∂nψ_g)(∂nψ_b)dS.

무차원 Hamiltonian −∇²/2의 계수이므로 1/2가 생긴다. 부호는 +다. 경계에서 ψ=0이고 D_Oψ_b=z_B n_x∂nψ_b라는 점을 사용했다. ℒ_B에는 이 표면항이 없다. 반면 xψ_b는 Dirichlet boundary condition을 보존하므로 P=ΔD에는 같은 표면항이 없다.

위 surface integral은 (1/√2)Σ_{ℓk}(∫Q_{ℓk}dη)u'_{gℓ}(r_max)u'_{bk}(r_max)로 평가할 수 있다. 하지만 유한 FEM state에는 공간 residual도 남으므로 이 표면항만 빼서 exact identity를 강제하면 안 된다. 이 식은 boundary와 spatial error를 분리하는 진단식이다. r_max가 크다는 정성적 이유만으로 surface contribution이 기준 이하라고 단정하지 않는다. Inner mesh를 보존하는 domain extension이 tail 위험을 따로 검사해야 한다.

## 5. Cusp centering이 바꾸는 것과 남기는 것

B 중심에서는 강한 Z_B cusp가 radial 원점에 놓인다. Local angular component ℓ의 Frobenius expansion은 r^ℓ[c_0−Z_B c_0 r/(ℓ+1)+O(r²)]다. 따라서 ℓ=0의 s cusp와 ℓ=1의 bright regularity를 각각 radial basis가 근사할 수 있다. Endpoint u(0)=0만으로 이 Frobenius power와 cusp slope를 정확히 강제한 것은 아니다.

A의 cusp는 r=R, η=−1에 남는다. 이 구면 위 r_A=R√[2(1+η)]이므로 g의 local s cusp가 가진 √(1+η) 항은 angular analytic 함수가 아니다. 이를 정량적으로 보는 **국소 모델 항**은

I_ℓ=∫_{−1}^{1}(1+η)^{1/2}P_ℓ(η)dη
=2^{3/2}Γ(3/2)²/[Γ(3/2−ℓ)Γ(ℓ+5/2)]
=(-1)^{ℓ+1}/[√2(ℓ−1/2)(ℓ+1/2)(ℓ+3/2)].

따라서 이 한 항의 normalized Legendre coefficient는 O(ℓ^{−5/2})다. 이는 fixed r=R에서의 endpoint cusp 설명이며, **전체 3D eigenenergy, direct coupling, force 또는 Ritz sequence의 오차율이나 유한 ℓ_max 충분성 증명이 아니다.** Radial integration, 다른 smooth terms, 실제 cusp amplitude와 bright-state vanishing이 서로 다르다. 지수 angular convergence를 가정하거나 이 국소 지수를 fitting/extrapolation에 사용해 실제 수렴 검사를 대체하지 않는다.

Z_B>Z_A이고 상태가 B 부근에 집중될 때 centering이 유리할 것이라는 판단은 설계 동기다. R=2에서 개선량은 실행 결과가 결정한다. 핵 중심 radial basis도 다른 핵 cusp와 tail을 자동으로 해결하지 않는다.

Spherical hp-FEM은 prolate separated weighted B-spline과 좌표, basis, coupled matrix assembly, eigenvalue formulation이 다르므로 독립 representation 자격을 유지한다. 단지 기존 O-centered spherical code의 refinement와 완전히 별개인 제3 solver라고 부르지는 않는다. Dense angular coupling의 block 수는 대략 O(ℓ_max²), 총 unknown은 (ℓ_max−m+1)(n_element p−1)이다. Sparse factorization의 fill과 Python assembly memory는 이 산술 차수만으로 보장되지 않으므로 실제 resource cap을 유지한다.

## 6. Residual·gap·검사 범위

Symmetric generalized matrix의 작은 algebraic residual은 해당 유한 matrix eigenpair를 검증한다. Radial C0 FEM의 derivative jumps 때문에 strong distributional PDE residual을 L² residual로 오인하면 안 된다. Full-space bound에는 적절한 dual-form residual 또는 domain에 맞는 strong residual과 verified continuum gap이 별도로 필요하다.

두 번째 Ritz root에서 얻는 λ_2^h−λ_1^h는 같은 discretization의 empirical separation이다. 두 Ritz 값이 upper bounds라는 사실만으로 그 차이가 exact gap의 lower bound가 되지는 않는다. 따라서 `continuum_certificate=NOT_CLAIMED`가 맞다. Exact integration을 전제한 conforming min–max, finite quadrature, floating-point eigensolve를 구분한다.

변경 범위에 직접 대응하는 clean checks는 다음과 같다.

- Closed-form radial hydrogenic fixture: u_g=2Z^(3/2)r e^(−Zr), u_b=Z^(5/2)r²e^(−Zr/2)/(2√6), l_g=0,l_b=1. ℒ_B=0, D=128√2/(243Z), P=16√2 Z/81, Δ=3Z²/8이며 P=ΔD. 이 fixture는 momentum 부호·1/√2·radial derivative와 translation을 독립 검산한다.
- 서로 다른 ℓ의 polynomial radial fixture로 Δℓ=0와 ±1 selection 및 α_k,β_k 부호를 검사한다. Forbidden pair가 roundoff 수준이어야 한다.
- Shifted-center force kernel을 closed-form 또는 고정 함수 spatial integral과 비교한다. a<0 및 a>0를 각각 검사하고 a=0 branch를 별도 검사한다. 이는 eigensolve 반복 없이 구현 인자와 부호를 점검한다.
- 같은 B numerical state에서 direct translation identity를 검사하고, 별도 O-centered state와의 차이는 independent basis convergence 항목으로 남긴다.
- ℓ, radial h/p, quadrature, outer domain을 계약처럼 분리한다. 고정 inner mesh의 tail-only extension과 surface diagnostic으로 box boundary 항을 확인한다.
- Invalid center/charge/domain 및 state convention mismatch를 fail closed로 처리한다. Continuum gap과 convergence를 test fixture만으로 PASS 처리하지 않는다.

## 7. 사전 판정

**DERIVED / 수학 설계 적합.** B-centering, positive origin-shift sign, projected direct momentum/dipole, exact finite force moment formulation은 주어진 convention과 양립한다. Cusp 처리 개선은 plausible design motivation이며 실제 convergence는 아직 미판정이다. Singular torque의 finite angular projection은 2D force quadrature 부담을 줄일 수 있으나 projected-commutator redundancy와 finite-box boundary term을 결과 해석에 반드시 반영해야 한다.

사전검토는 C1b tolerances, gate 또는 cap을 변경하지 않았다. Numerical execution과 independent evidence review가 끝나기 전 `electronic_discretization_converged`를 true로 바꾸지 않는다. `scientific_PROMOTE=HOLD`, `Eq55=NOT_RUN`, production 변경 금지를 유지한다.
