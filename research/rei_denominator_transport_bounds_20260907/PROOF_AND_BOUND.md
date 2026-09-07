# REI: a denominator-only bound for the mapped population stages

Work unit: REI_POPULATION_DENOMINATOR_TRANSPORT_BOUND_V1.
Task: derive and validate a partial scientific bound, not implement a production solver.
Parent: 032b59372e55bdbb86860e8075206bd0026f7be1 / tree 7220d791d614d34e63097e3115c8036fcfcb8e94 (PR #74).

## 1. What is inherited and what is new

PR #74's STAGE_MAPPING.md and the actual mprk22.py identify the predictor,
gamma population and corrector denominators as y0,y0,yp; all three RHSs are
y0. The corrector uses (F0+F1)/2 in its matrix. Its ALGEBRA_RESULT.json and
original exact-stage-algebra.log record 10/10 local algebra checks. Those
checks, the earlier #73 checker, XZ/GCC consumers and native work are NOT rerun.
The main conversation read the mapped equations and actual kernel, and accepts
that bounded source correspondence, not the absent four-site production ABI.

New result: cancel the inverse-square denominator derivative inside the
resolvent; derive its exact log-denominator sensitivity, a finite-difference
identity, and uniform partial gains on an explicitly declared continuum box.
These gains concern the *frozen-flux* map. F0 and F1 are independently chosen
but held identical in both compared paths and are not differentiated. This
retains denominator and direct-parent-RHS derivatives. It is NOT the full
state derivative of the physical MPRK method, whose fluxes must also vary.
No atomic flux envelope for a physical REI trajectory is inferred from our box.

## 2. Definitions and units

F_ij is the nonnegative transfer count rate from source j to destination i;
its diagonal is zero. Define B_ij=F_ij for i!=j and
B_jj=-q_j, q_j=sum_(i!=j)F_ij. Let D(d)=diag(1/d_j), d_j>0,
A=B D(d), L=I-hA, P=L^-1, and x=P b with b>0 and h>=0.

In the preserved source b and d are extensive counts per node in the fixed
one-comoving-Mpc^3 normalization, F is counts/s, h is proper seconds, B D is
s^-1. Thus h B D is dimensionless. No c^-1 time conversion or natural units
are introduced. The five species are HI,HII,HeI,HeII,HeIII. The only directed
edges are (1,0),(0,1),(3,2),(2,3),(4,3),(3,4), using zero-based indices.
Weights w=(cH,cH,cHe,cHe,cHe)>0 are fixed between compared paths. This gives
w^T B=0 and ||P||_(1,w)=1. Element totals and quadrature weights are not
renormalized separately at each evaluation site.

The algebra below is over exact reals. It does not certify binary64 solver
rounding, observed production arrays, MPFR residuals, or runtime admission.
Step and B are fixed for each derivative and each finite pair. For a parameter
g, D_g=-D diag(d_g/d). A parameter-dependent reweighting b'=T(g)b requires
b'_g=T_g b+T b_g; it cannot be treated as a constant RHS. Our d_g/d is a
componentwise ratio, not an extra differentiation of B.

## 3. Exact cancellation inside the solve

Differentiating Lx=b at fixed B,h yields

    x_g = P b_g + h P B D_g x.

Since h P B D=P-I and D^-1 D_g=-diag(d_g/d),

    x_g = P b_g + (I-P) diag(x) (d_g/d).                 (1)

This expression is exact, not a first-order truncation of the matrix inverse.
The coefficient derivative contains 1/d_j^2, but its solved contribution
contains a *relative* denominator perturbation and a bounded transfer operator.
For a pure denominator variation, w^T x_g=0. With a moving RHS,
w^T x_g=w^T b_g. The direct P b_g term must not be dropped.

Because P>=0 and w^T P=w^T, column j of W(I-P)W^-1 has absolute sum
(1-P_jj)+sum_(i!=j)(w_i/w_j)P_ij=2(1-P_jj). Therefore

    kappa(P) := ||I-P||_(1,w) = 2 max_j(1-P_jj) <= 2,
    ||x_g||_(1,w) <= ||b_g||_(1,w)
                       + kappa(P)*M*||d_g/d||_infinity, (2)

where M=w^T b. This is not a full-map contraction claim.

Column j of L P=I has (1+h q_j/d_j)P_jj=1+nonnegative incoming terms.
Thus P_jj>=1/(1+h q_j/d_j), so

    kappa(P) <= 2 max_j h q_j/(d_j+h q_j).               (3)

On any domain d_j>=m_j>0, q_j<=Q_j and 0<=h<=hmax, replace d,q,h in
(3) by m,Q,hmax to obtain a *uniform* upper bound kappa_bar. Hence

    ||x_g||_(1,w) <= ||b_g||_(1,w)
                      + kappa_bar*M*max_j |d_g,j|/m_j.  (4)

No endpoint sampling is needed for (3)-(4). They require quantitative margins
for absolute perturbations. Only the relative/log-denominator operator bound
has the universal factor 2 independent of those margins. This does not prove
uniform absolute smoothness or high-order accuracy at zero population.
At h=0 or B=0, P=I and the denominator term is exactly zero.

## 4. Finite pairs, not just point JVPs

With the same B,h and two positive denominators d,e, let x=P_d b, z=P_e c.
The exact resolvent identity implies

    x-z = P_d(b-c) + (I-P_d) diag(d/e-1) z.              (5)

Indeed h P_d B(D_d-D_e)=(P_d-I)diag(1-d/e). A reverse identity follows by
swapping the two paths. Equation (5) directly bounds a finite denominator
change by kappa(P_d)*||z||_(1,w)*||d/e-1||_infinity plus ||b-c||.
It is invalid when the two paths have different B unless the flux difference
term is also added. Integrating (1) on a common positive path gives a second
finite-pair bound; the continuum box below uses the straight parent segment,
not an arbitrary independent corrector denominator unrelated to the predictor.

## 5. Actual three-stage dependency at frozen F0,F1

Write B0=B(F0), Bc=B((F0+F1)/2). In this partial map these are constants,
not a common B and not a shared evaluation site. Let h_g=gamma*h,
gamma=1-1/sqrt(2). The mapped stages give exactly

    yp=P0(y0)y0,  yg=Pg(y0)y0,  yc=Pc(yp)y0,
    dyp=P0 dy0+(I-P0)diag(yp)(dy0/y0),
    dyg=Pg dy0+(I-Pg)diag(yg)(dy0/y0),
    dyc=Pc dy0+(I-Pc)diag(yc)(dyp/yp).                 (6)

The last RHS is dy0, NOT dyp. The second term in the last line carries the
predictor denominator derivative. A product Pc P0 dy0 omits that dependence
and implements a different derivative. Independent Cramer's-rule dual-number
checks differentiate the complete frozen-flux stage construction, not (1).
Both values and directional derivatives are compared in exact rational
arithmetic. The irrational gamma is handled analytically in the bound;
a rational h/3 endpoint fixture is explicitly not an execution at gamma*h.

For actual state-dependent F0,F1, (6) lacks the flux terms from #74; they are
not small remainders. In particular the corrector would also have
h Pc delta_Bc D(yp) yc. This work does not evaluate or bound that term.
Thermal source dependence and branch-table jumps remain outside (6).

## 6. A complete illustrative continuum-box certificate

This box is declared for the algebraic partial map, NOT measured from the
REI canonical state or certified as an envelope of its atomic/owner rates.
Choose fixed elemental reference totals NH*,NHe*>0 and time tau*>0.
Let u_j=y_j/N_element*, f_ij=tau*F_ij/N_element*, t=h/tau*.
These are dimensionless. Normalize each parent element to sum one and impose

    u_HI,u_HII >= 1/4;   u_HeI,u_HeII,u_HeIII >= 1/6;
    each of the six f0 and six f1 edges is in [0,1/16];
    0 <= t <= 1/8.

The parent domain is a convex product of simplexes; independently specified
F0,F1 remain fixed when differentiating or comparing parents. Use
E=max(||delta_u_H||_1, ||delta_u_He||_1). Tangents and differences have zero
sum in each block. Consequently max_j |delta_u_j|<=E/2 in either block.
This factor 1/2 is not available for comparisons with differing element totals.

The largest outflux is Q=1/8 in the central HeII column. The H and other He
columns have Q<=1/16. With m0=1/6, tmax=1/8,

    t Q/m0 <= 3/32,
    kappa_p <= 6/35,
    Gp := 1+kappa_p/(2*m0) = 53/35.

For the predictor, positivity of incoming terms gives

    up_j >= u0_j/(1+t q0_j/u0_j)
          >= m0_j/(1+tmax Q0_j/m0_j).

Thus a common (loose but uniform) predictor margin is mp=16/105. This is
not an assumed minimum inferred from a sampled trajectory. It follows over
the complete box, including its zero-flux and zero-step faces.

The corrector's averaged flux has the same outgoing bounds, so

    kappa_c <= 2*(1/64)/(16/105+1/64)=210/1129,
    beta_c := kappa_c/(2*mp)=11025/18064,
    Ec <= E0+beta_c Ep <= Gc E0,
    Gc = 1+beta_c*Gp = 34759/18064.

For gamma, 0<gamma<1/3 follows from 1/2>4/9. Therefore
(t_g Q/m0)<=1/32, kappa_g<=2/33 and Gg<=13/11. This is a rational
upper enclosure for the actual irrational gamma, not a substituted tableau.

Final continuum-box bounds for the frozen-flux population map are

    Ep <= (53/35) E0,
    Eg <= (13/11) E0,
    Ec <= (34759/18064) E0.                              (7)

They apply to both admissible directional derivatives and finite pairs in
the convex parent domain. For the latter integrate the derivative along the
parent segment; every predictor along it has the proved margin mp. Bounds
hold uniformly for every fixed choice of F0,F1,t in the stated box. They are
upper bounds, not attained gains, and are not claims of nonexpansion.
Finite rational samples merely check the implementation of this proof.

## 7. Validation, limits and literature

D01-D12 cover selected inherited byte links (not a rerun of #74's 26-file
suite), solved cancellation, an independent dual/Cramer derivative, finite
pairs, weighted operator norm, rare-species cancellation, nested corrector
derivative and wrong-RHS/omitted-denominator controls, exact box constants,
box samples, finite stage pairs, zero-step/zero-flux limits and invalid inputs.
The independent derivative check is first run against an intentionally
omitted-denominator hypothesis; its real assertion failure is preserved as
MUTANT evidence, not misrepresented as a pre-existing production bug or an
implementation-absent RED. Only the new research checker runs after that.

The rational reference uses the existing #73 matrix helper without executing
its old tests. The research validation domain is a strict positive subset;
its input rejection precedence is not a reproduction of every production
error case. Complexity is cubic for the small Fraction inverse and constant
size for 2x2/3x3 Cramer blocks; arbitrary precision rational arithmetic avoids
roundoff but its bit cost grows with operands. It is not a production kernel.

SciSpace located MPRK denominator/order and stability papers. Independent
primary-source web follow-up located Torlo, Offner and Ranocha, 'Issues with
positivity-preserving Patankar-type schemes', Applied Numerical Mathematics
182 (2022), 117-147, DOI 10.1016/j.apnum.2022.07.014, arXiv:2108.07347.
Its abstract and publisher section text discuss oscillations and accuracy loss
near vanishing initial components. This is methodological context only;
we neither borrow a theorem for this checkout nor claim novelty of (1)-(7).
The formulas and explicit box certificate above are direct derivations here.

Sequential same-assistant math/code review: fixed B versus total derivative,
fixed step/weights/totals, source RHS and denominator ordering, exact-real
versus numerical implementation, gamma enclosure and synthetic-versus-physical
box are explicit. No independent reviewer or native approval is claimed.

## 8. Scientific frontier

Earned after successful execution: conditional denominator-only derivative and
finite-pair bound for the mapped stages, with exact arithmetic corroboration
and the explicit algebraic box (7). UNKNOWN remains: a trajectory-relevant
physical rate/owner envelope, total delta_F0/delta_F1 bounds, thermal coupled
inverse bounds, exact-flow defect rho, and executable production four-site ABI.

Next scientific obligation: on one explicitly selected event-free physical
state/forcing tube, bind and bound the omitted flux-numerator derivative,
including node-owner normalization. Reuse (1)-(7) for the denominator part;
do not re-derive it or replace the true physical fluxes by the illustrative
constant box. A native/CAS requirement is handed to local Codex only after
identifying the actual local-only input or executable need. No worker was
started by this document. First interval/provider and production changes
remain outside this work unit.
