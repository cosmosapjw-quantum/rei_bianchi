# Backup package layout

## Durable repository layers

- `main`: source, compact authoritative artifacts, provenance/status ledgers, handoff, sandbox and verification tooling.
- `archive/full-history`: every currently available historical bundle. Files above the GitHub hard object limit are split into verified chunks below 48 MiB.
- `checkpoint-b2c2b0c-r1-failclosed`: scientific checkpoint before backup receipt commits.
- `archive-full-history-2026-08-04`: archive payload checkpoint.

## External deliverables

1. `rei_bianchi_main.bundle`
   - cloneable Git bundle for immediate scientific continuation;
   - includes `main` and the scientific checkpoint tag.
2. `rei_bianchi_full_mirror.git.tar`
   - bare mirror containing all branches, tags, and Git objects;
   - preferred complete offline backup.
3. `rei_bianchi_main_worktree.zip`
   - convenient non-Git snapshot of `main`.
4. `rei_bianchi_handoff_package.zip`
   - lightweight interruption/thread-limit recovery package.
5. `rei_bianchi_BACKUP_RECORD.json`
   - authoritative package hashes and final local branch heads.

The external backup record, rather than `LOCAL_GIT_STATE.json`, is authoritative for package hashes because an archive cannot contain its own final hash without recursion.
