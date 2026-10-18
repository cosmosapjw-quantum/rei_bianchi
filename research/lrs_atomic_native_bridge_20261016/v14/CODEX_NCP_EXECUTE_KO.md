# Codex: REI-LRS V14 실행 전용 인계

사용자에게 파일 다운로드·압축 해제·SSH/SCP를 요구하지 않는다. GitHub에 있는 완성 소스와 실행기를 직접 확보한다. 새 물리 알고리즘 설계가 아니라 컴파일/작은 호환 수정/실제 실행/결과 회수가 목표다.

Draft PR #198: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198
Repository cosmosapjw-quantum/rei_bianchi, branch research/rei-lrs-v14-physical-birth-20261018. 실행 코드 anchor f6046418d15e2f44418dfbc04ca67999f389a7df, parent V13 7fb18cec3d6d6eebad5fe418ec83b36d82cfff1e. 최신 HEAD가 anchor 후손인지 확인하고 새 NCP 결과가 게시됐으면 중복 실행하지 않는다. AGENTS.md, v14/RESEARCH_DELIVERY_KO.md, SOURCE_DELTA.json, stages/C6_ENERGY_RECONSTRUCTION.json, RUN_V14.sh를 읽는다.

현재 실제 상태: Python57 PASS, 네 native 파일 복원 SHA 일치. native Rust 컴파일/시험/NCP는 NOT_RUN. 같은 대화의 이전 22/32개 테스트·NOT_PUSHED 기록은 과거 checkpoint다. 이번 branch에는 수정본과 실행기가 정상 파일로 게시되었다.

기존 인증으로 local repository를 fetch하되 active branch 변경/reset/clean을 하지 않는다. git archive를 이용해 세 형제 경로 research/lrs_atomic_native_bridge_20261016/{v12/native_owner,v13,v14}를 task input에 직접 추출한다. 기존 작업 dirty 파일은 보존한다. 다른 production clone/worktree를 새로 만들 필요는 없다.

NCP 접속:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22

Codex가 hostname/date/CPU/RAM/disk/load와 실행 프로세스를 조사하고, 위 input을 /root/REI_LRS_V14_<UTC>/input/ 아래에 직접 전송한다. 기존 production/R9/v3/rux checkpoint와 타 연구 프로세스는 수정·종료하지 않는다. input 안의 v12,v13,v14 형제관계를 유지한다. NCP에 Rust가 PATH에 없으면 /root/.cargo/bin을 추가한다.

먼저 별도 smoke output에서:
export CARGO_BUILD_JOBS=2
export V14_MAX_N=16
export V14_CELLS=8
export V14_NONLINEAR_TOL=1e-13
export V14_RUN_ROOT=/root/REI_LRS_V14_<UTC>/smoke
bash /root/REI_LRS_V14_<UTC>/input/v14/RUN_V14.sh

source reconstruction 네 파일, 표적 기존29+신규7 테스트 및 smoke 결과를 실제 출력으로 판정한다. 숫자를 예상 PASS로 바꾸지 않는다. cargo --offline --locked가 cache 부족으로 실패하면 cache/dependency 파일을 원본 lock 기준으로 회수하는 작은 환경 수정만 허용한다. source_hash/spec/model/rate를 바꾸지 않는다.

smoke 통과 후 다른 새 output에서 V14_MAX_N=256,V14_CELLS=16으로 같은 실행기를 호출한다. 두 구간 Xend=1e-5,1e-4; seven modes×six grids=84 histories,7056 macro rows. native CPU thread는 원본 설정을 유지한다. 1..4 cargo build jobs를 넘기지 않고 실제 서버 부하에 맞춰 줄인다.

분석기는 실제 birth GL2 위치, 양의 proper-time weight, source-off 주입 금지, 요청 grid 완결성, 전자/EOS·사건·binding·thermal·escaped radiation의 여섯 잔차를 독립 재구성한다. 이 판독기는 초기(.075,.12,.03),T0=15000K,Y=.2454/[4(1-.2454)]에 고정됐다. 새로운 초기조건을 임의로 넣지 않는다. source-off segmented controls는 GL2의 세분화 비용과 birth 효과를 구별하는 대조군이다.

common_combined 두 birth 행은 동일 midpoint에서 전체 source increment/2를 재구성한 기록이다. physical_gl2는 실제 두 기하에서 각각 주입한다. 이를 같은 물리시계로 취급하지 않는다. surviving photon energy 및 boundary photon number가 CSV에 없으므로 완전한 독립 photon energy residual을 만들어내지 않는다.

실패 시 최초 exit/stdout/stderr를 보존한다. 컴파일 경로·API visibility·type 호환의 작은 수정만 허용하고 diff를 기록한다. 반응률/source spectrum/허용오차/closure를 바꿔 통과시키지 않는다. 새 과학적 결정을 요구하는 문제는 해당 경로 HOLD, 안전한 부분 결과 백업으로 끝낸다.

각 완료단계마다 작업 소스·결과·DAG를 이 독립 branch에 commit/push하고 Draft PR에 범위를 기록한다. 원본 production에 merge하지 않는다. Google Drive REI_RESEARCH_BACKUPS/rei_bianchi/REI_LRS_V14_PHYSICAL_BIRTH_20261018/ 및 Dropbox bianchi/research_backups/rei_bianchi/에 create-only 결과 아카이브를 저장하고 각 원격 파일을 다시 읽어 SHA256을 확인한다. 실패한 한쪽을 완료라 하지 않는다.

최종 한국어 보고: 실제 host/time/compiler, 테스트수, 84이력 완결 여부, signed self-difference/차수와 floor, birth/source/species/thermal/binding/cooling/work, Newton residual, 비용, 실패·작은 수정, source commit/PR, 두 백업 SHA. full source-on p2는 관측된 수렴과 독립 근거 없이는 HOLD. Case B/full EoR/signed Bianchi/uniform stiff accuracy도 별도다.
