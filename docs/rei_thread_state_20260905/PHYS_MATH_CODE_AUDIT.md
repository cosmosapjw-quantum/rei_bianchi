# PHYS-MATH-CODE audit

## Audit question

Does the consolidated package correctly map the REI mathematical, runtime, and dependency claims to actual source and execution evidence without creating a false implementation or runtime pass?

## Code-path reality map

| Surface | Actual path/evidence | State | Claim allowed |
|---|---|---|---|
| M1 spatial-curvature oracle | `research/rei_math_m1_generic_background/derive_spatial_curvature.py` | exact-head executed | formula GREEN |
| M1 adversarial generator | `research/rei_math_m1_generic_background/adversarial_curvature_residuals.py` | exact-head executed | mutation-sensitive regression |
| M1 tests | `tests/research/test_rei_math_m1_spatial_curvature_*.py` | exact-head executed | scoped test evidence |
| Runtime import closure | PR #37 lock delta | source verified | source defect closed only |
| Pre-lease import firewall | PR #45 package | exact-head source CI | governance source PASS |
| Authority/byte binding | PR #47 package | exact-head source CI | governance source PASS |
| Ruleset/live readback | ruleset 22240889 and exact-ref GET | fresh server reads | server state only |
| Runtime path binding | PR #57 package | exact-head source CI | source PASS |
| H1A Docker mechanism | operator receipts bound by PR #59 | operator evidence | isolation mechanism PASS |
| H1B/H2/H3 epoch closure | no completed implementation | absent | NOT_RUN |
| Successor Section-0 | no target-host receipt | absent | NOT_RUN |
| Global/local leases | final ref 404; no local state | absent | NOT_ACQUIRED/NOT_CREATED |
| Native worker | no result receipt | absent | NOT_RUN |
| First interval/provider | no admitted output | absent | NO_PASS/NOT_AUTHORIZED |

## Equation-to-code mapping

### Spatial geometry

```text
locked commutator
→ `_structure_constants`
→ Koszul `_connection`
→ `_ricci_from_connection`
→ candidate residuals
→ Groebner reduction modulo Jacobi
→ machine-readable audit
```

The oracle constructs the connection and curvature instead of inserting only the final Ricci expression. This blocks the simplest formula-copy self-confirmation failure.

### Adversarial route

```text
same derived connection curvature
→ correct formula residual
→ one-term sign mutation
→ class-A/class-B deterministic fixtures
→ CSV/JSON/SVG
```

The controls are structurally discriminating: class A cannot detect the mixed term, while class B must.

### Runtime route

```text
static source/package/Git verification
→ live ruleset/ref GET
→ future global lease
→ future local O_EXCL lease
→ future dispatch intent
→ future separate worker
→ future runtime-result audit
```

The consolidation adds no executable path into this chain. It only validates state metadata.

## Source and branch topology

The active formula line and runtime line diverge:

```text
formula publication base  PR #62 / 01fd5ea...
runtime evidence pin      PR #59 / 00d17c9...
```

A content merge would risk silently composing independent experimental lines. The package instead uses exact external pins and is docs/validation-only on PR #62.

Disposition: PASS topology choice.

## Package integrity design

`SOURCE_INDEX.json` exact-pins the Git blob for each indexed file except itself. This avoids a self-hash cycle. The enclosing Git tree and commit bind the index file.

`validate_package.py` must verify:

1. every indexed path exists;
2. `git hash-object` equals the declared blob;
3. JSON schemas and exact critical identities;
4. claim-ledger uniqueness and required claims;
5. no forbidden claim promotion;
6. one remaining attempt and no runtime/provider pass;
7. exact formula/runtime ancestry pins;
8. allowed changed-path closure.

Disposition: design sound; execution must be demonstrated on the published commit before completion is claimed.

## Runtime authority audit

### Fixed GitHub authority

The active source line fixes `https://api.github.com` and `cosmosapjw-quantum/rei_bianchi`. The consolidation does not add an override.

### Ruleset semantics

The live GET shape omits request-only update parameters. Request creation and GET readback semantics remain separate. The consolidation records the normalized live shape rather than reconstructing the request payload.

