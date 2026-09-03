# REI runtime bridge declared-import closure — `ntpath`

## Scope

This node repairs exactly one observed software-contract defect at the active
REI scientific checkpoint:

```text
STOP_INVALID: UNEXPECTED_RUNTIME_BRIDGE_EXCEPTION:
RuntimeClosureError: UNDECLARED_IMPORT: ntpath
```

The production bridge imports `pathlib`; CPython 3.12 `pathlib` imports both
`ntpath` and `posixpath` at module scope so that it can provide pure path
classes for both path flavours.  The invocation-scoped REI import observer
records the actual imported root and therefore correctly rejects `ntpath`
when that transitive standard-library dependency is absent from the closed
allowlist.

## Allowed change

Only this semantic field may change:

```text
runtime_closure.declared_import_roots
```

Exact delta:

```text
+ ntpath
```

The list remains sorted and unique.  The production bridge, all 17 declared
source paths and their hashes, the forbidden roots `jax` and `jaxlib`, Rust
source, MPFR/GMP identities, numerical coefficients, tolerances and physics
claims remain unchanged.

## TDD sequence

1. `test_ntpath_runtime_closure.py` is committed first and requires the
   currently missing root.
2. `patch_ntpath_closure.py --assert-red` confirms the exact pre-patch closure.
3. `patch_ntpath_closure.py --apply` changes the one field and writes a
   create-only receipt.
4. `patch_ntpath_closure.py --verify-green` checks:
   - the exact one-root delta;
   - cached `ntpath` import is observed and admitted;
   - an unrelated `random` import remains undeclared;
   - `jax` remains forbidden;
   - the production bridge SHA-256 is unchanged.

## Physics and claim boundary

This is a software import-closure repair.  It does not alter or validate REI
thermochemistry, photon conservation, finite-optical-depth allocation, the
Rust/MPFR interval operator, generic Bianchi transport, global tilt, or the
finite-electron collision operator.

A green closure workflow authorizes only construction of a new exact-pinned,
one-attempt standalone runtime handoff.  It does **not** authorize reusing the
consumed attempt claim, silently retrying the old handoff, promoting the first
canonical interval, exporting a provider, merging the Draft PR, or changing
Atlassian workflow state.

```text
runtime_bridge     STOP_INVALID until a new fresh standalone rerun
first_interval     NO_PASS_FIRST_CANONICAL_INTERVAL
provider_export    NOT_AUTHORIZED
scientific_pass    NOT_CLAIMED
```
