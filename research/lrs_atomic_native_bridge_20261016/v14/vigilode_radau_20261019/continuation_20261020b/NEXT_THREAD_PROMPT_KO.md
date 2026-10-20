# 새 대화: rei_bianchi 독립 LRS borrowed-cell C10 이어가기

나는 이론물리·우주론 연구자다. $physmath-research-loop로 실제 유도와 경량 샌드박스 코딩 연구를 이어라. 가능한 코드 수정은 완성해 기존 branch에 push하고, NCP에는 컴파일·작은 호환 수정·실제 실행만 남겨라. 단계별 게시·Drive/Dropbox 백업·DAG를 기록하라. 사용자에게 다운로드나 수동 SSH/SCP를 요구하지 말라. 독립 LRS와 production v3/rux 및 BASS/rec/RUN19 등 다른 연구 경로를 구분한다.

## 첫 행동: 새 실행 증거

다른 대화의 반환 기록, PR198과 관련 branch/repo, Google Drive REI_RESEARCH_BACKUPS/rei_bianchi/ 및 Dropbox /bianchi/research_backups/rei_bianchi/에서 새 실행 결과부터 확인하라. source SHA, command, stdout/stderr, exit code, raw 결과를 실제로 읽고 새 결과가 있으면 우선 분석한다. 검색 오류·404·목록만 확보한 범위를 성공한 전체 검색으로 꾸미지 말라.

Repository: cosmosapjw-quantum/rei_bianchi
PR: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/198
Branch: research/rei-lrs-v14-physical-birth-20261018
검증·게시된 실행 source: 5248822167e3fbe374f4333f7f2efdcdbfdaeeaf
이전 cache source: 33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1
직전 전달 HEAD: 70a9ff3f2437101a1df13054dcb10f8106741b26
C1–C4 checkpoint commit: d2d9ed9fa9f339448f2a6c3ba35d56c6d75280cb
VigilODE pin: 8a8bd409b1d96c7b7421f496d229e119fd3d284e
최종 전달 metadata commit은 이 파일을 담은 Git commit 또는 PR198의 후속 HEAD에서 확인한다. 실행 source SHA와 metadata HEAD를 구분하라.

먼저 research/lrs_atomic_native_bridge_20261016/v14/의 RESEARCH_DELIVERY_KO.md, SOURCE_DELTA.json, stages/FINAL_DELIVERY.json, CODEX_NCP_EXECUTE_KO.md를 읽어라. 최신 상세 기록은 같은 v14 아래 vigilode_radau_20261019/continuation_20261020b/의 RESEARCH_REPORT_KO.md, ROOT_ADMISSION.json, SOURCE_DELTA.json, FINAL_DELIVERY.json, FINAL_PUBLICATION_ACK.json, DAG_FINAL.json, CODEX_NCP_EXECUTE_KO.md다.

## 완료된 연구와 판정

NativeCellCache가 cached RHS마다 하던 상태 clone과 준비된 node clone/flatten을 제거하는 opt-in cell-borrowed를 구현했다. owned/borrowed 경로가 원본 native-rate 산술 helper를 공유한다. immutable cache/state borrow와 변경 셀 PreparedCell 하나를 사용하며, cell/node/species/compensated_sum 순서 및 diagnostics·오류 순서를 유지한다.

원본 native 152개 파일의 기존 바이트와 기존 append hook, VigilODE 477개 source, Cargo pin/lock, provider/EOS/FD/허용오차/GL2 birth/default/transaction을 유지했다. default는 legacy, 성능 목적의 기존 경로는 cell-cache다. batch도 그대로 cell-cache다. borrowed를 가속 기본값으로 승격하지 말라.

v1 external-for와 한 번 승인된 v2 for_each를 실제 compile/test/run했다. v2가 최종 명시적 실험 옵션이다.

