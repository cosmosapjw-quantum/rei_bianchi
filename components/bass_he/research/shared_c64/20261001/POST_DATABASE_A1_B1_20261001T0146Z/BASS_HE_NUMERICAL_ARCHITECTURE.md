# First-loop architecture boundary

Status: FORMULATION_CONTRACT_ONLY. C1 electronic solver architecture is not frozen: physical A1 remains open. This file fixes only the interface derived and checked during A1.

The input is a hash-bound basis definition χ_a(r,t), with its explicit origin, active rotation, ETF field, channel/subspace labels, nuclear-path convention and physical units. It must supply S, h=q_t(χ_a,χ_b), D=〈χ_a|dotχ_b〉 and Sdot, all evaluated from the same basis. If W†SW=I is used, Wdot is also an input. The output is K=W†(h−iℏD)W−iℏW†SWdot.

`A1/code/connection_algebra.py` validates and evaluates this matrix identity. It supplies no Coulomb eigenstates, radial coupling, ETF choice, nuclear trajectory or cross section. It rejects non-Hermitian h, inconsistent Sdot, singular or overly ill-conditioned S, inconsistent W/Wdot, and non-Hermitian K. It never repairs K by averaging it with K†. The condition threshold 1e8 and scaled algebra tolerance 1e-12 apply only to these fixtures; they are not electronic-convergence tolerances.

The direct reference is Y=XW, K=Y†HY−iℏY†Ydot for finite matrix examples; the second formulation uses the metric matrices. Twelve tests include static limits, norm preservation, non-Abelian and rephasing covariance, moving-origin cancellation, common boost, R10R sign placement, and failure cases. The exact static-H `expm` example is a matrix fixture, not a collision propagation run. Wall time is recorded; no speedup, physical convergence, memory-scaling or parallel-efficiency claim is made.

Reproduce the existing algebra tests with `python A1/code/test_connection_algebra.py` in an environment containing NumPy and SciPy. Recorded versions are NumPy2.3.5, SciPy1.17.0, Python3.12.14. To generate another create-only evidence set using `run_checks.py`, first copy the `A1/code` directory into a fresh empty run directory; its sibling `evidence` must not contain the output filenames. Do not overwrite the delivered evidence.

Deferred C1 comparison remains: prolate-spheroidal separation, high-order FEM/spectral elements, B-splines, DVR/Lagrange mesh and two-center orbitals. No winner is selected before A1b fixes asymptotic subspaces and ETF embedding. C2 direct/commutator coupling checks, D1 propagation, D2 quadrature, E1/E2 channel/continuum convergence, F1/F2 trajectory/Stokes and G1 frozen benchmark comparison are NOT_RUN.

Any later cache key must include exact source commit, convention/basis/grid identities, tolerance, state/subspace label, R token and frame. The current matrix helper does not create a physical cache. Each later numerical node must preregister its own reference method, efficient method, convergence tests and failure policy before consuming external benchmarks.