### Attempt state

The exact global ref returns 404. No local attempt state is introduced. The workflow will have `contents: read` only and a changed-path guard.

### Host paths

The matching extracted compiler is not wired into any script. H1B/H2/H3 remain explicit prerequisites.

Disposition: PASS no-bypass preservation.

## Test classification

| Test/evidence | Classification | What it proves | What it does not prove |
|---|---|---|---|
| M1 symbolic suite | formula validation | exact residual closure in declared algebra | spacetime/background runtime |
| M1 adversarial suite | mutation regression | mixed-term sign sensitivity | all possible formula defects |
| repository verify | integrity regression | repository-defined checks | scientific completeness |
| runtime governance tests | contract/source tests | no-bypass source behavior | target-host native execution |
| H1A operator audit | environment mechanism evidence | container/isolation mechanism | installed historical epoch |
| package validator | publication integrity | exact package bytes and claim gates | native physics |

Smoke, contract, formula, runtime, and scientific evidence are not conflated.

## Numerical maturity boundary

The M1 oracle uses exact symbolic reduction plus finite adversarial fixtures. It is not a numerical background integrator.

The Rust/MPFR runtime has historical bounded evidence, but this work unit does not execute it. No claim is made about the first canonical interval, global error, stiffness, step control, or provider output.

Disposition: correct claim ceiling.

## Dependency-code firewalls

- REI does not implement a duplicate BASS geometry owner.
- REI does not copy a REC source bundle.
- REI does not implement HTT local-observer processing.
- REI does not treat BASS `L<=8` scalar parity as physical source parity.
- REI does not treat integrated `J/G` as a frequency-preserving source state.
- REI does not expose a local-boost shortcut for global/electron tilt.

Disposition: PASS.

## Hostile failure modes and guards

### Stale exact head

Failure: package cites a historical PR head while the branch has moved.

Guard: exact commit/tree pins and fresh PR readback in the publication receipt.

### Source-index self-cycle

Failure: index tries to hash itself and cannot be sealed deterministically.

Guard: exclude index from its own entries; bind through enclosing tree/commit.

### Pull-request merge checkout

Failure: workflow runs on a synthetic merge commit and source index mismatches.

Guard: indexed content is unchanged by a clean merge; validator checks bytes, while ancestry and changed-path closure separately constrain topology. Any conflict fails closed.

### False runtime pass

Failure: source tests or 404 readback become `native_runtime=PASS`.

Guard: exact forbidden values in validator and claim ledger.

### Extracted-compiler bypass

Failure: alternate matching binary is passed to path-bound runtime.

Guard: no executable handoff in this package; explicit prohibition and H2 canonical-path closure.

### Cross-repository overreach

Failure: dependency summary becomes authority to mutate another repository.

Guard: ownership document states observational-only dependency pins and no foreign work assignment.

## Ranked findings

### P0

None in the docs-only consolidation design.

### P1

1. The package validator and workflow must be run on the exact published head before a package PASS is claimed.
2. A publication receipt must record the actual workflow disposition, including prestart or failure if applicable.
3. The runtime line remains divergent and must not be silently merged by later work.

### P2

1. Large historical PR stack makes “latest” ambiguous; exact head/tree pins are mandatory.
2. Atlassian descriptions may retain stale locators; GitHub remains source truth.
3. Operator receipts are not copied as raw bytes, so their evidence class must remain operator-reported/bound.

### P3

1. Fresh Wolfram unavailable due HTTP 502.
2. SciSpace metadata is method support, not a source checksum.

## Acceptance criteria for this publication

```text
all package blobs published under one bounded prefix
one read-only workflow outside the prefix
exact base ancestry
source index verifies every indexed blob
critical JSON parses
claim ledger unique and complete
changed paths restricted to package/workflow
no attempt or runtime path added
no forbidden promotion string in machine state
git diff --check equivalent passes
remote commit/tree/files read back
Draft PR remains unmerged
```

## Audit verdict before execution

```text
DESIGN_ACCEPTABLE
COMPLETION_WITHHELD_PENDING_EXACT_HEAD_VALIDATION
```
