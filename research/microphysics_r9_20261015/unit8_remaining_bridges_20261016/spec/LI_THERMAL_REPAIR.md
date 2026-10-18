# Unit8 Li thermal continuation: one equivalent linear-solve repair

Frozen 2026-10-17 before any repaired numerical execution. Requested authority
Astra; observed runtime identity UNKNOWN. This amendment supplements
`LI_THERMAL_CONTRACT.json`; every original physical input, rate construction,
acceptance limit and claim ceiling remains binding.

## Observed failure and scope

The original ground Radau production and reusable rate work are saved. The
required unchanged BDF reference failed with `Required step size is less than
spacing between numbers` at u=0.5673291649750605. The replay had 208 RHS
evaluations, 8 Jacobians and 74 LU decompositions. Its q2 direct population was
2.6680432865425157e-12. Classify this as an observed BDF numerical precision
stall. Poorly scaled Newton linear systems are a repair hypothesis, not an
established causal diagnosis. Do not interpret the stall as a physical no-go.

Preserve `failure.json`, `run.log`, `BDF_diagnostic.json`,
`BDF_diagnostic.log`, `ground_BDF_diagnostic.npz`, `ground_production.npz`,
all saved rate evidence and original implementation files. Add a separate
continuation runner `code/li_thermal_resume.py`; a narrowly scoped helper/test
is permitted under the original owned paths. No original numerical work is
repeated, except the single repaired reference attempt authorized here.

## Exact repair

For each BDF Newton linear system A delta = b, let D be a positive diagonal
matrix of powers of two returned by scipy.linalg.matrix_balance with
permute=False, scale=True, separate=True. Factor

    B = D^(-1) A D,
    B w = D^(-1) b,
    delta = D w.

Then A delta = b identically in real arithmetic. Dyadic scaling avoids extra
rounding in representable scaling operations. This is linear algebra
conditioning only: it changes no physical state definition, RHS, analytic
6x6 Jacobian, interpolant, source, implicit equation, error norm or tolerance.
It is not a new ODE solver or a stationary-state approximation.

Use a subclass of the installed scipy.integrate._ivp.bdf.BDF. After its normal
initializer, replace only `self.lu` and `self.solve_lu`. The first calls
matrix_balance as above and scipy.linalg.lu_factor on B, increments self.nlu
once and returns the LU factor together with the diagonal scaling. The second
calls scipy.linalg.lu_solve on b/D and returns D times that solution. Do not
mutate the original A or RHS array, add permutations, alter scipy source, or
modify any step/order/Newton/error-control policy. Reject nonfinite or
nonpositive scaling rather than adding floors or clipping. Retain BDF
rtol=3e-9, atol=3e-14 and the exact original zero initial six-vector.

Before the reference solve, one mechanical dyadic system verifies the wrapper:
A=[[4,2^-20],[2^20,4]], x_expected=[2^-20,1], b=[5*2^-20,5]. Require
max_i |x_i/x_expected_i-1| <= 64*machine_epsilon and record the returned scale
factors. This tolerance is frozen now for implementation arithmetic only;
it does not replace or weaken any original scientific acceptance threshold.
Do not add a diagnostic solver sweep or tune the scaling after seeing results.

## Continuation and diagnostic reconstruction

Load the existing rate tables, raw quadrature/formula checks, Be history and
production arrays. Reconstruct their original scalar metrics algebraically;
do not run quadrature or repeat production. Run exactly one balanced BDF
reference, then the originally pending ground257, ground_half_Be and total-RR
Radau solves with their original settings. The balanced reference must satisfy
the unchanged 5e-6 maximum absolute per-origin comparison against saved
production. All original positivity, normalization, rate, ledger and other
acceptance tests remain mandatory.

The original production dense solution was not persisted. For the six
selected-z diagnostic rows only, interpolate the saved 1025 production state
rows using PCHIP in u, reconstruct q3 as originally prescribed, and label the
result `PCHIP_of_saved_1025_output_states`. Endpoints use exact saved states.
This interpolation is diagnostic reconstruction, not a new trajectory or an
extra accuracy certification. All scientific solver comparisons and inventory
history use the original common saved output grid. Existing tiny-fraction
accuracy limits remain explicit. Freshly computed comparison models may use
their own solver dense output as before, with the method distinguished.

After successful continuation, finish the originally required histories,
diagnostics, inventory17, availability map, summary, focused tests and execution
receipt. Record balanced-BDF solver class, scales/range, factorization counts,
raw success/message and measured wall time. On failure serialize the partial
state and actual message before stopping. Use a new continuation failure file;
never overwrite original failure evidence. No scoped admission is automatic:
return outputs/diff to the independent reviewer.

## Cumulative budget and stopping rule

The initial measured elapsed time is UNKNOWN. Controller authorized a
conservative accounting debit of 3 seconds; diagnostic command wall time is
0.460839424 seconds. Thus remaining accounting allowance is 26.539160576
seconds, not a newly reset 30-second allowance. One thread throughout.

Use one continuation process with external timeout 26s and internal deadline
at most 26s, including the wrapper check, remaining solves and validation.
Record process wall time and cumulative accounting (3 + 0.460839424 + new
measured command wall time). Preserve UNKNOWN for initial actual elapsed;
do not relabel accounting as a measurement. No unmeasured new numerical pass.

If the wrapper check, repaired BDF or any subsequent frozen test fails, or the
remaining deadline is reached, preserve completed evidence and return
FAIL_RETURN_TO_AUTHORITY. This consumes the single permitted targeted repair;
no second scaling strategy, tolerance change, alternate solver ladder,
production rerun or numerical retry is authorized. Successful completion goes
directly to independent scoped review and then publication at the frozen
reduced early-radiative-model ceiling.

Execution requires the independent reviewer's approval of this frozen repair
contract. PASS has the immediate next action: the coding agent implements this
continuation and performs the single bounded pass.
