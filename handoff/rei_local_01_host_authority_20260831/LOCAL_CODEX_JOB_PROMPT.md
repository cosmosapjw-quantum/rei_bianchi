# Local Codex job — REI Rust host-authority Git-small continuation

You are the single root local Codex job responsible for continuing
`cosmosapjw-quantum/rei_bianchi`. Perform every remaining action that requires
the user's host, installed formal systems, exact external bytes, or native
runtime. Do not hand ordinary commands back to the user. Ask only for a missing
absolute locator or an OS/GitHub approval that cannot be obtained by the job.

## Immutable authority

- remote branch:
  `agent/implementation/rei-git-authority-transport-20260831-r1`
- stack parent: commit
  `d549c91fe078b2e9f567c09f2be50df95fb28d79`, tree
  `53f69801e733f045b4925cb9d4d4b21d6c1f71c3`
- historical reconstruction base: commit
  `59c3c9d135860cf3d359a0b70c370eb65b918898`, tree
  `c6ee7d9959c5f5ffe1aa87f056b8c90cd1dd9653`
- user-reported checkpoint `c7792c854fb00ba6bbed31baa9c2e3da13ceee9e`
  is not a usable base unless its exact object later materializes and is
  independently admitted
- external-input contract: `CONTRACT.json`
- Git-resident small-input manifest:
  `git_authority_transport/SMALL_INPUTS_MANIFEST.json`
- Git-resident small-input directory:
  `git_authority_transport/small_inputs/`
- technical intake procedure: `LOCAL_EXECUTION_PROMPT.md`
- sealed-native procedure:
  `../rei_sealed_native_build_authority_20260831/LOCAL_EXECUTION_PROMPT.md`
- downstream Rust continuation:
  `../rei_local_01_rust_rebuild_20260830/LOCAL_EXECUTION_PROMPT.md`

Only Sections 1 through 7 of that older downstream prompt remain normative.
Its opening branch/base instruction is superseded by this active continuation
branch and the exact pushed head/tree observed by this job. Never switch back
to its older branch after beginning this continuation.

First fetch read-only refs, resolve the remote branch to an exact commit/tree,
and create a new isolated worktree and continuation branch. Preserve every
existing dirty/untracked checkout and worktree. Verify all handoff manifests
including `MANIFEST.sha256` and
`git_authority_transport/MANIFEST.sha256` before interpreting their contents.
Never substitute semantically similar
archives, toolchains, commits, locators, receipts, or host binaries for locked
bytes.

## Codex execution policy

1. Own the complete local execution. Use local Codex subjobs for independent
   read-only audits or disjoint implementation tasks when useful, but keep one
   root job responsible for the dependency graph, evidence classification,
   final diff, and claim ceiling.
2. Keep a durable progress ledger from the first command. After each bounded
   work unit, record exact command, exit status, input/output digests, observed
   versus inferred facts, first failing gate, and every intentionally unrun
   successor.
3. Use one coherent repair for a verified P0/P1 defect, then repeat its focused
   tests and an independent audit. Do not consume time in meta-review loops or
   reconstruct missing authority from prose.
4. Commit and push recoverable checkpoints on an isolated branch. Maintain a
   stacked **draft** PR; never mark ready, merge, rewrite unrelated history, or
   modify another worktree. A failed gate is still a valid checkpoint when its
   evidence is precise and the scientific claim is not promoted.
5. Python may orchestrate dependency registries, REIAFF1, transactions, and
   APIs. It is not the load-bearing numerical backend. Do not execute JAX or
   `jaxlib`. The numerical route is Rust 1.94.1 with MPFR 256-bit directed
   rounding.

## Required dependency order

### 0. Bootstrap the immutable Git checkout

Before touching either external authority package, verify the remote branch,
exact commit/tree, Git object integrity, clone configuration, and Git-resident
handoff manifests in a new isolated worktree. Reject shallow, promisor,
partial-clone, alternates, lazy-object, and worktree-config state.

### 1. Git-small plus exact Rust external intake

The four small contract inputs are already Git-resident under
`git_authority_transport/small_inputs/`; verify them against both
`SMALL_INPUTS_MANIFEST.json` and `CONTRACT.json`. Do not ask the user to
download those four files. Ask only for one absolute, real non-symlink source
directory containing:

```text
08-rust-1.94.1-x86_64-unknown-linux-gnu.tar.xz
size        192287020
SHA-256     294b3d81fa72e62581276290c60c81eb8b58498d333d422ca1dfc432877d0c40
```

If that locator is unavailable, record exactly
`RUST_ARCHIVE_SOURCE_MISSING`, push a durable stacked draft checkpoint, and
stop all successors. Do not broaden the search or substitute a similar Rust
archive.

Use `git_authority_transport/materialize_small_plus_rust.py` to construct a
new staged source root and a byte-bound mixed-source receipt. It must run
after Git manifest verification but before repository numerical/native imports
and must not execute, extract, or source any input member. Then use the
existing `materialize_authority.py` with that staged source root to install all
five exact files into a new external authority root. The final production
materializer's source and destination roots must be distinct, real,
non-symlink directories; preserve its byte-bound receipt and require an
identical idempotent second invocation. Run in an exclusive authority tree
with no concurrent writer: either receipt is point-in-time byte evidence, not
kernel-enforced pathname immutability.

