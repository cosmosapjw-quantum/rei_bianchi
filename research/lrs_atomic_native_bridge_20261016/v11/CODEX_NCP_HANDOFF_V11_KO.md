# Codex 자율 실행 handoff: V11 source-off thermal → native Rust V12

당신은 `cosmosapjw-quantum/rei_bianchi`의 별도 V11 연구 브랜치
`research/rei-lrs-v11-sourceoff-thermal-clocks-20261016`의 HEAD를 GitHub에서
직접 fetch해 `research/lrs_atomic_native_bridge_20261016/v11/`을 읽어라.
사용자에게 파일 다운로드, SSH 실행, SCP 또는 수동 업로드를 요구하지 않는다.

## 권위와 경계

원본 frozen native PR150 owner source commit:
`6ea2b1b4b3875c9163cafc45efe720afded43fc4`.
V10 experimental parent PR172:
`c91ba18a38b744a1e64ff40423f02a35f2999605`.
최신 PR150을 먼저 조회하되 이 연구의 비교 입력은 frozen owner가 권위다.
PR150, PR172, PR167, PR169 및 active NCP checkpoint/production은 수정하지 않는다.
다른 연구에서 사용하는 source-age GL2, MD14/Case B/signed Bianchi는 별도다.

V11 Python Grackle literal source-free 41/41 pytest와 144-case Radau matrix,
CE midpoint 97.0–97.5% error reduction, all-midpoint nonstiff p≈2는 이미
검증되었다. 불필요하게 144-case sweep을 재계산하지 마라.

## 첫 실행 단위

1. `AGENTS.md`, V11 `R5_THEORY_KO.md`, `RESEARCH_V11_KO.md`,
   `src/ci_thermal_clock.py`, `evidence/C8_SUMMARY.json`,
   V10 `RESEARCH_V10_KO.md`, frozen owner `igm_rates.rs`, `igm_thermal.rs`,
   `axbi_driver.rs`, `igm_state.rs`를 읽어 실제 호출·단위·clock 위치를 고정.
2. 새 isolated git worktree와 새 NCP run dir를 생성.
3. 기존 `Driver::fixed_step`의 photon-off/zero-source opt-in 실험에서
   원래 `backward Euler`와 CE-only midpoint,
   chemistry-only midpoint, CE+CI+RR+FF+CMB 모두 midpoint를
   **서로 다른 experimental variants**로 구현하라.
   직접 구현이 과도하면 먼저 CE-only + all-mid 최소 3모드만 수행한다.
4. `X∈[0,10⁻⁵]`, HII=.075, HeII=.12, HeIII=.03, Tgas=15000K,
   total-H nuclei density, H(a), proper dt=dX/H(X), exactly matching EOS.
   N=8,16,32,64,128 (+256 if needed), and prescribed D5/Xend1e−4
   separate cases only when native inputs support identical physics.
5. Photon/source remain zero, **collisional and CMB terms stay ON**.
   No hidden RR/DR double application, no neutral-H-versus-total-H mistake,
   no rate coercion outside native Grackle source domains.
6. Output species, n_e, T, CE_HI/HeI/HeII cooling, CI events/binding,
   RR/DR cooling/escape, FF, CMB, gas expansion work,
   Newton mixed chemical+thermal residual and exact source identities.
   Evaluate conservation independently and compare actual native numerical
   endpoint to V11 Python benchmark and preferably matched native Radau RHS.
7. Reject nonphysical/negative states and failed Newton convergence without
   changing allowed tolerances. Separate order loss from roundoff and stiffness;
   do not equate conserved energy ledger to 2nd-order time accuracy.
8. Build/test and execute only bounded runs in NCP after live load inspection.
   Use preauthorized local SSH below, no user prompts.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

Observe existing ~64 CPU/125GiB constraints and other production/R9 jobs.
Use new `/root/REI_LRS_V12_CE_CLOCKS_<unique>` only. Default 1–4 Rust
build jobs, modest worker pool, never kill/update existing native run.

## DAG and delivery

At every selected completed theory/coding stage, push actual code, tests,
numerical evidence and `DAG_PROGRESS.json` to a new Draft PR stacked on V11.
Back up create-only archives to Drive
`REI_RESEARCH_BACKUPS/rei_bianchi/REI_LRS_V12_NATIVE_CE_CLOCKS/`
and Dropbox
`bianchi/research_backups/rei_bianchi/REI_LRS_V12_NATIVE_CE_CLOCKS/`,
then independently remote-read back SHA-256 from each.

Return Korean report with verified original and experimental source SHA,
actual commands/tests, per-clock per-step time convergence / Radau errors,
signed gas and photon ledger, physical applicability, NCP performance,
GitHub PR/commits and both verified remote backup hashes. Native causal
contribution, source-on p=2, and full EoR remain HOLD until actually checked.
