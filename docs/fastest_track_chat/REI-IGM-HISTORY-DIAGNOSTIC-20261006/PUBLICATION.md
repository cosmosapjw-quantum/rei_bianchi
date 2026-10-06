# Manufactured FLRW H/He diagnostic checkpoint

**Software verification PASS; numerical accuracy FAIL. Not merge-ready or scientifically validated.**

This additive checkpoint publishes 22 reviewed source/config/test/document paths against thermal commit a0001ca14644fc9fd2fbe52f8cfcae3edbedd110. It preserves the manufactured Case-A escape, C=1 primary-only homogeneous model. Original tolerances, source amplitude, physics and prior scientific gates are unchanged.

Fresh isolated publication tests pass: 203 Rust tests, 3 CLI tests, 14 Python tests. Current-schema endpoint histories, restart and conservation checks pass. The finest 12,560-step time probe still exceeds the frozen GammaHI accuracy allowance by 361.69 times; energy4→8 exceeds its allowance by 2.133 times. Birth refinement remains pulse-phase-sensitive, and exploratory birth64 fails its own budgets. Combined refinement was not run after independent-axis failures. The original full numerical acceptance unit remains incomplete.

Canonical birth16/energy2 tight and retight Python references were rerun from the exact frozen script and inputs, independently hash-audited, and reproduced the earlier compared physical fields exactly. Historical birth32/64 and energy4/8 producer provenance remains partial. Archive hashes certify their bytes only. See PROVENANCE_REPLAY.md and the independent review.

Both providers store the identical reviewed full diagnostic ZIP, with remote full-byte SHA256 and ZIP CRC verification. BACKUP_RECEIPT.json records immutable identities. Large raw histories and exploratory proposals are preserved in that archive rather than copied into GitHub. This publication includes bounded comparison, regression, review and refinement evidence.

Full cargo fmt --check still fails on exactly 12 unchanged legacy paths; the previously introduced lib.rs ordering issue is corrected. See verification/format-base-comparison.json. Actual remote CI must be checked on the published commit; local test success does not imply remote CI success.

Published on separate branch forward/rem-hhe-igm-20261006, with a draft PR targeting forward/rust-reion-kernels-20260922 to isolate the current-work diff. Existing PR83 head is not changed by this publication. No merge, deployment, scientific gate promotion, interval certificate, observed EoR claim, or validated replacement numerical method is included. Rollback, if authorized, is a revert of this additive commit; immutable backups remain.
