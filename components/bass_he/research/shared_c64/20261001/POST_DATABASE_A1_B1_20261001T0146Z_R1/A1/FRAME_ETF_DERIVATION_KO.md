# A1 — 이동하는 두 중심 기저의 metric·frame·ETF connection

판정: **FRAME_CONNECTION_GAP_IDENTIFIED**. 일반 이동기저의 진폭 방정식, Hermitian 표현, 원점·회전·위상 변환법칙을 유도했다. 이 형식에 R10R의 bare bright matrix element를 정확히 배치할 수 있다. 그러나 실제 He–H collision에 사용할 finite-R ETF/점근 채널 embedding과 그 행렬요소는 아직 결정되지 않았다. 따라서 A1 전체가 닫혔다고 판정하지 않으며 A2/C1 이후 collision 계산으로 진행하지 않는다.

## 1. 범위, 원전, 표기

전자 하나, spinless, 비상대론적 점-Coulomb Hamiltonian과 미리 주어진 매끄러운 핵궤적을 사용한다. 현재 유도에서 핵운동 자체는 풀지 않는다. Lab 전자 좌표 r, 핵 위치 X_A(t), X_B(t), 전자 질량 m_e, p=-iℏ∇_r에 대해

\[
H_{\rm lab}(t)=\frac{p^2}{2m_e}
-\frac{\kappa_A}{|r-X_A(t)|}-\frac{\kappa_B}{|r-X_B(t)|},
\qquad \kappa_J=\frac{Z_J e^2}{4\pi\epsilon_0}.
\tag{A1.1}
\]

핵간 반발은 전자에게 동일한 scalar이므로 이 전자 TDSE에서는 생략했다. 핵궤적·에너지 보존을 자체 계산하는 후속 문제에는 별도 필요하다. Clamped 전자 질량 m_e와 P24의 Jacobi reduced electronic mass를 무언중 교체하지 않는다. 상대론·spin·복사·핵 양자산란 정확도를 주장하지 않는다.

원전 연결: P01 Liu2024 §2 Eqs.(3)–(6)는 trajectory AOCC와 ETF/overlap equation, P24 Belyaev–Dalgarno–McCarroll2002 §§II–III Eqs.(11)–(17)는 원점 이동과 전체 핵운동 operator의 상쇄, P03 Liu2003 §I는 finite-R MO ETF ambiguity의 범위를 제공한다. P02 Stolterfoht2010 §II의 전자–고전핵 coupled treatment와 P06 ARSENY §2.6의 특정 회전 convention도 대조했다. 직접 읽은 페이지·DOI·PDF SHA256은 `source_notes/A1_SOURCE_MANIFEST.json`에 있다. 이하 A1 식은 현재의 직접 유도이며, 원문의 동일 식으로 위장하지 않는다.

## 2. 비직교 이동기저에서 출발

N개의 미분 가능한 ket을 열로 모은 X(t)=[|χ_1〉,…,|χ_N〉]를 두고 Ψ_N=Xc로 전개한다. 이 X는 핵 좌표 기호 X_A와 구별되는 기저 사상이다. 시간 구간에서 선형독립이고 Gram matrix S가 positive definite라고 가정한다. 필요한 Hamiltonian/derivative matrix elements가 유한하도록 기저의 form-domain 및 시간 regularity를 요구한다.

\[
S=X^\dagger X,\qquad h_{ab}=q_t(\chi_a,\chi_b),
\qquad D=X^\dagger\dot X.
\tag{A1.2}
\]

q_t는 H_lab의 닫힌 sesquilinear quadratic form이며 첫 인자에 antilinear이다. Coulomb의 form domain H¹에서 kinetic part는 ℏ²/(2m_e)∫∇χ_a*·∇χ_b로 정의한다. 모든 χ_b∈D(H_lab)이면 h=X†H_labX라고 쓸 수 있지만, form-domain 유도에서는 이 강한 operator 표기를 전제하지 않는다. 시간 미분 χdot_a∈L²를 가정한다.

TDSE를 X의 span으로 Galerkin projection하면

\[
i\hbar S\dot c=(h-i\hbar D)c\equiv M c.
\tag{A1.3}
\]

이는 지정된 유한 basis ansatz의 정확한 projected equation이다. Full Hilbert-space exactness 또는 채널 완전성은 별도다. Sdot=D+D†, h=h†이므로

