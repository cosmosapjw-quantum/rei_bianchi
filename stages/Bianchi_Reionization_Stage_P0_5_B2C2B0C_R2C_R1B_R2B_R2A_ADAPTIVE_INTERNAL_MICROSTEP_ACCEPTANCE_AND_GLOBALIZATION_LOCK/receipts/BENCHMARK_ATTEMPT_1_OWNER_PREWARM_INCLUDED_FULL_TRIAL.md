# Benchmark attempt 1 — owner benchmark polluted by full-trial warmup

The first corrected harness still executed a full physical `dt/1024` trial
before the owner-only benchmark.  On the pre-optimization legacy commit this
warmup dominated and exceeded the harness timeout, so no owner timing was
recorded.  The owner benchmark was corrected to warm only the owner kernel;
physical-trial warmup remains confined to physical benchmarks.
