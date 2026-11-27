# Saved-evidence verifier: static correction review

Date: 2026-10-23T15:22:53.966123+00:00
Scope: author review of the saved verifier and one R7 tar layout; no verifier execution, compile/import, scientific test, IVP, render or remote mutation. The live unit was read only and was not modified.

Previous verifier SHA256: 8bf7d75c26a43a9c4dead92ff1ead7f140f9d43ff70322e9c99cd16277cceb60.
Corrected verifier SHA256: f9c39a4290a499d7e7006fc808db0a1f7352711b2acf71d50dc62de4dbdadc46.

Concrete defects were reported to the controller before edits. The controller independently identified the same archive layout defect and authorized the correction.

## Corrections

1. Stage tar entries actually use unit/<relative>; prior candidates missed them. The reader now uses exact canonical member names and never extracts to the filesystem.
2. Historical ACK absolute paths do not survive relocation. Repeatable --archive-dir provides an explicit basename fallback when the old path is unavailable.
3. An available archive with absent/wrong expected historical bytes was previously only a note. It now produces a saved-evidence error; unavailable required historical bytes remain pending and cannot produce final_complete.
4. Available archives now check outer SHA256/size, MANIFEST stage/count/inventory, and every listed payload SHA256/size, with duplicate/ambiguous entries rejected. The original archive SHA remains distinct from payload SHA.
5. Manifest self-reference and a two-manifest hash cycle are rejected. --output cannot replace a verified manifest input, ledger/receipt/output or archive and silently invalidate the just-completed check.
6. Resource reconciliation now checks START prior debits and nonoverlap, START frozen identity, child+wrapper CPU arithmetic and wall-window arithmetic in addition to ledger totals.

## Assembly guidance

Keep immutable scientific source/results separate from evolving DAG, stage ACK, delivery and own-commit metadata. A local manifest may hash the science manifest in one direction. A verifier report written after manifest freeze must be outside that manifest's covered files, or incorporated only before a later manifest freeze. Final archive SHA/provider ID cannot be preclaimed by including its own later ACK. An expected-SHA push/readback receipt establishes publication separately; the offline verifier certifies saved identities and does not establish its containing commit ID.

Current R7 receipt was read only: known cumulative debit CPU0.211275 s and wall0.1680309520015726 s, remaining CPU9.788725 s/wall29.831969047998427 s. No charge was reset or transferred. The runner was not changed, preserving its executed SHA256 505fe06d2adcc7c3d93ad7207a1a2fcf437a6c08582430d140f58f2f1a98503c.

No runtime validation of the corrected verifier is claimed. The controller can run the single intended saved-evidence C8 check; it does not import or execute scientific code.
