# REI UVB shape innovation diagnostic

Single bounded attempt `outputs/attempt001` completed with exit 0 and seven new control groups passing. The actual-data amplitude-profiled and contrast statistics both equal Q = 19.381736839571925. For the fixed-template, fixed-EOS, Gaussian statistical-only null with six degrees of freedom, p = 0.003565238159436219, yielding the predeclared `CONDITIONAL_STATISTICAL_SHAPE_TENSION` descriptive flag.

The calculation retains all seven observations and the original correlated statistical covariance. It reuses the saved template; it does not calculate new rate tables. Six adjacent contrasts expose local observed/template ratio discrepancies. Seven dependent leave-one-out innovations expose conditional predictive residuals. Neither set of marginal Z values may be summed as independent evidence. Template selection used the full observations, so this is not independent held-out validation. Jeans/systematic covariance and selection corrections are absent. Physical F4 remains partial; global completion delta is zero.

Production uses standard-library binary64 Cholesky solves and explicit residual quadratics. A separate Decimal60 partial-pivot Gaussian elimination implementation checks Q, beta, contrasts and all seven deletion diagnostics. Fixed tolerances are relative 1e-10 plus absolute 1e-12, with variance absolute 1e-15 dex squared. Raw differences are retained without clamping. New controls cover block identities, normalization shifts, weighted diagonal predictive oracle, actual and synthetic correlations, joint permutations and invalid inputs. No old tests, production source imports, IVPs, rate calls, NumPy/SciPy or network calls occurred.

See `outputs/attempt001/RESULT.json`, `TEST_RESULT.json`, `DECIMAL60_REFERENCE.json`, both CSVs and `covariance.json`. `outputs/RUN_RECEIPT.json` records child CPU 0.046631 s, wall 0.06185467 s and peak RSS 12416 KiB, with wrapper overhead separate. The new orchestration ledger reserves child 10 CPU s / 30 wall s / 512 MiB plus wrapper 1 CPU s / 5 wall s; owner ledger debits are unchanged. Host/global overhead is unknown, not zero.

Original command (already executed once; do not replay by deleting evidence):

```
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python run_bounded.py --cpu-limit 10 --wall-limit 30 -- /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python suite.py --inputs /workspace/scratch/d855c1e0c0ed/orchestration_20261028/authority/rei/inputs --output /workspace/scratch/d855c1e0c0ed/orchestration_20261028/release/research/orchestration_sync_20261028/rei_uvb_shape_innovation/outputs/attempt001
```

The runner additionally needs the task's `helpers/bounded_child.py` at the recorded orchestration-relative path. Scientific admission remains pending fresh nonauthor review of the actual code and outputs. No new plot was required.
