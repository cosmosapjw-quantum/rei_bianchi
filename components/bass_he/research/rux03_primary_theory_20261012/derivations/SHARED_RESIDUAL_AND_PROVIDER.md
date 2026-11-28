# Shared-event residual and coefficient-provider construction

Unit: HERE_RUX03_PRIMARY_THEORY_03. Author: /root. 2026-10-12.
The fixed assumptions and source identity are in ../dossier/SCIENTIFIC_CONTRACT.md
and ../source_map/CURRENT_SOURCE.json. Results below concern that stage model.

## 1. Coordinates, units and primitive events

Write v=(x,a,b)=(HII,HeII,HeIII), y=(v,w), f=n_He/n_H, and

\[
e=x+f(a+2b),\qquad d=1+f+e,\qquad n_e=n_H e,
\]
\[
w=c_v dT,\quad c_v=\frac{3k_B}{2\epsilon_{\rm eV}},\quad
T=\tau w/d,\quad \tau=c_v^{-1}.
\tag{1}
\]

Here w is eV per H nucleus, k_B is in erg/K and epsilon_eV is erg/eV.
All C_i,R_i,D_r below are events per H nucleus per second. K_i and L_r
are captured kinetic powers in eV per H nucleus per second. P_iq is the
photo-event rate in channel i at node q, in the same event units.

For i=(HI,HeI,HeII), let chi_i denote the binding energies already used by
the source. Define

\[
j_i=C_i-R_i+\sum_qP_{iq}-\mathbf1_{i=1}\sum_{r=0}^1D_r,
\quad G(v,w)=\left(j_0,\frac{j_1-j_2}{f},\frac{j_2}{f}\right),
\tag{2}
\]
\[
B(v)=\chi_0 x+f\chi_1 a+f(\chi_1+\chi_2)b,
\quad \boldsymbol b_\chi=\nabla_vB=(\chi_0,f\chi_1,f(\chi_1+\chi_2)).
\tag{3}
\]

The common event-to-power projections are

\[
Q=-\sum_i\chi_i C_i-\sum_iK_i-\sum_rL_r
       +\sum_{iq}(E_q-\chi_i)P_{iq},
\tag{4}
\]
\[
Q_{\rm esc}=\sum_i(\chi_iR_i+K_i)+\chi_1\sum_rD_r+\sum_rL_r.
\tag{5}
\]

CI transfers thermal to binding energy; RR/DR transfer binding and captured
kinetic energy to the Case A escape account. A primary photo-event removes
E_q from its photon and deposits chi_i in binding and E_q-chi_i in heat.
These are the linear projections already established in EVENT_BRIDGE_02.

**Lemma 1 (event identity).** At every candidate state, independently of
whether it solves a stage equation,

\[
Q+\boldsymbol b_\chi^T G+Q_{\rm esc}=\sum_{iq}E_qP_{iq}.
\tag{6}
\]

**Proof.** Equation (2) gives b_chi^T G=sum_i chi_i j_i. For each CI channel,
the terms -chi_i C_i and +chi_i C_i cancel. For each RR channel the three
terms are -K_i, -chi_i R_i and chi_i R_i+K_i. For each DR channel they are
-L_r, -chi_1 D_r and chi_1 D_r+L_r. A photo-event contributes
(E_q-chi_i)P_iq+chi_i P_iq=E_qP_iq. Summing proves (6). The proof is linear
in independent event counts and moments; it does not divide a moment by a
possibly zero event rate.

## 2. Exact source-aware reconstruction and Schur derivative

At a prescribed stage let p_q be photons per H nucleus and s_q their external
source in photons per H nucleus per second. With

\[
\ell=(1-x,\ f(1-a-b),\ fa),\quad
\lambda_{iq}=c n_H\sigma_{iq}\ell_i,\quad \lambda_q=\sum_i\lambda_{iq},
\]
\[
W_q=p_q^0+h s_q,\quad D_q=1+h\lambda_q,
\quad \Phi_q(y)=\frac{W_q}{D_q},\quad P_{iq}=\lambda_{iq}\Phi_q,
\tag{7}
\]

the photon residual F_pq=p_q-p_q^0-hs_q+h sum_i P_iq vanishes exactly at
p=Phi(y). Nonnegative input and source give Phi>=0 and D_q>=1. The case
s=0, including differentiation through Phi, is implemented in the current
primary; source and geometry generalizations are derived in the independent
PHOTON_ELIMINATION.md.

