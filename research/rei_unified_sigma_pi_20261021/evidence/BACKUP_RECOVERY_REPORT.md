# D0/D1 backup and interrupted-work recovery

Observed 2026-10-21, Asia/Seoul. This workstream performed read-only provider discovery, complete archive retrieval, byte verification, immutable local copying, and raw structure/identity checks. Scientific ODE executions: **0**. Existing reviews were recovered, not reopened.

## Lane A: PR198

Both Drive object `1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7` and Dropbox object `id:BSpOijBcT10AAAAAAD_fYA` returned the complete final archive, 37,945,383 bytes, SHA256 `2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d`.

Both final ACK objects returned 6,006 bytes, SHA256 `568972bdc59c5f5aa45c9871fba1046562cc8ce3397bb5e78f6d36409d4dee1a`. Drive ACK object: `1TiStfVpIT2CiivFZfxNrVlq_kEyq6dpI`; Dropbox ACK: `id:BSpOijBcT10AAAAAAD_fcw`.

The archive contains 5,747 payload files and its manifest. Every member size and SHA256 matched; membership is exact. Manifest SHA256 is `3907bc7a228642443178af706e925aedf0e0b0c5e71843569befec552a6586d6`.

Actual files establish 625 original completed cases, 40,625 samples, and 606 component completed cases, 39,390 samples. Every trajectory stores 8 states and 65 samples, zbar 20 to 4. Executed parent file hashes match the recovered archived files. The component executable has SHA256 `e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e`. Completion receipts and source identity are distinct from the recovered scoped scientific reviews.

Recovered source/raw root: `pr198_extracted/repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021/`.

## Lane B: 91+3 original; 175 extension

The remote contract archive `REI_SIGMA_PI_PILOT_20261021_CONTRACT_cbe27ad9a13d.tar.gz`, Dropbox `id:BSpOijBcT10AAAAAAD_fVQ`, was recovered in full: 15,239 bytes, SHA256 `cbe27ad9a13d3ef2aed7a89f631685e69e16600c64c9199394083ccc3a05a028`. Its six documents contain design/intake/review, not completed numerical data. The contract review identifies original working path `/workspace/scratch/3fac997d7514/pilot_20261021`.

A current-turn filesystem probe found that exact previous working path still readable. Its package, reviews, delivery, current handoff, publication staging, and top-level research documents were copied into `laneB_recovered/`. All 576 copied files, 11,832,521 bytes, were hashed before and after copying; none changed during capture. No original file was modified.

**Original pilot: COMPLETE_WITH_VERIFIED_RAW.** The staged `RAW_RESULTS.tar.gz` is 4,494,862 bytes, SHA256 `4699dfe6f559ae4011b7ccfed1936ac35e80163cd54f6bfd9a9853aabd96d6c9`. All 376 archived raw/input/result/attempt members match the manifest and the corresponding loose files. All 94 case IDs/configurations and completed exit statuses match. There are 91 nominal state arrays of shape 40×121 and 3 refinement arrays of shape 56×121, all zbar 20 to 4. Recovered C9 admission is PASS_SCOPED_PRELIMINARY.

The source kernels and cosmology lock are pinned to PR147 commit `3b85dedce84d37b3e165da00685a8a984950aafe` and byte-identical to their Lane A counterparts. Actual executed wrappers were unpublished, but their bytes are preserved in `package/verification/executed_source/` and match the execution manifest. They must not be relabeled as the later repaired wrappers or as code executed at PR199's historical HEAD.

Actual original stored normalization is Frobenius. The raw relation Sigma_F=sqrt(6)|s|/H differs only by maximum 4.16e-17 in the saved arithmetic. The source and raw data retain gamma, nu, and massive signed stress contributions.

**175 extension: PARTIAL_WITH_VERIFIED_RAW.** Of the nominal 175 physical configurations, exactly 35 with initial matter stress zero have matching existing nominal raw trajectories and preserved original receipts. New component nominal trajectories recovered: **0/140**. New component refinements recovered: **0/3**. The component contract and its PASS_SCOPED_EXECUTION review exist, together with `component_adapter.py`; no component controller, results directory, or final raw/diff review exists in the recovered source. Therefore 140 planned new runs are still unexecuted in the recovered evidence.

Publication staging exists, but its current receipt says PENDING_EXPECTED_HEAD_FF and complete backup AWAITING_ACTUAL_ACK. The unchanged remote PR199 HEAD independently agrees with this pending state. The intended owner path is documented as `research/rei_age_exposure_envelope_20261018/sigma_pi_pilot_20261021/`; this historical plan is separate from the native AGE lane.

The recovered 94 raw cases require durable checkpointing before any extension. Original raw results must be retained; no 91+3 repeat is needed.

## Coverage and limits

Provider discovery enumerated the shared Drive research-backup folder, both relevant Dropbox backup locations, the direct Dropbox research directory, and focused Sigma/Pi pilot filename queries. Known PR198 anchors were fetched from both providers in full. The AGE backup folder has only the 91-case contract under the relevant pilot naming; it is not evidence that the previously run 91 cases were absent, as direct recovery subsequently established them. Search results are bounded and do not prove global absence of every possible renamed archive.

No NCP host was accessed. No other process or owner checkout was changed. Current scientific-state claims are based on recovered files and receipts. Historical notes about runtime restrictions were not used as current capability evidence. Default-network downloads failed with Operation not permitted; authorized read-only downloads succeeded with sandbox escalation. Python's requests package was unavailable; standard-library urllib provided successful download execution.

## Machine-readable evidence

- `provider_metadata/FULL_READBACK_PR198.json`, `READBACK_PR198.json`
- `provider_metadata/PR198_MANIFEST_VERIFICATION.json`, `PR198_RAW_STRUCTURE_CHECK.json`
- `provider_metadata/PR198_625_CASE_RECOVERY.json`, `PR198_606_CASE_RECOVERY.json`
- `provider_metadata/PILOT_CONTRACT_READBACK.json`
- `laneB_recovered/RECOVERY_SNAPSHOT.json`
- `provider_metadata/LANEB_RAW_RECOVERY_VERIFICATION.json`, `LANEB_94_CASE_RECOVERY.json`, `LANEB_35_REUSE_MAP.json`
- `provider_metadata/CROSS_LANE_VENDOR_IDENTITY.json`

Temporary transfer inputs with `.private.json` names contain expiring download URLs and are not publication payload. Account-wide inventory files are discovery evidence and should not be included in a public scientific package without filtering.
