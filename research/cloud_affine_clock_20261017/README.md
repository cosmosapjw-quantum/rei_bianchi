# Externally prescribed affine scalar photon clock

Second bounded cloud DAG step from source commit `a50c379a4a533054ccecc49938133a7df7426fbc`, published additively after `8c56aa5ac20d9bf0f08b73dd57e7fee8ef19b363`. The first fixed-geometry Phi/cohort lane is unchanged. This self-contained reference crate reuses unchanged prior blobs and all 12 owner modules.

Read `docs/AFFINE_RESULT_KO.md` and `docs/AFFINE_REVIEW.md` for the final step. Earlier RESULT/COHORT documents and unposted flags are historical stage records.

## Scoped result

The new scalar API assumes externally prescribed, nonnegative affine source j(t) and absorption lambda(t), with fixed photon energy and proper volume. Positive Gauss quadrature shares birth weights between surviving and absorbed photons. Constant coefficients reuse the exact Phi kernel. The variable-coefficient path supports integrated optical depth <=1; this is a supported-domain guard, not an accuracy certificate.

Final affine tests: 10 PASS. An earlier selected run also passed the 21 uniform-birth tests; the final guard change touched only the affine module. Saved 24 rows (four coefficient families, six grids) were checked against 100-digit mpmath. For three exactly affine families, N32 absolute survivor errors are 5.2742893e-10, 6.8868776e-10 and 5.9945977e-10, with observed N16-to-N32 order about 4. SymPy optical-depth and total-injection identities have zero residual. These results do not establish a coupled solver order. Endpoint linear interpolation of general smooth functions introduces its own, generally second-order, error.

The review-found underflow issue was corrected by forming endpoint rate*time integrals first. Unsupported positive underflow/overflow and subnormal variable-path integrals fail closed. Original failure attempts remain in the evidence history.

## Independent gates remain HOLD

There is no H/He/D species allocation, gas evolution or Bianchi transport in this scalar API. Time-varying channel proportions require joint integrals of lambda_i(t) N(t); a single endpoint ratio cannot generally allocate total absorption. Variable geometry, coupled second order, global convergence and full native histories remain HOLD.

## Evidence and costs

The cumulative COMMAND_LEDGER contains 30 commands, including prior 20, with measured wall 26.696080 seconds and child CPU 26.817213 seconds. The existing 300/600-second cap was not reset. These are measured command totals; whole-project costs remain UNKNOWN. No scientific execution occurred during publication. No Wolfram or local/NCP execution occurred in this cloud phase. Clippy remains unrun.

PUBLICATION_PROVENANCE maps original and published hashes. Executor paths in stderr are redacted; original command-ledger hashes still identify original outputs. The copied runner has the same optional RUST_TOOLCHAIN_BIN portability change as the first publication and has not been rerun. Unused local/Wolfram handoffs and all binaries, caches and private files are excluded. SOURCE_FILE_MANIFEST records all files except itself.
