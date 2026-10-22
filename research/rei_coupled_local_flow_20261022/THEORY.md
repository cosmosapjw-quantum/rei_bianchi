# Two finite local coupled flows with supplied hydrogen inputs

Derivation date: 2026-10-22 (Asia/Seoul). This document derives the models and
reference solutions; it contains no new integration results, timing claims or empirical accuracy
claims. The existing 156-check baseline and two onset checks are reused without
rerunning them. Input provenance, exact repository pins and the limitations of
the saved providers are recorded in [SOURCE_INTAKE.md](SOURCE_INTAKE.md).

The two cases answer complementary questions. Case 1 couples composition to
temperature using an available number coefficient and its own conditional
thermal moment. Case 2 couples a supplied nuclear decay to atomic recombination
at prescribed temperature. The latter does not need an invented beta heating
partition. Both are finite, explicitly specified restricted models in the
retained charge-state coordinates; no generic reaction framework is introduced
here.

## 1. Shared conventions and input boundary

Abundances are numbers per baryon. The baryon density `nB` is fixed and has
units m^-3, the expansion rate is zero, and the external photon field is zero.
Hydrogen recombination is the donor's Verner–Ferland rate, evaluated on the
public 100–10000 K interval of the restored provider. All nonparticipating
species are zero. Emitted Case-A recombination photons escape.

The retained charge slots are neutron 0, H I 1 and H II 2. Charge neutrality
sets the free-electron abundance equal to the H II abundance in these cases.
The electron abundance is therefore used once in the recombination flux; it
is not an additional independently prescribed factor.

The hydrogen scalar coefficient is

\[
 \alpha(T)=\frac{10^{-6}A_{\rm VF}}
 {u(1+u)^{1-b}(1+v)^{1+b}},\qquad
 u=\sqrt{T/T_0},\quad v=\sqrt{T/T_1},
\]

where the donor inputs are

\[
 A_{\rm VF}=7.982\,10^{-11}\ {\rm cm^3\,s^{-1}},\quad
 b=0.748,\quad T_0=3.148\ {\rm K},\quad T_1=703600\ {\rm K}.
\]

The factor `10^-6` converts the numerical coefficient from cm^3/s to m^3/s.
The hydrogen stored ionization energy is the donor value
`chi_H = 13.6 eV` converted to joules. Define

\[
 \kappa(T)=n_B\alpha(T),\qquad
 D(T)=\frac{d\ln\alpha}{d\ln T}.
\]

Thus `kappa` has units s^-1 and `D` is dimensionless. Boltzmann's constant is
kept explicit. The supplied kinetic energy coefficient is

\[
 \Lambda_{\rm RR}(T)=k_BT\alpha(T)\left(\frac32+D(T)\right)
       \quad [{\rm J\,m^3\,s^{-1}}].                 \tag{1}
\]

This is the provider's derivative-of-its-own-fit moment, with its Maxwellian
and fixed-target assumptions. Attaching a different rate's derivative to this
number rate would change the model. Equation (1) is a conditional closure of
this fit, not a new measurement of the accuracy of a physical cooling function.
The H selection has no DR channel requiring an absent DR thermal moment.

## 2. Case 1: pure-hydrogen recombination with evolving temperature

### 2.1 State, event rate and the energy balance

Let `x = Y_HII`, so `Y_HI = 1-x` and `Y_e = x`. Assume initially

\[
 0<x_i\leq1,\qquad T_i>0,\qquad n_B>0.
\]

The nuclei, neutral atoms and thermal electrons have a common, nonrelativistic
Maxwellian temperature. Neutral products retain the heavy-particle kinetic
energy at the accuracy of the provider's fixed-target, negligible-recoil
closure. The number of translational particles per baryon is `1+x`.

The recombination event rate per baryon is

\[
 \mathcal R=\kappa(T)x^2,
 \qquad \dot x=-\mathcal R.                         \tag{2}
\]

Define thermal energy `U`, stored ionization energy `I`, and cumulative
escaped bolometric recombination energy `E_gamma`, all in joules per baryon:

