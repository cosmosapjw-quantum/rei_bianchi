# BASS_HE PR125 | Rice 2000 absolute source and double-backup readback receipt

## Git authority

- Draft PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/125
- Branch: `research/he-dd-rice2000-absolute-measured-source-20261030`
- Immutable parent PR124 HEAD: `9696297205c2560bd8bdfc8d72b8b80b86fae8d3`
- PRE-RECEIPT PR125 HEAD: `58e98242553b819ee4c9c13f23f1a0b164671f42`. Final HEAD must be read from Git after this receipt is published.
- 39 source/data/code/note/stage paths and blobs matched locally expected Git blob SHA **39/39** before ledger publication.
- 20 stage commits, and 20 individual Library stage files have successful ACK; `STAGE_LEDGER.json` includes exact SHA and Library file reference for each R01–R10/C01–C10.
- No merge, no force push, no modification to parents PR124 and main.

## Restorable backups: verify byte SHA, not only provider ACK

1. Source-typed code-and-measurement ZIP `BASS_HE_PR125_RICE2000_CODE_AND_MEASUREMENTS_20261030.zip`, 157724 bytes, SHA256 `21982f5b73d325fddd44743b0438568fafe4c50fe216086436163cfb9458a380`. Google Drive file ID `1CcxXFVQ1clklY-NURD9WqekbSz0xyiEw`. Library file ID `file_00000000ba5881fab002e546a688a86a`. BOTH FULL BINARY READBACK and `cmp`: PASS.
2. Private user-input full source-inclusive ZIP `BASS_HE_PR125_RICE2000_FULL_PRIVATE_SOURCES_20261030.zip`, 8048034 bytes, SHA256 `1056a0c4e51f8e009497aada1d3369b8298083bae979159417d2d96eb1d78e1f`. Google Drive file ID `1hYZHp_vayedabgp24z_iD4kIKy_vnPY4`. Library file ID `file_000000004bb481fa8b721972992b4587`. BOTH FULL BINARY READBACK and `cmp`: PASS.

Google Drive folder `/Google Drive/BASS_HE_PR125_RICE_ABSOLUTE_20261030/`, Library folder `/BASS_HE_PR125_RICE_ABSOLUTE_20261030/`. Dropbox FULL BINARY upload/readback NOT_RUN. The private second ZIP includes ALL seven user-provided source files (six PDFs plus EXFOR request ZIP), plus PR124 immutable parent ZIP whose SHA was independently checked. They are not in public Git.

Archive checks: code ZIP 45 members, 44 payload SHA PASS, CRC PASS; private ZIP 53 members, 52 payload SHA PASS, CRC PASS. Final private ZIP restored fresh from Google Drive and executed `bash REPRODUCE.sh`: Python 28/28 PASS, compileall PASS, source JSON/CSV regeneration byte match; `python3 src/verify_pdfs.py --pdf-dir original_uploads`: Rice published 12/12 tokens plus thesis preliminary 6/6 PASS.

## Scientific status

- Rice et al. 2000 primary Table I ABSOLUTE angular measured rows 12, original campaign 1; scoped blocker CLOSED.
- Table II 8 alternative Legendre fits typed, NOT 8 original experiments. One author-internal Table II P2 unconstrained source discrepancy held.
- Rice 1998 Table5.1 six earlier same-experiment values differ from journal and must not be pooled. Attached thesis 139-page file incomplete.
- Experimental covariance beyond author aggregate systematic 7.1% / 13% NOT SOURCE OWNED.
- `Central 28/88`, `HE physical 14/18`, new Rice micro-DAG `3/3`; canonical physical delta 0.
- `kappa=null`, `R_event=null`, `heat_rate=null`, `L4=false`, `production=HOLD`.
- Native different-author R06/C09 NOT_RUN. Same-author adversarial source review PERFORMED, discrepancies preserved, no independent peer-review certification.
