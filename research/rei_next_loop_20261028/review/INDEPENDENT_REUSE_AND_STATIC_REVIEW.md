# Independent scoped review of REI continuation

Reviewer task: `/root/review28`. Requested review tier: Astra. Observed backend model: unknown; no runtime model identity is inferred from the requested tier. This reviewer does not author the implementation. Review scope is read-only source/equation inspection, with this report as its only authored artifact. No scientific code, tests, hash suite, plotting, packaging, provider or IVP has been run by this reviewer.

**Current final decisions:** old finite-caloric unit `PASS_SCOPED_CLOSURE_BY_REUSE`; new mathematical derivation `PASS_SCOPED_CONDITIONAL_BRANCH_AND_UNCERTAINTY_DERIVATION`; new first executed branch/calibration evidence `PASS_SCOPED_EXECUTED_REPRESENTED_BRANCH`. The preparation-only statements below describe the earlier review phase and are superseded for the observed run by section C. Physical REI admission and original DAG completion remain unchanged.

## A. Existing evidence reuse

The original unit is `finite_thermal_endpoint_20261028` at REI PR240 pin `b77c7b8d45c48a7e4722e733309430d5ba668b0d`. I read the pinned AGENTS policy, unit CONTRACT, R5 derivation, native post-disclosure R6/C9 report, bounded F1 closure, governing correction, and post-review source-delta selection. The preserved reports are being reused as prior independent evidence; I have not repeated their full source audit or re-executed their computations.

The governing F1 correction defines `delta_theta = theta_a - k_src*T_native` and gives

`T_a^E/T_native = k_src*EV_src/k_B_SI + delta_theta*EV_src/(k_B_SI*T_native)`.

This follows directly from `T_a^E = theta_a*EV_src/k_B_SI`. The correction retains the actual nonzero represented product residual. Its bounded native finding-closure report explicitly admits R6 as `PASS_SCOPED_R5_AND_CORRECTED_SOURCE_REPRESENTATION` and preserves C9 as `PASS_SCOPED_REPRESENTED_INPUT_AND_FROZEN_SOURCE_DIAGNOSTIC`. No new F1 repair or replay is needed.

R7 may adopt C7 and both distinct C8 evidence sets under the same representation and source assumptions. Those two C8 sets are one stage and one shared source dataset, not two independent physical datasets. Their relevant discrimination is that direct subtraction of rounded endpoints loses information, whereas transporting residuals retained before rounding uses a different information set. The count-margin examples are synthetic conditioning examples. Neither these examples nor source residuals supply a physical error radius.

Native review supports the constant-caloric common-volume map, source gas-slot ownership, one application of work, declared inert-He source bath and represented-source diagnostics. It does not admit recipient EOS, recipient normalization, coupled feedback, native25, physical temperature updates, or physical radii. Historical He-branch reconstruction remains a coverage limitation. The separate BASS restart result cannot replace the frozen source or create physical error radii.

The selected R7 question is identity- and assumption-matched evidence adoption. I read the original workflow 1.0.0 `THEORY_LOOP.md` and `CODING_LOOP.md` stage definitions and the new `theory/FINITE_THERMAL_CLOSURE.md`. The synthesis performs the remaining duties: R7 adopts the discriminating saved evidence; R8 makes the corrected scoped decision; R9 states the result, physical interpretation and next implementation connection; R10/C10 preserve original identities, existing commands/results through their source references, unresolved obligations and the next unit. The author made one minimal provenance correction requested here: the final native R6 disposition and `FINDING_CLOSURE_R6_C9.md` now accompany the earlier post-disclosure report. This closes the documentation finding; it changes no science.

**Old-unit decision: PASS_SCOPED_CLOSURE_BY_REUSE.** The scientific content supports closing R7–R10 and C10, hence old-unit 20/20 after the controller's scoped adoption. The native R6/C9 two-stage increase already occurred before this continuation; only these five remaining stages are new closure work here. Actual publication/backup acknowledgements remain separate delivery evidence. No new computation or further old-unit review is required. New general-EOS implementation remains outside the closed finite-caloric runtime evidence; R5 §7 was expressly a theoretical result.

## B. New general-EOS adapter

I read the new `theory/THEORY.md` and `theory/EOS_BRANCH_CONTRACT.md`. Equations (1)–(5) are supported by independent algebra/order inspection:

