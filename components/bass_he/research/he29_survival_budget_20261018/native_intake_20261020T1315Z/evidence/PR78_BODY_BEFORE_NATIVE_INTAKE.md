## Current HE29 continuation — exact shared-reference budgets (2026-10-20)

The stored HE28 strip differences change sign with the time grid, while the four independent HE29 native reference pairs are still unreturned. This continuation adds a read-only analysis path that preserves shared reference terms, separates signed reference-conditioned residuals from strip/table contrasts, and retains useful partial returns. Original physics, rates, tolerances and solver paths are unchanged.

### Published and verified

| Role | Commit | Actual changed-file Git readback |
|---|---|---:|
| New-return intake | `3b125fc3cf80ce715353be17f640f2d9a5fb9f4a` | 12/12 |
| New analysis code pin | `09929b0a06a833f0c2497e72f074ec8694a264df` | 45/45 |
| Handoff/documentation snapshot | `a143b08eeeb37e7f8cdbc78d84f750c321a220be` | 8/8 |
| Final metadata and canonical handoffs | `d63135807c80dc2ada7f85214b5087b9e3dff375` | 11/11 |

These counts describe separate publication stages and include overlapping files. Source code remains pinned at `09929b0a`; the later metadata commits do not replace that execution identity. The original baseline remains `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner `f7830e2f55e7a1938bc3c98f61b60651f8dae474`, and packed ABI2 code `a5d4711460c09b310b78c9692aa62534b7a843d3` with VigilODE `a21d573980f66fe02891bd216153443b5352f921`.

### Behavior and new verification

- `linear_budget.py` exact-converts each binary64 operand, merges shared-key coefficients before projection, and reports independent-key product hulls separately from coherent same-method hulls. Exact widths and outward binary64 display widths remain distinct.
- `partial_returns.py` classifies absent/prepared/method-only/timeout/failure/completed states, reuses the original physical pair admission, checks file consistency and provenance cohorts, and preserves valid subsets. Method timing and whole-case/process timing remain separate.
- `analyze_budget.py` binds 18 stored transport DATA files to their pinned hashes and source/model/table identities. It copies the original audit bytes without rerunning its time/mixed/sign calculations. Existing restored baseline DATA can be read through `--data-root`; source and manifests stay in the analysis Git checkout. Output is create-only, atomic and fsynced.
- **28 new test methods passed on their first executions: core 10 + classifier 12 + CLI integration 6.** A single split independent C9 review found no blocking defects. These are new-scope checks, not replays of prior science or optimization suites.
- **20 independent manufactured theory cases** and the actual Wolfram signed-closure/shared-reference cancellation checks passed. These do not count as native results.
- The actual local no-return CLI matched **18/18 DATA hashes**, admitted **0/4 pairs**, produced **0 reference-dependent rows**, reported no input errors and returned the expected **exit 1/HOLD** in 0.16578906699942308 s. This wall time is not a native performance benchmark or an observation of NCP processes.
- The new analysis handoff Bash syntax passed. Its execution commands and all inherited suites were not run in this continuation.

### Intake, preservation and remaining execution

Intake preceded research. It compared 83 BASS_HE branches and inspected related VigilODE/REI/REC/HH/BASS/bass_cr changes, recent backup surfaces and local evidence. Related projects contain new results with different model/source/binary identities; none were admitted as an HE29 reference pair. Other-conversation search returned an actual error, and capped provider/index observations do not prove absence of unpublished remote work. Exact coverage and failures are retained in the intake receipts.

**New native HE29 references: 0/4. NCP submissions: 0. NCP starts: 0. Unpublished NCP processes: unobserved.** The previously observed Remote Desktop Commander monthly quota/no-retry boundary was retained without another call. It is separate from the Drive upload status below.

| Preservation scope | Archive identity | Observed provider result |
|---|---|---|
| Complete current research changes + prior immutable preservation archives | `BASS_HE_HE29_REFERENCE_BUDGET_COMPLETE_20261020_7a86d5bb.tar.gz`; 6,621,294 B; SHA256 `7a86d5bbe27da9da52584edb27145b626c6954455729c9af3365147fc4802c08` | Dropbox `id:BSpOijBcT10AAAAAAD_SUQ`: actual raw GET, full SHA/content_hash, 70/70 payloads and 71/71 members PASS. Drive: one first upload without ACK/ID after 43 s, UNKNOWN; one capped exact-name observation found no match; no retry/alternate route. |
| Final canonical handoffs and actual final Git receipt | `HE29_REFERENCE_BUDGET_HANDOFF_CLOSEOUT_20261020_d0a76860.tar.gz`; 41,313 B; SHA256 `d0a768606dfe208152aa6015daa094361095dafefd0710e8b24eadf85d88b749` | Dropbox `id:BSpOijBcT10AAAAAAD_SVQ`: actual raw GET at 07:20:36 UTC, full SHA/content_hash, 15/15 payloads, 16/16 members and 2/2 canonical prompts PASS. Drive not attempted again after the two earlier unacknowledged new-object uploads. |

Full-archive Dropbox content_hash: `014e6096765e924b44a28ac25a6469ff1718be83c306cd37e72df68ff91bfdb2`. Final-handoff content_hash: `8aff5424c27a5a790111c0b74fe29a1a149c8d9d7a0024365869e9b0b2a89b73`. The final handoff receipt SHA256 is `afc1c413cf99c6852f4d5e97f0d377827a0ebab5c46dc1fa93d8ff662f1e6405`.

The full bundle preserves 62 Git snapshot files, four publication metadata files, one source snapshot manifest and three exact prior archive blobs. Their old internal verification and science were reused without replay. Earlier `77f1c73e`/`3380c7c4` dual raw PASS remain historical evidence. The standalone intake `f6efa95f` and older checkpoint `5675177f` Drive UNKNOWN outcomes are not relabelled by nested preservation.

Run source from Git and restore only verified DATA from archives. First read any new returns and their source/binary/table identity; analyze available subsets before requesting new execution. If absent, execute only missing original m8/GL4/q0 `(r2,512)`, `(r4,512)`, `(r8,512)`, `(r4,1024)` cases, each Radau+DOP853. Preserve the existing 1569 Bash and both overlays. Only after all four pairs are admitted is one optional r4/table512 packed canary allowed, at a5/a21 with one thread and the original full-state ledger norm.

**Scientific scope remains conditional.** Finite-candidate hulls and two-method agreement do not certify true ODE temperature error. Continuous spectra, a global gas-temperature bound, full EoR, whole upstream Grackle equivalence and observational Bianchi/CMB remain HOLD. Original gates remain unchanged, including absolute fraction `1e-11`. Completed HE28, HE29, VigilODE/Schur and ABI2 optimization results were reused; new native calls and inherited-suite replays were zero.

Current lane: [`continuation_20261020T0557Z`](https://github.com/cosmosapjw-quantum/BASS_HE/tree/d63135807c80dc2ada7f85214b5087b9e3dff375/research/he29_survival_budget_20261018/continuation_20261020T0557Z). See its `DELIVERY.json`, `DAG_STATUS.json`, `RESEARCH_KO.md`, `evidence/FINAL_BACKUP_RECEIPT.json` and `NCP_HANDOFF_KO.md`; canonical `NEW_CHAT_HANDOFF_KO.md` is also current. This closes the scoped analysis unit with declared native/Drive holds. PR78 remains **Draft/open/unmerged**.

---

<details>
<summary>Earlier published HE29 and packed Rust optimization closeout — reused evidence</summary>
# HE29 현재 상태 — 2026-10-20 최적화 closeout

원래 Python sparse 삽입과 반복 JVP callback 비용을 줄이는 선택적 ABI2 경로를 구현하고, 실제 측정·Git 게시·양쪽 백업 검증을 마쳤습니다. **새 HE29 native 반환은 관측상 0/4이며 이번 NCP 제출·시작은 0건**입니다. PR78은 Draft, open, unmerged로 유지합니다.

## 게시 및 고정 source

| 항목 | 실제 identity |
|---|---|
| 최종 문서·영수증 HEAD | `1765522318438e966e61d8a72f12084550da399d` — actual Git readback 39/39 PASS |
| 최종 ABI2 실행 코드 | `a5d4711460c09b310b78c9692aa62534b7a843d3` — actual Git readback 82/82 PASS |
| 첫 최적화 checkpoint | `8cb0ebb91a78d2f1b751caa1c3ffc5d170ddfe41` — actual Git readback 19/19 PASS |
| 원래 과학 source·tests | `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f` |
| 원본 Rust owner | `f7830e2f55e7a1938bc3c98f61b60651f8dae474` |
| 재사용 VigilODE | `a21d573980f66fe02891bd216153443b5352f921` |

실행 pin은 [DELIVERY.json](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/optimization_20261020/DELIVERY.json)의 `implementation_publication.code_commit`입니다. 후속 문서 HEAD로 대체하지 않습니다.

## 구현과 실제 측정

- 원래 계수와 canonical CSR 구조를 유지하면서 LIL scalar 삽입을 배열 조립으로 교체했습니다.
- 원래 RODAS5P–GMRES와 RHS/FD/partial-time 연결을 재사용합니다. Rust packed JVP는 정확한 state/time의 Jacobian을 재사용하며 한 행의 gas-then-photon 누산 순서를 보존합니다.
- 계수 저장량은 `16K+92`개입니다. 전체 gas4/photonK/ledger19 상태와 error norm, 원래 물리식·반응률·허용치를 유지합니다.
- Rayon1.12.0의 독립 출력 행 병렬화를 구현하고1/2/4 thread를 실제 비교했습니다. 이 workload에서는2/4가 느려 **NCP 기본값1**을 채택했습니다. 하드웨어 SIMD 명령 발생이나 native 전체 속도는 측정하지 않았습니다.

| r / K | Jacobian 조립 paired 가속 | 합성 비자율 IVP packed1 paired 가속 |
|---|---:|---:|
|2 /512|8.3455×|1.5324×|
|4 /640|8.7024×|1.4986×|
|8 /896|8.7804×|1.3787×|

조립 실험은 manufactured gas RHS로 조립 비용을 분리했고, IVP 실험은 알려진 해와 고정 Jacobian을 사용했습니다. 두 가속 비율을 곱하지 않습니다. 모든 IVP 비교에서 endpoint bits와 attempt 수가 같았습니다. 기존 HE28 pilot/6 study, HE29 90/720 및50 tests, 기존 VigilODE96/3/Schur23은 재실행하지 않았습니다.

새 범위의 model9개 고유 검사, Rust kernel7개와 serialization1개, 직접FFI4개, wrapper1개, builder boundary3개, controller entrypoint5개 및3크기×4모드 paired 측정의 증거를 보존했습니다. 별도 clean published checkout에서 NCP builder의 실제 컴파일도146.650초에 PASS했습니다. 이 빌드는 solver/test/native 호출0입니다.

측정 library `8299915d8490e958fbebe54d253d98c98b1b932a50e8640398ad4ec274abf434`와 compile-only rebuild `802190605e7b5e175f36d1d986e2a203c1835fbd6a39571895481b8efe9a92b4`는 별도 artifact입니다. 소스/toolchain/flags 일치와 경로·ELF layout 차이를 기록했으며 새 바이너리의 수치 동등성을 주장하지 않습니다.

고정1569의 입력 manifest에62자리 SHA가 하나 있었습니다. 검증된 a70 archive와 내부 manifest를 근거로 누락된 `4b` 두 문자를 복원했고,22개 DATA의 실제 복원/preflight/독립 검토가 PASS했습니다. 원본 DATA는 바꾸지 않았습니다. baseline isolated checkout에는 기존 재사용 overlay와 새 manifest repair patch 둘 다 필요합니다.

## 검증된 백업

| 묶음 | bytes | SHA256 | 실제 readback |
|---|---:|---|---|
|BASS_HE_HE29_OPTIMIZATION_COMPLETE_20261020_77f1c73e.tar.gz|4,719,121|`77f1c73e8b4239cabcf03983ec9f0852fe334ac732544e410947935c7f4d7ab6`|Drive·Dropbox 각각 raw+91/91 payload PASS|
|HE29_OPTIMIZATION_HANDOFF_CLOSEOUT_20261020_3380c7c4.tar.gz|1,714,101|`3380c7c432d6c05840b215b5ff129e8209e7ce5908221ed75d9a3e4a6f6e19aa`|Drive·Dropbox 각각 raw+47/47 payload 및 중첩 checkpoint21/21 PASS|

- Complete Drive: [1NBjWqsghFxbujCP6FELTfn7VPU-J8zfz](https://drive.google.com/file/d/1NBjWqsghFxbujCP6FELTfn7VPU-J8zfz/view)
- Closeout Drive: [12l06rbWAjxbsnJaLlsvRBTiXXBUYAhsd](https://drive.google.com/file/d/12l06rbWAjxbsnJaLlsvRBTiXXBUYAhsd/view)
- Complete Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_HE29_OPTIMIZATION_COMPLETE_20261020_77f1c73e.tar.gz`, ID `id:BSpOijBcT10AAAAAAD_SLA`, provider content_hash `a69aa6054a0442e010a0289f502a3c29fc7e4166ce3a41fd817b0302749c0463`.
- Closeout Dropbox: `/BASS_DERIVATION_DOSSIERS_20260912/HE29_OPTIMIZATION_HANDOFF_CLOSEOUT_20261020_3380c7c4.tar.gz`, ID `id:BSpOijBcT10AAAAAAD_SMA`, provider content_hash `3d4c91817c34cd72c6c86df42169050a696f54bb473da93e9dc2fea20f4781c9`.

