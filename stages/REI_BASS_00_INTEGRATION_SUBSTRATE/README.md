# REI-BASS-00 integration substrate

This stage supplies a fail-closed custody and publication boundary for later
BASS/REC integration. It is not a numerical BASS lock and does not authorize a
scientific interval claim.

## Implemented boundary

- Exact BASS and REC authorities are caller-supplied tuples of repository URL,
  full commit OID, exact tree OID, and load-bearing blob path/OID pairs.
- Authority validation is local-only. Repository, Git/common-directory, and
  object-store descriptors remain pinned for the full invocation. Common and
  worktree configuration plus object-store namespace identity are replayed
  before and after every exact Git read. Promisor config and pack markers,
  partial-clone, worktree origin overrides, config includes, shallow history,
  alternates, and observable validation races are rejected.
- `GitCustodyReceipt` is a serializable, self-attested wire statement only.
  Successful local replay mints a process-local `AdmittedGitAuthority`
  capability. Claim-bearing graph construction rejects plain receipts.
- Certificate integration is a closed, canonical reference graph. Only SHA-256,
  byte length, media type, owner, role, and dependency edges are admitted. Raw
  certificate payloads are outside this representation.
- `validate_reference_graph_bytes` proves only structural self-consistency and
  returns `claim_bearing=False`. Serialized graph admission additionally needs
  both admitted authorities and an independently recorded full-payload SHA-256
  through `admit_reference_graph_bytes`.
- A validated publication uses an unnamed Linux `O_TMPFILE` inode. After
  validation, the write descriptor is replaced by a read-only descriptor to the
  same inode. The inode is linked into the destination via `/proc/self/fd`; no
  pathname-named temporary file exists to swap. Exact `0444` mode and the
  lexical parent-directory identity are rechecked before success.
- Event-set publication pre-pins every unique parent-directory descriptor and
  rejects a split namespace before publishing another item. It retains each
  publication descriptor through commit or rollback.
  Rollback atomically moves the current entry into a private quarantine inside
  that descriptor-pinned namespace. Automatic rollback never unlinks an inode;
  a replacement is restored create-only when possible and always reports
  `BASS_EVENT_TRANSACTION_ROLLBACK_RACE`. Quarantine tombstones are retained for
  explicit audited cleanup. The API does not claim multi-name atomicity.

## Current stop

`BASS_REC_EXACT_AUTHORITY_MISSING`

The exact BASS and REC physical authority pins are not present in this REI
checkout. They must be materialized locally and validated before a reference
graph can be treated as an integration receipt. Neither branch names nor pull
request endpoints may substitute for exact commit/tree/blob pins.

Raw certificate payload admission and the numerical Rust four-site operator are
separate later gates. The scientific status remains
`NO_PASS_FIRST_CANONICAL_INTERVAL`; the 46,080 x 3 canonical pilot is not run by
this stage.

## Focused verification

```bash
python3 -m unittest -v \
  stages/REI_BASS_00_INTEGRATION_SUBSTRATE/tests/test_bass_integration_substrate.py
(cd handoff/rei_bass_00_integration_substrate && sha256sum --check MANIFEST.sha256)
```
