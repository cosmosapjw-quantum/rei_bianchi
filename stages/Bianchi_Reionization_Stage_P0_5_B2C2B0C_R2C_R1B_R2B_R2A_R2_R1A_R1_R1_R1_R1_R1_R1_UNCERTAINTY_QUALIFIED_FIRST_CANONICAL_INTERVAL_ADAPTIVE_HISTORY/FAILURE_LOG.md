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
