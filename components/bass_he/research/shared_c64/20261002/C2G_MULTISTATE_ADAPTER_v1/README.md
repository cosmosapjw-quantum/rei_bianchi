# BASS_HE C2g multistate reference package

Start with `C2G_REPORT_KO.md` and `C2G_NEXT_HANDOFF_KO.md`. The exact execution contract is `contract/PHYSICAL_PREREGISTRATION.json` plus `PHYSICAL_TASKS.json`, approved by `review/PRELAUNCH_INDEPENDENT_REVIEW.json`.

The completed bounded reference uses R=4 and4.25 a_A, three basis levels, m=0 six roots and |m|=1 three roots. All root vectors, finite C†HC/C†MC, source hashes, matrix residuals, explicit ±m reconstruction and common physical embedding are retained. 52 new unit tests,8 independent prelaunch checks,314 registered scalar gates pass in their separate evidence scopes. No continuum/full-C2/production certificate is claimed.

Successful records: `results/numpy_serial_1x1.json` and `results/native_mpi_2x1_retry1.json`. The original `native_mpi_2x1.json` is a preserved pre-physics missing-mpi4py failure. See the additive environment retry amendment and `results/campaign_ledger/AMENDED_COMPLETED.json`. Do not overwrite or re-label that failure. The full analysis is `results/analysis/ANALYSIS.json`; a separate radial mass-form cross-check is `review/INDEPENDENT_RESULT_CHECKS.json`.

Code details: `docs/MULTISTATE_PROVIDER_KO.md`, `math/COMMON_EMBEDDING_KO.md`, `docs/REFERENCE_RUNTIME_KO.md`, `docs/ANALYSIS_KO.md`, `docs/NCP_OPTIMIZATION_POLICY_KO.md`. Python runtime pins are in `requirements.txt`. Native kernels use strict binary64 arithmetic profiles; explicit backends and OpenMPI have no implicit fallback.

The source publication excludes NPZ and native binaries. The private ZIP includes exact archived coefficients, native build products, logs and an mpi4py CPython3.12 x86_64 recovery wheel. Recorded absolute paths identify the creation environment; they are not a portability promise. Use the handoff for a new namespace and new registered work, rather than replaying completed C2g solves. No NCP64 measurement has been made.
