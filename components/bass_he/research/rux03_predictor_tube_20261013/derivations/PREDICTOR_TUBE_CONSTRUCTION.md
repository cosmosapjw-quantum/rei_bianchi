# THEORY07 — a constructive full-rate predictor-tube pair

Status: author derivation with an actual 14/14-group Wolfram tube certificate. Independent adoption is recorded separately in `../review/DECISION.json`. Parent: BASS_HE PR34 at `3932669f7904f7f68f2f07dced4cf1da9d472480`. Scientific source: rei_bianchi PR114 at `a5c958c414dea41216b445c05f58df837f05cacb`.

## 1. Fixed source, common chart and the new input family

For each fixed \(\mu\in[10^9,1.5\times10^9]\,\mathrm{eV/H}\), use the THEORY06 seven-dimensional affine chart, scales and physical cube

\[
X=(X_{\zeta_1},X_{\zeta_2},X_{\zeta_3},X_t,X_{m_x},X_{m_y},X_{m_z}),\qquad Q=[-1,1]^7.
\tag{P1}
\]

The fixed Eulerian density is \(D=10^{-3}\,\mathrm{cm^{-3}}\), helium abundance is \(f=2/25\), and the chart center is \(\zeta_*=(1/2,1/50,1/50)\), \(T_*=50000\,\mathrm K\), \(\beta_*=(0,0,41/841)\), \(\gamma_*=841/840\). The full retained processes are CI3/RR3/DR2 and primary photoabsorption, with the source-defined Case-A captured kinetic and binding-energy escape. The six fixed rays and their old inventories \(p_q^-=1/100\) are unchanged; external photon sources vanish. The metric signature is \((-+++)\). Dimensional constants \(c,\hbar,k_B,\epsilon_{\mathrm{eV}}\) retain their parent definitions; no unit convention sets them to one.

The varying old gas state has coordinate \(\xi\in Q_\eta=[-\eta,\eta]^7\), \(\eta=1/100\). The stage endpoint is \(X\), and its exact finite residual is

\[
F(X,h;\xi)=X-\xi-hG_h(X),\qquad h\ge0.
\tag{P2}
\]

The old gas is represented in the one fixed reference chart. Every member keeps its own fixed \(\mu\), the same \(D,f\), fixed tetrad and fixed photon inputs. Therefore the source's endpoint dependence is through \(X,h\); its only direct old-gas dependence in the finite residual is the term \(-\xi\). The family does not vary old photons, density, external irradiation or the mass-per-H parameter inside a stage.

THEORY06 proves physical primitive recovery on an open neighborhood of \(Q\), with positive inventories and fixed smooth Doppler cutoff cells. It supplies exact nonnegative row-norm majorants

\[
\|\operatorname{row}_iD_XG_h(X)\|_1\le \ell_i(H)
=\ell_i^{(0)}+H\ell_i^{(1)},\qquad X\in Q,\quad0\le h\le H.
\tag{P3}
\]

Here the coefficients are the adopted exact strings in parent `evidence/FULL_SOURCE_CERTIFICATE_RESULT.json`. Their analytic proof uses \(1+h\Lambda_q\ge1\), and hence applies to each finite nonnegative \(H\). It is not restricted by the particular \(H=5\times10^8\) used in the parent's numerical self-map. The new construction reuses these coefficients and evaluates the changed inequalities at the new \(H\).

## 2. Rational anchor model with all source channels

At the exact anchor define

\[
e_*=\frac{14}{25},\qquad y_*=(\tfrac12,\tfrac1{25},\tfrac1{50}),\quad
v_*=(\tfrac12,\tfrac1{50},\tfrac1{50}),\quad
\alpha_*=D\gamma_*^{-2}e_*.
\tag{P4}
\]

The Doppler factors are \((841/840,841/840,841/840,841/840,20/21,21/20)\). The corresponding gas-frame energies are

