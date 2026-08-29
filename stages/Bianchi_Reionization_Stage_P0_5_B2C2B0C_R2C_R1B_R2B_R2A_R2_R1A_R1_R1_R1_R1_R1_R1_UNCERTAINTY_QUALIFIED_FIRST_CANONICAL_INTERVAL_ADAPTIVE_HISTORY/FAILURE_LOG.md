# Failure log

## Inherited long-lived worker stall

Earlier endpoint sweeps accumulated numerical-runtime/BLAS state and stalled;
even chunks were unreliable while each file passed alone. This rules out a
persistent pool. Retry only with short-lived workers, one-thread BLAS, timeout,
and distinct transport failure.

## Environment bootstrap limitation

The branch runtime has NumPy/SciPy but lacks pytest, SymPy, mpmath, JAX, Rust,
and Wolfram. Use stdlib `unittest`; record unavailable optional validation.

## Known table-event blocker

The predecessor exposes detection and a synthetic localizer, but no certified
actual-step callback or source-cell rebuild API. Stop, preserve parent, and
package the receipt; implement the missing scientific primitive separately.

## Supervisor cleanup sentinel failure during implementation

An initial controller test replaced a temporary-directory variable with
`Path()` after commit; the `finally` block interpreted `.` as a cleanup target.
The disposable clean clone was removed and restored byte-for-byte from remote
main at `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`; no user result existed and no
external data was affected. This rules out truthy path sentinels. The corrected
implementation uses `None` and `_safe_rmtree`, which permits only a direct child
of an explicit generation/snapshot root. Unit tests then passed against the
restored repository.
