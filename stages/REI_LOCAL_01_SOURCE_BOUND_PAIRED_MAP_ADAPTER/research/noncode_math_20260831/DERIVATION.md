# rei_bianchi: Remaining Non-Coding Mathematical Blockers and Derived Closure

**Date:** 2026-08-31 (KST)  
**Repository:** `cosmosapjw-quantum/rei_bianchi`  
**Latest repository tip inspected:** `policy/wolfram-trirepo-20260830-r1` at `cf1470b5b2b33938380ebd868e85937e3231dc50` (draft PR #21; policy only)  
**Scientific source retained:** PR #14, `agent/implementation/rei-first-canonical-interval-20260829-r1` at `053b97c56e089e28a83f37d79a4128ed3cdae9f4`  
**Scientific continuation:** PR #18 at `1893f12d14b212eb4b6bd637332824f692e6f4b3`; PR #19 terminal handoff at `04a353339c0fe517ac5209a78bc57b49b8006f77`  

## 0. Executive verdict

The remaining scientific blocker is **not a missing H/He reaction equation** and is **not a defect in the locked strict tolerance**. A single four-site MPRK22(1)–Alexander-SDIRK2 microstep was already enclosed. The first canonical adaptive interval fails because the accepted nonpoint state is projected to Cartesian boxes before the same-parent full-step versus dependent-two-half-step comparison. For a scalar interval `I`, the present cross-box separation obeys `D(I,I)=width(I)`, so inherited enclosure width contaminates the local comparison.

The required repair is a source-bound affine/Taylor representation of the complete discrete map, with:

1. exact conservation-reduced H/He coordinates;
2. persistent parent and first-half dependency owners;
3. distinct source-site owners at all four evaluation sites of every leg;
4. full implicit population and thermal tangent/remainder certificates;
5. endpoint public transformation followed by owner-wise `H-F` subtraction before interval projection;
6. joint event and ledger certificates using the same dependency state.

This document closes the **formula-level architecture** for those items. It does **not** claim that the 46,080-node × three-lane uniform certificate, the first canonical interval, or the R3 history has passed.

---

## 1. Scope, variables, dimensions, and assumptions

### 1.1 State and units

At one spatial node let

\[
Y=(N_{\rm HI},N_{\rm HII},N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII})^T
\]

be particle counts. Let `V` have units `cm^3`, number densities be `n_s=N_s/V` in `cm^-3`, time step `h` be in seconds, temperature `T` in kelvin, and

\[
x_T=\ln T
\]

be dimensionless. Reaction/event fluxes `P_{ij}` have units particles per second; the Patankar generator has units `s^-1`. Thermal energy `U` is in erg and thermal power `Q` is in erg/s. The Boltzmann constant is retained explicitly,

\[
k_B=1.380649\times 10^{-16}\ {\rm erg\,K^{-1}}.
\]

### 1.2 Conserved totals

\[
N_{\rm H}=N_{\rm HI}+N_{\rm HII},\qquad
N_{\rm He}=N_{\rm HeI}+N_{\rm HeII}+N_{\rm HeIII}.
\]

These are structural invariants, not independently interval-bounded residuals.

### 1.3 Smooth-cell assumption

All derivatives below are taken inside one fixed table/topology cell. If a validated temperature tube intersects a Hummer–Shull/PCHIP knot or another piecewise branch surface on which the selected smooth expression changes, the derivative model is not continued across it. The attempt must be rejected, the earliest event localized, topology rebuilt, and the step restarted.

---

## 2. Blocker ledger