- On each positive-slope affine segment, substitution proves the inverse and membership in that segment. Shared knots give identical endpoint values. Summing the increments across knots proves the global secant bound with `m0=min(si)>0`; differentiability at knots is not needed.
- Under the supplied uniform discrepancy, `F_*(T0)<=F0(T0)+eta<=Elo` and `F_*(Tn)>=F0(Tn)-eta>=Ehi`. These give existence on the caller's bracket, while continuity and strict monotonicity of actual `F_*` give uniqueness. Bounding `F0(T_*)` then gives the widened-energy inverse interval with the stated signs.
- The radius combines three distinct energy terms, `abs(F0(Tbar)-Ebar)`, `eE`, and `eta`, then divides by the nominal positive slope bound. It is conditional on an actual same-bracket solution, not a standalone existence certificate. No actual-EOS derivative lower bound is silently inferred from `m0`.
- Constant shifts `F_*=F0±eta` attain the two interval endpoints for the unconstrained mathematical family. This supports the stated mathematical sharpness without claiming correlated or physical sharpness.
- The composition-discrepancy line-integral bound is valid when the derivative bounds apply along the whole connecting segment. The affine energy transformation scales numerator and slopes together, preserving temperature and radius. A shifted energy zero may make energies negative without invalidating the monotone inverse.
- In the manufactured nonlinear case, `F0(T)-T^2=(T-1)(3-T)` lies in `[0,1]` on `[1,3]`, and energy 4 yields enclosure `[3/2,2]` containing the exact root 2. This provides a different mathematical check from the ideal quotient; it is not astrophysical EOS data.

**Theory decision: PASS_SCOPED_CONDITIONAL_BRANCH_AND_UNCERTAINTY_DERIVATION.** No mathematical correction is indicated. Literature and remote-CAS descriptions are treated as the author's contextual support, not independently reverified evidence or premises of these proofs. The local mathematical review does not need a new CAS or numerical run.

### Static implementation and authored-test review

I read complete `implementation/caloric_branch.py`, `test_caloric_branch.py`, `run_saved_caloric_branch.py`, `suite_once.py` and `run_once.py`, including the targeted repaired portions. I did not import, compile or execute them. The equations were reviewed before the new code/test read; this is a distinct-author static review, not a source-data-blinded new runtime review.

`CaloricBranch` validates explicit exact input representations, positive increasing temperatures and strictly increasing energies. Negative energy ordinates remain admissible under an energy-origin shift. Its exact segment choice covers interior points, shared knots and the two endpoints; clipping only the segment index does not extrapolate a temperature or energy. Out-of-image values are rejected before the inverse. `enclose_energy` implements the two expanded endpoints with the correct signs. `residual_radius` uses the global nominal minimum slope and keeps unknown bounds unknown.

One minor contract discrepancy was found and repaired by the implementation author: a missing uncertainty term previously caused early return before rejecting a negative or floating-point partner term. The repaired function validates each supplied bound first, then returns unknown if its partner is missing. The author added four targeted authored fixtures for negative/float values paired with a missing term. Inspection closes this static finding. Those regression fixtures remain NOT_RUN and are not represented as executed evidence.

The principal test oracles are fixed rational values independently specified in the theory contract: branch values, inverse(7)=3, interval [2,3], radius 5/4, endpoint shifts, energy-origin/scale covariance and the nonlinear square-law inclusion. These do not merely compare two calls to the same implementation. Round-trip and covariance comparisons add useful structure checks, while the fixed values prevent those checks from being the only oracle. Boundary tests cover monotonicity failures, out-of-domain values, reversed intervals, negative radii and forbidden float inputs. No count of tests is used as scientific admission.

The source calibration reads only the preserved C7 stdout at its original byte/SHA identity and takes exact `reconstructed_endpoint` U/N/cv/T fields. It builds a declared ideal-law calibration branch, compares the new inverse with an explicitly assembled quotient and the saved T, and never imports the old consumer or reruns the producer. Its zero eta/eE basis is explicitly represented-law calibration; physical uncertainty, recipient temperature, native25 and full-state update remain null/false. Source arithmetic residuals are not used as physical error radii. The caller still owns the physical EOS, branch, store/reference-volume match and any physical discrepancy certificate.

The combined suite runs manufactured tests before one saved-source calibration. The wrapper requires a separate controller authorization/approval record, binds exact authored files and command, preserves the corrected prior lower debit, records measured child and supervisor portions separately, and leaves whole-command accounting explicit. Static inspection is not a claim that signal delivery, failure handling or resource ceilings have been exercised. This review grants no execution authority.

**Implementation decision: PASS_SCOPED_STATIC_PREPARATION.** The prepared exact-rational implementation corresponds to the reviewed contract after the one targeted validation repair. No unresolved current-scope static defect was found. Tests, combined saved-source calibration and runtime/resource behavior remain NOT_RUN. This does not close new-unit C6–C8 or grant a new runtime/scientific PASS. The next executable action, when separately authorized, is the already prepared single bounded combined suite; the current stopping point needs no additional review framework.

## Claim and resource boundary

Original DAG remains working 33/88 and central last observed 28/88, canonical delta zero. `L4_ready=false`; global physical completion and physical outputs remain null. New preparation does not increment original DAG completion without its original gate.

The prior planning partial lower bound 16.323598885 CPU s and the separately recorded closed F1 checker debit 0.026759 CPU s combine to a known lower bound 16.350357885 CPU s, counted once. The former planning cap was 16. Presentation partial lower bound remains 48.263016494 CPU s (old cap 47), with unmeasured cost unknown rather than zero. The wrapper floor now retains that combined planning lower bound. Main policy remains `NO_MORE_IVPs`. This report creates no execution allowance and no claim of runtime verification.

