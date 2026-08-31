# REI Rust-first execution policy

## Authority and recovery class

This checkout is rebuilt from commit
`1893f12d14b212eb4b6bd637332824f692e6f4b3`, tree
`773fcdc4d1ab115fa0542d26ba67af5c086f450b`.  The policy documents and
work-unit records introduced on this branch are new versioned artifacts.  They
are classified `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`; they must not be
presented as byte-identical copies of any lost transient worktree.

The supplied research and coding harness archives are input authorities only
at their exact SHA-256 identities recorded in
`stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/INPUT_LOCK.json`.

## Required workflow

1. Declare the current task layer: `diagnose`, `design`, `implement`,
   `validate`, `review`, or `document`.
2. Update the durable progress checkpoint before and after a material step.
3. Compile each load-bearing claim into an executable gate in
   `AUDIT_COMPILED_WORK_UNIT.json` before promoting the claim.
4. Run low-cost focused checks before broader checks.  Record the exact
   command, exit code, and result; an earlier summary is not fresh evidence.
5. Run one primary PHYS-MATH audit and one fresh PHYS-MATH-CODE audit.  A
   coherent task may receive at most one P0/P1 repair after those audits.

## Progress-first and anti-meta-loop rule

An attempt has material delta only when it adds a new authority byte, changes
an executable hypothesis, changes an implementation, or produces new gate
evidence.  Rewording, re-prompting, relabelling the same blocker, or rerunning
an unchanged failing command is not material progress.

Each blocker receives one initial attempt and at most one diagnostic retry.
Two consecutive attempts with no material delta require `STOP_META_LOOP`, a
durable checkpoint, and a typed handoff.  Do not silently begin a third route.

## Identity classes

- `BYTE_IDENTITY` requires an exact cryptographic digest of the exact bytes.
- `SEMANTIC_IDENTITY` requires a declared normalization, versioned parser or
  comparator, and evidence that the accepted semantics are equivalent.
- A filename, commit ancestry, object type, or successful parse does not prove
  byte identity.
- Byte and semantic identities are never interchangeable without an explicit,
  audited transformation record.
- A summary-derived reconstruction is always
  `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL` even when its behavior matches.

## Runtime and numerical boundary

The load-bearing numerical core is Rust 1.94.1 with MPFR 256-bit directed
rounding.  Python may coordinate dependency authority, certificate graphs,
transactions, REIAFF1, and APIs.  JAX and `jaxlib` are forbidden from the
load-bearing path; their presence cannot discharge a numerical gate.

Runtime validation is fail-closed for undeclared file opens, undeclared import
roots, source/hash drift, and Git lazy-object configuration.  Inspect local,
worktree, and common Git configuration and reject `promisor`,
`extensions.partialClone`, or a promisor remote before consuming authority
bytes.  The guarded callback must be entered through the factory-issued
capability and observed automatically by the audit hook; caller-supplied
path/import observations are rejected.  This is an invocation-scoped guard,
not a claim that Python can police unrelated processes, a hostile
fresh-process boundary, or interpreter/ELF inputs loaded before the guard
starts.

## Claim ceiling

The 46,080-node x three canonical pilot is outside this work unit and must not
be run.  Until every mandatory gate is green, the only valid scientific status
is `NO_PASS_FIRST_CANONICAL_INTERVAL`; production status is `STOP_INVALID`.
Never merge, mark ready, or describe a bounded fixture result as a canonical
scientific pass.