최종 양쪽 readback 시각은2026-10-20T05:32:25–26Z입니다. 이전7bf complete도 이번에 Drive에서 실제 재다운로드하고229/229 payload를 확인했습니다. c47/798/7bf/882 등 기존 불변 객체는 덮어쓰지 않았습니다.

첫 checkpoint567의 개별 Drive 업로드는 provider 응답을 받지 못했고 Dropbox는 호출하지 않았습니다. 별도 조회에서는 완료 객체를 찾지 못했으므로 개별 업로드 성공을 주장하지 않습니다. **그 원본 archive의 정확한 바이트와 내부21개 파일은 새 closeout3380에 포함해 양쪽 실제 readback으로 보존을 확인했습니다.** COMPLETE 묶음은 변경된 Git source84개, 원본 입력 archive, 이전 complete archive와 측정 library를 보존합니다. 전체 Git history와 Rust registry/toolchain vendor는 포함하지 않습니다. 실행 source는 Git, archive에서는 검증된 입력 DATA만 사용합니다.

## DAG 및 다음 실행

이번 범위의 R1–R9, C1–C9 연구·구현·독립검토·경량 측정을 마쳤습니다. R10/C10은 실제 Git 게시와 complete/closeout dual raw 검증 및 다음 실행 계약으로 종결했습니다. Native 물리 검증은 별도 HOLD입니다.

