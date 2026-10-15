# Codex handoff: rei_bianchi independent LRS H/He recombination + thermal, 2026-10-16

다음 작업은 **실행**이다. 메타검토나 반복적인 DAG 재작성에 시간을 쓰지 말고, 복원 가능한 실제 NCP 테스트·수렴성 결과·백업·증거를 만들어라.

## 0. Authority and boundaries

- 원본 repo: `cosmosapjw-quantum/rei_bianchi`.
- PR #152 fixed background input: `bbbd18b5c16eff70bc32ba4296360dceb9060ec4`.
- PR #153 verified source base: `e98d30efb5e725a79743d3a8ff61ee7e5169b498` (`research/rei-dynamic-verner-chemistry-20261016`).
- V4 신규 독립 브랜치: `research/rei-lrs-recomb-thermal-oracle-20261016` (이 브랜치 head는 현재 GitHub에서 읽어 확정할 것). Draft PR을 open 상태로 유지하되 production에 merge하지 않는다.
- 원본 저장소의 `codex/rux-science-delivery-20261014`, PR #150 FLRW native production, PR #151/154, 다른 source owner, 활성 NCP jobs/checkpoint/readback/분석결과를 건드리지 않는다. 기존 dirty/untracked 파일은 절대로 덮어쓰지 않는다.
- metric `(-,+,+,+)`, `Σ=sqrt(3)|s|/H>=0`와 별도의 signed `s/H`, eV, Mb, proper H0(s^-1), `X=ln(a/a0)`, `Tgas[K]`를 고정한다.
- 결과의 물리 claim은 조건부 photo+recomb+thermal reference이며 **물리적 Case-B/실제 EoR production은 HOLD**. 이번 recombination rate와 cooling은 toy closure, Verner cross section만 primary-data sourced.
- ChatGPT는 Desktop Commander 월간 할당량 때문에 사용자 Ubuntu와 NCP에 새 V4를 실행하지 못했다. Ubuntu/NCP 실행을 허위로 승격시키지 말 것.

## 1. 우선 readback과 최신 repo 대조

GitHub의 `research/rei-lrs-recomb-thermal-oracle-20261016` 브랜치에서 `RESEARCH_V4_KO.md`, `NCP_RUN_V4.sh`, `V4_INPUT_SHA256SUMS.txt`, `recomb_thermal.py`, `tests/test_recomb_thermal.py`, `run_recomb_thermal_v4.py`, `ncp_recomb_sweep_v4.py`, 그리고 기존 `dynamic_chemistry.py`, `verner_angular.py`, `lrs_threshold_oracle.py`, `donors/verner1996_photo.dat`를 읽어라. 정확한 source SHA/parent SHA를 확인하고 실제 `git status`와 `git worktree list`를 기록한다. 기존 Ubuntu PR #152의 untracked `dynamic_chemistry.py`는 이전 미검증 중단본일 수 있으므로 절대 덮어쓰지 않는다. 별도 작업 디렉터리만 사용한다.

## 2. NCP 서버, 전용 작업경로

사용자가 이미 승인한 SSH:

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

접속 후 `hostname`, `nproc`, `free -h`, `uptime`, `ps -eo pid,pcpu,pmem,args --sort=-pcpu | head -15`, `python3 -V`, `/root/.cargo/bin/rustc -V`를 **읽기 전용**으로 점검한다. Rust가 PATH에 없어도 이미 설치된 `/root/.cargo/bin/rustc`를 이용한다. 기존 PR #150, PR #151, rux, microphysics 작업은 중단하거나 변경하지 않는다. 새 독립 경로 `/root/REI_LRS_CASEB_V4_20261016`을 create-only로 만든다. 동일 경로가 있으면 그 상태를 조회·대조하고 사용자 파일을 덮어쓰지 않는다.

표준 배포: GitHub에서 정확한 브랜치를 clone/checkout 가능하면 `git clone --single-branch -b research/rei-lrs-recomb-thermal-oracle-20261016`을 사용한다. NCP에 repo credentials가 없으면 GitHub clone 인증을 우회하려 하지 말고, 제공된 `REI_LRS_CASEB_THERMAL_V4_20261016.zip`을 로컬에서 NCP로 SCP 전송해 별도 경로에 압축 해제한다.

```bash
# 아래 첫 인수는 사용자가 다운로드한 V4 ZIP의 실제 경로로 바꿔라.
scp -i /home/cosmosapjw/.ssh/ncp_key -P 22 /path/to/REI_LRS_CASEB_THERMAL_V4_20261016.zip root@49.50.142.2:/root/
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
# inside NCP:
mkdir /root/REI_LRS_CASEB_V4_20261016
cd /root/REI_LRS_CASEB_V4_20261016
python3 -m zipfile -e /root/REI_LRS_CASEB_THERMAL_V4_20261016.zip .
cd research/lrs_threshold_oracle_20261015
sha256sum -c V4_INPUT_SHA256SUMS.txt
```

