# Proposed allowance and one-shot execution — NOT APPROVED, NOT RUN

Preparation implements the frozen THEORY_AND_CONTRACT.md only. The pinned PR242 dependency is copied verbatim under deps/caloric_branch.py, Git blob bc3ebd682c363afc7d5c36d164406086145b6964. No implementation/test import, py_compile, test runner, plot or scientific calculation was executed during preparation.

## Existing authority finding

PR242 FINAL_DELIVERY_RECEIPT.json budget.planning and budget.presentation each declare temporary_cap_active=false and restored_policy_cap_cpu_s10/30. Charged known-plus-reserve planning16.586967885 and presentation50.928518494 remain historical records. The preceding native-review F1 Bash display wall0.037/user0.037/system0.000 is a separate provenance chain and is not silently substituted for PR242's separately reported F1 amount0.026759. Main595.225063/600 NO_MORE_IVPs, foreign owner ledgers, closed reservations and UNKNOWN_NOT_ZERO remain unchanged.

No already-authorized unclosed current-task numerical or presentation allowance was established in the inspected receipt, contract, earlier native-review records or latest backup metadata. Current preparation/text-publication authority does not imply permission to run these commands.

## Proposed explicit cumulative ceilings

Request absolute cumulative planning ceiling20 CPU seconds and reserve2 CPU seconds for this bounded work item. Proposed worker stop is1 CPU second, wall10 seconds, address-space256MiB, one worker and one invocation. Reserve2 includes worker and wrapper/final receipt allowance; it is not a child budget to add a second time. Historical16.586967885 plus proposed reserve2 is18.586967885 as a bookkeeping partial value only; unknown overhead remains UNKNOWN_NOT_ZERO and no whole-session cap PASS follows.

Request absolute cumulative presentation ceiling56 CPU seconds and reserve4 CPU seconds for one future plot/packaging invocation, with CPU hard stop4 seconds, wall30 seconds and512MiB address-space bound. Historical50.928518494 plus proposed reserve4 is54.928518494 as a partial bookkeeping value only. This proposal replaces no old debit, reopens no closed reservation, transfers no foreign allocation and authorizes no IVP. Neither requested ceiling is currently approved.

## Future commands from the unit root

Numerical command, exactly once after explicit approval:

```bash
python -B -S execution/run_once.py --execute-authorized
```

The wrapper creates execution/attempt_01 exclusively, verifies the frozen dependency blob, invokes only the new targeted unittest source, applies the worker limits, and preserves raw STDOUT.json, STDERR.txt and PROCESS.json. OS RUSAGE_CHILDREN measures the sole complete child; wrapper and external costs remain separate. Any failure stops with its raw evidence; no auto-retry or tolerance adjustment is authorized.

Presentation command, one invocation after successful new data and explicit presentation approval:

```bash
timeout --signal=TERM --kill-after=1s 30s prlimit --cpu=4:4 --as=536870912:536870912 -- python -B figures/plot_saved.py --execute-authorized
```

External OS accounting and raw stdout/stderr/exit must be preserved by the authorized caller for this presentation command; the script also records its process-time prefix. The output is one two-panel PNG/SVG plus a figure/saved-controls ZIP. Actual rendered-image inspection remains required separately before any figure acceptance. Packaging does not import implementation or rerun science.

## Authored controls and acceptance

One future invocation contains seven unittest methods covering controls A-G. A verifies11/6 and independently derived rational forward/central error formulas at h=1/4,1/8,1/16,1/32,1/64. B verifies1/3 versus−1/2 directional values, the false centered5/12 candidate and1/12 error; saved directional-map rows provide the first panel. C verifies moving-knot8/3,1,2. D covers endpoint domain/type/dimension refusals and inward/tangent acceptance. E covers equal-slope interior common coefficients. F verifies consistent moving energy coordinates and a deliberately inconsistent target-direction negative control. G verifies callback(11/2,7/3), missing temperature column, dimensions and accidental-float refusal.

Optional saved-source derivative controlH is deliberately not selected for this minimal invocation; its state remains NOT_RUN_NOT_SELECTED. No source producer, old inverse calibration, existing PR242 suite, CAS or IVP is invoked. Passing authored controls would be new executed evidence only, never automatic stage or physical admission.
