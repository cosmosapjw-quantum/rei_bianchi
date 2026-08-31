# Local execution prompt: REI-BASS-00

Continue from the pushed REI branch without weakening any typed stop.

1. Materialize the exact BASS and REC repositories locally as complete object
   stores. Do not use partial clone, promisor remotes or pack markers, shallow
   history, alternates, config includes, or worktree-scoped origin overrides.
   Preserve the repositories read-only during validation.
2. Obtain each authority independently as:
   - canonical repository URL;
   - full commit OID;
   - exact `commit^{tree}` OID;
   - every load-bearing file path and blob OID.
   Do not infer an authority from a branch name, PR number, working tree, ZIP
   endpoint, or semantic similarity.
3. Construct `GitAuthorityPin(project="BASS", ...)` and
   `GitAuthorityPin(project="REC", ...)`. Call
   `require_exact_bass_rec_pins`, then `validate_local_git_authority` on the
   corresponding repository paths. Preserve both returned
   `AdmittedGitAuthority` capabilities. A serialized `GitCustodyReceipt` is
   self-attested wire data and must never substitute for either capability.
4. If validation returns any `BASS_CUSTODY_*` or `BASS_GIT_AUTHORITY_*` code,
   stop. Do not fetch objects automatically and do not mutate the pin to match
   the checkout.
5. Create only digest/size/media-type/owner/role references and a DAG of
   `ReferenceEdge` objects. Build it with `build_reference_only_graph` and
   publish with `publish_reference_graph` into a new destination. Existing
   paths are a typed stop and must not be overwritten.
6. Treat `validate_reference_graph_bytes` as structural wire replay only; its
   result is explicitly `claim_bearing=False`. Call
   `admit_reference_graph_bytes` only with both admitted capabilities and an
   independently recorded SHA-256 of the complete serialized graph. Computing
   the expected digest from the bytes being admitted is not independent
   authority.
7. If an event transaction aborts, inspect `.rei-rollback-*` directories through
   the original custody namespace. A rollback race is
   `BASS_EVENT_TRANSACTION_ROLLBACK_RACE`; unrelated inodes are never
   automatically unlinked. Quarantine cleanup is a separate audited action.
8. Treat the resulting graph as reference custody only. Before any production
   solve, specify and implement a separate raw-certificate admission boundary
   that binds the exact Rust ABI artifact, receipt, source identities, and
   replay result. Do not reinterpret `REFERENCE_ONLY_NO_RAW_CERTIFICATE_PAYLOAD`
   as a numerical certificate.
9. Run the focused suite and manifest verification:

   ```bash
   python3 -m unittest -v \
     stages/REI_BASS_00_INTEGRATION_SUBSTRATE/tests/test_bass_integration_substrate.py
   (cd handoff/rei_bass_00_integration_substrate && sha256sum --check MANIFEST.sha256)
   ```

10. Preserve `NO_PASS_FIRST_CANONICAL_INTERVAL`. Do not run the 46,080 x 3
   canonical pilot in this handoff and do not mark a PR ready or merge it.

Expected first local stop until exact pins are supplied:

```text
BASS_REC_EXACT_AUTHORITY_MISSING
```
