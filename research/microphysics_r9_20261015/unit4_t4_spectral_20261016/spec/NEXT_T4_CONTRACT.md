# NEXT T4 contract: saved-complement spectral diagnostic

Decision: proceed with one constructive finite-space T4 unit. Unit3 recovery succeeded; no additional V6 ground-state solve is justified. Selected stages for framing are PhysMath 1.3.0 C1–C4. The lower-tier executor implements the following complete path; a fresh Astra reviewer makes the scoped decision from its diff and actual outcomes. Existing AGENTS_CURRENT.md governs trusted-owner operation, typed identity and finite review.

## Baseline and allowed change

- Current intake repository head: `284916e758d87852a6137fbbb36befe83f15d271`.
- Unit3 source archive SHA256: `d25308b8e7f1a2ea0f6f3e203c074553c661511034d7dbc07920b1d0dd65bfa0`.
- Recovered NPZ SHA256: `7aa230b66d500e7637161589533eef4f3f4efdc13f4beafb7e28fd275ab82c5d`.
- Recovered receipt SHA256: `3ae0c54716df1a7cfc1586a2641e1b461dffd3a721ed77daa4ca676bb0c0c3c8`.
- Frozen V6 source SHA256: `31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c`.
- Frozen V6 input/contract SHA256: `289520d8aed460cdee460f5497762b0c613f003bd6ba43bb505416d945995097` / `cf7b06ad72815513e799be253539bdfecfb9102c1fc586589003e8b6fd364e4d`.
- Actual recovered case: `quench_Li_Be_union_aug_TZ_occ_list_v6`, 92 orbitals, CI shape `(4186,92)`, 385112 determinants; P=0.5756391820077925, W=0.42436081799220793.

Use the existing checkout for repository work, inspect its branch/HEAD/status, and preserve all unrelated changes. Within the task package, create only `code/t4_spectral.py`, focused `tests/test_t4_spectral.py`, result files and an NCP command/instructions file. Additional small helper modules are allowed if needed for a complete executable path. Do not edit historical source, contracts, saved arrays or receipts. No new credentials/remote tool calls; NCP control is currently unavailable. No owner PR150 transport execution or file changes. Latest separate owner intake is head `0e25846433170d0f420c4cda44a0bedbf02cd177` (23:15 UTC observation), with a completed native campaign awaiting its corrected postprocessor; inspect actual host resource availability rather than inferring a reservation from an old deadline.

The construction and residual-aware scalar formulas are frozen in `NEXT_T4_DERIVATION.md`. Immutable source/input bytes remain identified; rederived numerical outputs are checked by numerical agreement. This unit's claim is the finite projected measure of the saved complement under the same Be+ Hamiltonian. It is not an exclusive continuum or electron-capture calculation.

## Two executable modes

Implement `summarize` using only NumPy and standard Python. It reads actual NPZ/receipt, normalizes working copies, recomputes A/P/W, saved q identity, norms/RDM traces and closure, then evaluates the residual-aware conditional mean/second-moment/variance intervals and Cantelli upper bounds at 5/10/20 Eh. Preserve raw inputs and report assumptions. Also compare the actual saved aug-DZ receipt P with aug-TZ, if supplied; this single difference is a measured basis sensitivity, not an error bound or basis-closure decision. This mode MUST run now on restored actual Unit3 bytes.

Implement `run` as a complete NCP-local supervised path using NumPy/SciPy/PySCF and the frozen V6 `raw_action` routine. It reconstructs the same Be+ integrals using saved expanded shells and saved X, validates reconstruction, then extends a single two-pass reorthogonalized projected Lanczos basis to nested lengths 16/32/64. Continue to 128 only if the 32→64 broadening checks do not pass and the same wall/action budget allows it. Save each milestone. If 64 passes, stop with finite diagnostic convergence at the declared broadenings; if 128 does not pass, preserve actual partial/convergence-not-met output. No automatic new-budget replay.

Example exact interfaces (paths become absolute at invocation):

```text
python3 code/t4_spectral.py summarize --receipt <actual-recovered-receipt.json> --data <actual-data.npz> --aug-dz-receipt <saved-aug-DZ-receipt.json> --out <new-summary-directory>
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python code/t4_spectral.py run --receipt <actual-recovered-receipt.json> --data <actual-data.npz> --v6-source <frozen-microphysics_driver_v6.py> --out <new-T4-directory> --threads 12 --memory-gib 24 --wall-s 7200
```