For a full gas/photon residual with block Jacobian J, the photon block is
J_pp=diag(D_q). The chain rule at a reconstructed state gives

\[
D_y\Phi=-J_{pp}^{-1}J_{py},\qquad
D_yF_{\rm red}=J_{yy}-J_{yp}J_{pp}^{-1}J_{py}.
\tag{8}
\]

**Proof.** Differentiate F_p(y,Phi(y))=0, solve its diagonal linear system,
and substitute the derivative in F_g(y,Phi(y)). This is the exact Schur
complement of the assembled full derivative. At a full Newton iterate with
F_p=0, the gas increment from that block elimination is the reduced Newton
increment. A reduced iteration reconstructs photons again at its new gas
state. Equation (8) concerns this gas increment; a linear full-space photon
increment and nonlinear reconstruction can differ at quadratic order.

The state dependence in (7) stays inside the function being solved. Existing
nonlinear proposals may freeze its coefficients at a guess and then update
the guess; the endpoint residual and its derivative are defined by (2),(4),(7).

## 3. Thermal and conservative residuals are a constant row transformation

The thermal stage residual and the species residual are

\[
F_v=v-v^0-hG,\qquad F_w=w-w^0-h(Q-2Hw).
\tag{9}
\]

Also write F_esc=epsilon- epsilon^0-hQ_esc. For fixed node energy in the
microphysics substep, define the total-energy residual

\[
F_{\rm total}=\Delta w+\Delta B+\Delta\epsilon+\sum_qE_q\Delta p_q
                   +2hHw-h\sum_qE_q s_q.
\tag{10}
\]

**Theorem 2 (off-solution residual identity).**

\[
F_{\rm total}=F_w+\boldsymbol b_\chi^TF_v+F_{\rm esc}+\sum_qE_qF_{pq}.
\tag{11}
\]

After reconstructing photons by (7) and escape by epsilon=epsilon^0+hQ_esc,
the reduced conservative row is

\[
F_E=(1+2hH)w-w^0+\Delta B+hQ_{\rm esc}
                    +\sum_qE_q(p_q-p_q^0-hs_q),
\tag{12}
\]
\[
F_E=F_w+\boldsymbol b_\chi^TF_v.
\tag{13}
\]

**Proof.** Substitute the definitions in the right side of (11). The change
terms give (10). The remaining rate terms are h[-Q-b_chi^TG-Q_esc+
sum_iq E_qP_iq], which vanish by Lemma 1. Reconstruction sets F_p=F_esc=0
and gives (12)-(13). This identity is valid before the gas residual vanishes.

Order gas residuals as F=(F_v,F_w) and F^E=(F_v,F_E). Then

\[
F^E=L_\chi F,\quad
L_\chi=\begin{pmatrix}I_3&0\\\boldsymbol b_\chi^T&1\end{pmatrix},\quad
L_\chi^{-1}=\begin{pmatrix}I_3&0\\-\boldsymbol b_\chi^T&1\end{pmatrix}.
\tag{14}
\]

Thus the two systems have exactly the same zeros and
J^E=L_chi J. At a nonsingular derivative, J delta=-F and
J^E delta=-F^E give the same Newton increment. Existing ordinary and
conservative fixed-point proposals can have different iterates; (13) ties
their endpoint equations. A stopping norm or line search can distinguish the
two row representations, so the proposed implementation retains one declared
canonical endpoint criterion.

For a fixed positive scaling S, use L_hat=S L_chi S^{-1}. With the current
style S=diag(1,1,1,1/w_scale), the last row contains b_chi/w_scale and 1.
The scaling must be fixed for differentiation. It can be chosen from the
known incoming point, rather than made a function of the unknown w.

### 3.1 Stable absorption form and a constructive thermal-domain condition

Compute each absorbed event count A_iq=h lambda_iq Phi_q and A_q=sum_i A_iq
directly. Equation (7) implies p_q-p_q^0-hs_q=-A_q, giving

\[
F_E=(1+2hH)w-w^0+\Delta B+hQ_{\rm esc}-\sum_qE_qA_q.
\tag{15}
\]

This form avoids recovering a small absorption by subtracting a large photon
reservoir and injection. Once the candidate's events are evaluated, define

\[
U=w^0-\Delta B-hQ_{\rm esc}+\sum_qE_qA_q,\qquad
\widetilde w=U/(1+2hH).
\tag{16}
\]

The proposed thermal state has temperature in [T_min,T_max] precisely when

