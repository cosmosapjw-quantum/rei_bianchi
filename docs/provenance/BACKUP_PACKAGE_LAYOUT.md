# Backup package layout

## Durable repository layers

- `main`: source, compact authoritative artifacts, provenance/status ledgers, handoff, sandbox and verification tooling.
- `archive/full-history`: all currently recoverable historical bundles. Files above the GitHub hard object limit are split into verified chunks below 45 MiB.
- `checkpoint-b2c2b0c-r1-failclosed`: scientific checkpoint before backup receipt commits.
- `backup-offline-recovered-2026-08-05`: repaired main checkpoint after the missing-mirror incident.
- `archive-full-history-recovered-2026-08-05`: repaired archive payload checkpoint.

## External deliverables

1. `rei_bianchi_main_recovered.bundle`
   - cloneable Git bundle for immediate scientific continuation;
   - includes `main` and scientific/recovery tags.
2. `rei_bianchi_full_mirror_recovered.git.tar.part-*`
   - numbered parts of the complete bare mirror;
   - reassemble using the supplied script and verify against the parts manifest;
   - preferred complete offline backup after the original single tar failed upload-status processing.
3. `rei_bianchi_main_worktree_recovered.zip`
   - convenient non-Git snapshot of repaired `main`.
4. `rei_bianchi_handoff_package_recovered.zip`
   - lightweight interruption/thread-limit recovery package.
5. `rei_bianchi_full_mirror_recovery_manifest.zip`
   - reassembly scripts, hashes, branch heads and recovery explanation.

The external recovery manifest is authoritative for package hashes because an archive cannot contain its own final hash without recursion.