| ID | Formula-level blocker | Prior status | Result here | Remaining gate |
|---|---|---|---|---|
| MATH-01 | Conservation-reduced state and nonlinear public transform | chart existed; discrete public remainder not closed | exact Jacobian, Hessian, product-difference, asymmetric remainder formulas derived | implementation + outward tests |
| MATH-02 | Source-site branch polynomial and owner normalization | one-site first-order/mixed source model existed | exact branch coefficients, photon identity, normalized-measure Jacobian/Hessian derived | evaluate at every named site |
| MATH-03 | Full 2×2 H and 3×3 He Patankar implicit sensitivity | point/interval Krawczyk existed; persistent generators absent | M-matrix proof, first/second implicit derivatives, uniform remainder Krawczyk derived | local certificate execution |
| MATH-04 | Whole thermal residual including state-dependent photoheating | scalar `d/d logT` froze photoheat/context | complete residual, first/second derivatives, OTS derivative and implicit tangent formulas derived | outward PCHIP/rate bounds |
| MATH-05 | Same-parent full versus dependent two-half composition | Cartesian endpoints only | exact first/second chain rules and owner rules derived | source-bound operator run |
| MATH-06 | Difference-first public local comparison | endpoint interval separation contaminated by widths | direct affine/Taylor `H-F` and exact helium difference identities derived | strict `<2e-4` pilot |
| MATH-07 | Validated event localization | bounded synthetic event existed; persistent affine tube absent | interval-Newton/earliest-event contract derived | path tube execution |
| MATH-08 | Joint integrated ledgers | marginal zero containment only | generator-by-generator and joint-feasibility criteria derived | whole-history/pilot evidence |
| MATH-09 | Physical cone and every denominator | scattered checks plus `1e-300` guards in old oracle | explicit pre-division theorem conditions listed | fail-closed implementation |
| EVID-01 | node 38382 RED and independently solved nonlinear fixture | NOT_RUN in new adapter | no symbolic obstruction remains | numerical execution |
| EVID-02 | all 46,080 nodes × all three lanes uniform pilot | NOT_RUN | not a formula problem | numerical execution |
| EVID-03 | original-start R3 first interval/history | NOT_RUN | not a formula problem | only after EVID-02 pass |

---

## 3. Conservation-reduced coordinates

Define the internal coordinates

\[
u=(x_{\rm HI},x_{\rm HeI},r,x_T),\qquad
q=1-x_{\rm HeI},\qquad
r=\frac{x_{\rm HeIII}}{x_{\rm HeII}+x_{\rm HeIII}}.
\]

The domain is

\[
0\le x_{\rm HI}\le 1,\quad 0\le x_{\rm HeI}<1,\quad q>0,
\quad 0\le r\le 1,\quad x_T\in\mathbb R.
\]

The public map is

\[
\Pi(u)=\left(
1-x_{\rm HI},\ q(1-r),\ qr,\ x_T
\right)
=\left(x_{\rm HII},x_{\rm HeII},x_{\rm HeIII},\ln T\right).
\]

Its Jacobian is

\[
D\Pi=
\begin{pmatrix}
-1&0&0&0\\
0&-(1-r)&-q&0\\
0&-r&q&0\\
0&0&0&1
\end{pmatrix}.
\]

The only nonzero second derivatives are

\[
\partial_{x_{\rm HeI}}\partial_r x_{\rm HeII}=+1,
\qquad
\partial_{x_{\rm HeI}}\partial_r x_{\rm HeIII}=-1.
\]

Around `(x_0,r_0)` with `q_0=1-x_0`, the expansion is exact:

\[
\delta x_{\rm HeII}
=-(1-r_0)\delta x-q_0\delta r+\delta x\,\delta r,
\]

\[
\delta x_{\rm HeIII}
=-r_0\delta x+q_0\delta r-\delta x\,\delta r.
\]

The mixed terms cancel in the helium sum, so

\[
\delta x_{\rm HeII}+\delta x_{\rm HeIII}=-\delta x_{\rm HeI}
\]

exactly.

### 3.1 Remainder propagation

Write

\[
x=x_0+a_x+e_x,\qquad r=r_0+a_r+e_r,
\]

where `a_x,a_r` are retained affine/Taylor polynomials and `e_x,e_r` are outward asymmetric remainders. Then

\[
R_{\rm HeIII}
=q_0e_r-r_0e_x-a_xa_r-a_xe_r-e_xa_r-e_xe_r,
\]

\[
R_{\rm HeII}
=-q_0e_r-(1-r_0)e_x+a_xa_r+a_xe_r+e_xa_r+e_xe_r.
\]

Hence

\[
R_{\rm HeII}+R_{\rm HeIII}=-e_x.
\]

The HeII and HeIII remainder blocks must therefore be coupled with the same owner and opposite nonlinear contribution. Independent species-axis remainder owners are mathematically inconsistent with exact helium conservation.

### 3.2 Exact difference-first verifier identities

