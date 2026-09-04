# Operator evidence excerpts and normalization

## Scope

This file records load-bearing facts supplied by the operator in this thread. It does not copy whole local logs into Git and does not upgrade operator evidence to an independently replayed repository execution.

## Compiler package provenance

Operator classification:

```text
PASS_LOCKED_CC_PACKAGE_IDENTIFIED_PROVENANCE_ONLY
```

Locked target:

```text
expected compiler SHA-256
6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234

package
gcc-13-x86-64-linux-gnu

binary path inside package
usr/bin/x86_64-linux-gnu-gcc-13
```

Matching Snapshot candidate:

```text
snapshot        20250115T120000Z
version         13.3.0-6ubuntu2~24.04
architecture    amd64
DEB SHA-256     7cd398670e8306eabc9e77202f356a3206c440bd9f3dc764680a19be01784776
binary SHA-256  6117c52522997d2aaccb2b52b3c6bf42c0a6c5edb1d718431fed6b2fc5fec234
match           YES
```

Negative control:

```text
snapshot        20240501T120000Z
version         13.2.0-23ubuntu4
binary SHA-256  29d93d06ab60d67ae118dcf1f8ee0ae14f593b0272df58d3d4ee8c12e0243715
match           NO
```

Current interactive host:

```text
Ubuntu          24.04.4 LTS
installed       13.3.0-6ubuntu2~24.04.1
resolved path   /usr/bin/x86_64-linux-gnu-gcc-13
compiler SHA    1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26
matches lock    NO
```

Operator boundary:

```text
DO_NOT_USE_EXTRACTED_BINARY_FOR_03A4=true
authorization_effect=NONE
global_attempt_ref=NOT_CREATED
local_lease=NOT_CREATED
native_runtime=NOT_RUN
remaining_native_attempts=1
```

Interpretation: the package origin is identified. The historical root filesystem, canonical installed paths, dependency closure, ELF closure, Rust closure, and Section-0 authority are not established by this result.

## Repository ruleset readback

Operator administrator readback:

```text
classification=PASS_EXISTING_RULESET_READBACK
ruleset_id=22240889
global_ref=ABSENT_404
native_runtime=NOT_RUN
```

Focused source tests:

```text
12 tests
12 PASS
```

The read-only operation emitted a durable three-file bundle and checksum verification passed.

## Initial independent audit stop

The first independent live audit returned:

```text
STOP_INVALID: LIVE_RULESET_UPDATE_POLICY_MISMATCH
classification=STOP_INDEPENDENT_LIVE_AUDIT_FAILED
```

The source self-tests passed before this live stop. The failure arose because GitHub's GET representation omitted the request-only update parameters. No attempt ref, local lease, or native runtime was created.

The subsequent REI source line repaired GET normalization while retaining strict request-payload validation. This consolidation separately performed a new live ruleset read and confirmed the active ruleset shape and final-ref absence.

## H1A Docker evidence

Operator statuses bound in PR #59:

```text
PASS_REI_03A4_H1A_DOCKER_ADMISSION
PASS_H1A_DOCKER_ADMISSION_INDEPENDENT_AUDIT
PASS_H1A_DURABLE_AUDIT_CLOSEOUT
```

Durable identities:

```text
independent audit receipt SHA-256
5d344fbfc8a68368386dfcc1ef0ef882813c819e8a263f5a589ab41100d7c9b6

post-audit manifest SHA-256
d1054f80c3d6b48918d840b4b0ad479a8df7381350e1ee9cfacbd1086427eb26

seed RepoDigest
ubuntu@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517

seed image ID
sha256:a6f81fb630d51837271b89f8193810a5fc493fa4f30a55d7ebcdb3a66f3cc63a
```

Interpretation: isolation mechanism only. The external verifier-source identity limitation remains typed, and H1B/H2/H3 must reconstruct package and runtime closure independently.

## Rust environment helper

The supplied helper exports:

```text
RUST_1_94_1_PREFIX=/mnt/data/rust-1.94.1-prefix
PATH=$RUST_1_94_1_PREFIX/bin:$PATH
LD_LIBRARY_PATH=$RUST_1_94_1_PREFIX/lib:$LD_LIBRARY_PATH
```

Interpretation: environment locator only. It is not a Rust driver/LLVM/stdlib/ELF closure receipt and cannot discharge H3.

## BASS state-surface dependency

The prior thread audit distinguishes six BASS state surfaces. The REI-relevant rule is:

```text
frequency-preserving exact primary pair
f(q,e) <-> F_Aell(q)

integrated states
J_Aell^(i), G(e)
require source projection or a spectral-closure certificate
```

This prevents REI from consuming an integrated source summary as a general frequency-dependent provider.

## Formula-SSOT boundary

The supplied formula SSOT and eleven-branch atlas state:

```text
metric signature (-,+,+,+)
epsilon_123=+1
c explicit
collision = cold non-tilted electron-rest Thomson
```

They explicitly exclude finite electron tilt, recombination/reionization microphysics, truncation, line-of-sight integration, solver construction, numerical evolution, likelihood, and inference.

Interpretation: REI may consume the formula layer under its declared domain, but the formula documents do not establish a reionization solver, finite-tilt collision, first interval, provider, or statistics result.

## Evidence-class warning

Every fact above remains one of:

```text
OPERATOR_DURABLE_EVIDENCE
REPOSITORY_BOUND_EVIDENCE
DEPENDENCY_CONTRACT
FORMULA_SCOPE_AUTHORITY
```

No entry is silently promoted to `DIRECT_GITHUB_EXECUTION` unless a fresh GitHub object or workflow readback is separately recorded in `EVIDENCE_INDEX.json`.