\[
(1+2hH)c_v d\,T_{\min}\ \le U\le\ (1+2hH)c_v d\,T_{\max}.
\tag{17}
\]

This is an explicit budget check on a candidate proposal. Positive U gives
positive w. Retaining the existing compensated Delta-w update is compatible
with (15). Thermal rates are re-evaluated at the final candidate when applying
the canonical endpoint residual, as the current solver already does.

### 3.2 Root certification under row changes

In real arithmetic choose a preconditioner R for F and R^E=R L_chi^{-1} for
F^E. Then R^EF^E=RF and I-R^EJ^E=I-RJ. Consequently the exact set-valued
Krawczyk construction is unchanged under this consistent row/preconditioner
change. If independently assembled interval entries are multiplied before
the algebra is simplified, dependency loss can enlarge the enclosure.

The concrete handoff therefore retains the thermal residual as the canonical
four-variable interval field and uses the common event projection for it.
The conservative row is evaluated from (15) for the point proposal and energy
diagnostic. A future implementation can change interval rows by preserving
the simplified preconditioned expression and checking the resulting enclosure.
The current source's K subset int(Y) and q<1 gates stay tied to the actual map.

## 4. Coefficient-level provider defined on species boundaries

The point iteration needs destruction/creation intensities even when an
incoming population is zero. Supply the following functions of temperature:

\[
\mathcal C(T)=\{\beta_i(T),\alpha_i(T),\delta_r(T),
                  \kappa_i(T),\zeta_r(T)\}.
\tag{18}
\]

beta, alpha, delta have units cm^3/s. kappa and zeta are kinetic power
coefficients in erg cm^3/s. They are nonnegative on the chosen temperature
domain. Preserve the existing event-bundle compatibility conditions
alpha_i(T)=0 implies kappa_i(T)=0, and delta_r(T)=0 implies zeta_r(T)=0.
The selected FT03 formulas satisfy these conditions; they also specify the
admissibility check for a common coefficient object. Define upper populations
per H as u=(x,fa,fb). The primitive lift is

\[
C_i=n_H\ell_i e\,\beta_i(T),\quad R_i=n_Hu_i e\,\alpha_i(T),
\quad D_r=n_Hu_1 e\,\delta_r(T),
\tag{19}
\]
\[
K_i=\frac{n_Hu_i e\,\kappa_i(T)}{\epsilon_{\rm eV}},\quad
L_r=\frac{n_Hu_1 e\,\zeta_r(T)}{\epsilon_{\rm eV}}.
\tag{20}
\]

Proper-cgs event outputs are n_H times (19); proper-cgs powers are
n_H epsilon_eV times (20). This gives an explicit bridge to the existing
conditional CaseAEventBundle without changing its units.

Equations (19)-(20) remain defined for u_i=0 or n_e=0. The same coefficients
directly supply the existing positive chemistry proposal:

\[
I_i=n_e\beta_i+c n_H\sum_q\sigma_{iq}\Phi_q,\quad
r_0=n_e\alpha_0,\quad r_1=n_e(\alpha_1+\sum_r\delta_r),\quad
r_2=n_e\alpha_2.
\tag{21}
\]

No reconstruction of alpha or beta from a zero event/population ratio is
needed. A provider owns the coefficient functions and primitive lift; its
event summary is the evaluated diagnostic view of that lift.

### 4.1 Positive chemistry construction reused from the primary

At a coefficient guess set A=h I_1, B=h r_1, C=h I_2, D=h r_2 and
h_0=1-a_0-b_0. The full He fractions obey the resolvent of

\[
\mathsf A=\begin{pmatrix}-I_1&r_1&0\\I_1&-(r_1+I_2)&r_2\\0&I_2&-r_2\end{pmatrix}.
\tag{22}
\]

Its column sums vanish and off-diagonal entries are nonnegative. Solving
(I-h A) z=z_0 gives the already implemented formulas

\[
a_+=\frac{a_0+A h_0/(1+A)+D b_0/(1+D)}
             {1+B/(1+A)+C/(1+D)},\quad
b_+=\frac{b_0+C a_+}{1+D},\quad
h_+=\frac{h_0+B a_+}{1+A}.
\tag{23}
\]

All fractions are nonnegative. Adding the three equations before solving
gives h_++a_++b_+=1. Hydrogen has the corresponding two-state result
x_+=(x_0+hI_0)/(1+h(I_0+r_0)). Zero rates and zero populations are admitted.
This is the full generator's nonnegative resolvent expressed in reduced
coordinates, matching Blanes et al. (2022), Proposition 3.4. The present
contribution is the shared provider construction (18)-(21) that preserves
these already existing proposals while changing the event-consumption seam.

