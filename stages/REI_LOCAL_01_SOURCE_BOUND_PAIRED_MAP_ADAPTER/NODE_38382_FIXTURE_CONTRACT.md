# Node 38382 fixture boundary

This stage does not contain the imported canonical fixture. Production remains
`STOP_INVALID` until the endpoint, full-field context, four-site owner context,
and reduction sidecar are supplied under external immutable SHA-256 pins.

The production loader additionally requires the exact repository-relative
`field_trial.py` path, source SHA-256, and Git blob OID, and verifies that the
same blob is present at the path in `HEAD`. It does not execute that source:
the canonical file obtains parent classes through an unpinned `sys.modules`
cache and `next(glob(...))`. Until every parent source is externally pinned and
loaded through an isolated closed loader, production stops with
`NODE_38382_FIELD_PARENT_AUTHORITY_MISSING`. Arbitrary module injection is
available only through the explicitly named `load_node_38382_fixture_for_test`
seam and is inadmissible evidence for a production or scientific claim.

At rebuild base `1893f12d14b212eb4b6bd637332824f692e6f4b3`, the field source
authority observed by the focused production-loader test is:

- path: `stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_R2A_R2_R1A_R1_R1_AFFINE_SET_PARAMETERIZED_TAYLOR_MODEL_CONTINUOUS_BRANCH_ENCLOSURE_LOCK/analysis/field_trial.py`
- SHA-256: `ae26814e03931ebd623f7125409d4a6e7f83e1c12205ca8cfe4b24de73460e14`
- Git blob: `e5580fcab1ce316e7f39c11e04493f8696c257dc`

Before replay, each fixture artifact is copied into a distinct Linux `memfd`.
The snapshot receives `F_SEAL_WRITE`, `F_SEAL_GROW`, `F_SEAL_SHRINK`,
`F_SEAL_SEAL`, and `F_SEAL_FUTURE_WRITE` when the running kernel supports the
latter. SHA-256, size, device, inode, and seals are checked before and after the
predecessor call. Replay receives only the sealed descriptors and their frozen
receipts; it never receives the mutable source paths. A source-inode mutation,
including mutate-and-restore during replay, therefore cannot change consumed
bytes. A host without the required sealed-memory support fails typed rather
than weakening this boundary.

There is likewise no accepting production replay API at this base. In
particular, a predecessor's self-reported `node_count`,
`endpoint_state_sha256`, or `hard_gates_pass` cannot establish a gate. The
production method stops with `NODE_38382_VERIFIED_REPLAY_ABI_MISSING` until a
closed verifier independently derives the node count, endpoint authority,
hard-gate result, and node-38382 predicate from the sealed fixture bytes and
calculation result. The synthetic replay API is named
`replay_and_predicate_for_test` and exists solely to exercise snapshot
plumbing; its result cannot discharge the production gate.

The eventual verified predecessor must replay all 46,080 nodes. Only its final
predicate is evaluated at node 38382. This bounded contract neither
materializes the absent fixture nor runs the excluded 46,080-by-three canonical
pilot. With the fixture absent, the default and first production stop remains
`NODE_38382_FIXTURE_MISSING`.
