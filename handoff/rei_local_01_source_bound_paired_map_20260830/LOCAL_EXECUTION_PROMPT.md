# Local executor prompt: REI-LOCAL-01 source-bound paired-map adapter

Copy the prompt below into the local executor together with the exact delivery
terminal SHA and stacked draft PR URL supplied by the publishing response.

---

You are continuing `cosmosapjw-quantum/rei_bianchi` from a provenance-only
handoff. The earlier stop `BLOCKED_BY_MISSING_LOCATOR` is resolved by an exact
`FETCH_AND_VALIDATE.py`. Do not reconstruct it, do not substitute the old
`FETCH_AND_VALIDATE.sh`, and do not infer authority from a branch tip.

## Bootstrap inputs

The external handoff supplies:

```text
DELIVERY_TERMINAL_COMMIT=<exact 40-hex SHA from the publishing response>
DELIVERY_DRAFT_PR=<exact GitHub PR URL from the publishing response>
```

The delivery branch is stacked on:

```text
agent/continuation/research-followthrough-20260830-r1
1893f12d14b212eb4b6bd637332824f692e6f4b3
```

Fetch only `DELIVERY_TERMINAL_COMMIT` without moving a ref or writing
`FETCH_HEAD`. Read
`handoff/rei_local_01_source_bound_paired_map_20260830/REMOTE_PUBLICATION.json`
from that exact commit. Cross-check its payload commit/tree, locator blob and
SHA-256, changed-path allowlist, base commit, and `merge_or_ready_authorized:
false` against the draft PR readback and the external response.

Materialize the locator by exact blob ID into a new path outside the repository,
verify its raw SHA-256, and invoke it exactly once:

```bash
python /absolute/pinned/FETCH_AND_VALIDATE.py \
  --repo /absolute/path/to/rei_bianchi \
  --destination /absolute/path/to/new-upstream-intake \
  --receipt /absolute/path/to/new-upstream-intake.locator-receipt.json
```

Capture the complete stdout outside both output paths and preserve its exact
`receipt_sha256` as external authority. Never recreate that expected value by
hashing the writable receipt. Before reading or executing any materialized
byte, run:

```bash
python /absolute/pinned/FETCH_AND_VALIDATE.py \
  --destination /absolute/path/to/new-upstream-intake \
  --verify-receipt /absolute/path/to/new-upstream-intake.locator-receipt.json \
  --expected-receipt-sha256 <exact receipt_sha256 from locator stdout>
```

Require `status: PASS_DESTINATION_BINDING`. Receipt existence or its embedded
PASS fields are not current-path authority. If another same-UID writer may have
accessed the output, run the fresh verifier again immediately before use.

Require:

```text
transport_status      PASS_IMMUTABLE_PAYLOAD_ONLY
scientific_validation NOT_RUN
canonical_adapter     NOT_RUN
pilot_46080x3         NOT_RUN
first_interval        NO_PASS
pr14_disposition      RECORDED_BLOCKED_MINIMUM_STEP
```

`remote_ref_status` may be `MATCH`, `DRIFT`, or `NOT_CHECKED`; it is
observational. Exact object, receipt digest, destination identity, or closure
mismatch is fatal. The locator requires Linux `renameat2`, `O_TMPFILE`, and
`/proc/self/fd` support. On an error before destination publication it retains
the original stage inode, restores mode 0700 through the continuously held FD,
and never deletes by pathname. Trust `undeleted_stage_pathname` only when
`stage_path_status` is `MATCHES_BOUND_IDENTITY` and the reported device/inode
match. For `SUBSTITUTED_DO_NOT_REMOVE_REPORTED_NAME`, do not remove that name.
`STAGE_PRIVACY_FAILURE` (exit 41) requires manual containment before proceeding;
it takes precedence while also reporting any concurrent repository drift.

Snapshot every existing worktree and dirty/untracked path first. Create one new
sibling worktree from the exact `DELIVERY_TERMINAL_COMMIT`. Never reset, clean,
stash, amend, rebase, force-push, merge, mark ready, enable auto-merge, or move
an existing branch. Preserve PR14, PR18, the R2 stage, old evidence, tables,
blocked archive, and `external/rec_bianchi.lock.json` byte-for-byte.

## Changes already delivered

- exact stdlib-only object locator with full-SHA unfiltered partial-clone
  refetch, sanitized Git repo/object/config environment, no-replace object reads,
  exact commit/tree/parent/path/mode/blob/raw-digest checks, semantic receipt
  cross-binding, exact-once authenticated-stdin validator execution, atomic
  no-clobber materialization, v2 fd-bound exact-closure destination receipts,
  externally retained receipt hashing, fresh consumer verification, and
  repository-state preservation;
- real-Git behavioral/attack tests, including branch drift, missing-object
  fetch, replace refs, rehashed manifest, symlink/mode/path, receipt mismatch,
  unexpected validator output, collision, and dirty/index/ref/worktree cases;
