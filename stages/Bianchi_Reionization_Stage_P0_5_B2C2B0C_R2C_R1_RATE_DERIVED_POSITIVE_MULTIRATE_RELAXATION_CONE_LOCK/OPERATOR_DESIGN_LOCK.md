# Operator design lock

For each macro and family `f`, the one-mode path is

`Y_f(t)=Y_f,inf + (Y_f,0-Y_f,inf) exp(-k_f t)`,

with `k_f>0` shared by all 2560 nodes of that macro. The endpoint equation fixes

`Y_f,inf = Y_f,0 + (Y_f,1-Y_f,0)/(1-exp(-k_f Delta t))`.

Writing `a_f=[1-exp(-k_f Delta t)]^-1`, every asymptotic cone inequality is linear in the six variables `(a_M,a_I,a_U,a_C,a_J1,a_J2)`. The stage therefore uses a bounded linear feasibility problem, not node-wise fitting. A feasible solution minimizes normalized equilibrium extrapolation subject to the cone and rate-box constraints. HiGHS primal/dual marginals are stored; infeasible systems receive an independently solved normalized Farkas certificate.

The full finite-time path is then certified. Individual positivity follows from positive endpoints and equilibrium. Coupled neutral and cycling slacks are exponential polynomials. Their interval enclosures are recursively bisected; an interval whose lower enclosure is nonnegative is certified, while an unresolved interval at depth 24 fails closed.

A two-mode kernel may be evaluated only if the one-mode equilibrium box is feasible and the finite-time cone fails. Its rates are fixed to the prelocked lower/upper family bounds. The positive weight is determined by the one-mode endpoint attenuation, so it adds no post-hoc rate freedom. If the one-mode equilibrium LP is infeasible, the two-mode equilibrium region is identical and is skipped by theorem.