\[
 U=\frac32k_B(1+x)T,\qquad I=\chi_H x,
\]
\[
 \dot U=-n_B\Lambda_{\rm RR}(T)x^2,
 \qquad \dot I=-\chi_H\mathcal R,
\]
\[
 \dot E_\gamma=
 \mathcal R\left[\chi_H+k_BT\left(\frac32+D\right)\right].       \tag{3}
\]

Consequently

\[
 \boxed{\frac{d}{dt}(U+I+E_\gamma)=0.}               \tag{4}
\]

`E_gamma` is a cumulative escaped-energy ledger, not a radiation spectrum or
a photon count. Since expansion is zero, no redshift term is required in this
local ledger. The ionization energy is included exactly once in (3).

Applying the chain rule to `U` gives

\[
 \frac32k_B[(1+x)\dot T+T\dot x]
 =-\kappa x^2k_BT\left(\frac32+D\right),
\]
\[
 \boxed{\dot T=-\frac23\frac{\kappa(T)x^2TD(T)}{1+x}.}          \tag{5}
\]

The particle-number term `T xdot` is essential. Introduce the dimensionless
temperature coordinate `w = ln(T/T_i)`:

\[
 \dot x=-\kappa x^2,\qquad
 \boxed{\dot w=-\frac23\frac{\kappa x^2D}{1+x}.}                \tag{6}
\]

For this hydrogen fit `-3/2 < D < -1/2`, as shown below. Therefore `T` rises
while `U` decreases: the recombining electron population removes less kinetic
energy per event than the thermal energy per particle in the remaining gas.
The number and energy equations jointly produce this behavior.

### 2.2 Exact elimination of the composition coordinate

For `x>0`, divide the two equations in (6):

\[
 \frac{d\ln T}{dx}=\frac{2D(T)}{3(1+x)},\qquad
 \frac{d\ln(1+x)}{d\ln T}=\frac{3}{2D(T)}.
\]

Define

\[
 L(T)=\frac32\int_{T_i}^{T}\frac{d\ln\theta}{D(\theta)}.
\]

The exact composition path is then

\[
 \boxed{x(T)=(1+x_i)e^{L(T)}-1.}                    \tag{7}
\]

Substitution into (6) leaves one nontrivial state equation:

\[
 \boxed{\dot w=F(w)
  =-\frac23\frac{\kappa(T_i e^w)x(w)^2D(T_i e^w)}{1+x(w)}.}   \tag{8}
\]

Equation (3) can be integrated as a separate energy quadrature. Equations
(7)–(8) are an exact coordinate reduction within the supplied model. They
retain the evolving coefficient, temperature and heat capacity.

### 2.3 Closed primitive for the actual hydrogen VF rate

Set

\[
 r=\sqrt T,\quad r_i=\sqrt{T_i},\quad
 s_0=\sqrt{T_0},\quad s_1=\sqrt{T_1}.
\]

Differentiating the supplied rate gives

\[
 D=-\frac12
   -\frac{(1-b)r}{2(r+s_0)}
   -\frac{(1+b)r}{2(r+s_1)}
   =-\frac{Q(r)}{2(r+s_0)(r+s_1)},                 \tag{9}
\]
\[
 Q(r)=3r^2+c_Qr+s_0s_1,\qquad
 c_Q=(2+b)s_0+(2-b)s_1.
\]

For `r>0` and `|b|<1`, each fraction `r/(r+s_j)` lies between zero and one.
It follows that

\[
 -\frac32<D<-\frac12,\qquad
 0<\frac{\Lambda_{\rm RR}}{\alpha}<k_BT.            \tag{10}
\]

The quadratic factorization uses two distinct positive numbers:

\[
 \Delta=c_Q^2-12s_0s_1>0,\qquad
 Q(r)=3(r+\ell_1)(r+\ell_2),\qquad 0<\ell_1<\ell_2.
\]

Indeed `c_Q^2 >= 4(4-b^2)s_0s_1 > 12s_0s_1` when `|b|<1`.
Compute the roots without subtracting nearly equal positive numbers:

