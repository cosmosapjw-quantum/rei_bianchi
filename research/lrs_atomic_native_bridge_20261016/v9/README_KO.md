# REI LRS V9: positive photon-birth and opacity clock controls

Parent [PR #168](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/168) HEAD `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b`. Standalone smooth manufactured test. **No edits to PR150 owner, PR168, NCP or running production checkpoints.**

Physics: `X=ln(a/a0)`, source photons N, neutral H I target M, ionized I and emitted B, all stocks per **total H nuclei**. `N'=S(X)-lambda(X)*N*M; M'=-lambda N*M; I'=lambda N*M`. One fixed E=80 eV, H binding=13.6 eV; no actual source spectrum/stellar profile, redshift, Grackle RR/CI/DR, Case B, or EoR history.

**Run** from `research/lrs_atomic_native_bridge_20261016/v9`:
```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH="$PWD/src"
python -m pytest -q tests/test_birth_opacity_clock.py
python run_study.py
```
Alternatively `bash REPLAY_V9.sh`. Python >=3.11, numpy, scipy, pytest. Source and tests have exact byte-matched Github blob identity against the ChatGPT sandbox executed originals.

**Measured**: 61/61 pytest PASS and 180 independent 5-case×6-method×6-resolution Radau comparisons. For smooth dynamically depleting neutral stock, final N256 photon error 4.0868e-7 (source/opacity midpoint exact pair) vs 1.9614e-4 (source-left), 1.3589e-4 (opacity-left), 6.0717e-5 (both-left), 4.3077e-4 (all source photons at start), 5.4372e-4 (BE pair). Last orders ~2.000, .997, 1.005, .989, .998, .998. The source- and opacity-lag defects may cancel at a single resolution while p remains ~1. A manufactured proportional S/k with affine k is exactly captured by midpoint, so near-zero error there cannot certify universal high order.

Source stages: `stages/R5_THEORY_KO.md`, `stages/DAG_R5/C5/C6/C8/FINAL.json`, `stages/C8_RESULT_KO.md`. Local complete restorable ZIP includes full raw `evidence/convergence.csv` (180 cases), JSON, inputs and test receipt. **Cloud status**: GitHub per-stage publication and Google Drive R5/C5/C6/C8 native-Doc **text mirrors** with readback are complete; binary raw ZIP upload via Library/Drive failed `container_session_expired`; Dropbox upload not attempted because connector needs fileParam injection. These are distinct assurance levels.

**Claim**: smooth conditional 0D factor isolation only; original PR150 native source-on first-order causal allocation still **HOLD**. No all-physics 2nd order, Case B, signed Bianchi or full EoR claim. Native subagents NOT_RUN.
