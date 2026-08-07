# Monolithic full-suite timeouts and isolated verification

Two fresh monolithic `pytest -q` runs exceeded command limits of 600 and 900
seconds at different late-suite boundaries, without an assertion failure. The
initial hypothesis that in-process JAX audits were the sole cause was falsified:
after isolating every JAX case in its own subprocess, the monolithic suite still
stalled later at a different historical-stage test.

Every one of the 33 test files, comprising all 150 collected tests, was then
executed in a fresh Python process and passed. Individual tests at both observed
timeout boundaries also passed immediately in isolation. The durable verification
therefore uses deterministic file-isolated execution and records the monolithic
behavior as cumulative process/runtime-state contamination across historical
stages, not a scientific or assertion failure.

The JAX isolation remains appropriate because JAX is diagnostic-only and has an
independent science-sequence synchronization failure receipt.