Now verify all 36 `INPUT_LOCK.json` path descriptors against the materialized
bytes and preserve the result. This verification and step 0 must pass before
the sealed supplement is inspected or extracted.

### 2. Sealed native authority

Obtain exactly:

```text
REI_SEALED_BUILD_DRIVER_AUTHORITY_20260831.v2.tar.xz
size        51199448
SHA-256     74b59278ade83c8b5935d5d592ae3d4d45e30634aece9daa6d80ea0b28e9719b
manifest    f8f6c84eaf10acd5ddf5a8f4b24d7c35736b9a6bd92a45de505e2966a05e0391
```

Use only the supplied safe extractor and verifier. Extract into a new external
directory; never overlay `/`, `/usr`, `/lib`, the repository, or another
authority tree. A verifier PASS establishes packaged-member byte identity
at the observation time only. Exclude concurrent writers. It does not
authorize compilation or execution.

### 3. Complete immutable Section 0

Complete the Rust/LLVM/stdlib/MPFR/GMP identity closure without importing
repository Python or starting a bundled member. If any exact byte is absent or
mismatched, stop immediately.

### 4. Compile and audit the host process boundary

Implement the unresolved kernel-mediated pre-start gate under
`stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/runtime_boundary/` with
these durable artifacts:

```text
POLICY.schema.json
POLICY.json
compile_runtime_boundary.py
verify_runtime_boundary.py
tests/test_runtime_boundary.py
receipts/RUNTIME_BOUNDARY_RECEIPT.json
MANIFEST.sha256
```

The compiler and verifier must fail closed on unknown fields or undeclared
mounts. Pin `bwrap` (or the admitted equivalent), child executable, ELF
interpreter, dynamic libraries, repository/input/output roots, environment,
`/proc`, `/dev`, networking, and every read/write/execute mount. The allowlist
must be installed before the child interpreter or authority starts. Do not
bind the host root or broad host `/usr`, `/lib`, `/etc`, or workspace.

`POLICY.json` must bind the exact repo commit/tree, compiler/verifier, sealed
archive/manifest/contract, child and production entrypoint, all mount source
and target identities, namespace flags, environment, and output root.
`RUNTIME_BOUNDARY_RECEIPT.json` must bind the policy SHA-256, child/ELF closure,
production request/response digests, observed access/import/exec inventory,
and mutation probes. It may say PASS only if undeclared open, import,
executable, dynamic-library, mount, network, and write attempts are each
denied; declared accesses succeed; source authority trees are made
kernel-read-only before final re-verification and remain so through child
exit; and the production entrypoint rejects a missing, changed, replayed, or
caller-authored receipt.

Integrate receipt verification into the fresh-process launcher consumed by
`analysis/rust_source_bound_thermal.py`; retain its factory-minted invocation
capability. Have an independent local Codex audit falsify the policy and
receipt with the denial/mutation families above. Only the exact policy, green
tests, observed receipt, manifest, and production-entrypoint mutation tests may
discharge the boundary. A rendered argv fragment or matching `cc`/`ld` hash is
not a PASS.

### 5. Continue only after the boundary is green

Follow Sections 1 through 7 of the downstream Rust handoff in dependency
order, with its old branch/base sentence superseded as stated above:

1. admit exact BASS/REC authority and source-bound evaluator/kernel inputs;
2. connect the certified Rust thermal certificate to the concrete four-site
   operator at `population_t0`, `population_t1_predictor`, `thermal_tgamma`,
   and `thermal_t1_final`, recomputing state, forcing, owner, denominators,
   implicit substages, and remainder at every site;
3. run the certified 46,080-node predecessor replay once and decide only node
   `38382`; do not replace the trial class produced by
   `field.make_trial_class(repo)` with raw `UncertaintySecondOrderTrial`;
4. verify adapter containment, event transaction, rollback/mutation families,
   joint ledger, and real-operator split restart;
5. bind the certificate payload to strict REIAFF1 metadata/block ordering,
   ghost aliases, external receipt digest, legacy-normalization hash, mixed
   terms, asymmetric remainder, and the full certificate graph;
6. after those gates, run the available Wolfram/xAct, SageMath/Singular,
   Lean/mathlib, and Rocq cross-checks, followed by PHYS-MATH and then
   PHYS-MATH-CODE audit;
7. allow at most one evidence-backed P0/P1 repair, rerun all affected tests,
   update the durable checkpoint, push, and update only a stacked draft PR.

The `46,080 x 3` canonical pilot is explicitly outside this work unit and must
remain `NOT_RUN`, even if every preceding local gate passes.

## Mandatory stop and report contract

At the first failed prerequisite, preserve the exact failure and stop all
successors. Never report an expected downstream failure as observed. The final
local response must include branch, commit, tree, draft-PR URL/status, exact
tests and manifests run, first failing gate, changed files, external receipts,
and a NOT_RUN table.

Unless a later authorized work unit actually closes the relevant scientific
gate, retain exactly:

```text
adapter                STOP_INVALID
canonical_pilot        NOT_RUN
first_interval         NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass        NOT_CLAIMED
scientific_publication NOT_RUN
```
