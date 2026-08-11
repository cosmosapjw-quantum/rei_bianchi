# TDD red receipt

Before implementation, `python -m unittest discover ...` exited 1 because the
new state, policy, worker, and supervisor modules did not exist. The tests now
retain the required deterministic-state, common-commit, bisection, event,
transport-failure, and resume checks.

Subsequent adversarial RED probes reproduced and then closed: arbitrary resume
cursor acceptance, missing receipt acceptance, CONTROL/LATEST reverse order,
malformed state/envelope commit, unsafe foreign-run cleanup, active
runner/package races, injected production workers, dependency/JAX drift,
cross-lane duration drift, known scientific exceptions misclassified as
transport crashes, transition-temporary and initialization crash windows,
launcher option injection/preflight clobber, boolean-as-integer schema drift,
unlinked history parent states, and receipt jobs not bound to accepted records.

The current suite contains 49 cases. Every behavioral fix above was preceded by
a focused failing test; the complete suite is rerun after integration changes.
