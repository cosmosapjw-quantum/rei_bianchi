# Full H/He moving-source bounds and continuation certificate

Unit: HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06. Author derivation. The fixed model and explicit domain are in ../dossier/SCIENTIFIC_CONTRACT.md. Primitive inclusion and differential bounds are supplied by PRIMITIVE_DIFFERENTIAL_BOUNDS.md; actual rate functions and their envelopes are supplied by RATE_ENVELOPES.md. The argument below uses those quantified bounds and the accepted THEORY05 finite equations, with no native RHS or ODE evaluation.

## 1. Affine variables and exact source equations

Use signature (-,+,+,+), fixed Eulerian normal n, D=gamma n_H, and the parent neutral-reference EOS. Set epsilon=epsilon_eV, mu=m_ref c^2/epsilon, a=mu+B(zeta), e=E/(D epsilon), m=M/(D epsilon). The physical photon energies obey epsilon E_q=hbar omega_q. Energies a,t,w,e,m are expressed in eV per H; c remains explicit in rates. In the source-bound arithmetic use cm, seconds and erg with the exact native constants.

Let u_* = gamma_*(n+beta_*) be a fixed unit timelike anchor. Define

\[
 t=\gamma_*\bigl(e-\boldsymbol\beta_*\cdot\mathbf m\bigr)-a,
 \qquad z=(\zeta_1,\zeta_2,\zeta_3,t,m_1,m_2,m_3). \tag{S1}
\]

Since B is affine in zeta and gamma_*>0 is fixed, (zeta,E,M) -> z is an invertible affine map. The inverse energy row is e=(t+a)/gamma_*+beta_* dot m. Consequently the parent backward-Euler equation transforms exactly, including its finite-time meaning. This transformation is tied to the original fixed Eulerian stage; the time foliation is unchanged.

Let X=H_s^{-1}(z-z_*) with diagonal positive scales H_s and the specified initial state z_*. The task uses the closed cube ||X||_infinity<=1. The parent positive-cone inverse, composed with this affine map, defines w(X), gamma(X), beta(X), n_H(X) on the entire cube once physical inclusion has been established. At X=0, t_*=w_*.

The edge incidence vectors for H I->H II, He I->He II, He II->He III are

\[
 \nu_0=(1,0,0),\quad \nu_1=(0,1,0),\quad \nu_2=(0,-1,1). \tag{S2}
\]

Write lower and upper abundances per H as

\[
 y=(1-\zeta_1,f-\zeta_2-\zeta_3,\zeta_2),\quad
 v=(\zeta_1,\zeta_2,\zeta_3),\quad
 e_H=\zeta_1+\zeta_2+2\zeta_3. \tag{S3}
\]

For an atomic coefficient k_c(T), the event rate divided by D is

\[
 R_c(X)=D\gamma^{-2}e_H y_c k_c(T). \tag{S4}
\]

Here y_c is a lower abundance for CI, an upper abundance for RR, and v_1 for either DR channel. Thus R has units s^-1 per H and includes the two proper-density factors from n_e n_abs. The gamma^-2 factor follows from n_H=D/gamma; no additional lab-time factor is inserted.

For photons define b_q=1-beta dot e_q, delta_q=gamma b_q, p_q^-=N_q^-/D, s_q=S_q/D, and

\[
 \lambda_{iq}=cD y_i b_q\sigma_i(\delta_q E_q),\qquad
 \Lambda_q=\sum_i\lambda_{iq},\qquad
 P_q(h)=p_q^-+hs_q,
\]
\[
 p_q^+(X,h)=\frac{P_q(h)}{1+h\Lambda_q(X)},\qquad
 R^\gamma_{iq}(X,h)=\frac{\lambda_{iq}(X)P_q(h)}{1+h\Lambda_q(X)}. \tag{S5}
\]

All external s_q are prescribed nonnegative inputs independent of X. The explicit certificate below selects s_q=0. Absorption, chemistry, energy and momentum consume the same h D R^gamma events.

Let K be the sum of the RR and both DR captured-kinetic powers divided by D epsilon. Let B_esc be the binding part of the escape power divided by D epsilon:

\[
 B_{\rm esc}=\sum_i\chi_i R_i^{\rm RR}
       +\chi_1(R_1^{\rm DR}+R_2^{\rm DR}),\qquad
 K=\sum_i K_i^{\rm RR}+\sum_k K_k^{\rm DR}. \tag{S6}
\]

Both quantities are in eV per H per second. Their kinetic coefficients are the actual FT03 coefficients, converted from erg to eV; no assumed cooling coefficient replaces them. Put

\[
 \Gamma_*=-u_*\cdot u=\gamma_*\gamma(1-\boldsymbol\beta_*\cdot\boldsymbol\beta),
 \qquad E_{q,*}=\gamma_*(1-\boldsymbol\beta_*\cdot\mathbf e_q)E_q. \tag{S7}
\]

The exact affine source rows are

\[
 S_\zeta=\sum_i\nu_i\left(\sum_qR^\gamma_{iq}+R_i^{\rm CI}-R_i^{\rm RR}\right)
     -\nu_1(R_1^{\rm DR}+R_2^{\rm DR}), \tag{S8}
\]
\[
 S_t=\sum_{iq}(E_{q,*}-\chi_i)R^\gamma_{iq}
       -\sum_i\chi_iR_i^{\rm CI}-\Gamma_* K-(\Gamma_*-1)B_{\rm esc}, \tag{S9}
\]
\[
 \mathbf S_m=\sum_{iq}E_q\mathbf e_qR^\gamma_{iq}
       -\gamma\boldsymbol\beta(K+B_{\rm esc}). \tag{S10}
\]

To derive (S9), take gamma_* times the parent lab-energy row minus beta_* dotted into its momentum row, divide by D epsilon, and subtract the affine B increment. The RR/DR binding gain in -Delta B cancels the unit part of the escape binding power, leaving -(Gamma_*-1)B_esc. This cancellation is exact at the finite endpoint. The photon weight E_{q,*} is constant during this stage even though its opacity depends on the candidate gas velocity. xAct verifies the anchor projection and its variation in XACT_CONTINUATION_VARIATIONS_v2.wl.

The scaled finite problem is

\[
 X=hG_h(X),\quad G_h=H_s^{-1}S(z_*+H_sX,h),\quad
 F(X,h)=X-hG_h(X)=0. \tag{S11}
\]

It has all three CI, three RR, both DR and active photo channels. Its energy and momentum ledgers are the exact affine image of the parent ledgers.

## 2. Composable rate and photon derivative bounds

For a scalar/vector-valued function f, use L_f as an upper bound on ||D_X f||_{infinity->absolute/Euclidean} on the whole physical cube. The derivative norm is over the normalized X coordinates. For a vector component the absolute norm is used. Constants carrying a bar bound absolute values.

From primitive inclusion take T in [T_-,T_+], gamma>=1, gamma<=gamma_bar, |beta|<=beta_bar, and finite L_T,L_gamma,L_beta. Abundances have exact affine bounds e_H<=e_bar, |D_X e_H|_1<=L_e, y_c<=y_bar_c and |D_X y_c|_1<=L_y_c. If k_c<=k_bar_c and |k_c'|<=k_prime_bar_c throughout [T_-,T_+], then (S4) gives