\[
E_q^*=\left(\frac{19343}{840},\frac{19343}{840},\frac{841}{24},\frac{841}{24},\frac{200}{3},\frac{147}{2}\right)\,\mathrm{eV}.
\tag{P5}
\]

There are twelve active cross sections: HI at all six nodes, HeI at four, and HeII at two. Source-threshold-inactive entries are exactly zero. For each active atomic or cross-section coefficient, the anchor computation constructs a rational interval \([c^-,c^+]\) containing the source-decimal real function. Define

\[
\widehat c=(c^-+c^+)/2,\qquad e_c=(c^+-c^-)/2.
\tag{P6}
\]

This is a certified rational coefficient replacement at one exact state, not a change in the physical model: the discrepancy is explicitly carried into the tube residual bound below.

At the anchor let

\[
\lambda_{iq}=cD y_{*,i}(1-\beta_*\cdot e_q)\sigma_i(E_q^*),\quad
\Lambda_q=\sum_i\lambda_{iq},\qquad
r_{iq}(h)=\frac{\lambda_{iq}p_q^-}{1+h\Lambda_q}.
\tag{P7}
\]

Put hats on coefficients to define \(\widehat\lambda,\widehat\Lambda,\widehat r\). Define the collisional, recombination and dielectronic event coefficients

\[
C_i=\alpha_*y_{*,i}k_{CI,i},\quad R_i=\alpha_*v_{*,i}k_{RR,i},\quad
D_j=\alpha_*v_{*,1}k_{DR,j}\quad(j=1,2).
\tag{P8}
\]

For the total captured kinetic loss in \(\mathrm{eV/H/s}\),

\[
K=\frac{\alpha_*}{\epsilon_{\mathrm{eV}}}
 \left[\sum_i v_{*,i}\kappa_{RR,i}+v_{*,1}\sum_{j=1}^2\kappa_{DR,j}\right],\qquad
B_{esc}=\sum_i\chi_iR_i+\chi_1(D_1+D_2).
\tag{P9}
\]

All edge-vector indices in (P7)–(P13) are zero-based, i.e. 0=HI, 1=HeI, 2=HeII; component 1 of the vector \(v_*\) is therefore its second entry. Binding thresholds are the adopted exact parent values, distinct from the fit cutoffs. The incidence rows are

\[
\nu_0=(1,0,0),\quad\nu_1=(0,1,0),\quad\nu_2=(0,-1,1).
\]

With edge labels 0,1,2, the full anchor source is

\[
\begin{aligned}
S_\zeta&=\sum_{i=0}^2\nu_i\left(\sum_qr_{iq}+C_i-R_i\right)-\nu_1(D_1+D_2),\\
S_t&=\sum_{iq}(E_q^*-\chi_i)r_{iq}-\sum_i\chi_i C_i-K,\\
S_m&=\sum_{iq}E_qe_qr_{iq}-\gamma_*\beta_*(K+B_{esc}).
\end{aligned}\tag{P10}
\]

The thermal simplification uses the exact anchor relative Lorentz factor \(\Gamma_*=1\); it does not drop the escape terms from the general source or its derivative bounds. With \(s_\zeta=10^{-3}\), \(s_t=1/4\) and \(s_m=a_*10^{-6}\), define the exact rational predictor

\[
p(h;\mu)=h\widehat G_h(0),\qquad
\overline X(h,\xi;\mu)=\xi+p(h;\mu).
\tag{P11}
\]

The actual momentum scale remains \(s_m=a_*(\mu)10^{-6}\). Only inequalities use its uniform lower bound \(s_m\ge1000\). Thus the predictor is the full seven-component rational expression in \(h,\mu\); the certificate is uniform in \(\mu\).

### 2.1. Exact error propagation at the anchor

Let \(e_{\lambda,iq}=cD y_{*,i}(1-\beta_*\cdot e_q)e_{\sigma,iq}\) and \(e_{\Lambda,q}=\sum_i e_{\lambda,iq}\). For nonnegative exact and midpoint coefficients, subtract the two fractions in (P7):

