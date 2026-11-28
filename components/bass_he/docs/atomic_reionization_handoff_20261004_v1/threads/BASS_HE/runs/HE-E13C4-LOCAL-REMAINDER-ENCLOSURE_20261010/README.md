# BASS_HE E13C4 local remainder enclosure

Six fixed-gas local controls, exact captured binary64 lift, incoming correction zero. The delivered interval bounds concern continuous-minus-exact-frozen corrections. Physical/production HOLD.

## Read

- REPORT_KO.md: findings, exact scope, actual computations and limits.
- THEORY.md: detailed remainder and validated quadrature derivation.
- INDEPENDENT_REVIEW.json / INDEPENDENT_REVIEW_KO.md: separate decision reviewer.
- PLAN.json: contract fixed before new scientific runs.
- PHYSICAL_RESULT.json, NEXT_DAG.json: machine-readable results and next scope.
- NCP_LOCAL_CODEX_HANDOFF_KO.md: complete requested NCP local Codex prompt.
- NCP_EXECUTION_CONTRACT.json, EXECUTION_LOCK.json: executable scope and byte identities.

## Data and implementation

inputs/SIX_CONTROLS.json contains the six exact captured rows/stages, saved E13C3 correction and read-only E13C2 numerical reference. inputs/e13c3 retains the complete recovered prior payload; its solvers are not rerun by this node. code/directed_interval.py implements directed Decimal and Jet2; code/local_enclosure.py computes full-cell coefficient/derivative enclosures and remainder bounds. evidence/N32_P60.json, N128_P60.json, N512_P60.json, N32_P80.json contain four actual new runs; START/checkpoint and run directories preserve provenance/raw output.

The N512 arithmetic projection digest is 2be12c6fcadcefd17cf40a8f3b3a1a2656c8242a9c46279afe6796ec211a7514. It is an identity of deterministic saved numerical fields, not a proof by itself.

## NCP execution

From this full package root, with CPython3.12.x and a new output path:

```bash
python3 code/ncp_execute.py --out /absolute/new/ncp_run_directory --execute --timeout 180
```

This performs identity/host checks, one fresh six-control N512/P60 execution and actual output parity. Default without --execute only verifies identity/host; it does not evaluate new scientific accuracy. NCP has NOT_RUN in this delivered packet. Read the complete NCP prompt before execution.

The adapter's 7 boundary checks use explicitly synthetic one-scalar child fixtures under evidence/ncp_boundary_fixtures/. These are not physics or NCP executions. Its final metadata-only change adds an allowlist of thread/launcher environment values; evidence/ncp_verify_metadata is verify-only, and the earlier adapter source/lock remain under evidence/ncp_verify_only/.

## Evidence reuse and delivery

No unchanged old continuous/native/gas/Newton suites were rerun. E13C3 restoration checked sealed archive and99payload/89reviewbound identities once. Do not run old solvers to verify this deliverable. The default artifact is the complete ZIP; the additive Git projection omits large inherited inputs and synthetic fixture packages, but retains the current minimal runnable sources/data/results and all reviewable reports.

FILE_MANIFEST.json lists payload bytes and SHA256, excluding itself. The final delivery receipt is detached and records scientific_core_commit and provider ACK metadata. An ACK is not a remote restore. The existing E13C3 archive was actually restored for this work; E13C4 backup is separately reported. No self-containing archive/receipt identity is claimed.