\[
\frac{d}{dt}(c^\dagger Sc)
=c^\dagger(\dot S-D-D^\dagger)c=0.
\tag{A1.4}
\]

일반적으로 S^{-1}M은 Euclidean inner product에서 Hermitian이 아니다. P01의 S^{-1}M 형태에 임의 Hermitian symmetrization을 가하면 다른 방정식을 만들 수 있다. 필요한 보존량은 c†Sc다.

매끄러운 W(t)를 W†SW=I로 선택하고 c=Wa로 두면

\[
i\hbar\dot a=K a,
\quad K=W^\dagger(h-i\hbar D)W-i\hbar W^\dagger S\dot W.
\tag{A1.5}
\]

Y=XW는 직교정규 basis이고 동일한 식은 K_ab=q_t(Y_a,Y_b)-iℏ〈Y_a|Ydot_b〉다. Strong operator 조건이 충족될 때 K=Y†HY-iℏY†Ydot로 쓸 수 있다. W=S^{-1/2}는 한 선택이며 유일하지 않다. 미분한 W†SW=I를 사용하면

\[
K-K^\dagger=-i\hbar\left[
W^\dagger\dot S W+W^\dagger S\dot W+\dot W^\dagger S W\right]=0.
\tag{A1.6}
\]

따라서 정확한 K가 정의되면 그 finite-dimensional propagator는 unitary다. 이는 spatial/channel/continuum truncation error가 작다는 진술이 아니다. 실제로 projector P=X S^{-1}X†와 Q=1-P를 두면

\[
\mathcal R_t(v)=i\hbar\langle v,\dot Xc\rangle-q_t(v,Xc),
\qquad v\in H^1\cap\operatorname{Ran}Q
\tag{A1.7}
\]

는 projected equation이 검사하지 않는 weak residual이다. 추가로 모든 χ_a∈D(H_lab)이고 dotXc∈L²이면 강한 residual Q(iℏdotX-H_labX)c로 표현된다. Norm preservation만으로 이 residual이 제어되지 않는다. R10R에서 사용한 Lψ에 D(H)를 새로 부과하지 않는다.

## 3. Rephasing과 비가환 subspace gauge

동일 span의 다른 기저 X'=XA(t), A가 가역이면 c'=A^{-1}c이고

\[
S'=A^\dagger SA,\quad h'=A^\dagger hA,\quad
D'=A^\dagger DA+A^\dagger S\dot A,
\tag{A1.8}
\]
\[
M'=A^\dagger MA-i\hbar A^\dagger S\dot A.
\tag{A1.9}
\]

직교정규 표현에서 U(t) unitary를 사용하면

\[
K'=U^\dagger K U-i\hbar U^\dagger\dot U,
\qquad a'=U^\dagger a.
\tag{A1.10}
\]

U=diag(e^{iα_a})는 local state rephasing이며 diagonal connection에 +ℏ αdot_a가 생긴다. Degenerate subspace에서는 U를 전체 unitary block으로 두어야 한다. 개별 state phase를 고정하거나 energy gap으로 나누는 scalar formula는 퇴화점의 일반 prescription이 아니다. Isolated cluster의 projector가 매끄럽다는 추가 spectral assumption이 있어야 projectors/subspace continuation을 쓸 수 있다. 이 연구에서 그 물리 cluster gap을 증명하거나 계산하지 않았다.

## 4. 하나의 active origin/rotation convention

Rvec=X_B-X_A=Q(t) R e_z, r=O(t)+Q(t)x로 둔다. Q∈SO(3)는 body→lab active rotation이고 Q^T Qdot x=Ω×x, V=Q^T Odot다. R10P와 같이 internuclear axis z, collision plane xz, 회전축 y를 사용한다. Hilbert-space 사상은

\[
[\mathcal U_{O,Q}\phi](r)=\phi(Q^T[r-O]),
\quad \mathcal U_{O,Q}=T(O)\mathcal D(Q),
\quad T(O)=e^{-iO\cdot p/\hbar}.
\tag{A1.11}
\]

Planar case에서 D(Q)=exp(-iθ L_y/ℏ), L_y=-iℏ(z∂_x-x∂_z)이다. Chain rule 또는 group generator로

\[
\mathcal U^\dagger\dot{\mathcal U}
=-\frac{i}{\hbar}(V\cdot p+\Omega\cdot L).
\tag{A1.12}
\]