Let full and two-half endpoints be `(q_F,r_F)` and `(q_H,r_H)`. Define

\[
\bar q=\frac{q_H+q_F}{2},\quad \bar r=\frac{r_H+r_F}{2},
\quad \Delta q=q_H-q_F,\quad \Delta r=r_H-r_F.
\]

Then, exactly,

\[
\Delta x_{\rm HeIII}=q_Hr_H-q_Fr_F
=\bar q\,\Delta r+\bar r\,\Delta q,
\]

\[
\Delta x_{\rm HeII}=q_H(1-r_H)-q_F(1-r_F)
=(1-\bar r)\Delta q-\bar q\,\Delta r.
\]

These are cross-checks for endpoint-public-transform-then-subtract. They are not permission to subtract already projected internal interval boxes.

---

## 4. Source-site H/He OTS branch algebra

Within one authenticated evaluation site, let `v,f in [0,1]`, opacity fractions `y,z in [0,1]`,

\[
\ell=1.425,\qquad m=0.737,
\qquad w=(\ell-m)+my.
\]

The branch allocations are

\[
A_H=vw+(1-v)fz,
\]

\[
A_{\rm HeI}=vm(1-y)+(1-v)f(1-z).
\]

They satisfy the exact photon-allocation identity

\[
A_H+A_{\rm HeI}+v(2-\ell)+(1-v)(1-f)=1+v.
\]

### 4.1 Exact same-site polynomial

Let

\[
v=v_c+v_h\theta_v,\qquad f=f_c+f_h\theta_f,
\qquad \theta_v,\theta_f\in[-1,1].
\]

Then `A_H` and `A_HeI` are exactly bilinear. For `A_H`,

\[
A_H^{(0)}=v_cw+(1-v_c)f_cz,
\]

\[
A_{H,v}=v_h(w-f_cz),\qquad
A_{H,f}=f_h(1-v_c)z,
\]

\[
A_{H,vf}=-v_hf_hz.
\]

For `A_HeI`,

\[
A_{\rm HeI}^{(0)}=v_cm(1-y)+(1-v_c)f_c(1-z),
\]

\[
A_{{\rm HeI},v}=v_h\{m(1-y)-f_c(1-z)\},
\]

\[
A_{{\rm HeI},f}=f_h(1-v_c)(1-z),
\]

\[
A_{{\rm HeI},vf}=-v_hf_h(1-z).
\]

The `vf` term is one mixed monomial of a site's two source coordinates. It is not an independent third uncertainty.

### 4.2 Temperature-dependent source bounds

Inside a PCHIP cell, write the lower/upper table envelopes as `v_-(x_T),v_+(x_T)` and

\[
v_c=\frac{v_++v_-}{2},\qquad v_h=\frac{v_+-v_-}{2}.
\]

Then

\[
\partial_x v=\partial_xv_c+(\partial_xv_h)\theta_v,
\qquad
\partial_x^2 v=\partial_x^2v_c+(\partial_x^2v_h)\theta_v.
\]

For a cubic cell polynomial

\[
p(x)=a+b\tau+c\tau^2+d\tau^3,\qquad \tau=x-\kappa_m,
\]

\[
p_x=b+2c\tau+3d\tau^2,\qquad p_{xx}=2c+6d\tau.
\]

The range of `p_x` over a cell is obtained from both endpoints and, when it lies in the cell, `tau=-c/(3d)`. A tube touching `kappa_m` is an event, not a single smooth-cell derivative evaluation.

---

## 5. Normalized owner and opacity measures

For positive raw measures `h_i>0`,

\[
S=\sum_jh_j>0,\qquad q_i=\frac{h_i}{S}.
\]

The first variation is

\[
Dq_i[u]=\frac{u_i}{S}-\frac{h_i}{S^2}\sum_ju_j.
\]

Equivalently,

\[
Dq[u]=\frac{u-q\,\mathbf1^Tu}{S}.
\]

The bilinear Hessian is

\[
D^2q_i[u,v]
=-\frac{u_i\,\mathbf1^Tv+v_i\,\mathbf1^Tu}{S^2}
+\frac{2h_i(\mathbf1^Tu)(\mathbf1^Tv)}{S^3}.
\]

Two structural identities follow:

\[
\sum_iq_i=1,\qquad \sum_iDq_i[u]=0.
\]

