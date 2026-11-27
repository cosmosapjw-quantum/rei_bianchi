# Audit-led DR8 adaptive Eq. (54) reconstruction and analytical optimization

Goal: replace false branch certification and inefficient repeated work, preserving the published approximation scope.
Authority: CPC 286 (2023) 108662, attached 2010 END paper, legacy DR7 archive SHA efcc252fcf0bfc8ed8d4a36949c0d1ee859835bd356c3fb5a0b317a1dd6625b8.
User-approved sequence: adversarial audit -> mathematical/physical alternatives -> derived optimizations -> code -> new tests -> pilot -> Git publication.

## Recovery
DR8 directory contains only README.md and README_KO.md, both still describe DR7. No DR8 executable payload or completed numerical result is present. Do not inherit transcript-only execution.
Seven returned archives: transport/manifests checked; these do not prove physical correctness.

## New bounded work units
- A1: formulate explicit branch degeneracy witness; downgrade prior coalescence certificate, preserve baseline.
- A2: prove rotating-frame gauge removal, sparse column action, identity-tail subtraction, and energy-independent geometry reuse. Compare alternatives in RESEARCH_REPORT.
- C1 `src/bass_he/spectral.py`: analytic continued-fraction derivatives; F=0 and det(dF/d(p,lambda))=0 root; monodromy diagnostic.
- C2 `src/bass_he/rotation.py`: gauge-regularized polynomial Hamiltonian, fourth-order unitary Magnus, parity subblocks, batched energies/rho, no singular rho=0 path.
- C3 `src/bass_he/transport.py`: sparse Eq50 initial-column propagation, explicit exponent lanes, disjoint sink vs bound-channel reporting, finite off-diagonal Eq54 only.
- C4 `src/bass_he/geometry.py`: reference-seeded geometry and contour error/branch diagnostics; reuse geometry across energies, process-level parallelism with per-job durable JSON receipts.
- V1: failing tests first; post-fix counterexample rejection, analytic Jacobian checks, monodromy, gauge equivalence, dense/sparse identity, batching/scalar equality and probability bounds.
- V2: limited post-upgrade pilot and timing; no old DR8 full run, no unrelated already-passed test loops.
- P1: clean repository commit and non-force push. Repository is public and initially empty; exclude raw private runtime paths, attached PDFs, tokens and binary caches.

## Stop and claims
No continuum/thermal/production closure. Any ambiguous sheet or failed numerical budget is explicitly rejected. No imputation of missing scientific results. Push requires successful actual remote acknowledgement, not merely push permission in metadata.


## AUDIT2 DR8 adaptive update

Canonical base: GitHub `main@6ef63136d14dbe68a1c9eff4a43fece78cd87b35`, tree `1d6bcd2ef0d57849826650a3c02de4789668292c`. Work branch: `audit2/adaptive-eq54`.

### Closed bounded units
- D1: transform Eq. (54) to `u=rho^2`, so `2*pi*rho drho = pi du`; split exactly at every known Eq. (52) support cutoff and inherited rotational matching boundary.
- D2: component-wise adaptive Gauss-Kronrod quadrature. `gk7` (Gauss-3/Kronrod-7) is the economical adaptive lane; `gk15` (Gauss-7/Kronrod-15) is an independent verification lane. A summed total cannot hide an unconverged material component.
- D3: shared geometry evaluation for energies `0.5, 5 keV/u` and exponent factors `1,2`. The factor lanes remain independent physical/source policies even though they reuse identical `Delta(rho)`.
- D4: exact geometry anchors plus local cubic interpolation in `u=rho^2`. The surrogate is usable only after exact held-out sentinels pass; extrapolation outside a branch support interval is forbidden.
- D5: rotational matching-radius sensitivity with `R_cut_scale={0.9,1.0,1.1}` and S23 contour-panel sensitivity separated from radial quadrature error.
- D6: cache scientific dependencies split by EP / geometry / transport ownership. Scratch cache re-key was allowed only after AST equality of the contour kernel and clean spectral dependencies; it is not a general cache-migration policy.

### Fresh numerical gates
- pre-interruption final suite recorded `48 passed in 8.87s`. After runtime interruption and publication reconstruction, the reconstructed publication tree was freshly reverified: `48 passed in 5.51s`; `git diff --check`, package build/install/import and `compileall` passed. The pre-interruption tree hash is historical evidence only; `evidence/DR8_FINAL_VERIFICATION.json` is the publication-verification authority.
- exact support-split GK7 at 2%: 7 intervals, 49 evaluations, no refinement, component-wise gate pass.
- surrogate runtime validation: 10 exact held-out sentinels, maximum relative `Delta` error `1.388034624856879e-05` against threshold `2e-4`.
- broader held-out study: 212 exact cached GK15 geometry points; maximum local-cubic relative `Delta` error `4.3469e-05` (S23), with other branches smaller.
- surrogate 0.2% adaptive: GK7 8 intervals / 63 evaluations / 1 refinement; independent GK15 7 intervals / 105 evaluations / 0 refinements.
- GK7 vs GK15: maximum component relative difference `3.3442230407223834e-05`, relative L1 difference `4.3540716529505146e-06`.
- S23 contour panels 32->64 at rho={0,0.5 support,0.9 support}: maximum relative change `2.2470166629794012e-06`.

### Model-systematic gate
The 0.2% quadrature target is not the dominant uncertainty in every lane. A ±10% rotational matching-radius change moves the total indexed reaction-loss area by approximately:
- factor=1, E=0.5 keV/u: `-0.478%, +0.510%`;
- factor=1, E=5 keV/u: `-0.0118%, +0.0137%`;
- factor=2, E=0.5 keV/u: `-6.44%, +6.82%`;
- factor=2, E=5 keV/u: `-0.111%, +0.125%`.

Therefore Eq. (54) numerical convergence does **not** promote the low-energy model to production. Eq. (52)/Eq. (55) exponent ambiguity, stochastic-vs-coherent dynamics, straight-line trajectory validity, upper-shell semantics and rotational matching-radius authority remain independent gates.

### Next bounded units
- DR8V: independent exact-node validation of the `Delta(u)` surrogate near support endpoints and any adaptive-refinement node; no claim of a global interpolation error bound.
- DR9A: physical-model comparison lane for straight-line/static-Coulomb vs trajectory-aware references, beginning with energies where the source assumptions overlap.
- DR9B: resolve or externally constrain Eq. (52)/Eq. (55) exponent normalization before any production cross-section claim.
- Optional numerical oracle: independent prolate-spheroidal collocation/generalized-eigenvalue calculation for selected complex-R branches.

Heavy local handoff is not opened by default. Sandbox-first remains canonical; local execution is used only after measured wall-time/memory establishes a genuine heavy workload. Final publish verification is recorded in `evidence/DR8_FINAL_VERIFICATION.json`.
