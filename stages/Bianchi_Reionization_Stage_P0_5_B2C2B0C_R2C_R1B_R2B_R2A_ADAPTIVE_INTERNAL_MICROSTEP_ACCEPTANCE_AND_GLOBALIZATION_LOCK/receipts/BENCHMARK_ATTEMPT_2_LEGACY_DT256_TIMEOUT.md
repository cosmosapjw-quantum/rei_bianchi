# Benchmark attempt 2 — legacy physical dt/256 timeout

The source-equivalent pre-optimization implementation at `d978d09` did not
complete its physical warmup plus the predeclared three `dt/256` repetitions
inside 600 seconds.  No partial timing is promoted and the empty JSON target was
removed.  This is consistent with the earlier 900-second broad partition-sweep
timeout, but it is not used as a parity benchmark because the legacy tail-node
roundoff correction also changed the fixed-point trajectory.
