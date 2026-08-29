# Codex handoff — rei_bianchi first canonical interval

```text
repository: cosmosapjw-quantum/rei_bianchi
base main: ae3402713c4b6530ab2b27f008f5f5d5c6a999ed
base tree: e7bce0e77797f7c755059a1c88e284591728b77c
audit source: ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e
scaffold tree: 213c29c4b9d6bf4a626111c105bc2d7979507c49
exact next action: FIRST_CANONICAL_INTERVAL_BOOTSTRAP_RUN
claim: NO_PASS_FIRST_CANONICAL_INTERVAL
```

## Preserve and validate

Use an isolated worktree from the exact package branch. Do not clean/reset/stash
an occupied worktree, rewrite shared history, or merge the old corrected-ODE
candidate. Materialize this package and run manifest, offline and live
validators.

Then run:

```bash
./scripts/bootstrap_sandbox.sh
python scripts/verify_repo.py
cd stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_R1_R1_R1_R1_UNCERTAINTY_QUALIFIED_FIRST_CANONICAL_INTERVAL_ADAPTIVE_HISTORY
sha256sum -c SHA256SUMS
pytest -q tests
python analysis/preflight.py
```

Record actual fresh results. The scaffold's old 58-test review is carried
evidence only.

## Execute the interval

Start at partition 2048. For every attempted step compute one full image and two
half images; independently require implicit, positivity, uncertainty-width,
structural-ledger and local-error gates. Bisect only the failed attempted step
and fail closed at the locked minimum.

Run all three shape lanes without post-hoc selection. Track sparse generator
rank, named owner low-rank modes, remainder growth, table-event distance, and
accepted/rejected transaction records.

Localize every Hummer–Seaton knot before commit, preserve parent bytes and
restart the fixed-topology model. History receives accepted states only.
Exercise the audit regressions in `PACKAGE.json#audit_regressions`; do not
transplant the old candidate implementation.

## rec_bianchi dependency

Read `external/rec_bianchi.bootstrap_dependency_candidate.json`. rec PR #26 is
monitoring-only. The first FLRW interval may proceed because it imports no rec
rates/history. Do not activate the hydrogen-frame adapter, recombination splice,
primordial numerical input or Bianchi feedback until rec earns
`PASS_PR05C2C1B2B1E1C_SPLIT_DOMAIN_REPLACEMENT` and a deliberate adapter/input
lock review passes.

## Review and delivery

One PHYS-MATH and one PHYS-MATH-CODE review, at most one reproduced P0/P1
repair. Ordinary push and one draft PR. No merge/ready, CAMB, production node
chemistry or Bianchi-family sweep.

Final headings:

```text
STATUS
ACTUAL PROGRESS
VERIFIED
DEFERRED
BLOCKERS
NEXT
```
