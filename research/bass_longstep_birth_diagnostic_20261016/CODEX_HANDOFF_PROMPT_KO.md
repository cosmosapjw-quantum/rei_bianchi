# Codex: REI PR159 long-chemistry timestep anomaly, source-age and Newton ablation

다음 연구 루프를 자율적으로 진행해. 사용자에게 파일 다운로드, 명령 입력, 권한 확인을 반복
요청하지 말고, GitHub 공개 저장소 및 기존 로컬/NCP 인가된 환경에서 직접 소스를 읽고 진행해.
이 실험은 REI PR159 source-bound BASS 동적 기하 내 **긴 구간 chemistry 비단조
수렴의 실제 인과 분해**가 목표이며 전체 EoR production 적합성 승인을 목표로 하지 않는다.

**Anchor:** [REI PR159](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/159),
source head `64a6dc33873e8be494f78e580a577c8083064eb1`, base REI PR150.
원래 `RETURN_TO_CHATGPT.json`, `research/bass_dynamic_20261016/CONVERGENCE_VALIDATED.json`,
`rust/rei_microphysics/src/axbi_driver.rs`, `axbi_covariant_transport.rs`,
`examples/bass_dynamic_trial.rs`를 먼저 확인하고 실제 최신 PR, source commit 및
`git status`를 읽어라. 이번 ChatGPT 연구에서는 source 자체를 변경하지 않는
독립 이론/수치 handoff PR에 다음 자료를 게시했다:
`research/bass_longstep_birth_diagnostic_20261016/{README_KO.md,birth_cohort.py,
manufactured_birth.py,audit_pr159.py,evidence/RAW_SNAPSHOT.json}`.
원본 22개 NCP raw `result.json`+`step_trace.csv` 44 파일의 SHA/base64가
`RAW_SNAPSHOT.json`에 보존되어 있어 **다운로드 요청 없이 GitHub checkout만으로**
재생산할 수 있다.

1. 원래 PR159 raw 상태와 원래 source 패킷을 byte-identity 검증하고, 기존 PR159
   checkpoint/production PID/output을 수정하거나 재시작하지 마. Git worktree는 별도 생성.
2. 기존 fixed 481-row BASS table, `COLD_FLRW`와 `SIGNED_MINUS`, 동일 초기 가스/광자/source,
   동일 endpoint `Δln a=4e-4`로 원래 4/8/16/32/64/128-step 결과를 재검증하고,
   원래 첫 4/8/16 출력은 변경하지 마. 16-step 원래 Newton 최대 residual
   `7.205e-12`/`8.841e-12`은 acceptance `1e-11` 근처다.
3. 별도 독립 축으로 (a) 기존 chemistry Newton, (b) 더 타이트한 Newton tolerance,
   (c) 각 photon old/newborn source-age 보정 후보를 비교해라. (b),(c)는 **새
   research opt-in lane**이어야 하며 기존 허용 오차나 물리 source/최초 입력을
   조용히 바꾸지 마. test matrix는 총 2 BASS cases, fixed grid 481,
   4/8/16/32/64와 필요할 때 128 chemistry steps; 기존 22개는 읽기 전용 기준.
4. 해석적 reference `N_BE=(Nold+S)/(1+τ)`,
   `N_uniform=Nold*exp(-τ)+S*φ1(-τ)`,
   `φ1(-τ)=-expm1(-τ)/τ`,
   `N_BE-N_uniform=[1/(1+τ)-exp(-τ)]*(Nold-S/τ)`를 활용하되, 기존 REI의
   분산 energy/mu cells와 Verner threshold, stage 내 비선형 gas opacity와
   original photospecies Γ/heat/binding interface를 존중해. `be_old_uniform_birth`
   hybrid가 제조모형에서는 **여전히 1차**였으므로 단순 일괄 새 photon 보정만으로
   실제 solver second-order를 주장하지 마. 기존 광자/신생 광자를 source age
   분리한 뒤 동일 parent photon number/energy moments, support and species
   absorption ledgers를 보존하며 투영해. HE24 PR71과 bass_cr PR75의 source-age/
   threshold-safe 연구는 source/units/semantics 확인 뒤 조건부로 재사용.
5. 각 step에 `dt_proper`, `emissivity(t_mid)`, old/new photon stocks,
   per-cell/species τ distribution, pre/post spectral support, photoevents,
   gas EOS/temperature, Newton nonlinear residual by iteration,
   Jacobian conditioning estimate and rejection/rollback records를 추가해.
6. 이 아카이브의 기존 원본에서는 광자 source count 4→8→16 오차비가 **3.997**이고
   가스 T 오차비는 **0.652**였다. 따라서 소스 통합 **총량**과 가스 state
   step 오류를 혼동하지 마. `p_eff = log2(|Δ_h/Δ_{h/2}|)`는 로그 지표이지
   충분한 단계/참고해가 없으면 수렴 차수를 판정하지 마. 32/64/128과
   Radau/DOP853 또는 고정된 더 작은 dt의 *같은* native physics reference가 필요해.
7. 광자수, H/He nuclei, thermal+binding+escape energy, redshift/shear work,
   Hamiltonian, Raychaudhuri, proper-time, signed shear Σ와 s의 분리,
   source-bound restart parity를 original tolerance와 units로 각각 검증해.
8. NCP 64 logical cores/125 GiB 중 이번 독립 작업 총 추가≤16 workers,
   메모리≤16GiB, 추가 disk≤4GiB, per-job wall≤1800 s. SSH는 사용자 인가 로컬
   `ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22`로 직접 접근,
   PATH rust는 `/root/.cargo/bin`. 기존 실험과 CPU affinity 충돌 방지,
   nested BLAS/OpenMP/Rayon 병렬화 제한. 접속 불가 시 local bounded 계산 및
   정확한 NOT_RUN 증거만 보존.
9. distinct draft REI PR을 새 브랜치에 게시하고 source + result raw + tests +
   negative gates + original first failures + restored git bundle를 보존한 뒤,
   Dropbox와 Google Drive에 서로 다른 create-only paths로 백업하고 각각
   다시 다운로드해 SHA256 비교. 실패한 upload/readback은 HOLD로 보고.
10. `RETURN_TO_CHATGPT.json`에 exact source/parent/commit/tree, 실행 명령 및
    exit code, source hashes, worker resources, 원시 및 normalized physics residual,
    4/8/16/32/64/128의 동등조건 convergence, 각 ablation 인과 판단,
    사전 과학 claim과 미완료 Q^a/stellar recoil/polarized Thomson/EoR 등을 기록.

**Science ceiling:** 원래 제조모형 결과는 `CONDITIONAL_DERIVED + SANDBOX_TESTED`,
실제 REI PR159 22결과는 `SOURCE_VERIFIED`, 하지만 긴 interval의 native
chemistry 수렴은 `HOLD` until new actual source-locked run verifies it.
PR159/PR150을 자동 병합하거나 과거 checkpoint로 새 배경을 재개하지 마.
사용자에게 별도 파일을 요구하지 않고 완료된 실제 결과만 보고해.
