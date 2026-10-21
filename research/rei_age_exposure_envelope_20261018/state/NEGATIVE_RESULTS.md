# Negative and limiting results

- Original native time8↔16 and time16↔32 target of 0.005 is not met for the selected scalar set.
- Naively applying `log2(relative_distance_8_16 / relative_distance_16_32)` gives a denominator-dependent quantity, not the raw-difference three-level slope. Do not label it convergence order.
- Finite-grid slopes are not an error bound, solver contraction theorem, continuum certificate, or production result.
- Stored positive DOP853 age32 is not interchangeable with native BE.
- First diagnostic script attempt used the wrong mesh parity index and exited1; failure preserved. Corrected script verifies `fine[1::2] == coarse` and passes.
- The current PR CI root `cargo fmt` check fails and workspace tests were skipped; this scoped diagnostic does not resolve those checks.
