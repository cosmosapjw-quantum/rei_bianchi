# R9 NCP recovery handoff — 2026-10-16 KST

The remote-command connector's monthly quota prevents further commands from this session. This package makes the next authorized recovery executable in local Codex and on the existing NCP host.

- [Complete portable archive, 43,601,197 bytes / 755 files](https://drive.google.com/file/d/1a9SxVdcJBup_zrgbcNmlIyxOXx6joW5J/view)
- [Standalone Korean Codex handoff prompt](https://drive.google.com/file/d/1S5UX6tLnvr5P-3G_bXhJ9mST0K1FQhEc/view)
- Dropbox destination: `/BASS_DERIVATION_DOSSIERS_20260912/REI_R9_NCP_HANDOFF_20261016.tar.gz`.

The archive contains the entire verified Unit2 tree (726 files, 77 NPZ, all 83 solver receipts, sources, contracts, tests, raw inputs, reviews and English PDF/TeX report), plus the new recovery tool, fixtures, acceptance contract, current intake, instructions and independent review. Large raw arrays remain in the backed-up archive; this Git directory holds the compact executable handoff and delivery evidence.

Archive SHA256: `1247d0be653afd72099773d640a51b7ebbbfb4ed49c0e7855f13e1ecc6dbcdf1`.

Drive and Dropbox upload acknowledgements and object sizes are recorded in `HANDOFF_DELIVERY.json`. Uploaded Dropbox archive and prompt were downloaded once and byte-compared to the local originals. Drive byte-level readback was not performed; its successful upload and metadata size are verified.

## First action

Give the complete `CODEX_HANDOFF_KO.md` to local Codex in the existing checkout. Transfer and extract the full archive in a new NCP staging directory. Use `handoff/recover_c10.py inspect`, then `collect`, with the existing NCP Python environment. See `README_RUN_NCP_KO.md` and `handoff/README_COMMANDS.md` for exact commands. Fixture paths assume the extracted archive root; in another layout set `C10_PAYLOAD` to the restored `unit2/ncp_results` subtree.

The old conditional collector ended at 15:24:03 UTC because Unit2 publication had not finished; Unit2 publication completed at 15:48 UTC. This does not establish FCI failure. The actual current aug-TZ Li/Be three-electron run is **unknown** until NCP inspection. Do not replay it as the first action.

## Verification and scope

The implementation has 17 passing local fixture tests, a passing final-layout run, and independent review `PASS_FOR_PACKAGING_AND_NCP_INSPECT_COLLECT`. These are recovery-tool checks, not actual NCP execution or scientific convergence. The tool only inspects and collects. It preserves failed and conflicting attempts and does not start or stop solvers.

All eight full physical programmes remain open. This handoff preserves the finite-model results and directs one concrete next calculation after actual recovery. The independent PR150 campaign is left untouched. No merge or production activation is part of this unit.
