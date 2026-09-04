# REI 03A4 Runtime Toolchain Path-Binding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent any alternate-path same-hash compiler or native-library witness from authorizing the final REI attempt when the post-lease production bridge will use different fixed runtime paths.

**Architecture:** Preserve the existing 13-field semantic byte lock and production bridge. Add one contract-owned lexical path map, validate each supplied witness against the resolved fixed production path, canonicalize a four-role path snapshot, bind its SHA-256 through preflight and all attempt receipts, and recheck the actual paths in the worker immediately before runtime entry.

**Tech Stack:** Python 3 standard library, canonical JSON/SHA-256, Git blob package sealing, GitHub Actions unittest workflows.

**Spec:** `docs/rei_runtime_bridge_03a4_toolchain_path_binding/RED_CONTRACT.md`

## Global Constraints

- Parent is exact RED head `2b2b717283e070c0d07b632e3a7eb99649f2044f`.
- Do not modify the production bridge or Rust numerical source.
- Do not change any of the 13 semantic-toolchain values or lock hash.
- Fixed runtime lexical paths are `/usr/bin/x86_64-linux-gnu-gcc`, `/usr/bin/ld`, `/usr/lib/x86_64-linux-gnu/libmpfr.so.6.2.1`, and `/usr/lib/x86_64-linux-gnu/libgmp.so.10.5.0`.
- Compare canonical resolved paths and bytes; symlink aliases are not independent authorities.
- No hosted-CI global ref, local lease, production import, worker, or native execution.
- Keep the PR Draft and preserve one remaining native attempt.

---

### Task 1: Contract and canonical runtime-path snapshot

**Files:**
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/CONTRACT.json`
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/common_v3_impl.py`
- Test: `tests/governance/test_rei_runtime_03a4_toolchain_path_binding_red.py`

**Interfaces:**
- Produces: `validate_runtime_toolchain_witness_paths(contract, *, cc, ld, mpfr, gmp) -> dict[str, Any]`.
- Snapshot fields: `schema`, `paths`, `sha256`; each role records `declared_path`, `resolved_path`, `sha256`, `size_bytes`, and `executable`.

- [ ] Add `runtime_toolchain_path_binding` to the exact contract schema with authority `POSTLEASE_PRODUCTION_PATHS` and the four lexical paths.
- [ ] Add strict contract validation for exact roles and paths.
- [ ] Resolve each contract path, require a regular file and executable bit for `cc`/`ld`, require the caller witness to resolve to that same file, then compare the actual file SHA-256 to the existing semantic lock.
- [ ] Canonically hash the closed snapshot and reject alternate paths as `RUNTIME_TOOLCHAIN_WITNESS_PATH_MISMATCH:<role>`.
- [ ] Add focused behavioral hostile tests for alternate-path rejection, wrong hash, missing path, and deterministic snapshot hashing.

### Task 2: Static preflight binding

**Files:**
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/successor_section0_preflight_bound_impl.py`
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/successor_section0_preflight.py`
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/common_v3_impl.py`

**Interfaces:**
- Consumes: the Task 1 snapshot.
- Produces receipt fields `runtime_toolchain_paths` and `runtime_toolchain_snapshot_sha256`.

- [ ] Validate runtime paths before the first Section-0 emitter invocation.
- [ ] Invoke the emitter only with the canonical resolved paths returned by the validator.
- [ ] Add the closed snapshot and its SHA-256 to the preflight receipt.
- [ ] Recompute the live snapshot in `validate_preflight_receipt` and require byte-for-byte equality and the same canonical hash.

### Task 3: Pre-lease and attempt-receipt propagation

**Files:**
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/common_v3_impl.py`
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/successor_runtime_controller.py`

**Interfaces:**
- `revalidate_successor_toolchain` returns `runtime_toolchain_paths` and `runtime_toolchain_snapshot_sha256`.
- `acquire_global_lease`, `create_local_lease`, and `create_dispatch_intent` accept and persist the snapshot hash.

- [ ] Run the same path validator before pre-lease Section-0 re-emission.
- [ ] Require the revalidation snapshot hash to equal the static-preflight snapshot hash before reservation.
- [ ] Bind the hash into global, local, and dispatch records.
- [ ] Extend `validate_attempt_receipts` to require equality across all records.

### Task 4: Worker pre-entry recheck

**Files:**
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/native_runtime_worker.py`

**Interfaces:**
- Consumes: dispatch snapshot hash and fixed contract path map.
- Produces: no new authority; validates the actual host immediately before `run_native_once`.

- [ ] Recompute the snapshot from the fixed runtime paths after all receipt checks and before runtime entry.
- [ ] Require equality with the dispatch/global/local snapshot hash.
- [ ] Record the snapshot hash in the runtime lineage only after successful pre-entry validation.

### Task 5: Closed-package reseal and verification

**Files:**
- Modify: `handoff/rei_runtime_prelease_import_firewall_green_20260903/PACKAGE_INDEX.json`
- Modify: `.github/workflows/rei-runtime-03a4-toolchain-path-binding-red.yml`
- Create: `tests/governance/test_rei_runtime_03a4_toolchain_path_binding_behavior.py`

**Interfaces:**
- Produces exact Git-blob closure for every modified package file.

- [ ] Turn the six-method RED contract GREEN.
- [ ] Run hostile behavior tests without requiring the historical host binaries by injecting temporary paths only into a test-specific contract and proving alternate resolved files are rejected.
- [ ] Reseal every changed package blob and verify the package index against exact HEAD.
- [ ] Run inherited authority/firewall tests and repository verifier.
- [ ] Confirm hosted CI created no preflight, attempt, dispatch, outcome, or native-runtime files.

### Task 6: Target-host operational boundary

**Files:**
- Create: `docs/rei_runtime_bridge_03a4_toolchain_path_binding/GREEN_CLOSEOUT.md`

- [ ] Record exact tested head/tree and workflow IDs.
- [ ] State explicitly that source GREEN does not establish availability of the historical compiler bytes.
- [ ] Require a read-only actual-path census next; only a matching actual runtime path may reopen 03A4.
- [ ] Preserve `GLOBAL_ATTEMPT_REF=ABSENT`, `REMAINING_NATIVE_ATTEMPTS=1`, and `NATIVE_RUNTIME=NOT_RUN`.
