# Equation–code and execution contract

| Formula | Function / role | Validation |
|---|---|---|
| P=pI+qD; p=(2X+Y)/3, q=(Y-X)/3 | invariants | cone, vacuum, subnormal equal-pressure edge |
| THEORY Eq6, Q=j=0 | rhs | energy and ratio identities |
| THEORY Eq11 | step | independent CAS, collisionless/collision-only, semigroup, stiff/projector cases |
| exp(A(tmid)dt) product | advance | analytic variable drift and independent noncommuting CAS refinement |
| THEORY Eq9 plus temperature term | thermalLedger | separate expansion/shear/particle/temperature ledger |

All arguments use SI units. nu is nu_pi, the pressure-anisotropy decay rate.
The positive source-free propagator does not integrate heat, chemical changes,
magnetic dynamics, gravity feedback or a calibrated multispecies operator.

The ECMAScript core has no imports and is executed as its exact source text in
functions.exec's V8. It also exports CommonJS when a Node module is present.
The Node module-loading/CLI path must be smoke-tested on an available host;
this turn's shell service failed before Python/C++/Node execution could start.
No scientific result depends on that unrun wrapper.

Finite nonnegative inputs and forward time are required. Explicit errors cover
unrepresentable scaled rates and final pressure under/overflow. Signed s and H
are permitted. The vacuum branch returns exact zero after input validation.
There is no clipping, hidden rate substitution, external package or random input.

The invariant pressure e,piF must be representable. Very small q/p has the usual
binary64 cancellation floor; no relative accuracy claim below that floor.

Validation is bounded to manufactured mechanical problems. A convergence gate
near second order applies to smooth prescribed functions sampled at midpoints.
No uniform stiff-order claim or runtime speedup benchmark is made.

Resource budget: one current V8 process, finite scalar loops, no NCP, no original
HE32 IVP calls, no plots. Existing source/provider/campaign evidence is reused.