The same formula covers:

- global owner amplitudes;
- group/species owner fractions;
- node allocation fractions;
- OTS opacity fractions `y`, `z`, and the three-channel `y2` split.

Every use requires a prior proof that `S` excludes zero over the complete source-bound enclosure. A literal `+1e-300` is not a certificate.

---

## 6. MPRK22(1) population map

For a conservative production-destruction system, let `P_{ij}>=0` be transfer into destination `i` from source `j`, with `P_{ii}=0`. For positive Patankar denominators `d_j>0`, define

\[
G_{ij}(P,d)=\frac{P_{ij}}{d_j}\quad(i\ne j),
\qquad
G_{jj}(P,d)=-\sum_{i\ne j}\frac{P_{ij}}{d_j}.
\]

Then

\[
\mathbf1^TG=0.
\]

For step `h>=0`,

\[
A(P,d,h)=I-hG(P,d).
\]

Its off-diagonal entries are nonpositive, and each column has strict dominance margin one:

\[
A_{jj}-\sum_{i\ne j}|A_{ij}|=1.
\]

Therefore `A` is a nonsingular M-matrix and `A^{-1}>=0`. Moreover,

\[
\mathbf1^TA=\mathbf1^T,
\]

so `Az=b` implies exact linear-invariant preservation `1^Tz=1^Tb`. The same proof applies to the H 2×2 and He 3×3 blocks, with the corresponding element-count left invariant.

### 6.1 Concrete stages

Let `P_0=P(Y_n,x_n,t_0,eta_0)`.

**Patankar-Euler predictor**

\[
A(P_0,Y_n,h)Y^{(2)}=Y_n.
\]

After the authenticated predictor source evaluation,

\[
P_1=P(Y^{(2)},x^{(2)},t_1,\eta_1),\qquad
\bar P=\frac{P_0+P_1}{2}.
\]

**MPRK22(1) corrector**

\[
A(\bar P,Y^{(2)},h)Y_{n+1}=Y_n.
\]

**Gamma population stage**

\[
A(P_0,Y_n,\gamma h)Y_\gamma=Y_n,
\qquad \gamma=1-\frac1{\sqrt2}.
\]

### 6.2 First implicit variation

For a generic stage

\[
A(\theta)Z(\theta)=b(\theta),
\]

\[
A\,Z_a=b_a-A_aZ.
\]

For the generator entries,

\[
(G_{ij})_a=\frac{(P_{ij})_a}{d_j}
-\frac{P_{ij}(d_j)_a}{d_j^2}\quad(i\ne j),
\]

with the diagonal derivative equal to the negative outgoing-column sum. If `h` also varies,

\[
A_a=-h_aG-hG_a.
\]

This is the required full-system tangent solve. No conserved row is deleted before certification.

### 6.3 Second implicit variation

For two owner directions `a,b`,

\[
A Z_{ab}=b_{ab}-A_{ab}Z-A_aZ_b-A_bZ_a.
\]

For `i != j`,

\[
(G_{ij})_{ab}
=\frac{(P_{ij})_{ab}}{d_j}
-\frac{(P_{ij})_a(d_j)_b+(P_{ij})_b(d_j)_a+P_{ij}(d_j)_{ab}}{d_j^2}
+\frac{2P_{ij}(d_j)_a(d_j)_b}{d_j^3}.
\]

This supplies exact same-site mixed coefficients and the Hessian information needed for a Lagrange remainder or a uniform residual certificate.

### 6.4 Uniform parametric remainder certificate

Let `p(theta)` be the retained center+generator+mixed polynomial and write the true solution as

\[
Z(\theta)=p(\theta)+r(\theta),\qquad r(\theta)\in R.
\]

Define the defect and Jacobian enclosures

\[
D\supseteq\{A(\theta)p(\theta)-b(\theta):\theta\in\Theta\},
\]

\[
\mathcal A\supseteq\{A(\theta):\theta\in\Theta\}.
\]

For a fixed preconditioner `C` approximating `A(theta_0)^{-1}`, use

\[
K(R)=-CD+(I-C\mathcal A)R.
\]

Strict inclusion

\[
K(R)\subset\operatorname{int}R
\]

