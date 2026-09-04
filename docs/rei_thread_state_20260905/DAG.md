# REI synchronized DAG

## Status vocabulary

```text
PASS              executed gate satisfied
PASS_SOURCE       source/contract gate satisfied; target runtime not executed
PASS_EXPECTED_RED test-first absence/hostile contract observed as designed
OPERATOR_EVIDENCE durable operator receipt not independently replayed here
NOT_RUN           target operation did not execute
BLOCKED           prerequisite missing
NO_PASS           scientific admission explicitly withheld
NOT_AUTHORIZED    operation is outside current authority
```

## Formula and background DAG

```text
REI-MATH-M1-RED
  PR #61 / 5736882a3007109fab74a640fab71ff4df85db58
  8 expected failures / 0 errors
  PASS_EXPECTED_RED
      ↓
REI-MATH-M1-GREEN
  PR #62 / 01fd5ea775795d27758f354971ca478f90701295
  generic spatial Ricci/scalar + homogeneous STF divergence
  symbolic residuals exact zero
  PASS
      ↓
REI-MATH-M1-CRAG
  class-A negative controls + class-B mixed-sign detections
  workflow 33870832194 SUCCESS
  PASS
      ↓
REI-MATH-M1B-SPACETIME-GAUSS-CODAZZI-CONSTRAINT-SIGN
  positive K^+ convention
  locked four-dimensional Riemann and stress-energy signs
  explicit BASS owner/oracle relation
  NOT_STARTED
      ↓
REI-MATH-M1C-CONSTRAINT-PROPAGATION
  D_0 C = A_C C or equivalent closed system
  NOT_STARTED
      ↓
REI-BACKGROUND-NUMERICAL-ADMISSION
  I / II / V / IX / VI_-1/9 sentinels
  residual and convergence gates
  BLOCKED
```

The formula DAG is independent of the irreversible runtime-attempt lane until a later admitted background executable consumes the formulas.

## Runtime-governance DAG

```text
historical standalone runtime attempt
  first blocker UNDECLARED_IMPORT: ntpath
  STOP_INVALID
      ↓
ntpath declared-import closure
  PR #37
  PASS_SOURCE
      ↓
successor handoff and compact packet
  PR #38 / PR #40
  PASS_SOURCE
      ↓
successor-host governance and executable handoff
  PR #41 / PR #42
  PASS_SOURCE
      ↓
successor Section-0/read-only preflight source
  PR #43
  PASS_SOURCE
      ↓
pre-lease production-import firewall
  PR #44 RED → PR #45 GREEN
  PASS_SOURCE
      ↓
fixed authority and exact executing-byte binding
  PR #46 RED → PR #47 GREEN
  PASS_SOURCE
      ↓
protection freshness/live readback
  PR #48 RED → PR #49 GREEN
  PASS_SOURCE
      ↓
admin ruleset source and independent audit
  PR #50–#54
  source repaired
  live ruleset 22240889 ACTIVE
  final attempt ref ABSENT
      ↓
canonical runtime-path binding
  PR #56 RED → PR #57 GREEN
  PASS_SOURCE
      ↓
H0 compiler package provenance
  Snapshot 20250115T120000Z
  PASS_PROVENANCE_ONLY
      ↓
H1A Docker isolation mechanism
  operator admission + independent audit + durable closeout
  OPERATOR_EVIDENCE PASS
      ↓
H1B1 full signed-Snapshot package-provenance census
  NEXT
      ↓
H1B2 fresh isolated root construction
  BLOCKED_ON_H1B1
      ↓
H2 installed-byte / canonical-symlink / ELF closure
  BLOCKED_ON_H1B2
      ↓
H3 Rust driver / LLVM / stdlib closure
  BLOCKED_ON_H2
      ↓
H4 complete thirteen-field dry census
  BLOCKED_ON_H3
      ↓
H5 successor Section-0 + GET-only static preflight
  BLOCKED_ON_H4
      ↓
independent preflight audit
  BLOCKED_ON_H5
      ↓
atomic global lease
  ref currently ABSENT
  NOT_AUTHORIZED_YET
      ↓
persistent local O_EXCL lease
  NOT_CREATED
      ↓
dispatch intent + one native worker
  remaining attempts 1
  NOT_RUN
      ↓
runtime-result audit
  BLOCKED
      ↓
first-canonical-interval eligibility
  NO_PASS_FIRST_CANONICAL_INTERVAL
      ↓
REI provider review/export
  NOT_AUTHORIZED
```

## Cross-repository join DAG

```text
BASS native background/constraint completion ───────┐
REI M1/M1B independent oracle completion ───────────┤
                                                    ├→ admitted background input
REC primordial source/provider ─────────────────────┤
REI runtime + first canonical interval ─────────────┤
BASS representation/source certificates ───────────┘
                                                        ↓
                                      coupled cosmic-frame transport
                                                        ↓
                                      HTT local-observer processing
                                                        ↓
                                      identification / likelihood
```

## Parallel frontier

The following may proceed independently on separate branches:

```text
A. REI-RUNTIME-03A4-H1B1 signed-Snapshot package census
B. REI-MATH-M1B spacetime Gauss-Codazzi sign derivation
C. BASS native E_ab projection/constraint bridge
D. REC physical source/provider construction
E. HTT K1R and local-observer method work
```

Only A and B belong to this repository's direct next-step authority. C–E are dependency observations, not REI work assignments.

## Forbidden edges

```text
H1A Docker PASS -> Section-0                 forbidden
compiler package found -> execution          forbidden
404 final ref -> execution authorization     forbidden
source GREEN -> native runtime PASS           forbidden
M1 spatial curvature -> background ready      forbidden
BASS L<=8 scalar parity -> REI source parity forbidden
local observer boost -> global/electron tilt forbidden
first interval NO_PASS -> provider export    forbidden
```

## Current terminal

```text
FORMULA_STATE     M1_GREEN_M1B_OPEN
RUNTIME_STATE     HOST_EPOCH_RECONSTRUCTION_REQUIRED
ATTEMPT_STATE     GLOBAL_REF_ABSENT_ONE_ATTEMPT_REMAINS
SCIENCE_STATE     NO_PASS_FIRST_CANONICAL_INTERVAL
PROVIDER_STATE    NOT_AUTHORIZED
MERGE_STATE       DRAFT_ONLY
```