## 5. Explicit first and second derivatives for the shared lift

Let t=(1,f,2f), extended by t_w=0, and let indices i,j range over all four
gas coordinates. For chemical coordinates r,s, equation (1) gives

\[
T_r=-Tt_r/d,\quad T_w=\tau/d,\quad
T_{rs}=2Tt_rt_s/d^2,\quad T_{rw}=-\tau t_r/d^2,\quad T_{ww}=0.
\tag{24}
\]

n_e has gradient n_H(t,0) and zero Hessian. For any affine population m(v)
and any coefficient c(T), put A(v)=m(v)e(v). Then

\[
A_i=m_i e+m e_i,\qquad A_{ij}=m_i e_j+m_j e_i,
\]
\[
\partial_i[n_H A c]=n_H[A_i c+A c'T_i],
\tag{25}
\]
\[
\partial_{ij}[n_H A c]=n_H[A_{ij}c+A_i c'T_j+A_j c'T_i
                      +A(c''T_iT_j+c'T_{ij})].
\tag{26}
\]

Taking m=ell_i or u_i gives every rate; choosing the power coefficient and
dividing by epsilon_eV gives every captured kinetic power. At population-zero
faces the rate can vanish while its incoming-population derivative is nonzero;
(25) retains that derivative without division.

For the externally prescribed source and fixed stage cross sections,
lambda_q is affine in the three fractions and independent of w. Thus

\[
\Phi_{q,i}=-\frac{h\Phi_q}{D_q}\lambda_{q,i},\qquad
\Phi_{q,ij}=\frac{2h^2\Phi_q}{D_q^2}\lambda_{q,i}\lambda_{q,j},
\tag{27}
\]
\[
P_{aq,i}=\lambda_{aq,i}\Phi_q+\lambda_{aq}\Phi_{q,i},
\]
\[
P_{aq,ij}=\lambda_{aq,i}\Phi_{q,j}+\lambda_{aq,j}\Phi_{q,i}
                         +\lambda_{aq}\Phi_{q,ij}.
\tag{28}
\]

All the thermal, binding and escape derivatives then follow from the same
linear projections (2)-(5). No event needs an independent second consumption
to compute a derivative.

### 5.1 Kinetic moment differentiation

For the current analytic RR fit the kinetic coefficient is

\[
\kappa(T)=k_BT\alpha(T)[3/2+g(T)],\qquad g=T\alpha'/\alpha.
\tag{29}
\]

Its derivatives are

\[
\kappa'=k_B[\tfrac32\alpha+\tfrac72 T\alpha'+T^2\alpha''],
\quad
\kappa''=k_B[5\alpha'+\tfrac{11}2T\alpha''+T^2\alpha'''].
\tag{30}
\]

This identifies a concrete derivative obligation: constructing the moment
through derivatives of alpha uses alpha''' for the moment Hessian. A more
direct implementation evaluates the explicit analytic expression for kappa
with the same scalar/Jet algebra as alpha. The declared contract requires
each function in (18) to have a valid C2 lift, so an independently supplied
moment has its own derivatives. For the existing DR fit, zeta_r is
delta_r(T) times its fixed captured energy, and inherits that expression's
derivatives. The source already evaluates analytic moment expressions in its
interval path; the next adapter should preserve those dependencies.

### 5.2 Point / interval agreement as a constructive inclusion result

Evaluate the same (18)-(20),(7),(2),(4) expression graph with either real
scalars or outward interval Jets. Suppose each primitive operation and each
coefficient lift encloses the value and needed derivatives on the input box,
with d>0, D_q>=1 and T in the declared provider domain. Induction over that
expression graph proves that the resulting interval value, gradient and
Hessian enclose the point field and its derivatives everywhere in the box.
Products use the product rule, unary functions use the chain rule, and the
event ledger is a fixed linear map; (24)-(28) give the same derivatives
explicitly. This is the mathematical point/interval contract.

For the concrete FT03 implementation, use one pinned set of fit constants
and the same selected provider identity in ordinary point, conservative
point, endpoint and interval calls. The current point function and interval
formula are separate source expressions. Factoring their common coefficient
algebra is the proposed implementation work; this theory supplies its exact
equations and inclusion obligation.

## 6. A single-channel residual-and-derivative witness

Take a manufactured positive HeIII RR coefficient increment delta alpha_2
=rho (cm^3/s), and delta kappa_2=epsilon_eV eta rho, with eta>=0 in eV.
At fixed state define

\[
r_\delta=n_H f b e\,\rho,\qquad k_\delta=\eta r_\delta.
\tag{31}
\]

One consumption produces

\[
\delta G=(0,r_\delta/f,-r_\delta/f),\quad
\delta Q=-\eta r_\delta,\quad
\delta Q_{\rm esc}=(\chi_2+\eta)r_\delta,\quad \delta\Phi_q=0.
\tag{32}
\]

For the canonical reduced residual its exact perturbation is

\[
\delta F=h r_\delta(0,-1/f,1/f,\eta)^T,
\quad
\delta F^E=h r_\delta(0,-1/f,1/f,\chi_2+\eta)^T.
\tag{33}
\]

For constant rho,

\[
\nabla r_\delta=n_H f\rho\,(b,fb,e+2fb,0),
\tag{34}
\]
\[
\nabla^2r_\delta=n_H f\rho
\begin{pmatrix}0&0&1&0\\0&0&f&0\\1&f&4f&0\\0&0&0&0\end{pmatrix}.
\tag{35}
\]

Differentiate (33) with (34)-(35) to obtain all expected residual Jacobian
and Hessian shifts. These checks distinguish omitted or repeated consumption
and the population/electron-density dependence of the moment. The photon
reconstruction stays fixed at a fixed gas candidate; after solving a changed
physical residual the gas state, and hence its reconstructed photons, can
change. This witness compares evaluations at the same candidate.

The event identity alone cancels an event even if it is erroneously consumed
twice. Equation (33), with the known coefficient increment and multiplicity
one, provides the discriminating check for the next coding loop.

### 6.1 A temperature-sensitive companion

To probe the kinetic coefficient's temperature derivatives as well, use

\[
\rho(T)=\rho_\star(T/T_\star)^2,\qquad
\delta\kappa_2(T)=\epsilon_{\rm eV}\eta\rho(T),
\quad \rho_\star,T_\star,\eta>0.
\tag{35a}
\]

The rate r_delta in (31) now uses this rho(T), and the event/residual shifts
(32)-(33) remain exactly the same. Equations (25)-(26) give all of its
derivatives without a population division. Holding the fractions fixed,
T is proportional to w, so in particular

\[
\partial_w r_\delta=2r_\delta/w,\qquad
\partial_{ww}r_\delta=2r_\delta/w^2,
\]
\[
\partial_w\delta F_w=2h\eta r_\delta/w,\qquad
\partial_{ww}\delta F_w=2h\eta r_\delta/w^2.
\tag{35b}
\]

For an interior candidate with b>0 and e>0 these are strictly positive.
Freezing the injected kinetic coefficient's temperature dependence would
instead give zero for these thermal derivatives. Thus (35a)-(35b) supply
the missing temperature-specific discriminator. The constant witness retains
its simpler population/charge derivative check, and this companion tests the
additional coefficient dependence. The independent review identified the
original constant-witness wording as too broad; the correction and its exact
algebra check are preserved in this unit's evidence/review records.

## 7. Preserve the native energy variable under an optional T coordinate

One may solve the same endpoint residual in coordinates (v,T) by substituting
w=c_v d(v)T. The chain rule gives the exact Jacobian of that coordinate change.
The finite-step identity is

\[
\Delta w=c_v[d_+\Delta T+T_0\Delta d]
        =c_v[d_0\Delta T+T_+\Delta d].
\tag{36}
\]

By contrast, discretizing the continuous temperature equation separately
with endpoint d and T uses c_v[d_+Delta T+T_+Delta d], provided the same
species endpoint equation makes Delta d=h dot d. Its residual differs from
the native energy residual by exactly

\[
c_v\Delta T\Delta d.
\tag{37}
\]

This is a computed finite-step correction, O(h^2) along a smooth solution.
The concrete handoff keeps w as the native BE state; if T is used as a solver
coordinate, it evaluates the original energy residual after substitution.
That construction preserves the current energy map and event ledger.

## Evidence and adoption links

The exact evaluator script and raw response are in ../evidence/. Independent
photon/geometry derivations are in PHOTON_ELIMINATION.md. Source-specific
callsites and reused implementation are in ../source_map/SOURCE_MAP.md.
Final adoption is recorded separately in ../review/DECISION.json.