is a uniform Krawczyk certificate for the nonlinear parameter dependence of the stage. The certified remainder is then transformed to `(x_HI,x_HeI,r)` only after the full 2×2/3×3 population solve has passed.

---

## 7. Whole thermal map

The number of translational particles is

\[
N_p(Y)=N_{\rm HI}+2N_{\rm HII}+N_{\rm HeI}+2N_{\rm HeII}+3N_{\rm HeIII}.
\]

Define

\[
U(Y,x)=\frac32k_BN_p(Y)e^x.
\]

Let

\[
Q(Y,x,t,\eta)=H_{\rm ph}(Y,x,t,\eta)
-\Lambda(Y,x,t)
-3H(t)k_BN_p(Y)e^x.
\]

Here

\[
H_{\rm ph}=H_{\rm base}+H_{\rm OTS,resolved}
\]

exactly once. Unresolved OTS and escaped radiation are ledger-only and do not enter `Q`.

### 7.1 Alexander SDIRK2

\[
\gamma=1-\frac1{\sqrt2},
\qquad
\begin{array}{c|cc}
\gamma&\gamma&0\\
1&1-\gamma&\gamma\\\hline
&1-\gamma&\gamma
\end{array}
\]

and `(1-gamma) gamma + gamma = 1/2`, so the method is second order and stiffly accurate.

The gamma residual is

\[
F_\gamma(x_\gamma)
=U(Y_\gamma,x_\gamma)-U_n-\gamma hQ_\gamma=0.
\]

The final residual is

\[
F_1(x_1)
=U(Y_1,x_1)-U_n
-h\{(1-\gamma)Q_\gamma+\gamma Q_1\}=0.
\]

The backward-Euler thermal predictor has the analogous form with its locked predictor context and weight one. Its context must be source-bound over the complete predictor enclosure, not frozen at a midpoint.

### 7.2 Exact derivatives

Let

\[
w=(1,2,1,2,3)^T.
\]

Then

\[
U_x=U,\qquad U_{xx}=U,
\]

\[
D_YU=\frac32k_Be^xw^T,
\qquad D_{Yx}U=D_YU,
\qquad D_{YY}^2U=0.
\]

For the thermal RHS,

\[
Q_x=H_{{\rm ph},x}-\Lambda_x-3Hk_BN_pe^x,
\]

\[
Q_{xx}=H_{{\rm ph},xx}-\Lambda_{xx}-3Hk_BN_pe^x,
\]

\[
D_YQ=D_YH_{\rm ph}-D_Y\Lambda-3Hk_Be^xw^T,
\]

\[
D_{Yx}Q=D_{Yx}H_{\rm ph}-D_{Yx}\Lambda-3Hk_Be^xw^T.
\]

Therefore a scalar stage residual `F=U-U_n-h(C+w_Q Q)` has

\[
F_x=U-hw_QQ_x.
\]

The existing frozen-photoheat derivative corresponds to setting `H_ph,x=0`. That is valid only where the authenticated site law proves photoheating independent of the thermal unknown. It is not valid for the state/temperature-dependent resolved OTS channel.

### 7.3 Resolved OTS photoheat derivative

Inside one smooth branch, write

\[
H_{\rm OTS}=C(Y)\,\alpha_c(T)\,[1-v(x)]\,f\,E[z(Y)],
\qquad T=e^x.
\]

At fixed `Y`,

