# Independent scientific review of completed bounded unit

Reviewer: `/root/physics_start_audit`; 2026-10-29. Independent source/result inspection, with no test, solver or rendering re-execution. Reviewed `implementation/validation_driver.py`, updated `start_audit.py`, frozen RHS and derivative sources, and `outputs/main_structural_20261029/{JACOBIAN_VALIDATION.json,START_AUDIT.json,ATTEMPT_RESULT.json,FINAL_RUSAGE.json,FAILED_TIME_LAUNCHER.json}`. The test result is embedded in JACOBIAN_VALIDATION.json; there is no separate TEST_RESULTS.json.

## Admission

**PASS_SCOPED** for the source-origin audit, analytical frozen-RHS Jacobian construction and completed fixed-field structural validation under its recorded driver criterion. **PENDING** for actual saved-bath linkage and rendered visual validation. No original DAG node, full physical source Jacobian or anisotropic evolution is admitted by these results.

The derivative adapter was previously matched independently against exact source `coupled.py` blob 4773d4278e1fa2f1a8a24a9df79f9ba5d46d5771. The execution driver verifies that blob and the event-model/config blobs, AST-extracts the unchanged RHS and event compiler, and uses the actual compiled event matrices. It deliberately supplies synthetic constant G, nref=1e-5 cm^-3 and hidden_dot=0. Real saved ON_refined states/scales are evaluated under those fixture coefficients in both modes. Accordingly the result correctly says `SOURCE_COMPILED_FIXED_FIELD_STRUCTURAL_VALIDATION_NOT_SAVED_BATH` and `saved_bath_linkage: MISSING`. OFF evaluations at ON_refined states are legitimate derivative probes; they are not OFF trajectory validations.

Six mode/state records cover OFF and ON at saved indices 0, 180 and 360. Each contains three directions and two step sizes: 36 directional checks total. All driver checks passed, as did two zero-state polynomial checks, six capture-gradient checks, and three plot-contract unit tests. Maximum recorded baryon/charge derivative residuals are approximately 1.14e-16 / 1.37e-16, zero ledger feedback columns are exact in every record, and the largest recorded scale-transform discrepancy is 2.465190328815662e-32. The largest recorded raw directional absolute discrepancy is 1.4429082928479886e-13. These are reported outputs inspected here, not independently recomputed values or universal error bounds.

## Acceptance-criterion distinction

One provenance distinction is material. The older proposal `intake/github/JACOBIAN_CONTRACT.md` specifies a 1e-7 relative directional criterion where resolvable and ledger residual <=5e-13. The executed driver uses componentwise `error <= 1e-6*(abs(J)@abs(v)) + roundoff_allowance` and ledger <=1e-12. Root explicitly confirmed to this reviewer that the latter criteria were selected, sent to the coding agent and accepted BEFORE execution GO. Accordingly the older proposal is **SUPERSEDED_BY_ROOT_PRE_EXEC_CONTRACT** for this unit, not an unmet execution gate. This is a pre-execution criterion selection, not a result-dependent relaxation. The acceptance provenance timing is root-supplied; the actual criterion and outputs were directly inspected. The effective contract should preserve that root message/GO binding alongside the historical proposal. No claim that the older directional criterion was tested is made, and no additional postprocessing or rerun is needed for the scoped admission. The actual ledger residuals are visibly far below both thresholds.

The driver's `64*eps` roundoff term is a practical floating-point allowance for these short event sums, not a proved interval enclosure. Central differences have zero analytic truncation error for this quadratic RHS, while finite-precision subtraction remains present. The exact derivative claim is supported by direct differentiation/source matching; the fixture checks are additional numerical evidence within their stated scope.

## Curve-onset result and repaired schema handling

The updated audit correctly asserts 23 physical state arrays and iterates only `physical[:17]` for the plotted heavy states. The previous 17-array assertion was incorrect and the earlier pre-execution review did not catch it. The two-line correction was inspected here and its executed result covers the intended 17 states, avoiding accidental inclusion of fast stocks, energies or ledgers.

The resulting ON_refined audit matches the prior independent raw-CSV/metadata read: 361 saved times, ten initially zero states, and all 17 first positive-time indices equal to 1 at 0.08238295318127252 seconds and rounded mean z=20.0. The nine omitted-positive counts are T I 57, T II 48, He3 II 84, He3 III 155, He4 II 79, He4 III 150, Li7 I 160, Li7 III 106 and Li7 IV 160. Their old first-visible indices are respectively 58, 49, 85, 156, 80, 151, 161, 107 and 161. These are visibility thresholds, not physical species-start times. Neutron and the seven initially positive states have no positive points below the old overview window.

Three successful plot-contract tests support early positive-range inclusion, signed common limits and top-tick spacing. No new plot was rendered; actual figure appearance remains pending the separately approved presentation attempt.

## Execution and accounting

FINAL_RUSAGE records exit code 0, final child CPU 0.21412799999999999 seconds, wall 0.21534485499796574 seconds and max RSS 33800 KiB. The initial `/usr/bin/time` command failed before the scientific child started because the executable was absent; its shell cost remains explicitly UNKNOWN. The root-authorized wait4 launcher repair uses the same 4-second reservation, and no IVP retry occurred. The completed child's cost does not erase the unknown failed-launch cost.

The 620-second temporary main ceiling and restoration to original 600 are recorded. Parent accounting reports a full reserved debit 608.750604 -> 612.750604, a measured-child subtotal 608.964732 and 3.785872 seconds retained reservation difference. Preserve both the measured subtotal and conservative reserved accounting rather than treating the difference as an unrecorded fresh allowance. Presentation ceiling 70 still requires its distinct owner approval; this scientific execution does not confer it.

The root reports a 3-second Wolfram TimeConstrained angular-integral attempt returning `$Aborted`. It is an attempted check, not validation evidence; no CAS rerun is requested. The existing analytical angular-moment proof remains the basis for the quadrupole selection and shear-monopole coupling statements.

## Remaining scope

Publishable now: the source-scoped derivative adapter, explicit structural fixture/output evidence, curve-origin audit, analytical coupling derivation, and prepared plot implementation with pending-render status. Remaining scientific dependencies are actual donor-bath recovery/linkage, source-qualified self-consistent physical Jacobian, tangent initial/boundary conditions and anisotropic controlled evolution. Remaining presentation work is the separately authorized one-attempt render plus inspection. Original working33/88, central28/88 and physical-fast4/7 counts remain unchanged.
