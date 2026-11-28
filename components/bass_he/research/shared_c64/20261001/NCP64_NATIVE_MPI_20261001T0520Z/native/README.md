# Fixed-order Fortran element kernel

Build with `python native/build.py --mode strict`. GNU Fortran and an OpenMP
runtime are required. `--mode debug` builds a separate bounds-checked library
with FPE compiler flags; hardware exception trapping is host/runtime dependent
when a Fortran shared library is loaded by Python.
An optional, separate local-ISA build uses `--native --output-dir native/build-native`.
The default portable build does not use `-march=native`. The adjacent
`libbass_element.build.json` records the compiler binary/version/target, source
SHA-256, all flags, library SHA-256, and actual vectorization diagnostics.
External `FFLAGS` are intentionally not consumed.

The Python API is `native_backend.element_blocks(B, gaunt, vl, weights, kin,
cent, ls)`. Inputs must be finite NumPy float64 arrays, with int64 nonnegative
strictly increasing `ls`. Shapes are `B[nq,na]`, `gaunt[nk,nl,nl]`, `vl[nq,nk]`,
`weights[nq]`, `kin[na,na]`, `cent[na,na]`, `ls[nl]`. Output is C-contiguous
`blocks[nl,na,nl,na]`. Neither Gaunt nor radial matrix symmetry is assumed.
Input arrays must not be mutated by another Python thread during a call.

For repeated elements use `kernel = prepare_element_kernel(B, gaunt, ls)` once
per solve, then `kernel.blocks(vl, weights, kin, cent)` per element. Preparation
validates the large Gaunt tensor once and retains an owned read-only copy;
subsequent caller mutations cannot change the prepared tensor. Only the small
element-varying arrays and output are checked on each element call.

ABI 3 uses C value int32 dimensions `(nq,na,nk,nl)`, six const double pointers
`(B,gaunt,vl,weights,kin,cent)`, a const int64 pointer `ls`, and a double output
pointer. B uses C-contiguous storage, seen as Fortran `basis(na,nq)`; vl/kin/cent
use Fortran-contiguous storage. Gaunt uses C-contiguous storage, seen as Fortran
`gaunt(nl,nl,nk)`, so the angular j index is contiguous. Output C `(i,a,j,b)` is Fortran
`blocks(b,j,a,i)`. Python validates shapes/dtypes and owns converted buffers.
Direct C callers are responsible for the same validation; the native ABI
alone does not validate arbitrary pointers.

The two sums are increasing-k (multipoles) and increasing-q (quadrature).
OpenMP distributes distinct angular rows `i` using static scheduling.
SIMD operates across distinct angular columns `j` in the first stage and distinct
radial output entries in the second. No OpenMP reduction, fast math,
reassociation, symmetry-copy shortcut, or changed quadrature is used. All
physical inputs and discretization remain caller
controlled. Roundoff ordering differs from NumPy/BLAS contractions, so
numerical agreement must be checked; byte identity against NumPy is not claimed.
Thread-count byte identity is checked separately in the synthetic kernel test.

Set `OMP_NUM_THREADS`, `OMP_DYNAMIC=FALSE`, and BLAS thread limits before launching
Python. `native_info()` records the loaded library SHA and OpenMP maximum threads.
`BASS_NATIVE_LIBRARY` selects an explicit alternative library;
`BASS_NATIVE_EXPECTED_SHA256` optionally enforces its digest. Missing libraries,
ABI mismatches and absent/stale build metadata fail; no fallback occurs. SHA is measured
at initial load, not after arbitrary external replacement of an already mapped file.

Run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 python native/test_native.py`.
For the bounds/FPE build, also set
`BASS_NATIVE_LIBRARY=/absolute/path/native/build-debug/libbass_element.so`.
These are kernel tests, not physical convergence or 64-core scaling evidence.
