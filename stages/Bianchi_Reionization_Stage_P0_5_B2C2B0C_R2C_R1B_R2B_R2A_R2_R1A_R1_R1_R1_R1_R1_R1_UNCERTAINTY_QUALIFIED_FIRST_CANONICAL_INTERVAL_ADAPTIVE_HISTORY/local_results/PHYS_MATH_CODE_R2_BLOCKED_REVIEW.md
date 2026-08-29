# PHYS-MATH-CODE review: R2 first-interval blocked terminal

Reviewed frozen commit:
`a35c8b3fceaf9c832b401bc01480f5e3b0b4af30` (tree
`85a446c9954a6d0c9e02eaa04374a234500bd481`).

Reviewed archive:
`first_interval_r2_blocked_minimum_step.tar.gz`, 11,637,524 bytes,
SHA-256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.

## Verdict

PASS for preservation and attribution of the blocked terminal; no P0/P1 code
repair was reproduced. This is not scientific acceptance of the first
interval.

## Verified code/evidence properties

- Gzip integrity and all 35 archive members pass. The workspace archive,
  sidecar, receipt, and committed artifact agree on byte identity.
- The immutable preflight and run owner consistently bind runtime contract
  `10ab5823e109f32d693c82d246b3369045ddecf5217fa30fc4013ab6d55c3810`
  and runtime source HEAD `11030b860989916d2c84ae0177ef8bfa3eb2b7dc`.
- All three named lanes execute full, first-half, and dependent second-half
  images on the locked attempt. Every envelope reports
  `VALIDATED_LOCAL_ERROR_GATE_FAILURE` with the same maximum
  `2.1245050576368385e-4`.
- Bisection is exactly
  `160->192->176->168->164->162->161`, followed by
  `STOP_MINIMUM_STEP` at depth six.
- Attempts 5 through 10 retain the same tick-160 parent SHA-256 in each lane,
  publish `candidate_state: null`, and leave the accepted record at index 3.
- The accepted-record and ten-transition chains hash-link exactly, and every
  transition binds its immutable attempt receipt.
- The exploratory untracked event, oracle, and cumulative-ledger modules and
  tests are absent from both the frozen commit and the packaged evidence.

The existing code correctly enforces the locked `2e-4` threshold and one-tick
minimum. Altering either, or admitting the exploratory files, would change or
weaken the contract rather than repair a code defect.

Claim ceiling for this delivery is
`CANDIDATE_UNSEALED_LOCAL_EXECUTION / BLOCKED_MINIMUM_STEP`. No complete
first-interval, event-restart, independent-oracle, or whole-history-ledger
claim is admitted.
