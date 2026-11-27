# NCP local Codex 전용: E11 → E12 native 내부장부·관측기 source 식별 및 검증

ROLE=SOURCE_PINNED_NCP_HE_OWNER_TELEMETRY_EXECUTOR
NEXT=E12_NCP_NATIVE_INTERNAL_5_AND_STAGE_TRACE_VALIDATION
CURRENT_ADMISSION=SHADOW_CANDIDATE_ONLY

너는 NCP local Codex다. 이 prompt는 채팅환경에서 유도·실행한 E11 저장값 분석과 **컴파일하지 않은 E11 native telemetry 후보**를 구분하여 이어받는 실행 계약이다. 이미 완료된 E10 3×384 native science, E6 5,199-row Endpoint, E7 1,155-row export, E8 photoelectron source, E11 CSV 분석을 이유 없이 재실행하지 않는다. 필요한 것은 **실제 owner State 내부 5필드 직독 + 수락 stage trace의 새로운 증거**다. 사용자 수동 업로드 없이 기존 Git/Drive/Dropbox credential/cache를 먼저 조회한다.

## 0. Authoritative source / intake

- BASS_HE repo `cosmosapjw-quantum/BASS_HE`, branch `research/shared-c64-crossrepo-20260928`. 먼저 실제 live HEAD를 fetch. 구 head로 reset하지 말고 history를 보존한다.
- E10 NCP science receipt Git `857045e0047f29a19fce18bf6d715afd085665c3`; full-shadow 3×384 accepted, original gas/live Gamma parity 50,820 f64 checks. 원 owner receiver commit `39c39eab1cc2f1a215723680accc123e67ef13b6` under `cosmosapjw-quantum/rei_bianchi`, branch `forward/rem-hhe-igm-20261006`. 이 branch는 owner-reserved: 무단 push/merge/force 금지.
- E10 NCP runtime ZIP `BASS_HE_E10_NCP_RUNTIME_20261008T155514Z_f9217156bb5e.zip`, bytes=2528362, SHA256 `d2cec9451719d534b78bdd6ebd7570e03697e9fdd69696c24a966c1a25c91598`, Drive ID `1ZsLe1LlC_hHNOUbhXug1llUZsLzt4mHS`, Dropbox id `id:BSpOijBcT10AAAAAAD3izA`.
- E7 source data `BASS_HE_RCT03E7_CONSUMER_ADOPTION_20261008_v1.zip`, SHA256 `020a58ebc4c57a89d973fde66fd1cd82cd5bc3e3f3bccf9f8dce8856cb8bfe2a`, Drive ID `1pCLtxukkwzMsEutFFj8UBngWHRvYHPI6`, already nested in E10 runtime `inputs/E7_ORIGINAL_020a58ebc4c5.zip`; do not redownload if local hash verified.
- E11 new immutable ZIP path/sha/payload count in BASS_HE Git `.../HE-E11-OBSERVER-ALIAS_20261009/DELIVERY_RECEIPT.json` (read after publication). It contains exact analyses plus `native_candidate/e11_native_telemetry.rs`, additive `.patch`, Python verifier, original selected data and recorded tests. Download only if not cached. No binary/compiler bundled.
- Cloud roots: Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/`. Metadata both, bytes once, verify SHA/size/CRC/manifest. Restore receipt is object-specific; R1 ACK is not restore verification.
- Recheck `AGENTS.md` and parent NCP/HPC_POLICY_KO.md. Observe actual cgroup quota, cores/NUMA/affinity, disk/memory, toolchain compiler binary SHA, long-lived processes. Dirty files/worktrees must remain intact. New isolated workspace, namespaced `output` and `PROCESS.json.tmp` per mode.

## 1. E11 read-only result to import WITHOUT rerun

Same binary64 3×385 states/clock and E10 original grid liveGamma vs E7 Endpoint: all stored-matched source identity. N24 source/cutoff anchors `k%16=0` (25 per mode) have 3-rate bit equality. Other360 epochs differ. Individual Gamma alias max E7 ratio=3.543295 (OFF HeII step59). Paired photoelectron instantaneous source `P=(1-x)Gamma_HI+fHe*((1-y-z)Gamma_HeI+y Gamma_HeII)` shows max relative live-vs-Endpoint paired signal KF≈0.00684984, GM≈0.00701847 at step24, near signed source reversal24→25. Final step384 paired alias exact0 for selected f64. These numbers are finite stored-data diagnostics; they are not future error bounds, true spectrum, or source equivalence.

E10 photon energy CSV permits only `Bsum≈emitted_E−Eactive−out_E−redshift_E` within stored rounding. From scalar Bsum, 3 individual `BH/BY/BZ` and nonphoto binding/thermal micro cannot be inferred from CSV alone. E7 reference has their saved values, but **not E10 actual owner independent output**. Do not zero-fill or copy E7 into a claimed E10 telemetry measurement.

## 2. Prepare E12 affected native change (TDD / first pilot)

2A. Extract one E10 complete runtime archive to new worktree and verify manifest + archived shadow source SHA. Check exact E10 three-patched owner Git blob identities (coupled/material/radiation). Do not reapply patch to an already patched shadow; do not re-create scientific models. E7 input SHA must match above. Rust 1.94.1; GPG authenticity status independent, not silently PASS.

2B. Add **only** the E11 `native_candidate/e11_native_telemetry.rs` as a new example in `research/transport_20261007/short-hhe-midpoint/examples/`. Old `e10_native_select.rs`, owner `output.rs`, live density/Gamma, source, residual, tolerance and 41-col CSV stay byte-unchanged. The telemetry example preserves `2|384 [--authorized-full]` explicit gate and distinct output directory; emits two extra files:

- `OWNER_INTERNAL_5.csv`: from actual `state.radiation.be[0..2]`, `state.material.nonphoto_binding`, `state.material.nonphoto_thermal`; correct units erg/H; no independent physical atomic heat claim.
- `OWNER_ACCEPTED_STAGES.csv`: actual `state.accepted_trace.stages` source count/temperature min/max and continuity info. Merely trace export, **not independent stage numerical verification**.

2C. **STOP if source is nonidentical or native build fails.** Compile `cargo build --offline --locked --release --example e11_native_telemetry`. Run affected existing 5 Rust E10 tests and only OFF/KF/GM 2-step opt-in examples to NEW dirs. Expect E7 3 rows×5 internal fields and 3×41 old outputs to match saved reference, check exact f64 bits. Run `python -m e11.verify_telemetry` against E7. Stage records for accepted k=1,2 nonempty, finite, evidence captured. Preserve all failures/exit codes. Code was *not compiled in ChatGPT*; initial validation authority is YOUR actual NCP log.

2D. Existing OFF E9 Debug checkpoint NONRESUMABLE; never use as seed. No fallback to fresh chemistry invented by Codex or old default/physical promotion.

## 3. One bounded full telemetry campaign ONLY if eligible

The E10 science has already run full3×384. Replaying that campaign only to produce **new 5-field native internal telemetry and stage evidence** is an affected-observability dependency change, not a new physics model or repetition needed for E11 arithmetic. After pilot source/bit parity, actual per-host memory/time preflight and owner execution scope confirmation, use exact same N384 lattice and mode selection with new opt-in example. Execute at most three independent k0→384 histories OFF/KF/GM, one campaign, each with unique output/receipt/temp names; 1,152 accepted steps maximum. If the user's existing scope does not cover this new measurement, stop at completed pilot and return needed scope hash rather than launching full history.

For each full candidate:
- `OWNER_NATIVE_41.csv`, `OWNER_SELECTED_RCT.csv`, `STEPS.csv` must remain **byte-identical to sealed E10 native full**; require no scientific source, event/tolerance, output ordering or clock mutation.
- 5 new native internal fields at 385 states must be matched bitwise against E7 source-locked saved reference. On first mismatch FAIL/CHECK_SOURCE, not post-hoc tolerance adaptation.
- Accepted trace must have declared stage records for every accepted k>0; numerical stage/root interval certification remains separate even if trace is exported.
- Max original number/energy/residual gates from sealed E10 cannot be relaxed; GM prior norm-ratio .994761998538 lies near1. No false wide-margin language.
- Provider gamma live vs Endpoint should retain the **distinct** source definitions, old max allowance ratio3.543295/FAIL. Do not treat final k384 equality as all-epoch equivalence. No change to physical E7 `Gamma` authority or default owner output.
- RCT cumulative photoheat, escape, chemical owners are already included in combined MaterialOwners; do not double add; preserve original 35eV **research escape closure only**.

Independent stage numerical evaluation, if requested, must use an algorithmically distinct source-bound residual/interval evaluator with actual stage inputs, not simply the accepted_trace metadata. If full stage preconditions/certificates are unavailable, keep `STAGE_INDEPENDENT_NOT_EVALUATED` and deliver trace only.

## 4. Parallel-lane information; NOT new combined ON model

Read latest bass_cr R14 and its conditional first-cell Thomson tau only as a provenance/claim guide, not an HE385 continuous error bound. Read rei_bianchi BRIDGE16 test-only checkpoint/compensation audit and preserve original nonresumable E9 Debug semantics. WU088_HH NCP Drive restore is per-object only; HH ON06G highT source must not be added to HE lowT. No silent CR/HH/REI science rerun or global F09 activation. Preserve a frozen source ledger and compatibility matrix.

## 5. Reporting, publication, backup, return

Create immutable per-step accepted evidence, `SOURCE_IDENTITY.json`, `RECOVERY_INVENTORY.json` (tree/mtime/size/SHA/processes), `TESTS.json`, `TELEMETRY_AND_GAMMA_COMPARISONS.json`, `STAGE_TRACE.json`, `FAILURE_RECORDS.json`, `CLAIM_GATES.json`, `REPORT_KO.md`, `RETURN.json`, `NEXT_DAG.json`. Include all executed commands/exit status and source/config/compiler flags/RSS/CPU/wall. Root/receiver remote unchanged unless separately approved by its owner. Additive report/code only in authorized BASS_HE research branch with non-force push and readback.

Immutable ZIP and create-only Drive+Dropbox in existing known destinations, both actual ACK/object ID/name/size/parent. One byte download primary provider then metadata second, do not duplicate bytes or overwrite old records. `UPLOAD_VERIFIED != RESTORE_VERIFIED`, original source PDFs never publicly redistributed.

New scientific gate remains baselineRCTOFF; actual physical atomic photon-energy/heat/recoil moments=NULL; HE-F2/F09 global OPEN; physical/production HOLD. Report exact statuses for pilot, 1152 telemetry replay (if executed), endpoint Gamma discrepancy, stage independent certification and owner remote adoption individually. No background jobs after the host process exits; no unreported retries.

First report **(a)** source pin/preflight/host, **(b)** compiled telemetry first2 result, **(c)** full telemetry eligibility and execution result or exact blocker. When possible execute, package, publish, double-backup and supply a concise Korean return with remote IDs and hashes. Do not respond with just a new plan.