\[
 \overline R_c=D\bar e\,\bar y_c\bar k_c, \tag{S12}
\]
\[
 L_{R_c}=D\left[
 (L_e\bar y_c+\bar eL_{y_c}+2\bar e\bar y_c L_\gamma)\bar k_c
 +\bar e\bar y_c\overline{k_c'}L_T\right]. \tag{S13}
\]

The factor 2L_gamma bounds the derivative of gamma^-2 because gamma>=1. The same two formulas apply to the kinetic coefficient, which already includes its eV energy weight. Bound B_esc and its derivative by the weighted sums in (S6).

For each photon, take b_bar=1+beta_bar, L_b=L_beta and

\[
 \|D_X\delta_q\|\le b_{\rm bar}L_\gamma+\bar\gamma L_\beta. \tag{S14}
\]

A declared L_delta may bound the right side of (S14), or may be supplied by a directly proved derivative enclosure. Over the fixed active cutoff cell, if sigma<=sigma_bar and |sigma'|<=sigma_prime_bar,

\[
 \overline\lambda_{iq}=cD\bar y_i b_{\rm bar}\bar\sigma_{iq}, \tag{S15}
\]
\[
 L_{\lambda_{iq}}=cD\left[
 L_{y_i}b_{\rm bar}\bar\sigma_{iq}+
 \bar y_iL_\beta\bar\sigma_{iq}+
 \bar y_i b_{\rm bar}\overline{\sigma'_{iq}}E_qL_\delta\right]. \tag{S16}
\]

Inactive sigma branches have both bounds zero because the whole cube stays strictly in that branch. Sum (S15) and (S16) over absorbers to obtain Lambda_bar and L_Lambda.

Differentiating the eliminated event at fixed h gives the exact formula

\[
 D_XR^\gamma_{iq}
 =P_q(h)\left[
 \frac{D_X\lambda_{iq}}{1+h\Lambda_q}
 -\frac{h\lambda_{iq}D_X\Lambda_q}{(1+h\Lambda_q)^2}
 \right]. \tag{S17}
\]

For 0<=h<=H,

\[
 \overline R^\gamma_{iq}=P_q(H)\overline\lambda_{iq},\qquad
 L^\gamma_{iq}(H)=P_q(H)
 \left[L_{\lambda_{iq}}+H\overline\lambda_{iq}L_{\Lambda_q}\right]. \tag{S18}
\]

A useful alternative independent of H inside the square brackets is L_lambda_i+L_Lambda, obtained from h lambda_i/(1+h Lambda)<=1. Either inequality is a rigorous enclosure; keep the smaller proved bound for the chosen H. They also cover Lambda=0 without dividing by Lambda.

For the stage-parameter derivative, with X fixed,

\[
 \partial_h\bigl(hR^\gamma_{iq}\bigr)=
 \lambda_{iq}\frac{p_q^-+2hs_q+h^2\Lambda_qs_q}{(1+h\Lambda_q)^2}. \tag{S19}
\]

In the explicit s_q=0 case this is lambda_i p_q^-/(1+h Lambda)^2. It is nonnegative and bounded by the same R_bar as in (S18). No finite-difference or cancellation estimate is needed for the h derivative.

## 3. Full source row majorants

Let B_bind,L_bind and B_kin,L_kin be the upper bounds obtained from (S6), (S12), (S13). Let Gamma_bar>=Gamma_*>=1 and L_Gamma bound its derivative. A direct sufficient pair is

\[
 \bar\Gamma_*\ge\gamma_*\bar\gamma(1+|\beta_*|\bar\beta),\qquad
 L_{\Gamma_*}\le\gamma_*[(1+|\beta_*|\bar\beta)L_\gamma+
 \bar\gamma|\beta_*|L_\beta]. \tag{S20}
\]

For a physical cube close to the anchor, the normalization-constrained first variation vanishes exactly at the anchor and can yield a tighter quadratic bound. The explicit certificate may use the simpler rational upper bounds in (S20).

Chemical row upper bounds follow from the absolute incidence entries in (S8). For example,

\[
 B_{\zeta_1}=\overline R_0^{\rm CI}+\overline R_0^{\rm RR}
        +\sum_q\overline R^\gamma_{0q},
\]
\[
 B_{\zeta_2}=\sum_{i=1,2}
       (\overline R_i^{\rm CI}+\overline R_i^{\rm RR}+\sum_q\overline R^\gamma_{iq})
       +\overline R_1^{\rm DR}+\overline R_2^{\rm DR},
\]
\[
 B_{\zeta_3}=\overline R_2^{\rm CI}+\overline R_2^{\rm RR}
       +\sum_q\overline R^\gamma_{2q}. \tag{S21}
\]

Replace every event upper bound by its derivative bound to obtain the corresponding row L values. The thermal and componentwise momentum rows satisfy

\[
 B_t=\sum_{iq}|E_{q,*}-\chi_i|\overline R^\gamma_{iq}
 +\sum_i\chi_i\overline R_i^{\rm CI}
 +\bar\Gamma_*B_{\rm kin}+(\bar\Gamma_*-1)B_{\rm bind}, \tag{S22}
\]
\[
 L_t=\sum_{iq}|E_{q,*}-\chi_i|L^\gamma_{iq}
 +\sum_i\chi_iL_{R_i^{\rm CI}}+\bar\Gamma_*L_{\rm kin}
 +(\bar\Gamma_*-1)L_{\rm bind}+L_{\Gamma_*}(B_{\rm kin}+B_{\rm bind}), \tag{S23}
\]
\[
 B_{m_j}\le\sum_{iq}E_q\overline R^\gamma_{iq}
      +\bar\gamma\bar\beta(B_{\rm kin}+B_{\rm bind}), \tag{S24}
\]
\[
 L_{m_j}\le\sum_{iq}E_qL^\gamma_{iq}
  +(\bar\beta L_\gamma+\bar\gamma L_\beta)(B_{\rm kin}+B_{\rm bind})
  +\bar\gamma\bar\beta(L_{\rm kin}+L_{\rm bind}). \tag{S25}
\]

The sharper |e_qj| may replace 1 in the photon momentum sums. Divide each row B,L by its corresponding scale in H_s. Denote the resulting seven-vectors by b and ell(H). Thus on the full cube and for all 0<=h<=H,

\[
 |G_{h,i}(X)|\le b_i,\qquad
 \sum_j|\partial_{X_j}G_{h,i}(X)|\le\ell_i(H). \tag{S26}
\]

For s_q=0, b is independent of H and the first bound in (S18) gives ell_i(H)=ell_i^(0)+H ell_i^(1) with nonnegative rational coefficients once the rate envelopes are rational. All absolute-value sums are explicit and source-owned. No counter channel or event is silently disabled.

## 4. Quantitative finite-step branch theorem

Assume the entire X cube is physically admissible and stays within a smooth cutoff cell, and (S26) holds on it for 0<=h<=H. Define

\[
 B=\max_i b_i,\quad L(H)=\max_i\ell_i(H),\quad q=HL(H).
\]

If

\[
 HB<1,\qquad q<1, \tag{S27}
\]

then for every h in [0,H], T_h(X)=hG_h(X) maps the cube into its interior and is a contraction with factor at most q in the infinity norm. Therefore F(X,h)=0 has exactly one solution in the cube, and the iteration X_(k+1)=hG_h(X_k), X_0=0 constructs it. Bounds are

\[
 |X_i(h)|\le hb_i,\qquad
 \|X(h)-X_k\|_\infty\le
 \frac{q^k}{1-q}\|X_1-X_0\|_\infty. \tag{S28}
\]

The proof is direct: (S26) supplies the self-map inclusion and the mean-value Lipschitz bound on the convex cube; Banach supplies the root and the displayed error estimate. At h=0 it equals the specified initial state. The Jacobian I-hD_XG_h is invertible throughout the cube by its norm bound, so the solutions form one C1 branch on [0,H] (and an open neighborhood of each endpoint within the defining model). This is a continuation in the backward-Euler parameter with the old physical state fixed.

A constructive candidate H can be generated before any root solve. For desired self-map margin theta<1 and q_target<1, let L0=max_i ell_i^(0), L1=max_i ell_i^(1). Then

\[
 H\le\frac{\theta}{B},\qquad
 H\le\frac{2q_{\rm target}}
 {L_0+\sqrt{L_0^2+4q_{\rm target}L_1}} \tag{S29}
\]

suffices when the denominator is positive. The usual infinity convention applies if the corresponding bound is zero. The rational positive H in the actual certificate is checked by the original inequalities (S27), avoiding a floating-point choice of the limiting root.

By differentiating F along the branch,

\[
 \frac{dX}{dh}=(I-hD_XG_h)^{-1}\partial_h(hG_h). \tag{S30}
\]

If b^(h) bounds the absolute rows of partial_h(hG_h), then

\[
 \left\|\frac{dX}{dh}\right\|_\infty
 \le\frac{\max_i b_i^{(h)}}{1-q}. \tag{S31}
\]

For s_q=0, (S19) and the same signed-row estimates give b^(h)<=b. Any guard g with known L_g can therefore be transported over a parameter increment Delta h using L_g B |Delta h|/(1-q). The direct uniform physical inclusion remains the primary guard certificate on the selected cube.

## 5. Preconditioned corrector and parameter tubes

For later continuation, let I_h=[h_-,h_+] be a closed parameter interval, let xbar(h) be a C1 predictor, and let the tube

\[
 \mathcal T=\{(X,h):h\in I_h,\ |X-\bar x(h)|\le r\},\quad r_i>0 \tag{S32}
\]

lie in a proved physical smooth domain. Fix an invertible 7x7 matrix A and define T_h(X)=X-A F(X,h). Obtain componentwise uniform bounds

\[
 Y\ge|AF(\bar x(h),h)|,\qquad
 Z\ge|I-A D_XF(X,h)|\quad\text{on }\mathcal T. \tag{S33}
\]

A verifiable way to obtain Z is |I-AJ0|+|A|DeltaJ if |D_XF-J0|<=DeltaJ componentwise on the whole tube. If

\[
 Y+Zr<r\quad\text{componentwise},\qquad
 q_r=\max_i\frac{(Zr)_i}{r_i}<1, \tag{S34}
\]

then each parameter section has one root in its box. Indeed T_h maps that box into its interior and contracts in ||v||_r=max_i|v_i|/r_i. The same bounds prove nonsingularity of A D_XF and hence of D_XF. Uniformity and the parameter-dependent contraction/implicit function theorem give one C1 branch in the tube. This full-box Jacobian statement supplies uniqueness explicitly.

Adjacent tubes represent the same branch when their certified roots at a common parameter are connected by a proved inclusion. Sufficient examples are: the entire endpoint box of one certificate lies in the uniqueness box of the other; or a common certified root enclosure is contained in both boxes. Mere geometric intersection of two boxes does not identify their distinct certified roots. Once the endpoint root is identified, local uniqueness joins the branches on their common connected parameter interval.

The weighted contraction, radii-bound and interval-Newton/Krawczyk framework is established mathematics. This finite-dimensional specialization is used with the concrete physical guards and source envelopes above. Primary references and their exact theorem scopes are in ../review/LITERATURE_MAP.md. It is not necessary to use a centered slope theorem beyond the conclusions it states, because (S33) directly controls the Jacobian on every point of the box.

## 6. Finite-endpoint continuation alternative

Consider a connected C1 branch F(X(h),h)=0 on [0,Hmax), with fixed old state and Hmax finite. If X(h) remains in a compact subset K of the open physical smooth domain and ||D_XF(X(h),h)^(-1)|| remains bounded, then the branch extends across Hmax.

Proof. The continuous partial_h F is bounded on a compact neighborhood of K times a finite h interval. Therefore X'=-D_XF^(-1)partial_h F is bounded. Hence X(h) is Cauchy as h approaches Hmax and converges to Xmax in K. Continuity gives F(Xmax,Hmax)=0. A uniform inverse bound on the approaching nonsingular matrices forces the limiting Jacobian to remain nonsingular: otherwise a unit null-vector of the limit contradicts that bound. The implicit function theorem extends the branch through (Xmax,Hmax), and uniqueness identifies it with the old branch.

Thus a finite nonextendible (maximal) endpoint of such a regular continuation is accompanied by escape from compact subsets of the chosen smooth physical domain or by loss of a bounded inverse Jacobian. Physical guards identify the concrete boundaries: warm range, composition simplex, |beta|<1, positive primitive cone, and fixed Doppler cutoff cell. Failure of a particular enclosure inequality leads to refinement of its bounds or chart; an actual branch boundary is determined by the stated mathematical conditions.

## 7. Computational and implementation connection

The primitive source scales, actual k/k' and sigma/sigma' envelopes, b and ell^(0,1), rational H, self-map/contraction margins and guard margins are recorded in the actual certificate result. All numeric conclusions are tied to exact rational arithmetic and domain inequalities. The short evaluator checks do not integrate the chemical history or run a native consumer.

Implementation can use the cheap uniform certificate first, then the preconditioned tube test (S33)-(S34) around an already available corrector and its Jacobian. It must retain the input old state while varying h within one branch problem, map each new chart affinely, and identify roots between charts using the explicit inclusion condition. Separate time stepping updates the old state and requires a fresh local certificate or a proved uniform family over the new initial states.

The finite balances and K_gamma diagnostic are inherited unchanged from THEORY05. The new H certificate quantifies branch existence, domain preservation and iteration convergence; a requested time-discretization accuracy target is supplied by the corresponding integration contract. Native implementation remains assigned to PRIMARY_PROVIDER_03, COVARIANT_MOMENTS_04 and MOVING_GAS_STAGE_05 plus the continuation-certificate adapter.
