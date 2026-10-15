# R9 bounded recovery intake

Observed on 2026-10-15 UTC. Read-only GitHub and Dropbox connectors; no NCP command was issued.

- PR151 is open and draft at `57e6e2d79c1a1ea4786d83b36c871abf581be738` (2 commits). Its body still describes pending Unit2 publication, but the current head and later delivery files establish that publication completed.
- `UNIT2_DELIVERY.json` is present at that exact GitHub commit and in Dropbox. The archive, standalone PDF and LaTeX each have recorded verified Drive and Dropbox destination hashes. This pass read those receipts; it did not independently download and hash the binaries.
- `PUBLISH_UNIT2.json` is in Dropbox, records the same commit with parent `13ebaff2d7c41f389140a3ea8af82e606889cae7`, and selected 652 files. It is absent from that GitHub commit (404), consistent with being written after the commit itself.
- `THREEE_COLLECTION_STATUS.json` and log record `collection_or_publication_failed` at 2026-10-15T15:24:03.612801Z. The collector stopped while waiting for Unit2 publication: `RuntimeError: Unit2 publication did not finish; collector not started`. Unit2 publication subsequently completed around 15:48Z. This is an orchestration failure, not evidence of a physics/FCI failure.
- The synchronized threeelectron_v6 case folder contains only launch.json, input.json, empty stdout.log and stderr.log; no receipt, result arrays, or terminal status. Its latest synchronized snapshot is 15:00:29Z. The current NCP case state is therefore unknown, not 'still running' and not 'failed'.
- UNIT3_RAW_DELIVERY.json and UNIT3_RAW_RETURN.md are absent both from the complete immediate Dropbox listing and from exact-commit GitHub paths (404).
- The actual Rust integration log states `8 passed; 0 failed` for deuterium_atomic. The library-only zero-test run remains separate.

## Recovery priority

Read the existing NCP case terminal receipt and process state first. Do not relaunch or delete anything merely because the collector failed. Collect and independently review a returned result, or classify an existing solver failure. Preserve the old failed collector evidence. Unit2 backup and publication need no blind repeat.

## Durable targets

- Unit2 archive: https://drive.google.com/file/d/1k2xnvrxMvUaQpTOGp-3K0dlrHNoQuIJT/view
- PDF: https://drive.google.com/file/d/15EuytSPKy9abpvJp2AJy7YrnrHQ6H5E4/view
- LaTeX: https://drive.google.com/file/d/1j1Va-GPdw-8fDTDF0Q4FnzEoAPGzcGnX/view
- PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/151
- Archive SHA256: `725cf8bf53d366b179d41708c4efc9477b29c6c6e0a748ac2d3585dbe33709a1`

Exact connector responses and extracted receipts accompany this note.
