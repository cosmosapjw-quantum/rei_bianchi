# NCP 64코어 실행 인계 (read-first, 2026-10-16 KST)

**본 파일은 명령 가이드이며 실행 기록이 아니다.** 현재 ChatGPT Desktop Commander는 월간 사용 한도로 차단됨. 사용자 Ubuntu와 NCP에서 이 배포물을 실행했다고 주장하지 않는다. 기존 PR150 q512/q1024 full-history 작업과 R9 계산의 resource lock, checkpoint, PID를 우선 존중할 것.

## 작업 환경 복구 및 충돌 회피

소유자 Ubuntu에서 먼저 원래 소스/권한/작업 상태를 점검. SSH 키 내용은 공개 GitHub/ZIP 어디에도 업로드하지 말 것. 다음은 사용자 제공 SSH 사용 방법이며, 공개 repo에는 host를 하드코딩하지 않는다.

```bash
SSH_KEY=/home/cosmosapjw/.ssh/ncp_key
NCP_HOST=49.50.142.2
ssh -i "$SSH_KEY" -o BatchMode=yes -o ConnectTimeout=8 -p 22 root@"$NCP_HOST"
```

연결된 NCP에서 비파괴 inventory:

```bash
export PATH=/root/.cargo/bin:$PATH
hostname; nproc; free -h; df -h /; rustc --version; cargo --version
ps -eo pid,etime,stat,pcpu,rss,args --sort=-pcpu | head -25
pgrep -af 'REI_FLRW|microphysics_driver|axbi_driver' || true
find /root -maxdepth 2 -type d -name 'REI_FLRW_*' -print | head -15
```

상태를 먼저 repo의 PR150 최신 HEAD `HANDOFF.json`, `NEXT_DAG.json`, current NCP source archive, resource deadline, 005 terminal receipts와 대조할 것. 기록이 현재 시간과 동일하다고 가정하지 않는다. **이미 돌고 있는 생산용 작업을 재시작·종료·overwrite 하지 말 것**. 현재 외부 작업의 CPU/GiB를 확인하기 전에는 `--jobs 64`로 새 계산을 시작하지 않는다.

## v1 연구 패키지 복원/검증

이 문서가 포함된 최종 ZIP을 Ubuntu에서 받은 뒤 별도의 stage 디렉터리로 복사한다. 예시:

```bash
ROOT=/home/cosmosapjw/research_backups/rei_bianchi/20261016/thermal_bridge
ZIP="$ROOT/REI_C16B_THERMAL_REACTION_HANDOFF_20261016_v1.zip"
sha256sum "$ZIP"  # 공개 manifest/최종 assistant 결과와 비교
ssh -i /home/cosmosapjw/.ssh/ncp_key -p22 root@49.50.142.2 \
  'mkdir -p /root/REI_C16B_THERMAL_BRIDGE_20261016_001'
scp -i /home/cosmosapjw/.ssh/ncp_key -P22 "$ZIP" \
  root@49.50.142.2:/root/REI_C16B_THERMAL_BRIDGE_20261016_001/
ssh -i /home/cosmosapjw/.ssh/ncp_key -p22 root@49.50.142.2
```

NCP 세션 안에서:

```bash
set -euo pipefail
STAGE=/root/REI_C16B_THERMAL_BRIDGE_20261016_001
cd "$STAGE"
unzip -t REI_C16B_THERMAL_REACTION_HANDOFF_20261016_v1.zip
unzip -q REI_C16B_THERMAL_REACTION_HANDOFF_20261016_v1.zip
cd REI_C16B_THERMAL_REACTION_HANDOFF_20261016
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt  # only after verifying pip/network availability
./verify.sh
```

이때 패키지의 원래 Git snapshot, 첫 실패 로그, T-dependent physics 미승인 사항을 유지해야 한다. `51 PASS`가 확인되면 source-locked Python 기준 package를 해당 host에서도 재실행한 것일 뿐, native Rust 또는 full EoR 물리 검증을 뜻하지 않는다.

## 독립 병렬 시뮬레이션 (heavy lane, 비생산)

