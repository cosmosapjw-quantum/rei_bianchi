# Canonical reference provenance supplement

The final delivered Python implementation was replayed at the existing birth16 / energy2 configuration only, with Radau rtol=1e-11 / atol=1e-14 and rtol=2e-12 / atol=2e-15. No new resolution, source, physics, or acceptance criterion was introduced. Runtimes were 35.9 and 53.7 seconds.

The independent reviewer verified implementation SHA-256: 0d827afc60f21e23d86c0b0d6b2850a80debf8182fd4f7622978e8ac93039ed6, exact config hash and source-input hash in both new manifests against the frozen delivered source. Both runs reach the requested endpoint and pass their own budgets. All compared physical fields exactly equal the earlier accepted CSVs; their numerical comparison conclusions therefore remain unchanged. Tightening changes the worst physical field by 7.567794e-8 of its ordinary allowance.

Canonical accepted references are evidence/canonical-reference-tight and evidence/canonical-reference-retight. The independent check is evidence/independent_review/canonical-reference-provenance-audit.json. Existing plots and comparison reports remain numerically applicable because compared physical fields are exactly unchanged.

Historical birth32/64 and energy4/8 outputs remain useful diagnostics with explicitly partial producing-script provenance; their archived hashes certify file contents only. Birth64 also fails its own budget and is not an accepted reference. No retroactive producer hashes were fabricated.

Overall numerical accuracy remains FAIL. This supplement closes canonical reference reproducibility only; it does not promote the failed time/source/energy refinement gates.
