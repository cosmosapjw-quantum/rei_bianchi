# Unit4 delivery

The complete 65-file package, including the 9.13 MB actual saved-state NPZ and frozen V6 source, is backed up to both providers.

- Full package: https://drive.google.com/file/d/1h8b044Pia3JfM_tvL4IMTKeNN4YnrXGt/view
- Standalone NCP Codex prompt: https://drive.google.com/file/d/1TDGGpaHDbVrNpKAOeLMLJiQnrm5U1Exj/view
- Dropbox archive: `/BASS_DERIVATION_DOSSIERS_20260912/REI_R9_UNIT4_T4_SPECTRAL_20261016.tar.gz`, file ID `id:BSpOijBcT10AAAAAAD9EyA`.
- Archive SHA256: `91977313e1004be22a540b1fd2b874ded4d437301b1f61e9ff54d59cbbda275b` (9,219,469 bytes).

Dropbox archive and prompt were downloaded and byte-compared to local originals; provider content hashes match. Drive acknowledged both uploads and returned matching metadata sizes. Drive byte-level readback was not performed.

The archive manifest/SHA256SUMS describe the full downloadable package. The Git copy deliberately omits `inputs/data.npz`; download the archive before execution. Publication metadata in ARCHIVE_IDENTITY.json, BACKUP_PROVIDERS.json and BACKUP_VERIFICATION.json was added after packaging.

Unit3 finite-model recovery passed. New Unit4 scalar calculations and 9 local dense/supervisor tests passed; independent review accepted local implementation and readiness for bounded NCP execution. Actual NCP reconstruction and 92-orbital projected spectrum remain NOT_RUN. Next action: hand NCP_CODEX_HANDOFF_KO.md to local Codex and execute the included runner under its existing PySCF environment.
