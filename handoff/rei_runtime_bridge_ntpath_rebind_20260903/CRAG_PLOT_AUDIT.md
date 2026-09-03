# Plot-based CRAG audit — handoff state

Figure: `HANDOFF_STATE.svg`

## Correctness

The figure shows completion of two bounded deliverables only:

```text
ntpath declared-import closure
fresh standalone handoff rebind
```

It shows zero completion for native invocation, result audit, first canonical
interval and provider export.  The bars are generated from
`HANDOFF_STATE.csv` and checked byte-for-byte by `render_handoff_state.py`.

## Retrieval

The plot agrees with the current GitHub/Atlassian evidence: PR #37 closes the
one-root import declaration while explicitly withholding a native rerun and
downstream scientific claims.

## Augmented adversarial checks

1. Relabeling `PINNED_HOST_NATIVE_INVOCATION` as complete would contradict the
   absence of a new attempt claim, runtime receipt and native artifact.
2. Relabeling `FIRST_CANONICAL_INTERVAL` as open would bypass the required
   runtime-result audit and retained REC/BASS/provider gates.
3. Interpreting the two 100% bars as 33% solver completion is rejected: these
   percentages describe each named deliverable, not weighted science maturity.
4. Adding an unindexed plot or status file fails package-closure verification.

## Generation

The figure predicts one narrow next observation: the pinned-host attempt will
produce either a new first blocker or a bounded runtime receipt.  It does not
predict which outcome occurs and gives no basis for a provider or science
claim.

## Verdict

```text
SURVIVING_CLAIM
  the handoff node can be complete while the runtime and scientific chain remain unrun

REJECTED_CLAIM
  handoff completion implies solver, first-interval or provider readiness
```
