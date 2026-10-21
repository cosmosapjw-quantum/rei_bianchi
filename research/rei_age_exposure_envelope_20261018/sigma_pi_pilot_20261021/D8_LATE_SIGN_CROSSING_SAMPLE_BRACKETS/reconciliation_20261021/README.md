# D8 result/review identity reconciliation

This additive correction preserves the original result, review, file manifest, failure sidecar and all numerical data. It does not silently replace the historical review hash.

## Why the hashes differ

The published D8_RESULT.json SHA256 is 9c7a3c74cff48bb76d00c6af9795783aae2a7bb4a1e455d07cc1dd89b51e71e8. The original review names643cea016e4bf35968f947aea3519bd292c434094a6e7430e8b9c2fb203318ce. Removing exactly eight additive provenance fields, then serializing with the frozen analysis script's sorted, indented JSON convention, reconstructs bytes with exactly that reviewed hash. REVIEWED_RESULT_RECONSTRUCTED.json is explicitly a reconstructed artifact, not a retrieved historical original.

The eight additions are execution_provenance_note and seven case-c fields enumerated in RECONCILIATION.json. They distinguish original FAILED_WORKER_EXIT124 from subsequent data-only recovery PASS, retain missing solver metadata, and clarify nominal zero matter stress versus stored near-zero value. They are scientifically important qualifications, not irrelevant formatting.

## What is and is not identical

All previously present fields, including configurations, raw hashes/byte counts,153sample counts, bracket indices/redshifts/signed values and scientific limitations, are identical. The full JSON documents are not semantically identical because provenance was added. No bracket result, tolerance, equation, source assumption or numerical array identity changed. Hash inequality alone is not evidence of a changed scientific prediction; this structural comparison supplies the missing distinction.

The comparison does not independently validate NPZ arrays: both representations and existing case receipts refer to the same raw SHA256s, but binary payload bytes were not downloaded here. No solver, root interpolation, statistical-significance test, or new numerical campaign ran. The near-zero stress value is retained from published provenance, not newly measured. AGE convergence HOLD, Grackle bound NOT_ESTABLISHED and production NOT_ISSUED remain unchanged.

## Reproduce the limited check

From this directory run: python verify_reconciliation.py

It verifies exact current result and reconstructed historical hashes, original analysis/review binding, exactly eight additive fields and no changed existing fields, case/config/raw receipt identities, bracket structure, and preserved failure124. A separate additive INDEPENDENT_REVIEW.json records review of the exact published result and reconciliation; it does not rewrite the original review or claim new raw/physics verification. Existing D9 work is unaffected.
