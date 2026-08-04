# Full mirror recovery — 2026-08-05

The originally reported `rei_bianchi_full_mirror.git.tar` was absent from the active artifact filesystem when the user reported an upload-status failure. The mirror was rebuilt from the verified `rei_bianchi_main.bundle` and the artifact registry.

One archive-only science ZIP was also absent. It was reconstructed from its compact bundle plus the nine canonical input bundles listed in `RECOVERY_INPUT_LOCK.json`. The original full manifest contains 689 tracked file entries; all 689 reconstructed files match their original path, size, and SHA-256. The reconstructed ZIP container necessarily has a new hash because ZIP metadata/container bytes are regenerated.

The repaired complete mirror is distributed as small numbered parts with a manifest and reassembly script. This avoids another single-file upload failure.
