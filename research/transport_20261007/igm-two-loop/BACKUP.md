# Publication and dual backup

PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/85

Target: `forward/rem-hhe-igm-20261006`. Scientific core commit: `35205180383747291c49e3bab3ae9792769476de`; 222 exact Git blobs verified, zero production source edits.

- Drive folder: https://drive.google.com/drive/folders/1tp_2Z4D-uC2JvJfF_dXNGBItQk6Mo3ho
- Drive archive: https://drive.google.com/file/d/1VXCW1AsUdgIpK5570T1PTIsQY8U5LtN8/view
- Dropbox archive: `/BASS_DERIVATION_DOSSIERS_20260912/IGM_TWO_LOOP_PR85_20261007/IGM_TWO_LOOP_PR85_20261007.zip`, file ID `id:BSpOijBcT10AAAAAADzv2w`.
- ZIP bytes: 993937. SHA256: `95195fa7af4317f5ebfd5be1a2689c6403112cad59b35b1df28069f66f3ae1a3`.

The local ZIP passed CRC and every payload SHA256. Both cloud copies have successful write acknowledgements and verified metadata identity/name/size (R1). No cloud redownload or restore test is claimed. `DELIVERY_RECEIPT.json` is stored separately after the immutable scientific-core ZIP and supersedes its pre-upload pending marker.

Repository CI on the scientific core fails at the unchanged `rust/rei_microphysics` formatting gate (12 paths); its cargo-test step is skipped. The new research crate's local 32 tests and all numerical oracles passed. `CI_STATUS.json` provides the exact run and paths. This PR is reviewable but is not a green-CI production merge certificate.

Only new folders and files were created. To undo the backup, the recorded copies can be deleted after an explicit deletion request; no previous backup was replaced.
