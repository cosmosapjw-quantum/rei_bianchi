# 독립 LRS: 병렬 이력 실행 계약
## Root Astra 계약 — 2026-10-20 UTC
Base metadata HEAD 96aaad584bbecded34485526a4bb53a49708ffc6; current Radau scientific source 5248822167e3fbe374f4333f7f2efdcdbfdaeeaf; VigilODE pin 8a8bd409b1d96c7b7421f496d229e119fd3d284e.

## 목표와 선택
한 가지 최적화는 독립 이력의 자원 제한 병렬 실행이다. 준비와 컴파일은 variant당 한 번, 각 이력은 하나의 native process, CSV 병합은 원래 순서로 수행한다. 새 수치 optimizer/rate cache/물리식은 도입하지 않는다. 기존 default legacy와 current Radau 성능 경로 cell-cache, borrowed 실험 지위를 보존한다.
현재 wrapper의 Cargo build jobs=1, Rust batch의 세 이력과 workers<=4 제한을 확인했다. 저장된 NCP compile345.14780946599785s와 별도 raw 내부19이력 합4.937230308s를 읽었다. 이 경계가 다른 시간을 속도비로 나누지 않는다. 추가 실제 profile3개가 모두 exit0인 근거는 profile_baseline/PROFILE_RECEIPT.json이다.

## 실제 backlog
- V12 photon/source-free thermal clocks: 3cases×8modes×6N=144 과거 local histories의 NCP host reproduction. cells8/threads1, native validation1e-8와 기존 Newton 기준 유지.
- V13: 2X×7modes×6N=84 과거 local histories의 NCP host reproduction. X=1e-5,1e-4; N=8,16,32,64,128,256; cells32; nonlinear tol1e-15. 원래 V14 84와 동일한 설정으로 취급하지 않는다.
- time_centered SSPRK2: 기존 transport52rows, coupled fixed6/birth10 이력 및 해당14tests의 NCP host reproduction.
- current source524882의19설정과 borrowedN2, original V14 84는 이미 NCP완료. 기본 backlog에서 제외.
이들은 새 과학 모델로 집계하지 않는다. 최신 cell-cache Radau의 seeded-disabled를 V12 photon-free나 V13의 solver에 대입하지 않는다.

## 식과 독립성
각 이력 j는 입력 theta_j가 고정된 dy_j/dt=F_j(t,y_j;theta_j)를 풀며 공유 mutable state가 없다. 전체 Jacobian은 block diagonal이고 i≠j에 대해 D F_j F_i-D F_i F_j=0이다. 따라서 서로 다른 이력의 실행 순서를 바꾸어도 각 초기값문제와 그 내부 계산 순서는 같다. 이는 프로세스 사이의 병렬화이며 cell/node/species/compensated_sum을 재배열하지 않는다.
total-H 기준 e=x+Y(y+2z), Y=.2454/[4(1-.2454)]=1227/15092와 de/dt=dx/dt+Y(dy/dt+2dz/dt)를 유지한다. P/C/R/D, binding/heat/cooling/escape/CMB/work columns는 원래 파일별로 유지한다. 여러 모델의 CSV는 하나의 물리 합으로 섞지 않는다.
독립 p개 worker, 양의 시간 t_j, W=sum(t_j), L=max(t_j)에 대해 T_p>=max(W/p,L). 완료가 가장 늦은 job의 시작 s는 list scheduling에서 p s<=W-t_last이므로 T_p<=W/p+(1-1/p)L. 예측시간 순서는 성능 heuristic이며 실제 NCP speedup 보장은 아니다. shared build B가 있을 때 S=(B+W)/(B+T_p), dS/dB=(T_p-W)/(B+T_p)^2. 식/부호와 block-Lie bracket은 실제 Wolfram으로 검산했다.

## 허용 경로와 원본 보존
신규 실행 코드와 문서는 research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/ 아래 둔다.
기존 prepare_and_run.py에 허용하는 최소 변경: --build-jobs 양의 정수(default1), --build-only, 필요하면 --run-focused-tests. --all/--case/--prepare-only와 default scientific behavior를 유지하고 CARGO_TARGET_DIR 영향을 제거하거나 명시 실패로 처리하여 정해진 binary 경로와 일치시킨다.
native 원본152파일, 기존 append hook, VigilODE477, Cargo pin/lock, native formulas, tolerances, provider/EOS/FD/GL2birth/default/transaction은 변경하지 않는다. old examples도 그대로 둔다.
V12/V13은 원본 example의 정확한 SHA에 묶인 새 derived example 파일만 추가한다. 원문 전체를 보존한 복사본에 (case,mode,N) 선택 guard만 삽입하고 새 filename으로 컴파일한다. 원본 history 본문/CSVheader/산술 연산/step loop는 그대로다. 필터는 모두 필수이며 허용 집합을 CSV생성 전에 검사한다. 필터가 없거나 잘못되면 실패한다. V13 while-loop에서 skip할 때 n*=2가 필수다. 생성한 파일과 원본의 유일한 차이를 기록한다.
정상 V13 RESTORE_NATIVE.py, SSPRK restore_ssprk2_native.py 및 현재 prepare_and_run.py의 복원 경로를 재사용한다. 임의 clone/worktree/reset/clean은 금지. 기존 dirty checkout을 고치지 않는다.