\[
\partial_xH_{\rm OTS}
=CfE\left\{(1-v)T\alpha_c'(T)-\alpha_c(T)v_x\right\}.
\]

The second derivative is

\[
\partial_x^2H_{\rm OTS}
=CfE\left[
(1-v)\{T\alpha_c'+T^2\alpha_c''\}
-2v_xT\alpha_c'-v_{xx}\alpha_c
\right].
\]

Population and owner-normalization derivatives enter through `C(Y)` and `z(Y)` using the normalized-measure formulas of Section 5.

### 7.4 Rate derivative templates

For any rate `k(T)` and `x=lnT`,

\[
k_x=Tk_T,\qquad k_{xx}=Tk_T+T^2k_{TT}.
\]

For the Hui–Gnedin family

\[
k=Ae^{mx}\lambda^a(1+u)^{-d},\quad
\lambda=Ce^{-x},\quad u=(\lambda/b)^c,
\]

\[
s_1\equiv\partial_x\ln k=m-a+dc\frac{u}{1+u},
\]

\[
\partial_xs_1=-dc^2\frac{u}{(1+u)^2},
\qquad
k_{xx}=k\{s_1^2+\partial_xs_1\}.
\]

For an excitation/ionization family

\[
k=AT^ae^{-E/T}(1+q)^{-1},\qquad q=\sqrt{T/T_0},
\]

\[
s_1=a+\frac ET-\frac12\frac q{1+q},
\]

\[
\partial_xs_1=-\frac ET-\frac14\frac q{(1+q)^2},
\qquad k_{xx}=k\{s_1^2+\partial_xs_1\}.
\]

For a reaction flux

\[
R=N_a n_e k(T),\qquad
n_e=\frac{N_{\rm HII}+N_{\rm HeII}+2N_{\rm HeIII}}V,
\]

all population derivatives are at most bilinear before owner normalization, and

\[
R_x=N_an_ek_x,\qquad R_{xx}=N_an_ek_{xx}.
\]

### 7.5 Thermal implicit tangent and Hessian

For a scalar implicit residual `F(x,theta)=0`,

\[
x_a=-\frac{F_a}{F_x},
\]

\[
x_{ab}=-\frac{
F_{ab}+F_{ax}x_b+F_{xb}x_a+F_{xx}x_ax_b
}{F_x}.
\]

For the final SDIRK residual, `F_a` and `F_ab` include the already propagated gamma-stage variations of `Q_gamma`; treating `(1-gamma)Q_gamma` as a frozen constant in the parent/source tangent is incorrect.

A uniform certificate requires

\[
0\notin F_x(X,\Theta),
\]

and the preferred monotone branch has `inf F_x>0`. The scalar remainder Krawczyk map is the same defect formula as in Section 6.4 with scalar preconditioner `C`.

---

## 8. Source-bound full versus two-half composition

Represent an affine/Taylor state by

\[
X=X_c+\sum_\alpha G_\alpha\xi_\alpha
+\sum_{(\alpha,\beta)\in\mathcal M}G_{\alpha\beta}\xi_\alpha\xi_\beta
+R,
\qquad \xi_\alpha\in[-1,1].
\]

Remainders are asymmetric outward intervals with explicit provenance. Equal numerical intervals do not imply equal owners.

For one leg, let

\[
\Phi_h(X;\eta_0,\eta_1,\eta_\gamma,\eta_f)
\]

be the exact locked four-site MPRK22–SDIRK2 discrete map. The paired maps are

\[
X_F=\Phi_h(X_n;\eta_{F,*}),
\]

\[
X_{H1}=\Phi_{h/2}(X_n;\eta_{H1,*}),
\]

\[
X_H=\Phi_{h/2}(X_{H1};\eta_{H2,*}).
\]

The parent dependency registry is byte-identical for `F` and `H1`; `H2` inherits the complete `H1` state. By default the 12 source-site owner sets `F/H1/H2 × {t0,t1pred,tgamma,t1final}` are distinct.

### 8.1 First-order chain rule

For an inherited parent direction `a`,

\[
(X_H)_a=(D_X\Phi_2)(D_X\Phi_1)(X_n)_a
+\text{source terms from H1 and H2},
\]

whereas

\[
(X_F)_a=(D_X\Phi_F)(X_n)_a+\text{full-leg source terms}.
\]

The paired coefficient is

\[
(\Delta X)_a=(X_H)_a-(X_F)_a.
\]

Distinct source-site IDs remain as separate coefficients; they are not canceled because their bounds happen to agree.

### 8.2 Second-order chain rule

For an augmented input `Z=(X,eta)`, the clean formula is

\[
D^2(\Phi_2\circ\Phi_1)[u,v]
=D^2\Phi_2[D\Phi_1u,D\Phi_1v]
+D\Phi_2D^2\Phi_1[u,v].
\]

Using the augmented vector automatically includes `XX`, `X eta`, and `eta eta` blocks and prevents omitted cross-site feedback terms.

### 8.3 Difference-first remainder

After each endpoint is transformed to a public dependency model, define

\[
\Delta_{\rm pub}=X_{H,{\rm pub}}-X_{F,{\rm pub}}.
\]

Centers, shared coefficients, and shared polynomial monomials are subtracted owner-by-owner. If endpoint remainder intervals are

\[
R_H=[L_H,U_H],\qquad R_F=[L_F,U_F],
\]

and no direct joint delta certificate exists, the only admissible subtraction is

\[
R_\Delta=[L_H-U_F,\ U_H-L_F].
\]

No width subtraction is valid.

The projected component comparison is

\[
E_k=\max\{|\inf\Delta_k|,|\sup\Delta_k|\},
\qquad E=\max_kE_k,
\]

with the locked strict condition

\[
E<2\times10^{-4}.
\]

For a classical order-two method, raw full-minus-two-half separation is asymptotically three times the more accurate two-half local error estimate. The repository contract deliberately uses the raw paired separation; no Richardson division by three is authorized.

---

## 9. Why the old Cartesian metric fails after a nonpoint parent

For symmetric scalar boxes

\[
B_F=[c_F-r_F,c_F+r_F],\qquad
B_H=[c_H-r_H,c_H+r_H],
\]

the old cross-box metric is

\[
D(B_H,B_F)=\max\{|L_H-U_F|,|U_H-L_F|\}
=|c_H-c_F|+r_H+r_F.
\]

Thus

\[
D(I,I)=2r=\operatorname{width}(I).
\]

It is a sound maximum separation of two independent set elements, but it is not a same-parent truncation comparison once the parent is nonpoint. The source-bound paired map repairs the quantity being certified; it does not relax the tolerance.

---

## 10. Validated table-event localization

For node `i` and knot `kappa_m`, define

\[
g_{im}(t,\xi)=x_{T,i}(t,\xi)-\kappa_m.
\]

A no-event certificate on a time tube `I` is

\[
0\notin g_{im}(I,\Xi)
\]

for every relevant `(i,m)`. If zero is included, certify monotonicity by

\[
0\notin \partial_tg_{im}(I,\Xi).
\]

Then interval Newton gives

\[
N(I)=t_c-\frac{g_{im}(t_c,\Xi)}{\partial_tg_{im}(I,\Xi)},
\qquad I\leftarrow I\cap N(I).
\]

If the derivative contains zero, contraction loses inclusion, or competing event intervals cannot be ordered, emit `TABLE_EVENT_LOCALIZATION_FAILURE`. If several earliest intervals overlap, rebuild all potentially simultaneous topology surfaces at their common certified hull rather than choosing a favorable node.

A rejected event attempt commits no candidate state or ledger. After localization, rebuild the fixed topology and restart from the unchanged parent.

---

## 11. Joint conservation and ledger certificates

### 11.1 Element invariants

Let

\[
c_H=(1,1,0,0,0)^T,\qquad c_{He}=(0,0,1,1,1)^T.
\]

Every transfer event has stoichiometric vector `nu=e_dest-e_source` within one element, hence

\[
c_H^T\nu=0\quad\text{or}\quad c_{He}^T\nu=0.
\]

Consequently the corresponding Patankar generator obeys

\[
c^TG=0,
\]

and every certified stage preserves the invariant exactly.

### 11.2 Photon and owner identities

For each group `g`, normalized owner fractions satisfy

\[
\sum_oq_{og}=1,
\]

so assigned destruction obeys

\[
\sum_oJ_gq_{og}-J_g=0
\]

as an algebraic identity, generator-by-generator. The OTS branch identity in Section 4 supplies the subgrid photon closure.

### 11.3 Energy identity

For each event, use one named allocation of chemical, resolved heat, unresolved OTS, and escaped radiation:

\[
R_E=E_{\rm chemical}+E_{\rm resolved}
+E_{\rm unresolved}+E_{\rm escaped}=0.
\]

The population/owner ledger uses the authenticated `t0` and predictor sites with its locked MPRK quadrature. The OTS/thermal ledger uses the gamma and final sites with weights `(1-gamma,gamma)`. Reusing a two-site summary or adding resolved OTS heat twice breaks the identity.

### 11.4 Joint criterion

Let the residual vector share the state dependency registry:

\[
L(\xi)=L_0+\sum_\alpha L_\alpha\xi_\alpha
+\sum_{\alpha\beta}L_{\alpha\beta}\xi_\alpha\xi_\beta+R_L.
\]

The strongest certificate is

\[
L_0=0,\quad L_\alpha=0,\quad L_{\alpha\beta}=0,
\quad 0\in R_L
\]

generator-by-generator. Otherwise one joint feasible residual-vector enclosure/self-inclusion is required. Independent marginal intervals containing zero are insufficient: `L1=xi-1/2` and `L2=xi+1/2` each range across zero on `[-1,1]`, but no single `xi` makes both vanish.

---

## 12. Physical cone and denominator theorem obligations

Before any coefficient, quotient, logarithm, exponential-derived energy, or implicit matrix is constructed, certify:

1. `0 <= x_HI <= 1`, `0 <= x_HeI < 1`, `q=1-x_HeI>0`, `0 <= r <= 1`;
2. all reconstructed species are nonnegative and H/He sums are exact;
3. finite `x_T` and outward finite `T=exp(x_T)>0`;
4. `N_p>0` and `U>0`;
5. every Patankar denominator used by predictor/corrector/gamma stages is strictly positive;
6. every raw owner/absorption normalization sum is strictly positive;
7. all OTS denominators for `y,z,y2` are strictly positive;
8. forcing normalizations are finite and exclude zero where divided;
9. every population Krawczyk matrix is uniformly nonsingular;
10. every thermal derivative interval excludes zero.

If one condition fails, the map is rejected before later-site use. Epsilon regularizers do not convert a zero-containing denominator into a proof.

---

## 13. Wolfram symbolic verification summary

The companion Wolfram script checks the following residuals exactly:

- public helium Jacobian/Hessians and mixed-term cancellation;
- exact product-difference identities for HeII/HeIII;
- OTS branch photon identity;
- normalized-measure sum and Jacobian column-sum identities;
- MPRK generator column sums and unit strict-dominance margins;
- scalar implicit first- and mixed-second derivative identities;
- generic whole-thermal `dF/d logT` including photoheating derivative;
- Hui–Gnedin and excitation/ionization log-derivative templates;
- Alexander SDIRK2 second-order condition.

All checked residuals reduce to exact zero. The connected evaluator reported Wolfram 15.0.1 on `Linux-x86-64`; the machine-readable receipt records all 18 checks and explicitly limits the claim to symbolic identities.

### 13.1 SciSpace literature cross-check

The external literature supports the selected building blocks—second-order positive/conservative MPRK schemes, interval/Taylor validation of implicit maps, Hui–Gnedin-style thermochemical fits, and the Friedrich et al. H/He rate family—but does not provide the repository-specific four-site paired-map closure. The full literature ledger is included separately.

---

## 14. What is mathematically closed versus still unproved

### Formula-level closure achieved here

- conservation-reduced chart and public nonlinear transformation;
- exact source branch polynomial and photon identity;
- normalized owner/opacity first and second derivatives;
- full Patankar first/second implicit sensitivities and M-matrix argument;
- whole thermal residual and state-dependent photoheat derivatives;
- full/two-half composition and difference-first remainder algebra;
- event localization and joint ledger proof obligations;
- dimensional, sign, positivity, and denominator conditions.

### Not closed by formulas alone

- outward numerical evaluation of every PCHIP/rate/Jacobian/remainder bound on the real node-38382 fixture;
- local adapter certification in all three lanes;
- uniform 46,080-node × three-lane pilot;
- strict `<2e-4` paired comparison and `<2e-3` public width gates on that pilot;
- complete event-free/event-restart and joint-ledger evidence over the pilot;
- original-start R3 interval/history.

These are numerical/evidence gates, not missing derivations.

---

## 15. Exact next scientific sequence

1. Encode this formula contract in `REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER` without changing R2 evidence or thresholds.
2. Run the independently solved nonlinear fixture and authenticated node `38382` RED in all three lanes.
3. If and only if local certification passes, execute the all-node three-lane uniform pilot (`REI-LOCAL-02`).
4. If and only if the pilot passes, start R3 from the original initial state. Do not continue from the old Cartesian boxed state and do not retroactively relabel PR #14.

**Scientific status after this derivation:** `FORMULA_CONTRACT_CLOSED / NUMERICAL_CERTIFICATION_NOT_RUN / NO_PASS_FIRST_CANONICAL_INTERVAL`.
