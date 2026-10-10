# PR98 targeted integration review

Date: 2026-10-10 UTC

Source: PR98 head `c168e578354c2f1e191a7064ffa31bd762d2a949`

Integrated as sibling merge: `242313d49c35ee70a0759169126b79c69ef5bf30`

Verdict: **CAUTION — component integration `SCOPED_PASS`; future solver execution `BLOCKED`**

## Findings

1. **Execution provenance is not prelaunch-bound.** `source_bound_interval.py` accepts an arbitrary `--binary`, while the Rust `BIND` exchange compares caller-supplied identity strings. Source and executable hashes are recorded after integration, so a protocol-compatible stale executable can be mislabeled as source-bound. Before any new interval, require the exact clean commit/tree, Cargo inputs, toolchain and build command in an immutable receipt; compare current source and binary hashes to that receipt before subprocess launch; and add a stale-binary negative component test.
2. **The recovery archive resolves raw-output availability, not build/run identity.** The reported JSON/NPZ were recovered from `/tmp/rei-p01-final-nrAQew/output` and match PR98's reported hashes exactly. A parent worker independently inspected the 3,288,066-byte Dropbox archive `REI_PHYSINPUT_P01_PRODUCTION_20261010_c168e578.tar.gz` at provider ID `BSpOijBcT10AAAAAAD3sHQ`, SHA-256 `9a82f25e...`, and verified both payloads. The archive lacks the actual production binary, P01 clean-build transcript, and P01 command/stdout/stderr receipt, so these bytes remain producer evidence rather than independent execution certification.
3. **Original PR98 changed sealed PR96 evidence and overclaimed P01 completion.** At `c168e578...`, `RESEARCH_DAG.json` SHA-256 `7a6ecb...` differs from manifest value `012f742...` and marks P01 complete; `p01/REPORT_KO.md` claims a source-preflighted production execution that the available build/run evidence does not establish. The integration branch restores the sealed DAG byte-for-byte to `012f742...` and P01 `ready`, giving current-tree 87/87. The original PR98 commit/report remain preserved in Git and are explicitly not accepted as execution certification.

## Evidence and non-findings

- Static time/state/unit/sign tracing found no obvious arithmetic blocker for the frozen warm H/He IVP.
- `PhysicalHistory` remains fail-closed; CR/RCT/HH remain OFF.
- Post-merge component checks passed without a new solver run: Rust conditional 8, Python boundary 5, contract/coupling 6+5, PR95 adapter 4.
- PR94's positive-energy/zero-temperature guard and PR95's current-field closure guard remain present in the sibling integration.
- This review does not admit cold primordial IGM, low-energy CR deposition, a long physical history, or a production run.

The machine gate is `P01_EXECUTION_GATE.json`; the recovered-byte receipt is `evidence/P01_RAW_EVIDENCE_RECEIPT.json`.
