# PHYS21 독립 기여: physical-birth-angle의 scalar 2차 응답

이 문서는 `/root/phys21_tensor`가 후보 생성과 검산에 기여한 결과다. 최종 decision review가 아니며 자체 PROMOTE를 발행하지 않는다. `physical=HOLD`를 유지한다. 근거 상태는 아래 수식에 대해 **derived**, 명시된 다섯 diagnostic에 대해 **numerically checked**다. Production FT03 evolving-gas, native solver, source/default, runtime returns는 실행하거나 변경하지 않았다.

## 1. 정의·범위

`PHYS20/NEXT_HANDOFF_KO.md` 및 보고서 §§3–4를 입력으로 읽었다. metric signature는 `(-,+,+,+)`, t는 comoving proper time이며

\[
ds^2=-c^2dt^2+a^2(t)\sum_i e^{2\epsilon B_i(t)}(dx^i)^2,
\qquad\sum_i B_i=0.
\]

평균 expansion과 gas density/history는 ε에 독립적으로 고정한다. 물리적으로 등방인 birth cohort의 방출 시각 b와 에너지 E_b도 고정한다. 이번 기여는 고정 principal axes, scalar cross section 및 smooth threshold-separated 구간을 다룬다. 시간에 따라 회전하는 고유축이나 scalar gas의 2차 feedback을 새로 가정하지 않는다.

physical birth direction을 \(\boldsymbol m\), \(|\boldsymbol m|=1\)이라 쓰고

\[
A_s=B(s)-B(b),\qquad
E_0(s)=E_b\frac{a(b)}{a(s)},\qquad
R_s=\frac{E(s)}{E_0(s)}
=\left[\sum_i m_i^2 e^{-2\epsilon(A_s)_i}\right]^{1/2}
\tag{1}
\]

로 둔다. \(\langle f\rangle=(4\pi)^{-1}\int f\,d\Omega_m\)는 physical-birth-angle 평균이다. 이 좌표에서는 birth source Jacobian을 추가로 곱하지 않는다. 이 선택은 scalar gas가 homogeneous한 baseline에서 한 photon cohort의 수송·흡수를 기술한다.

\(\lambda(s,E)=\sum_j c n_j(s)\sigma_j(E)\)는 총 hazard, \(\Theta=\int_b^t\lambda ds\), \(P=e^{-\Theta}\)다. Scalar terminal weight L에 대해 \(K=PL\)를 계산한다. 흡수 사건은 \(L=\lambda_j\), primary heat는 \(L=\lambda_j(E-\chi_j)\)이며, 다른 energy-dependent scalar terminal observable에도 같은 유도가 적용된다. \(D=E\partial_E\)다. D와 \(A_s\)는 무차원, \(\lambda\)는 s⁻¹, \(K\)는 L과 같은 단위다.

## 2. Metric energy의 두 번째 변분

\(a_s=\boldsymbol m^TA_s\boldsymbol m\), \(b_s=\boldsymbol m^TA_s^2\boldsymbol m\)라 쓰면

\[
R_s=1-\epsilon a_s+\epsilon^2\left(b_s-\frac12a_s^2\right)+O(\epsilon^3),
\quad
\ln R_s=-\epsilon a_s+\epsilon^2(b_s-a_s^2)+O(\epsilon^3).
\tag{2}
\]

따라서 \(\delta=\partial_\epsilon|_0\)에 대해

\[
\delta\ln E=-a_s,
\qquad \delta^2\ln E=2(b_s-a_s^2),
\qquad \frac{\delta^2E}{E_0}=2b_s-a_s^2.
\tag{3}
\]

매끄러운 scalar F(E)의 chain rule은

\[
\delta F=-(DF_0)a_s,
\qquad
\delta^2F=2(DF_0)b_s+(D^2F_0-2DF_0)a_s^2.
\tag{4}
\]

두 번째 로그 에너지 변분을 빠뜨리면 이후의 \(D(D+3)\)에서 \(+3D\) 항을 재현하지 못한다. \(\delta^2\)와 \([\epsilon^2]\)는 두 배 차이가 난다.

## 3. 정확한 isotropic contraction과 causal memory

연속 구면의 2차·4차 moment는

\[
\langle m_im_j\rangle=\frac{\delta_{ij}}3,
\quad
\langle m_im_jm_km_l\rangle
=\frac{\delta_{ij}\delta_{kl}+\delta_{ik}\delta_{jl}
+\delta_{il}\delta_{jk}}{15}.
\tag{5}
\]