- approved adapter design:
  `docs/superpowers/specs/2026-08-30-rei-source-bound-paired-map-adapter-design.md`;
- task-by-task TDD plan:
  `docs/superpowers/plans/2026-08-30-rei-source-bound-paired-map-adapter.md`.

Read `CONTRACT.json`, the design, and the complete plan before editing.

## Authorized local implementation

Execute only REI-LOCAL-01. Implement:

```text
src/rei_bianchi/correlated_map_adapter.py
src/rei_bianchi/joint_implicit_remainder.py
src/rei_bianchi/source_bound_mprk_sdirk_operator.py
stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/
```

The implementation must retain one immutable dependency registry across the
full step, first half, and second half. Full and first-half start from the same
parent realization. Second-half receives the complete first-half affine state,
including all source/global/mixed/remainder owners. Distinct physical source
sites remain independent unless a pinned authority record permits an alias.

Certify the full 2x2 H and 3x3 He population implicit systems before invariant
projection and certify the whole thermal
residual. Temperature/state-dependent photoheating/context must be in the total
derivative or in a separately proved outer self-inclusion. A point solve,
midpoint Jacobian, or frozen-context root is not sufficient.

Bind the real four-site map only through `LockedMPRK22SDIRK2Operator`. Recompute
each site's coefficients/remainders from that site's state, time, forcing, and
owners. Certify every Patankar, `q_He,ion`, absorption/owner-normalization, OTS,
energy, and forcing denominator before division. The existing interval wrapper
is a comparison oracle only, never the runtime implementation.

Before implementation, finalize an explicit `INPUT_LOCK.json` over the complete
imported/dynamically-loaded/copied/opened code and data closure; named plan
tables are minimum roots only. Undeclared runtime imports/opens reject. Use the
pinned primitive-level outward interval/PCHIP backend (or an equivalently
verified pinned replacement) and independent high-precision oracle tests.

Every population solve and thermal predictor/gamma/final residual needs its own
source-bound full-enclosure certificate. Gate the physical state cone at every
parent, predictor, substage, endpoint, and public transform. Resolved OTS heat
enters thermal photoheat and the resolved ledger exactly once; unresolved OTS
is ledger-only.

Integrated ledgers must consume all four authenticated site models on one
dependency registry and prove joint feasibility; separate marginal intervals
that each contain zero are insufficient. Localize the earliest validated table
event, reject without candidate mutation, rebuild topology, and restart;
non-monotone or uncertified event tubes fail closed.

Transform both endpoints to dependency-preserving public coordinates first,
then form two-half minus full by owner ID, then range the same-site `vf`
polynomial, subtract asymmetric endpoint remainder intervals as
`[H_lower-F_upper, H_upper-F_lower]` unless a direct delta remainder
has its own certificate, and only then project to intervals. Do not subtract
interval widths or endpoints.
Reconstruct `x_HII=1-x_HI` and `x_HeII=1-x_HeI-x_HeIII`; public helium
remainders use the same owner with opposite sign (or an equivalent sum-zero
constrained block), never independent species boxes.

Use TDD for every slice. Record the meaningful RED, minimal GREEN, refactor, and
regression command. Required proof includes an independently solved nonlinear
fixture, locked node `38382` static-hull RED/adapter containment with its pinned
full-field aggregate/global context, point-degenerate three-lane parity,
deterministic `REIAFF1` split restart preserving complete authenticated
certificate payloads, transaction rollback,
and mutation detection for dropped remainder, false alias, frozen photoheat,
reversed difference, relaxed strict comparison, and one-lane acceptance.

Run only bounded node-local propagation against the authenticated full-field
aggregate/global context (or the locked full-field fixture while asserting only
node `38382`). Never renormalize a one-node slice. Do not run the canonical
all-46,080-node three-lane pilot; that is REI-LOCAL-02. Even on local success,
report exactly:

```text
adapter             IMPLEMENTED_AND_LOCALLY_CERTIFIED
canonical_pilot     NOT_RUN
first_interval      NO_PASS
scientific_pass     NOT_CLAIMED
performance         NONE
```

Run one independent PHYS-MATH audit followed by one independent PHYS-MATH-CODE
audit. Permit at most one bounded P0/P1 repair and differential retest. If any
certificate or gate fails, preserve the earliest exact failure and remove all
stale pass fields.

## Publication boundary

If and only if local implementation, tests, manifests, protected-input hashes,
and dual audit pass, create one new branch and one stacked draft PR against the
delivery branch. Use object creation and a single new-branch creation; never
update an existing ref. Read back exact head/tree/base/changed paths/checks.
Mock merge eligibility with read-only compare/status/PR metadata. Do not call a
merge API because it has no dry-run mode.

Return exact commits, trees, blobs, raw SHA-256 values, test commands/counts,
audit verdicts, remaining blockers, and links. Never replace
`NO_PASS_FIRST_CANONICAL_INTERVAL` unless a later separately authorized full
pilot and original-start interval proof satisfy their own contracts.

---