## 자원·실행·재개
Linux allowed affinity를 읽고 사용자 max64 및 유한 cgroup CPU quota로 상한을 정한다. 실제 메모리 available/cgroup remaining과 사용자가 지정한 한도를 읽어 planner에 기록한다. nominal per-run memory budget은 검증된 peak-RSS 주장과 구별하고 여유를 남긴다. 실제 부족한 admission은 미실행 이유로 남긴다.
각 native job은 서로 겹치지 않는 CPU slot 하나와 transport/Rayon/OMP/BLAS threads1을 사용한다. compiler process 수는 자원계약 안에서 지정하며 빌드와 이력 실행의 합이 CPU budget을 넘지 않는다. 한 variant의 빌드는 하나만 실행한다.
spawn argv는 배열; 각 job에 독립 output, stdout/stderr, exit, elapsed, source/input/executable identity가 있다. start_new_session과 timeout 종료로 해당 process group만 정리한다. 원본 결과를 덮어쓰지 않는다.
기본 finite limits: V12 native aggregate180s(이번 신규 명시 cap), V13 X별 aggregate180s(기존 각 full sweep cap 대응), SSPRK native aggregate300s와 transport60s/coupled각180s. shard timeout<=원래 sweep cap. aggregate에는 완료 process wall과 active elapsed를 charge하고 소진 시 새 launch 중지/해당 active 종료, polling/teardown overshoot를 실제 기록한다. 빌드/표적시험 caps는 원래 recipe대로 또는 정확한 새 운영 override와 원인 기록.
재개는 같은 manifest/source/input/executable identity이고 검증된 completed 결과만 재사용한다. 실패·부분 결과는 보존하고 새 attempt 경로에 기록한다. 실행 실패를 PASS나 새 물리 no-go로 승격하지 않는다. DAG dependent 실패를 명시한다.
원래 순서의 CSV병합에서 V12 144keys/12096rows/46columns, V13 84keys/각X3528rows/동일header/정확한step범위를 검사한다. 타이밍 column은 비교에서 분리하되 dt_s는 물리량이다. 원래 analyzer의 tolerance를 유지한다.
SSPRK2 independent_coupled_audit의 고정 filename은 별도 alias directory에 원본 대응을 기록해 해결하거나 새 wrapper parameter로 해결한다. 과거 reviewer identity를 현재 독립 reviewer로 재사용하지 않는다.

## 경량 검증과 종료 기준
실제 source-derived examples가 필요하므로 이용 가능한 offline runtime을 복구해 bounded compile을 수행한다. 모든 기존 fixture를 재실행하지 않는다.
1. V12/V13 각각 대표 smallest native shard1개와 기존 저장된 같은 설정의 non-timing columns/rows를 비교한다. 실제차이가 있으면 원인을 root로 돌리고 tolerance를 발명하지 않는다.
2. scheduler의 서로 다른 CPU slots, child failure→DAG blocking, timeout/process-group 정리, resume reuse 및 source/input mismatch 처리, 정확한CSV merge coverage를 표적 테스트한다. 가짜 child는 scheduling 검증 전용이며 과학 검증으로 세지 않는다.
3. current exact binary c93db..의 기존 fixed/birth/disabled RadauN16을 동일환경에서 serial/parallel 실행하여 native outputs의 동등성과 새 runner를 확인한다. 성능을 주장할 경우 profile-off paired AB/BA와 전체 phase wall의 같은 측정 경계를 사용한다.
모든 실행은 bounded/원시로그보존; 신규 physics model 수0. 구현과 실제실행은 lower-tier agent, 최종diff/raw와 유도는 구현하지 않은 Astra reviewer, root admission으로 닫는다. 현재 NCP remote tool quota0/SSHkey부재를 사실대로 BLOCKED로 남기고 구현은 여기에서 완성한다.
production NOT_ISSUED, 기존 source-on general2nd/uniformstiff/positivity/CaseB/fullEoR/signedBianchi/positiveCMB/nonzeroBoundary/globalcertificate HOLD와 photonledger범위 유지.