\[
r_{iq}-\widehat r_{iq}=
\frac{p_q^-(\lambda_{iq}-\widehat\lambda_{iq})}{1+h\Lambda_q}
-\frac{p_q^-h\widehat\lambda_{iq}(\Lambda_q-\widehat\Lambda_q)}
 {(1+h\Lambda_q)(1+h\widehat\Lambda_q)}.
\]

Both denominators are at least one, so uniformly on \([0,H]\),

\[
|r_{iq}-\widehat r_{iq}|\le
 d_{iq}(H):=p_q^-\bigl(e_{\lambda,iq}+H\widehat\lambda_{iq}e_{\Lambda,q}\bigr).
\tag{P12}
\]

The errors \(e_C,e_R,e_D,e_K,e_B\) follow by replacing each coefficient in (P8)–(P9) by its nonnegative interval halfwidth and retaining every exact positive prefactor. Let \(d_i=\sum_qd_{iq}\). Componentwise source-error bounds are

\[
\begin{aligned}
\varepsilon_1&=10^3(d_0+e_{C_0}+e_{R_0}),\\
\varepsilon_2&=10^3(d_1+d_2+e_{C_1}+e_{C_2}+e_{R_1}+e_{R_2}+e_{D_1}+e_{D_2}),\\
\varepsilon_3&=10^3(d_2+e_{C_2}+e_{R_2}),\\
\varepsilon_4&=4\left[\sum_{iq}|E_q^*-\chi_i|d_{iq}+\chi\cdot e_C+e_K\right],\\
\varepsilon_{4+k}&=\frac1{1000}\left[\sum_{iq}E_q|e_{q,k}|d_{iq}
+\gamma_*|\beta_{*,k}|(e_K+e_B)\right]\quad(k=1,2,3).
\end{aligned}\tag{P13}
\]

Therefore \(|G_{h,i}(0)-\widehat G_{h,i}(0)|\le\varepsilon_i(H)\). These bounds do not require cancellation. At the anchor the two transverse momentum rows actually vanish by exact opposite-ray parity, for both the true and midpoint models, so the executed certificate uses zero defect in rows 5 and 6. The halfwidth input, propagated exact values and convenient outward rational caps are retained with the executed anchor certificate. Specifically that result bounds the displacement defect on [0,H_2]; dividing its cap by H_2 gives a source-defect bound uniform on both slabs. The first slab uses this same conservative source-defect bound.

### 2.2. Predictor magnitude on a whole parameter slab

Every term \(h\widehat r_{iq}(h)=p_q^-\widehat\lambda_{iq}h/(1+h\widehat\Lambda_q)\) is nonnegative and increasing for \(h\ge0\), since its derivative is \(p_q^-\widehat\lambda_{iq}/(1+h\widehat\Lambda_q)^2\). Atomic terms are constant multiples of \(h\). Collect the constant terms into \(a_p\) and the six denominator coefficients into \(B_p\), so that the five nonzero predictor rows equal \(h[a_p+B_p(1+h\widehat\Lambda)^{-1}]\), with the prescribed extra \(1/a_*\) on row 7. The two transverse rows are identically zero. Applying the triangle inequality after this exact collection gives \(H_j|a_p|+|B_p|[H_j/(1+H_j\widehat\Lambda)]\), and hence an exact rational vector \(P_j^{row}\) with

\[
|p_i(h;\mu)|\le P_{j,i}^{row}\le P_j,\quad h\in I_j,\quad
P_j\ge\max_iP_{j,i}^{row}.
\tag{P14}
\]

This is a full-interval proof. Endpoint evaluation is justified by the analytic monotonicity of the positive majorant; no grid or trajectory is substituted for the interval.

## 3. Concrete fixed preconditioners