- 버전마다 release build exit 0, Rust 4 unit + 6 integration = 10 PASS.
- 기존 19설정(10 Radau + 9 SSPRK 대조)을 각 버전에서 재현했다. 새로운 과학 문제 19개로 세지 않는다.
- 구현하지 않은 독립 Astra reviewer가 버전당 raw 60개에서 공유 숫자 2,272,828개·기타 360개·container 174,120개를 읽었다. 차이 0, metadata 문제 0. signed-zero bitwise 검증은 아니다.
- 정상 prepare-only와 compiled source의 native 153 / adapter 7 / VigilODE 477 일치. 정상 runner의 run_cases에서 실제 borrowed fixed RadauN2 전달 smoke PASS. Python runner 4 PASS는 v2 source 불변으로 재사용했다. 전체 runner main --all을 샌드박스에서 한 번에 새로 실행했다고 쓰지 말라.
- fixed RadauN16에서 RHS 2,992, occupied-cell preparations 14,720, node visits 1,914,880은 같다. 지정 cached state/node clones만 2,704 / 1,730,560에서 0 / 0으로 줄었다.
- v1의 median paired native cache/borrowed 시간비: fixed 0.760293, birth 1.030526, disabled 0.979692.
- v2의 같은 시간비: fixed 0.932206, birth 0.980651, disabled 0.879171. 모드별 5 AB/BA pairs, CPU0, profile-off였다. 1 미만이면 borrowed가 느리다.
- 가속 및 peak-memory 감소는 NOT_ESTABLISHED. 지정 clone 계수 0은 zero allocation이나 RSS 감소를 뜻하지 않는다.
- 두 버전의 관측 case subprocess wall 합계 53.148715초. 실패·부정적 성능 결과·원시 자료·소스·binary를 보존했다. 선택적 변형/시험 반복을 새 의무로 만들지 말라.

최종 v2 binary SHA256:
3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a

C9: PASS_SCOPED_EXPERIMENTAL_IMPLEMENTATION.
Root: ADMIT_SCOPED_EXPERIMENTAL_EQUIVALENCE_AND_NAMED_CLONE_ELIMINATION.
DAG: R1–R10 및 C1–C10 완료. 현재 source의 NCP는 NOT_RUN, production은 NOT_ISSUED다.

PR198의 과거 여섯 CI job은 기존 15개 native workspace 파일의 동일 cargo fmt 실패였고 test는 skipped였다. 새 source 524882의 두 run39385516271/39385511196도 cargo fmt 단계 실패·test skipped를 실제 확인했다. CURRENT_SOURCE_CI.json을 읽고 샌드박스 adapter PASS와 혼동하지 말라.

## 검증된 최종 백업

새 delta: REI_LRS_BORROWED_C10_20261020B.tar.xz
7,540,740 bytes
SHA256: 492681e5ed7f1f53820b3bdcf24f397cfedbb6dac20a1d6dd917c7a9e2aa866e
Drive ID: 1Dxj_adZQR4QEuxxatozwG10AMtvQw0z5
Dropbox ID: id:BSpOijBcT10AAAAAAD_SWQ
Dropbox path: /bianchi/research_backups/rei_bianchi/REI_LRS_BORROWED_C10_20261020B.tar.xz
양쪽 전체 GET: HTTP 200, exit 0, 동일 크기·SHA256. 로컬 압축본의 payload 1,153개 manifest 검사 PASS. 원격 회수본으로 native 시험을 추가 실행한 것은 아니다.

별도 ACK: REI_LRS_BORROWED_C10_ACK_20261020B.json
4,461 bytes
SHA256: bf9c95b76ea6a71d501f7da36e1d81adae771d69748ef7067aa7508713502183
Drive ID: 1APxc9ecMbXErRuLkF7_9cYUGmwZX--aH
Dropbox ID: id:BSpOijBcT10AAAAAAD_SWw
양쪽 전체 GET/SHA256 일치. archive 내부 문서는 포장 전 상태다. 최종 원격 readback은 이 sidecar와 최종 Git metadata로 닫혔다.

