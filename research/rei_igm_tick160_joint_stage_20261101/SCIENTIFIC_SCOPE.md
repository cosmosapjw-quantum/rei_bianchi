# REI IGM original [160,161] | full-parent stage inputs for a joint D_h certificate

2026-11-01. Source-locked parent: Draft PR334 HEAD cfb86457d859440cfd7bf103fcf6e2790b67907a, immutable original 26-event PR328 HEAD a85312cde63e5c0b0a7c0e5d182e79fe593bcf53. Reuse PR332's exact three-global-neutral-moment source Jacobian, PR337's within-step four-site instrumentation and Schur decomposition, PR339/340 exact finite source response, and PR341 Hessian. This is ONE focused nonproduction science attempt, not another point-parent scan and not a replacement for the original solver.

## Exact source mathematics, dimensions and common-parent requirement

Original species particle counts n_is (not spatial number densities) enter four photon groups through S_s = sum_i n_is, D_g = E_g + sum_s C_sg S_s, source r_isg = J_g C_sg n_is / D_g (events/s per node); C_sg includes original YHE, H/He owner-specific denominator and source cross sections. At a fixed original forcing clock (J, C, E unchanged), the exact full population Jacobian action is

    dr_isg = (J_g C_sg/D_g) [dn_is - n_is (sum_t C_tg sum_j dn_jt)/D_g].

The first numerator term is essential and was NOT present in PR332/337's denominator-only per-global-log-moment columns. For finite perturbations let v = delta D / D0 and L_isg = (J C / D0)(delta n_is - n0_is*v). When D0, D1 > 0,

    r(n0+delta n)-r(n0)= L / (1+v),
    R_source = -(v/(1+v)) L.

Over any positive rectangular outer source state box, let rho=max |(D_{lo/hi}-D0)/D0|, kappa=max |(D_{lo/hi}-D0)/D_{lo/hi}|. Then with n0 inside that box,

    |R_isg| <= (J_g C_sg / D0) (delta n_is,max+n0_is*rho) kappa.

This is exact in REAL arithmetic at a single fixed-forcing source site. The implemented numpy/longdouble evaluation is only a FLOATING-POINT NUMERIC ESTIMATE; it is not guaranteed-outward MPFR/MPFI interval arithmetic and cannot be used to certify the full F05 gate.

## Genuine original whole-uncertain-parent calculation, not representative-parent stepping

The new source-authenticated execution reads the unchanged original tick160 accepted interval state on 46,080 nodes, its 26-event MPRK22(1)/Alexander SDIRK2 map and the original proper clocks, preserving all three named shape lanes. It calls the unmodified original run_step on FULL original accepted X for full and first-half, then on its original first-half interval image for second-half. A passive event_box wrapper records final parent, predictor, gamma and final source-evaluation inputs for each map; repeated outer iterations overwrite intermediate gamma/final records. At each of these 12 original map sites it computes source rates, source-only remainder estimates over the ENTIRE inherited stage-population interval box, original primary source-energy rates and original interval-source inclusion. It also evaluates the *original frozen-photoheat partial thermal root derivative* in log T. Original fourth-group subnormal photon current is retained as an explicitly unresolved source group, not interpreted as physical photon rate.

No production history advance is attempted; only [160,161] is inspected. Source-site expansion-point particle numbers conserve each node's immutable original H and He nuclei, but that point is solely for representing a whole-BOX source bound and not a claimed reachable history.

## Precisely missing mathematics: full common-parent/source four-site D_h

Let w=(X,Theta) with one shared Theta containing the original forcing uncertainties, and let the augmented maps carry Theta unchanged. Then J_D = P(J_F-J_G2 J_G1) and the second directional derivative obeys

    D''[u,u] = P(F''[u,u]-G2''[G1'u,G1'u]-G2' G1''[u,u]).

For a differentiable implicit-stage residual R(z;w)=0 with invertible R_z,

    z'=-R_z^{-1} R_w u,
    z''=-R_z^{-1}(R_zz[z',z']+2 R_zw[z',u]+R_ww[u,u]).

At a fixed smooth Hummer-Seaton branch, if the only nonlocal population dependence is through the 3 original photon moments PER source evaluation, an augmented site-residual Jacobian has local-block plus low-rank form A+B V^T; its Schur complement must be validated over the WHOLE original X×Theta. In a three-step combined residual with four evaluation sites per step, 36 is a possible *lifted moment-coordinate dimension*, NOT an established rank or invertibility certificate of the actual code.

The current original thermal-root function differentiates with the photoheat interval held fixed. Its positivity alone does not prove that the *coupled* photoheat/population/temperature outer-root Jacobian is invertible. Table-event/Hummer-Seaton nonsmooth branch partitions and their certified bounds are also required. None are replaced by this experiment's source-only remainder.

Therefore the only admissible original first-interval outcome until those universal bounds exist is BLOCKED_MINIMUM_STEP. Historic separate-output upper 2.1245050576368385e-4 > original local error 2e-4. Public width gate 2e-3 unchanged; no physical admission can be inferred from small point-parent defects.

## Execution and claims

Run new workflow using original pinned requirements, tests ordinary and optimized, original archived source SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, state numerical SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01, unchanged source 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644. A failed underlying map or positive-derivative test remains a failure or partial diagnostic, NEVER silently PASS. No committed science data claim until actual CI and file readback.

Central 28/88_REPORTED; Working 33/88_REPORTED; Fast 4/7_REPORTED; canonical delta 0. PRODUCTION HOLD; NO_MERGE; NO_FORCE_PUSH; NO_TOLERANCE_RELAXATION; NO_BUDGET_RESET; AUTO_NEXT_NODE=false. Native subagent NOT_RUN because no delegation tool; distinct-author blind review NOT_RUN. Remote desktop offline. Same-author scoped algebraic tests are not independent external certification.
