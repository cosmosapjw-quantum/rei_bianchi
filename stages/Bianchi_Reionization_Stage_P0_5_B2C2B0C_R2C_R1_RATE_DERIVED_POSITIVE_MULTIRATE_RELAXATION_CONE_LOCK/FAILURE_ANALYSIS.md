# R2C-R1 failure analysis and adversarial alternatives

## Primary failure

The dominant blocker is not timestep convergence. It occurs before time
integration: 497/540 macro-shared equilibrium boxes are empty. Every empty box
has a self-contained Farkas ray, and an independent validator reconstructs the
ray algebra from emitted columns and right-hand sides.

The obstruction is highly localized by physical sector:

- 491 radiative-current/cycling failures;
- six macro mass-cap failures;
- zero Farkas failures from `I>=0`, `I<=M`, `U>=0`, or basic `C>=0`.

Thus the next model change should target rate heterogeneity and the coupled
current/capacity structure, not the already-closed ionization/thermal
bookkeeping.

## Why more modes are not the next move

A positive mixture with the same common equilibrium changes `Phi(t)` inside an
interval but leaves the endpoint equilibrium in the same attenuation-inverse
box. `MODE_COUNT_NO_GO.md` proves this for any finite number of modes. The
observed two-mode behavior agrees: it repairs all 42 one-mode trajectory
failures among equilibrium-feasible cases, but it is skipped for the 497 empty
equilibrium boxes because it cannot enlarge them.

## Coarse-refinement failures

Sixteen analytic passes fail only the two-step discrete cycling-cone check.
Every one passes at four and eight steps. This is a real warning against using
the coarse discretization, but it is secondary: even a perfect integrator
cannot remove the 497 equilibrium no-go cases.

## Dual-guided diagnostic, not calibration

For each single-row Farkas certificate, the stage computed the smallest
one-coordinate extension outside the normalized attenuation box. The result is
stored in `data/dual_single_bound_extension_diagnostic.csv` and is explicitly
non-authorizing.

- G1 nonnegativity: median finite one-coordinate upper-rate factor `6.98`;
- G2a nonnegativity: median finite factor `4.04`;
- cycling capacity: median finite factor `1.17`, but 97 best one-coordinate
  repairs would require `a<=1` and therefore no finite positive scalar rate;
- macro mass cap: required factor range `1.489--1.510`.

Widening the rate lock to match these numbers would be circular. They instead
identify where new independent physical evidence is required.

## Adversarial alternative A: macro averaging is the actual culprit

R2C-R1 deliberately shares one rate per family across all 2,560 nodes of a
macro. The inherited inputs contain node-local density, temperature, transfer,
current, opacity, and capacity. A deterministic local rate field derived from
those quantities is not the same as unconstrained node-by-node fitting. It is
the least-complex model extension and must be tested before introducing a more
flexible coupled generator.

A credible local law must use a small, prelocked set of macro-level
hyperparameters or no fitted parameters at all. The node dependence must come
from explicit process formulas. If a changing node has no positive physical
rate evidence, it is `UNIDENTIFIABLE_REQUIRED_RATE`; it is not assigned a
convenient rate.

## Adversarial alternative B: independent scalar families are structurally wrong

Even a deterministic local scalar rate may fail because the cone
`J_G1+J_G2a<=C` couples three variables. The natural positive coordinates are

\[
q_\gamma=(R,J_{G1},J_{G2a})^T,
\qquad R=C-J_{G1}-J_{G2a}\ge0.
\]

A physics-derived Metzler generator and nonnegative forcing preserve this
orthant by construction. Similarly, the mass cap can be represented by
`q_M=(M,M_cap-M)`. This coupled-generator route is authorized only after the
node-local rate-field preflight shows that deterministic local scalar rates
remain insufficient; otherwise it would add unneeded degrees of freedom.

## Adversarial alternative C: inherited rate evidence omits a process

The current `J_g` evidence uses endpoint secants and local/macro absorption
turnover, while the full radiation ledger may also contain source injection,
redshift-boundary flux, and capacity regeneration. The next stage must audit
all inherited terms before declaring a rate unidentifiable. Any added term
must be sourced and dimensionally checked before feasibility is examined.

## Claim boundary

R2C-R1 proves a no-go for the locked macro-shared common-equilibrium model. It
does not prove that no physical node history exists. It also does not license a
production history, a node-wise fitted rate field, rate-box dilation, clipping,
or an ad hoc generator.
