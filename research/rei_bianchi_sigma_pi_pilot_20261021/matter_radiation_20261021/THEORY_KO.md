# Matter와 radiation을 분리해야 하는 이유와 예상 응답

## 1. 텐서의 합과 magnitude의 합은 다르다

동일 orthonormal frame에서 π_tot=π_m+π_r이고 기존 norm은 |π|²=π_ab π^ab/2다. 따라서 일반적으로

\[
\Pi_{tot}^2=\Pi_m^2+\Pi_r^2+2\Pi_m\Pi_r\cos\theta,
\qquad
\cos\theta=\frac{\pi^{(m)}_{ab}\pi_{(r)}^{ab}}{2|\pi_m||\pi_r|}.
\]

이 pilot의 공축 LRS에서는 cosθ=sign(p_m p_r)이고,
\(\Pi_{tot}=|\widetilde\Pi_m+\widetilde\Pi_r|\)다. 성분의 magnitude만 저장하면 같은 총 응력으로 보이는 서로 다른 초기조건을 구별할 수 없다. component signed value, magnitude, 합의 magnitude를 모두 저장한다. 좌표 covariant tensor는 metric factor가 필요하므로 여기서 저장/표시하는 diag(-p,-p,2p)는 orthonormal tensor라고 명시한다.

## 2. 같은 순간 H를 써도 시간 의존성이 다르다

사실상 비상대론적 collisionless matter의 이방 pressure는 고정된 geometry를 기준으로 대략 a^-5로 감소한다. massless radiation의 pressure는 대략 a^-4다. matter-dominated 배경에서 H²∝a^-3이면 각각의 무차원 응력은 대략 a^-2와 a^-1이다. 실제 solver는 massive dispersion, Λ, shear-induced quadrupole, 공통 geometry feedback를 모두 기존 source대로 계산하므로 이 단순 power law를 integration rule로 대체하지 않는다.

이를 해석용 근사로만 사용하면 x=ln(a/a_ref), S=√3s/H에서

\[
S'+\frac32S=\widetilde\Pi_{m0}e^{-2x}+\widetilde\Pi_{r0}e^{-x},
\]

\[
S(x)=S_0e^{-3x/2}
+2\widetilde\Pi_{m0}(e^{-3x/2}-e^{-2x})
+2\widetilde\Pi_{r0}(e^{-x}-e^{-3x/2}).
\]

이 식은 matter-dominated H, prescribed stress dilution, geometry-induced stress perturbation을 무시한 reference response다. 실제 coupled system의 일반 선형해라고 부르지 않는다. Wolfram의 첫 DSolve 반환에는 내부 message가 있었으며 이를 보존했다. 반환식을 독립적으로 대입한 ODE residual 및 초기 residual은 실제 symbolic evaluation에서 각각 0이었다. 기록은 WOLFRAM_MATTER_ERA_APPROX.json이다.

a_end/a_ref=21/5=4.2에서 이 근사의 계수는

\[
S_{end}\approx0.1161785801S_0
+0.1189784754\widetilde\Pi_{m0}
+0.2438333160\widetilde\Pi_{r0}.
\]

초기 총 응력이 같은 두 모형이라도 matter/radiation 조성이 다르면 최종 shear가 달라질 수 있다. 특히 S0=0, Pi_m0=-Pi_r0이면 초기 총 응력은 0이어도 위 reference의 최종 signed shear는 약 -0.1248548405 Pi_m0다. 새 mixed6조건은 이 현상이 실제 원본 source의 coupled evolution에서도 나타나는지 확인한다. 이 수치 근사나 기존 separate-slice 결과의 선형 합으로 mixed 결과를 대신하지 않는다.

## 3. 실제 계산의 에너지 분리

원본 source는 물질과 복사의 moment를 따로 제공한다. scalar p_m,p_r를 합친 값이 shear source이고, 각각의 anisotropic work는

\[
\left.\rho_m'\right|_{aniso}=-6(s/H)p_m,\qquad
\left.\rho_r'\right|_{aniso}=-6(s/H)p_r.
\]

이들은 서로 다른 성분의 expansion work이며, 충돌을 통한 직접적인 matter–radiation 교환 항을 추가한 것이 아니다. full energy equation에는 각 성분의 isotropic dilution도 포함된다. 합산된 Einstein constraint의 전파는 split conservation equations로도 그대로 성립한다. WOLFRAM_SPLIT_ALGEBRA.json의 계산에서 constraint derivative=0이다.

원래 background equation의 비교 원전: Agullo–Olmedo–Sreenath, Bianchi I background, https://arxiv.org/html/2003.08428v2 . 원본 구현은 parent SOURCE_ATTRIBUTION.json에 고정된 PR147 canonical_momentum source이며, 이번 분리에서 byte를 변경하지 않는다. 첨부 BASS harness의 stress-energy ledger 의무는 ATTACHMENT_INTAKE.md에 해당 원문 위치와 제한된 조사 범위로 기록했다. 그 과거 harness의 admission을 이번 독립 LRS에 옮기지 않는다.