\[
 \boxed{\ell_2=\frac{c_Q+\sqrt\Delta}{6},\qquad
        \ell_1=\frac{s_0s_1}{3\ell_2}.}             \tag{11}
\]

Their product is exactly the required `s_0s_1/3`. The following partial
fraction identity gives the primitive:

\[
 \frac{(r+s_0)(r+s_1)}{rQ(r)}
 =\frac1r+\frac{B}{r+\ell_1}+\frac{C_2}{r+\ell_2},              \tag{12}
\]
\[
 \boxed{B=\frac{(s_0-\ell_1)(s_1-\ell_1)}
                 {-3\ell_1(\ell_2-\ell_1)},\qquad
        C_2=-\frac23-B.}                           \tag{13}
\]

An independent algebraic check of (12) is available from three coefficients.
The residue at zero is `s_0s_1/(3 ell_1 ell_2)=1`; the residue at `-ell_1`
is exactly `B` in (13); the coefficient at infinity is
`1+B+C_2=1/3`. These three conditions determine the quadratic numerator.

Using `d ln T = 2 dr/r` in the definition of `L` yields

\[
 \boxed{L(T)=-6\left[
    \ln\frac r{r_i}
   +B\ln\frac{r+\ell_1}{r_i+\ell_1}
   +C_2\ln\frac{r+\ell_2}{r_i+\ell_2}
                  \right].}                      \tag{14}
\]

All logarithms have dimensionless arguments. Near the initial state the
stable evaluation is

\[
 \delta r=r_i\operatorname{expm1}(w/2),
\]
\[
 L(w)=-6\left[\frac w2
 +B\operatorname{log1p}\!\left(\frac{\delta r}{r_i+\ell_1}\right)
 +C_2\operatorname{log1p}\!\left(\frac{\delta r}{r_i+\ell_2}\right)
            \right],
\]
\[
 \boxed{x(w)=x_i+(1+x_i)\operatorname{expm1}(L(w)).}             \tag{15}
\]

This avoids forming a difference of nearly equal square roots, ratios near
one followed by a logarithm, or `exp(L)-1` by direct subtraction. It does not
assert arbitrary relative accuracy at the complete-neutralization endpoint.
The finite experiment stops at `x_t >= x_i/4`, where that endpoint cancellation
is bounded.

### 2.4 Domain, stopping condition and useful Jacobians

Since `D<0`, `L` strictly decreases as `T` rises; `x(w)` decreases while
`F(w)>0` for `x>0`. A selected target `x_t` in `[x_i/4,x_i)` therefore has at
most one temperature on the physical path. Put

\[
 a_t=\ln\frac{1+x_i}{1+x_t}>0.
\]

The slope bound (10) gives `-3w <= L(w) <= -w`, hence

\[
 \frac{a_t}{3}\leq w_t\leq a_t,
\]
\[
 \boxed{T_i\left(\frac{1+x_i}{1+x_t}\right)^{1/3}
 \leq T_t\leq T_i\frac{1+x_i}{1+x_t}.}              \tag{16}
\]

This brackets the target without leaving the supplied interval. In particular,
`0<x_i<=1` and `x_t>=x_i/4` imply `T_t<=1.6 T_i`; choosing
`100 K <= T_i <= 6250 K` is a sufficient, conservative way to keep the entire
path in 100–10000 K. The actual finite run must declare its initial state and
target. A candidate stage outside the physical temperature or composition
interval is not an instruction to extrapolate the provider or clip a state.
For `nB=0` or `x_i=0` the direct equations instead give a constant state and
zero escaped power; the divided reduction need not be used.

The [frozen execution contract](EXECUTION_CONTRACT.md) chooses `x_i=0.9`,
`x_t=0.225`, `nB=1e12 m^-3` and `T_i` equal to 100, 1000 or 5000 K. All
three initial temperatures satisfy the sufficient domain bound above. With
`kappa_i=nB alpha(T_i)`, define dimensionless time `s=kappa_i t` and
`a_alpha(w)=alpha(T_i exp(w))/alpha(T_i)`. The reduced right-hand side is

