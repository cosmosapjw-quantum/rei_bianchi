# Cached residual QR implementation: observed local execution

Implemented `code/residual_qr.py` against the frozen
`spec/RESIDUAL_CONTRACT.json`. The public functions are `streamed_qr`,
`streamed_residual_factor`, and `residual_diagnostic_qr`. The factor API returns
`(J, R, delta_row, norm_u, scale_diagnostics)`. The diagnostic API returns the
seven Unit5-compatible eta-major arrays plus `summary`.

The first row pass validates finiteness and accumulates C, the conjugated
coordinate row, and cache norms. The second forms only row blocks of d and E
and applies sequential reduced Householder QR. No global E/A, rank truncation,
diagonal division, Gram norm, Hamiltonian callback, operator import, or runner
modification is used. Evaluation uses a single Hermitian eigendecomposition
and batches of at most 256 points. Float64/complex128 arrays and memmap views
are not globally copied by input conversion; lower floating precision is
promoted. NPZ CLI loading materializes V/KV/u and does not provide disk
streaming. Summaries separate existing cache storage from estimated extra
workspace; the estimate excludes BLAS/LAPACK internals and Python overhead.

The CLI requires an explicit weight and a new directory, uses
`numpy.load(..., allow_pickle=False)`, ignores other checkpoint keys, and
writes `residual.npz` and `residual_summary.json`. Its defaults are 2001 points
over 0–20 Eh and eta 0.05, 0.1, 0.2 Eh. The CLI caps m at 128; the local
validation stayed within N<=512,m<=32.

## Executed verification

One bounded suite plus one prescribed performance comparison was executed
with Python and NumPy versions/BLAS configuration in `results/laneA/runtime.json`
and `numpy_config.txt`. All five thread environment variables were fixed to 1.
The execution command was:

```sh
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 timeout 29s \
  python tests/run_residual_evidence.py
```

Eight test methods passed in 0.232 seconds. They cover exact real/complex/
nonorthogonal fixtures, seeded real and complex Hermitian matrices, independent
dense scalar solves, nonzero initial-coordinate defects, near invariance,
short and unequal blocks, rank deficiency, the standalone tiny cancellation
example, invalid inputs, inconsistent synthetic cache algebra, and a synthetic
CLI smoke/no-overwrite check. The tiny fixture returned norm 1e-10; its raw
Gram quadratic value was 0. The inconsistent cache is explicitly excluded from
the physical full-space bound claim. Per-fixture dimensions, block sizes,
norm/bound/scalar discrepancies, solve defects, dense scalar errors and B
values are retained in `test_observations.json`. Raw stdout/stderr and CLI
stderr are retained without discarding failures; the observed suite had none.

The single seed20261016 float64 benchmark used N=512,m=32,P=6003 and identical
arrays. Direct setup/evaluation/total were 0.000240472/0.131808403/0.132048875 s;
QR setup/evaluation/total were 0.001175639/0.010428353/0.011603992 s. The observed
direct/QR total ratio was 11.3796. The maximum norm discrepancy was
2.34479e-12, maximum B discrepancy 4.68390e-11, and maximum normalized norm
discrepancy 0.000988325 of the frozen allowance. Reported cache storage was
266240 bytes and extra-workspace estimate 1554512 bytes. The timing is one
bounded local observation, not a production performance measurement or gate.

Requested execution model: gpt-6.1-sol. Observed runtime model: UNKNOWN.
The working artifact directory has no Git checkout; status/HEAD/branch/remote
inspection returned “not a git repository.” Unit5 was read-only. No actual
394 MB checkpoint was loaded, no physical H/NCP action was performed, and no
actual-refinement admission changed. Scientific admission remains pending
independent authority review; production timing is NOT_MEASURED and actual
checkpoint execution is NOT_RUN.
