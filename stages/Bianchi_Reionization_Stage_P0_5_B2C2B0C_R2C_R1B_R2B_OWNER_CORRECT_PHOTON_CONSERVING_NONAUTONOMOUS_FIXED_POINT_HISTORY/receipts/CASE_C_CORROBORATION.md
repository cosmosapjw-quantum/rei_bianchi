# Case C corroboration — independent upstream evidence

The Case C determination in `RESULTS_AND_VERDICT.md` originally rested only on
probes run in this session. `R1B_R2B_INTERRUPTION_RECOVERY.zip`, delivered
afterwards, is an **independent upstream artifact reaching the same conclusion**.
It is preserved verbatim in `upstream_interruption_recovery/`.

## What the upstream sweep found

`RECOVERY_INVENTORY.json`:

```json
{
  "classification": "RUNTIME_INTERRUPTION_RECOVERY",
  "targets": ["d60c7f7", "47df6c5da4ddf7a309d110340adad8dbe68d148b"],
  "candidate_count": 0,
  "candidates": [],
  "selected_repo": null
}
```

`RECOVERY_TEST_RECEIPT.json` records `selected_repo: null` and an empty
`commands` object: no workspace was found, so no verification command was run.

Generated `2026-08-07T08:00:48Z`. Both files verify against the shipped
`SHA256SUMS`. Archive SHA-256:

```text
98ca13d62b98fe62e234c284b3e01c5c73ca8903c18485037d8362916ec4f1ca
```

## Why this matters

The upstream sweep targeted `d60c7f7` — the same commit this stage refused to
inherit — and returned **zero candidates**. Two independent searches, one in
this session across `rei_bianchi`, `rec_bianchi`, `htt_base`, the reflog, all
remote refs and the filesystem, and one upstream, agree that no such workspace
exists.

Case C was therefore the correct branch, and the decision not to inherit
`d60c7f7` as a transcript-only commit is externally supported rather than
resting on this session's word alone.

It also establishes that **no competing upstream R1B-R2B implementation
exists**. The upstream run was interrupted before producing one, `main` carries
no R1B-R2B stage directory, and no other remote branch holds one. There is no
content conflict for this stage to resolve.

## Deliberately not done

`INPUT_LOCK.json` was **not** amended to cite this artifact. The lock was frozen
before calculation, and editing it afterwards to add supporting evidence would
break exactly the discipline that makes a precalculation lock meaningful. The
corroboration belongs here, in receipts, with the lock left as sealed.

## Also verified at the same time

`rei_bianchi_R1B_R2A_incremental_452e8272_to_47df6c5d.bundle` was redelivered
alongside the recovery archive. It is byte-identical to the copy merged
previously —

```text
f212c1856affe37220c36140391bfc8607833a5d0f10beae3b91152a4d0ce0ad
```

— its head `47df6c5d` is already an ancestor of `main` at `e11dcb56`, and
`git bundle verify` passes. It is a reference copy and required no action.
