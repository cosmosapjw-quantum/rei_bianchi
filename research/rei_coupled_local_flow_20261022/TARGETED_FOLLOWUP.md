# Two targeted follow-ups after the first successful run

The first scientific diagnostic completed once: 103/103 checks, exit 0,
wall 40.260782102 s, CPU 38.323068887 s. Its original outputs and source
snapshot remain evidence. These follow-ups do not reset its count or replay
the prior atomic/C1/C2 units.

## 1. Self-contained replay repair

Observed defect: the initial input-copy check reads the adjacent previous
unit, and the initial shell helper writes to the delivered results directory.
That prevents replay from a standalone package and conflicts with evidence
preservation. This affects delivery, not the completed numerical results.

Authorized minimal correction: preserve the executed driver/helper version;
use an input SHA256 manifest populated from the successful source-copy checks;
make run_fresh.sh create a /tmp copy of this unit's necessary source and
inputs, then execute there. Provide --prepare-only to check the copied inputs
and imports without launching integrations. Record the exact diff, source
identity and prepare-only outcome. Do not rerun scientific experiments solely
for this packaging correction.

## 2. Paired timing clarification

Observed finding, also raised independently: sequential baseline timing
batches show large variation. Thermal100 reduced spans 15.3–741.6 ms;
thermal1000 full spans 26.3–108.7 ms. Those observations do not establish a
robust algorithm speedup or an adequate basis for a performance default.
No cause of the timing variation has been established.

Authorized finite timing-only diagnostic: reuse the unchanged scientific
local_flows.py and the saved final times/output grids/reference arrays for
the same three thermal and three beta cases. No Radau, new quadrature,
convergence sweep, parameter extension or scientific-tolerance change.
For each two-method pair, warm both and run seven paired batches, alternating
A/B versus B/A order; three solves per method per batch. Record both
process_time CPU and perf_counter wall clocks for each batch and the original
RHS/stage counts. Include equivalent output/reconstruction work for the two
thermal paths. Confirm the returned outputs against the preserved references
at the existing acceptance thresholds. Keep both raw baseline and paired
timing results. Inspect one paired timing plot if produced from these results.

Resource cap for this follow-up process: CPU30s, wall45s, AS1GiB, BLAS1.
This keeps the planned cumulative scientific/timing CPU below120s. If the
paired data are still inconclusive, report that fact and stop optional timing;
do not enlarge a sweep to obtain a desired winner. A conservative functional
default may use the direct 2-state thermal solve and high-accuracy adaptive
beta solve while retaining exact reductions/subflows for their proven roles.

The same independent reviewer checks these narrow changes and resulting
claims in the current review pass. This note is controller authorization
for the lower-tier worker; it does not claim either follow-up has executed.