Unboosted orthonormal clamped states φ_a(x;R), H_bodyφ_a=E_aφ_a를 택하면 F_R,ab=〈φ_a|∂_Rφ_b〉는 anti-Hermitian이고

\[
K^{(0)}_{ab}=E_a\delta_{ab}-i\hbar\dot R F_{R,ab}
-\Omega\cdot L_{ab}-V\cdot P_{ab}.
\tag{A1.13}
\]

추가 time-dependent channel gauge를 쓰면 A1.10을 적용한다. Diagonal electronic phases를 미리 basis에 넣는 interaction picture에서도 이 gauge 항을 포함해야 E를 중복 계산하지 않는다. E, F_R, L, P는 반드시 동일 basis·origin·phase에 속한다.

단위: E,K는 energy, F_R는 length^{-1}, L은 action, P는 momentum, Ω는 time^{-1}, V는 velocity이다. 네 항 모두 energy이고 ℏ는 유지된다. K^(0)의 Hermiticity는 F_R†=-F_R, L†=L, P†=P로 확인된다.

## 5. R10R bright term과 기존 Q12의 위치

R10R의 지정된 charge-center origin O_c와 real-positive meridional phase에서

\[
L_{gb}^{O_c}=-i\hbar\frac{C_R T_R}{\Delta_R}\ne0
\quad(R>0\text{ fixed},\ \kappa_B>\kappa_A>0).
\tag{A1.14}
\]

따라서 위 active convention의 unboosted matrix에는

\[
K^{\rm rot}_{gb}=-\dot\theta L_{gb}^{O_c}
=+i\hbar\dot\theta\frac{C_R T_R}{\Delta_R},
\quad K^{\rm rot}_{bg}=(K^{\rm rot}_{gb})^*.
\tag{A1.15}
\]

이는 R10R theorem의 위치를 정한 것이며 coupling 크기 계산은 아니다. R10R의 Lψ∈H¹ form-domain 근거를 재사용하고 Lψ∈D(H)를 새로 요구하지 않는다. Phase를 바꾸면 이 행렬요소의 복소 위상도 바뀐다. ETF-dressed state의 항은 원래 bare 값에 추가 rate를 더하여 얻을 수 없다.

Q12에 연결될 radial amplitude 항은 동일 state set에서 -iℏ Rdot F_R,ge이다. 기존 pinned `eq50_scoped.py`에서 Q12는 hidden-crossing branch `(1,0,0)↔(2,1,0)` 및 complex crossing 좌표를 가진다. 그 branch의 확률 또는 transition probability만으로 F_R,ge(t)와 coherent phase를 복원할 수 없다. Phase를 잃은 probability data로 coherent dynamics를 초기화하는 것은 추가적인 미해결 역문제다.

같은 final state g에 직접 e→g와 e→b→g가 기여한다면 time-ordered Dyson amplitude에서 더해진다. Full K를 사용하는 propagator는 이를 이미 포함한다. 여기에 기존 Q12 확률과 angular 확률을 별도로 더하거나 두 번째 transition operator를 삽입하면 동일 물리를 중복 계수할 수 있다. A1은 그 coherent K의 구성을 요구하고, S1/S2에 맞춰 rate를 선택하지 않는다.

P06 Eq.(47)의 +ωL_z와 A1.13의 -θdot L_y 사이에는 좌표축 permutation뿐 아니라 ω의 orientation 정의가 필요하다. R10P에 기록된 `(x_CPC,y_CPC,z_CPC)=(z,x,y)`는 proper rotation이며 자체로 부호를 뒤집지 않는다. ω=-θdot는 추가 convention을 명시했을 때의 조건이지 이번에 검증된 author-code identity가 아니다.

## 6. 원점 이동의 정확한 상쇄

