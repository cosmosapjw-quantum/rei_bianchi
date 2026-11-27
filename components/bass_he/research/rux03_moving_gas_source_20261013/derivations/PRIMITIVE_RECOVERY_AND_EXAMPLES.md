# Exact primitive recovery and constructive absorption references

Unit: HERE_RUX03_MOVING_GAS_SOURCE_05. Route: THEORY. Date: 2026-10-13 KST.

This contribution proves the global constitutive inverse used by the moving
source stage and constructs finite positive absorption references. It is an
author derivation; the independent adoption decision belongs to the designated
reviewer. The full seven-variable, all-channel source branch is the root
derivation's implicit-function construction.

## 1. Reused constitutive input and notation

The starting point is the opening in the accepted
[THEORY04 handoff](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/dossier/HANDOFF_KO.md) and
[next DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/dossier/NEXT_DAG.json).
The gas energy and pressure are the neutral-reference constitutive law in
[THEORY04, §5](https://github.com/cosmosapjw-quantum/BASS_HE/blob/ca85cfc7353da190613f7fb37a6e0ffed9b51913/research/rux03_covariant_exchange_20261013/derivations/COVARIANT_EVENT_EXCHANGE.md).
The current scope is the
[THEORY05 scientific contract](../dossier/SCIENTIFIC_CONTRACT.md).
The immutable source and reuse identities are recorded in
[VALID_REUSE_IDENTITY.json](../source_map/VALID_REUSE_IDENTITY.json) and
[CURRENT_SOURCE.json](../source_map/CURRENT_SOURCE.json).

Use one fixed local Eulerian tetrad, signature \((-+++)\), one fixed lab volume,
and one common gas velocity. All densities below are measured per that same
lab volume unless explicitly called proper densities. There is no geometrical
transport during this source substep. Let

\[
\Gamma=\frac53,\qquad \kappa=\Gamma-1=\frac23,\qquad
\alpha=\frac{\Gamma}{\kappa}=\frac52,\qquad
\theta=\epsilon_{\rm eV}w.
\tag{P1}
\]

Here \(w\) is thermal eV per H and \(\theta\) is physical thermal energy per H,
in erg when the inherited cgs constants are used. Define

\[
\begin{split}
&D=\gamma n_H>0,\qquad
\gamma=(1-|\boldsymbol\beta|^2)^{-1/2},\\
&r=m_{\rm ref}c^2+\epsilon_{\rm eV}B>0,\\
&\rho=n_H(r+\theta),\qquad p=\kappa n_H\theta,\\
&E=(\rho+p)\gamma^2-p,\qquad
\mathbf M=(\rho+p)\gamma^2\boldsymbol\beta .
\end{split}
\tag{P2}
\]

\(\mathbf M\) is \(c\) times physical momentum density. Consequently \(E,p\)
and each component of \(\mathbf M\) have the same units, erg cm\(^{-3}\).
The velocity \(\boldsymbol\beta=\mathbf v/c\) is dimensionless. The neutral
reference mass \(m_{\rm ref}=m_{\rm HI}+f m_{\rm HeI}\) already includes the
bound electrons. Ionization changes \(B\), while \(m_{\rm ref}\) stays fixed.
No electron rest mass is added again.

For the inverse problem, \(D,r\) and the composition are prescribed at the
candidate endpoint. Thus the particle count per H

\[
d=1+f+x+f(a_{\rm HeII}+2b_{\rm HeIII})>0,\qquad
T=\frac{2\theta}{3k_Bd}
\tag{P3}
\]

is prescribed apart from its dependence on \(\theta\). The inverse is applied
again at each candidate composition; it does not freeze composition or atomic
rates across a nonlinear source solve.

The following abbreviations avoid using the helium fraction or the photon
absorption increment as a rest-energy density:

\[
a_r=Dr>0,\qquad m=|\mathbf M|,\qquad
C=D(r+\Gamma\theta),\qquad
\mathcal W=E+p.
\tag{P4}
\]

In the root's Jacobian notation \(A=a_r\) and \(W=\mathcal W\).
Gas \(E\) is an energy density. A photon has lab energy \(E_q\) in eV and
\(\mathcal E_q=\epsilon_{\rm eV}E_q=\hbar\omega_q\) in erg; those quantities
are not interchangeable with gas \(E\).

## 2. Exact reduction to one scalar

Since \(\rho+p=n_H(r+\Gamma\theta)\), equations (P2) give

\[
\mathcal W=C\gamma,\qquad
\mathbf M=\mathcal W\boldsymbol\beta,\qquad
\mathcal W^2-m^2=C^2.
\tag{P5}
\]

For a physical state \(C\ge a_r>0\), so

\[
\begin{split}
\mathcal W(C)&=\sqrt{C^2+m^2},\\
\gamma(C)&=\frac{\mathcal W(C)}{C},\qquad
n_H(C)=\frac{DC}{\mathcal W(C)},\\
\boldsymbol\beta(C)&=\frac{\mathbf M}{\mathcal W(C)},\\
\theta(C)&=\frac{3(C-a_r)}{5D},\\
p(C)&=\frac{2C(C-a_r)}{5\mathcal W(C)}.
\end{split}
\tag{P6}
\]

The only equation left is

\[
\boxed{
E=\mathscr E(C;a_r,m^2)
=\frac{3C^2+2a_rC+5m^2}{5\sqrt{C^2+m^2}},
\qquad C\ge a_r.}
\tag{P7}
\]

Conversely, any solution of (P7) with \(C\ge a_r\), inserted in (P6),
satisfies every equation in (P2), \(D=\gamma n_H\), positive proper density,
and \(|\boldsymbol\beta|<1\). Thus this reduction is an equivalence.

## 3. Global existence and uniqueness theorem

**Theorem.** Fix \(D>0\), \(r>0\), a physical composition and a finite
\(\mathbf M\). A finite primitive with \(n_H>0\), \(\theta>0\) and
\(|\boldsymbol\beta|<1\) exists exactly when

\[
\boxed{E>\sqrt{(Dr)^2+|\mathbf M|^2}.}
\tag{P8}
\]

It is unique. If the algebraic EOS is extended to \(\theta=0\), equality in
(P8) admits exactly one cold primitive. No primitive with
\(\theta\ge0\) has \(E<\sqrt{(Dr)^2+|\mathbf M|^2}\).

**Proof.** The scalar map (P7) satisfies

\[
\mathscr E(a_r)=E_0\equiv\sqrt{a_r^2+m^2},
\tag{P9}
\]

\[
\mathscr E_C
=\frac{3C^3+C m^2+2a_r m^2}
       {5(C^2+m^2)^{3/2}}>0\qquad(C\ge a_r>0),
\tag{P10}
\]

and \(\mathscr E(C)\to+\infty\) as \(C\to+\infty\).
Continuity and strict monotonicity therefore map
\([a_r,\infty)\) bijectively to \([E_0,\infty)\), and map
\((a_r,\infty)\) bijectively to \((E_0,\infty)\).
The equivalence in §2 proves both necessity and sufficiency. Direction is
also unique because \(\boldsymbol\beta=\mathbf M/\mathcal W\). At \(m=0\),
the same equation gives \(\boldsymbol\beta=0\), without a direction choice.
This proves the theorem.

At the cold boundary the explicit state is

\[
p=\theta=0,\qquad
\gamma=\frac{E_0}{a_r},\qquad
n_H=\frac{D a_r}{E_0},\qquad
\boldsymbol\beta=\frac{\mathbf M}{E_0}.
\tag{P11}
\]

Since \(a_r>0\), this boundary still has a strictly subluminal velocity.
It is outside the adopted \(30000\)–\(110000\) K FT03 interval. Equation
(P11) is the exact boundary of the mathematical gamma-law inverse, not a
new cold physical scenario.

### 3.1 Exact warm-domain test

Positive thermal energy is a larger mathematical domain than the adopted
atomic provider's warm domain. For the current candidate composition set

\[
\theta_{\min,\max}=\frac32 k_Bd\,T_{\min,\max},\qquad
C_{\min,\max}=a_r+\frac53D\theta_{\min,\max}.
\tag{P12}
\]

The unique inverse has \(T_{\min}\le T\le T_{\max}\) **if and only if**

\[
\boxed{
\mathscr E(C_{\min};a_r,m^2)\le E
\le\mathscr E(C_{\max};a_r,m^2).}
\tag{P13}
\]

This follows directly from (P10). A strict warm interior uses strict
inequalities. Composition must separately lie in its H/He simplex, and
each active gas-frame photon energy must lie in the provider domain.
The source survey fixes that domain at \(0\le E'_q\le50000\) eV with the
separate fit cutoffs \(13.60,24.59,54.42\) eV. The cold-cone test (P8)
does not replace any of these constitutive conditions.

## 4. Stable scalar recovery and derivatives

The useful unknown close to the cold boundary is the thermal enthalpy
excess

\[
z=C-a_r=\frac53D\theta\ge0,\qquad
\delta=E-E_0.
\tag{P14}
\]

Let \(\mathcal W=\sqrt{(a_r+z)^2+m^2}\).
Rationalizing \(\mathcal W-E_0\) gives

\[
\mathcal W-E_0=\frac{z(2a_r+z)}{\mathcal W+E_0}.
\tag{P15}
\]

The energy gap has the exact, positive-term expression

\[
\boxed{
g(z)\equiv\mathscr E(a_r+z)-E_0
=\frac{z(6a_r+z)}{5(\mathcal W+E_0)}
 +\frac{2z^2(a_r+z)(2a_r+z)}
 {5\mathcal W(\mathcal W+E_0)^2}.}
\tag{P16}
\]

Indeed, first write
\(g=z[(2a_r+z)/(\mathcal W+E_0)-(2/5)(a_r+z)/\mathcal W]\),
put it over a common denominator, and replace
\(\mathcal W-E_0\) using (P15). Every factor on the right side of (P16)
is nonnegative. The positive root of \(g(z)=\delta\) therefore need not be
found by repeatedly subtracting the full rest energy from a computed
total energy.

The second derivative of the scalar energy is

\[
\mathscr E_{CC}
=\frac{m^2(7C^2-6a_rC+m^2)}
       {5(C^2+m^2)^{5/2}}\ge0\qquad(C\ge a_r).
\tag{P17}
\]

For the sign, \(7C^2-6a_rC=C^2+6C(C-a_r)>0\).
At \(C=a_r\), the first derivative is \(3a_r/(5E_0)\), and
\(a_r\le C\) bounds its numerator above by \(3C(C^2+m^2)\).
Consequently

\[
\frac{3a_r}{5E_0}\le g'(z)\le\frac35,
\tag{P18}
\]

which supplies a finite deterministic bracket for every \(\delta>0\):

\[
\boxed{\frac53\delta\ \le z_*\le\
\frac{5E_0}{3a_r}\delta.}
\tag{P19}
\]

At \(m=0\) the endpoints agree:
\(z_*=5(E-a_r)/3\), \(\theta=E/D-r\),
\(p=2(E-a_r)/3\), \(n_H=D\).

A constructive recovery algorithm is therefore:

1. Check \(D>0,r>0\), finite supplied data, and the exact intended sign
   of \(\delta=E-\operatorname{hypot}(a_r,m)\).
2. For \(\delta>0\), bracket \(z\) by (P19), evaluate \(g\) with (P16),
   and use safeguarded Newton with derivative (P10) or bisection.
3. Recover the primitive from (P6). A convenient normalization is
   \(\mathbf u_{\rm sp}=\mathbf M/C\) and
   \(\gamma=\sqrt{1+|\mathbf u_{\rm sp}|^2}\).
4. Check the actual composition, warm and Doppler-energy domains at
   that same primitive.

Using a common energy-density scale and a hypot operation avoids squaring
very large dimensional inputs. The formulas reduce algebraic cancellation;
they do not recover information already lost when \(E\) and \(E_0\) were
rounded to the same floating-point value. Near that boundary, a compensated
or interval evaluation of the supplied conservative gap can establish its
sign. An unresolved sign is an unresolved input-domain test, not a license
to clip the gap to a positive number. This is an implementation consequence
of the exact theorem, not a prescribed numerical tolerance.

### 4.1 Smooth dependence and exact inverse derivatives

Use \(s=m^2\), rather than the nondifferentiable norm \(m\), as the parameter
in (P7). With

\[
\mathcal N=3C^3+Cs+2a_rs>0,\qquad
\mathcal W=\sqrt{C^2+s},
\tag{P20}
\]

implicit differentiation yields

\[
\begin{split}
C_E&=\frac{5\mathcal W^3}{\mathcal N}>0,\\
C_s&=-\frac{7C^2-2a_rC+5s}{2\mathcal N}<0,\\
C_{a_r}&=-\frac{2C\mathcal W^2}{\mathcal N},\\
\frac{\partial C}{\partial M_i}&=2M_i C_s.
\end{split}
\tag{P21}
\]

The sign of \(C_s\) follows from
\(7C^2-2a_rC\ge5C^2>0\).
Every expression is smooth also at \(\mathbf M=0\), because \(C>0\).
Together with (P6), the inverse is \(C^\infty\) on the open cone (P8)
for fixed \(D,r\), and depends smoothly on varying positive \(D,r\).
The temperature also varies smoothly with a physical interior composition.
This gives the constitutive inverse needed by the root's local stage
implicit-function theorem. It does not assert that a nonlinear source
stage has a global unique endpoint for arbitrary step size.

## 5. Equivalent pressure root and forward Jacobian

An independent pressure representation makes a useful consistency boundary.
For \(p\ge0\), set
\(\mathcal W=E+p\), \(C=\sqrt{\mathcal W^2-m^2}\), and define

\[
F(p)=p-\frac25\left[
\mathcal W-\frac{m^2}{\mathcal W}
-a_r\sqrt{1-\frac{m^2}{\mathcal W^2}}\right].
\tag{P22}
\]

For data in (P8), \(C>a_r\) at \(p=0\) and at every \(p>0\). With
\(v^2=m^2/\mathcal W^2\),

\[
F'(p)=\frac15\left(3-2v^2+\frac{2a_rv^2}{C}\right),
\qquad \frac15<F'(p)\le\frac35.
\tag{P23}
\]

At \(p=0\), \(F(0)=-(2/5)C(C-a_r)/E<0\).
The upper point \(p_U=2(E-a_r)/3\) satisfies

\[
F(p_U)=\frac{2(\mathcal W-C)(\mathcal W+C-a_r)}
                  {5\mathcal W}\ge0.
\tag{P24}
\]

Thus \([0,p_U]\) is another exact bracket. It describes the same unique
primitive as (P7); the excess-variable form (P16) is preferable when
representing a small thermal energy next to a large rest energy.

For comparison with the root's forward-Jacobian proof, write

\[
\mathcal W=a_r\gamma+\alpha p\gamma^2,\qquad
E=\mathcal W-p,\qquad
\mathbf M=\mathcal W\boldsymbol\beta.
\tag{P25}
\]

In the coordinate ordering \((p,\beta_1,\beta_2,\beta_3)\), direct
differentiation or a rank-one determinant gives

\[
\begin{split}
\det\frac{\partial(E,\mathbf M)}{\partial(p,\boldsymbol\beta)}
&=\mathcal W^2\left[(\mathcal W_p-1)\mathcal W
-\boldsymbol\beta\cdot\nabla_\beta\mathcal W\right]\\
&=\boxed{\mathcal W^2\left[
a_r(\alpha-1)\gamma^3
+\alpha p\{(\alpha-2)\gamma^4+\gamma^2\}\right]}>0 .
\end{split}
\tag{P26}
\]

Here \(\mathcal W_p=\alpha\gamma^2\) and
\(\nabla_\beta\mathcal W=(a_r\gamma^3+2\alpha p\gamma^4)\boldsymbol\beta\).
At \(\alpha=5/2\), all displayed terms are nonnegative and the first is
strictly positive. The root communicated the determinant as its local
branch ingredient; this calculation and the global scalar inverse agree.
For the coordinate change to \((w,\boldsymbol\beta)\) at fixed \(D\),
\(\partial p/\partial w|_\beta=\kappa D\epsilon_{\rm eV}/\gamma>0\).
The positive determinant therefore persists in the thermal variable used
by the source residual.

## 6. Finite causal absorption and the binding budget

Let an initial admissible state have \(a_r=Dr\), and let a finite absorbed
photon energy-momentum increment be \((L,\mathbf J)\), in energy-density
units, with

\[
L\ge0,\qquad |\mathbf J|\le L.
\tag{P27}
\]

Let the composition update change \(a_r\) to \(a_r+b\), where
\(b=D\epsilon_{\rm eV}\Delta B\). The same absorbed photons give

\[
E^+=E+L,\qquad \mathbf M^+=\mathbf M+\mathbf J.
\tag{P28}
\]

Writing \(\mathcal C=E^2-|\mathbf M|^2-a_r^2\), the exact updated margin is

\[
\boxed{
\mathcal C^+=
\mathcal C+2(E L-\mathbf M\cdot\mathbf J)
+L^2-|\mathbf J|^2-2a_rb-b^2.}
\tag{P29}
\]

For \(b=0\), \(E>|\mathbf M|\) and (P27) imply
\(E L-\mathbf M\cdot\mathbf J\ge(E-|\mathbf M|)L\ge0\).
Every nonzero future-causal absorption increment therefore preserves, and
strictly increases, the positive-thermal margin at fixed composition.
For a single beam \(\mathbf J=L\mathbf e\), \(|\mathbf e|=1\),

\[
\mathcal C^+=\mathcal C+
2L(E-\mathbf M\cdot\mathbf e)-2a_rb-b^2.
\tag{P30}
\]

For equal opposite beams \(\mathbf J=0\),

\[
\mathcal C^+=\mathcal C+2EL+L^2-2a_rb-b^2.
\tag{P31}
\]

The \(b\) terms are the finite chemical rest-energy cost. Equations
(P29)–(P31), together with \(a_r+b>0\) and \(E+L>0\), are an exact
post-absorption cone test. The warm test is then (P13) at the new
composition. Positivity of photon counts alone does not remove the
chemical energy cost.

For a net finite update containing escape, use its actual signed lab
increment \((\Delta E,\Delta\mathbf M)\) in the identity (P29). The total
absorbed increment is future-causal; a difference between absorption and
escape need not be. Under the separate constitutive condition \(a_r+b>0\),
a direct sufficient condition for the new positive-thermal cone is

\[
|\Delta E|+|\Delta\mathbf M|+|b|
<E-\sqrt{a_r^2+|\mathbf M|^2}.
\tag{P32}
\]

To prove it, use the reverse triangle inequality for
\((a_r,\mathbf M)\) and
\(\sqrt{b^2+|\Delta\mathbf M|^2}\le|b|+|\Delta\mathbf M|\).
The new energy then exceeds the new rest-momentum norm. Equation (P32)
is conservative and only controls the algebraic cone. The root's
strict-interior local branch theorem also controls the warm, composition,
photon and smooth-provider margins for sufficiently small \(h\).

## 7. Exact warm single-beam HI absorption family

This section is an **absorption-only channel reference**: it uses the
inherited HI threshold, cross section, chemical binding and gas EOS, while
the other integrated channel increments are set to zero for this reference.
It does not change the adopted full FT03 model, in which CI, RR and both
DR channels remain present. The all-channel implicit stage is treated by
the root's local theorem.

### 7.1 Inputs and conservative update

Choose a rest initial state with

\[
\boldsymbol\beta^-=0,\quad T_0=50000\ {\rm K},\quad
0<x_0<1,\quad a_0>0,\quad b_0>0,\quad a_0+b_0<1.
\tag{P33}
\]

For example \(x_0=1/2,a_0=b_0=1/4\) is an explicit interior composition
for every fixed \(f>0\). This is a new analytic reference family, not a
replacement of the retained production initial data. Set

\[
\begin{split}
d_0&=1+f+x_0+f(a_0+2b_0),\\
\theta_0&=\frac32 k_Bd_0T_0,\quad
r_0=m_{\rm ref}c^2+\epsilon_{\rm eV}B_0,\quad
R_0=r_0+\theta_0,\\
E_\gamma&=23\ {\rm eV},\quad
\mathcal E=\epsilon_{\rm eV}E_\gamma,\quad
I=\epsilon_{\rm eV}\chi_H,\quad
k=I/\mathcal E=\chi_H/23\in(0,1).
\end{split}
\tag{P34}
\]

The inherited binding energy is
\(\chi_H=13.598434599702\) eV; its fit activation is \(13.60\) eV.
An absorbed photon count \(D\xi\) per lab volume, \(\xi>0\), gives

\[
\begin{split}
x^+&=x_0+\xi,\qquad a^+=a_0,\qquad b^+=b_0,\qquad d^+=d_0+\xi,\\
r^+&=r_0+I\xi,\\
E^+&=D(R_0+\mathcal E\xi),\qquad
\mathbf M^+=D\mathcal E\xi\,\mathbf e_z.
\end{split}
\tag{P35}
\]

H and He nuclei remain fixed per lab volume: \(D^+=D^-=D\) and
the helium nucleus density is \(fD\). The reference mass contribution
\(D m_{\rm ref}\) is also conserved. The proper H density is allowed to
change to \(D/\gamma^+\); omitting that Lorentz dilution would change the
EOS and the opacity. The same event increases the electron count per H
by \(\xi\), precisely as used in \(d^+\).

In particular, all proper collider and absorber densities share that same
dilution:

\[
n_H^+=D/\gamma^+,\qquad n_{\rm He}^+=fD/\gamma^+,\qquad
n_e^+=\frac D{\gamma^+}
[x_0+\xi+f(a_0+2b_0)] .
\tag{P35a}
\]

There is no independently frozen electron or helium proper density in
this reference. The fixed-volume conserved inputs are the nucleus counts
and neutral-reference mass per volume; the proper densities are recovered
quantities.

### 7.2 Closed rational parameterization

Let

\[
\zeta=\sqrt{\frac{1+v}{1-v}}>1,\qquad
v=\frac{\zeta^2-1}{\zeta^2+1},\qquad
\gamma=\frac{\zeta^2+1}{2\zeta}.
\tag{P36}
\]

The new scalar \(\zeta\) is a rapidity parameter and is unrelated to the
root's three-component composition vector. Define

\[
\mathcal D_\zeta=\zeta^2+5+2k\zeta(\zeta^2-1),
\tag{P37}
\]

\[
\boxed{
\ell(\zeta)=\frac{(\zeta^2-1)
[5(\zeta^2+1)R_0-4\zeta r_0]}
{2\mathcal D_\zeta},\qquad
\xi(\zeta)=\frac{\ell(\zeta)}{\mathcal E},}
\tag{P38}
\]

\[
\boxed{
\theta_+(\zeta)=
\frac{3(\zeta^2+1)
\{R_0[\zeta-\tfrac k2(\zeta^2-1)]-r_0\}}
{\mathcal D_\zeta},\qquad
r_+=r_0+k\ell(\zeta).}
\tag{P39}
\]

Together with \(n_H^+=D/\gamma\), \(p^+=(2/3)n_H^+\theta_+\), these
are explicit rational functions of \(\zeta\). Direct substitution gives

\[
E_{\rm EOS}^+=D(R_0+\ell),\qquad
M_{z,{\rm EOS}}^+=D\ell,\qquad
E_{\rm EOS}^+-M_{z,{\rm EOS}}^+=D R_0,
\tag{P40}
\]

and \(r_+-r_0=I\xi\).
One derivation is to solve the two linear equations

\[
\ell=(r_0+k\ell+\Gamma\theta_+)\gamma v,\qquad
R_0=\gamma(1-v)[r_0+k\ell+(1-\kappa v)\theta_+]
\tag{P41}
\]

for \(\ell,\theta_+\). The resulting gas momentum is exactly the full
absorbed photon momentum, and its total energy includes the chemical
rest-energy increase.

For every \(\zeta>1\), \(\mathcal D_\zeta>0\) and \(\ell(\zeta)>0\):
\(\zeta^2+1\ge2\zeta\) bounds the bracket in (P38) below by
\(\zeta(6r_0+10\theta_0)>0\).
Furthermore, for \(1\le\zeta\le1/k\),

\[
F_\zeta=\zeta-\frac k2(\zeta^2-1),\qquad
F_\zeta(1)=1,\qquad F_\zeta'=1-k\zeta\ge0.
\tag{P42}
\]

The brace in (P39) is therefore at least \(\theta_0>0\).
Thus this whole parameter range has positive thermal energy.

The endpoint forward-beam Doppler factor is exactly
\(\delta_\gamma=\gamma(1-v)=1/\zeta\). Restricting

\[
1<\zeta<\frac{23}{13.60}<\frac{23}{\chi_H}=\frac1k
\tag{P43}
\]

places the gas-frame photon strictly above the HI activation and below
the HeI activation \(24.59\) eV, as well as below the provider upper energy
bound. It uses a direction-resolved axial beam. No azimuth-averaged
nonaxial direction is substituted for this beam.

### 7.3 Exact warm and composition restrictions; nonempty small-fluence interval

Add the explicit inequalities

\[
0<\xi(\zeta)<1-x_0,\qquad
\frac32 k_B[d_0+\xi(\zeta)]\,30000
<\theta_+(\zeta)
<\frac32 k_B[d_0+\xi(\zeta)]\,110000 .
\tag{P44}
\]

All terms in (P43)–(P44) are explicit rational functions of \(\zeta\)
and the fixed input constants. They define a finite, directly evaluable
positive reference family.
At \(\zeta=1\), \(\ell=0\), \(\theta_+=\theta_0\),
\(x=x_0\), \(T=T_0\); all nonzero margins in (P43)–(P44) are strict.
Continuity therefore supplies an interval
\(1<\zeta<1+\varepsilon_\zeta\) on which all conditions hold.
Every sufficiently small positive rational \(\zeta-1\) in this interval
gives an exact member, without a numerical parameter scan.

There is also a local physical derivative description. Since
\(\ell'(1)=r_0+\Gamma\theta_0>0\), the family can be parameterized
smoothly by \(\xi\) close to zero, and

\[
\left.\frac{dv}{d\xi}\right|_0
=\frac{\mathcal E}{r_0+\Gamma\theta_0}>0,\qquad
\left.\frac{d\theta_+}{d\xi}\right|_0=\mathcal E-I.
\tag{P45}
\]

The rest-temperature slope includes the new electron's particle count:

\[
\left.\frac{dT_+}{d\xi}\right|_0
=\frac{2\epsilon_{\rm eV}}{3k_Bd_0}
\left[23-\chi_H-\frac{3k_BT_0}{2\epsilon_{\rm eV}}\right]>0 .
\tag{P46}
\]

The exact inherited cgs decimal constants
\(\epsilon_{\rm eV}=1.602176634\,10^{-12}\) erg/eV and
\(k_B=1.380649\,10^{-16}\) erg/K make the bracket strictly positive.
The actual exact arithmetic record gives its value and does not infer
this slope from a fitted numerical trajectory.

### 7.4 Constructing an actual positive endpoint absorption increment

For any member satisfying (P43)–(P44), use the endpoint proper lower
density and the actual cross-section function:

\[
n_{\rm HI}'=\frac D\gamma(1-x_0-\xi)>0,\qquad
\lambda=c\,n_{\rm HI}'\,
\sigma_H(23/\zeta)\,\frac1\zeta>0.
\tag{P47}
\]

This is the root's invariant event normalization specialized to one
forward beam: \(\lambda=c n_{\rm HI}'\sigma_H(E_\gamma')\delta_\gamma\).
Equivalently \(\lambda=cD(1-x_0-\xi)(1-v)\sigma_H(23/\zeta)\).
The endpoint opacity is evaluated at the actual endpoint; no initial
temperature, fraction or Doppler rate is frozen.

Given any \(h>0\), choose zero photon injection and lab photon densities

\[
N^-=\frac{D\xi(1+h\lambda)}{h\lambda}>0,\qquad
N^+=\frac{D\xi}{h\lambda}>0.
\tag{P48}
\]

Then exactly

\[
N^+=\frac{N^-}{1+h\lambda},\qquad
h\lambda N^+=D\xi=N^--N^+.
\tag{P49}
\]

The same event count in (P49) generates (P35).
Thus the family can be lifted to a finite backward-Euler photon/HI
absorption reference, with the specified incoming photon inventory.
It is not a claim that arbitrary prescribed incoming inventories, or
the full CI/RR/DR-inclusive provider, give this same closed-form endpoint.
At fixed admissible \(h\), the incoming inventory and absorbed fluence
both tend to zero with \(\xi\).

## 8. Equal-pair reference and continuous imbalance limit

Start from (P33)–(P34) and absorb \(D\xi/2\) photons from each of
\(\pm\mathbf e_z\), each with energy \(23\) eV. The exact endpoint is

\[
\boldsymbol\beta^+=0,\qquad \gamma^+=1,\qquad n_H^+=D,\qquad
x^+=x_0+\xi,\qquad r^+=r_0+I\xi,
\tag{P50}
\]

\[
\theta^+=\theta_0+(\mathcal E-I)\xi,\qquad
E^+=D(R_0+\mathcal E\xi),\qquad \mathbf M^+=0.
\tag{P51}
\]

Define

\[
T_{\rm exc}=\frac{2\epsilon_{\rm eV}(23-\chi_H)}{3k_B}.
\tag{P52}
\]

The exact temperature is the weighted average

\[
\boxed{T^+=\frac{d_0T_0+T_{\rm exc}\xi}{d_0+\xi}.}
\tag{P53}
\]

With the inherited constants,
\(T_{\rm exc}=72733.757372464264931\ldots\ {\rm K}\), and hence
\(50000<T_{\rm exc}<110000\) K. Therefore every
\(0<\xi<1-x_0\) gives a strictly warm reference between
\(T_0\) and \(T_{\rm exc}\), with positive proper density and valid
gas-frame photon energy. The two endpoint opacities are equal because
\(\gamma=1\), their energies match, and the absorber is isotropic.
Use (P48) separately with \(D\xi/2\) to obtain equal positive incoming
and surviving counts. The pair has zero absorbed momentum but a
strictly positive energy and ionization increment.

For a continuous link to an unbalanced distribution, fix a small total
\(\xi>0\) and let the two absorbed counts be
\(D\xi(1+\eta)/2\), \(D\xi(1-\eta)/2\), with \(-1\le\eta\le1\).
Then

\[
E^+=D(R_0+\mathcal E\xi),\quad
M_z^+=\eta D\mathcal E\xi,\quad
a_r^+=D(r_0+I\xi).
\tag{P54}
\]

The exact cone margin is

\[
\begin{split}
\frac{\mathcal C^+}{D^2}
={}&\theta_0(2r_0+\theta_0)
+2\xi[(r_0+\theta_0)\mathcal E-r_0 I]\\
&+\big[(1-\eta^2)\mathcal E^2-I^2\big]\xi^2 .
\end{split}
\tag{P55}
\]

The worst cone margin at fixed \(\xi\) occurs at \(|\eta|=1\).
It is positive on a nonempty interval of small positive \(\xi\),
uniformly for \(\eta\in[-1,1]\). Together with continuity and the
strict initial warm/domain margins, this supplies a common small
interval of admissible unbalanced references.
The inverse in (P21) is smooth in \(m^2\), so thermal quantities are
even in \(\eta\) and tend smoothly to (P51)–(P53) as \(\eta\to0\).
At a fixed composition and energy, \(C_s<0\) also shows exactly how
increasing momentum leaves less thermal energy than the equal pair.

For the single-beam endpoints \(|\eta|=1\), a direct explicit
cone-only upper bound on the event count is

\[
\begin{split}
A_0&=\theta_0(2r_0+\theta_0)>0,\\
B_0&=2[(r_0+\theta_0)\mathcal E-r_0 I]>0,\\
\xi_{\rm cone}&=\frac{B_0+\sqrt{B_0^2+4I^2A_0}}{2I^2},\\
0\le\xi&<\xi_{\rm cone}.
\end{split}
\tag{P56}
\]

It follows by solving \(A_0+B_0\xi-I^2\xi^2>0\).
The practical reference set intersects this bound with the composition,
warm and Doppler restrictions; it does not extrapolate a cross section
past its domain.

## 9. Constructive scope and exact-check record

The global cone theorem is a specialized rederivation of the known gamma-law
admissibility result (Wu and Tang 2015, Lemma 2.1). This contribution supplies
its project-specific application together with the positive-term
scalar inverse and derivative bounds, the smooth inverse/forward-Jacobian
connection, finite binding-aware cone identities, and the explicit warm
absorption references. The parent scalar photon elimination, event ledger,
reference-mass convention and accepted geometry work are reused under their
existing assumptions.

The exact check input is
[PRIMITIVE_EXACT_CHECK.wl](PRIMITIVE_EXACT_CHECK.wl), preserved before its
single actual Wolfram call. Wolfram Language 15.0.1 on Linux-x86-64 returned
18 passing named groups: 17 algebra/derivative groups and one group of
exact decimal-as-rational warm-fixture inequalities. The kernel-reported
evaluation elapsed time was 0.169961 s. The actual evidence is
[raw response](../evidence/PRIMITIVE_WOLFRAM_RAW_RESULT.json),
[normalized results](../evidence/PRIMITIVE_EXACT_RESULT.json), and
[execution context](../evidence/PRIMITIVE_EXECUTION_CONTEXT.json).
The warm fixture also evaluates the bracket in (P46) as the exact positive
rational
\(392341742281692686411/133514719500000000000\) eV,
or \(2.9385654536891169248\ldots\) eV.

The check program performs exact differentiation and rational identities;
positivity, bijectivity, warm continuity and finite-step domain claims are
proved above. A successful identity check does not stand in for those
proofs. The 18 named groups are counted once within this contribution.
If the root also executes the same forward-Jacobian factor identity,
the joint unit registry counts that mathematical group once.

No numerical parameter scan, native build, chemical RHS, ODE history,
new atomic fit, abundance-source law or independent species velocity is
part of this contribution. The pending PRIMARY_PROVIDER_03 coding owner
remains the first implementation dependency. The moving-source inverse and
references define additional implementation obligations after that owner;
they do not mark an existing scalar runtime as a moving-gas solver.
