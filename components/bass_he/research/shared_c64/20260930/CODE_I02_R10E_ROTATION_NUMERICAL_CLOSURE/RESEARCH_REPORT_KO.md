# BASS_HE R10E research: numerical closure of the Coulomb rotation adapter

## 0. Starting state

R10D correctly stopped before producing five-lane science results because the
precommitted fixed-resolution gate

\[
\max |P_{128}-P_{256}| \le 10^{-7}
\]

failed in three low-energy combinations. The worst difference was
\(4.6718423847291746\times10^{-6}\) for \(N=3,l=2\), author cutoff, 0.5 keV/u.
Unitarity and stochasticity remained at roughly \(10^{-13}\), so the failure was
accuracy/convergence, not structure preservation.

R10D's unresolved verdict is preserved. This research loop does not retroactively
relax its gate or admit the five-lane comparison.

## 1. Exploratory extended-resolution replay

Using the exact archived R10D adapter and the same fixed 105 rho nodes, a ChatGPT
research sandbox replayed all 12 block/energy/cutoff combinations at 256, 512, 1024
Magnus steps. This replay is explicitly outcome-informed and not independent.

All 12 combinations satisfy max|P512-P1024| < 1e-7. The worst is the same low-energy
N=3,l=2 author-cutoff combination: 2.5050147844929427e-8.

For the three originally failed combinations, the observed orders between 256->512
and 512->1024 are approximately 3.99, 3.91 and 3.90. Extending only those three to
2048 steps gives 1024->2048 differences 9.03e-11, 7.53e-10 and 1.60e-9, again near
fourth order.

## 2. Independent integrator spot audit

The same research sandbox independently integrated the full gauge ODE with SciPy
DOP853 (rtol=1e-12, atol=1e-14) at each combination's worst node.

Across all 12 combinations,

max |P_Magnus,1024 - P_DOP853| = 1.7024043286184565e-9.

The worst node is the smallest fixed rho=0.0381283839609398 at 0.5 keV/u,
N=3,l=2, author cutoff.

DOP853 is an auditor only. It does not replace the unitary Magnus propagator.

## 3. Interpretation

The evidence favors a simple diagnosis: R10D stopped in a pre-asymptotic /
under-resolved fixed-step regime for the strongest low-energy small-rho rotational
blocks. The failed differences decrease monotonically, fourth-order behavior emerges,
unitarity/stochasticity remain excellent, and an independent high-order ODE solver
agrees with Magnus-1024.

This is diagnostic evidence, not a global stiffness theorem.

## 4. Wolfram / Richardson check

For an order-p method with asymptotic error C h^p, successive step-doubling differences
fall by 2^p. For p=4 the ratio is 16 and the finest asymptotic error is the last
difference divided by 15.

Starting from the original worst 128->256 difference, pure fourth-order scaling predicts
256->512 = 2.92e-7 and 512->1024 = 1.82e-8. The exploratory observed value
2.51e-8 is consistent with this scale.

## 5. New bounded numerical contract

The next execution must be a new contract, not a reinterpretation of R10D.

Keep the original probability tolerance 1e-7. Change only the predeclared resolution
sequence to 256,512,1024.

Require all 12 combinations and all 105 nodes to satisfy:
1. max|P512-P1024| <= 1e-7;
2. unitarity <=5e-13;
3. collapsed stochasticity <=5e-13;
4. the three originally failed combinations have observed order >=3.5 at the
   relevant pointwise worst node;
5. independently coded DOP853, rtol=1e-12, atol=1e-14, agrees with Magnus-1024
   within 1e-8 at one predeclared worst node per combination.

Because the contract was designed after exploratory results were seen, it is not
outcome-blind.

## 6. Five-lane continuation iff the R10E gate passes

If the new gate passes, resume the original R10D factorial experiment without changing
its scientific decomposition.

Use:
- straight-line lanes at validated 64-step research resolution;
- Coulomb lanes at 1024 steps;
- the same R10C exact Delta table;
- zero new contour/Stueckelberg solves;
- same fixed 105-node GK15/GK7 replay;
- no adaptive quadrature refinement.

Then compute SL_CPC, SL_AUTHORCUT, COUL_CPC, COUL_AUTHOR,
COUL_AUTHOR_FROZEN and the original cutoff/trajectory/interaction decomposition.

## 7. If the extended gate fails

Stop R10E_ROTATION_NUMERICS_UNRESOLVED. Do not increase steps indefinitely.
Next options would be defect-based/adaptive Magnus, close-encounter reparameterization,
then only later a different exponential integrator. DOP853 remains an auditor.

## 8. Gate

CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