Subsequent controller message reports new explicit user approval: planning absolute cap 18 CPU s, one attempt reserve 1.5 CPU s, worker at most 1 CPU s, 10 s wall, 256 MiB and no retries. Static preparation GO was sent for that bounded combined command. This records the controller's new authority separately from the earlier preparation-only state; runtime evidence is still pending at this point.

## C. Targeted review of the single newly approved execution

After the reported explicit user approval and preparation GO, the implementation author supplied the first combined execution records. I read `execution/attempt01/RESULT.json`, `stderr.txt`, empty `stdout.txt`, `saved_source_result.json`, `execution/OUTER_WAIT4_RECEIPT.json`, and the final `execution/ACCOUNTING_CORRECTION.json`. I also read the final wrapper's localized distinction between resource signals/stops, execution failures and incomplete observation. No existing computation was repeated and no new verification code was executed by this reviewer.

The result records one combined command, zero retries, exit 0, terminal wait4 usage observed and no stop reason. Its exact source-file identities and approved command are recorded in the authorization and observed result. Each of the six distinct manufactured test methods records `ok`, including the repaired missing-peer bound validation. The acceptance basis is the independently specified rational assertions already reviewed, together with these actual outcomes; the method count itself proves nothing about physics.

The saved result explicitly preserves C7 byte length 19293 and SHA256 `2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948`, exact U/N/cv/T operands and the nominal branch knots. The saved T, inverse T, independently assembled ideal quotient and both endpoints of the zero-uncertainty represented interval have identical exact numerator/denominator records. The radius is exactly 0/1 under the stated represented-law eta=eE=0 basis. Physical eta/eE, recipient temperature, native25, physical interval/radii and global physical completion are null; full-state update and L4 readiness are false. This is the intended new code route on unchanged saved source operands, not a new source history or physical EOS calibration.

### Resource observation and bounded accounting correction

The inner worker CPU is 0.062480 s and supervisor pre-record CPU is 0.041805 s. The outer direct-child wait4 observation is 0.113551 s, inclusive of the waited nested worker on this Linux path; outer observer CPU is 0.023059 s. Therefore the observed outer pre-receipt total is 0.136610 s without adding the inner worker again. Observed outer pre-receipt wall time is about 0.122355 s. The raw receipt's 0.199090 label had counted that worker twice; the preserved additive accounting correction identifies the error and governs interpretation. It neither changes scientific output nor warrants a rerun.

The observed quantities fit comfortably inside the approved reservation. Final receipt/startup and other unmeasured overhead remain `UNKNOWN_NOT_ZERO`; this is not an exact whole-pipeline CPU total. Adding the observed 0.136610 s once to the prior known lower bound gives 16.486967885 CPU s. If the controller additionally charges the 0.1 s final-tail reserve, the charged ledger is 16.586967885 CPU s. That second number includes a reservation and must not be labelled a measured CPU lower bound. The temporary ceiling is restored under the existing policy while the accumulated debit is retained.

### Final executed-scope disposition

**PASS_SCOPED_EXECUTED_REPRESENTED_BRANCH.** The supplied exact-rational branch inverse, conditional enclosure/radius, authored edge controls and one preserved-source ideal-law calibration have actual first-run support corresponding to the inspected code and derived equations. The targeted findings are closed; no additional code repair, old-suite replay, new provider run or extra review gate is indicated.

This evidence supports the new unit's implementation/science/numerical checks within its exact represented arithmetic scope and closes the pending fresh independent review of those results. It supports no performance comparison, uncertain astrophysical EOS accuracy, physical recipient update or coupled thermal trajectory. Final result adoption and delivery can proceed under the controller's already authorized workflow; original DAG gates and physical nulls remain intact.

## D. Final figure and claim consistency

I visually inspected `delivery/eos_branch_four_panel.png` once and read the figure's source-to-panel mapping in `delivery/figure_caloric_branch.py`, its receipt, and the final `ADMISSION.json`, `REPORT_KO.md`, `STAGE_LEDGER.json` and `HANDOFF_KO.md` for obvious scope mismatch. I did not rerender or rerun scientific code. The SVG was not separately rendered by this reviewer.

Panel A shows the declared manufactured knots `(1,2),(2,4),(4,10)` and expanded energy interval `[4,7]`, mapping to `[2,3]`. Panel B correctly displays the nonlinear manufactured square law, its secant and the enclosure `[3/2,2]` with root 2. Panel C reads the preserved exact saved-source result, places the calibration point at normalized `(1,1)` and displays about 3003.4175 K. Its full diagonal is an illustration of the normalized ideal caloric law, including the mathematical origin; it is not an extrapolated implementation result or a physical time history. The actual calibrated point lies inside the supplied `[1,10000] K` bracket. Panel D preserves working 33/88 and central 28/88.

The rendered labels and curves are legible, and the footer explicitly retains missing actual recipient EOS/physical radii/completion. The final adoption, stage ledger and handoff agree with the reviewed scope, distinguish old/new unit closure from the original DAG, and distinguish scientific completion from pending provider delivery acknowledgements. No scientific or visual correction is required for this figure. Publication and preservation may continue without another review cycle.