Trace-free symmetric A와 M에 대해

\[
\langle\boldsymbol m^TA^2\boldsymbol m\rangle=\frac13\operatorname{tr}A^2,
\quad
\langle(\boldsymbol m^TA\boldsymbol m)^2\rangle=\frac2{15}\operatorname{tr}A^2,
\quad
\langle(\boldsymbol m^TA\boldsymbol m)(\boldsymbol m^TM\boldsymbol m)\rangle
=\frac2{15}\operatorname{tr}(AM).
\tag{6}
\]

따라서 식 (4)의 평균은

\[
\langle\delta^2F\rangle=\frac2{15}(D^2+3D)F_0\operatorname{tr}A_s^2.
\tag{7}
\]

인과적 opacity memory를

\[
M(t,b)=\int_b^t(D\lambda_0)(s)A_s\,ds,
\qquad
V(t,b)=\int_b^t[(D^2+3D)\lambda_0](s)\operatorname{tr}A_s^2\,ds
\tag{8}
\]

로 정의한다. M은 trace-free, M과 V는 무차원이다. \(\delta\Theta=-\boldsymbol m^TM\boldsymbol m\)이므로

\[
\langle(\delta\Theta)^2\rangle=\frac2{15}\operatorname{tr}M^2,
\qquad
\langle\delta^2\Theta\rangle=\frac2{15}V.
\tag{9}
\]

## 4. 핵심 결과: 고정 gas scalar kernel의 quadratic coefficient

출발 항등식

\[
\delta^2(PL)=P_0\left[\delta^2L-2\delta L\,\delta\Theta
+L_0\big((\delta\Theta)^2-\delta^2\Theta\big)\right]
\tag{10}
\]

에 위 평균식을 넣으면

\[
\boxed{
[\epsilon^2]\langle K\rangle
=\frac{P_0}{15}\left\{
[(D^2+3D)L_0]\operatorname{tr}A_t^2
-2(DL_0)\operatorname{tr}(A_tM)
+L_0\operatorname{tr}M^2-L_0V
\right\}.
}
\tag{11}
\]

\(\delta^2\langle K\rangle\)는 우변의 두 배다. 네 항은 차례로 endpoint spectral curvature, endpoint와 과거 opacity의 상관, survival variance, mean-opacity curvature다. 세 번째 항은 \(L_0\ge0\)일 때 비음수이나, 총합의 부호는 고정되지 않는다.

\(t=b\)이면 \(A_t=M=V=0\)이므로 계수가 0이다. \(\lambda=0\)인 free observable은 첫 항만 남는다. \(B(s)\mapsto B(s)+C\)의 일정한 trace-free shift에 A, M, V가 불변이므로 물리적 결과는 absolute birth anisotropy에 의존하지 않는다. Source의 전체 scalar amplitude가 ε에 독립적이면 cohort별 식 (11)에 source measure \(S(b,E_b)db\,dE_b\)를 곱해 적분한다. 미분·적분의 교환 조건과 threshold separation이 필요하다.

## 5. Fixed-q 표현과의 2차 일치

고정 q unit direction을 \(\boldsymbol v\), \(C=B(b)\)라 하자. 이 표현의 energy ratio는

\[
R_s^{(q)}=
\left[\frac{\boldsymbol v^Te^{-2\epsilon(C+A_s)}\boldsymbol v}
{\boldsymbol v^Te^{-2\epsilon C}\boldsymbol v}\right]^{1/2},
\quad
J_b=(\boldsymbol v^Te^{-2\epsilon C}\boldsymbol v)^{-3/2}.
\tag{12}
\]

\(c=\boldsymbol v^TC\boldsymbol v\), \(a=\boldsymbol v^TA\boldsymbol v\)에 대해

\[
\delta^2\ln E_q-\delta^2\ln E_m
=4[\boldsymbol v^TCA\boldsymbol v-ca],
\quad
\delta J_b=3c,
\quad
\delta^2J_b=15c^2-6\boldsymbol v^TC^2\boldsymbol v.
\tag{13}
\]

두 표현의 zeroth-order 방향을 동일하게 놓고 \(X=(DL_0)A_t-L_0M\)라 두면

\[
\frac{\delta^2(J_bK_q)-\delta^2K_m}{P_0}
=4\boldsymbol v^TCX\boldsymbol v
-10(\boldsymbol v^TC\boldsymbol v)(\boldsymbol v^TX\boldsymbol v)
+L_0\left[15(\boldsymbol v^TC\boldsymbol v)^2
-6\boldsymbol v^TC^2\boldsymbol v\right].
\tag{14}
\]

