# PR250 one-shot frozen verification dispatch

This metadata commit triggers the new branch-scoped GitHub Actions probe. The preceding workflow creation used [skip ci] and did not trigger Actions. This commit deliberately omits that marker. The workflow verifies six frozen SHA256 identities before running the actual selected RR/Mao worker once with a 3 CPU-second and 30 wall-second guard, then preserves raw output without issuing any scientific C9 acceptance. No IVP is run and no source code was modified.
