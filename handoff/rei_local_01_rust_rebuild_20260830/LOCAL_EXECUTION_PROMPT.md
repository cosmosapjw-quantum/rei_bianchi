# REI-LOCAL-01 Rust-first host continuation

Continue only from the pushed draft-PR head of
`agent/implementation/rei-rust-rebuild-followthrough-20260830-r2`. Treat the
checked-out commit, its tree, `INPUT_LOCK.json`, and this handoff manifest as
independent identities. Do not reconstruct missing authority from prose and do
not replace any typed stop with a fixture, Python/JAX arithmetic, or an older
shell locator.

## 0. Intake and immutable state

1. Verify the PR head and tree, then run `git fsck --full` and inspect local,
   common, and worktree Git configuration. Reject shallow, promisor,
   partial-clone, alternates, and lazy-object state before reading authority
   bytes.
2. Verify both handoff manifests and the non-code math manifest. Verify every
   path and digest in
   `stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/INPUT_LOCK.json`.
3. Record all tool versions and full executable/dependency digests. The
   load-bearing numerical path is Rust 1.94.1 plus MPFR 4.2.1 at 256 bits with
   directed rounding. Python is orchestration only. JAX and `jaxlib` are
   forbidden on the load-bearing route.
4. Work in a new isolated branch/worktree. Never overwrite existing evidence.
   Update the durable checkpoint after each material delta. One blocker gets
   one implementation attempt and at most one distinct diagnostic retry.

The dependency order is **runtime boundary first**, then BASS/REC authority,
four-site ABI, node replay, real REIAFF1 restart, and formal replay. Sections
below describe the scientific data flow, but no load-bearing authority may be
consumed and no production evaluator may run until Section 5's fresh-process
boundary is green.

## 1. Admit exact BASS and REC authority

Follow `handoff/rei_bass_00_integration_substrate/LOCAL_EXECUTION_PROMPT.md`
exactly. Supply canonical URLs, full commit and tree OIDs, and every
load-bearing blob OID. A serialized custody receipt is not authority. Preserve
the `AdmittedGitAuthority` capabilities minted by validation and require an
independently recorded complete-payload SHA-256 before graph admission.
The attached BASS background/high-\(\ell\) project-source ZIP is a harness and
context bundle, not a complete Git object store and not a substitute for the
exact BASS or REC Git authorities.

Expected first stop before supplying those bytes:

```text
BASS_REC_EXACT_AUTHORITY_MISSING
```

## 2. Implement the real four-site native operator

Replace the intentionally non-constructible seam in
`src/rei_bianchi/source_bound_mprk_sdirk_operator.py` only after exact physical
evaluators and inputs are pinned. The successful native call must recompute,
not deserialize or echo, all of the following at each site in canonical order:

1. `population_t0`
2. `population_t1_predictor`
3. `thermal_tgamma`
4. `thermal_t1_final`

At every site recompute the state, forcing, dependency owner, shared-owner
ledger contribution, all denominators, implicit substage, and outward/asymmetric
remainder. The population tangent must solve the full interval equation

\[
A\,\delta Z = \delta b-(\delta A)Z,
\]

and the thermal residual must include temperature-dependent photoheating,
owner feedback, nonlinear curvature, and the outer-context self-inclusion. A
midpoint inverse, frozen context, fixture certificate, or Python/JAX fallback
is a hard failure. Reject zero-containing divisor intervals before native
division and require strict full-interval Krawczyk self-inclusion for every
implicit block.

Bind every raw certificate byte string to its Rust source, artifact, build
receipt, request, site, owner/context digests, and external authority. The
45-byte `REICERT1` object is a reference only and cannot substitute for those
bytes. Complete the public concrete operator only when the four-site graph is
claim-bearing under that external closure.

## 3. Materialize and replay node 38382

Supply immutable artifacts for the authoritative endpoint, full-field state,
four-site owner-normalization context, and reduction sidecar. Use the exact
`field_trial.py` path/SHA/Git-blob authority recorded in
`NODE_38382_FIXTURE_CONTRACT.md`; do not use the test-only module-injection
seam. Pin the entire parent-module dependency closure and load it in an
isolated namespace; the current source-only gate intentionally stops with
`NODE_38382_FIELD_PARENT_AUTHORITY_MISSING` instead of executing an unpinned
parent.

