# External-audit shipping packet

## Delivery verdict

**Shipping with risk — external review enablement only.**

The branch packages all recoverable in-scope evidence for external audit. It does not cure or waive any numerical, physics, validation, custody, or production blocker.

## Frozen Git identity and target

- Repository: `cosmosapjw-quantum/rei_bianchi`
- Base branch at packaging start: `agent/ode-four-loop-audit-hardening-20260823`
- Base HEAD: `111b6ace750e36e218df7fc9626c6bad2ec19971`
- Base tree: `2f541ee051f0844bdeed88fd2dcba2a0c54ab035`
- External-audit branch: `audit/ode-four-loop-external-20260823`
- Remote: `origin` = `https://github.com/cosmosapjw-quantum/rei_bianchi.git`
- Remote visibility: public; the pushed audit artifacts will be publicly readable.
- Commit resolution: the delivery commit is the commit containing this packet at the external-audit branch tip. The exact local/remote SHA is checked after the non-force push and reported in the operator handoff.

## Source inventory

| Root | Files | Bytes | Deterministic source-tree digest |
|---|---:|---:|---|
| Candidate stage N | 71 | 537,800 | `928c85fc1fbab351252b757836004ff5ce3b96384f58723514383ee5367226b5` |
| Physics loop `/tmp/rei-ode-physics-loop.U8P8Z6` | 68 | 174,050 | `93b995182930e14779e3a6ce67a1913e526de4148ab491f039a579ffc813570f` |
| Coding loop `/tmp/rei-ode-coding-loop.4qpipi` | 49 | 113,027 | `0b11a4e22b72b15d1aee7906c9632b70bf7240e1b4acf44ff2f4847d1fb13635` |
| Integrated scratch top level | 3 | 53,052 | `e0709c241b2fa2617d6d2c4f8b8832bbac5df16da1e3dcde1cdb26cefe92417e` |
| User-supplied harness ZIP inputs | 2 | 58,181 | Per-file hashes below |
| **Total** | **193** | **936,110** | labeled source-set digest `f72ec60fa81080ec86d37c970b5229f1fdf827a63fb9fa896a978a6a59b2ad82` |

Harness input SHA-256:

- `physmath-research-harness-gpt56.zip`: `9adde688f8020e7feb2c1c0304b3204dbe70dd01e2d87e64a5c4eb357c019934`
- `physmath-coding-harness-gpt56.zip`: `6e67e999a0c19f6ed9de7c339067cc11691d5cf5cb662a11756d8fc393c849b4`

The exact unabridged per-file values are in `SOURCE_FILE_MANIFEST.json`. The package preserves 94 files with source mode 0644, 93 with 0664, and four executable files with 0755. Git can preserve the executable distinction but not every group-write or directory-mode bit.

## Evidence already present; not rerun during shipping

The candidate contains the previous detailed integration report, validation ledger, manifest, raw command streams, run sidecars, and independent adversarial review. Shipping relies on those frozen records and does not rerun them.

- Integrated report SHA-256: `26fd6a56fc0dcaab157a6abd63a3906905a5cc42c4d6a362805c5f027c2affa7`
- Independent review SHA-256: `b4ee087ad0a576a504e96e60227fdaf5e315422edc6144af596f4a56c3bd4422`
- Audit manifest SHA-256: `2eb9a4bf2a37e70fac6c1fb00109b47c5d78432e61052e56802de5dde711043e`
- Additive preimage manifest SHA-256: `ba71b4860328d9535ec5709d084176ed72c749264154ae61ff769dc4e5a7f6b0`
- Prior integrated decision: `STOP_INVALID`
- Independent disposition: `PARTIALLY_CONFIRMED`
- Promotion disposition: `HOLD / FORBIDDEN`

The independent review retains four medium and two low findings, including pre-limit resource use in exact arithmetic, incomplete process-tree termination, recorder-source nonbinding, incomplete physical-inventory validation, oracle schema robustness gaps, and a one-test narrative count discrepancy. See the candidate's `INDEPENDENT_AUDIT_REVIEW.md` for evidence and line-level detail.

## Explicit no-test receipt

During this shipping operation:

- no unit, integration, property, numerical, solver, parity, benchmark, package, security, or scientific test is run;
- no prior frozen command is rerun;
- no source implementation or research conclusion is repaired or altered;
- only inventory, byte/hash/mode comparison, JSON parsing, Git index inspection, checksum verification, branch creation, commit, push, and remote-ref equality checks are permitted.

These are custody/delivery checks, not scientific or software validation.

A bounded, read-only credential-pattern inspection was performed before public push and found no match for the selected high-confidence GitHub, OpenAI, AWS, or private-key-header patterns. It is not a comprehensive secret audit and does not change the no-test or scientific claim boundary.

## Staging and blast radius

The exact intended Git paths are:

- the 71-file candidate stage named above;
- `external_audit/ode_four_loop_20260823/`.

They are staged with `git add -f -- <exact paths>` to satisfy the user's forced-upload instruction. Nothing from the original checkout's protected bundles, the wrong-root `rec_bianchi` files, or unrelated worktrees is included.

## Rollback and recovery

No rollback is executed as part of shipping. If the audit branch must later be withdrawn, an authorized operator can delete only the remote audit ref:

`git push origin --delete audit/ode-four-loop-external-20260823`

The commit remains recoverable locally and through Git reflogs until normal expiry. This packet does not authorize reverting, resetting, deleting files, modifying the base branch, or rewriting remote history.

Deleting a public branch is not a confidentiality rollback: Git objects, forks, clones, and caches can retain already published content. If a credential is discovered later, revoke it immediately and use the host's sensitive-data-removal process. The audit records intentionally retain absolute provenance paths, including the local account path, because the user requested detailed external-audit run data.

## Residual checkpoint

No PR, merge, tag, release, deployment, branch-protection change, or scientific promotion is performed. External auditors must treat this branch as an evidence snapshot with disclosed missing historical artifacts and retained blockers.
