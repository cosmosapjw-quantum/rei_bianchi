# Bounded IGM thermal point-provider publication

This checkpoint adds source-parity-tested Grackle-bound low-temperature H/He point chemistry and cooling/CMB RHS to the previously published FLRW foundation. Parent: 47632ba113bd19b1d101001f843385dd620049d6. Exact 12-path source delta matches THERMAL_DELTA_MANIFEST.json. Prior research source and reports are retained.

Fresh isolated publisher verification passed all 166 tests (151 baseline + 15 thermal); scoped rustfmt on the four new Rust files passed. Full rustfmt flags 13 paths: 12 unchanged legacy files plus the new lib.rs export ordering (igm_rates should precede igm_state). See format-base-comparison.json. The reviewed archive/source bytes are preserved exactly, so this is not merge-ready. Upstream license/header/C whitespace is preserved byte-exactly. Local tests are not a remote CI pass. Exact-commit CI is checked after publication and recorded in the detached final receipt.

The cumulative archive is 450188 bytes, SHA256 53ce530df98ba1a8e5af83c85abcba5854f9ffc5827b1ef925b39eae9d4835a2. Both create-only Drive/Dropbox copies were downloaded and SHA256/ZIP-CRC verified; provider size readback and Dropbox content hash also match. BACKUP_RECEIPT.json records identities. No sharing/permission change.

Independent review is preserved in INDEPENDENT_REVIEW.md. All chemistry/cooling values are finite-point implementation checks, not validation over the full operational temperature range. Actual recovered EOS T must pass strict provider admission. No full cosmological history, coupled photon/source evolution, interval certificate, observational fit, or scientific-gate promotion. Existing PR83 remains draft, unmerged. No new branch or force update.

Rollback, if separately authorized: revert this additive commit; keep immutable archives.
