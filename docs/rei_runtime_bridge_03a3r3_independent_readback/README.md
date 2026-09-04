# REI-RUNTIME-BRIDGE-03A3-R3 — Independent ruleset readback RED

This node is an intentional test-first RED stacked on Draft PR #50.

```text
parent PR      #50
parent commit  a24f4710a1a105443da4c1bc5c7191ca1a4e33a5
parent tree    c27eab7b26906129dccd965306ea00ff63875263
```

The future auditor must not trust the administrator's mutation receipt as proof of current server state. It must separately validate:

1. `ADMIN_MUTATION_RECEIPT.json`;
2. the original controller-compatible `SOURCE_PROTECTION_RECEIPT.json`;
3. `RAW_OPERATION_EVIDENCE.json` and its operation ordering;
4. fresh GET-only GitHub ruleset details and prospective-branch effective rules;
5. exact global attempt-ref absence.

It must then write an independent audit receipt and only afterward a newly generated fresh source-protection receipt. No repository mutation, attempt reservation, local lease, dispatch, production import, native worker, first interval, or provider claim is allowed.

The implementation file is deliberately absent. Expected first execution:

```text
9 tests
9 FileNotFoundError errors
0 assertion failures
no attempt or runtime state
```

The actual repository ruleset remains absent and the final global attempt ref remains HTTP 404. This RED does not authorize the administrative apply operation and does not consume the remaining native attempt.
