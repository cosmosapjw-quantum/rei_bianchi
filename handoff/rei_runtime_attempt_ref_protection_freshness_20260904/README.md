# REI runtime attempt-ref protection freshness and live revalidation

This package is the minimal GREEN successor to Draft PR #48.

It does not create a repository ruleset during CI and does not run the native
REI bridge.  It adds four fail-closed boundaries before the one final global
attempt reservation:

1. a structurally valid source protection receipt must also be fresh, bounded,
   unexpired, and not materially future-dated;
2. after complete successor-toolchain re-attestation, the controller performs
   fixed-authority GET-only live reads of the prospective branch rules,
   contributing active ruleset details, and exact global-ref absence;
3. the live receipt and its source protection receipt are both hash-bound into
   the global lease record;
4. the post-lease worker revalidates those files and hashes before entering the
   unchanged production runtime.

The live observer uses only `https://api.github.com` and
`cosmosapjw-quantum/rei_bianchi`.  It contains no POST, PATCH, DELETE, ruleset
mutation, ref mutation, or production-bridge import.

## Strict execution boundary

```text
repository ruleset             NOT CREATED BY THIS PACKAGE
live target-host readback      NOT RUN
fixed global attempt ref       ABSENT / NOT ACQUIRED
persistent local lease         NOT CREATED
native runtime                 NOT RUN
remaining native attempts      1
first canonical interval       NO PASS
provider export                NOT AUTHORIZED
```

After exact-head GREEN, the next node is a separate administrative operation
that creates and reads back the server-side ruleset while leaving the global
attempt ref absent.  Only after that operation and a fresh target-host static
preflight may the final reservation/native attempt be considered.