\[
 g_s(w)=\frac{dw}{ds}
       =-\frac23\frac{a_\alpha(w)x(w)^2D(w)}{1+x(w)}.
\]

After solving the monotone equation `L(w_t)=-a_t` in the bracket (16), the
common finite final time is fixed independently of either production solver:

\[
 \boxed{s_t=\int_0^{w_t}\frac{dw}{g_s(w)}.}          \tag{16a}
\]

The integrand is finite and positive on this interval because the target
abundance is strictly positive, the coefficient is positive and `D` is bounded
away from zero. Full and reduced trajectories can therefore be compared at
the same specified values of `s`.

Within this selected model, both the orbit `T(x)` and the entire dimensionless
trajectory in `s` are independent of `nB` and of a multiplicative change in
the overall VF amplitude `A_VF`: the slope `D` and the rate ratio `a_alpha`
do not contain either factor. These changes affect only the physical clock
`t=s/[nB alpha(T_i)]`. This exact scaling permits reuse of the same finite
dimensionless solution across those densities or amplitudes; another density
sweep is not required to establish it. It does not assess omitted competing
processes or thermalization time scales.

For an analytic Jacobian, write `D_w = dD/dw`. Equation (9) gives

\[
 D_w=-\frac{(1-b)rs_0}{4(r+s_0)^2}
     -\frac{(1+b)rs_1}{4(r+s_1)^2},\qquad
 \kappa_w=\kappa D.                                \tag{17}
\]

The full composition/temperature equations `f_x=xdot`, `f_w=wdot` obey

\[
 \partial_x f_x=-2\kappa x,\qquad
 \partial_w f_x=-\kappa Dx^2,
\]
\[
 \partial_x f_w=-\frac23\kappa D\frac{x(2+x)}{(1+x)^2},\qquad
 \partial_w f_w=-\frac23\frac{\kappa x^2(D^2+D_w)}{1+x}.       \tag{18}
\]

Along (7), `dx/dw = 3(1+x)/(2D)`, so the reduced derivative is

\[
 \boxed{F'(w)=-\frac23\frac{\kappa x^2(D^2+D_w)}{1+x}
                   -\frac{\kappa x(2+x)}{1+x}.}    \tag{19}
\]

If the independently integrated energy is included as a third state, set
`epsilon = chi_H + k_B T (3/2+D)` and `g = E_gammadot = kappa x^2 epsilon`.
Then

\[
 \partial_x g=2\kappa x\epsilon,\qquad
 \partial_w g=\kappa x^2\left[
 D\epsilon+k_BT\left(\frac32+D+D_w\right)\right].   \tag{20}
\]

All derivatives with respect to `E_gamma` vanish. The energy value reconstructed
from (4) is a useful reference, but reconstructing it from the invariant and
then checking that same invariant would not independently test (3). A comparison
of the full state equations with (8), together with a separately integrated
escaped-energy quadrature, can test the reduction and the energy ledger.

## 3. Case 2: neutron beta production followed by hydrogen recombination

### 3.1 Physical channel and isothermal equations

Let

\[
 n=Y_n,\qquad p=Y_{\mathrm{H\,II}},\qquad h=Y_{\mathrm{H\,I}},
\]

with nonnegative initial values satisfying `n_0+p_0+h_0=1`. The selected
nuclear channel is continuum decay

\[
 n\longrightarrow p+e^-+\bar\nu_e,
\]

followed by `p+e^- -> H I + escaping radiation`. At the prescribed constant
temperature, `kappa=nB alpha(T)` is constant. The evaluated neutron mean
lifetime gives

\[
 \lambda=1/(878.4\ {\rm s}).
\]

Using this total evaluated lifetime as the selected continuum-channel rate
retains the inherited omission of separately resolved bound-beta branching.
No charge-state-dependent branching fraction is supplied or inferred here.

The equations are

\[
 \boxed{\dot n=-\lambda n,\qquad
 \dot p=\lambda n-\kappa p^2,\qquad
 \dot h=\kappa p^2.}                               \tag{21}
\]