Replay the certified 46,080-node predecessor once and evaluate the final
predicate only at node `38382`. The verifier, not the predecessor response,
must derive node count, endpoint digest, hard gates, and the node predicate
from the sealed authority streams and computed result. Do not run the
46,080-by-three canonical pilot.

Until an independent verified-replay ABI exists, production replay must stop
with `NODE_38382_VERIFIED_REPLAY_ABI_MISSING`; predecessor-returned digest,
node-count, or hard-gate fields are self-attested and inadmissible.

Expected first stop before the four fixture roles exist:

```text
NODE_38382_FIXTURE_MISSING
```

## 4. Close the real REIAFF1 split restart

Run the actual four-site operator continuously and as a split/restart pair.
Require byte-stable preservation of owner registry and aliases, affine and
mixed terms, asymmetric remainders, raw certificates and external receipt
pins, exact certificate DAG, and legacy source/normalizer/normalized digests.
Exercise mutations for block/record order, ghost aliases/owners, missing or
changed payloads, graph edges/cycles, receipt swaps, asymmetric-bound swaps,
and legacy normalization drift. Format-only fixture tests do not close this
gate.

## 5. Establish the runtime/process boundary

The repository now has an invocation-scoped automatic observer and rejects a
production backend call without its factory-minted capability. That closes the
caller-authored-observation defect, but it is deliberately not claimed as a
hostile same-process or pre-start boundary. Execute the load-bearing route in a
fresh child whose kernel-enforced read/execute allowlist is installed before
any authority byte is consumed. Bind that policy and the observed
access/import receipt to the exact child executable and require the externally
pinned receipt at the production entrypoint. A Python audit hook alone,
same-process private token, or post-hoc `strace` log is not a hostile-process
boundary.

Expected stop until that boundary is provided:

```text
RUST_BACKEND_CAPABILITY_PROCESS_BOUNDARY_MISSING
BLOCKED_PRESTART_ELF_INTERPRETER_IDENTITY_NOT_ESTABLISHED
```

## 6. Run the local formal cross-checks

Record raw stdout/stderr, exit code, executable identity, and dependency
identity for:

```bash
wolframscript -file stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/research/noncode_math_20260831/verify_rei_noncode_derivations_20260831.wl
wolframscript -file stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/formal/tangent_and_krawczyk.wl
sage stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/formal/tangent_and_krawczyk.sage
Singular -q stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/formal/tangent_and_krawczyk.sing
lake env lean /absolute/path/to/TangentAndKrawczyk.lean
coqc stages/REI_LOCAL_01_SOURCE_BOUND_PAIRED_MAP_ADAPTER/formal/TangentAndKrawczyk.v
```

Run Lean only inside an independently pinned workspace and record the exact
Lean version plus `lean-toolchain`, `lake-manifest.json`, mathlib commit/tree,
and their hashes. For Wolfram/xAct, record the kernel and xAct identities. A
green toy proof remains a bounded formula result; it does not prove the
four-site physical evaluator.

## 7. Validation and terminal decision

Rerun, in increasing cost order, syntax/import checks, every focused Python
suite, the native Rust 11-case suite, the 96-family/6,144-corner independent
oracle, full repository/payload verification, PHYS-MATH audit, and a fresh
PHYS-MATH-CODE audit. Permit only one coherent P0/P1 repair after those audits.
Seal all receipts and manifests after the last byte changes.

Do not execute the 46,080-by-three canonical pilot in this handoff. Unless all
host gates above close, terminate exactly as:

```text
adapter             STOP_INVALID
canonical_pilot     NOT_RUN
first_interval      NO_PASS_FIRST_CANONICAL_INTERVAL
scientific_pass     NOT_CLAIMED
scientific_publication NOT_RUN
```

Draft PR publication is allowed for this fail-closed substrate; scientific or
canonical-result publication is not. Never mark the draft PR ready, merge it,
or report a scientific pass from the
generic kernel, formal toy lemmas, node-38382 predicate, or format-only restart
tests.