1. 최신 native 반환과 접근 가능한 실행 중 프로세스부터 확인합니다. 반환이 있으면 source/binary/table identity를 읽고 분석합니다.
2. 없으면 원래 m8/GL4/q0 네 쌍 `(r2,512),(r4,512),(r8,512),(r4,1024)`에 각각 Radau+DOP853만 실행합니다. 완료 case와 기존 transport6개는 반복하지 않습니다.
3. 네 쌍을 모두 admit한 뒤에만 단일r4/table512 packed canary를1thread로 실행합니다. 새 solver 개발·전체 격자 확장은 하지 않습니다.
4. number3e-15/H, energy3e-12eV/H, species3e-12, positivity, 절대fraction1e-11, temperature difference1e-9K gate를 유지합니다. 성공·실패·partial과 source/binary/table/compiler/overlay identity를 보존합니다.

NCP 작업은 제출하지 않았습니다. Remote Desktop Commander 월간 quota와 재시도·재연결 금지 때문에 원격 프로세스는 미관측입니다. 이는 보이는 반환0/4와 구분하며, 사용자가 파일을 옮길 필요가 없습니다.

- [연구 보고서](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/optimization_20261020/RESEARCH_KO.md)
- [성능 보고서](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/optimization_20261020/PERFORMANCE_KO.md)
- [DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/optimization_20261020/DAG_STATUS.json)
- [기준해 Codex/NCP 인계](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/CODEX_HANDOFF_PROMPT_KO.md)
- [그 뒤 단일 canary 인계](https://github.com/cosmosapjw-quantum/BASS_HE/blob/1765522318438e966e61d8a72f12084550da399d/research/he29_survival_budget_20261018/optimization_20261020/NCP_HANDOFF_KO.md)

연속 스펙트럼, 전역 기체온도 오차상한, 전체 EoR, upstream Grackle 전체 동등성, 관측 Bianchi/CMB는 해당 범위 검증 전까지 HOLD입니다.

---

<details>
<summary>이전 게시 기록 — 아래의 당시 상태는 위 현재 closeout으로 대체됨</summary>

## Detached final handoff backup

The latest 12 closeout files and final Git readback receipt are separately preserved in `HE29_VIGILODE_HANDOFF_CLOSEOUT_20261019_88285fa4.tar.gz`: 24,809 bytes, SHA256 `88285fa4ea09e92b39bafbebd09ac6b25f5b76c201da6d297f14b4efe6663b96`. Drive `1IaFe8pGQ4qC-bOHXOhtDO_UHyA2t6nk9` and Dropbox `id:BSpOijBcT10AAAAAAD_Q4w`: both actual raw readbacks and all 14 payload hashes MATCH, verified 2026-10-19 13:47 UTC. This separate archive leaves the complete source/input archive `7bf7398b` immutable. It adds no solver execution or Git source change.

## 2026-10-19 VigilODE integration and verified closeout

Publication HEAD: `329f838399f24d3952f780d469ad657d8630c4e2`. Executable extension source: `57642252991b5c453db66eb5a078e6a62cc6f4ea` (54/54 exact GitHub file readbacks). The subsequent closeout changes docs/DAG/receipts only (12/12 readbacks). Original scientific source/tests remain `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`, native owner `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474`.

The original four HE29 Radau+DOP853 pairs are still 0/4 observed new returns. Related GitHub branches/results and direct backups were read; the additional 40 folders contained 881 direct entries and no new HE29 return. The separately downloaded VODE comparison archive was read in full and its 10-member manifest matched; it lacks HE29 source/binary/table identity. Unpublished NCP workspace state remains unobserved. Remote Desktop Commander is paused by its monthly quota, so this thread has not submitted or started NCP jobs.

The new opt-in lane reuses VigilODE `a21d573980f66fe02891bd216153443b5352f921` sequential RODAS5P/GMRES and its existing faer dependency. It connects the original physical RHS/CSR Jacobian through a checked C ABI, uses normalized cutoff intervals and endpoint output without dense interpolation, preserves raw/partial failures, and admits at most one r4/table512 canary only after all four original reference pairs are completed and admitted. No replacement solver, old transport rerun, automatic larger grid, changed microphysics or relaxed gates.

New evidence: 23 synthetic Schur systems plus symbolic block residuals; 96 unique Python callback/FFI/identity/canary checks; actual Rust 1.94.1 locked/offline bridge build; three real small Rust FFI smokes (analytic nonautonomous endpoint, callback failure, partial output). These are scoped new checks, not HE29 native reference completion. The 4x4 Schur reduction is theory/check code; a custom production Schur preconditioner is not claimed. Existing HE28 pilot/6-case study and HE29 90-case/720-bound/50-test evidence were reused without rerun.

Complete archive: `BASS_HE_HE29_VIGILODE_COMPLETE_20261019_7bf7398b.tar.gz`, 2,958,755 bytes, SHA256 `7bf7398b77b2bf04a6917bef4241fc216764c7658ebf25c85e5df7377fb6147a`. Drive `1RypR402ikbM_nF42R6NUzExWQfa0Xp6G` and Dropbox `id:BSpOijBcT10AAAAAAD_Q4A`: actual raw-byte SHA and all 229 payload hashes MATCH; Dropbox provider content_hash MATCH. The archive preserves the new source/receipts, authenticated VigilODE source subset, sandbox library and unchanged original HE29 code/input archives. R2 checkpoint `78356130` also has dual-provider raw readback MATCH. Old archival readback limits below are historical records and are not relabeled.

Current status and reproducible NCP commands: `research/he29_survival_budget_20261018/vigilode_20261019/{README_KO.md,NCP_HANDOFF_KO.md,DAG_STATUS.json,DELIVERY.json,CLOSEOUT_RECEIPT.json}` and the top-level HE29 handoffs. Keep PR78 draft/unmerged. Continuous spectrum, full EoR, global gas-temperature bounds, whole upstream Grackle equivalence and observational Bianchi/CMB remain HOLD.

## Earlier preserved continuation records

## 2026-10-19 continuation

Current publication HEAD: `a2caf95d92399f6ffc096882c0617a0c6b5bd69b`; continuation implementation/handoff snapshot: `2f17a0313fea3fd4d109b0e1f8b88a8d812af447`. Scientific source and tests remain pinned to `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`.

Latest GitHub and direct Drive/Dropbox folder intake found no new HE29 native reference return. The inherited four-pair status remains 0/4 NOT_RUN; unpublished NCP workspace state is unobserved. Remote Desktop Commander reports its monthly usage limit, so this thread has **not submitted or started** native jobs.

The original bootstrap would rerun the inherited pytest suite. To follow the user's current no-repeat instruction, the separately hashed `ncp/REUSE_SOURCE_VALIDATION_20261019.patch` replaces only that invocation with an explicit evidence-reuse log and records execution HEAD/overlay/bootstrap hashes. Original Git bootstrap, scientific modules, tests, compiler/native qualification, four-case campaign and tolerances are unchanged. Only the new overlay application/drift rejection/Bash boundary checks were run; inherited tests and native calls in this continuation are zero. Use the updated `CODEX_HANDOFF_PROMPT_KO.md` to create a clean 1569 checkout, verify/apply this patch and execute the prepared four pairs.

Continuation package `BASS_HE_HE29_CONTINUATION_20261019_242201a1.tar.gz`: 18845 bytes, SHA256 `242201a11e93f1df71deb20324c7af8ff5ec1df49172fdfb1efd256e8e724664`. Drive upload/metadata and Dropbox upload/provider content_hash are confirmed. New archive raw-byte readback is NOT_VERIFIED in this sandbox. Full receipt and actual DAG are in `results/continuation_20261019/DELIVERY.json` and `DAG_STATUS.json`. Keep this PR draft/unmerged.

## Preserved 2026-10-18 publication record

Backup-first continuation of HE28 PR77 `a41dd37124e34cb22bb9782aaf687a0da91640b7`. Existing HE28 native pilot and six transport cases are preserved, not rerun.

Previously interrupted S2 implementation is now published at execution revision `1569f3718cd4b17a16936ad3d72bc7d5ed9b0f4f`. All six HE29 scientific/analysis Python modules and three bootstrap/input-recovery files were fetched from Git and their blob SHAs matched the tested local source. 47 inherited HE29 tests plus three new packaging-only tests pass: **50/50**. No scientific tolerances or original microphysics changed. No new native integration in this publication task.

Source result: positive-measure Jensen/chord survival envelopes, 90 frozen-source cases/720 nested evaluations. These certify the finite donor measure numerically, not continuum-energy or downstream gas-temperature errors. Existing HE28 cross-strip differences change sign with time resolution, so four same-model adaptive reference jobs are prepared: m8/GL4/q0 with (r2,table512),(r4,512),(r8,512),(r4,1024), each Radau+DOP853. All four new references are NOT_RUN. Original native owner `rei_bianchi@f7830e2f55e7a1938bc3c98f61b60651f8dae474` is compiled only on authorized NCP. Six saved native point checks are scoped point qualification, not upstream Grackle runtime equivalence.

A Git-only checkout now starts with `bash research/he29_survival_budget_20261018/ncp/START_REFERENCES.sh`: authenticated rclone retrieves the immutable original input archive if needed, restores only 22 individually hashed DATA files without executing archive code, rejects existing mismatches, then calls the unchanged bounded bootstrap. Whole archived input snapshot:129635 bytes, SHA256 `a70d320c7ead5f1fd93170c18f1f80ae5eb58a293a6045a0f728bb7ae2743205`; Drive id `1I31wE6A3laYE6nxMcKNmm5rNMeESIsXi`, Dropbox id `id:BSpOijBcT10AAAAAAD_Ncg`. Drive actual full-byte readback matched. Dropbox upload completed and provider content_hash matched; full raw readback remains blocked, not claimed. Full raw input records remain in this archive; the public selected projection is not their byte identity.

Final updated prompts, DAG and detached delivery receipt follow on this branch. Keep draft/unmerged. Full continuous-spectrum/EoR/CMB/upstream-equivalence claims remain HOLD.

</details>


</details>

