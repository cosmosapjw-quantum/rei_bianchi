# Codex handoff — HE31 실행만 수행

아래 블록은 NCP Codex에 복사한다. 실제 게시된 구현 commit을 실행 pin으로 고정했다.
후속 delivery metadata commit은 과학 코드나 입력을 변경하지 않는다.

```text
목표: BASS_HE HE31의 이미 구현·검토한 실제 R15 donor pilot18을 NCP에서 실행하고
결과 JSON/그림/receipt를 반환한다. 이론 조사나 알고리즘 설계는 완료되어 있다.

Repository: https://github.com/cosmosapjw-quantum/BASS_HE
Draft PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/84
Branch: research/he31-electron-donor-thomson-20261021
실행 source pin: 1c8a56aac89d0e40ede8770009f80ebca40a4d2c
Unit: research/he31_electron_donor_20261021
Donor identity: 96661134c04f69c67188863e585d831f61e090ac0fdc05dda7e977f1810d9eaa

1. 현재 다른 Codex 작업의 checkout과 프로세스를 보존한다. 기존 repo의 위 branch를
   fetch하고 고정 commit의 별도 worktree에서 실행한다. dirty checkout을 reset하거나
   다른 프로세스를 종료하지 않는다.
2. Python3.12 호환 환경의 NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8을 사용한다.
   필요한 경우 unit/requirements.txt로 환경을 맞춘다. 별도 native compile은 없다.
3. 저장소 root에서 다음을 실행한다:
   bash research/he31_electron_donor_20261021/run_ncp.sh pilot18_on
4. max64, reserve2CPU/16GiB, native threads1, 공통 lease
   /tmp/cosmosapjw_hpc64_cpu_leases와 관측된 CPU/quota/memory headroom을 유지한다.
   다른 session 존재만으로 중지하지 말고 가용 자원으로 계속한다.
5. exit2는 일부 실패/보류를 뜻한다. receipt와 실패 로그를 보존하고 원인을 분류한다.
   시작하지 않은 DEFERRED만 같은 명령으로 완료 identity를 재사용하며 재개한다.
   시작 후 TIMED_OUT/FAILED receipt는 PRIOR_ATTEMPT_PRESERVED로 고정된다.
   같은 명령이나 새 output만으로 재시도되지 않는다. 원 receipt를 보존하고 원인을
   분류한 뒤 영향 범위의 수정(새 과학 identity) 또는 명시적 retry 처리로 진행한다.
6. pilot18 완료 뒤 필요하면 같은 runner로 joint175_on을 실행할 수 있다.
   상세 benchmark나 완료된 HE30의237개 z20→2 baseline을 재실행하지 않는다.
7. results/ncp_pilot18_on/RUNNER_REPORT.json, case JSON, plots PNG/SVG,
   endpoints.csv, ANALYSIS_SUMMARY.json, 실제 git HEAD, 환경 및 resource receipt를
   함께 백업·게시하고 반환한다. 새 결과를 이전 source identity와 혼동하지 않는다.

과학 범위:
- 실제 donor는16,385행의 R15/HG97-B reduced Q history, z20→4이다.
- HII+HeII ionized filling region, HeIII=0, residual electrons 없음.
- 기존40 physics state + target-clock tau 진단1; unpolarized Thomson은 photons만.
- matter fm=.1,m/Tref30은 비바리온 collisionless sector다.
- P_r=P_gamma+P_nu를 signed로 합치고 Pi_r=abs(P_r)를 취한다.
- 현재 입력을 z2로 extrapolate하거나 기존 native source의 z>=4 guard만 삭제하지 않는다.
  실제 z20→2 H/He source 채택·생성은 다음 ChatGPT 연구 단위다.

이미 확보한 sandbox evidence:
- actual on/off2 + original-FV reference1 완료, 121시점씩.
- source-pinned prepared/reference max state diff1.8030021919912542e-12.
- paired z4 tau=.03724155220658596; Sigma_on=.00013890261117025876.
- 기존 결과 재사용2건/새 worker0; 독립 donor/prepared/receiver/result 검토 통과.
- 초기 clock기준 실패 및 NumPy JSON 실패 로그를 보존했고 영향 항목만 재확인했다.
```

## 고정 source 실행 명령

기존 BASS_HE repository 안에서 `HE31_NCP_WORKTREE`만 원하는 새 절대 경로로 바꾼다.

```bash
git fetch origin research/he31-electron-donor-thomson-20261021
HE31_NCP_WORKTREE=/absolute/new/path/BASS_HE_HE31_NCP
git worktree add --detach "$HE31_NCP_WORKTREE" 1c8a56aac89d0e40ede8770009f80ebca40a4d2c
cd "$HE31_NCP_WORKTREE"
python3 -m pip install -r research/he31_electron_donor_20261021/requirements.txt
bash research/he31_electron_donor_20261021/run_ncp.sh pilot18_on
```

이미 적합한 Python 환경이면 pip 명령은 생략한다. 결과별 source content는
`evidence/EXECUTED_SOURCE_MANIFEST.json`, transport와 Git pin은 `delivery/`에서
확인한다. 실행 commit 이후의 최종 metadata commit은 새로운 물리 실행을 뜻하지 않는다.
