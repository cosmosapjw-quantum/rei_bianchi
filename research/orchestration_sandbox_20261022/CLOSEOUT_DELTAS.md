# Post-window closeout deltas

These observations occurred after the fixed intake cutoff and are not counted as initial-window results.

## rec_bianchi

# X1 REC closeout delta — 2026-10-22 07:10 UTC

Read-only refresh; zero ODEs, zero postprocessor reruns. Existing REC1 source/publication map was not changed.

**PR121** is the already adopted thermal-moments source, now formally published: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/121 . HEAD892aad5c3e9fb0b2abd021154b62a42c39277125, branch research/rec-thermal-moments-20261022, tree503fa14793f385a1e235763818251c5d34987842. Its eight full63 histories are already counted. Published provenance/REC_THERMAL_PUBLICATION_DROPBOX_20261022.json records full-GET size/SHA256/Dropbox-content-hash PASS for the38621529B release and its integrity/restore-audit sidecars. This supersedes the old local delivery-blocked snapshot and our earlier metadata-only observation; no repeat download was made here.

**PR122** adds a broader omitted-process budget: https://github.com/cosmosapjw-quantum/rec_bianchi/pull/122 . Live HEAD11897e09ea9368460ed074c0233afb924f39a7bf, branch research/rec-thermal-omitted-budget-20261022, tree022e31f6b7b0618fbd35c296850a8615ec9ce675. Runtime identity88edf8e7e5ccff94509e03ff2979b3b93e5e988641c5dbd4a5d64f4583bca02c. Actual results/budget_v1/RESULT.json is COMPLETE, finished03:27:15Z, newODE0/oldreruns0; DAG confirms872savedstates and0.676866s postprocessing. It includes actual-photon-monopole hot Compton, an independently specified Planck reference, diluteUV Compton, HG97 H/He collisional ionization and HI/HeII excitation with source-domain/missing-channel masks.

**Relationship to our PR123 REC1:** the Planck-reference component overlaps exactly in scientific scope. Read-only reconciliation of all eight existing ENERGY_BUDGETS.csv simpson_109 entries against REC1 RESULT.json gives maximum absolute difference1.7763568394002505e-15eV/baryon. PR122's main table uses trapezoid109; compare matching quadratures. Preserve REC1 as an independently implemented C kernel plus frozen-step identity and matching reference-field budget. Do not count another eight physical trajectories or present the overlapping scalar result as an additional independent physical prediction. PR122 is the broader source-budget/future-contract anchor.

PR122's actual-U hot term is scientifically distinct from the Planck reference: primary-path cooling2.576–2.592eV/baryon,29.72–29.92% of retained photoheat; HI excitation about−0.00132eV/baryon, CI kinetic→binding about2.05e-5, UV Compton about+6.23e-5. Full actual-CMB recoil/induced closure remains spectrum-dependent. Its independent raw recomputation and65implementation checks are source receipts, not new tests run by this refresh.

**No new coupled Compton run is present.** NEXT_UNIT_CONTRACT.md explicitly says PROPOSED_FINITE_CONTRACT/FUTURE_ODE_NOT_RUN; DAG future_compton_full63 is PROPOSED_NOT_RUN. Reuse this concrete contract: seeds s03_m03_r03 ands04_m04_r04 × actual_hot/planck_reference × nominal/refined =8newfull63IVPs, initial donor index84,z7.9637328→2. Both branches add the sameUVCompton term; do not sum their two CMB terms. Actual-hot uses current integrated U_gamma, not saved-path replay. Preserve full63 Jacobian couplings, exactzero n/T, Mao-factor RR, old baselines and test-fluid gas/bath ownership. Opposite exchange is ledgered but not dynamically fed into the photon/Einstein sector. Persist109comparisonstates and actual513/1025diagnostic arrays. Serial one-thread limits240s/case,1200s/campaign; same-branch refinements and retained-energy gates fixed by the contract. No automatic CI/CE activation.

Future orchestration: deduplicate this proposed8 against any fresh actual run before submitting; align its radiation ownership/ICs with the separate REI C22B lane rather than counting those as identical campaigns. Source-bound CI/CE diagnostics are already available inPR122, so the former plan to implement them from scratch should be replaced with adapter/reuse on new states. HeI excitation/metastables,Li CI/CE and the actual spectral recoil/induced closure remain explicit obligations.

PR122 final combined archive/delivery supplement was still described as being finalized in its actual live body; its frozen DELIVERY_STATUS is prepublication, and current comments list is empty. StageA/B and prior thermal-release whole-byte evidence are published. Do not infer final-combined backup success from these predecessors. All physicalHOLD/globalconvergenceNOT_RUN/productionNOT_APPROVED/REI_activation=false and historical closed budgets remain.


