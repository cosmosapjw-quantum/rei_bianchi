# Supplied caloric branch: authored, NOT_RUN

The frozen contract is `../theory/EOS_BRANCH_CONTRACT.md`. The implementation is a supplied one-dimensional piecewise-affine gas caloric slice. It does not bind an actual REI recipient EOS or change the existing source module. `caloric_branch.py` uses exact rational arithmetic; `test_caloric_branch.py` contains manufactured controls. `run_saved_caloric_branch.py` calibrates the inverse against the preserved C7 represented endpoint, and `suite_once.py` combines fixture tests and that saved-source read in one child process. The input copy is `../inputs/C7_STDOUT.json`, 19,293 bytes by file metadata; identity is verified by the future runner.

No code here has been imported, tested, hashed, or executed at authoring. No approval token or authorization file is authored. The controller proposes a new absolute planning cap of 18 CPU seconds and one 1.5-CPU-second combined reservation, including a child allowance of at most 1 second and supervisor/final-record allowance. Those values are **not approved** by this file. The historical known planning lower bound is 16.350357885 CPU seconds, with additional unknown overhead retained.

After separate explicit approval, the controller may create a one-attempt authorization JSON and a matching independently issued approval-token JSON, freeze file hashes and the exact worker command, then invoke:

```sh
python -B implementation/run_once.py --authorization <authorization.json> --approval-token <approval-token.json> --output-dir <fresh-output-dir> --source inputs/C7_STDOUT.json
```

The authorization schema is `REI_CALORIC_BRANCH_RUN_AUTH_V1` with `approved=true`, `unit=rei_supplied_caloric_branch_20261028`, `mode=combined`, `attempts=1`, nonempty `attempt_id`, `authority_ref`, `accounting_boundary`, `unknown_costs=UNKNOWN_NOT_ZERO`, exact `worker_command`, `source_sha256` for the five Python files, `prior_known_planning_cpu_s`, `approved_absolute_planning_cap_cpu_s`, and `limits` containing decimal-string `attempt_cpu_s`, `worker_cpu_s`, `final_record_reserve_cpu_s`, `wall_s` and integer `memory_bytes`. The independent token schema is `REI_CALORIC_BRANCH_EXECUTION_APPROVAL_V1`, with matching `unit`, `attempt_id`, `authority_ref`, `approved_absolute_planning_cap_cpu_s`, `approved=true` and decimal `max_attempt_cpu_s`. The wrapper records child `wait4` rusage and supervisor pre-record usage; external whole-command accounting remains required because startup precedes its clock.

On any input mismatch, invariant failure or resource stop, preserve raw stdout/stderr and records; do not retry automatically. A zero exit proves only represented source and manufactured fixture checks, never a physical recipient update. Physical temperature, native25, radii and completion remain null.
