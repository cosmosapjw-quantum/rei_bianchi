# Codex NCP 인계: Σ–Π preliminary pilot

## 현재 완료 상태

이 문서와 같은 디렉터리의 `FINAL_DELIVERY.json`, `DAG.json`, `RESEARCH_REPORT_KO.md`, `evidence/final_review/FINAL_REVIEW.json`, `FINAL_ADDENDUM.json`을 먼저 읽는다. 실제 게시 HEAD는 원격 branch에서 다시 읽고, 실행 코드 identity는 `FINAL_DELIVERY.json`의 source publication과 `results/pilot/run.json`의 파일 SHA256으로 확인한다. 문서 게시 SHA를 과거 실행 checkout SHA라고 소급 표기하지 않는다.

625개 signed 초기 조건의 sandbox 실행, 40,625개 저장 시점, preliminary plot 및 구현하지 않은 Astra의 독립 raw 검토는 완료됐다. 판정은 `PASS_SCOPED_PRELIMINARY`, 실패 0이다. 완료된 sandbox 실행·검토를 다시 수행하지 않는다. NCP에서는 이 새 Python pilot의 실제 실행만 남아 있다. NCP에서 필요한 Python 의존성은 NumPy, SciPy, Matplotlib이다. 이번 additive pilot에 Cargo build는 필요하지 않다. 기존 native LRS의 compile/test/run 지시와 혼합하지 않는다.

## 연결 및 기존 작업 보존

사용자가 지정하고 승인한 접속은 다음과 같다.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

현재 ChatGPT sandbox에서는 이 key가 없고, 연결된 원격 실행 도구는 월 사용량 소진을 반환했다. SSH 인증이나 NCP 실행이 이루어진 것으로 기록하지 않는다. 다른 실제 인증 수단이 제공된 Codex 환경에서는 위 연결을 사용한다. 사용자를 수동 SSH/SCP나 파일 다운로드 담당자로 돌리지 않는다.

접속 후 기존 rei_bianchi checkout, HEAD, dirty 경로, 이 pilot 경로의 존재 및 실행 receipt를 먼저 읽는다. 다른 Codex 작업과 기존 owner checkout을 보존한다. 다른 작업이 있다는 이유만으로 중단하거나 그 작업을 종료하지 않는다. 불필요한 clone/worktree/reset/clean/전체 checkout 전환을 추가하지 않는다. 기존 branch `research/rei-lrs-v14-physical-birth-20261018`의 확인된 source에서 이 additive subtree를 정상 전달하고, 충돌하는 로컬 변경은 보존해 별도로 보고한다. receipt가 동일한 source/config/case identity의 완료 실행을 보여 주면 그 결과를 먼저 회수한다.

## 유한 실행 명령

기존 checkout의 루트에서 실행한다.

```bash
bash research/rei_bianchi_sigma_pi_pilot_20261021/run_ncp.sh
```

스크립트는 `receipts/ncp_<UTC stamp>/`에 command/stdout/stderr/exit code를 기록하고, `results/ncp_<UTC stamp>/`에 case별 NPZ/JSON/log, endpoint CSV 및 run receipt를 저장한다. 성공 후 NCP 표기의 그림을 생성하고 별도의 plot receipt도 남긴다. 새 출력 경로를 만들므로 완료된 sandbox 자료를 덮어쓰지 않는다.

최대 worker 수는 64이며 실제 affinity, cgroup CPU quota, 관측된 여유 CPU와 메모리에 맞추어 batch마다 줄인다. 명목 메모리 예산은 worker당 256 MiB이고 별도 reserve를 둔다. 이것은 측정된 peak RSS 보장이 아니다. BLAS/OpenMP는 worker당 1 thread로 고정한다. 우선순위 nice 10, wall cap 900초, aggregate child task cap 3,600초를 유지한다. 다른 작업에 쓰이는 자원을 강제로 회수하지 않는다. 이 유한 pilot에는 별도 benchmark campaign이 필요하지 않다.

실패·중단·미실행은 성공과 분리해 원래 receipt와 누적 debit을 보존한다. 자동 retry나 tolerance/physics 변경은 금지한다. 동시 실행이 가능한 가용 자원에서 진행하되, 자원이 부족한 경우 관측된 제약과 미실행 상태를 반환한다. source/config/case identity가 일치하는 resume만 허용한다. 수학적/물리적 변경이 필요하면 실행 담당자가 임의 수선하지 말고 Astra 판정 단계로 반환한다.

## 유지할 범위와 반환물

모델은 자체 중력·충돌 없는 reflection-even LRS Bianchi I, z̄20→4, 공통 γ/ν quadrupole, massive fm=.1, m/Tref=30, A_m=0, 24×12 Gauss3 canonical cells, L8 even-energy block이다. half-contraction norm을 유지한다: `Sigma=sqrt(3)*abs(s)/H`, `Pi=sqrt(3)*(8*pi*G/c**2)*abs(p)/H**2` (p는 J/m³). full native H/He feedback, 일반 Bianchi I closure 또는 production admission으로 확대하지 않는다.

반환물은 실제 source commit 및 파일 해시, command, host/resource observations, stdout/stderr, exit code, run.json, endpoints.csv, 모든 case NPZ/JSON/log, plot data와 그림이다. 기존 Drive/Dropbox 경로에 archive와 manifest를 저장하고 실제 업로드 ACK 및 가능한 전체 readback의 크기/SHA256을 기록한다. 기존 PR198에 expected-head fast-forward로 evidence/DAG를 게시하며 PR은 open/draft로 유지한다.

과거 V12 cap 180초/debit 200.39897231891518초와 남은 100개 job의 `NOT_AUTHORIZED`를 변경하지 않는다. 완료된 AGE time8/16/32나 과거 84/19 native 실행을 재실행하지 않는다. native age/time convergence는 HOLD, nonlinear Grackle response bound는 NOT_ESTABLISHED, production은 NOT_ISSUED다.
