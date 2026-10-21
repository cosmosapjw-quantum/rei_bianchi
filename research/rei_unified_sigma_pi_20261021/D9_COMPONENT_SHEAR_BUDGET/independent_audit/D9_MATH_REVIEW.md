# D9 independent physical and mathematical review

Status: PASS for frozen analytic identity and sampled-data analysis design. Numerical implementation and figures await the same bounded review pass.

Requested model: gpt-6-astra. Observed runtime model identity: NOT_VISIBLE. Fresh delegated context; no recursive delegation. Applied PhysMath Research Loop 1.3.0 R6/C9 and integrated policy.

Source read directly: EXECUTION_CONTRACT.md; original adapter.py observables; components/component_adapter.py components; vendor/canonical_fv.py fields/rhs; vendor/species_hierarchy.py fields/rhs; actual intake_remote/D8_RESULT.json. No source imports, ODE calls, or moment recomputation.

The saved s has proper-time inverse-second units and H>0. adapter.py uses K=8*pi*G/c^2 and signed component Pi_F_signed_X=sqrt(6)*K*p_X/H^2; component_adapter maps P_m to the matter quantity and P_r to gamma+nu. The source RHS in x gives ds/dx=-3s+K*(p_m+p_r)/H, using the critical-energy normalization K*rho_crit=3*H0^2. Thus S=sqrt(6)*s/H obeys S'=-(3+H'/H)*S+P_m+P_r. This sign and normalization agree with the frozen contract, including the full Frobenius shear norm sqrt(6)*abs(s)/H rather than the source's half-norm sqrt(3)*abs(s)/H.

For M=exp(3*(x-x_i))*H/H_i, M'/M=3+H'/H, M(x_i)=1, M>0. Product differentiation yields (M*S)'=M*(P_m+P_r). The integrated identity Q=S_i+I_m+I_r follows without division by S; it is regular at S=0. All normalized quantities and the dx integral are dimensionless. At a zero, S'=P_tot and dS/dz=-P_tot/(1+z); a simple zero produces a cusp in abs(S), not a physical singularity. Initial shear plus signed component integrals is accounting on each solved coupled trajectory; changing component initial data changes the geometry and other sources, so these pieces do not define independent counterfactual solutions.

The sampled-data approximation is only the integral quadrature. The frozen per-case residual scale protects zero and near-zero trajectories; endpoint Simpson/trapezoid differences are sensitivity diagnostics, not an error certificate. The prescribed quadratic weighted-source, source-free decay, exact cancellation, and grid-rejection controls target the new transform/quadrature surface. No widening of the gate or additional IVP is warranted by this review.

D8 authoritative adjacent index pairs read from actual result: (135,136), (141,142), (144,145), (147,148). Endpoint signs are positive then negative. The local residual requirement abs(R)<0.1*abs(Q), together with reconstructed sign agreement, is essential before budget-resolved bracket interpretation. Case c retains nominal zero initial matter stress with actual small nonzero stored value and historical worker exit 124; recovery status describes data validation, not solver success. These provenance limitations are distinct from the new scientific residual checks.
