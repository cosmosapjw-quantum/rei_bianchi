# Exact block structure of the isotope-native atomic kernel

Date: 2026-10-22. This is the local theoretical construction after the
completed C2 mapping, within the executable unit in `EXECUTION_CONTRACT.md`.
This note derives an exact simplification of the
existing conditional atomic number operator. It retains all 21 abundances and
does not introduce a nuclear charge branch, thermalization law or energy
closure. The arguments are algebraic proofs; no new finite test or trajectory
is claimed here.

## 1. Source and assumptions

The starting scientific contract is
`research/rei_coupled_isotope_mapping_20261022/RESUME.md` and `THEORY.md`,
especially the latter's sections 5–6. The actual source read is
`research/rei_coupled_isotope_mapping_20261022/vendor/donor_atomic/code/atomic_network.py`.
Its C2 `SOURCE_IDENTITY.json` records donor commit
`8be7533cc97b3302bf42608699d6e8313ed6af8a`, original repository path
`research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/code/atomic_network.py`,
and SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`.
`AtomicNetwork.__init__` (L75), `_transition_matrix` (L226), `rates` (L233)
and `evaluate` (L265) supply the state ordering and matrices used below.

The assumptions of this local construction are explicit:

1. `Y_i=n_i/n_B` are absolute abundances per conserved baryon. The 21 states
   are n; H1 I/II; D I/II; T I/II; He3 I/II/III; He4 I/II/III;
   Li6 I/II/III/IV; Li7 I/II/III/IV, in the C2 order. A and q denote the
   mass-number and positive ionic-charge vectors. Physical states satisfy
   `Y>=0`, `A^T Y=1`; exact zero components are allowed.
2. All free electrons in this local fixture belong to the thermal pool, so
   `n_e=n_B q^T Y`. There are no positrons or negative ions in the retained
   model. `n_B>=0` is a fixed input during a local abundance linearization.
3. T and the prescribed UV field are fixed inputs during that linearization.
   At different times their supplied values may change. Photo coefficients
   Gamma are nonnegative [s^-1], and total RR+DR coefficients alpha are
   nonnegative [m^3/s], within their declared input domains. Individual signed
   DR fit amplitudes are not separate event probabilities.
4. The inherited electronic-equality rule is retained: coefficients depend
   on `(Z,q)` and are shared by H1/D/T, He3/He4 and Li6/Li7. Equal charge
   fractions or equal isotope inventories are **not** assumed.
5. The local atomic operator includes the donor photo/RR/DR terms and omits
   its returned beta matrix D. The separately specified nuclear event layer
   owns beta once, as required by C1/C2. Nuclear and energy sources are not
   silently included in an atomic Jacobian.

The geometry convention remains non-tilted LRS with signature (-,+,+,+),
isotropic thermal baryonic `pi_b=0`, nonbaryonic `pi_m`, and separate
`pi_r=pi_gamma+pi_nu`. This fixed-input number-kernel simplification changes
none of those component definitions.

## 2. Edge fluxes give a conservative sparse operator

For isotope a of nuclear charge Z, write its charge populations as
`y_a=(Y_a0,...,Y_aZ)^T`. On edge j between charges j and j+1, let

\[
g_{Zj}=\Gamma_{Zj},\qquad
\alpha_{Z,j+1}=\alpha^{\rm RR}_{Z,j+1}+\alpha^{\rm DR}_{Z,j+1},
\qquad r_{Z,j+1}=n_e\alpha_{Z,j+1}.
\]

Define `r_Z0=0`, `g_ZZ=0` at the two charge boundaries. The signed net upward
edge flux, in events per conserved baryon per second, is

\[
f_{aj}=g_{Zj}Y_{aj}-n_e\alpha_{Z,j+1}Y_{a,j+1}.
\]

Equivalently, keep its three nonnegative physical contributions separately:
photo `g Y_lower`, RR `n_e alpha_RR Y_upper`, and DR
`n_e alpha_DR Y_upper`. Add `-f_aj` to the lower state and `+f_aj` to the
upper state. Thus

\[
\dot Y_{a0}=-f_{a0},\quad
\dot Y_{aj}=f_{a,j-1}-f_{aj}\ (0<j<Z),\quad
\dot Y_{aZ}=f_{a,Z-1}.
\]

There are `3*1+2*2+2*3=13` isotope charge edges. If E is the 21-by-13
incidence matrix with column `e_upper-e_lower`, then

\[
F_{\rm atom}=E\{\phi^{\rm PI}-\phi^{\rm RR}-\phi^{\rm DR}\}.
\]

This avoids constructing a dense matrix for an RHS evaluation. Its correctness
does not depend on equilibrium, a small step or isotope proportionality.
Since both endpoints of each edge are the same isotope,

\[
\ell_a^TE=0,\quad A^TE=0,\quad q^TE=\mathbf1^T,
\]

where `ell_a` selects all charge states of isotope a. Therefore every isotope
total, and consequently baryon number, is conserved by this atomic operator;
the free-electron source is exactly the sum of signed upward edge fluxes:

\[
\ell_a^TF_{\rm atom}=0,\quad A^TF_{\rm atom}=0,
\qquad \dot Y_e=q^TF_{\rm atom}=\sum_{a,j}f_{aj}.
\]

At a component boundary `Y_i=0`, every loss term from that component vanishes
and its gains are nonnegative for a physical state. Hence this continuous
atomic vector field preserves the nonnegative orthant. This statement is
about the ODE; it does not assert that every Newton iterate or time integrator
preserves positivity.

## 3. Three shared charge blocks, without identifying isotopes

For a given instantaneous n_e, each isotope has a column-conservative
birth/death generator B_Z. Its nonzero entries are

\[
(B_Z)_{j,j}=-(g_{Zj}+r_{Zj}),\quad
(B_Z)_{j+1,j}=g_{Zj},\quad
(B_Z)_{j-1,j}=r_{Zj}.
\]

Suppressing the Z label, the three distinct matrices are

\[
B_1=\begin{pmatrix}-g_0&r_1\\g_0&-r_1\end{pmatrix},
\]

\[
B_2=\begin{pmatrix}
-g_0&r_1&0\\
g_0&-(r_1+g_1)&r_2\\
0&g_1&-r_2
\end{pmatrix},\qquad
B_3=\begin{pmatrix}
-g_0&r_1&0&0\\
g_0&-(r_1+g_1)&r_2&0\\
0&g_1&-(r_2+g_2)&r_3\\
0&0&g_2&-r_3
\end{pmatrix}.
\]

The full frozen-electron matrix is exactly

\[
B=\operatorname{diag}(0,B_1,B_1,B_1,B_2,B_2,B_3,B_3)
  =G_0+n_eG_{ne},\qquad G_{ne}=G_{rr}+G_{dr}.
\]

The leading neutron block is zero in B and identity in `I-hB`. Each H block
is shared by three independently stored isotope vectors; each He and Li
block is shared by two. Factorization sharing is valid even when all their
charge fractions differ, or one isotope is absent. It reduces repeated
arithmetic; it does not replace the 21-dimensional state by common fractions.

The block structure is exact for the donor's current adjacent-charge,
electronic-equality coefficients. Rates and UV energy moments retain their
existing source identities; no VF/Badnell coefficient substitution is involved.

## 4. The abundance Jacobian is one rank-one update

Because only the common electron density depends on Y at fixed T, UV and
n_B, an arbitrary perturbation v gives

\[
\begin{aligned}
\delta F_{\rm atom}
 &=Bv+(G_{ne}Y)\,\delta n_e,\\
\delta n_e&=n_Bq^Tv.
\end{aligned}
\]

Consequently

\[
\boxed{J=B+u q^T,\qquad u=n_B G_{ne}Y.}
\]

Both B and u have the appropriate s^-1 factor because Y and q are
dimensionless. The Jacobian action can be evaluated without forming J:

\[
Jv=Bv+u(q^Tv).
\]

The same edge assembly computes `G_ne Y` by using only downward coefficient
fluxes `alpha Y_upper`, before multiplying by n_e or n_B. Applying an RR
energy factor to the summed G_ne would still be incorrect: the number-operator
compression does not merge the separate RR and DR energy meanings.

For any atomic invariant `ell_a` or A, `ell^T B=0` and `ell^T u=0`, hence
`ell^T J=0`. If `(I-hJ) z=b` is solved exactly, it follows that
`ell^T z=ell^T b`. A numerical implementation can preserve the paired edge
updates and inspect residuals; post-step abundance renormalization is not part
of this derivation.

## 5. Exact implicit solve by shared blocks and Sherman–Morrison

Let h be the nonnegative effective implicit coefficient in seconds, such as
an implicit time-method coefficient times its step. Define

\[
M=I-hB,\qquad K=I-hJ=M-hu q^T.
\]

At one fixed linearization, factor only
`M_1=I_2-hB_1`, `M_2=I_3-hB_2`, and `M_3=I_4-hB_3` and reuse each factor
for its isotope blocks. The neutron solve is the scalar identity. Given b,
compute

\[
a=M^{-1}b,\qquad v=M^{-1}u,\qquad d=1-hq^Tv.
\]

Whenever M is invertible and d is nonzero,

\[
\boxed{K^{-1}b=a+\frac{h\,v\,(q^Ta)}{d}.}
\]

Direct substitution proves it: `Ma=b`, `Mv=u`, and the coefficient of u
in `K[a+c v]` is `c-h q^Ta-hc q^Tv`; choosing
`c=h(q^Ta)/d` sets that coefficient to zero. Also

\[
\det K=\det M\,d.
\]

The same factors and v serve multiple RHS columns at the same state, h and
external inputs. At a different Newton state n_e changes, and at different
h or T the blocks generally change; cached factors cannot be reused as exact
factors across those changes. No dense inverse is needed.

### 5.1 The base blocks cannot be singular on a physical state

For h>=0 and nonnegative g,r, the diagonal entry of M in column j is
`1+h(g_j+r_j)`, and the sum of off-diagonal absolute values is
`h(g_j+r_j)`. The column diagonal-dominance margin is exactly one.
Writing M as a positive diagonal minus a nonnegative off-diagonal matrix
gives a convergent Neumann series after diagonal scaling: each scaled
off-diagonal column sum is strictly less than one. Thus M is invertible and
`M^-1>=0`. Since `1^T B_Z=0`,

\[
\mathbf1^TM_Z^{-1}=\mathbf1^T,\qquad \|M_Z^{-1}\|_1=1.
\]

In particular, a frozen-electron backward-Euler block step maps a nonnegative
input to a nonnegative state with the same isotope total. That property of
the frozen block step is not a positivity claim for the full nonlinear Newton
iteration.

### 5.2 Stronger denominator result: d>=1 for physical Y

A small-denominator singularity is absent for the specified physical atomic
kernel. This requires a proof because u has both signs; treating J as a
positive Markov generator would be incorrect.

For one element, let `c=(0,1,...,Z)^T` and solve the adjoint block

\[
w=M_Z^{-T}c.
\]

Define adjacent differences `delta_j=w_(j+1)-w_j` for `0<=j<Z`. The j-th
adjoint equation is

\[
w_j-h[g_j(w_{j+1}-w_j)+r_j(w_{j-1}-w_j)]=j.
\]

Subtracting the equation at j from the one at j+1 gives

\[
[1+h(g_j+r_{j+1})]\delta_j
 -h r_j\delta_{j-1}-h g_{j+1}\delta_{j+1}=1,
\tag{*}
\]

with missing boundary terms omitted (`r_0=g_Z=0`). The matrix in (*) has
positive diagonal, nonpositive off diagonal, and strictly positive column
diagonal-dominance margin. Interior column margins are one; boundary columns
have additional nonnegative endpoint terms. The same Neumann-series
argument shows its inverse is nonnegative, and its positive diagonal
contribution acting on the all-ones RHS makes every `delta_j>0`.

Now `G_ne` is the downward edge generator. Summing over isotopes,

\[
q^TM^{-1}u
 =n_B w^TG_{ne}Y
 =-n_B\sum_{a,j}\alpha_{Z,j+1}Y_{a,j+1}\delta_{Zj}\le0.
\]

Therefore

\[
\boxed{d=1+h n_B\sum_{a,j}
\alpha_{Z,j+1}Y_{a,j+1}\delta_{Zj}\ge1.}
\]

It equals one when the relevant correction vanishes, for example h=0,
n_B=0 or no occupied recombining states. This proof uses no equilibrium
assumption and permits exact zero isotope inventories. The same delta_Z
can be shared by isotopes of one element. Equation (*) also supplies a
nonnegative-sum representation of d if a numerical implementation needs to
diagnose cancellation in the adjoint differences; computing it is an optional
algebraic route, not a new physical provider.

The result proves nonsingularity for the physical local problem; it is not a
bound on every floating-point forward error or the condition number of the
full matrix. Very different rate scales, extreme h and poor abundance scaling
still require a residual-based numerical decision.

### 5.3 Signed trials and a genuine fallback boundary

The donor allows finite signed Newton trial populations without clipping.
Such a trial can give a negative n_e; even when n_e remains nonnegative,
negative Y can reverse the sign of the sum above. The d>=1 proof therefore
does not apply to a general signed trial. The Sherman–Morrison identity
itself remains exact whenever M is invertible and d!=0.

A bounded implementation can try the shared-block formula and use a pivoted
dense solve of the **same** 21-by-21 K when block factorization, a denominator
conditioning check or the linear residual fails its frozen numerical criterion.
One useful dimensionless cancellation indicator is

\[
\kappa_d=\frac{1+|h|\sum_i|q_i v_i|}{|1-hq^Tv|}.
\]

The actual residual is formed from the original equation,
`r=b-z+h[Bz+u(q^Tz)]`, preferably with the same edge action used for the
operator. A componentwise scale is

\[
s_i=|b_i|+|z_i|+|h|\sum_j|B_{ij}||z_j|
          +|h||u_i|\sum_j|q_j||z_j|.
\]

`|r_i|/s_i` is interpreted as zero for an exactly zero numerator and scale;
the implementation contract must define its floating-point floor/tolerance.
No tolerance is inferred from a physical conservation identity.

If M is invertible but d is mathematically zero, K is singular: a dense
fallback cannot cure that singularity. It must return the linear-solve failure
to the declared step/linearization policy. If M alone fails but K is
nonsingular, a dense solve can still succeed. Neither path clips a trial,
changes a physical rate, inserts an abundance floor or silently drops the
electron derivative.

## 6. Autonomous exponential midpoint: order and invariant properties

For the selected atomic-only stepper, T, UV and n_B are fixed and f=0, so
`F(Y)=B(Y)Y` is a smooth autonomous vector field. Use

\[
Y_{1/2}=\exp\!\left[\frac h2 B(Y)\right]Y,\qquad
Y_{\rm new}=\exp\!\left[hB(Y_{1/2})\right]Y.
\]

The second exponential acts on the original Y, not on `Y_(1/2)`. This is
the exponential midpoint in Blanes, Iserles and Macnamara,
[*Positivity-preserving methods for ordinary differential equations*, §3.3,
equation (3.8)](https://arxiv.org/html/2102.08242v2). `SOURCES.md` records
the primary-source intake. The derivation below applies that existing method
to these isotope blocks; there is no novelty claim for the integrator.

Because B is affine in Y through n_e,

\[
Y_{1/2}=Y+\frac h2 F(Y)+O(h^2),\qquad
B(Y_{1/2})=B(Y)+\frac h2 n_B(q^TF)G_{ne}+O(h^2).
\]

Expansion of the second exponential therefore gives

\[
\begin{aligned}
Y_{\rm new}
 &=Y+hF+\frac{h^2}{2}
   \{BF+n_B(G_{ne}Y)(q^TF)\}+O(h^3)\\
 &=Y+hF+\frac{h^2}{2}JF+O(h^3).
\end{aligned}
\]

This matches the autonomous exact-flow Taylor expansion through h^2. The
one-step local defect is O(h^3), yielding global order two on a fixed finite
interval under the usual smoothness and stability conditions. Here F is a
finite quadratic polynomial for fixed admissible coefficients; its derivatives
are bounded on the conserved physical abundance simplex. This is not a
uniform finite-step accuracy estimate for arbitrary stiff rates.

For any frozen physical state, B has nonnegative off-diagonal entries.
Choose lambda at least its largest outgoing rate. Then `B+lambda I>=0`, and

\[
e^{tB}=e^{-\lambda t}\sum_{m=0}^{\infty}
\frac{t^m(B+\lambda I)^m}{m!}\ge0\quad (t\ge0).
\]

Also `ell_a^T exp(tB)=ell_a^T` because `ell_a^T B=0`. Thus the first stage
preserves nonnegativity and every isotope total. Its electron density remains
nonnegative, so the same argument applies to the second stage. Both stages
preserve `A^T Y` in exact arithmetic for any h>=0. No clipping, abundance
floor or post-step renormalization is needed in the mathematical method.

At each stage only the three 2-by-2, 3-by-3 and 4-by-4 exponentials are
distinct; each acts on its isotope columns, with the neutron identity
unchanged. These exponential actions do not require the Newton solve in
section 5; that solve is a separately reusable implicit-kernel component.
Finite-precision exponential evaluation and timestep accuracy still require
the independent numerical comparisons in the execution contract.

An initially absent isotope remains absent under this atomic-only method,
as the atomic equations require. Positive nuclear/event onset is a separate
source operation. The proof does not establish second order or positivity
for an unspecified combination with nuclear sources, evolving T, photons or
fast-electron kinetics. Time-dependent external inputs would likewise require
their own time-stage treatment.

## 7. Exact zero and fixed positive scaling at source onset

Suppose an isotope has zero initial inventory and a supplied charge-resolved
source S(t,Y) first gives `S_i(t0,Y0)>0`. Because its atomic block vanishes
on the zero isotope vector, a smooth local solution satisfies

\[
Y_i(t_0+\Delta t)=S_i(t_0,Y_0)\Delta t+O(\Delta t^2).
\]

There is no singularity in the absolute-abundance ODE. This statement is
conditional on an actually supplied source; it does not assert a particular
nuclear branch or stopping law. Generic prescribed negative losses would
need their own availability condition to preserve positivity.

For supplied unary/binary mass-action events the source derivatives are also
regular at zero. With `m=sum_i a_i`, `sigma=product_i a_i!` and
`R=k n_B^(m-1) product_i Y_i^a_i/sigma`, use the polynomial derivative

\[
\partial_{Y_l}R=
\frac{k n_B^{m-1}}{\sigma}\,a_lY_l^{a_l-1}
\prod_{i\ne l}Y_i^{a_i}\quad(a_l>0),
\]

and zero when a_l=0. Zero powers have their polynomial value one, including
at a zero component. Do not compute `R*a_l/Y_l` at zero. For unequal
reactants `R=k n_B Y_i Y_j`, for example, `partial_i R=k n_B Y_j` can be
nonzero at `Y_i=0` even though R itself vanishes. For identical binary
reactants `R=k n_B Y_i^2/2`, the derivative is `k n_B Y_i`. This preserves
both the factorial symmetry and the correct linear response at source onset.

Choose a **fixed positive** numerical scale s_a for each isotope, common to
all its charge states, and let `S=diag(s_i)`, `z=S^-1 Y`. The scale for an
initially absent isotope cannot be its zero initial inventory. It may be an
explicit numerical reference chosen for the finite problem. Then

\[
\dot z=S^{-1}F(Sz),\quad
z_i(t_0)=0,\quad
\dot z_i(t_0)=S_i^{\rm source}(t_0,Y_0)/s_i.
\]

Zero is exactly representable, and the newly positive stock is represented
without a seed abundance. Since S is a scalar multiple of the identity within
each isotope block, it commutes with B:

\[
J_z=S^{-1}JS=B+u_z q_z^T,
\qquad u_z=S^{-1}u,\quad q_z=S q.
\]

The same three base blocks can therefore be factored in scaled coordinates.
The Sherman–Morrison denominator is unchanged by this similarity transform.
The conserved abundance covectors become `ell^T S` and `A^T S`, while
`n_e=n_B q_z^T z`. Different charge-dependent scales remain mathematically
possible but generally change the per-isotope base blocks and their shared
factorization; an adaptive/time-dependent scale also introduces
`-S^-1 dot S z` and cannot be treated as this fixed transform.

Scaling determines numerical resolution, not the physical inventory. A scaled
absolute tolerance `atol_z,i` means physical tolerance
`atol_Y,i=s_i atol_z,i`. Relative accuracy in a tiny positive stock therefore
requires an adequately small physical absolute-error budget. The inherited
`1e-20` n/T scale alone is not an accuracy proof. A representable source or
stock may still be lost through underflow, cancellation or a tolerance too
large for the requested observable. Separate signed/log source diagnostics
can retain information beyond a chosen linear-state range; that is a numerical
representation extension, not a reason to manufacture nonzero initial Y.

### Why a log-only state is not a regular zero-onset coordinate

For `ell_i=ln Y_i`, exact zero is not a finite initial value. After a linear
positive onset,

\[
\dot\ell_i=\frac{\dot Y_i}{Y_i}\sim\frac1{t-t_0}.
\]

Thus an ordinary finite-dimensional ODE in finite log coordinates cannot
start at the exact zero boundary using this transform alone. Starting from
`Y_i=epsilon` changes the specified initial condition; it may also change
charge and baryon normalization. This is not a general prohibition on log
methods: a declared analytic onset rule, linear/log hybrid or event-triggered
coordinate change can be designed later. The minimal regular local state is
absolute Y with fixed positive scaling.

### Why the old fixed isotope lift cannot represent the source

The old compact chemistry lift P fixes n/T slots to zero. Its tangent image
therefore contains no nonzero velocity in those slots. If a new event has
positive source there, `F(Pv)` is outside `image(P)`, so no reduced derivative
can satisfy `P dot v=F(Pv)`. This is an exact obstruction to that particular
lift, without requiring a numerical counterexample.

Even after an isotope is populated, equal electronic rates do not by
themselves force equal isotope fractions. For `Y_a>0`,

\[
\dot f_{aq}=(B_Z f_a)_q+
\frac{S_{aq}-f_{aq}S_a}{Y_a},\qquad S_a=\sum_q S_{aq}.
\]

Shared fractions require compatible normalized injection terms. At `Y_a=0`
this fraction formula is undefined, while the 21 absolute equations remain
regular. Shared **matrix factors** avoid the fixed-lift obstruction because
the isotope state vectors and their source directions stay independent.

## 8. Scope under additional nuclear and thermal couplings

An externally supplied event replay S(t) independent of Y changes the RHS but
not this atomic abundance Jacobian. For state-dependent resolved events,

\[
F_{\rm total}=F_{\rm atom}+\sum_j\nu_jR_j(Y,T,\ldots),\qquad
J_{\rm total}=J_{\rm atom}+\sum_j\nu_j(\nabla_Y R_j)^T.
\]

These terms preserve `A^T J_total=0` when every event satisfies `A^T nu_j=0`,
but they generally do not preserve isotope totals or the three shared
atomic base blocks. A supplied unary beta branch has the exact rank-one
contribution `lambda nu e_parent^T`. A specified small event set may admit a
Woodbury extension; a general nuclear network needs its actual derivative
and an appropriate full solve. The atomic block solver remains a useful
component/preconditioner, not an exact substitute for omitted nuclear terms.
No d>=1 statement for the augmented problem follows from the atomic proof.

With T as an independent evolving variable, the fixed-T abundance block is
still the J above, but the full Jacobian includes
`F_T=(partial_T G0+n_e partial_T Gne)Y` and the actual thermal-equation
derivatives. If T instead depends algebraically on Y, its chain-rule term
must be included. Dynamic photons, density feedback, target-state kinetics,
charge exchange or charge-dependent nuclear availability likewise add their
actual dependencies. A bordered/low-rank treatment may be possible after
those equations are supplied; it is not licensed by treating their inputs as
fixed without stating that approximation.

The execution contract also permits an independently supplied scalar
`f=Y_e,fast`, with `0<=f<=q^T Y`. At fixed f, T, UV and n_B, set

\[
e=n_B(q^TY-f),\qquad B=G_0+eG_{ne},\qquad u=n_BG_{ne}Y.
\]

Then the exact partial Jacobian and fast-electron column are

\[
J_{YY}=B+u q^T,\qquad J_{Yf}=-u.
\]

The q-based partial does not require f=0 when f is held independent. Its
base-block/denominator proof still applies at a physical point with Y>=0
and e>=0, because those are the signs used in section 5. It does not prove
nonsingularity of the full Y/f/thermal Jacobian or provide an equation for
f. The selected atomic-only midpoint stepper remains f=0; no fast-electron
stopping or escape law is inferred from this local source extension.

With all nuclei thermal, the supplied fast-electron scalar gives
`C_th=(1+q)^T Y-f` and `dot C_th=(1+q)^T dot Y-dot f`. Hence

\[
\dot T=-2HT+
\frac{2Q_{\rm per\ baryon}/(3k_B)-T\dot C_{\rm th}}{C_{\rm th}}.
\]

Here Q is an explicitly supplied translational source [J/baryon/s] and
`C_th>0`; omitted energy channels are not silently zero. More general
thermal-electron closures require
`(G_ne Y)(grad_Y n_e,thermal)^T` and their other dependencies. Number-operator
factorization supplies no missing energy partition or equilibration rate.

Finally, all equations here use proper seconds. At a fixed outer H, the
abundance block in x=ln(a/a_ref) is divided by H once; the effective local
implicit coefficient is correspondingly h_x/H. A fully coupled geometry
Jacobian also differentiates H and includes its cross blocks. The algebra
does not replace that outer coupling or authorize another H division.

## 9. Optional log-linear coefficient interpolation has an explicit bound

The saved three-knot nuclear fixture is `KNOT_ONLY` by default. For an
explicitly supplied positive coefficient on an interval, let `x=ln T`,
`g(x)=ln k(T)`, and L be the linear interpolant between x0 and x1. If a
source actually supplies `|g''(x)|<=M` throughout that interval, the
interpolation remainder is

\[
g(x)-L(x)=\frac{g''(\xi)}2(x-x_0)(x-x_1),\qquad
|g-L|\le\frac{M(x_1-x_0)^2}{8}=:\varepsilon.
\]

For `k_hat=exp L` this yields the relative coefficient bound

\[
\left|\frac{\widehat k}{k}-1\right|
 \le e^{\varepsilon}-1=\operatorname{expm1}(\varepsilon).
\]

It is a bound conditional on the supplied curvature, not a way to estimate
curvature from three saved samples. It admits off-grid use only when the
bound meets the independently fixed requested tolerance. It provides no
extrapolation guarantee. A structural-zero interval can be represented as
zero only when that whole interval is explicitly declared zero. Absent,
zero and positive statuses cannot be joined by taking a logarithm or by
silently replacing a nonfinite log entry. The result bounds a rate coefficient,
not the error of a full nonlinear trajectory or an unprovided physical model.

## 10. Constructive implementation consequence

The next bounded implementation can keep the inherited rates as input, store
all 21 absolute/scaled abundances, assemble 13 paired edge fluxes, and apply the
positive second-order atomic-only exponential midpoint with three shared
small exponentials per stage. Its implicit-kernel component evaluates
`Jv=Bv+u(q^Tv)` and solves local linear systems using three shared small
factorizations plus one scalar correction. A dense 21-state solve is a direct
fallback for the same equation where the structured numerical route is not
adequate. The physical-state denominator has the proven bound d>=1; signed
trials and additional dependencies retain explicit applicability limits.
These are exact structural reductions of the chosen kernel, with no empirical
accuracy, runtime speedup, full coupled closure or trajectory claim attached.
