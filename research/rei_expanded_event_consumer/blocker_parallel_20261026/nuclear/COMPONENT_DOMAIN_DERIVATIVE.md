# Named beta-transfer component: parameter derivatives and finite-interval domain

2026-10-26. Theory-only continuation by nuclear_blocker26. Applies to the exact affine component in CONTRACT.md and R1_R10_RESEARCH.md; frozen implementation API and tests are unchanged. No local runtime and no new symbolic-service call. Uses the already checked identities P1+kI=P0+sh, dI/dh=P1 and regular phi expansions. Independent review/admission remains the root/reviewer's responsibility.

## 1. Named component and physical units

Call this component F_beta(P0,s,lambda,kappa,h)=(P1,I,B,R). P0 and P1 are isotope number per fixed Href, s is that number per proper second, lambda and kappa are inverse proper seconds, h is proper seconds, I has isotope-number times seconds, and B,R are event numbers perHref. Inputs are finite and nonnegative. Source, lambda and kappa are constant over the component step. lambda belongs to the declared continuum beta branch; kappa contains other explicitly supplied losses. It is not inferred from missing data.

Set k=lambda+kappa and

E=exp(-kh), A=integral_0^h exp(-ku)du,
C=integral_0^h (h-u)exp(-ku)du.

Then P1=E P0+A s, I=A P0+C s, B=lambda I, R=kappa I. At k=0, A=h and C=h^2/2. These integral definitions fix continuous values and derivatives at k=0 without subtractive cancellation. They also cover h=0.

The following two additional moments are derivative quantities, not new physical closure variables:

D=integral_0^h u exp(-ku)du,
F=integral_0^h u(h-u)exp(-ku)du.

For k>0, x=kh:

D=[1-(1+x)exp(-x)]/k^2,
F=[x-2+(x+2)exp(-x)]/k^3.

For k=0, D=h^2/2 and F=h^3/6. The integrals establish D,F>=0, and dA/dk=-D, dC/dk=-F. For a future derivative implementation, small-x integral/series forms are required; the displayed quotient forms are algebraic identities, not an instruction to evaluate near zero. This note does not amend current code.

## 2. Complete analytic Jacobian

Define L=h E P0+D s and G=D P0+F s. Then

P1_k=-L, I_k=-G,
P1_h=s-kP1, I_h=P1,
L=I-kG.

The last equality follows by differentiating kI=P0+sh-P1 with respect to k. It yields I>=kG>=0 and is useful for signed derivative bounds.

Rows of the Jacobian below are (P1,I,B,R); columns are (P0,s,lambda,kappa,h):

| Output | P0 | s | lambda | kappa | h |
|---|---|---|---|---|---|
| P1 | E | A | -L | -L | s-kP1 |
| I | A | C | -G | -G | P1 |
| B | lambda A | lambda C | I-lambda G | -lambda G | lambda P1 |
| R | kappa A | kappa C | -kappa G | I-kappa G | kappa P1 |

The rate derivatives include the effect of each rate on the surviving parent and on newly injected parents. Holding I fixed when differentiating B=lambda I would omit a real feedback term. In particular,

B_lambda=L+kappa G>=0, R_kappa=L+lambda G>=0,
B_kappa=-lambda G<=0, R_lambda=-kappa G<=0.

Increasing the beta rate increases cumulative beta events, while increasing a competing loss decreases them, even though both decrease the final parent. These derivative signs are a discriminating physical check of this component.

Differentiate exact number balance to obtain independent identities:

P1_lambda+B_lambda+R_lambda=0,
P1_kappa+B_kappa+R_kappa=0,
P1_h+B_h+R_h=s,
P1_P0+B_P0+R_P0=1,
P1_s+B_s+R_s=h.

These follow by hand from the displayed Jacobian, E+kA=1 and A+kC=h. They do not require a finite-difference tolerance.

## 3. Continuous boundaries

As k approaches zero through nonnegative lambda,kappa, both rates approach zero. Write

I0=hP0+(h^2/2)s,
L0=hP0+(h^2/2)s=I0,
G0=(h^2/2)P0+(h^3/6)s.

The zero-rate Jacobian is

| Output | P0 | s | lambda | kappa | h |
|---|---|---|---|---|---|
| P1 | 1 | h | -I0 | -I0 | s |
| I | h | h^2/2 | -G0 | -G0 | P0+sh |
| B | 0 | 0 | I0 | 0 | 0 |
| R | 0 | 0 | 0 | I0 | 0 |

At h=0 with arbitrary finite rates, P1=P0 and I=B=R=0. Parameter derivatives with respect to lambda,kappa vanish; duration derivatives remain (s-kP0,P0,lambda P0,kappa P0). Source derivative of P1 is zero at h=0, and initial-parent derivative is one. The h=0 output being zero does not imply its h derivative is zero.

For checking smoothness without numerical execution:

D=h^2/2-k h^3/3+k^2 h^4/8+O(k^3 h^5),
F=h^3/6-k h^4/12+k^2 h^5/40+O(k^3 h^6).

