# Delivery boundary

The immutable C1 source checkpoint contains the reviewed scientific contract,
finite diagnostic, fixtures, producer evidence, independent review, report,
stage DAG and resume instructions, plus the inherited root AGENTS.md.
Its 21 members are identified by SOURCE_MANIFEST.json and BACKUP_RECEIPT.json.

Both newly uploaded provider copies were read in full, matched the source
SHA256 and passed ZIP CRC. BACKUP_RECEIPT.json records the observed identities
and verification. No temporary download URL or collaborator metadata is stored.

These delivery files were written after the source ZIP was frozen, so they
are additional Git records and are not recursively added to that ZIP. A later
publication receipt identifies the scientific publication commit and draft PR;
the current remote branch head remains the authority for subsequent changes.
