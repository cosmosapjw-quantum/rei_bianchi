# R9 Unit4: saved-complement spectral diagnostic

Start with REVIEW_AND_NEXT_T4_KO.md and NCP_CODEX_HANDOFF_KO.md. The complete NCP runner is code/t4_spectral.py, with the frozen mathematical/numerical contract in spec/ and independent acceptance in review/. Inputs and the immutable V6 Hamiltonian-action source are included.

Unit3 recovery and its 86 frozen gates passed. The new scalar summary was calculated from actual saved states; nine dense/supervisor implementation tests passed and the independent reviewer accepted bounded NCP execution readiness. The actual 92-orbital PySCF reconstruction and Krylov spectral run have NOT RUN in this session. No physical continuum or electron-capture result is established.

## Local verification

From this directory, with a Python/NumPy environment:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 python -m unittest discover -s tests -v
python code/t4_spectral.py summarize --receipt inputs/receipt.json --data inputs/data.npz --aug-dz-receipt inputs/aug_dz_receipt.json --contract spec/NEXT_T4_CONTRACT.json --out /tmp/REI_R9_T4_fresh_summary
```

Choose an unused output directory. NCP_INSTRUCTIONS.md gives the supervised NCP command using the existing PySCF environment. No dependency upgrade is needed.

## Evidence layout

- inputs/: exact recovered aug-TZ receipt, NPZ, input and launch; prior aug-DZ receipt.
- baseline/: immutable V6 source and original contract/runtime lock.
- results/: actual scalar result and implementation test receipts. NCP status is explicit.
- numerics/: historical mechanical recovery checks and their source/execution record. The historical audit command references the original Unit2/C10 archive and is not the new standalone runner.
- unit3_collection_metadata/: original collection evidence; its SHA256SUMS describes the original Unit3 archive layout. Use the root SHA256SUMS for this package.
- intake/: selected primary-source/CAS evidence and recovered review, with no temporary download URLs.

The external UNIT4_DELIVERY receipt records archive hashes, actual provider object identities and the publication commit. It is created after archiving to avoid a self-referential archive hash. The Git version excludes inputs/data.npz and links the full backup.