If `numpy`, `scipy`, `pytest` are missing, use an **isolated local venv** inside the new NCP research folder, never modify shared OS Python or another research process. Set `PYTHON_BIN` to that venv's Python when running `NCP_RUN_V4.sh`.

## 3. 실제 실행

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export NCP_WORKERS=12
# NCP_RUN_V4.sh: input checksums -> 98 tests -> Radau benchmark
# -> smoke serial/parallel byte-equivalence -> 816-case deterministic full sweep
bash NCP_RUN_V4.sh
```

스크립트는 최대 16개 worker, 풀스윕 최대 900초, 실행별 독립 폴더를 사용한다. 기본 12개 worker로 다른 NCP 작업을 남겨두어라. 부하가 과도하면 더 작은 worker 수로 실행하되 결과와 실행 변경을 기록한다. 파라미터 816건은 17 signed shear × 4 photon rate strengths × 4 recombination strengths × 3 initial gas temperatures다. 각 경우 `.01/.005` X-step 재현성 비교 및 photon/electron/nuclei/thermal+binding+radiative energy residual을 측정한다. 이 self-refinement는 독립 Radau 오차가 아니며 따라서 별도 해석적 admission을 자동으로 허용하지 않는다.

## 4. 결과 판정 규칙

- source/donor SHA 일치, 기존 V2/V3/V4 test 98/98 PASS, output CSV 재열람, full/partial sample count 일치, 모든 gas/photon nonnegative, mass/number/electron ledger, gas+photon+binding+escape+work energy ledger, FLRW angular isotropy and Bianchi reflection symmetry 검증.
- 가장 작은 `.005` step 기준 Radau 연속 비교는 `run_recomb_thermal_v4.py`의 결과 참조. 사용자 장비에서 차이가 있다면 수치허용오차를 임의 확장하지 말고 **상태 오차·독립 RHS·atol/rtol·단위·시계·파라미터·기준 입력** 순으로 원인을 재현 가능한 자료와 함께 분석한다.
- 기존 검증 anchor: s/H -0.04, 0, +0.04에서 ne ≈ 0.07491382090756712, 0.07491323590241768, 0.0749137414064937; Tgas ≈ 6368.972438 K, 6369.389164 K, 6368.947747 K. 독립 Radau와 최대 state/ledger 오차 ≈ 4.3–4.6×10^-6 (mixed raw values). 전체 에너지 보존 잔차 ≲ 1e-12 eV/n★; 테스트 기준에 적힌 채널별 허용오차를 우선한다.
- 실패 시 stderr/stdout, retcode, seed/inputs, SHA, process state, last valid snapshot을 보존하고 한 번의 원인 확인 후 targeted fix/re-run만 진행. 같은 실패를 무의미하게 반복하거나 새로운 paperwork blocker를 추가하지 않는다.

## 5. 재사용과 마감

모든 새 관측 결과·코드·실행로그를 격리된 연구 브랜치의 독립 `research/lrs_threshold_oracle_20261015/evidence/ncp_v4_runs/...`에 필요 경로만 선택적으로 push한다. 기존 v3/rux/PR #150 base merge나 GitHub force-push는 하지 않는다. Push 후 GitHub readback으로 정확한 commit/tree/source/input identity와 기존 PR 대비 변경파일 목록을 확인한다.

최종 아카이브를 create-only로 `Google Drive/REI_RESEARCH_BACKUPS/rei_bianchi/REI_LRS_RECOMB_THERMAL_V4_20261016/` 및 `Dropbox/bianchi/research_backups/rei_bianchi/REI_LRS_RECOMB_THERMAL_V4_20261016/`에 각각 백업한다. 클라우드 업로드 완료 응답 및 실제 remote download/readback SHA-256 **양쪽**을 확인하되 서비스 오류 시 무의미한 재시도 반복을 중지한다. 저장 성공만으로 scientific PASS라고 주장하지 않는다.

종료 시 한국어 return handoff에 실행한 `hostname`, UTC/KST, branch/commit SHA, Python/Rust versions, NCP processes 충돌 여부, test counts/FAIL, 816 parameter results/statistics, 계산 비용, 체크포인트 경로, Google Drive/Dropbox object path 및 SHA-256 readback, independent scientific status, 최소 다음 구현 단위(확정된 Case-B/H-He cooling donor와 PR150 native chemistry rate matching)를 제공한다.

**STOP:** 원본 데이터/원자 provider 소스 식별 불일치, production checkpoint 덮어쓰기 위험, SSH 인증 차단, 예산 초과, 화학/복사 에너지 또는 photon-electron ledger 실패, 테스트 false PASS 중 어느 것이라도 발생하면 해당 경로의 mutation을 멈추고 유효한 결과만 보존한다.
