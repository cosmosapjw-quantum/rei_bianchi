# Universal progress-first, identity, and audit policy

Version: `rei-universal-execution-policy/v2`

Recovery classification: `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`

This document is a new repository artifact reconstructed from the controlling
thread summary, the two pinned PHYS-MATH harnesses, and the exact Git base.  It
does not claim byte identity with the unavailable documents named in the
thread.

## 1. Progress before orchestration

A work unit starts with a falsifiable acceptance condition and ends in exactly
one of `PASS`, `BLOCKED`, `STOP_INVALID`, or `STOP_META_LOOP`.  Planning,
delegation, review, and prompt generation count as progress only when they
change the authority set, executable hypothesis, implementation, or gate
evidence.

For one blocker the retry budget is:

1. one initial attempt;
2. one diagnostic retry only if it tests a distinct falsifiable cause;
3. after two attempts without material delta, emit `STOP_META_LOOP`, preserve
   evidence, and hand off the missing authority or capability.

Changing labels, rewriting the prompt, starting an equivalent agent, or
repeating an unchanged command does not reset the budget.  A new attempt may
begin only after a new authority byte, capability, implementation delta, or
testable hypothesis is recorded.

## 2. Durable checkpoints

The checkpoint is append-oriented and records the base identity, task layer,
last material delta, gate results, blockers, attempted hypotheses, retry count,
and next executable action.  A resumed run reads that checkpoint before
planning.  It must not infer missing bytes from prose.

Every checkpoint distinguishes:

- `OBSERVED`: freshly read or executed evidence;
- `INFERRED`: a conclusion derived from observed evidence;
- `PENDING`: not yet executed or materialized;
- `BLOCKED`: a named missing authority, capability, or failed mandatory gate.

## 3. Audit-compiled execution

Before implementation promotion, every load-bearing claim is compiled to:

`claim -> invariant -> executable gate -> expected result -> evidence path -> status`.

P0 and P1 findings must name an executable gate or a typed external blocker.
Narrative review alone cannot close a finding.  Candidate producers cannot
approve their own claim.  Run one PHYS-MATH audit and one fresh
PHYS-MATH-CODE audit; permit at most one P0/P1 repair for a coherent task, then
rerun the affected gates.  Residual P0/P1 becomes `STOP_INVALID` and a handoff,
not another repair loop.

## 4. Byte identity and semantic identity

`BYTE_IDENTITY` is established only by a digest over the exact bytes under a
named algorithm.  `SEMANTIC_IDENTITY` is established only by a declared
normalization, versioned parser/comparator, and equivalence evidence.  The
classes answer different questions and neither implies the other.

A reconstruction from a summary, a same-named file, matching metadata, valid
syntax, or Git ancestry is insufficient for byte identity.  Such an artifact
is labelled `RECOVERED_FROM_SUMMARY_NOT_BYTE_IDENTICAL`.  If it is later shown
semantically equivalent, preserve both the reconstruction label and the
semantic proof receipt.

## 5. Runtime closure

Before load-bearing execution:

1. resolve every declared path without following an undeclared replacement;
2. verify its byte digest against `INPUT_LOCK.json`;
3. reject every undeclared authority-file open and import root;
4. reject JAX or `jaxlib` on the load-bearing route;
5. inspect repository-local, worktree, and common Git configuration and reject
   `remote.*.promisor`, `extensions.partialClone`, and equivalent lazy-object
   state;
6. build outside every Git worktree and bind source, compiler, linker, MPFR,
   GMP, artifact, and receipt identities;
7. execute the guarded callback through the factory-issued runtime capability;
   automatic audit-hook observation, rather than caller-supplied path/import
   lists, supplies the evidence;
8. reject legacy self-reported observations and unobserved thread/fork
   contexts;
9. treat the guard as invocation-scoped.  Do not claim system-wide,
   pre-interpreter-start, or hostile fresh-process mediation.

An open/import that is not declared is an error even when it appears harmless.
Adding it requires an explicit lock revision; silent discovery or fallback is
forbidden.  The current bounded guard does not close
`RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING` or
`BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED`.

## 6. Rust-first boundary

Rust 1.94.1 plus MPFR at 256-bit precision and directed rounding owns
load-bearing interval arithmetic.  Python owns orchestration, lock checking,
certificate graph/transaction logic, REIAFF1, and API adaptation.  JAX is not
load-bearing.  Native division must reject zero-containing divisor intervals
before evaluation, and every accepted implicit enclosure must prove strict
self-inclusion.

## 7. Scope and claim ceiling

The 46,080 x 3 canonical pilot is excluded.  Fixture, oracle, or bounded
operator checks cannot promote the canonical claim.  Until all declared gates
are green, retain:

- adapter: `STOP_INVALID` or a more specific partial-invalid state;
- canonical pilot: `NOT_RUN`;
- first interval: `NO_PASS_FIRST_CANONICAL_INTERVAL`;
- scientific pass: `NOT_CLAIMED`.
