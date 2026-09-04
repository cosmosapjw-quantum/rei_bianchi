# PHYS-MATH-CODE audit — REI 03A4 cross-CAS sidecar

## Current claim

A non-authoritative sibling verifies the declared no-bypass order using several
independent algebra systems while leaving the canonical target-host preflight
and the final native attempt untouched.

## Actual source surfaces

```text
cross_cas_contract.py   SymPy/mpmath contract and deterministic receipt
 octave_verify.m        independent floating/exact-integer matrix witness
 sage_verify.py          rational matrix plus Boolean polynomial ideal
 singular_verify.sing    Groebner refutations of missing predecessors
 lean/REI03A4.lean       kernel-checked implication theorems
```

The workflow has `contents: read`, performs no GitHub write, does not load the
REI production bridge, and asserts absence of attempt, preflight, and runtime
state.

## Ranked residuals

### P1 — methodology cannot replace target-host evidence

Even unanimous CAS results prove only the declared finite chain.  They cannot
attest the target host's Rust/Python/MPFR/GMP/compiler/linker bytes or execute
`PASS_READ_ONLY_STATIC_PREFLIGHT`.

### P1 — declared implications are assumptions

Lean and the Boolean ideals prove consequences of adjacent prerequisite
implications.  They do not prove that every future controller implementation
actually enforces those implications.  Source-level controller tests and the
real receipt chain remain load-bearing.

### P1 — operator-reported local receipt bytes are not in Git

The two SHA-256 identities are recorded from the operator's successful run.
This branch does not independently read the Dropbox files.  The distinction is
preserved in the contract and README.

### P2 — package-version and runner variation

Octave and Singular are installed from the current Ubuntu runner archive.
SageMath is container-pinned and Lean/mathlib are release-tag-pinned.  All
version outputs must be read from CI before any external-axis PASS is claimed.

### P2 — numerical mpmath and Octave witnesses are not formal proofs

They supplement, but do not replace, SymPy exact arithmetic, Sage/Singular
ideals, or Lean kernel checking.

### P2 — absence receipt freshness

The audited protection receipt is bounded in time.  A successful historical
cross-CAS run must not be reused as current authority for global reservation.
The controller must perform its required fresh protection readback later.

## Minimal support condition

The sidecar may claim only
`PASS_03A4_CROSS_CAS_NO_BYPASS_SIDECAR` after all six external jobs and the
live read-only boundary job succeed on the same exact source head.

It may not claim:

```text
PASS_EQUIVALENT_SECTION_0_SUCCESSOR
PASS_READ_ONLY_STATIC_PREFLIGHT
global or local lease acquisition
native runtime result
first canonical interval
provider or scientific readiness
```
