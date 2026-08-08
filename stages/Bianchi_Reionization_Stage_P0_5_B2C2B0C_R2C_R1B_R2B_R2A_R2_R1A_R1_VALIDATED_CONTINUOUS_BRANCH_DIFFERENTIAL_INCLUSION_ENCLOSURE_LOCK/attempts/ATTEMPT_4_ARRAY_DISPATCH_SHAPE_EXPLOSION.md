# Attempt 4 — ndarray/Interval dispatch produced shape explosion

The first full interval-RHS process was killed after resident memory grew to about 3.9 GiB.  Root-cause tracing found that NumPy dispatched a mixed ndarray/Interval multiplication through ndarray semantics because the interval class lacked a dominant array priority.  This recursively materialized object/broadcast intermediates rather than a componentwise interval result.

Correction: `Interval.__array_priority__ = 10000`, a broadcast-size guard, and allocation-free four-product min/max multiplication.  This attempt is numerical infrastructure evidence only and carries no scientific verdict.
