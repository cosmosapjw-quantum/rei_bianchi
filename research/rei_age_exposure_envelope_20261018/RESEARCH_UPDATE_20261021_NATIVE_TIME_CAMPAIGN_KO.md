# Native BE time8·16·32 NCP campaign — 2026-10-21

## 실행과 provenance

V10에서 남아 있던 native BE `time8`, `time16`, `time32`를 각 한 번 실행했다. 완료된 age32·age64·spectral128·v7 benchmark·v8 fixed-model은 재실행하지 않았다. 세 case 모두 exit 0, 원 `validate_outputs` PASS이며, 자동 retry 0·새 결과 재사용 0·현재 실패 0이다. 분석은 유효한 세 새 attempt만 썼다. 과거 time 실패 네 건은 source/binary가 달라 reuse 부적격이므로 원 raw와 함께 기록하고 child-wall debit 48.08575484400353 s를 유지했다.

- Source commit `4f13648985e417028c530892ea02be4f56018a31`; v10 final task tree `cc0046a197bf4f28c0df728296ee9de983c045de` (2397 files).
- Frozen original native153 `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`; computational base `78386db7ac2e35488ab610c4a3ddb1d87f8b51bbe25d855bf417dc17dd07d620`.
- New prepared identity `ca09947a4a460d3643430547688da8f7c8e0d8bd2e7f4b79e66d3fd0bc17cb1c`; new native BE binary SHA256 `2d5d95371df4c4cf882a4563edc4becdf965c76fdbbf9b9dfaa97fe083fd57fd`. This is distinct from positive B1 reference binary SHA256 `89c646db1de80c6e85fe34f7c3eaae2f10904810a8a6c3acc3426a7e7c1dd7a4`.
- Host `s1a0e5abed09`, affinity 0–63, 64 CPUs, cgroup CPU/memory limits unlimited, preflight available memory 131,366,031,360 bytes. No matching age native campaign jobs were present before launch; unrelated jobs were left intact.
- Existing Python 3.12.3 / NumPy 2.3.5 / SciPy 1.17.0 venv and Rust/Cargo 1.99.0 offline cache were used. Build exit 0 in 12.7937 s. Run plan jobs3 × workers20 + 3 main lanes = 63 slots, per-case address-space cap 24 GiB, reserve 16 GiB; BLAS/OMP=1. The same planned allocation was used for execution.
- ``time8`: 22.0025 s (968 native steps); `time16`: 43.1565 s (1,936 steps); `time32`: 80.1614 s (3,872 steps). Aggregate new child wall 145.3204 s; with four historical attempts 193.4062 s, under the frozen 5400 s aggregate cap. Campaign elapsed including historical debit: 128.4273/2000 s.

The accepted-step trace is complete for each case (15,488 / 30,976 / 61,952 rows); no zero-node rows and no rounded-after-outside-kernel-sum rows. The subnormal-barycenter repair totals are 5,724 / 22,076 / 99,626, with maximum repaired masses 1.43166177492782e-309 / 2.137630883034545e-309 / 2.117284223644764e-309. The saved age32 input is the hash-verified positive DOP853 reference; it was not rerun.

## 수치 분석과 판정

원 finite-neighbor threshold 0.005는 유지했다. 각 쌍의 relative N/U differences는 다음과 같고 모두 target을 넘는다.

| 비교 | N | U | 0.005 target |
|---|---:|---:|---|
| time8 ↔ time16 | 0.3217324692 | 0.2736494289 | FAIL |
| time16 ↔ time32 | 0.1491153641 | 0.1288608016 | FAIL |
| time8 ↔ stored age32 | 0.7447440510 | 0.6231817042 | FAIL |
| time16 ↔ stored age32 | 0.3200432702 | 0.2744336608 | FAIL |
| time32 ↔ stored age32 | 0.1487473856 | 0.1289555444 | FAIL |

Age32 uses positive DOP853 and these time runs use native backward Euler; comparisons to age32 are cross-operator finite differences. They do not establish native convergence. The execution gate is complete, but `native_age_time_convergence=HOLD`, `nonlinear_Grackle_response_bound=NOT_ESTABLISHED`, and `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED` remain. An exit-0 campaign, stored-denominator discrete BE observer, and backup readback do not change these conclusions.

## 반환 파일과 검증 범위

`evidence/ncp_time_campaign_20261021/` contains the NCP return bundle, NCP package receipt, copied campaign/host/resource/run receipts, exact attempt stdout/stderr/receipts/identities/raw outputs, BE trace analysis and hashes. Bundle bytes 97,904,010; SHA256 `3f8a8214d0c1909e70d2804ae606280295cda95db1a9541597900df1327d38c2`; 692 tar members. A first SCP copy was truncated (SHA mismatch and tar EOF), preserved outside the task package as transfer-failure evidence; a second complete transfer matched the NCP whole-file hash and all 692 members extracted successfully.

The campaign itself reported `PASS_EXECUTION_AND_ORIGINAL_OUTPUT_VALIDATION`; this is a scoped execution result. Packaging note: the embedded `EVIDENCE_FILE_MANIFEST.json` contains a pre-final `CAMPAIGN_RECEIPT.json` hash (4f3305e6aa7a730b7598b17a67bd19ed908b8d3874a094a06244692f7fa57e9c; 44,908 bytes), while the final receipt is 45,101 bytes with SHA256 `d7ed2beb165aca6e44ad3c203ed75b7705a631748a15549535d4850b9ed352a5`, bound by the outer NCP package receipt. The final receipt embeds the manifest SHA. This generated-evidence packaging mismatch is disclosed; it does not affect the raw output hashes, case validation, analysis identity, or scientific result. The exact outer receipt and embedded manifest are both preserved. The historical root `cargo fmt` failure and skipped workspace tests in the previous full CI remain separate from scoped task checks; the PR199 HEAD `349aeef40bc27fe922d1e3afe77ae6747a408c6a` CI runs 39522976092 and 39522970156 both fail at root workspace `cargo fmt --check`; workspace tests are skipped. This is recorded separately from the scoped campaign PASS. Fresh independent Astra-tier read-only review returned `PASS_SCOPED_FACTUAL_PUBLICATION` for publishing the factual report and DAG (review artifact: `native_optimization_20261021/evidence/ncp_time_campaign_20261021/INDEPENDENT_REVIEW.json`). This does not grant scientific admission; convergence HOLD remains. No scientific admission is requested here.

## 게시와 이중 백업 확인

결과·DAG commit `349aeef40bc27fe922d1e3afe77ae6747a408c6a`는 PR199 branch의 `652a7e03b844a145d6c6cbb401ab81f4a8429aff`를 부모로 한 일반 fast-forward다. PR199는 open/draft다. Backup archive는 97,636,165 bytes, SHA256 `3fde54fdfbdccc3cb0e6991209fe156f3535f44e6c0ad0f1582ea9adbb999c06`; Drive ID `1IdjtDx9AkbGmBVNRhRZtmHirphSfW3VF`, Dropbox ID `id:BSpOijBcT10AAAAAAD_cRw`로 저장했다. 두 provider에서 전체 GET readback bytes와 SHA256가 모두 일치한다. ACK는 `evidence/ncp_time_campaign_20261021/BACKUP_READBACK_ACK.json`이다.

최종 최신 결과/DAG 패키지 `REI_AGE_NATIVE_TIME_CAMPAIGN_20261021_v10_FINAL.tar.gz`는 97,637,067 bytes, SHA256 `f57a019786f7cb2afba205040fe400fbc97f43a0783e03572f080214fa61224b`이다. Drive ID `1E24n-kw72nR_9qnvfNHiU3AMasBHDdQp`와 Dropbox ID `id:BSpOijBcT10AAAAAAD_cWA`에서 두 전체 GET readback이 같은 크기와 SHA로 PASS했다. 영수증은 `evidence/ncp_time_campaign_20261021/FINAL_PACKAGE_READBACK.json`이다.