## rei_bianchi

# REI closeout delta: C2 delivery and concurrent C3 coordination

Read-only refresh after the original48-hour intake and the local C3 publication. No scientific code, diagnostic, solver or NCP command was run during this refresh.

## Current exact identities

| Item | Observed identity | Interpretation |
|---|---|---|
| PR221 current HEAD |42e44494bd0956756d8c610e75da5b1cafe20d3c|2026-10-22T06:55:29Z commit; delivery metadata |
| PR221 current root tree |f87f1fd71c87b41bbfa4c9f7d4525788f130b37f|new delivery subtree |
| Preserved C2 scientific commit |c1714f82ea7de15fee230a1a995365970ee6dc02|unchanged C2 code/input/results |
| Preserved C2 scientific root tree |dd1ce4d9870c86e30823e15ecf6a05436a811367|actual214-check science |
| PR222 orchestration HEAD |20539a00d3fb5dcdb4165b1c90b4d5d5d1f8ebb3|includes our C3 finite representation probe |

The Git compare c1714f82...42e44494 shows exactly one new commit and four added paths, all below research/rei_coupled_isotope_mapping_20261022/delivery/: BACKUP_READBACK.json, FINAL_DELIVERY_ACK.json, README.md and RESTORATION_RECEIPT.json. No existing file was modified or removed. Therefore the source/input/evidence bytes used by our frozen C3 baseline remain unchanged. This is an exact source-preservation result, not an inferred numerical equivalence and not a new214-check execution.

## Backup assurance updated

The newly published delivery receipts establish producer-side full-body Drive and Dropbox readbacks for the C2 archive:

- File: REI_COUPLED_ISOTOPE_C2_20261022_7fa873d9c276.zip.
-135,421bytes;40members; SHA2567fa873d9c276f6f12ff4a4e32e7f83314da678e24d26741761230bf08b4ec36d.
- Drive1lVhz8Zl6kyzDV3IftjJjYnqUXT4_WuA_; Dropboxid:BSpOijBcT10AAAAAAD_h4Q.
- Both producer remote copies matched SHA256/size/member count and passed ZIP CRC. The receipt also preserves a39-file byte-identical local restoration without scientific reruns.

This supersedes our earlier metadata-only observation for this C2 archive. We read the published producer receipts; we did not repeat those downloads. The compact archive does not contain all historical nuclear arrays or outer-source references needed to replay all214 checks. Its assurance must not be transferred to the distinct20,634,190-byte bootstrap/provider archive, whose own receipt still says no new full remote download.

## Actual workflow status

Both workflows at exact delivery HEAD42e44494 are completed/failure:

| Event | Run | Job | Observed steps |
|---|---:|---:|---|
| pull_request |39737034930|119685035037|cargo fmt --check failed; workspace cargo test skipped |
| push |39737029515|119685017114|cargo fmt --check failed; workspace cargo test skipped |

The failed command is cargo fmt --manifest-path rust/rei_microphysics/Cargo.toml --all -- --check. The skipped command is cargo test --manifest-path rust/rei_microphysics/Cargo.toml --workspace --locked. This independently confirms the reported fmt failure/test skip. The metadata-only delta contains no Rust change. Source-preservation booleans and scoped scientific PASS do not mean full repository CI is green; conversely these formatter failures are not failed C2 physical assertions or executed failed Rust tests.

## C3 work already available; avoid another equivalent run

Our completed conditional representation probe is actually published at PR22220539a00 in research/rei_c3_zero_tiny_source_20261022/. Its current RESULT_SUMMARY.json and directory listing were read back:

- Seven finite fixtures, nine applicability controls and five additional controls pass.
-8rate,147scaled-source,3087scaled-Jacobian and42central-difference comparisons pass.
- Actual local execution receipt: one invocation, exit0, wall0.100463153s, CPU0.094889168s, maxRSS19,968KiB.
- local_source.py SHA256e6818290a2f50f4e6872eff861f1aec1c461c21539751dbc4763496461549a79.
- run_probe.py SHA256e52bca4f756e4b00fdab3ae385beb2b918c0a96576b594b589d9a0e803e1433d.
- Result scope remains manufactured local representation, including exact-zero/tiny-stock/underflow/scaled-Jacobian and17→21baryon projection. It does not complete full C3 numerical design or coupled physical production.

Root's central conversation refresh reports another same-owner thread starting C3 around07:03Z. That is a concurrency signal, **not a recovered result**. At this read, PR221 still contains C2 and its delivery only; no newC3 result was found in the relevant current Git research directory or exact REI_COUPLED_ISOTOPE_C3 Drive/Dropbox title searches. These bounded searches cannot establish that private/local work does not exist.

