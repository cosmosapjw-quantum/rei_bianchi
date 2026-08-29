# PHYS-MATH review: R2 first-interval blocked terminal

Reviewed frozen commit:
`a35c8b3fceaf9c832b401bc01480f5e3b0b4af30` (tree
`85a446c9954a6d0c9e02eaa04374a234500bd481`).

Reviewed archive:
`first_interval_r2_blocked_minimum_step.tar.gz`, 11,637,524 bytes,
SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.

## Verdict

`BLOCKED_MINIMUM_STEP` is mathematically correct and terminal under the frozen
contract. No in-scope repair was demonstrated. This review does not admit the
complete first interval or the terminal ceiling.

## Findings

- P0: none. No failed endpoint was committed.
- P1: all three lanes fail the strict local-error gate on `[160,161]` with
  `log_T = 2.1245050576368385e-4`, above the strict `2e-4` limit by
  `1.245050576368384e-5` (6.225%).
- P1: the implemented cross-box quantity is
  `max(abs(half.lo-full.hi), abs(half.hi-full.lo))`. For scalar boxes it equals
  center separation plus both radii and therefore gives `D(I,I)=width(I)`.
  It is a conservative maximum separation, but after a nonpoint parent it is
  not a correlation-preserving same-parent local-truncation estimator.
- P2: the frozen rejected-attempt receipt does not retain the full and
  two-half endpoint arrays, and whole-history ledger closure remains
  unimplemented. Neither limitation can be promoted to a pass.

The four-, two-, and one-tick values are respectively
`2.144803577710519e-4`, `2.131269352698695e-4`, and
`2.1245050576368385e-4`. At one tick, the public width
`2.257243260856967e-4` remains below `2e-3`; all 14 returned ledger intervals
per lane contain zero; the implicit and positive-root diagnostics pass; and no
table event is reported (minimum distance `2.624595747171554e-4`). The stop is
therefore specifically the locked local-error gate.

Changing the tolerance or minimum, subtracting widths, intersecting boxes,
using midpoint comparisons, or reconstructing correlation after the fact is
not an admissible repair. A sound continuation requires a new
dependency-preserving full-versus-two-half propagation with a validated
discrete-map remainder, authorized through a new scientific contract.
