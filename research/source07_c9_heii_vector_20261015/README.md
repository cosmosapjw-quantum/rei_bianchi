# rei_bianchi SOURCE07: C9 three-absorber positive age compression, 2026-10-15

**Status: numerically checked subproblem; production admission NOT_ISSUED.**
This isolated additive stage follows SOURCE07 C7/C8 and is not a new physical reionization solution or a modification of the frozen AX08 solver. The original untracked C1 numerical baseline is preserved here *byte for byte* as `research/source07_c1_baseline_20261014/q_emission_baseline.py` so this branch is reproducible from a clean Git checkout.

## Mathematical calculation

Use the physical `(-,+,+,+)` axial metric
```
ds² = -c² dt² + a² exp(-2b)(dx²+dy²) + a² exp(4b) dz²
s = db/dt,      mu = local cosine along the z axis.
```
Fixed Killing momenta imply
```
d ln E / dt = -H - s(3mu²-1),    dmu/dt = -3s mu(1-mu²).
```
The exact identities were independently checked using the Wolfram Language evaluator (result `{0,0}`, not an xAct tensor test). At a chosen emission age the source energy is mapped to the proper received photon energy `E = R(a_emit,mu,q) E_emit`. Emit energies 13.6–100 eV. Direction quadrature: 12 GL nodes; energy: threshold-aware 16 GL nodes separately on each interval split at `chi_HI/R`, `chi_HeI/R`, `chi_HeII/R`. These are a specified discretization, **not** certified continuum quadrature.

For each receiver gas vector `(n_HI,n_HeI,n_HeII) >= 0` in cm^-3, apply the frozen-gas proper-rate model
```
lambda_j(E) = c n_j sigma_j(E) [s^-1]
tau(E) = dt sum_j lambda_j(E)
A_j(E) = N_emit(E) [-expm1(-tau)] lambda_j / sum_k lambda_k
N_esc(E) = N_emit(E) exp(-tau)
Q_heat(E) = sum_j A_j(E) (E - chi_j).
```
`c=29979245800 cm/s`, `dt=1e10 s`, Verner HI, HeI and HeII cross-sections in cm²; E and Q in eV. All rates and number densities are proper-frame. At exactly zero total opacity, no species absorbs. Two by-construction event ledgers are evaluated numerically, including escaped energy:
```
N_emit = N_esc + sum_j A_j,
U_emit = U_esc + sum_j (chi_j A_j) + Q_heat.
```
The compressed age basis is a finite convex combination of 36 source ages. The normalized discrete source weights are `w_i proportional to rate(a_i) Delta(log a_i)/H(a_i,q)`; this source-inspired discretization is **not** a verified source-epoch continuous emissivity integration or physical source aging in a full solver. The LP preserves photon N/U and H I, He I, He II absorption and heat for the training gas states. Carathéodory's theorem gives finite convex representability at fixed training functionals, but says nothing about unseen gas states, spectral source changes or time-dependent opacity. Holdouts deliberately probe the latter limitation.

## Runs and evidence

From the *repository root*, with Python 3 + NumPy + SciPy:
```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s research/source07_c9_heii_vector_20261015 -p 'test_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/source07_c9_heii_vector_20261015/experiment.py --workers 1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/source07_c9_heii_vector_20261015/experiment.py --workers 3 --output research/source07_c9_heii_vector_20261015/results_parallel.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/source07_c9_heii_vector_20261015/benchmark.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 research/source07_c9_heii_vector_20261015/perf_runs.py
```

Physical settings: `q=-0.01,0,+0.01`; 36 ages from `a=1/21` to `a=1/5`; five training proper-gas tuples; 48 unseen H/He ionization-simplex states with nonzero HeII. Model fixed to C1's source-backed geometry; no evolving gas, electron abundance or gas temperature.