The next thread should first retrieve the other thread's current source/contract/result receipt, if it has since been published, and compare its scientific identity with PR222's completed probe. Reuse our finished fixtures rather than rerunning them. Integrate a genuinely complementary C3 deliverable—off-grid coefficient policy, actual event assembly or thermal/fast Jacobian dependence—only after identifying the remaining difference. Do not treat PR221's historical C3_READY text as evidence that no C3 work has started. Keep D10 zero-initial matter stress as a separate ready theory/saved-data node.

## Direct source pointers

- [Exact metadata delta](https://github.com/cosmosapjw-quantum/rei_bianchi/compare/c1714f82ea7de15fee230a1a995365970ee6dc02...42e44494bd0956756d8c610e75da5b1cafe20d3c)
- [C2 final receipt](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/42e44494bd0956756d8c610e75da5b1cafe20d3c/research/rei_coupled_isotope_mapping_20261022/delivery/FINAL_DELIVERY_ACK.json)
- [C3 completed probe](https://github.com/cosmosapjw-quantum/rei_bianchi/tree/20539a00d3fb5dcdb4165b1c90b4d5d5d1f8ebb3/research/rei_c3_zero_tiny_source_20261022)
- [PR CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39737034930)
- [Push CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/39737029515)


## vigilode

# Closeout delta: VigilODE NCP C1, 2026-10-22

At the parent X1 refresh around07:10UTC, research/bassrei-port-20261021 advanced from2064366ea39ef35a9eae7966b4b5b2424a46124c to7647d545d79ed8723331194a36c68e6adf4d80f7 (commit07:00:47UTC; tree d78b234293c0ff92121a5fd48f537f5f85f4998a).

The new commit imports actual attempt2 results and Julia installation evidence. Its latest HANDOFF progress paragraph supersedes the earlier paragraphs saying attempt2running/attempt3notlaunched.

| Item | Latest directly read result |
|---|---|
| NCP C1 attempt2 | **PASS**,1034s; actual execution source e3341309e42954fd946bce53a6a7be9c69a0d165. Imported results.json and REPORT.md agree on G1–G7 alltrue. |
| Coverage |1212planned/1212typed rows:720OK,424HOLD,66NOT_APPLICABLE,2TIMEOUT; no missing/untyped rows and no VigilODE/reference cutoff. This is not1212successfulnumericalruns.|
| Julia in attempt2 | **HOLD** from missing temporary depot; this remains part of the attempt2 scope.|
| Julia installation |Reported JULIA_INSTALL_OK1.12.7,exit0;06:45:37–06:59:00UTC; private persistent depot1.5GB. Project/Manifest hashes are committed.|
| NCP C1 attempt3 |**Launched07:00:04UTC** from2064366ea39ef35a9eae7966b4b5b2424a46124c with new depot found. Still inprogress in this commit; no result imported yet.|
| Timing meaning |Budget-matched rungs and ABBA ratios remain diagnostic_only; loose-edge censoring is explicit. No general speed promotion.|
| Final ledger/DAG |HANDOFF states attempt2ledger row remains tobeappended, and final DAG/results are to follow bothattempts. Keep production HOLD.|

The imported attempt2 tarball SHA256 is9aa4033bf04879fadff2011d2f15175f15964178e9269cc2d5b44f996e35f032. It is read from IMPORT_MANIFEST.json; this delta did not redownload/hash the tarball or rerun a calculation.

Read-only sources at immutable commit7647d545d79ed8723331194a36c68e6adf4d80f7:

- research/bassrei_ncp_wp_c1_20261022/attempt2/results.json
- research/bassrei_ncp_wp_c1_20261022/attempt2/campaign/REPORT.md
- research/bassrei_ncp_wp_c1_20261022/attempt2/IMPORT_MANIFEST.json
- research/bassrei_ncp_wp_c1_20261022/handoff/HANDOFF.md
- research/bassrei_ncp_wp_c1_20261022/julia_install/INSTALL_START_UTC.txt
- research/bassrei_ncp_wp_c1_20261022/julia_install/INSTALL_END_UTC.txt
- research/bassrei_ncp_wp_c1_20261022/julia_install/ENV_SHA256SUMS.txt

This late update is separate from the immutable intake window ending06:42:09UTC. It does not alter this orchestration's already published norm-kernel package or its test receipts. No NCP process was started, polled, stopped or changed by this lane. Our independentVigilODE PR79 remains separate from the active port branch. BASShead574c3af93810122af0a7977e00e34195e5251a09 remains unchanged according to the parent X1 refresh.

