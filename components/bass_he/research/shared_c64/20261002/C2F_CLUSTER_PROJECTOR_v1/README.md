# BASS_HE C2f

Read `C2F_REPORT_KO.md`, then `C2F_NEXT_HANDOFF_KO.md`. This package implements finite-frame cluster contracts and projector transport; it is not a physical Coulomb eigensolver or a production collision model. `CLAIMS.json` and `review/INDEPENDENT_REVIEW.json` delimit the completed scope.

Python implementation: `code/projector.py`; exact API: `code/README_API.md`. Fortran overlap: `native/weighted_overlap.f90`; explicit MPI runner: `code/launch_manufactured.py`. The tested stack was Python 3.12, NumPy 2.3.5, mpi4py 4.1.2, Open MPI 4.1.6 and GNU Fortran 13.3. No automatic dependency installation or backend fallback is performed.

## Rebuild on the execution host

Use a new output directory so prior build evidence is preserved. Existing binary/metadata directories are historical evidence tied to their recorded source and compiler. The current source is v2b; a binary from `native/build/` is the earlier baseline and is not compatible with the current source identity check.

```bash
python native/build_overlap.py --compiler gfortran --mode strict --output-dir native/host-strict
python native/build_overlap.py --compiler gfortran --mode debug --output-dir native/host-debug
```

GNU Fortran and libgomp must already be available. External FFLAGS/FCFLAGS/LDFLAGS are rejected by the closed build profile. The archive includes tested binaries as evidence, while the Git namespace publishes source and metadata only. The bundled author unit-test paths refer to the recorded `build-v2b`/`build-debug-v2b` builds; host execution should use its explicitly selected fresh library and the affected manufactured integration check below. Completed source tests need not be replayed without an affected dependency.

## Bounded manufactured integration

From this package directory, choose an output path that does not exist. The launcher sets thread controls, performs actual host preflight and preserves errors. An MPI implementation other than Open MPI is rejected.

```bash
python code/launch_manufactured.py \
  --manifest contract/MANUFACTURED_TASKS.json \
  --execution mpi --backend native --native-library native/host-strict/libbass_overlap.so \
  --ranks 2 --threads 4 --binding core --mpiexec /absolute/path/to/mpiexec \
  --output /absolute/new-result.json
```

For an unbound constrained host, explicitly use `--binding none`. Reference execution uses `--backend reference` and omits `--native-library`; `--execution serial` requires `--ranks 1`. These are separate explicit choices, never fallback routes.

`contract/NCP64_MANUFACTURED_TASKS.json` prepares 64 synthetic tasks, 96 GiB sampled memory budget and a 180 s wall limit for the intended host. Candidate layouts include 64×1, 32×2 and 16×4 when actual topology/quota and free memory admit them. It has not been run on NCP. It does not authorize molecular solves. Compare identical cases and retain numerical parity before interpreting performance; short-task launch overhead can dominate.

The local overlap microbenchmark showed reference BLAS faster than native for every measured small-rank workload. `review/PERFORMANCE_DECISION.json` retains that result; Fortran is not selected merely because it is compiled. To measure the same microbenchmark with a fresh host library:

```bash
OMP_NUM_THREADS=4 OMP_DYNAMIC=FALSE OMP_PROC_BIND=close OPENBLAS_NUM_THREADS=1 \
  python code/benchmark_overlap.py --native-library native/host-strict/libbass_overlap.so \
  --output /absolute/new-benchmark.json
```

Use `docs/RUNTIME_KO.md` for process ownership, Linux namespace/cgroup support and sampled-watchdog limitations. The actual molecular provider, common-grid map and concrete physical reference contract are next, as specified in the handoff.
