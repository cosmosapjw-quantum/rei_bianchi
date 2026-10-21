# Independent contract review: PASS_SCOPED_EXTENSION_CONTRACT

Reviewer: `/root/pilot_independent_review`, requested independent Astra role. Developer context identifies GPT-6 Astra Pro; no additional runtime model telemetry. The reviewer implemented no solver and ran no expanded campaign. This record captures the prior scientific recommendation and verifies the frozen `CONTRACT_KO.md` against it. **No blocking mismatch was found.**

## Agreed finite scope

Decompose all 625 saved histories without new ODE integration. Add 600 nonzero matter-initial-stress cases, explicitly reference 25 original neutral controls for the companion zero axis, and solve six mixed initial-cancellation cases. The new scientific sweep therefore contains 606 trajectories. Four new original-source comparisons are a separate validation gate; old completed science and validation are preserved.

The components live in the common comoving orthonormal frame: `pi_i=diag(-p_i,-p_i,2p_i)`. With the original half-contraction norm and `K=8*pi*G/c²`, retain signed `Pi_m` and `Pi_r`, their magnitudes, and `Pi_total=abs(signed_Pi_m+signed_Pi_r)`. Adding component magnitudes is generally incorrect. Pressureless non-tilted dust has zero anisotropic stress; the matter contribution comes from the canonical massive species. Combining photons and massless neutrinos is valid under their identical collisionless energy initial data.

Saved `massive_pi_s_norm`, E2, H and x already determine both components. Use `p_m=rhocrit0*(fm*Omega_m/a_ref³)*M_pi_s` and `p_r=rhocrit0*(Omega_r/a⁴)*E2/3`; preserve original raw files and check component-sum reconstruction over every saved sample.

## Actual static attainability evidence

Original-helper evaluation at Sigma0=.004 gives signed initial matter Pi approximately `-0.0004833821888780246` for A_m=-1 and `+0.0009667643777560494` for A_m=2. These are the positivity boundaries of `W_m=1+A_m P2`. A symmetric +/-0.001 axis is unavailable under the frozen model. The contracted +/-0.0004 range is feasible, requiring maximum |A_m| approximately `0.8275025625756662`. Actual-helper inversion and realized-axis checks, without changing mass/fraction/tolerance, correctly enforce this boundary. Mixed radiation cancellation requires only |k| approximately .189466, within the original .5 limit.

## Original controls are references, not new executions

The 25 neutral controls can be reused under the 1e-12 physical-axis tolerance when their original identity, old k, actual component axes and history locations remain explicit. Mark them REFERENCE_REUSE and do not manufacture a new resume or execution identity. The inspected saved isotropic control has signed matter Pi0=0 and signed radiation Pi0=`1.4928082245968736e-19`, equal to its saved total. Scalar and batched helper roundoff can distribute negligible offsets differently; actual saved values govern the decomposition. This is tolerance-based reuse and does not assert exact-zero or bitwise equality.

## Sufficient new validation

The four contracted signed `(Sigma0,Pi_m0,Pi_r0)` comparison cases are `(+.004,+.0004,0)`, `(-.004,-.0004,0)`, `(0,+.0004,-.0004)`, and `(+.004,-.0004,+.0004)`. They cover both massive amplitude signs, pure and mixed stress, and zero/nonzero shear. Compare original40 and reduced8 histories at 65 samples with the existing 1e-8 absolute observable threshold, including separately signed components; source H² residual remains <=2e-13. Two massive directional-energy checks at opposite amplitude signs, <=1e-7 relative, plus all new initial-axis, finite-energy/H, canonical population and sampled-brightness diagnostics are sufficient for this finite-model extension. Repeat old closure/tolerance campaigns only in response to a material new discrepancy.

The saved actual Wolfram output agrees with the half norms, cross contraction, anisotropic work and exact formal constraint cancellation. It is formal algebra, not a numerical global certificate.

Initially matter-isotropic and radiation-isotropic labels refer to the initial slice; each component can develop stress during coupled evolution. Mixed cases must be solved as coupled histories, not reconstructed by adding separate trajectory responses. General non-LRS closure, native H/He feedback, global positivity/full convergence, production admission and benchmark claims remain outside scope.

**Next executable action:** lower-tier implementation and the frozen bounded validation/sweep. Independent final acceptance will inspect the new implementation and actual raw component results; this contract PASS is not an assertion that those unexecuted results have passed.
