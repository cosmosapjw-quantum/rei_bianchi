# Saved-complement T4 execution

The package is `REI_R9_UNIT4_T4_SPECTRAL_20261016/` with `code/`, `tests/`, `spec/`, `results/`, `inputs/receipt.json`, `inputs/data.npz`, `inputs/aug_dz_receipt.json`, `baseline/microphysics_driver_v6.py`, and `baseline/requirements.lock`. It contains a complete executable runner. The existing NCP environment supplies PySCF 2.14.0; do not install or upgrade it for this task. Recorded historical NumPy/SciPy versions are 2.5.4/1.18.1. Summarize and dense fixtures need NumPy only.

The actual local summary and dense/supervisor tests are in `results/`. NCP reconstruction/spectral execution is **not_run_remote_unavailable**. Local fixtures do not substitute for an NCP receipt.

From the unpacked package on NCP, run a fresh summary if needed:

```bash
cd /root/REI_R9_UNIT4_T4_SPECTRAL_20261016
/root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python code/t4_spectral.py summarize --receipt inputs/receipt.json --data inputs/data.npz --aug-dz-receipt inputs/aug_dz_receipt.json --contract spec/NEXT_T4_CONTRACT.json --out /root/REI_R9_T4_SUMMARY_YYYYMMDDTHHMMSSZ
```

For the single new spectral chain, first inspect current host resources and the existing owner workload. Leave all PR150 owner processes/files untouched. The runner records load, CPU count, MemAvailable and runtime versions; it requires 20 GiB host headroom and watches it during execution. Replace the timestamp below with current UTC and use a never-existing output directory:

```bash
cd /root/REI_R9_UNIT4_T4_SPECTRAL_20261016
OMP_NUM_THREADS=12 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 /root/REI_MICROPHYSICS_R9_20261015/.venv/bin/python code/t4_spectral.py run --receipt inputs/receipt.json --data inputs/data.npz --v6-source baseline/microphysics_driver_v6.py --contract spec/NEXT_T4_CONTRACT.json --out /root/REI_R9_T4_SPECTRUM_YYYYMMDDTHHMMSSZ --threads 12 --memory-gib 24 --wall-s 7200
```

The public `run` command starts exactly one supervised local worker. It enforces cumulative 7200 seconds, 24 GiB address-space/RSS, at most 160 Hamiltonian actions and basis length 128. The supervisor stops its own child process group at a wall/resource limit, preserving logs and the latest valid checkpoint. It does not retry or replay ground states. A process that remains in a native action is still bounded by the external supervisor.

The worker rebuilds spherical, nonsymmetric Be+ at the origin using the **saved expanded shells and X**. It checks metric, saved-state energy/residual, parent moments and Hermiticity before Krylov extension. It imports the exact frozen V6 `raw_action`, including occupation-list triangular links. It performs no SCF, FCI eigensolve, new orbital metric diagonalization, or spin-2RDM calculation. h/ERI are constructed once in memory and are not included in checkpoints.

Nested milestones are 16, 32, 64, then 128 only if needed within the same budget. Every milestone records direct moment tests, Gram/leakage/Hermiticity/eigensystem gates, raw pole positions and six largest-weight Ritz residuals. A negative node below −1e−7 Eh is retained and requests Astra interpretation. Lorentzian outputs use η=0.05/0.1/0.2 Eh and ω=0…20 Eh, step 0.01 Eh, with analytic CDF tails; there is no window renormalization. Spectral refinement requires all three declared changes ≤1e−3 at every η. Moment agreement alone is not spectral refinement.

Inspect `receipt.json`, `reconstruction.json`, `chain.json`, `milestone_*.json/.npz`, `milestones.csv`, `spectra.npz`, `progress.json`, `checkpoint.npz`, `stdout.log`, and `stderr.log`. The terminal receipt distinguishes `success`, `partial`, `deferred`, and `failure`; ordinary shell exit 0 is not scientific admission. `partial` preserves an actual finite diagnostic or the last checkpoint without claiming refinement. Happy breakdown certifies only a finite invariant Krylov subspace with measured recurrence/direct-action evidence.

The checkpoint contains exact working basis/actions, ground/u, next vector, source/input identities, action count and cumulative remaining budget. **Resume is not implemented or advertised** in this version. Keep the checkpoint for a separately contracted continuation; do not restart the same work under a fresh budget automatically. If reconstruction fails, preserve all diagnostics and stop before basis extension.

Local verification from the package root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 timeout 120s python3 -m unittest discover -s tests -v
```

The unit describes the finite projected complement measure only. Its excitation cuts do not identify outgoing ionization channels or electron capture. Physical continuum, basis closure and the other campaign dependencies remain open. No NCP command was executed while building this package.
