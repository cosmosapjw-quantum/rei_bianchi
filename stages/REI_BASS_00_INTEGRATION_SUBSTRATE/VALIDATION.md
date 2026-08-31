# Validation matrix

| Requirement | Public seam | Focused evidence | Status |
| --- | --- | --- | --- |
| Missing BASS/REC identities stop with a stable code | `require_exact_bass_rec_pins` | missing and reversed-authority tests | Confirmed |
| No lazy Git object acquisition | `validate_local_git_authority` | common/worktree promisor config, pack-marker, partial-clone, include mutation tests | Confirmed |
| Exact reads cannot cross a mutable object namespace | descriptor-pinned Git custody snapshot | alternates and promisor-marker insertion between exact reads | Confirmed |
| Worktree config cannot shadow pinned origin | effective authority closure | worktree `remote.origin.url` override mutation | Confirmed |
| Commit/tree/blob identity is exact | `validate_local_git_authority` | valid local object set plus tree/blob mutations | Confirmed on synthetic repositories |
| Self-attested receipts cannot become claim authorities | `build_reference_only_graph` | plain-receipt rejection | Confirmed |
| Wire replay is explicitly non-claim-bearing | `validate_reference_graph_bytes` | status and `claim_bearing=False` regression | Confirmed |
| Claim admission binds external authority and payload identity | `admit_reference_graph_bytes` | admitted capability plus full-payload digest success/digest mutation | Confirmed on synthetic repositories |
| Certificate graph stores references only | graph build/wire/admission APIs | canonical replay, raw-payload mutation, digest mutation, cycle/unknown-node tests | Confirmed |
| Validated inode is the published inode | `publish_validated_bytes` | inode equality, callback mode mutation, destination-race, existing-destination tests | Confirmed on Linux O_TMPFILE filesystem |
| Receipt path remains bound to its parent inode | descriptor-pinned publication | parent rename and lexical replacement mutation | Confirmed |
| Event items cannot split across parent namespaces | `publish_event_transaction` | parent replacement between first and second publication | Confirmed |
| Failed event publication retains original namespace | `publish_event_transaction` | parent-directory rename after first publication | Confirmed |
| Rollback never deletes a swapped unrelated inode | descriptor-pinned quarantine | atomic-rename race injection and inode comparison | Confirmed |
| BASS/REC physical source is authoritative | exact external pins | pins are absent | Blocked: `BASS_REC_EXACT_AUTHORITY_MISSING` |
| Numerical BASS integration is certified | not in this stage | no numerical run | Not claimed |

Fresh focused command on 2026-08-31 UTC:

```text
python3 -m unittest -v stages/REI_BASS_00_INTEGRATION_SUBSTRATE/tests/test_bass_integration_substrate.py
Ran 33 tests
OK
exit 0
```

The synthetic Git repositories in the custody tests prove the mechanism. They
are not semantic substitutes for the missing exact BASS and REC repositories.
The admission capability is API type-state within one process, not a hostile
same-process security boundary. Independently recorded authority and payload
digests remain mandatory. Rollback quarantine directories are retained until a
separate audited cleanup verifies their contents.
