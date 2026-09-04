# REI 03A4 cross-CAS no-bypass sidecar

This package is an explicitly non-authoritative verification sibling of the
canonical target-host static preflight.  It checks the finite ordering contract
with several independent algebra systems after the attempt-ref ruleset audit was
completed.

## Canonical parent and evidence boundary

```text
PR #54 head
9ecaa45d4794b2c7f2a430acff4e3ac7f213a2fc

PR #54 tree
db334db438c59f20ebd8c9b289e00c9f3ede27cc

operator-reported independent-audit SHA-256
7438d027d306308628a87d9d546506c31f39db4523c9cf151091b98e99af856c

operator-reported audited-protection SHA-256
ca1b13ddd7dc9d124bcfd484aedd94016a761c36c5b32a243e54746ee644914a
```

The local Dropbox bytes are not copied into this branch.  Their identities are
recorded as operator-reported inputs and corroborated only by current GitHub
ruleset/ref reads.  They are not timeless reservation authority.

## Checked order

```text
IndependentAudit
→ TargetHostStaticPreflight
→ FreshProtectionReadback
→ GlobalLease
→ LocalLease
→ DispatchIntent
→ NativeWorker
→ RuntimeResultAudit
→ FirstIntervalEligibility
→ ProviderReview
```

The sidecar checks the same chain through:

```text
SymPy             exact adjacency matrix and Boolean satisfiability
mpmath             100-digit numerical matrix witness
GNU Octave         matrix powers and transitive closure
SageMath           Boolean ideal and exact rational matrix
Singular           Groebner refutation of missing-predecessor states
Lean + mathlib     kernel-checked implication theorems
```

The expected test-first RED is commit
`6ea848a189b37782b297b373c545f77ded395960`.  It records seven
`FileNotFoundError` results because the implementation module is deliberately
absent there.

## Strict boundary

```text
authority_effect       NONE
mutation_effect        NONE
global attempt ref     ABSENT_REQUIRED
local lease            NOT_CREATED
native runtime         NOT_RUN
first interval         NO_PASS
provider export        NOT_AUTHORIZED
```

A successful cross-CAS run does not execute or replace the actual preflight.
The next canonical operation remains the existing fixed-authority,
production-import-free:

```text
handoff/rei_runtime_prelease_import_firewall_green_20260903/
successor_section0_preflight.py
```

on a fresh standalone target-host clone of the exact PR #54 release.  That
operation must emit `PASS_EQUIVALENT_SECTION_0_SUCCESSOR` and
`PASS_READ_ONLY_STATIC_PREFLIGHT`, then stop for separate audit.
