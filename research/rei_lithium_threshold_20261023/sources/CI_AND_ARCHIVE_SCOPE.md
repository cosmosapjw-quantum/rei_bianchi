# Narrow CI and archive observation

Observed 2026-10-23. No CI rerun, build, formatting edit, science replay or new gate was introduced.

Both inspected current heads have two completed failing `verify` check-runs. For the PR-triggered job on PR221 (`120210648621`, workflow run `39891053782`) and PR222 (`119991431872`, workflow run `39826604840`), the failed step is `cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check`. The following Rust workspace test step was skipped. Legacy commit-status arrays are empty; they must not be interpreted as CI success. Check annotations were outside github.fetch's permitted endpoint family, but the supported job-step read supplied the failure location. This is a formatting-stage observation, not a complete diagnosis of all potential workspace test failures.

The exact local archive `REI_ANGTHERM01_FINAL_20261023_46519489c540.zip` is **15,397,188 bytes**, SHA256 `46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036`. Read-only ZIP inspection finds **148 members**, including **24 NPZ files and 7 PNG figures**. Those 31 binary members total **19,005,518 uncompressed bytes**. They include both frozen background histories, all ten completed result NPZ files, preserved partial/failure results and all seven figures. ZIP CRC testing reported no failed member. The full filename/size inventory is in `LOCAL_ARCHIVE_INVENTORY.json`.

Therefore the controller-reported memory statement calling this exact 15,397,188-byte archive “metadata-only” is contradicted by its actual local contents. The Git publication being predominantly reviewable text is a different fact; the companion archive contains the binary science payload. This followup does not repeat a remote provider download or claim that today's local inspection establishes remote whole-byte identity. Historical backup acknowledgements remain in the prior delivery receipts.

The observed repository Rust formatting failure does not invalidate the saved scoped Python ANGTHERM01 calculations and does not require diversion from the selected frozen-bath Li numerical leaf. A full gas/Einstein IVP or unrelated CI repair has not been selected or performed.

