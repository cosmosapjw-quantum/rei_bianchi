# Codex / NCP handoff — HE30 완료 결과 소비

아래 블록을 그대로 다음 Codex 세션에 전달할 수 있다.

```text
BASS_HE HE30의 완료 결과를 이어받아라. 사용자 목표는 non-tilted LRS Bianchi I의 독립 matter/radiation stress preliminary sweep와 평균 redshift z20→2 시간 진화이며, 이 목표는 완료됐다. 상세 성능 benchmark와 동일 science 재실행은 요청 범위에 없다.

권위:
- BASS_HE PR83: https://github.com/cosmosapjw-quantum/BASS_HE/pull/83
- source/data/D8 release commit: fb3146b94093776cad88e68cffb89b6559a405b3
- branch: research/he30-z2-continuation-20261021
- unit: research/he30_z2_continuation_20261021
- 최종 문서/ACK는 위 branch의 후속 metadata commit이다. 실행 source는 위 pin으로 고정한다.
- REI 원결과 publication: 3a525e3e16f1ba9393818a800327cc58597fd7b5
- REI closure 관찰: 744438f4512c7df1646aad0136ddc435b27200b0
- HE의 REI D8 전달: PR216, commit1f32cc442ebde284bbb944455ba96066c9e0e055

완료 상태:
237 saved histories = 231 nominal +6 guards. joint grid175, baseline91, overlap35. 각153epochs, 원래 full40/full56, exact z4 prefix/tail join. 이번 HE science0/benchmark0/NCP execution0. Independent data+figure admission PASS_SCOPED_PRELIMINARY, changed-code PASS, D8 delta PASS. 원본100개 recovered metadata는 null을 유지한다.

핵심 입력 identity:
D3 archive SHA256 7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498
compact histories.npz SHA256 d4258bc58948b318df2b9d5ea7ceca6258eac62147aececc6ec10068987b6c6c
kernel PR147 3b85dedce84d37b3e165da00685a8a984950aafe

물리:
sigma=diag(-s,-s,2s), pi_X=diag(-p_X,-p_X,2p_X).
Sigma_F=sqrt(6)|s|/H, signed S=sqrt(6)s/H.
P_X=(8piG/c^2)sqrt(6)p_X/H^2, Pi_X=abs(P_X), Pi_total=abs(P_m+P_r).
z는1/a-1의 평균redshift. elapsed time은z20부터의경과시간.
matter는fm=.1 massive collisionless nonbaryonic 성분, radiation은gamma+masslessnu, ne_source=None.
half-contraction과Frobenius의sqrt2변환 및DeltaP/3를보존한다. nativeHHe/production/CMB/continuumwide certificate로승격하지말라.

실행 원칙:
기존 owner checkout이나 다른 Codex worktree를 변경하지 말고 아래 pin으로 별도 worktree를 사용한다. 같은 완료237은 재실행하지 않는다. source/compact hash가 맞으면 반복 raw audit나전체테스트를 하지 않는다. 기존그림은즉시사용가능하며, 재표시가필요할때만 --plot-saved를쓴다. continuation.py는이미완료된자료의receipt만materialize하며ODE를호출하지않는다.

HPC:
다른 세션/과학 프로세스가 있다는 이유로 전체작업을 중지하지 말라. affinity/cgroup quota/currentCPUload/MemAvailable와 공유 /tmp/cosmosapjw_hpc64_cpu_leases를 사용한다. max_workers64, 기본reserveCPU2/RAM16GiB, one native thread, global content identity lock. 현재catalog는pending0이므로worker0이정상이다. 다른PID를종료하지말라. 실제NCP scaling/speedup은미측정이며 1GiB/worker는admission budget이다.

D8도완료:
Sigma_i=.003,Pr_i=-.001의Pm_i=-.0003,-.0001,0,+.0001에서저장인접표본bracket은각각
(2.8729833462,2.9353050508), (2.5192408407,2.5758703349),
(2.3546766722,2.4086580994), (2.1978077332,2.2492649203).
정확한eventroot/uniqueness/rigorousODEenclosure가아니다. 새root나ODE호출0이다.

실제로 후속 변경을 요청받으면 단일 다음 단위는 source가확정된 BASS_HE H/He electron-history donor의 ne(a)[m^-3] adapter다. ne=n_H*xHII+n_He*(xHeII+2*xHeIII), photon의Gamma_T=c*sigma_T*ne에만연결한다. 독립nu/massive stress의충돌항으로대체하지않는다. 기존완료baseline237과다른AGE/V12hold·budget는그대로보존하고변경된영역만검토한다.

반환물: 실제HEAD, 입력hash, 사용명령/exit, 새로생긴출력만의manifest, pending/worker상태, 변경된DAG와정확한publication/backup ACK. 이번완료단위를끝난것으로읽고남은과학계산을가상으로만들지말라.
```

## 필요한 경우의 실행 명령

기존 BASS_HE clone 안에서 실행한다. 대상 worktree 경로가 이미 있으면 해당 HEAD를 읽거나 새 경로를 선택한다.

```bash
git fetch origin research/he30-z2-continuation-20261021
git worktree add --detach /tmp/bass-he-he30-fb3146b fb3146b94093776cad88e68cffb89b6559a405b3
cd /tmp/bass-he-he30-fb3146b
python3 research/he30_z2_continuation_20261021/src/continuation.py
python3 research/he30_z2_continuation_20261021/src/shared_runner.py \
  --dry-plan --max-workers 64 --reserve-cpus 2 --reserve-gib 16 \
  > /tmp/he30-dry-plan.json
python3 -c 'import json; p=json.load(open("/tmp/he30-dry-plan.json")); print({"pending":p["pending"],"worker_starts":p["worker_starts"],"cases":len(p["statuses"])})'
```

예상 출력은 pending0, worker_starts0, cases237이다. 재표시나 D8 파일 재생성이 필요한 경우만 다음을 실행한다.

```bash
python3 research/he30_z2_continuation_20261021/src/analyze_saved.py --plot-saved
python3 research/he30_z2_continuation_20261021/src/late_reversal_brackets.py
```

검증 당시 Python3.12.14, NumPy2.3.5, Matplotlib3.10.8을 사용했다. 새 solver 설치는 필요 없다. 독립 검토용 과거 스크립트의 scratch 경로는 역사적 실행 경로이며, 동일 audit를 다시 실행하라는 인계가 아니다.