식 (5)–(6)에 의해 평균은

\[
\left(\frac43-10\frac2{15}\right)\operatorname{tr}(CX)
+L_0\left(15\frac2{15}-\frac63\right)\operatorname{tr}C^2=0.
\tag{15}
\]

따라서 birth-coordinate 변화, first-order kernel과 source Jacobian의 공분산, second-order source Jacobian을 함께 포함하면 두 계산이 정확히 일치한다. Endpoint 에너지의 fixed-q second variation만 취하거나 \(J_b\)를 누락하면 이 취소가 깨진다. 이 검산은 PHYS20 first-order 반복이 아니라 새 second-order covariance 항 전체에 대한 검사다.

## 6. Power-law 진단과 부호

\(A_s=h_sS\), \(\operatorname{tr}S=0\), \(\lambda(s,E)\propto E^p\), \(L(t,E)\propto E^r\)라 하자. \(I_k=\int_b^t\lambda_0(s)h_s^k ds\)라 두면 식 (11)은

\[
\frac{[\epsilon^2]\langle K\rangle}{K_0}
=\frac{\operatorname{tr}S^2}{15}
\left[r(r+3)h_t^2-2rp h_tI_1+p^2I_1^2-p(p+3)I_2\right].
\tag{16}
\]

이는 baseline \(\lambda_0(s)\)와 평균 expansion이 시간에 따라 변해도 성립한다. H=0, \(h_s=(s-b)/T\), \(t-b=T\), 일정한 \(\lambda_0\), \(\tau=\lambda_0T\)라는 analytic diagnostic에서는 \(I_1=\tau/2,I_2=\tau/3\)이므로

\[
\frac{[\epsilon^2]\langle K\rangle}{K_0}
=\frac{\operatorname{tr}S^2}{15}
\left[r(r+3)-rp\tau+\frac{p^2\tau^2}{4}
-\frac{p(p+3)\tau}{3}\right].
\tag{17}
\]

이 H=0 입력은 가벼운 analytic diagnostic이며 Einstein equation을 만족하는 background로 제출하지 않는다.

### 6.1 Inverse-cube opacity

\(p=-3\)에서 \((D^2+3D)\lambda_0=0\)이므로 local mean-opacity curvature가 사라진다. 더 강하게, \(\det e^{-2\epsilon A_s}=1\)이므로

\[
\langle R_s^{-3}\rangle=1
\tag{18}
\]

이 연속 구면에서 정확하다. 이는 determinant-one linear momentum map의 solid-angle Jacobian 적분이다. 따라서 전 경로가 같은 매끄러운 inverse-cube law에 속하면 \(\langle\Theta\rangle=\Theta_0\)이며 Jensen inequality로

\[
\langle P\rangle=\langle e^{-\Theta}\rangle\ge e^{-\langle\Theta\rangle}=P_0,
\qquad
\langle1-P\rangle\le1-P_0.
\tag{19}
\]

즉 이 특별한 고정-gas power law에서는 **cumulative absorption probability가 baseline보다 작거나 같다.** 이것이 endpoint event rate의 부호까지 고정하지는 않는다. 현재 사건률은 survival의 시간 미분이기 때문이다. 실제 threshold crossing 또는 다른 opacity slope가 있으면 식 (18)–(19)를 전체 경로에 적용할 수 없다. 이 Jensen 결과는 직접 유도한 연속 구면 명제이며 별도의 finite-amplitude exact quadrature 인증으로 표기하지 않는다.

\(L=\lambda\), 즉 \(r=p=-3\)이면

\[
\frac{[\epsilon^2]\langle P\lambda\rangle}{P_0\lambda_0}
=\frac35\operatorname{tr}S^2\,\tau\left(\frac\tau4-1\right).
\tag{20}
\]

따라서 0<τ<4에서 음수, τ>4에서 양수다. \(S=\operatorname{diag}(1,-1,0)\)에 대해 τ=1/4에서 −9/32, τ=8에서 48/5다. Local opacity 평균이 정확히 보존되어도 causal survival covariance는 남는다.

### 6.2 Primary heat의 smooth sign counterexample

\(L=\lambda(E-\chi)\), \(p=-3\), \(\eta=\chi/E_0(t)<1\)인 같은 diagnostic에서

\[
\frac{[\epsilon^2]\langle K_Q\rangle}{K_{Q,0}}
=\frac{\operatorname{tr}S^2}{15(1-\eta)}
\left[-2+(-6+9\eta)\tau
+\frac94(1-\eta)\tau^2\right].
\tag{21}
\]

