# Codex handoff — rei_bianchi first canonical interval

```text
current accepted result: one four-site FLRW microstep at partition 2048
historical audit candidate: STOP_INVALID / HOLD
exact next action: REI-BOOT-00
terminal ceiling: PASS_REI_FIRST_CANONICAL_INTERVAL_ONLY
```

## Exact audit evidence

```text
audit branch: audit/ode-four-loop-external-20260823
audit commit: ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e
audit tree:   c8167922076f52628b1f7243c9ebd8b40ebe7508
```

The package branch was created from live `main`. Resolve and pin its exact pre-package parent before mutation. The audit branch and corrected ODE candidate are read-only evidence, not an implementation base or wholesale merge source.

## Preserve local state

Use a new isolated worktree. Do not clean, reset, stash, amend, rebase, force-push, switch an occupied worktree, or discard unknown bytes.

## Intake

Read this package, then `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`, `handoff/CURRENT_HANDOFF_PROMPT.md`, `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`, and `external/REC_BIANCHI_MONITORING_POLICY.md`.

Run current-main bootstrap, repository verification, current-stage tests, exact/independent validators and current-stage checksums. Freeze the rec lock byte-for-byte. Do not update it during this work unit.

Read the audit candidate and independent review. For each finding, write a current-main RED that reaches the numerical path. Do not count missing imports, packaging/transport differences, stale hashes or the existence of a candidate as numerical evidence. Port only fixes whose failure reproduces on current main; reject the rest explicitly.

## Execute the first interval

Proceed in order:

```text
REI-BOOT-00
REI-AUDIT-RED-01
REI-HISTORY-02
REI-REC-LOCK-03
REI-DELIVER-04
```

Start from partition 2048 and compose accepted microsteps over the complete first canonical BDF interval. For every attempt compute one full image and two half images. Accept only when implicit, positivity, public-width, structural-ledger and local-error gates pass. Bisect only the failed attempt to the locked minimum.

Localize every Hummer-Seaton/table knot before commit, preserve parent bytes, restart the fixed-topology model, run all three shape lanes without post-hoc selection, and close the seven ledgers over the whole interval. Retain accepted/rejected transactions, generator rank, named owner low-rank modes, remainder growth and event distance.

Keep the existing rec lock exact. If `PASS_REC_SPLIT_DOMAIN_REPLACEMENT_AND_INTERFACE_V1` is unavailable, finish with `LOCK_HELD_PENDING_REC`; this does not invalidate the rec-independent first-interval result. Recombination splice, hydrogen-frame adapter, CAMB transfer and Bianchi-family work remain forbidden.

Use BASS only as verification discipline: typed identity, exact event/restart/history semantics, independent oracle/mutation tests, nondegenerate fixtures and failure-preserving ledgers. Import no BASS physics or incomplete RF-04 code.

Do not change the frozen width limit `2e-3` or local-error limit `2e-4` after observing results. No clipping, extrapolation, favorable lane selection, dense full Jacobian, timing, GPU, Wolfram or unrelated full-suite reassurance.

Finish with one bounded review, at most one reproduced P0/P1 repair, ordinary push and one draft PR. Stop without merge or ready transition.