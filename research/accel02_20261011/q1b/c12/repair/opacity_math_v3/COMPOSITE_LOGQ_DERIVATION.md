# Bounded composite log-q quadrature for the unchanged positive closure

The accepted continuation reached generation60, then attempt67 failed in cell66 even after the former128/256 probability rule: the preserved own-component heat errors are8.107858431290887e-6 at64/128 and2.4062745412590576e-7 at128/256, both against1e-7. The old candidate correctly failed closed. Repeatedly changing only a global probability order would leave the nearby inverse-CDF singularity unresolved as the reconstructed power-law steepens.

This note derives the selected new fallback: threshold-split composite positive Gauss quadrature directly in x=ln(q/a), with each panel satisfying |p|*Delta_x<=4 and a maximum128 panels. It retains the same source, native cross sections, moment closure, fitting and response gates. The ordinary old API is used first; only the documented INCIDENT_ORDER_PAIR case enters this versioned fallback. It does not run an unbounded retry ladder.

## Same measure, better coordinate

For the existing interior power-law reconstruction, the photon-number measure is

dM = N*exp(p*x)*dx/Z,    0<=x<=L=ln(b/a),
Z = integral_0^L exp(p*x)dx.

This is exactly the measure represented by the old inverse CDF. No new closure, power-law exponent or moments are introduced. For a response K(q),

integral K(q)dM = N/Z * integral_0^L K(a*exp(x))*exp(p*x)dx.

Use physical threshold splits q_i=E_i/R strictly inside(a,b), mapped to x_i=log1p((q_i-a)/a). Within each threshold piece, divide into n_i=max(1,ceil(|p|*Delta_x_i/4)) panels. If the sum exceeds128, stop before opacity calls; do not discard a tail, increase the cap silently or reinterpret the event as zero density. For p=0 no exponent-driven extra panel is needed.

On every panel, the exponential source factor changes by at most exp(4). The inverse-CDF branch point no longer appears in the numerical coordinate. Native sigma and its heat-weighted forms are smooth on each threshold side; the discontinuity remains a true panel boundary. This does not create a universal finite-order error theorem, since attenuation can add nontrivial curvature, but it removes the concrete inverse-CDF conditioning mechanism observed in attempts66/67.

## Positive weights and exact represented moment binding

For positive Gauss weights w_j on a log-q panel with Jacobian h_j, form logarithmic base weights

log W_j = log(h_j*w_j)+p*(x_j-x_ref),

where x_ref is chosen at L for p>0 and at0 for p<0. Normalize with log-sum-exp (equivalently subtract the largest log weight before exponentiation). This common scaling cancels analytically and prevents overflow without changing the distribution. Every retained weight must remain strictly positive and finite; underflow is a reported failure, not permission to remove nodes. With the bounded p*panel-width policy, large total dynamic range is explicitly budgeted rather than hidden.

Retain the old global exponential moment fit on xi_j=(q_j-a)/(b-a):

P_j = N*W_j*exp(eta*xi_j)/sum_k W_k*exp(eta*xi_k),

where eta is solved so sum_j P_j*xi_j/N equals the unchanged represented target (mean_q-a)/(b-a). The target must lie strictly inside the node convex hull. Use the existing positive normalization, bracketed root,1e-12 number/energy/cell-relative mean fit and exact state inputs. No mean shift, positive floor, threshold displacement or node at a support endpoint is allowed.

The old moment-fitting consistency argument still applies. For finite p and strict-interior moments the continuous tilted mean has derivative Var_eta(xi)>0. As the underlying positive Gauss integrals converge, eta tends to0 and the fitted measures approach the same continuous power-law measure. Moment fitting cannot by itself certify opacity or heat; their separate own-component order comparisons remain mandatory.

## Common attenuated measure and unchanged gates

Construct coarse/fine64/128 rules **per declared log-q panel**, then retain the same prepared-measure API. Sigma is evaluated by the unchanged pinned native provider at E_j=R*q_j. Surviving and absorbed photons use the existing factor

P_j^+ = P_j/[1+h*c*sum_i(n_i*sigma_i(E_j))].

The same positive P_j, sigma values and denominator generate N, U, species K0/KE, direct heat, absorbed counters and paired energy. Thus the existing positivity and photon/energy pairing identities are preserved. Threshold crossing, exact-threshold equality, support endpoint and native-domain guards remain in force. Chemical chi stays distinct from sigma's threshold.

Acceptance still requires original1e-7 own-component incident and attenuated64/128 differences, original1e-12 moment fit and pairing, direct-vs-ABI heat checks and every downstream gas/original-IC ledger/domain gate. Exact-zero reference components require exact-zero differences. Reaching the panel cap or failing the composite pair is a terminal localized numerical failure for this policy, not a trigger for another silent order increase.

## Why not only geometric probability panels?

Geometric probability panels are mathematically consistent. For negative p, with branch point v*=1+delta, enforcing panel width <=v*−v_right yields a mapped singularity x*>=3 and favorable local analytic separation. Positive p has the corresponding near-zero-endpoint construction. However, delta can become smaller than binary64 spacing at v=1, making final probability panels/nodes unrepresentable even though log-q remains a regular coordinate. A direct log-q formulation avoids this additional representation limit and requires only O(|p|L/4) bounded panels. This is a numerical coordinate choice, not a change of physics.

## Evidence scope and remaining limitations

This mathematical lane read the saved attempt67 refinement receipt and immutable implementation; it executed no source integration, SIGMA, native gas, whole map or old test. The implementation owner supplies exact-cell diagnostics and candidate execution evidence separately. The128-panel cap and64/128 policy must be fixed prospectively in the new numerical identity before trajectory continuation. No speedup or full-history scientific admission is inferred from this derivation.

The method has a consistency argument and concrete safeguards, not a rigorous1e-7 continuum certificate or uniform bound for every possible later p, gas state and h. The actual pair gates and subsequent full-history time/spectral refinements remain necessary. Even successful local fallback only licenses the new continuation under its declared allocation and durable checkpoints.
