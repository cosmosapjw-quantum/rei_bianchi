# FULL005 pair diagnostics implementation

## C1 — goal and baseline

The frozen R10 contract calculates continuous piecewise-linear reconstruction diagnostics using dimensionless d ln(a). Baseline file hashes match CONTRACT.json. The supplied snapshot has no Git metadata; publication belongs to the controller/publisher. R10 immutable capture released this implementation. Existing successful FULL005 postprocessing and physical validation are reused; native solver runs and physical-history reads in this unit remain zero. All tests below use small synthetic arrays or files. Current actual full-history continuous norms remain NOT_RUN.

The helper and standalone use only Python standard library. Test-only moderate-fixture comparisons use the frozen relative 1e-12 and absolute 1e-14 tolerances; these are not physical acceptance thresholds. C9 and C10 belong to the independent reviewer and publisher.
