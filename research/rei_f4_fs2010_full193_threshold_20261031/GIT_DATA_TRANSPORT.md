# Git transport for original 18,528-row F4 source kernel

The complete uncompressed 6,587,861-byte `results/FS2010_FULL193_KERNEL_18528.csv` remains in the immutable, independently restored private `REI_F4_FS2010_FULL193_THRESHOLD_20261031_FULL.zip`. To avoid a GitHub connector h2 transport limit on a >6 MB blob, this public Draft PR carries a byte-exact XZ-encoded copy (`results/FS2010_FULL193_KERNEL_18528.csv.xz`, 1,629,400 bytes) and the original 192-arrival and 192 thermal coefficients as plain CSV.

From a Git checkout, run `python code/restore_full_kernel_csv.py`, requiring only Python standard library. This writes the exact original raw CSV if missing, or verifies an existing copy. The script checks the compressed SHA-256, the decompressed SHA-256 and 18,528 scientific data rows, with the provenance recorded in `evidence/KERNEL_TRANSPORT.json`. The reconstructed raw content is **bit-for-bit identical** to the original source archive, not a resampled or reserialized CSV.

Running the original full `VERIFY.sh` additionally requires the private source-inclusive ZIP (which includes publisher PDF originals and upstream Git snapshots and is deliberately not copied into public Git). Physics claims and DAG gates are unchanged; `GIT_DATA_TRANSPORT` is a packaging-only, no-science-delta repair. No merge, production release or source-owner switch.