Delta는 아래 base 위에 새 repo_payload를 overlay하는 구조이며 단독 복원본이 아니다.
Base: REI_LRS_OPTIMIZATION_C10_20261020.tar.gz
53,269,577 bytes
SHA256: 623797d7a8b83b078f10ffaad780c7b2c223247e8b5593110c8d5f52286991b0
Drive ID: 1TV56tJoJXkK4XyFTXTrnTgCtfDDOTJzT
Dropbox ID: id:BSpOijBcT10AAAAAAD_SPg
기존 base의 양쪽 전체 GET와 payload 5,462개 검증 근거는 재사용한다.

C1–C4 중간 백업도 양쪽 전체 GET/SHA256 일치:
REI_LRS_BORROWED_C1_C4_20261020B.tar.gz, 2,935,762 bytes
SHA256: 0763a61ff9a3497313751114fdaf546c2fc4023bc80938168668f6bb36c3a5e4
Drive ID: 1FITnoSg6WW1GOnJiJQhDxAn8Vc2u4UB1
Dropbox ID: id:BSpOijBcT10AAAAAAD_SUg

## 다음 유한 작업

현재 source 및 이전 cache optimization의 새 NCP 실행은 이 대화에서 NOT_RUN이었다. 과거 d87ba9ca25acb8a2a032154fa23057b45acd6207의 NCP 19설정 완료는 별도 과거 증거다. 초기 인계의 오래된 V14 NOT_RUN 문구를 현재 상태로 되돌리지 말라. 과거 84이력도 새 미완료 작업으로 되살리지 말라.

새 결과가 없으면 CODEX_NCP_EXECUTE_KO.md의 정상 Git source와 prepare_and_run.py로 현재 source의 cell-cache compile → 표적시험 10개 → 기존 19설정 실제 NCP 실행을 우선하고, 동일 binary의 borrowed fixed RadauN2 하나로 호환성을 확인하라. env -u CARGO_TARGET_DIR를 유지해 runner의 binary 경로와 외부 Cargo target override를 일치시킨다. 실제 compiler·host·source/binary SHA·stdout/stderr·exit·raw를 게시·백업하라.

사용자 지정 연결:
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22

이 대화 샌드박스에는 해당 key가 없었다. 허가된 인증/원격 실행 수단이 없으면 실행했다고 꾸미지 말고 원인을 기록한다. 기존 checkout과 dirty 상태를 보존하며 새 clone/worktree/reset/clean을 만들지 않는다.

후속 최적화는 실제 profile이 필요성을 보일 때 하나만 고른다. rate/scratch Vec 6개 재사용 또는 정확한 T-bit 조건의 RUN19 coefficient cache는 아직 구현·채택한 결과가 아니다. VigilODE PR77의 reaction–diffusion/localAD 증거를 LRS 전역 미분·성능 증거로 옮기지 말라. Exa의 공식 Rust 문서와 Wolfram 기호계산은 실제 사용했고, SciSpace는 이전 실제 검색·1차 원문을 재사용했다.

## 과학적 범위와 작업 규칙

total-H 기준, e=x+Y(y+2z), Y=.2454/[4(1-.2454)]를 유지한다. 원시 P/C/R/D 사건과 binding/heat/cooling/escape/CMB/work를 분리한다. 제조 76개(선형54·비선형16·강성6), Python57, 과거84 및 기존19설정을 새 연구로 재집계하지 않는다. 선형 GL2 약4차를 일반 비선형/native4차로 확장하지 않는다.

source-on 일반2차, uniform stiff, 일반 양수성, CaseB/fullEoR/signed Bianchi, positive-CMB/비영 boundary의 넓은 범위, continuous global certificate는 HOLD다. CSV에 없는 photon energy와 boundary photon number의 완전한 독립 회계나 production admission을 주장하지 말라.

현재 AGENTS의 tiered scientific delegation을 따른다: Astra 계약/판정 → lower-tier 구현/실행 → 구현하지 않은 Astra 독립 검토. 실제 독립 agent가 없으면 수행한 것으로 꾸미지 말라. 완료된 경량 검증을 의무적으로 반복하거나 toy/메타 감사만 늘리지 말고 새 NCP 실행 결과를 우선한다.
