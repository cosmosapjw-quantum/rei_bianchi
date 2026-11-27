# Accuracy-preserving HPC research policy
This namespace implements the owner request of 2026-10-01 for subsequent BASS_HE research.
Read HPC_POLICY_KO.md, CONTRACT.json and NEXT_HANDOFF_KO.md before new numerical work.
Default architecture: explicit OpenMPI task parallelism, Fortran binary64 hot kernels,
OpenMP/SIMD inside kernels where measured useful, Python for orchestration and an
unchanged reference lane. Choose rank/thread layout from measured host throughput.
Do not alter physics, conventions, discretization, tolerances or claim gates for speed.
No fast-math, hidden mixed precision, rounded cache keys, implicit backend fallback,
MPI floating-point science reductions or benchmark-target fitting.
Validate changed kernels against the pinned reference; benchmark identical workloads.
Frozen C1b science is reused; this optimization node does not execute the C2 R grid.
A failed parity, resource, state-identity or code-identity gate fails closed.
