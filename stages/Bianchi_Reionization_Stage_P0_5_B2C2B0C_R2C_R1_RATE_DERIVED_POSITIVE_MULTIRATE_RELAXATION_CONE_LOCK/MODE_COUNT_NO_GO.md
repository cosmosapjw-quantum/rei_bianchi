# Mode-count no-go within the locked common-equilibrium model

## Assumptions

For one extensive family and one macro, suppose

\[
Y(t)=Y_\infty+\Phi(t)(Y_0-Y_\infty),
\qquad
\Phi(t)=\sum_{r=1}^{R} w_r e^{-k_rt},
\]

with `w_r>=0`, `sum_r w_r=1`, and every rate inside the prelocked interval
`k_-<=k_r<=k_+`, where `0<k_-<=k_+`. All modes share the same equilibrium
`Y_inf`. The endpoint time is `Delta t>0`.

## Proposition

The set of equilibria reachable at the fixed endpoint is independent of the
number of positive exponential modes. It is exactly

\[
Y_\infty=Y_0+a(Y_1-Y_0),
\qquad
a\in[a_-,a_+],
\]

where

\[
a_-=[1-e^{-k_+\Delta t}]^{-1},\qquad
 a_+=[1-e^{-k_-\Delta t}]^{-1}.
\]

Consequently, a Farkas certificate proving that no `a` in this box satisfies
the equilibrium cone cannot be repaired by adding a third, fourth, or any
finite number of positive exponential modes while keeping the same rate box
and common equilibrium.

## Proof

At the endpoint,

\[
Y_1=Y_\infty+\Phi(\Delta t)(Y_0-Y_\infty),
\]

hence

\[
Y_\infty=Y_0+rac{Y_1-Y_0}{1-\Phi(\Delta t)}.
\]

Because `Phi(Delta t)` is a convex combination of numbers in
`[exp(-k_+ Delta t),exp(-k_- Delta t)]`, it lies in the same interval. The map
`phi -> 1/(1-phi)` is strictly increasing for `0<phi<1`, which gives exactly
the stated `a` interval. Conversely, every endpoint attenuation in the
interval is already representable by a convex combination of the two endpoint
decays, so two modes span the full endpoint attenuation interval. Additional
modes can change the interior-time shape but cannot enlarge the equilibrium
box. QED.

## Application to R2C-R1

The equilibrium LP is feasible in 43/540 macro cases and infeasible in 497.
The two-mode kernel repairs the interior-time cone in 42 of the 43 feasible
cases, showing that mode shape matters after equilibrium feasibility. For the
497 Farkas-certified equilibrium failures, however, more modes are irrelevant
under the locked assumptions.

## Scope of the theorem

The proposition does not apply if any of the following changes:

1. rates are replaced by a new physically justified rate field outside the
   current lock;
2. rates vary deterministically by node rather than being macro-shared;
3. different modes have different equilibria;
4. the operator is non-autonomous or has explicit forcing;
5. families are coupled by a positive generator rather than relaxed
   independently.

Those are new model classes and require new pre-calculation locks. They cannot
be introduced as post-result repairs inside R2C-R1.
