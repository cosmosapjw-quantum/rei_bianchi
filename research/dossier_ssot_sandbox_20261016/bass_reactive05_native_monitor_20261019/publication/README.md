# Publication receipts

These files are added after the scientific ZIP is fixed. `FINAL_RECEIPT.json` joins the exact scientific commit/tree and full ZIP to actual provider acknowledgement, provider hash/size evidence, and separate Drive/Dropbox raw-restore results. `FINAL_HANDOFF.md` is the current restart entry point.

The scientific archive remains byte-identical. Its local archive-creation receipt predates upload completion; the later final receipt records the completed cloud states. Exact final Git HEAD is published outside this directory to avoid a receipt hashing its own commit. No private download URLs or account metadata are published.

`ARCHIVE_IDENTITY.json`, `PROVIDER_IDENTITIES.json`, `DRIVE_RAW_RESTORE.json`, `DROPBOX_RAW_RESTORE.json`, `PACKAGING_EXECUTION.json`, and `RESTORE_ASSETS_CREATED.json` retain their distinct scopes. Local patch and bundle verification used separate parent-only object seeds; unchanged missing parent blobs and actual shallow boundaries are disclosed. The full 133-input crate is directly included in the ZIP.