O'=O+Q s(R,t), x'=x-s이고 같은 physical basis를 φ'_a(x';R,t)=φ_a(x'+s;R)로 표현한다. Then

\[
P'=P,\quad L'=L-s\times P,\quad
V'=V+\Omega\times s+\dot s.
\tag{A1.16}
\]

Intrinsic basis derivative에는 〈φ|sdot·∇φ〉=(i/ℏ)sdot·P가 추가되므로 effective connection에 +sdot·P가 생긴다. 따라서

\[
-\Omega\cdot(L-s\times P)
-(V+\Omega\times s+\dot s)\cdot P+\dot s\cdot P
=-\Omega\cdot L-V\cdot P.
\tag{A1.17}
\]

벡터 항등식 Ω·(s×P)=(Ω×s)·P가 핵심이다. s=s(R)이면 +sdot·P는 radial derivative F'_R=F_R+(i/ℏ)(∂_R s)·P에 들어간다. 원점에 따라 L과 F_R 각각이 달라져도 전체 equation은 동일하다. 동일한 기저를 정확히 변환한 관계에서 이 상쇄는 finite span에서도 성립한다. 다른 원점에서 independently truncated basis를 다시 선정하면 같은 span이라는 전제를 별도로 검증해야 한다.

핵 질량 M_A,M_B를 사용하면 CNM과 charge center의 차이는

\[
O_c=O_{\rm CNM}+\gamma Rvec,\qquad
\gamma=\frac{\kappa_BM_A-\kappa_AM_B}{(\kappa_A+\kappa_B)(M_A+M_B)}.
\tag{A1.18}
\]

즉 CNM→O_c에서 s=γR e_z이고 Odot의 lever/translation correction을 반드시 포함한다. Isotope masses는 이 식의 입력이며 nominal mass-number를 실제 질량으로 바꾸지 않았다.

## 7. 공통 boost의 정확한 검사

Body basis에 공통 multiplication B=exp[i m_e u(t)·x/ℏ+iγ_b(t)]를 적용한다. γ_b는 여기서 scalar phase이며 A1.18의 origin coefficient γ와 구별된다. B†pB=p+m_eu이고 B†LB=L+m_e x×u이므로

\[
\begin{aligned}
K_B={}&H_{\rm body}+(u-V)\cdot p-\Omega\cdot L
 +m_e\dot u\cdot x-m_e\Omega\cdot(x\times u)\\
 &+\tfrac12m_eu^2-m_eV\cdot u+\hbar\dot\gamma_b,
\end{aligned}
\tag{A1.19}
\]

여기에 φ(R)의 -iℏ Rdot F_R와 channel gauge가 일관되게 투영된다. u=V, ℏγdot_b=m_eV²/2를 선택하면 scalar가 소거되고 inertia term은 m_e(dotV+Ω×V)·x이다. 이것은 body components로 본 origin acceleration이다. 일정한 lab velocity와 Ω=0에서는 H_body가 회복된다. Lab 표현은 exp[i(m_ev·r-m_ev²t/2)/ℏ]이어서 P01의 상수속도 ETF와 차원이 맞는다.

공통 boost 하나로 서로 다른 두 핵의 asymptotic electron transport를 동시에 완성할 수는 없다. 이 검사는 sign/translation consistency를 확립하며 two-center channel ETF 선택의 증거는 아니다.

## 8. 채널별 ETF를 넣는 정확한 자리

우선 같은 bare lab state ψ_a=U_{O,Q}φ_a를 사용하고 χ_a=e^{iη_a(r,t)}ψ_a로 정의한다. Real differentiable η_a가 명시되면

\[
\begin{aligned}
S_{ab}&=\langle\psi_a|e^{i(\eta_b-\eta_a)}|\psi_b\rangle,\\
D_{ab}&=\langle\psi_a|e^{i(\eta_b-\eta_a)}
 |\dot\psi_b+i\dot\eta_b\psi_b\rangle,\\
h_{ab}&=\langle\psi_a|e^{i(\eta_b-\eta_a)}
 \left[\frac{(p+\hbar\nabla\eta_b)^2}{2m_e}+V_{\rm Coul}\right]|\psi_b\rangle.
\end{aligned}
\tag{A1.20}
\]

마지막 operator 표기는 strong operator 조건이 성립하는 경우에 사용한다. Form-domain에서는 g_a=(∇+i∇η_a)ψ_a를 두고 h_ab=ℏ²/(2m_e)∫e^{i(η_b−η_a)}g_a*·g_b+∫e^{i(η_b−η_a)}ψ_a*V_Coulψ_b로 정의한다. Multiplication phase가 H¹을 보존하도록 필요한 regularity를 가정한다. 여기서 kinetic square는 operator product이며 p와 위치에 따라 변하는 ∇η의 commutator를 포함한다. 원자별 일정 velocity를 사용하는 대표적인 선택은

\[
\eta_a(r,t)=\frac{m_e v_{C(a)}\cdot r-m_ev_{C(a)}^2t/2}{\hbar}+\alpha_a(t),
\tag{A1.21}
\]

이다. 시간에 따라 변하는 velocity로 일반화하려면 phase와 fixed-lab-r time derivative를 명시하고 acceleration 항을 포함해야 한다. 위 S,h,D를 A1.5에 넣으면 하나의 Hermitian amplitude equation을 얻는다. 채널별 phase를 붙인 후에도 h=diag(E), S=I라고 가정하는 것은 일반적으로 옳지 않다. A1.13의 항과 ETF correction을 별도로 모아서 더하지 않고, 정의된 χ 전체에서 S,h,D를 한 번 계산한다.

이번 문서는 특정 η_a의 finite-R 선택을 확정하지 않았다. R10R의 molecular g,b와 incoming σ channel을 asymptotic localized states에 대응시켜야 한다. 특히 separated-atom H(1s)와 He⁺(n=2)의 clamped-Coulomb energy는 무한 핵질량 근사에서 같으므로, 개별 adiabatic state label만으로 parent center를 정하는 처방은 일반적으로 부족하다. Reduced masses/isotope effects를 넣으면 exact degeneracy 자체도 다시 평가해야 한다. 이번에는 localized degenerate-subspace projectors, finite-R switching, overlap spectrum을 구하지 않았다. 이는 기저와 근사 설계의 미완결성이며 새로운 자유 물리매개변수를 benchmark에 맞춰 고르라는 뜻이 아니다.

## 9. 全量子核問題との境界

P24의 Jacobi 구조와 비교하자. x=r-γRvec에서 γ가 일정하면 ∇_R|r=∇_R|x-γ∇_x이므로

\[
-\frac{\hbar^2}{2\mu_N}\Delta_R\big|_r
=-\frac{\hbar^2}{2\mu_N}\Delta_R\big|_x
+\frac{\gamma\hbar^2}{\mu_N}\nabla_R\cdot\nabla_x
-\frac{\gamma^2\hbar^2}{2\mu_N}\Delta_x.
\tag{A1.22}
\]

Second derivative/mixed derivative를 포함한 전체 operator의 변환이 필요하며, A1.13의 trajectory equation으로 이를 단순 대체할 수 없다. P24의 full coupled nuclear equation에 대한 coordinate independence와 여기서 유도한 prescribed-classical-path 전자 equation의 covariance는 적용 범위가 다르다. 후자를 유도했다고 fully quantum nuclear scattering을 검증한 것으로 간주하지 않는다.

## 10. 실제 검증과 남은 closure 조건

실제 수행한 것은 origin-vector identity, metric derivative, Hermitian orthonormalization의 Wolfram 대수 검산과 작은 행렬 fixture 12개다. 첫 실행에서는 11개가 PASS였고 bright-term 1개가 부동소수 완전일치 assertion에서 실패했다. 물리식과 사전 허용오차를 바꾸지 않고 이미 정한 2e-12 tolerance를 사용하도록 assertion을 고쳐 12개 PASS를 얻었다. 실패 로그도 보존했다. Wolfram context lookup은 connector 내부 오류였고, algebra evaluator는 계산 결과를 반환하면서 undefined-symbol wrapper warnings를 출력했다. 원 응답과 명시적으로 구분한 transcript에 검증 범위를 기록한다.

유도한 범위는 A1.3–A1.10의 transport/covariance, A1.13–A1.19의 common-frame sign/origin/boost 구조 및 bare R10R 항의 위치다. 이 대수 검산은 physical completeness의 증명이 아니다. 독립 검토 판정은 `../review` 기록에 있다.

남은 최소 physical closure 과제는 (i) asymptotic localized channel/subspace와 finite-R continuation 정의, (ii) 그 χ의 S,h,D와 S의 비특이성, (iii) incoming/outgoing projector와 동일 physical boundary state의 frame 비교, (iv) bare Q12 probability representation에 의존하지 않는 radial amplitude 데이터의 구성이다. 이를 명시한 후 수치 solver 구현으로 연결해야 한다.

다음 단일 node는 **A1b ASYMPTOTIC_CHANNEL_EMBEDDING_AND_ETF_CHOICE**다. A2/C1–G1은 선행 조건 미충족으로 NOT_RUN이며 Eq55=NOT_RUN, scientific_PROMOTE=HOLD를 유지한다.
