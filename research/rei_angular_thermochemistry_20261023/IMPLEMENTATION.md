# ANGTHERM01 implementation record

This record describes observed implementation mechanics; scientific admission belongs to the controller and independent reviewer.

## Source use and state layout

`vendor/c22/atomic_network.py` and its seven-file atomic dependency set remain exact copied bytes. The C22A model snapshot is attribution/reference only; it is never imported. The unmodified RR energy-moment provider is imported. The prescribed backgrounds are loaded from the copied NPZs with `allow_pickle=False`.

`code/angular_model.py` defines `Background`, exact fixed-q `geometry`, the 9-fraction optical-depth `Reduced` model, and independently assembled 21-scaled-population `FullOracle`. Shared functions contain source constants, background interpolants, and constitutive fits; `FullOracle.rhs` never calls or lifts the reduced RHS. It loops over every original isotope edge and computes its direct packet absorptions and RR event. The 8-copy representation retains signed directions. Its numerical Jacobian is supplied independently by SciPy.

The primary has 9 fractions, 6M optical depths, and eight scalar ledgers in this order: thermal energy, escaped energy, gas work, mean UV work, shear UV work, RR count, absorption count, Thomson optical depth. The full oracle replaces the 9 fractions by 21 scaled isotope populations and optical depths by 48M direct counts. Dimensions are 17+6M and 29+48M.

Initial fractions are extracted from the immutable `AtomicNetwork21.initial_state()`; the quotient checks equality between isotopes and rejects unequal data. Zero neutron/tritium inventories remain zero. Folded photons retain their integrated initial fixed-q weights without a second angular Jacobian. Photo coefficients are directly exponentiated in scaled log coordinates before multiplication by signed trial populations. The analytic Jacobian includes the common-temperature electron response and the derivative of the RR capture energy.

The 201-node raw backgrounds define Hermite b with saved s/H slopes, PCHIP log H, and nHref(0) exp(-3 eta). The actual tiny grid022 shear is retained. The sign-reversed case changes only b and its derivative. Each source-threshold and LiI provider-switch crossing is found by root finding with the adopted geometry. For a segment endpoint, only the cross-section energy uses an interior eta offset min(1e-12, segment-width*1e-8), with nextafter fallback; photon energies, directions and work remain at actual eta. This endpoint convention is recorded in each case JSON.

## Execution and evidence

`run_fresh.sh --prepare-only` verifies the 34 copied-file identities without starting an IVP. `code/algebra_checks.py` is the finite pure-algebra check suite. Its first authorized report is preserved at `checks_pre_ivp.json`; scientific execution reuses it instead of replaying unchanged checks.

`code/bounded_run.py` supervises the finite owner-authorized batches, enforces one-thread libraries, CPU120/wall180 per invocation, cumulative CPU300/wall420, and 1.5 GiB address space. It records whole-child CPU/wall/RSS separately from case and solver timers. Case work is performed by `code/run_cases.py`, which saves raw accepted nodes, the 201 common reporting samples, support crossings, segment endpoints, and individual solver counters. Existing outcomes are not silently rerun.

`code/analyze_results.py` compares matched common times with contract tolerances, reports angular M4/8/16 differences without presuming continuum convergence, and renders the required diagnostics. One unpaired full-versus-primary cost observation is explicitly insufficient for a robust speedup claim.

## Preserved first failure and authorized completion

The first batch exposed a reporting-only implementation error: a short successfully integrated threshold interval contained no common reporting time, and calling SciPy dense output with an empty array raised `ValueError: need at least one array to concatenate`. This was returned to the controller before repair. The saved checkpoint retains 363 accepted nodes through eta=0.3720455828589731 and 39 reporting times. No scientific coefficient, solver, tolerance, or physical convention is implicated by that traceback. The original batch logs, failure JSON and partial raw NPZ are preserved.

The controller authorized the empty-mask guard and resumption without replay of persisted intervals, then an absolute numerical zero-face diagnostic for full-oracle roundoff (64 machine eps) without changing any saved state. A NumPy-scalar JSON conversion completed that summary repair. Original failures, raw arrays and process costs remain preserved. The added same-grid044 H/n mean-redshift control was separately authorized as case10. Ten completed cases and one conservatively charged interrupted attempt exhaust the11-IVP ceiling. Five main process launches include one summary-only launch; the final cost/refinement analysis and six actual PNG inspections are complete. See `RESULTS_OBSERVED.md` and `FINAL_RUN_RECEIPT.json`; scientific admission remains pending Astra review.
