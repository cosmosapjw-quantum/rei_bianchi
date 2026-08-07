# Performance benchmark and backend decision

- Owner-kernel legacy: `22.208008802 s / 100` calls.
- Owner-kernel candidate: `0.697513076 s / 100` calls.
- Speedup: `31.838842x`.
- Process maximum-RSS reduction: `0.848726%`.
- Owner hot path: **promoted**, because the predeclared `>=5x` speed gate closes with parity.
- Candidate physical `dt/256`: `4.365894005 s` per trial over three repetitions.
- Legacy physical benchmark: timed out before a comparable parity result; no whole-solver speedup is claimed.
- JAX thermal candidate: unit parity passed, but science-sequence synchronization stalled; it is diagnostic only.
- Stable production backend: `NUMPY_ARRAY_ORACLE`.

The optimization changes no scientific authorization.