Observed at all three q: 1 training state -> six retained ages, worst holdout relative error 5.35e-4; 3 -> ten ages, max 2.73e-9; 5 -> eleven ages, max 1.71e-11. Photon-number and energy ledger residuals below 2.4e-15 on evaluated states; positive absorption and escaped photon counts. Five independent validation tests passed; the independent original C8 scalar reference agrees with C9 vectorization over the full 36-age x 5-gas q=0 sample to 1.94e-15 relative.

**Three-repeat median matched-physics performance** (36 ages × 5 gas states, q=0): C8 scalar 1.06975994 s, C9 NumPy vectorized 0.01624145 s, 65.866-fold local subproblem speedup. Cached spectral packet arrays total 1,486,848 bytes in this sample; *not* total solver RAM. No speed gain inferred for production AX08.

**Parallelism**: three independent q jobs through Python ProcessPoolExecutor, BLAS one thread per worker, strictly identical sample moments and LP weights compared with serial in five repeats. Median whole Python-process wall time 0.6023 s serial and 0.5455 s three workers, factor 1.104; small start-up dominated benefit, **no claim of a material production parallel speedup**. Within the timed Python algorithm, workers speed it up more, but the full process is the appropriate cost for this tiny job.

**Hard-source adversarial stress**: replace BB50K with a separately normalized `phi(E) proportional E^-1.5` between 13.6 and 100 eV at the same frozen gas/source ages, q=0. This is not a physical source replacement. Under the most ionized training gas state, the HeII fraction of total absorption changes from 0.00102949 to 0.387599. Reusing the 11-node BB50K-fit weights yields a worst hard-source holdout error of 0.00460223 (HeII absorption). Refitting with the hard-source kernels yields 12 retained nodes and a max hard-source holdout error 1.554e-9. Hence an opacity/species/spectrum dependent compressed basis is necessary. This is a *specific counterexample to spectrum-blind transfer*, not an impossibility theorem for adaptive compression.

Observed failure resolution: an initial unit test incorrectly demanded positive HeII absorption for every aged cohort. Very early packets legitimately redshift below 54.42 eV, and the corrected test checks nonnegative absorption plus actual above-threshold absorption in later packets. No tolerance was widened to hide an implementation error.

## Provenance and boundaries

- Base HEAD: `0fcb2dddf5de6b583c2e00f150abff0b2afb6315` (SOURCE07 C8 multistate).
- Baseline C1 file SHA256 `43f7805703f08516b2b4b8e686b097b1c38e2140ac06b556e7de07159cf42b06`. Imported exactly from authorized local original; an upstream untracked file was **not** assumed to exist after Git checkout.
- Scalar C8 SHA256 `f8a7d7ecbf7b839ef138c024384bed0fa16ec6889a332ef2ade2dc7c9d47b72b`.
- Original scenario authority `research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json`, SHA256 `07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696`.
- Physics: Gnedin & Madau, *Cosmic Reionization*, arXiv:2208.02260, https://arxiv.org/abs/2208.02260 ; Pawlik & Schaye, *Multifrequency, thermally coupled radiative transfer with TRAPHIC*, arXiv:1008.1071, https://arxiv.org/abs/1008.1071 . These sources motivate photon accounting and multi-species spectral/thermal modeling; they **do not** validate this compression method.

Acceptance achieved: executable source, independent scalar parity, threshold/empty-opacity tests, positive He simplex, three-absorber energy/photon event ledgers, multi-q process parity, same-problem performance measurement, hard-spectrum counterexample. Scientific admissions still needed: physically sourced continuous age-dependent emissivity, changing gas/temperature/HeII with self-consistent electron abundance, independent dynamic short-interval reference, convergence/error enclosure and matched solver-time/memory comparisons, then AX08 transport/chemistry integration on a separately authorized binding. AX11/AX12 and final observable history claims remain independent.

`native_subagent = NOT_RUN`: current host exposed no native delegation; Python process parallelism is not a subagent.