Freeze \(T,\gamma,\beta\) at their anchor values and retain the exact electron closure \(e_H(\zeta)=\zeta_1+\zeta_2+2\zeta_3\), target abundances \(y(\zeta)\), upper populations \(v(\zeta)\), and the eliminated-photon denominators. Use the midpoint coefficients to define \(\widehat S_\zeta^{fr}(\zeta,h)\) by (P7)–(P10) with those variable abundances.

For \(h_{c,1}=2.5\times10^8\) and \(h_{c,2}=7.5\times10^8\), set

\[
J_j=\left.\frac{\partial\widehat S_\zeta^{fr}}{\partial\zeta}\right|_{\zeta_*,h_{c,j}},\quad
A_j=\operatorname{diag}\bigl[(I_3-h_{c,j}J_j)^{-1},I_4\bigr].
\tag{P15}
\]

All entries are rational. Because all three abundance scales are equal, the frozen chemical derivative is the corresponding scaled chemical derivative. The actual full Jacobian additionally differentiates the primitive recovery, temperature, velocity and all retained source terms. Its bounds (P3) are used in the certificate. The frozen block is only the fixed preconditioner in (P15); no claim identifies it with the exact chemical block. Exact nonsingularity and a rational norm enclosure for each \(A_j\) are checked in the new evaluator call.

## 4. Uniform-radius full-Jacobian tube theorem

For \(I_1=[0,5\times10^8]\,\mathrm s\) and \(I_2=[5\times10^8,10^9]\,\mathrm s\), let

\[
\mathcal T_j(h,\xi)=\{X:\|X-\overline X(h,\xi)\|_\infty\le\rho_j\},\qquad h\in I_j.
\tag{P16}
\]

First require the physical inclusion

\[
\eta+P_j+\rho_j<1.
\tag{P17}
\]

Then every tube and every line from its predictor to zero lie in \(Q\). By (P3) and (P13),

\[
|F_i(\overline X,h;\xi)|
\le R_{j,i}:=H_j[\varepsilon_i(H_j)+\ell_i(H_j)(\eta+P_j)].
\tag{P18}
\]

Define nonnegative vectors

\[
Y_j=|A_j|R_j,\qquad
z_j=|I-A_j|\mathbf1+H_j|A_j|\ell(H_j),\qquad q_j=\max_i z_{j,i}.
\tag{P19}
\]

For the preconditioned corrector map \(T_j(X)=X-A_jF(X,h;\xi)\),

\[
D_XT_j=I-A_j+hA_jD_XG_h.
\]

Hence the \(i\)-th absolute row sum of this **full seven-by-seven Jacobian** is at most \(z_{j,i}\). A row-sum certificate suffices for the uniform \(\ell^\infty\) radius; it is not an entrywise majorant matrix and no artificial matrix entries are inferred from it.

If exact or outward rational inequalities show

\[
Y_{j,i}+\rho_jz_{j,i}<\rho_j\quad(i=1,\ldots,7),\qquad q_j<1,
\tag{P20}
\]

then for each fixed \((h,\xi,\mu)\), \(T_j\) maps the complete closed tube strictly into itself and is a contraction. Banach's fixed-point theorem gives a unique fixed point there. Since \(A_j\) is invertible, fixed points are precisely zeros of \(F\). The derivative is nonsingular, with

\[
\|F_X^{-1}\|_\infty\le\frac{\|A_j\|_\infty}{1-q_j}.
\tag{P21}
\]

Strict margins, smooth retained coefficients and primitive recovery give joint \(C^1\) dependence on \((h,\xi)\) in a neighborhood of each certified parameter point. At boundaries, the branch is the restriction of that local continuation; compact parameter sets and uniqueness join the local neighborhoods.

### 4.1. Stronger uniqueness from the inherited derivative bound

If \(q_Q=H_2\max_i\ell_i(H_2)<1\), any two roots in \(Q\) obey

