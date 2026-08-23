# Exclusions and unavailable artifacts

This file makes the completeness ceiling explicit. It does not silently replace missing evidence with reconstructed material.

## Unavailable historical current-REI artifacts

- The standalone original output of loop R1 (the first current-REI physics-specific investigation) was no longer present when the integrated custody pass began. Its surviving content is represented only through later seed/provenance records.
- The standalone original output of loop R2 (the independent current-REI math/algorithm/coding investigation) was likewise no longer present. Its surviving content is represented only through later seed/provenance records.
- `/tmp/rei-ode-integrated-audit.ZcRbz6/WORK_CONTRACT.json` was an ephemeral bounded-work contract and was mandatorily deleted at the prior closeout. Its last recorded pre-deletion SHA-256 was `2ae45d16a6436bc139f4c9d265e2b5e18d35af5e84c8f64590e0ac95981c8a7d`. It is not reconstructed.

## Deliberate scope exclusions

- The nested full worktree under `/tmp/rei-ode-integrated-audit.ZcRbz6/worktree` is not copied into itself. It is a roughly 1.34 GB repository checkout, not a research-generated artifact. The 71-file candidate already lives at its canonical repository path, while the three generated top-level scratch records are copied into this package.
- Five `/tmp/rec_bianchi_*.md` records are excluded because they bind a different repository/model/root and a 56-row `full_bianchi_hyrec` problem, not this current-REI four-loop investigation:
  - `/tmp/rec_bianchi_physics_research_record.md`
  - `/tmp/rec_bianchi_independent_numerical_research.md`
  - `/tmp/rec_bianchi_physseed_research_record.md`
  - `/tmp/rec_bianchi_algoseed_coding_research_record.md`
  - `/tmp/rec_bianchi_algorithm_independent_review_receipt.md`
- Two pre-existing untracked Git bundles in the original checkout are protected custody objects and were not produced by these research loops. They were not opened, hashed, copied, staged, committed, or pushed:
  - `rei_bianchi_0cf932378225e4b14c36d1c80597b76cda2b7088_self_contained.bundle`
  - `rei_bianchi_agent-precalc-adaptive-history-parallel-runtime_from-ae340271.bundle`
- The current shipping scratch directory `/tmp/rei-ode-external-ship.ByOEXi` is operational packaging state, not an earlier research result, and is not delivered.

## No hidden cleanup

No source artifact was deleted or normalized for this delivery. Duplicate contents are preserved at every source role/path. No test cache or ignored benchmark-result directory was found in the in-scope roots. Hidden `.agents` trees and both harness `.gitignore` files are included.
