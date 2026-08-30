# REI-LOCAL-01 bootstrap, specification, and local handoff

This package resolves the earlier `BLOCKED_BY_MISSING_LOCATOR` stop without
changing the scientific verdict. It supplies the exact stdlib-only
`FETCH_AND_VALIDATE.py`, behavioral tests, a frozen contract, and the prompt for
the local scientific implementation.

## Current result

The locator authenticates and materializes the immutable continuation graph:

```text
053b97c56e089e28a83f37d79a4128ed3cdae9f4
  -> 82c67218248cb896019b2bffc590da1260a214fc
  -> 70330fa5e833411bfa9337691e5773431ccd5ac3
  -> 1893f12d14b212eb4b6bd637332824f692e6f4b3
```

On success the CLI returns transport/provenance status, an observational
remote-ref status, and an out-of-band digest for the locator receipt:

```json
{
  "canonical_adapter": "NOT_RUN",
  "first_interval": "NO_PASS",
  "pilot_46080x3": "NOT_RUN",
  "pr14_disposition": "RECORDED_BLOCKED_MINIMUM_STEP",
  "remote_ref_status": "MATCH",
  "receipt_sha256": "<64 lowercase hex retained from stdout>",
  "scientific_validation": "NOT_RUN",
  "transport_status": "PASS_IMMUTABLE_PAYLOAD_ONLY"
}
```

`remote_ref_status: DRIFT` is observational and does not invalidate retained
pinned objects. A missing or mismatched pinned object remains fail-closed. The
`receipt_sha256` value is intentionally not stored inside the receipt (which
would create a self-hash cycle); retain it from stdout as external authority.

## Use

The repository must be an existing non-bare, non-shallow SHA-1 Git worktree. The destination
and receipt must not exist and must be outside every worktree and Git directory.

```bash
python handoff/rei_local_01_source_bound_paired_map_20260830/FETCH_AND_VALIDATE.py \
  --repo /absolute/path/to/rei_bianchi \
  --destination /absolute/path/to/new-intake \
  --receipt /absolute/path/to/new-intake.locator-receipt.json
```

Before consuming any materialized byte, use the retained stdout digest for a
fresh binding check:

```bash
python handoff/rei_local_01_source_bound_paired_map_20260830/FETCH_AND_VALIDATE.py \
  --destination /absolute/path/to/new-intake \
  --verify-receipt /absolute/path/to/new-intake.locator-receipt.json \
  --expected-receipt-sha256 <exact digest retained from locator stdout>
```

Only `PASS_DESTINATION_BINDING` from that command authorizes the current
pathname at the instant of verification. Never derive the expected digest by
rehashing the possibly replaced receipt itself.

The script may refetch the exact full terminal SHA with `--no-filter --refetch`
when a blobless/partial clone lacks the pinned reachable closure. It uses no
checkout, worktree creation, ref update, `FETCH_HEAD` write, submodule recursion,
or branch-tip authority. Ambient Git repo/object/index/config routing variables
are scrubbed for both locator and validator processes. It snapshots HEAD, refs,
pseudorefs, shallow metadata, index, worktrees, and dirty/untracked status
before and after. Only object-database growth is allowed.

The pinned validator is read with no-follow semantics, authenticated, and those
same bytes are run exactly once through `python -I -B -`; its pathname is never
reopened as execution authority. The materialized tree must contain exactly the
13 manifest entries, the externally pinned manifest, and the upstream terminal
publication receipt.
Files, directory closure, types, and modes are revalidated after execution.
The private staging-root inode/type/mode is bound before validation and checked
again after publication, so a source-name substitution cannot earn a receipt.
The destination uses Linux `renameat2(RENAME_NOREPLACE)` and the complete
sidecar is built in an anonymous `O_TMPFILE` inode and uses an atomic
capability-free `/proc/self/fd/<fd>` + `linkat(AT_SYMLINK_FOLLOW)` no-clobber
link. Receipt bytes/type/mode/digest and the fd-bound destination are fully
verified before that link, and the link is the last fallible semantic step.
Linux `renameat2`, `O_TMPFILE`, and procfs are required; unsupported
filesystems/platforms fail closed.