The CLI may accept an explicit contract path. It must not expose silent tolerance/basis/model changes. The `run` supervisor must enforce wall and address-space/RSS limits, preserve stdout/stderr and partial results, and return a terminal receipt with success/partial/deferred/failure classification. Normal shell exit alone is never a scientific PASS. Use a new output directory; if an existing unfinished T4 checkpoint is explicitly resumed, it must continue its exact saved basis/actions/input identity and cumulative budget rather than restart work. A simpler implementation may omit resume and retain a reusable checkpoint plus an explicit not-implemented resume note; do not advertise a nonexistent resume interface.

## Reconstruction acceptance: PASS → begin Lanczos

Use PySCF 2.14.0 from the existing NCP environment where available; record actual runtime versions. Do not install or upgrade packages on NCP as part of this command. Expected NumPy/SciPy historical versions are 2.5.4/1.18.1. Local NumPy/SciPy availability is enough for summarize/tests; local PySCF absence is an NCP execution dependency, not a reason to omit the runner.

Rebuild Be+ at the origin, charge 1, spin 1, spherical (`cart=False`), no symmetry, atomic units, from `common_expanded_basis` in the actual receipt. Retain the supplied X and determinant ordering. Never solve SCF/FCI or diagonalize S for new orbitals. Construct h and ERI, then call immutable V6 raw_action (its >=64 triangular links are necessary).

Require current input identities and finite arrays; reconstructed n=92, electron sector `(2,1)`, compatible saved dimensions; `||X†SX−I||inf <=1e−8`; daughter norm error after documented roundoff normalization <=1e−10; `|<g,Hg>−E0|<=1e−8 Eh`; `||Hg−E0g||<=1e−7 Eh`; reproduced `<i,Hi>` differs from receipt by <=1e−8 Eh; reproduced `||Hi||²` differs by <=`1e−8 max(1,|receipt second moment|)` Eh². Evaluate Hermiticity on saved i/g/u pairs as `|<a,Hb>−<Ha,b>| <=1e−9 max(1,|<a,Hb>|,|<Ha,b>|)` Eh. These checks reuse required actions and need no new random full-size run. Record measured defects. Failure preserves diagnostic evidence and stops before expensive basis extension.

Use Q on both sides of H−E0 and retain the saved E0 shift. Independent direct K moments are the measured values from u and Ku. Recorded scalar estimates use the historical residual; reconstructed direct moments supersede estimates for this executed operator, while both remain in the output.

## Numerical algorithm and acceptance: PASS → retain milestone

Use the derivation's projected, two-pass full reorthogonalized Lanczos. Keep basis V and actions KV; compute actual small projected matrix C=V†KV, and diagonalize its Hermitian part J. Report C's anti-Hermitian and off-tridiagonal defects. This is a finite-precision realization of the same Krylov compression, not an altered Hamiltonian. A minimal equivalent tridiagonal implementation is allowed only if it records reorthogonalization corrections and verifies their effect on the same moments; do not add two solvers.

At every milestone require finite vectors/matrix/eigenvalues/weights, Gram defect `||V†V−I||inf<=1e−9`, ground leakage `max|g†vj|<=1e−10`, anti-Hermitian defect `||C−C†||inf <=1e−10 max(1,||C||inf)`, eigensystem defect `||JY−Ydiag(theta)||inf <=1e−10 max(1,||J||inf)`, mass error <=1e−10, and moment error `|Σ w theta^k−m_k_direct| <=1e−8 max(1,|m_k_direct|)` for k=0,1,2. Weights are W times squared coefficients; never clip negative weights from a different formula to obtain a pass.

Happy breakdown threshold: remainder norm <=`1e−12 max(1,||Kvj||)` Eh. Save actual remainder and certify first-three-moment and recurrence/direct-residual evidence before marking an invariant-subspace termination. A small beta is not automatically full physical closure. Compute the six largest-weight Ritz residual norms from cached KV and report them; these are diagnostics and do not all need to meet the ground-state solver residual tolerance. A node below −1e−7 Eh is a flagged issue for ground-relative excitation interpretation; retain the raw Hermitian compressed spectrum and ask Astra to interpret the concrete finding. Do not clip pole positions.

## Declared spectral outputs and refinement