\[
\|X-Y\|_\infty=\|h[G_h(X)-G_h(Y)]\|_\infty\le q_Q\|X-Y\|_\infty.
\]

Thus the certified root is unique in the entire physical cube for each fixed \((h,\xi,\mu)\), even when the old zero-centered cube self-map \(H_2B<1\) fails. This conclusion uses convexity of \(Q\) and the full-domain derivative bound. It does not require self-mapping the whole cube. Also

\[
\|F_X^{-1}\|_\infty\le(1-q_Q)^{-1}.
\tag{P22}
\]

This sharper uniform bound will be used for old-state sensitivity.

### 4.2. Common-root connection

Both tubes use the same exact rational function \(p(h;\mu)\) and the same \(\xi\). If \(\rho_1\le\rho_2\), then at \(h_*=5\times10^8\,\mathrm s\),

\[
\mathcal T_1(h_*,\xi)\subseteq\mathcal T_2(h_*,\xi).
\tag{P23}
\]

The first tube's root is consequently inside the second root's uniqueness domain; they coincide. At \(h=0\), \(p(0)=0\) and \(F=X-\xi\), so the branch starts at \(X(0,\xi)=\xi\). For \(\xi=0\), parent and new roots belong to \(Q\) and share the same residual, hence agree throughout their common \(h\) interval by cube uniqueness. This is the required same-root connection, not merely intersection of two boxes.

## 5. Error and state bounds produced by the tube

At the exact root, the predictor error has the uniform scalar bound

\[
\|X-\overline X\|_\infty\le e_j:=\frac{\max_iY_{j,i}}{1-q_j}\le\rho_j.
\tag{P24}
\]

A componentwise refinement is

\[
|X_i-\overline X_i|\le Y_{j,i}+z_{j,i}e_j.
\tag{P25}
\]

For a trial point \(\widetilde X\) in the same tube,

\[
\|X-\widetilde X\|_\infty\le
\frac{\|A_jF(\widetilde X,h;\xi)\|_\infty}{1-q_j}.
\tag{P26}
\]

A rigorous finite-precision implementation must include the residual evaluation and preconditioner multiplication errors in the numerator. Formula (P26) is a posteriori error transport, not an assertion that any native solver has been run.

If exact corrector updates start at \(\overline X\), their theorem bound is

\[
\|X^{(k)}-X\|_\infty\le q_j^k e_j.
\tag{P27}
\]

No corrector updates are needed to prove or evaluate this inequality. A displayed update count is an a-priori contraction estimate, not an executed iterative trajectory.

The physical abundance displacements from the common reference are at most \(10^{-3}(\eta+P_{j,i}^{row}+e_j)\). For temperature and velocity, the parent primitive Lipschitz constants yield

\[
|T-T_*|\le1400(\eta+P_j+e_j)\,\mathrm K,\qquad
|\beta-\beta_*|_2\le3\times10^{-6}(\eta+P_j+e_j).
\tag{P28}
\]

These are certified endpoint enclosures for an implicit stage parameter family. Time-history error needs a separate time integration contract.

## 6. Discriminating questions and adoption boundary

The new numerical calculation must show (i) exact rational coefficient enclosures, (ii) all fourteen tube inequalities, (iii) physical inclusion for both complete parameter slabs, (iv) invertibility of both fixed preconditioners, (v) common-root nesting, and (vi) \(H_2>1/B\) using the unchanged parent \(B\). A subdivision of the former unchanged cube would not answer (vi); the rational predictor and translated tubes are the constructive mechanism.

The old input family, finite affine transition and mixed moving-anchor xAct checks are derived in `OLD_STATE_FAMILY_AND_REANCHORING.md`. Actual numerical values and evidence identities are recorded in `TUBE_CERTIFICATE_NUMBERS.md` and `../evidence/TUBE_CERTIFICATE_RESULT.json`. All retained native implementation obligations and the original owner DAG remain in the coding handoff.
