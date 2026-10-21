# Codex NCP 실행 인계: matter/radiation을 분리한 Σ–Π pilot

## 최신 목표와 이미 완료된 작업

Repository: cosmosapjw-quantum/rei_bianchi. 기존 PR198 branch는 `research/rei-lrs-v14-physical-birth-20261018`이다. 먼저 실제 remote HEAD와 이 디렉터리의 FINAL_DELIVERY.json, SOURCE_DELTA.json, ROOT_ADMISSION.json, DAG.json을 읽는다. `34f93a48778a2d8a36b058e33de5302732752bae`는 source/검증 checkpoint이며 최종 HEAD라고 가정하지 않는다.

새 사용자 요구는 π_ab를 matter와 radiation으로 분리하는 것이다. 실제 sandbox에서 기존625를 ODE 없이 분해했고 새 matter600+mixed6=606개가 모두 완료됐다. 25 neutral controls는 기존 source/actual k/hash를 보존한 REFERENCE_REUSE다. 독립 최종 검토와 response-fit addendum은 PASS_SCOPED_PRELIMINARY이며 numerical gate는 닫혔다. 완료된 분해/606/local tests/4-source comparisons를 의무 반복하지 않는다. 새로운 NCP site에서의 실제606 실행은 아직 NOT_RUN이다.

## 인증과 source 전달

사용자가 지정하고 승인한 연결:

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

이 ChatGPT sandbox에는 위 key가 없었고, 연결된 remote tool은 월 사용량 소진을 반환했다. 실제 SSH 인증이나 원격 자원 관측을 한 것으로 기록하지 않는다. 이 연결을 사용할 수 있는 Codex 환경에서는 사용자를 수동 SSH/SCP 또는 파일 다운로드 담당자로 돌리지 않고 직접 진행한다.

서버의 기존 checkout/HEAD/dirty 상태와 실행 receipt부터 읽는다. 같은 source/config/case의 새 NCP 결과가 이미 돌아왔으면 그 결과를 우선 회수한다. 다른 Codex 세션이 있다는 이유만으로 작업을 중지하지 않고, 그 작업을 종료하거나 dirty 파일을 덮어쓰지 않는다. 불필요한 clone/worktree/reset/clean/전체 checkout 전환을 추가하지 않는다. 확인된 remote source의 additive pilot subtree를 정상 전달하고 원래 수치 source 및 reference table 해시를 확인한다. 충돌하는 로컬 변경은 보존하고 범위를 보고한다.

이 경로는 NumPy/SciPy/Matplotlib를 사용하는 Python 코드다. 원래 native LRS의 Cargo compile/test/run 계약과 섞지 않는다. 이 새 pilot에 Cargo build는 필요하지 않다. Python 환경의 실제 버전과 command stdout/stderr/exit code를 기록하고, 필요하면 작은 실행환경 호환 수정만 한다. Physics/tolerance/model 변경은 Astra 판정으로 반환한다.

## 하나의 유한 실행

기존 repository root에서:

```bash
bash research/rei_bianchi_sigma_pi_pilot_20261021/matter_radiation_20261021/run_ncp.sh
```

이 wrapper는 새 timestamp 경로에606 coupled trajectories를 실행하고 성공 후 NCP-labeled figures를 만든다. 필요한 source는 parent `pilot.py`, `record_command.py`, `SOURCE_ATTRIBUTION.json`, vendor4개 및 이 확장의 코드/CONTRACT_KO.md/reference_controls.json/old_representative_histories.csv다. 게시된 참조 table 덕분에 기존625 raw NPZ 전체를 서버로 옮길 필요가 없다. 최신 체크아웃에는 이 필요한 파일들이 함께 있다.

최대64 worker를 지원하되 affinity/cgroup quota/관측 spare CPU/host-cgroup 가용 memory에 따라 batch마다 조정한다. Worker BLAS/OpenMP1, nice10, 명목256MiB/worker와 reserve를 유지한다. 이 메모리는 peak RSS 측정값이 아니다. Wall cap900초, aggregate child task cap3600초, 자동 retry 없음이다. 실제 사용 가능한 자원에서 나누어 진행한다. 다른 작업의 자원을 강제로 회수하지 않는다.

`--resume`은 new model/contract/parent6 files/reference-table/config/case identity가 모두 일치할 때만 허용한다. FAILED나 started-but-unfinished 상태를 성공으로 바꾸거나 재제출하지 않는다. 종료 관측/회계는 저장된 receipt 의미대로 보고하고 cap overshoot가 절대 불가능하다고 주장하지 않는다.

## 물리적 조건과 반환 evidence

같은 orthonormal normal frame과 같은 순간 H에서 `signed_Pi_m`, `signed_Pi_r`를 따로 저장한다. `Pi_total=abs(signed_Pi_m+signed_Pi_r)`이며 성분 magnitude 합이 아니다. Matter는 massive collisionless fm=.1 및 isotropic dust, radiation은 photons+massless neutrinos다. 두 slice는 초기에 특정 성분이 isotropic한 것이며 진화 중에는 반대 성분 stress가 생길 수 있다.

고정값은 zbar20→4,m/Tref30,24×12 Gauss3,L8,8-state,DOP853 rtol3e-11/atol3e-13,65samples다. 새 matter 초기 타깃은 |Pi_m0|≤.0004, mixed는 S0=0,±.004 및 signedPi_m0=−signedPi_r0=±.0004다. 원래 source의 positivity domain에서 bracketed A_m inversion을 사용한다.

반환할 것은 실제 source commit와 파일 해시, host/resource observations, command, stdout/stderr, exit code, results/ncp_<stamp>/run.json/summary.json/endpoints/모든 case NPZ·JSON·log, plot CSV/PNG/PDF다. 새 결과를 기존 Drive/Dropbox 경로에 archive+manifest로 저장하고 실제 upload ACK와 전체 readback 크기/SHA256을 기록한다. PR198에 expected-head fast-forward로 evidence/DAG를 게시하며 open/draft 상태를 유지한다.

이 명령은 과거 V12의 남은100건을 재승인하지 않는다. Cap180초/debit200.39897231891518초를 유지하고 이미 완료된 AGE time8/16/32 및 과거84/19를 replay하지 않는다. Native age/time convergence, full native H/He 및 일반 Bianchi I admission은 HOLD이며 production은 NOT_ISSUED다. 이번 local preliminary PASS 또는 NCP의 단순 실행 성공만으로 이를 승격하지 않는다.
