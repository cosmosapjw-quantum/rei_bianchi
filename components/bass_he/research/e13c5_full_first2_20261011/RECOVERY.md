# Local recovery

The recovery tar includes the full task, including PATHS.jsonl, the preceding
reviewed branch-cover task, all 23 START input paths and their SHA-256 identities.
Absolute input paths are stored as relative archive names, without altering
source bytes. Restore into a staging directory and inspect before placing files
at their recorded locations. No scientific replay is part of recovery validation.

PATHS.jsonl is excluded from normal Git blobs. RESULTS.json and the raw execution
receipt remain byte-identical. The local recovery receipt records archive name,
hash, archive-member comparisons, and the compact Git publication state.
