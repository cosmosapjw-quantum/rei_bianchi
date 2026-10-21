# Independent response-fit addendum — PASS

The descriptive joint fit and six heldout mixed predictions reproduce from the existing complete history CSVs. This is a narrow postprocessing review: **no ODE solves, full raw-audit repetition or reopening of the numerical gate**.

The independent calculation uses actual initial `(sqrt(3)*s/H, signed_Pi_m, signed_Pi_r)` and actual final `sqrt(3)*s/H`. Training consists of625 original rows plus600 new matter rows, totaling1225 unique cases. The25 historical reference rows are not added again, and all6 mixed cases are excluded from fitting.

The zero-intercept coefficients are:

- initial signed shear: 0.11438019418589546;
- initial signed matter stress: 0.11914730406637555;
- initial signed radiation stress: 0.24184661410997463.

Maximum training absolute residual: `3.7067612774230665e-07`. Training RMS residual: `9.0259575439290182e-08`. Maximum absolute prediction difference on the6 genuinely heldout mixed cases: `5.9500572850484587e-08`. Radiation-to-matter coefficient ratio: `2.0298118871010691`. Each heldout residual also matches the controller's recorded value, up to floating-point ordering.

The stated interpretation is acceptable: these are empirical values on the finite chosen LRS domain. They do not provide a continuous, general nonlinear or general Bianchi closure bound, and fitted predictions do not replace the actual mixed coupled solves. The response ratio describes this fixed model and selected domain.

The frozen contract hash still matches the independently reviewed contract. The final review retains the implementation clarification: worker model/energy matrix reuse does not mean cached quadrature construction; original CanonicalMomentumFV objects and quadrature are reconstructed during amplitude inversion. No measured speedup or memory-reduction claim follows.

**The addendum closes with PASS; no further reviewer action is requested.** The prior PASS_SCOPED_PRELIMINARY and production NOT_ISSUED status remain unchanged.