These follow by termwise integration of exp(-ku) on a finite interval; its power series is uniformly convergent on every bounded (k,h) rectangle. Thus all derivative expressions are continuous at k=0 and h=0. Nonnegative input boundaries use the corresponding one-sided physical derivatives, with a smooth analytic extension available mathematically.

## 4. Nonnegative invariant domain and finite horizon

For continuous evolution with accumulated beta/removal/integral counters initialized to zero,

P'=s-kP, I'=P, B'=lambda P, R'=kappa P.

At P=0 the vector field is s>=0; at I=B=R=0 their derivatives are nonnegative. The nonnegative orthant is forward invariant. P+B+R=P0+st, so no beta daughter can be generated without a supplied parent or parent source.

Let 0<=P0<=Pmax, 0<=s<=Smax and 0<=t<=H. Then the following finite-time tube contains every trajectory:

0<=P<=Pmax+Smax*t,
0<=B, 0<=R, P+B+R<=Pmax+Smax*t,
0<=I<=t*Pmax+(t^2/2)*Smax.

This is a domain with an explicit clock, not a claim that a fixed bounded box remains invariant for arbitrarily long injection. The total-number barrier has derivative s-Smax<=0; the I barrier has derivative P-Pmax-Smax*t<=0. Positivity establishes its lower boundaries. No upper bound on lambda or kappa is needed for this invariant tube. Continuous time-dependent nonnegative source/rates obey the same tube when s(t)<=Smax, although the frozen-coefficient finite-step formula is then a subflow approximation rather than the exact variable-coefficient solution.

For finite H define

M=Pmax+Smax*H,
Imax=H*Pmax+(H^2/2)*Smax,
Gmax=(H^2/2)*Pmax+(H^3/6)*Smax.

The integral representation gives

0<=P1<=M, 0<=I<=Imax, 0<=B,R<=M,
0<=L<=Imax, 0<=G<=Gmax,
0<=I-lambda G<=Imax, 0<=I-kappa G<=Imax,
0<=lambda G<=Imax, 0<=kappa G<=Imax.

The event bounds B,R<=M come from number balance and remain finite in the stiff-rate limit. This is stronger than replacing B by an unbounded lambda*Imax. The derivative bound for h still requires finite rate caps: at h=0, B_h=lambda P0 can be arbitrarily large if lambda has no cap. It would be false to claim a rate-uniform duration-Lipschitz bound on a domain containing h=0 and unbounded lambda.

For fixed s,lambda,kappa,h the parent-to-(parent,beta,removal) transfer column has nonnegative entries (E,lambda A,kappa A) summing to1. Its unscaled number l1 norm is exactly1. Thus it is number-conservative and nonexpansive for a perturbation of P0 when all three destinations are retained. Dropping the R counter loses this conservation witness; assigning R to a physical daughter still needs its actual reaction owner.

## 5. Dimensionless scales and explicit Lipschitz certificate

A mixed-unit Jacobian norm is meaningless until scales are fixed. Choose one fixed positive abundance/count scale P_* and one fixed positive proper-time scale t_* for this component. These are reporting/conditioning scales, not changed physical tolerances. Define dimensionless inputs

z=(p0,sigma,alpha,beta,eta)
 =(P0/P_*, s*t_*/P_*, lambda*t_*, kappa*t_*, h/t_*),

and outputs

w=(p1,j,b,r)=(P1/P_*, I/(P_* t_*), B/P_*, R/P_*).

The formulas in Sections1-3 retain exactly their form after this rescaling, with a=A/t_*, c=C/t_*^2, ell=L/(P_* t_*), g=G/(P_* t_*^2), and kbar=alpha+beta. In particular the dimensionless Jacobian is

[[E,a,-ell,-ell,sigma-kbar*p1],
 [a,c,-g,-g,p1],
 [alpha*a,alpha*c,j-alpha*g,-alpha*g,alpha*p1],
 [beta*a,beta*c,-beta*g,j-beta*g,beta*p1]].

Freeze a convex dimensionless box

0<=p0<=pbar, 0<=sigma<=sbar, 0<=alpha<=abar,
0<=beta<=bbar, 0<=eta<=Hbar,

with finite stated upper bounds. Define

m=pbar+sbar*Hbar,
i=Hbar*pbar+(Hbar^2/2)*sbar,
gbar=(Hbar^2/2)*pbar+(Hbar^3/6)*sbar.

Four valid absolute row-sum bounds are

L_P=1+Hbar+2*i+sbar+(abar+bbar)*m,
L_I=Hbar+Hbar^2/2+2*gbar+m,
L_B=min(1,abar*Hbar)+min(Hbar,abar*Hbar^2/2)+2*i+abar*m,
L_R=min(1,bbar*Hbar)+min(Hbar,bbar*Hbar^2/2)+2*i+bbar*m.

Derivation: E<=1, a<=Hbar, c<=Hbar^2/2; absolute rate derivatives of P1,B,R are bounded by i, those of j by gbar. Also alpha*a<=1 and alpha*c<=eta from kbar*a=1-E and kbar*c=eta-a; the analogous beta bounds hold. Duration derivatives use |sigma-kbar*p1|<=sbar+(abar+bbar)*m, j_eta=p1<=m, b_eta<=abar*m and r_eta<=bbar*m.