At each milestone output nodes/weights, raw moments m0=W,m1,m2, conditional mean m1/W and second moment m2/W, conditional_variance_Eh2=m2/W−(m1/W)^2, weighted_central_second_moment_Eh2=m2−m1²/W, and Lorentzian spectra at η=0.05,0.1,0.2 Eh on 0≤ω≤20 Eh with step 0.01 Eh (2001 samples). Also output analytic CDF and mass below 0/inside 0–20/above 20 from the same nodes and broadenings. These diagnostic choices are explicitly recorded; they are not a physical energy-resolution claim.

For each adjacent milestone pair compute sampled trapezoidal `integral_0^20 |Snew−Sold| dω / W`, `max_grid |Fnew−Fold|/W`, and absolute window-mass change/W. At 32→64 all three must be <=1e−3 for every declared η to report refinement-met and stop at 64. Otherwise attempt 128 within the same budget; assess 64→128 with the same conditions. Passing the first-three-moment tests alone does not imply spectral refinement. Failure of refinement yields an actual finite diagnostic with `refinement_met=false`, not a solver-code failure or physical no-go. Retain tails without window renormalization.

## Resources, outputs and stopping rule

One worker, 12 OpenMP threads; `OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`; memory/address-space 24 GiB, total wall 7200 s including reconstruction, at most 160 Hamiltonian actions, maximum basis length 128. Before launch inspect actual available resources and avoid disturbing independent owner work. Require at least 20 GiB host headroom while running, as in the inherited driver. Stop checkpointing at a resource limit; a separately supervised limit handles a stuck native action. No automatic retry. One 385112-element float64 vector is 3,080,896 bytes, V at 128 is 394,354,688 bytes, V+KV is about 0.735 GiB; transformed-integral/work storage remains covered by 24 GiB. Do not allocate spin-2RDM arrays or run the original FCI solver. Local summarize/tests have a 120 s wall budget and no large Hamiltonian actions.

Required results: `summary.json` from actual saved inputs; actual test command/log/exit; NCP runner source and invocation instructions; for an executed NCP run `receipt.json`, `spectra.npz`, small milestone scalar JSON/CSV, stdout/stderr, runtime/resource measurements and the last valid basis/action checkpoint. Save h/ERI once if useful for reuse and within disk budget; report whether those integrals are included. Checkpoint at 16/32/64/128 with atomic replacement of a latest progress file while preserving milestone small spectra and failed-run logs. The received Unit2/Unit3 inputs remain immutable. Report actual NCP execution `not_run_remote_unavailable` until a real runtime receipt exists; local synthetic validation cannot replace it.

## Focused tests and transition

Run local deterministic dense-Hermitian tests against direct diagonalization in small dimensions for (1) exact normalized ground and known complement measure, (2) approximate g with nonzero <g,Bg> validating conservative scalar moment/variance/Cantelli bounds and the Q on both sides, (3) repeated eigenvalues/happy breakdown, and (4) rotated-basis invariance of measure and moments. Include a malformed saved-array shape/missing-field check only for actual parser contract. Test independent exact spectral observables, not merely copies of implementation formulas. Exercise supervisor timeout/partial-output preservation with a cheap sleeping fixture, not FCI. Use one meaningful failure fixture for failed reconstruction if the reconstruction adapter can be tested without PySCF. Do not rerun historical FCI tests.

PASS local tests + actual summarize → ship the complete runner and its concrete NCP command. Actual NCP reconstruction PASS → execute the single bounded spectral chain. Internal milestone PASS → preserve diagnostic; refinement PASS → scoped numerical admission at declared broadenings after independent review. Resource/refinement partial → preserve measured outcome and give one concrete next dependency. A substantive defect → one Astra-authorized targeted repair episode and selective regression; no recursive audit tree.

Primary-source and symbolic prerequisites are preserved in `intake/PRIMARY_SOURCES.md` and `intake/WOLFRAM_MOMENT_CHECK.json`. The parent verified the official PySCF Hamiltonian action convention and the author-hosted Golub–Meurant Lanczos/Gauss construction. Reuse that intake; no new literature cycle is required for implementation.

Naming clarification: ν has total mass W, so its weighted central second moment is distinguished from the variance of the normalized conditional measure. A ground-inclusive variance is optional; if reported, call it `projected_block_mixture_variance_Eh2=m2−m1²` for Pδ0+ν with P+W=1. Because g is approximate, this block-compressed mixture variance is distinct from the original-H parent variance. No numerical acceptance criterion is changed.