The v2 receipt binds the canonical destination path, root device/inode/type/mode,
and an exact fd-relative closure digest independently derived from authenticated
Git bytes. There is no false cross-path atomicity claim: if sidecar publication
loses a race, the authenticated destination is retained and concurrent owner
data is never deleted by pathname rollback. On any earlier error, the randomized
staging inode is restored to mode 0700 through its continuously held directory
FD and retained; the locator never performs pathname-based recursive cleanup.
An `undeleted_stage_pathname` is emitted only if a final no-follow lookup still
matches the held device/inode/type. If the name was substituted, only the bound
identity and `SUBSTITUTED_DO_NOT_REMOVE_REPORTED_NAME` status are emitted. A
failed fd-mode restore is the explicit `STAGE_PRIVACY_FAILURE` (exit 41), which
dominates but also reports concurrent repository drift so the unsafe retained
mode cannot be hidden. Remove a retained stage only after matching the reported
identity.

A same-UID writer can mutate either pathname after return. The receipt alone,
or its embedded PASS fields alone, therefore does not authorize later pathname
contents. Preserve the stdout digest outside the writable output area and run
the fresh verifier immediately before use; stronger historical guarantees need
permission separation, a protected attestation store, or filesystem sealing.

## Verify the locator

No external Python package is required for the locator or its tests.

```bash
python -m unittest -v \
  handoff/rei_local_01_source_bound_paired_map_20260830/tests/test_fetch_and_validate.py
```

The 38 tests use real temporary Git repositories and cover full-SHA and blobless
unfiltered closure fetching,
exact commit parents/trees, raw-byte materialization, branch drift, replace
refs, a self-consistent rehashed-manifest attack, mode/symlink/path attacks,
hostile ambient Git routing/config, validator pathname replacement, semantic
publication cross-binding, exact-once validator execution, unexpected files or
directories, metadata-mode mutation, dangling symlinks, atomic no-clobber
target/source substitution and publication races, expected-vs-observed closure
binding, out-of-band receipt hashing, consumer rejection after destination or
receipt mutation, strict rejection of rehashed forged receipt contracts, a pure
receipt-link `EEXIST` race, post-link close failures, pre-receipt repository drift,
fd-safe mode-0700 error-stage restoration/substitution reporting,
shallow-repository rejection, raw CRLF/NUL preservation, and preservation of
dirty/staged/untracked/ref/index/worktree state.

## Scientific implementation handoff

Read, in order:

1. `CONTRACT.json`;
2. `LOCAL_EXECUTION_PROMPT.md`;
3. `docs/superpowers/specs/2026-08-30-rei-source-bound-paired-map-adapter-design.md`;
4. `docs/superpowers/plans/2026-08-30-rei-source-bound-paired-map-adapter.md`.

Those documents authorize a future local implementation and bounded local
certification of the source-bound paired-map adapter. They do not authorize the
46,080-node three-lane pilot, a first-interval pass, a merge, or a ready
transition.

## Files and authority

- `FETCH_AND_VALIDATE.py`: executable transport/provenance locator;
- `tests/test_fetch_and_validate.py`: stdlib behavioral/attack tests;
- `CONTRACT.json`: exact upstream pins, claim boundary, and delivery paths;
- `MANIFEST.sha256`: raw SHA-256 closure for this package, excluding itself and
  the later terminal publication receipt;
- `TESTS.log`: fresh checks run for this delivery;
- `LOCAL_EXECUTION_PROMPT.md`: local-only next-stage prompt;
- `REMOTE_PUBLICATION.json`: added in the terminal publication commit and kept
  outside the immutable package manifest to avoid a hash cycle.

Git object identity proves exact bytes and ancestry, not signed authorship. The
four upstream commits and this delivery are not represented as GPG-signed
attestations.
