# FLRW/HHe IGM foundation publication

First bounded unit only: explicit flat radiation+matter+Lambda FLRW background, baryon H/He density normalization, boundary-valid H/He EOS, units/adapters, exact geometry transport and manufactured adiabatic tracer.

Parent: `2b6005fd9c88e5cb38213c5bb66baee7caf54583`. Four new source/test/example files and three additive lib.rs exports; existing research lanes preserved.

Fresh isolated publication verification: `cargo test --locked --offline` passed all 151 tests (142 existing + 9 new); scoped rustfmt and git diff --check passed; probe output is byte-identical to the independently formula-checked delivery CSV. Two initial build attempts lacked sparse-checkout fixture files; adding their existing base-version paths resolved this without product changes. Independent review and final source hashes are in INDEPENDENT_REVIEW.md. Historical clippy passes with legacy warnings, not warning-free or strict-clippy qualification.

The original archive README records pre-publication state. This file records subsequent authorized publication. Both identical 195681-byte archive backups were fully downloaded, SHA256-matched, and ZIP-CRC verified; see BACKUP_RECEIPT.json. Archive SHA256: `26bb9a8e1f55e3a86e91dc1b14e1814f47fa224cc7deec72be055a0325a22a57`.

No low-temperature chemistry/cooling admission, coupled non-equilibrium history, observational applicability, interval certificate or production campaign is claimed. No science gate promotion or merge. PR83 remains draft. Exact-commit CI is checked after publication; local proof is not a CI pass.

Rollback: revert this additive publication commit on the same branch if authorized; immutable backups remain. Next unit: source-parity-tested low-temperature H/He rates and cooling, separately reviewed.

Final isolation recheck: all 151 tests passed again with publisher-only CARGO_TARGET_DIR, independent of ongoing next-unit builds. See isolated-target-tests.log.