생산용 프로세스가 사용하는 코어와 메모리를 조사하고 안전한 상한을 정한 뒤 **별도 scratch**에서 실행. 일단 `--jobs 1`, `--jobs 8` 순으로 비교한다. 기초 컨트롤:

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python hpc_sweep.py --cases 512 --jobs 1 --substeps 64 --out evidence/ncp512_serial
python hpc_sweep.py --cases 512 --jobs 8 --substeps 64 --out evidence/ncp512_8proc
cmp evidence/ncp512_serial/results.json evidence/ncp512_8proc/results.json
```

`results.json`은 결정론적 입력의 순서화된 **수치 결과**이며 `timing.json`은 별도 비결정론적 측정이다. 원본 수치를 유지한 채 `sha256sum`, `time -v`, CPU 사용률, max RSS, 실제 exit code 및 `uname -a`를 저장한다. 8프로세스 실행만으로 `64-core` 사용률이 충분하다고 주장하지 않는다. 성공한 뒤에만 다른 무거운 진단의 resource allocation을 결정한다.

## native parity 계약: 무조건 실행 전 점검

1. `git status --porcelain`, git worktree, HEAD, open PR/active branches 확인. 외부 Codex/진행 중인 NCP full-run checkout 또는 checkpoint를 덮지 말 것.
2. source authority는 PR154 photon mirror와 실제 최신 PR150 Rust `igm_thermal`, `igm_rates`, `igm_state`, `axbi_covariant_transport`, `axbi_driver`. 계약/해시 `contracts/native_authority.json`의 SHAs는 **2026-10-16 수집된 과거 snapshot**. 최신 tree가 달라졌다면 exact current identity를 다시 기록하고 실제 semantic 영향을 비교할 것.
3. 첫 native parity는 읽기 전용 source+gas fixture에서 `native_photo_contract.photo_point`의 per-absorber `gamma_s`, `heat_erg_per_absorber_s`와 native `IgmPhotoInput`/`igm_point_rhs` *derivative*를 비교. Native CI/RR/DR/CE/freefree/CMB는 원래 Rust owner에서만 수행. 우리 Python 테스트용 CI/RR를 production photon operator와 **중복 결합 금지**.
4. `IgmGasState.fractions=[xHII,yHeII,zHeIII]`, `w_erg_per_h=thermal_ev_per_H * ev_erg`. `nHe=nH*fHe`. `gamma_s = c*nH*sum(Nj_per_H*sigma_i(Ej))`. `heat_erg_per_absorber_s=c*nH*ev_erg*sum(Nj*sigma_i(Ej)*(Ej-chi_i))`, fit threshold vs physical chi separate.
5. Native RR thermal owner is `rates.rr_cooling_erg_cm3_s` (coefficient!) times proper electron+ion densities. Do **not** equate the reference manufactured `rr_electron_kinetic_ev` with a physical coefficient. If deriving positive per-event `xi_RR`, first check `rr_cooling/rr` domain, DR/non-RR branches and Case-A escape ownership. `CE`, `DR`, `freefree`, `CMB`, expansion work, source photons and baryon recoil remain separate ledgers. This is **the missing physics implementation**, not a preapproved merge.
6. Claim gates: original H/He nuclei, electron charge, photon number, full binding+thermal+radiative energy with geometric/CMB/stellar owners, positivity, source-node ages, zero-UV source and FLRW tests, signed shear ± controls, finite-time/energy/angular refinements, and Native Rust tests. Retain initial failures. No tolerance widening for mismatch.
7. If all review gates pass, present exact diff, tests and intended scientific admission for owner review. Do not automatically merge this branch or modify the running full campaign.

## Backups and return payload

User-local `rclone` remotes: `dbx:` and `gdrv:`. Read actual configured remote paths before creating a new filename. Use `scripts/backup_dual_cloud.sh ZIP` to do create-only uploads and full byte-level redownload with SHA. Git commit + branch + PR and two provider successful upload ACKs are separate evidence dimensions. Append receipt with original `source_commit`, `source_tree`, SHA256/bytes, actual test logs and NCP run JSON, do not rewrite original failed runs.

Return to this ChatGPT thread: actual Git HEAD/branch/PR URL, suite count+commands+exit, source manifest, native parity numerical residuals, NCP CPU/RAM wall/peak/CPU metadata, `rclone` provider refs/upload/readback/restore results, and which physical owners remain unresolved. Then the next selected research stage can be executed from exact evidence.
