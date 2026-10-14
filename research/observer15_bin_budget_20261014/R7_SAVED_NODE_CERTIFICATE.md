# OBSERVER15 R7: same-source saved-node and observer-bin time certificate

2026-10-14 KST. Actual next stage R7_SAME_SOURCE_SAVED_NODE_RESIDUAL_BINDING from R6 commit7782c0fd819400ae9e06a97e283d72779ddfc40c. The existing PR115 branch was read at that exact head before this additive publication. No R5/R6 overwrite, main merge, production activation, source ODE or historical scientific-suite replay.

## Complete executable research payload

- Name: REI_OBSERVER15_R7_20261014_SOURCE.zip
- Size:236530bytes;49members,48manifest payload files.
- SHA256:3524a7e6b5211c268222bd6ef1af108e35d23ff23330fb116c741afdcff70eaa.
- [Full Korean proof, immutable source inputs, tested code and actual evidence](https://drive.google.com/file/d/1_y0StgG8NmfFnfKf0YD-r2sxfCv3Wm1v/view?usp=drivesdk).
- Drive ID1_y0StgG8NmfFnfKf0YD-r2sxfCv3Wm1v; existing parent1zzbClTE3qzz8gaiQwopXJqVk9ZGBawYZ. Actual upload and name/ID/size/parent readback matched. Local CRC/all48payload hashes verified. New Dropbox backup and remote full restore not performed.
- REPORT_KO.md SHA256:a0d6c584f0c8e003124f4f6c4e4087f82866d5d65d624e0460361f8e5c97222b.

Git contains this substantive result/restore entrypoint. The complete executed code, full24-equation proof, input CSV and all100cell/101node bounds are inside the immutable archive rather than expanded into Git.

## Exact mathematical target

Recovered original SHEAR12 ZIP776788bytes SHA2563b275b00a9542f34a1e4075c7eb1ab8f7248a63e65226d4be40756a5789b2ce9. Original source SHA25650d2bbd8d6dd4c3a60c34644297041adb5a55ba0ab03bf8f96978a8e819456ba. Unchanged101-node CSV SHA25669bceac64e356d202c4cc4cb8c3db35d9e37c632df7d37bc6219f7c53a696927.

The archived code defines Gauss-Legendre32 on q in[65,110]eV with normalized q^2 exp(-q/20) photon weights summing to0.7. Historical internal q/weight raw bytes were not archived. The certificate targets the exact-real mathematical Gauss32 definition, with all32 roots enclosed by exact rational sign brackets and exact positive Gauss weights. It does not claim restoring historical internal array bytes or certifying the continuous-energy quadrature. The saved curve is arbitrary approximate input; its earlier arithmetic error is covered a posteriori against this mathematical source.

Use signature(-+++), u=t/t_star, H*t_star=.04, k0=.4, Y=.08, r0=(.9,.076,.004), thresholds(13.60,24.59,54.42)eV, amplitudes(1,2,4), slopes(3,5/2,7/2). Keep c and physical units. This source's gas/photon subsystem is independent of thermal energy; no new thermal/atomic approximation is inserted.

## Analytic lift and whole-cell defect

Let r=(h,z,v), xi=1+2Y-h-2z-v. Set A_aj(u)=c_aj exp(beta_a u), beta=(0,-.02,.02), c_aj=.4 amplitude_a(threshold_a/q_j)^p_a. The exact source is

    F_j'=-kappa_j F_j, kappa_j=sum_a A_aj r_a,
    M_a=sum_j A_aj F_j,
    r'=(-h M_H,-z M_1,z M_1-v M_2).

Build a C1 cubic Hermite reference rhat through the unchanged gas nodes with the saved alpha columns defining endpoint slopes. The slopes need not be exact true derivatives. Recover photons WITHOUT time stepping:

    J_a(u)=integral_0^u exp(beta_a s) rhat_a(s) ds,
    Fhat_j=w_j exp(-sum_a c_aj J_a).

The photon residual is exactly zero. The gas defect is R=rhat'-f(rhat,Fhat). On each of100cells, evaluate its midpoint quadratic Taylor coefficients with directed Decimal80 and bound the complete third derivative of the RHS. For v=A Fhat:

    v'''/v=(beta-kappa)^3-3(beta-kappa)kappa'-kappa''.

Combining this with exact cubic derivative bounds and sum Fhat<=.7 yields whole-cell bounds, not maxima inferred from samples. Maximum cell l1 defect<4.636010841e-13. Exact exponential-polynomial integrals use an explicit Taylor tail. All source inputs, divisions, roots, exp/sqrt and propagation are outward enclosed.

## Forward-error proof exploiting the actual source blocks

At fixed photons, the gas matrix is Metzler with column sums(-M_H,0,-M_2), hence its propagator is l1 nonexpansive. Photon loss is diagonal nonnegative. With e_r=||r-rhat||1, e_F=||F-Fhat||1:

    D+e_r<=C e_F+rho_i,
    D+e_F<=K e_r,
    C=hhat_max A_H_max+2zhat_max A_1_max+vhat_max A_2_max,
    K=.7 max A_a_max.

Actual upper constants: C=.01782339442137827122..., K=.60545256434663311962..., omega=sqrt(CK)=.10388079638597766130.... The comparison matrix is [[0,C],[K,0]]. Its cell transition is cosh(omega*h)I+sinh(omega*h)M/omega; the constant residual contribution is rho*(sinh(omega*h)/omega,(cosh(omega*h)-1)/C). Use the full outward values in RESULT.json, not rounded displays.

Initial gas mismatch is2.4173e-17; the lifted photons have the exact same initial weights. The source positivity/simplex and the reference positivity were verified. No assumption that the entire nonlinear chemistry is cooperative is needed. This is a forward-error bound, not residual control alone.

At u=.5:

    gas l1 error<2.062498156e-13,
    photon l1 error<3.185679985e-14,
    max saved xe-node error<4.125777901e-13.

The xe certificate includes the saved gas-to-xe arithmetic mismatch. Each actual CSV timestamp is also covered by adding .0588*|t_csv-i/200|. Its maximum timestamp difference is exactly3.55e-17; the maximum reported xe radius stays within the displayed bound. The rational-grid and timestamp semantics are retained separately.

## Actual observer coefficients and probability

Keep observer u=.5, near .25, far .20 and exact baseline redshift labels exp(.01)-1 and exp(.012)-1. Missing fixture tail is0. Keep r=sigma_T/sigma_star symbolic.

    C_bin=integral_.20^.25 .4 exp(-.12u) xi(u)du,
    C_near=integral_.25^.50 .4 exp(-.12u) xi(u)du.

The Hermite reference is integrated analytically; its dynamics error is bounded by .8*h*sum E_r(right_cell). Thus the intervals contain the true source-model coefficients, not only the interpolant:

    C_bin in[.00204512357395889456,.00204512357396664554],
    C_near in[.01011097644266596950,.01011097644272915924].

Hermite centers are.002045123573962770049944168... and.010110976442697564367998094.... Their respective dynamics radii are<3.875486001e-15 and<3.159486320e-14. Using this directly certified Hermite reference replaces the extra linear interpolation remainder; it does not assume cubic interpolation is exact.

The original linear pathway is also completed: add the real nodal bound to R5/R6's preserved curvature bound, yielding total bin time radius/r<1.771431344e-9 and near radius/r<8.857168937e-9. Both Hermite intervals lie inside those preserved linear enclosures. The center differences are reconstruction changes, not a different source evolution.

The passive cross-section-free column is C/sigma_star[m^-2], depth=r*C. Apply sigma_T once at depth level, then

    P(r)=exp(-r C_near)*(1-exp(-r C_bin)).

For normalized control r=1, missing tail0:

    P in[.00202248074816642495,.00202248074817421008].

Actual physical r, continuous-energy discretization, finite-epsilon response, provider accuracy and native consumer remain separate. This fixture needs no fabricated late cosmological tail to close its mathematical time certificate.

## Cross-repo and actual CAS checks

Read new HE44 R9 actual compact proof atdb92d431453a93913ba63e47d7ea92934ad11e20 and new CR55 full-source event compact proof sections1-5 at4abd195f1a3124e59b0fa498b446b590ef0116e5. Reuse the source-bound cross-section-free column and nonexpansive-block/defect separation. No CR center, event radius, HH rate or other source's certificate is transplanted. Current HH61 different continuum-model scope was read at PR metadata level. Existing BASS143 observer-measure conditions and REC source ownership retained. This is a connected six-repo update review, not all unpublished chat/local data.

Actual new evidence:
- Main interval computation205named checks PASS.
- Separate exact Rodrigues,120-digit antiderivative recurrence, direct positive convolution and arithmetic audit146named checks PASS. Forty residual samples are supplementary diagnostics; the analytic whole-cell bound is independent of sampling. Counts overlap in source/identity coverage.
- Cloud Wolfram15.0.1 confirmed19distinct scalar groups across original/diagnostic/targeted calls. One unsimplified algebraic zero caused initial JSON failure; targeted FullSimplify closed it. Infinity-limit warnings remain recorded. The formatted final replay was not run as one fresh combined command.
- Actual remote Wolfram15.0.0 with xTensor1.3.0/xCoba0.8.6:6new covariant-derivative/current contractions were zero, exit0. They verify normalized defect->proper-time current units, electron+photon accounting, error column and passive sigma. Exact submitted input SHA256d311106a7fe2a96e28399cc59ecea96ea3cfa688288882aa7b93dec7c5a5c244; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Raw JSON/exit and input/stdout byte matches preserved.

First interval z/v dependency overestimate was repaired by bounding their correlated sum before evaluation. Checker Decimal conversion and strict-versus-inclusive timestamp equality were repaired without changing model, bounds or physical tolerances. Original failures are preserved. No external independent scientific review or native subagents; no source ODE, old suite, HPC or native receiver execution.

## Next selected stage

R8_SCOPED_JUDGMENT_AND_CONSUMER_RETURN_SELECTION. Read the full REPORT_KO.md, RESEARCH_STATE.json, RESULT.json and AUDIT_R7.json. Same-source Gauss32 nodal and finite-bin time errors are now closed; do not return them to null or rerun completed ODE/atomic/R5/R6 campaigns. The default return candidate is the tighter Hermite coefficient interval, with the legacy linear enclosure preserved. Original SOURCE07-CONSUMER, global DAG, CR/RCT/HH OFF, BASS prelaunch provenance and physical-source/finite-epsilon/native duties retain their owners. Additive publication only; PR remains draft and unmerged.