The beta electron is admitted to the prescribed thermal electron pool, with
`Y_e=p`. This is the instantaneous number-thermalization, isothermal bath
assumption of this population calculation. It does not calculate a stopping
time or the beta electron's energy deposition.

Equation (21) preserves `n+p+h=1`. At each coordinate boundary its outward
derivative is zero or points into the nonnegative region. Charge neutrality
is also consistent: beta creates one unit of positive ionic charge and one
electron; RR removes one of each. No independent electron production factor
is to be added to the `p^2` flux.

### 3.2 Exact positive subflows and their composition

For a duration `tau>=0`, the beta subflow is

\[
 n'=n e^{-\lambda\tau},\qquad
 d_\beta=-n\operatorname{expm1}(-\lambda\tau),\qquad
 p'=p+d_\beta,\qquad h'=h.                          \tag{22}
\]

For the RR subflow put `z_R=kappa tau p`:

\[
 p'=\frac{p}{1+z_R},\qquad
 d_R=\frac{p z_R}{1+z_R},\qquad
 h'=h+d_R,\qquad n'=n.                             \tag{23}
\]

The event extents avoid subtracting nearly equal populations for a small step.
Both maps preserve nonnegativity and the baryon sum in exact arithmetic for
every nonnegative step, without clipping or normalization.

Let these maps be `Phi_beta^tau` and `Phi_R^tau`. One palindromic step is

\[
 \boxed{S_\tau=
 \Phi_\beta^{\tau/2}\circ\Phi_R^\tau\circ\Phi_\beta^{\tau/2}.} \tag{24}
\]

Chronologically this means a beta half-step, one RR full-step, and a beta
half-step. Each stage is an exact physical subflow. The composed map is
nonnegative and preserves the linear baryon invariant. For fixed finite
`lambda` and `kappa`, the autonomous vector fields are smooth on the invariant
simplex; symmetric Strang composition has local error `O(tau^3)` and global
error `O(tau^2)` on a fixed finite time interval.

The fields do not commute. With
`v_beta=(-lambda n,lambda n,0)`, `v_R=(0,-kappa p^2,kappa p^2)` and the
explicit convention `[v_beta,v_R]=v_R' v_beta-v_beta' v_R`,

\[
 [v_\beta,v_R]=(0,-2\kappa\lambda np,2\kappa\lambda np).       \tag{25}
\]

Thus exact individual substeps do not make their finite composition exact.
The stated second-order limit is not a uniform stiff-limit error bound.
Positive populations and conserved totals also do not by themselves establish
relative accuracy in a small produced species.

For the frozen population experiment use dimensionless time `v=lambda t`
and `rho=kappa/lambda`. Then

\[
 \frac{dn}{dv}=-n,\qquad
 \frac{dp}{dv}=n-\rho p^2,\qquad
 \frac{dh}{dv}=\rho p^2.                            \tag{25a}
\]

The contract chooses `(n_0,p_0,h_0)=(0.1,0.2,0.7)`, `rho` equal to 0.1,
1 or 10, and `0<=v<=4`. The prescribed temperature is 1000 K and the
corresponding density is `nB=rho lambda/alpha(1000 K)`. These define a local
model family, not a measured thermal or cosmological history.

In dimensionless time a direct expansion of (22)–(24) through a full step `d`
gives

\[
 n_{\rm new}=n-nd+\frac12nd^2+O(d^3),
\]
\[
 p_{\rm new}=p+(n-\rho p^2)d
       +\frac12(-n-2\rho np+2\rho^2p^3)d^2+O(d^3),
\]
\[
 h_{\rm new}=h+\rho p^2d
       +\rho p(n-\rho p^2)d^2+O(d^3).               \tag{25b}
\]

These coefficients equal the first two Taylor coefficients obtained by
differentiating (25a). This verifies order two for the particular retained
fields without relying only on the name of the splitting scheme.

### 3.3 Independent exact solution through modified Bessel functions

For `lambda>0`, `kappa>0`, `n_0>0`, first solve

\[
 n(t)=n_0e^{-\lambda t}.
\]

The Riccati substitution