Consequently L_F=max(L_P,L_I,L_B,L_R) is a concrete finite bound on ||D_z F_beta||_infinity throughout this box, and the fundamental theorem of calculus on its line segments gives

||F_beta(z)-F_beta(z_tilde)||_infinity <= L_F ||z-z_tilde||_infinity.

This is an analytic component certificate with named inputs and explicit constants, not a numerical claim that the full REI client stays in that box. More refined row-specific error bounds follow directly from the displayed Jacobian and input uncertainty components. An interval for lambda or source can therefore be propagated without an IVP. Values for P_*,t_*,pbar,sbar,abar,bbar,Hbar must come from the selected physical consumer; this report does not invent them.

## 6. Reference, proper clock and parameter variations

For a fixed reference number Nref, abundance Y=N/Nref and normalized source s=S_N/Nref. If reference normalization itself varies across configurations,

delta Y=delta N/Nref - Y*delta ln Nref,
delta s=delta S_N/Nref - s*delta ln Nref.

These terms must be included in the input pullback; changing Nref while holding normalized P0,s fixed changes the physical problem. P_* and t_* are held fixed when taking the scaled Jacobian above. If they also vary across configurations, their normalization derivatives must be included or the comparison must first be expressed in common fixed scales.

For physical density n and a reference density nref under expansion theta, let n_dot+theta*n=S_phys-k*n. Then Y=n/nref obeys

Y_dot=S_phys/nref-kY-Y*(theta+nref_dot/nref).

The affine abundance component applies directly only when nref obeys nref_dot+theta*nref=0, or when the extra reference/dilution term is explicitly modeled. It is not automatically a nonnegative destruction rate: the sign depends on the chosen reference. Do not silently absorb it into kappa.

For a parent of Lorentz factor gamma relative to the evolved time coordinate, lambda=lambda_rest/gamma and

delta lambda=delta lambda_rest/gamma-lambda_rest*delta gamma/gamma^2.

A broad energy/direction distribution needs the corresponding resolved population or weighted operator; a single effective gamma is an extra closure. For logarithmic scale-factor time eta_cos with dt/deta_cos=1/H_cos, the component duration is h=integral deta_cos/H_cos. With fixed integration endpoints,

delta h=-integral delta H_cos/H_cos^2 deta_cos.

Variable endpoints contribute +(delta eta_end)/H_end-(delta eta_start)/H_start. These are clock pullback terms, not new beta dynamics. To bound them uniformly requires a positive H_cos lower bound and a bound on delta H_cos over the chosen domain. Simply replacing proper h by delta eta_cos changes units and decay probability.

## 7. Actual input supplied to V6/V8/H5, and missing full-client piece

The named component now supplies: an explicit nonnegative finite-time tube; exact derivatives in state/source/rates/duration; continuous zero-rate and zero-duration limits; a dimensionless finite-box Jacobian norm; and a number-conservative parent transfer column. These are usable local inputs for an existing history/domain argument without repeating its generic theorem.

For an actual client input map z=z(y,theta), the component pullback is

D_y(F_beta composed with z)=D_z F_beta * D_y z,

with analogous parameter derivative. A bound ||D_y z||<=L_z in the same chosen scales gives the named contribution <=L_F*L_z. This chain rule includes source, rate, clock and normalization feedback; the present component certificate alone does not bound L_z.

A physical coupled-state injection can be written

y_new=y+e_parent*s*h+nu_beta*B+nu_comp*R,

where each reaction incidence vector includes parent consumption and the appropriate products. Then its derivative contains the identity, source-duration derivatives, nu_beta*DB and nu_comp*DR, plus any derivatives of a state-dependent branch/embedding. Using P1 as a separate replacement while also applying parent consumption in nu_beta/nu_comp would double-count removal. The current scalar API merely returns counters; this formula explains a future named consumer's required assembly.

The exact remaining full-client obligations are:

1. A selected component input map with bounded source/rate derivatives, finite rate/source caps, common scales and explicit parameter normalization. The CR flux/source, density and thermal/atomic derivatives are not supplied by decay algebra.
2. Named reaction/charge-state products for every competing loss and beta branch, with one electron owner; actual energy/spectrum/stopping maps for energy outputs. The current four-output count component has no thermal-energy Jacobian.
3. A full-client reachable domain that simultaneously controls the other species, temperature, radiation/CR spectra and metric/clock variables, including positive reference-density and H_cos bounds where they enter denominators.
4. Bounds and numerical error evidence for coupling/composition with the other component maps, source quadrature, interpolation and event transitions; frozen-source exactness does not establish exactness of the nonlinear coupled step.

These are specific missing maps/bounds, not a claim that no domain exists. The existing canonical nodes keep their current admission state. No node is added and no14-node group is marked complete by this component proof. Next action is to select the actual client's z-map and insert these explicit derivatives/bounds into its existing V6/V8/H5 calculation; the original beta implementation/testing contract stays unchanged.