\(S=\operatorname{diag}(1,-1,0)\), \(E_0=2\chi\)에서는 τ=1/4에서 **−59/96**, τ=4에서 **+8/3**이다. 충분히 작은 ε에서는 모든 방향의 에너지가 threshold에서 떨어져 있으며 L과 λ가 매끄럽고 양수다. 따라서 같은 감소하는 opacity power law와 같은 positive primary-heating closure에서도 optical depth만 바꾸면 scalar quadratic response의 부호가 바뀐다. 이 counterexample은 실제 FT03 온도계수나 source-integrated heat의 부호를 계산한 것이 아니다.

## 7. 실제 독립 검산

`verify_second_order.py`는 owner의 구현을 import하지 않는 Python stdlib 프로그램이다. 다음 두 계산을 서로 대조했다.

1. Fraction 다항식으로 각 ray의 energy, opacity, survival, terminal weight의 ε² 계수를 전개하고 시간 적분을 정확히 수행한 다음 angular average.
2. 식 (11)의 trace contraction을 Fraction으로 평가.

Angular rule은 축의 6점에 각각 1/15, cube vertex의 8점에 각각 3/40을 부여한 14-ray rule이다. 고정 diagonal tensors에서는 direction square가 같은 ray들을 합쳐 4개 class로 구현했다. Q2와 Q4를 정확히 만족하므로 새 second-order 평균에는 충분하다. 이 rule을 production 처방으로 채택하지 않았고, 유한 ε의 angular function 전체를 정확히 적분한다고 주장하지 않는다.

독립적인 finite-amplitude 검사는 Decimal80에서 원래 exponential energy 및 survival kernel을 계산했다. 시간 적분은 composite Boole 8 blocks 및 16 blocks, central coefficient는 ε=10⁻⁴와 ε/2에서 계산해 \((4C(\epsilon/2)-C(\epsilon))/3\)로 leading finite-difference error를 제거했다. 다음 다섯 진단에서 physical-birth 및 fixed-q+J_b 표현 모두를 계산했다.

- inverse-cube absorption, τ=1/4;
- inverse-cube absorption, τ=8;
- inverse-cube heating, χ/E₀=1/2, τ=1/4;
- inverse-cube heating, χ/E₀=1/2, τ=4;
- \(A_s=xS+x^2T\), \(T=\operatorname{diag}(1/3,1/6,-1/2)\), 시간에 따라 변하는 opacity \(T_{\rm time}\lambda_0=1/5+x/10\), p=2, 혼합 terminal powers −1과 3.

마지막 사례는 모든 A_s가 하나의 고정 tensor에 비례해야만 성립하는 우연을 배제한다. 고유축은 고정하고 eigenvalue의 상대 시간 의존성만 바꿨다. Fixed-q 표현에서는 \(B_b=\operatorname{diag}(2/5,-1/3,-1/15)\)를 사용해 absolute birth anisotropy와 새 covariance 항을 실제로 포함했다.

실행 명령:

```bash
python3 verify_second_order.py --output second_order_results_v1.json
```

실행 결과는 **44/44 PASS, exit 0**이다. 이 44개는 독립된 연구 주장 44개라는 뜻이 아니라, 10개 moment 항, 5개 Fraction kernel 대조, 5개 source-covariance 대조, 20개 finite-amplitude/시간 구적 대조, 4개 analytic sign 값 확인이다.

- 외삽된 relative ε² coefficient와 정확 수식의 최대 절대차: \(1.03446306758096\times10^{-15}\).
- Boole resolution 변경에 따른 relative coefficient의 최대 차이: \(7.65321756814567\times10^{-19}\).
- tolerance: 각각 10⁻¹².

이 numerical agreement는 rigorous quadrature enclosure나 full physical-history error certificate가 아니다. 결과 JSON에는 coefficient와 second derivative를 따로 기록했고, 실제 실행 provenance는 `EXECUTION.json`에 보존했다. 최초 실행에서 실패한 check는 없었다.

## 8. Claim ceiling

고정 gas에서의 continuum second-order functional, birth-coordinate equivalence, power-law scalar sign diagnostic까지 닫았다. Coupled gas의 second variation은 root가 별도로 정식화한다. FT03의 실제 evolving temperature, ionization fraction, Γ, scalar τ의 2차 계수·부호, native scheme의 error는 이 기여로 해결되지 않는다. 기존 물리 gate와 실패 기록을 변경할 근거는 제공하지 않는다.
