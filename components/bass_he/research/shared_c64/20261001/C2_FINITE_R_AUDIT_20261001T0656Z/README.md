# C2 finite-R audit package

Read `C2_FINITE_R_AUDIT_KO.md`, `CLAIMS.json`, and `NEXT_HANDOFF_KO.md` before execution. A successful task process is not a scientific convergence verdict. This package preserves failed force-integral gates; C2 and D1 promotion remain blocked.

The full archive contains the 39 prolate state pairs, eight new spherical anchor states, exact task inputs, immutable execution identities, independent review, and all quadrature/continuation records. The public Git namespace contains selected text evidence and code; raw binary states are in the archive. Parent C1b R2 checks are reused, not silently recomputed.

The current environment is GNU Fortran13.3/OpenMPI4.1.6, Python3.12.14, NumPy2.3.5, SciPy1.17.0, mpi4py4.1.2. C2 prolate eigenproblems still use the pinned C1b solver and optimized BLAS/LAPACK. Scalar BSpline evaluation and Fortran/OpenMP/SIMD direct/force contractions accelerate the operators. The original operator implementation is `reference/coupling.py`; the CLI `reference` backend is the scalar-spline Python comparison implementation in `prolate_fast.py`. Physical parity with the original implementation is recorded separately in `review/`.

## Reproduction

Keep existing result folders. Primary solve, grid, anchor, and continuation evidence writers are create-only. For a new authorized solve, build the strict native library with a local GNU Fortran toolchain:

```bash
FC=gfortran python native/build.py --mode strict
```

A new build has its own source/compiler/binary identity. Never claim the supplied binary SHA for a rebuilt binary. Native source and binary identities are validated; no backend fallback is allowed. `-Ofast`, fast-math, mixed precision, and unordered floating-point reductions are excluded.

The NCP launcher inspects actual topology, CPU quota, memory availability, and 20% memory headroom. Review the command it prints before using `--execute`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/launch_ncp.py \
  --manifest inputs/PROLATE_TASKS.json --output-dir /absolute/new/output \
  --backend native --ranks 32 --threads 1
```

This is a candidate layout, not a measured 64-core optimum. Rank0 is the controller. The 39 tasks bound useful independent workers; excessive ranks leave idle workers. NCP64 scaling is NOT_RUN. Local evidence used four ranks/three workers without core binding because the sandbox cannot apply hwloc binding; the NCP launcher retains core binding and no oversubscription.

`code/state_io.py` loads archived coefficients without an eigensolve. `code/analyze_grid.py` evaluates the registered gates. `code/analyze_continuation.py` checks physical common-O overlaps and adopts a phase only after numerical quadrature passes. Its supplied results already exist; do not overwrite them.

The independent spherical anchor audit can be reconstructed without the full parent archives by using the byte-pinned minimal dependencies:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python code/analyze_anchors.py \
  --hpc-parent private_dependencies/HPC_PARENT \
  --c1b-parent private_dependencies/C1B_PARENT
```

This reads coefficients and computes independent direct operators; it does not solve new states. For the next iteration, preserve these states and preregister the remaining integration work before computing. See `NEXT_HANDOFF_KO.md` for the single unresolved dependency.

## Interpretation

The two selected lowest fixed-m branches and their dark azimuthal partner are not a rank-five H1s+He n2 cluster. Finite-box eigenresiduals, finite-grid refinement, and asymptotic scaled diagnostics are not continuum error enclosures. No collision propagation, cross section, Eq55 calculation, or production-default change is included.
