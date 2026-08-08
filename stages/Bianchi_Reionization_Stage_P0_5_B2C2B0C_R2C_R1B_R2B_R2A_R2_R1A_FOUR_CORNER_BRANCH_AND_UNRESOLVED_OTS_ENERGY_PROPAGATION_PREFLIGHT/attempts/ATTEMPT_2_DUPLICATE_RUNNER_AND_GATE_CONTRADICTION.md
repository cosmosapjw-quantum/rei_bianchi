# ATTEMPT 2 — duplicate runner and gate contradiction

Classification: `PRECALCULATION_POLICY_CONTRADICTION_CORRECTED_BEFORE_SCIENCE`.

Two propagation runners were introduced by overlapping TDD tracks. `run_preflight.py` incorrectly allowed four endpoint trajectories to authorize the continuous nonlinear branch family and used Python `hash()` for parent identities. The approved design and the later input-lock hypotheses require an independent continuous-parameter enclosure certificate. The same input lock also stated that the source-uncertainty gate remains `2e-3` while its numeric fields accidentally contained `2e-4`.

Disposition:

- `run_four_corner_preflight.py` is the sole canonical runner.
- numerical local error remains `<2e-4`; source-model enclosure width is `<2e-3`;
- narrow corners without a validated continuous-parameter certificate remain fail-closed;
- parent and endpoint identities use SHA-256;
- the duplicate runner and its test are removed, with their failed log preserved below.

No science calculation had started when this correction was made.
