# REI AX03 C9: actual native driver physical-clock integration and adversarial audit

Date 2026-10-15 KST. Selected physmath coding C9. This is real executed theory, native Rust source changes, source-bound tests, floating-clock counterexample, local CPU/performance and resume safety. Native subagents NOT_RUN (host tools absent), local Codex NOT_USED. The original owner checkout /home/cosmosapjw/Dropbox/bianchi/rei_bianchi was inspected read-only, not edited. The changed branch is an isolated research worktree on top of REI PR123.

## Defect, affected physics and minimal native fix

Original rei_microphysics/src/axbi_driver.rs Driver::tentative did:

    dt = background.point_at_scale(to).time_s - background.point_at_scale(old.a).time_s

At elapsed proper time ~1e16 s, two source-correct cumulative Simpson4096 values can lose the physically significant local dt. This dt feeds photon injection, H/He chemistry, thermal energy and event ledgers. It is not a mere output presentation problem.

The exact stress-free LRS AX03 source formulas, with signature (-,+,+,+) and fixed signed source q_ref=0, +/-0.005, +/-0.01 and q=.01 SAME_H diagnostic:

  H_F(a)^2=H0^2*(Omega_m/a^3+Omega_r/a^4+OmegaLambda)
  s(a)=q_ref*H_F(aref)*(aref/a)^3
  H(a)=hypot(H_F,s) for density-fixed, H_F for SAME_H
  delta_t=integral [log(a0),log(a1)] dx / H(x)
  delta_b=integral dx s(x)/H(x)

Use physical binary64 endpoints delta_x=log1p((a1-a0)/a0). Source-bound 4-point Gauss-Legendre normalized weights over panels of width <=0.0028 in x, cache H_F(a_ref) per interval, source-equivalent s, Kahan accumulation and strictly positive clock, with real-domain guards. Native module rust/rei_microphysics/src/axbi_background.rs adds local_increments(a0,a1) returning (dt,db), and proper_time_increment(a0,a1). No external dependencies, no heap allocations in the integration loop. The actual science Driver::tentative now calls background.proper_time_increment(old.a,to), NOT a subtraction of huge accumulated times. This is a deliberate new numerical version with the same physical model and unit conventions. Absolute times in output/checkpoints continue using the old source cumulative origin and representation.

New science output metadata declares background_time_increment=local_source_GL4_log1p_from_actual_scale_endpoints, and warns not to mix historical saved science. No atomic source, no H/He reaction law or photon collision/closure was changed.

## Actually verified independent science

The prior independent MP80 physical reference contains 90 exact-binary64 source-locked interval pairs for six real/diagnostic families across a0=.05/.1/.18, widths 1e-4,1e-8,1e-10,1e-12,nextafter. Real rustc/Cargo Rust local GL4, actual physical AxbiBackground source rather than an interpreted Python toy:

- 90/90 cases match independent MP80, maximum dt relative difference 2.220446049250313e-16, maximum db relative difference 4.440892098500626e-16.
- q=.01, a0=.1, a1=nextafter(.1,+inf): new dt=3.5706700623663608 physical seconds. Original native Simpson4096 cumulative time subtraction gave 6 seconds, a relative error ~68.04%. The preceding Python accumulated-time comparison returned 4 seconds; the two distinct cumulative algorithms have different rounding errors, both untrustworthy for short steps.
- Source q sign parity, q0 zero shear, SAME_H counterfactual separation, positive domain, NaN/inf/reversed input and full-scale interval test all pass.
- A real Rust source admission test invokes run(config,out,"ZERO",resume=true) with a fake previous source_identity.txt and NO checkpoint present. run returns AXBI_RESUME_IDENTITY before attempting checkpoint reads. This is not just a line-search assertion.
- Old REI background-table proof already had a stable, source-bound Hermite increment with sampled max relative difference 2.3826052242270634e-11. Its original native trial callsite still used cumulative time subtraction, and 356 SHORT_STEP_SUBTRACTION_HOLD cases existed. This branch fixes that callsite only. It does not invalidate old scientific source data or automatically clear the historical empirical benchmark's record.

Wolfram 15.0.1 independently verified all first 8 Gauss4 monomial moment residuals zero (degree<=7), positive normalized GL weights sum to 1, physical mean constraint H^2=H_F^2+s^2 zero residual. For signed q, H^-1=H_F^-1 - q^2*S^2/(2 H_F^3) + 3q^4*S^4/(8 H_F^5)+O(q^6), S(a)=H_F(aref)(aref/a)^3; it confirmed even-q parity and the q² coefficient exactly. This explains fixed-a clock drift but does not equate fixed-a HII difference to fixed-proper-t HII difference.

## Source identity and readback gates

Normal native run explicitly compares saved source_identity.txt with compiled_identity before calling read_checkpoint. The identity contains original driver + background source bytes and multiple physics contracts; new source differs from original. The normal run therefore refuses an old clock algorithm checkpoint. Low-level public Driver::read_checkpoint alone is NOT a source-identity admission interface and must not be used to bypass run. Existing checkpoint V2 string syntax was retained to avoid rewriting previous records; numerical compatibility is governed by compiled source identity, not the unchanged text header. A real negative test covers this.

## Actual on-host Rust performance and parallelism

Release-built native benchmark on 90 same source input intervals:

  old uncached double-Simpson4096 time subtraction ~0.0199514 s median
  new direct physical source Gauss4 serial ~0.000010199 s median
  2 std::thread workers ~0.000091563 s median
  4 std::thread workers ~0.000112813 s median

Old native cumulative subtraction relative error >1e-8 on 70/90 pairs, vs new max 2.22e-16. Thus the new correct scoped *clock component* is ~1956x faster than the incorrect uncached old direct Simpson pair. This is not a whole-REI H/He ODE speedup, not a comparison against the pre-existing cached Rust Hermite background_table_001, and not a claim of full scientific HII convergence. The physically correct fast default is serial, since actual two and four workers ran slower and yielded bitwise identical outputs. New method has constant O(1) integration-loop memory.

After source modification, native targeted tests for original AX03 background, AX03 driver, photon q-reference, q-event, q-closure and resource continuation pass, plus the new C9 native MP80 and negative guards. Scientific source and numerical checkpoint identity must remain explicitly separated.

## Scope and next selected stage

C9 physical callsite defect: FIXED_ON_ISOLATED_NATIVE_BRANCH, scoped mathematical and actual native implementation tests PASS. Original owner checkout and active science solver processes untouched. Original signed AX08 history/checkpoints cannot be resumed under the new numerical source; no new full production scientific trajectory was run. Global interval-arithmetic error bound, full Einstein–Boltzmann radiation anisotropic stress, actual cold H/He numerical AX11 convergence and final EoR publication admission remain HOLD.

Next C10 is ready but not executed. Only a future source-controlled scientific run may adopt this new algorithm with its own valid config, source byte identity, clock interval tests and failure/audit ledgers. Keep release as Draft PR, do not merge main automatically or rewrite native historical signed outputs.