\[
 p=\frac{u'}{\kappa u},\qquad u(0)=1,\quad u'(0)=\kappa p_0
\]

turns the remaining population equation into

\[
 u''=\kappa\lambda n_0 e^{-\lambda t}u.             \tag{26}
\]

Set

\[
 a=2\sqrt{\kappa n_0/\lambda},\qquad
 z=a e^{-\lambda t/2}.
\]

Both variables are dimensionless. Equation (26) becomes

\[
 z^2u_{zz}+zu_z-z^2u=0,
\]

so

\[
 u=A_B I_0(z)+B_B K_0(z),
\]

where `I_nu,K_nu` are modified Bessel functions. Define

\[
 c_0=\frac{2\kappa p_0}{\lambda a}.
\]

Using `I_0'=I_1`, `K_0'=-K_1` and
`I_0(a)K_1(a)+I_1(a)K_0(a)=1/a`, the initial conditions give

\[
 A_B=a[K_1(a)-c_0K_0(a)],\qquad
 B_B=a[I_1(a)+c_0I_0(a)].                           \tag{27}
\]

The independent exact population reference is

\[
 \boxed{p(t)=\frac{\lambda z}{2\kappa}
 \frac{B_BK_1(z)-A_BI_1(z)}{A_BI_0(z)+B_BK_0(z)},\qquad
 h(t)=1-n(t)-p(t).}                                \tag{28}
\]

In the contract's dimensionless variables, the same normalized coefficients
can be written without the auxiliary `c_0`:

\[
 a=2\sqrt{\rho n_0},\qquad z=a e^{-v/2},
\]
\[
 \boxed{c_B=aK_1(a)-2\rho p_0K_0(a),\qquad
        d_B=aI_1(a)+2\rho p_0I_0(a),}               \tag{28a}
\]
\[
 \boxed{u=c_BI_0(z)+d_BK_0(z),\qquad
 p(v)=\frac{z}{2\rho}
       \frac{d_BK_1(z)-c_BI_1(z)}{c_BI_0(z)+d_BK_0(z)}.}      \tag{28b}
\]

The Bessel identity above gives `u(0)=1` exactly in algebra. This coefficient
form does not divide by `c_B`, which may vanish or be negative for valid
nonnegative initial populations. The optional ratio

\[
 q=\frac{c_B}{d_B}
 =\frac{K_1(a)-(2\rho p_0/a)K_0(a)}
        {I_1(a)+(2\rho p_0/a)I_0(a)}
\]

is also nonsingular for `a>0`, since its denominator is positive. It gives
`p=z[K_1(z)-q I_1(z)]/[2rho(K_0(z)+q I_0(z))]`, but the normalized coefficient
form (28a)–(28b) is sufficient. A negative coefficient is not a negative
population or an alternative physical branch.

For the frozen positive cases `a<=2` and `a exp(-2)<=z<=a`, so the specified
finite reference does not require a large-argument asymptotic evaluation.
At `v=0`, return the supplied initial state directly rather than using special
functions to rederive it numerically. The positivity proof below controls
the exact denominator; floating-point agreement remains a measured check.

The denominator is analytically positive. In fact `u(0)=1`, `u'(0)>=0`
and (26) imply that `u` and its derivative cannot decrease while `u>0`, so
there can be no first positive-time zero. This argument remains valid when
the coefficient `A_B` is negative.

The physically useful onset choice `p_0=0` gives the simpler expression

\[
 \boxed{p(t)=\frac{\lambda z}{2\kappa}
 \frac{I_1(a)K_1(z)-K_1(a)I_1(z)}
      {K_1(a)I_0(z)+I_1(a)K_0(z)}.}                \tag{29}
\]

The denominator is now a sum of positive terms. The numerator vanishes at
`t=0`, where the reference must return the prescribed `p_0` exactly. Its
small-time limit follows directly from (21): for `p_0=0`,

\[
 p(t)=\lambda n_0t-\frac12\lambda^2n_0t^2+O(t^3).  \tag{30}
\]

The RR term first enters the cubic coefficient of this onset series. Near
`t=0`, directly subtracting the two positive terms in (29) can lose relative
precision. If `J_1=I_1(a)K_1(z)` and `J_2=K_1(a)I_1(z)`, its numerator can
instead be organized as

\[
 J_1-J_2=-J_1\operatorname{expm1}(\ln J_2-\ln J_1).             \tag{31}
\]

Scaled Bessel functions or log products also avoid unnecessary exponential
overflow at large arguments. These are evaluation considerations, not an
unmeasured claim of uniform reference accuracy. The finite run should choose
and assess its reference evaluation on its actual argument range, including
the onset. No integration of the original nonlinear equations is required
to define the analytic reference (28).

### 3.4 Degenerate limits

The singular parameter limits of the Bessel representation have regular
population solutions and should use those expressions directly:

| Condition | Exact population evolution |
|---|---|
| `kappa=0` | `n=n_0 exp(-lambda t)`, `p=p_0+n_0[-expm1(-lambda t)]`, `h=h_0` |
| `n_0=0` | `n=0`, `p=p_0/(1+kappa p_0 t)`, `h=h_0+p_0-p` |
| `lambda=0` | `n=n_0`, `p=p_0/(1+kappa p_0 t)`, `h=h_0+p_0-p` |
| `n_0=p_0=0` | The neutral initial state is constant |

In dimensionless variables the `rho=0` limit is
`n=n_0 exp(-v)`, `p=p_0+n_0[-expm1(-v)]`, `h=h_0`; the `n_0=0` limit is
`p=p_0/(1+rho p_0 v)`, `h=h_0+p_0-p`. The composed subflows reproduce these
limiting trajectories exactly in algebra, because the inactive subflow is
the identity and each active subflow has the semigroup property.

For a source-onset case with `p_0=0`, put

\[
 S(v)=n_0(1-e^{-v})=n_0[-\operatorname{expm1}(-v)].
\]

The exact solution satisfies `0<=p(v)<=S(v)`. Integrating the population
equation gives

\[
 S(v)-p(v)=\rho\int_0^v p(\eta)^2\,d\eta.
\]

Since `p(eta)<=n_0` and `p(eta)<=S(v)` for `0<=eta<=v`,

\[
 \boxed{0\leq\frac{S(v)-p(v)}{S(v)}\leq\rho n_0v,
             \qquad n_0>0,\ v>0.}                 \tag{32}
\]

This gives an analytic component-relative reference bound for the frozen
trace case `rho=1`, `n_0=1e-104`, `v=1`. The omitted quadratic loss has
relative size at most `1e-104`, so the analytic decay source is an adequate
binary64 relative reference. The tiny produced amount must remain a separate
stored component when its subtraction from a neutral population near one
rounds away. This bound justifies that trace reference without assigning an
artificial floor or claiming that Bessel subtraction is accurate at arbitrary
small source amplitude.

### 3.5 Energy boundary of the isothermal case

The saved neutron beta input supplies the total bare-mass release
`Q_bare = 1.2534365419049505e-13 J` per event. In the prior neutral-atom ledger,
the matching continuum endpoint has `dI=chi_H` and `Q0=Q_bare+chi_H`. These
are energy-reference identities, not thermal-energy partitions.

No electron/neutrino/recoil partition or stopping provider is supplied for
this case. The fixed temperature is maintained by a prescribed bath, whose
energy exchange is not solved. Therefore (21)–(31) describe an isothermal
population calculation only. A total beta-release counter, if retained, must
remain explicitly unpartitioned; assigning its value to heat would introduce
an unsupported physical input. Case 1 provides the closed thermal calculation
using the moment that is actually available.

## 4. What these derivations establish

The derivations establish exact model identities, a closed finite composition
path for the actual hydrogen rate, an exact scalar state reduction, positive
analytic subflows for the coupled nuclear/atomic population case, and an
independent special-function reference for the latter. They identify the
provider interval, finite stopping condition and the energy assumptions that
make each case defined.

Numerical accuracy, achieved convergence, solver cost and measured speedup
remain execution results. They must be reported from the newly frozen finite
experiments, without relabeling inherited tests as new results or interpreting
the conditional moment as an empirical thermal-provider validation.
