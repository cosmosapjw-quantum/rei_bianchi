# 독립 LRS: 64-core NCP backlog를 위한 이력 병렬화

## 결과와 범위

이번 최적화는 여러 독립 이력을 자원 제한 queue에서 실행하는 것이다. V12/V13의 이력 내부 산술과 원래 SSPRK2 명령을 보존한 채, 준비·컴파일을 variant당 한 번 수행하고 native 작업을 최대64개 CPU slot에 배정한다. 기존 branch의 한 연구 경로로 구현했으며 별도 수치 optimizer나 rate cache를 만들지 않았다.

실제 샌드박스에서 대표 V12/V13 shard 두 개가 저장된 같은 설정의 출력과 일치했고, 기존 current Radau binary의18개 직렬·병렬 실행도 모두 완료됐다. 3-worker 전체 phase의 직렬/병렬 시간비 중앙값은 **2.199360426**이다. 이 값은 이 호스트의 세 기존 이력에 관한 관측이다. NCP64 scaling, compiler 가속, 개별 RHS 가속, RSS 감소를 입증하지 않는다.

새 NCP backlog 실행은 **NOT_RUN / BLOCKED_EXECUTION_ACCESS**다. 실제 원격 도구의 quota0과 지정 SSH key 부재를 관측했다. 사용자에게 수동 SSH/SCP나 파일 다운로드를 요구하지 않는다. 기존 source524 NCP19와 borrowed N2, 원본 V14 NCP84는 이미 완료된 과거 근거로 유지한다.

## 새 결과 확인과 실제 미실행 범위

PR198, 현재 branch와13개 research/rei-lrs branch head, 선택한 과거 handoff/receipt59개를 읽었다. PR의 intake HEAD는96aaad584bbecded34485526a4bb53a49708ffc6였다. 다른 대화 검색은 실제 성공 반환을 받았지만 검색 snippet을 모든 대화 원문이나 raw 회수로 표현하지 않았다. Google Drive는 관측한38개 하위 folder를 방문하는39회 목록 조회, Dropbox는 지정 folder의 재귀 목록을 확인했다. 그 범위에서 이미 승인한 현재 source의 NCP 반환 이후 새 실행 receipt는 발견하지 못했다. Drive API는 전역 완전성을 노출하지 않았으며, tree/listing만 본 파일은 본문을 읽은 파일로 세지 않았다. 정확한 범위는 intake/INTAKE_SUMMARY.json과 intake/BACKLOG_REVIEW.json에 있다.

과거 V6→V7, V7→V8_native, V9→V10의 실제 NCP 반환은 오래된 NOT_RUN을 닫는다. 현재 실행 source는5248822167e3fbe374f4333f7f2efdcdbfdaeeaf, VigilODE pin은8a8bd409b1d96c7b7421f496d229e119fd3d284e다. 이번 대표 Radau 실행은 기존 NCP binary c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992를 사용했다.

| 남은 NCP 호스트 재현 | 고정된 기존 설정 | 처리 단위 |
|---|---|---:|
| V12 thermal clocks | 3cases×8modes×6N, cells8 | 144이력 |
| V13 source-on average clocks | 2X×7modes×6N, cells32, tol1e-15 | 84이력 |
| SSPRK2 native diagnostics | 원래 transport/fixed/birth 명령 | 52transport행+16coupled이력 |

전체 계획은 **246 jobs**다. 준비3, build3, 표적시험3, native명령231, merge3, analysis3으로 구성된다. native231명령은 V12/V13의228이력과 SSPRK2의 원래3명령이며, SSPRK2 coupled의6+10이력은 각 명령 안에서 원래대로 실행된다. 새 과학 모델 수는0이다. source524의19설정·borrowedN2·원본 V1484를 이 backlog에 다시 넣지 않았다.

## R5–R7: 물리적 독립성과 시간 경계

각 이력 j의 방정식을 dy_j/dτ_j=F_j(τ_j,y_j;θ_j)로 두고 시간좌표도 해당 이력의 상태 block에 포함한다. 초기조건·불변 입력θ_j가 고정되고 서로 다른 이력 사이에 공유 mutable state가 없으면, 서로 다른 block의 vector field는 상대 block을 미분할 때0이므로 Lie bracket이0이다. 따라서 각 이력을 다른 CPU에서 처리해도 그 이력의 내부 수치 연산 순서는 바뀌지 않는다. 이 명제는 이력 사이의 병렬성에 한정되며, 한 LRS 상태 안의 전역 Jacobian이 block diagonal이라는 주장이 아니다.

total-H 정규화는 다음을 유지한다.

\[
Y=\frac{0.2454}{4(1-0.2454)}=\frac{1227}{15092},\qquad
e=x+Y(y+2z),\qquad
\dot e=\dot x+Y(\dot y+2\dot z).
\]

V12 CSV의 HeII_per_H와HeIII_per_H에는Y가 이미 들어 있으므로 해당 CSV의 electron 진단은 HII_per_H+HeII_per_H+2HeIII_per_H다. 두 정규화를 중복 적용하지 않았다. 원시 P/C/R/D, binding, heat, cooling, escape, CMB, work는 원래 열과 파일 범위대로 유지한다.

동시에 ready인 독립 작업의 고정 실행시간을t_j>0, W=Σt_j, L=max t_j라 하고 동일한worker p개가 work-conserving list scheduling을 수행한다고 이상화하면

\[
\max(W/p,L)\le T_p\le W/p+(1-1/p)L.
\]

마지막 완료 작업이s에서 시작하고 길이가t라면 시작 전 worker가 모두 바빴으므로 ps≤W−t, 따라서T_p=s+t≤W/p+(1−1/p)t≤W/p+(1−1/p)L이다. 이는 고정된 작업시간과 무시한 scheduling overhead 아래의 경계다. source hash 계산·process launch·CSV병합·메모리대기·compile을 포함한 실제 wall 보장이 아니다.

공통 준비·빌드시간B까지 포함한 속도비는 S=(B+W)/(B+T_p)이고

\[
\frac{dS}{dB}=\frac{T_p-W}{(B+T_p)^2}.
\]

T_p<W일 때 공통 준비비용이 클수록 전체 속도비가1에 가까워진다. 이전 NCP compile345.147809466초와 raw 내부19설정의 시간합4.937230308초는 측정 경계가 다르며 그 비를 speedup으로 사용하지 않는다.

Exa로 Cargo 공식 build.jobs/--jobs와 --timings, Python 공식 subprocess/affinity 관련 문서를 실제 검색·회수했다. SciSpace는 독립작업 list scheduling에 관한 실제 검색을 수행했으며 abstract 검색을 원문 전체 검토로 바꾸어 표현하지 않았다. Graham1966 원문과1969 publisher bibliographic record의 읽기 범위를 구분한다. Wolfram은 정규화, 비용식·미분, 독립 block의 bracket을 실제 계산했다. 첫 symbolic 반환의 undefined-symbol 경고도 보존했다. 상세 URL과 읽기 범위는 theory/LITERATURE_KO.md 및 원시 Wolfram JSON에 있다.

## 구현과 실행 계약

V12/V13 원본 example의 SHA256을 확인하고 새 이름의 selector-only 사본을 생성한다. 원본 파일과 history body/step/CSV schema는 그대로다. 모든 selector는 CSV 생성 전에 유효성을 검사한다. V13의 while-loop skip은N을 증가시키고 진행한다. 삽입을 제거하면 원문 전체 bytes가 복원됨을 실제 확인했다.

정상 V13 RESTORE_NATIVE.py와 SSPRK restore_ssprk2_native.py의 복원 chain을 사용한다. current Radau prepare_and_run.py에는 양수 build-jobs(default1), build-only, 명시적인 focused-test 옵션과 CARGO_TARGET_DIR 정리만 추가했다. 기본 legacy, 현재 성능 경로 cell-cache, borrowed의 opt-in 실험 상태는 유지한다.

최대64 native worker와 Cargo build jobs64를 요청할 수 있다. 실제 admission은 allowed affinity·cgroup CPU quota·host MemAvailable·cgroup 가용 추정·사용자 상한으로 제한한다. nominal memory는 native process당512MiB, compiler slot당1GiB이며 측정 peak RSS가 아니다.20%여유를 유지하고 cgroup 회수 가능 추정에는 실제 관측한 inactive_file만 더한다. 64-slot 빌드는64GiB nominal reservation이므로 실제 한도가 부족하면 명시적으로 미실행 상태를 남긴다. 64는 동시성 상한이며64개 core가 모든 순간 바쁘거나64배 빨라진다는 약속이 아니다.

각 variant의 Cargo target을 분리한다. 각 native process에는 겹치지 않는CPU slot과 threads1 환경을 부여한다. 준비/build/test가 끝난 뒤 native queue를 실행하며, timeout은 해당 child process group만 종료한다. V12 aggregate180초, V13 X별180초, SSPRK aggregate300초 및 개별60/180/180초를 적용하고 실제 polling/정리 overshoot도 기록한다.

Resume는 manifest/source/input/executable와 검증된 완료 출력·log identity가 같을 때만 결과를 재사용한다. 복원 script/spec/payload가 바뀌면 과거 completed dependent도 현재 DAG에서 blocked로 표시한다. 실패·부분 결과는 새 attempt와 함께 보존한다. CSV merge는 정확한 key집합·step1..N·header·원래 순서를 검사한다.

V12는 stdlib coverage와 원래 진단·정규화 관측값을 정리하고 과거 reference analysis를 연결한다. SciPy/numpy의 reference3 IVP를 강제로 재적분하지 않는다. V13의 원래 stdlib analyzer와 SSPRK Decimal audit는 NCP 전체 결과에 적용할 준비가 됐다. SSPRK alias는 원본 bytes를 보존하며 audit의 과거 reviewer 문자열을 새 독립 검토로 인정하지 않는다.

## 실제 경량 검증

V12 release build exit0는11.700944882초였다. V13의 처음 공유 target build는exit101,0.114367888초였으며, 동일 source를 전용 target에서 재시도하여exit0,12.105879507초로 완료했다. 세 시도의 합23.921192277초이고 실패 원문을 보존했다. 이는 실제 호환 문제를 해결한 기록이며 native식이나 허용오차 변경이 아니다.

대표 shard는 V12 D1_X1E5/owner_like_be/N8/cells8과 V13 X1e-4/be_control/N8/cells32/tol1e-15를 실행했다. 각8행이며 원래 saved CSV와 비교한 유한 숫자344+232=576개, 기타16+8=24개에서 차이가 없었다. elapsed_wall_s/wall_s만 제외했고 dt_s는 포함했다. V13의 다른 cells8 자료를 cells32의 같은 설정으로 비교하지 않았다.

기존 c93db binary의 fixed/birth/disabled RadauN16을 profile-off, cell-cache로3쌍 AB/BA/AB 실행했다. 총18회 모두exit0이고 독립 reviewer가9쌍의 raw를 직접 읽어 유한 숫자463,323개·기타72개·container35,619개에 차이0을 확인했다. signed-zero bitwise 검증 주장은 아니다.

| Pair | 직렬 전체phase초 | 병렬 전체phase초 | 직렬/병렬 |
|---|---:|---:|---:|
| AB | 1.656947672 | 0.753377051 | 2.199360426 |
| BA | 1.618014477 | 0.702647920 | 2.302738585 |
| AB | 1.666196855 | 0.775281123 | 2.149151844 |

시간 경계는 input hashing과 receipt를 포함한 동일한 scheduler phase다. serial CPU0, parallel CPU0/1/2이며 이 sandbox의 allowed affinity9/cgroup CPUquota8 안이다.18회 charged process wall합9.626661057초는 승인한60초 cap 안이다. 실제 resume는3개 완료 결과를 재사용했고 추가 native launch는0이었다.

별도 profile-on3개는 비용 위치 확인용이며 위 시간비에 섞지 않았다. profile3+대표shard2+paired18=실제 native23회다. 새 unique 모델은0이다.17개 신규process시험과4개 원래 runner회귀, 총21개가 실제PASS했다. 이후 root가 발견한 불필요한 buildjobs4 상한을64로 교정한 경로는 별도의 한 표적시험으로 검증했다. 전체suite/native를 다시 실행하지 않았다.

## 독립 검토와 승인 경계

Root Astra 계약→lower-tier 구현·실행→구현하지 않은 Astra 독립검토의 실제 위임을 수행했다. C9/R6는 PASS_SCOPED_RESOURCE_AWARE_ORCHESTRATION이며 복원 identity누락과V12reference경로를 같은 episode에서 수정·확인했다. Root의64-core 상한 교정도 같은 episode의 한 addendum으로 닫았다. 기존21tests/23native의 근거와 최종 administrative CLI repair를 구분한다.

source-on 일반2차, uniform stiff, 일반 양수성, CaseB/fullEoR/signedBianchi, 넓은 positive-CMB·비영 boundary, continuous global certificate는 HOLD다. 해당 CSV가 제공하지 않는 photon energy·boundary photon number의 완전한 독립 회계나 production admission은 주장하지 않는다. GL2 선형 약4차를 일반 비선형/native4차로 확장하지 않는다. borrowed의 속도와 peak-memory 감소는 여전히 NOT_ESTABLISHED다. repository CI의 과거 cargo fmt실패/test skipped는 이 scoped native/process PASS와 별개다.

## 게시·백업과 다음 실행

단계 A 계약/intake/profile은 commit2a8656afd0a077da00d3335a95899cedcf824dae에 게시했고8개파일의 전체 Git readback이 일치했다.414,044byte archive의 SHA256은27b4df0144d64e8e7d572ea4b5fc393e67d92e6856e26cbd0615634d79a39943이다. Drive1ZW_rhUXIzk06tn88GmTxhm2LKyQkTsI-, Dropboxid:BSpOijBcT10AAAAAAD_aKg에서 각 전체 파일을 회수해48개members와manifest까지 일치했다. Drive origin HTTP는 connector가 노출하지 않았고 materialization HTTP200, Dropbox HTTP200이었다.

최종 source/results와 C10 archive·별도 ACK의 실제 commit/ID/bytes/hash는 FINAL_DELIVERY.json, FINAL_PUBLICATION_ACK.json 및 DAG_FINAL.json이 기록한다. archive내 문서는 포장 시점 상태이며 이후 원격회수 완료는 별도 ACK와 최종Git문서로 닫는다. 기존 저장소·dirty상태를 보존하며 force/reset/clean이나 불필요한 clone/worktree는 수행하지 않았다.

접근 가능한 NCP에서 CODEX_NCP_EXECUTE_KO.md의 한 명령을 실행하면 정상복원→variant별컴파일→기존표적시험→228shards+SSPRK3명령→병합·분석을 이어간다. 완료된19/N2/원본84는 재실행하지 않는다. 다음 대화는 NEXT_THREAD_PROMPT_KO.md대로 새 실행receipt부터 확인한다.

현재 source 게시 commit의 CI는 2026-10-20 22:42:57UTC에 단 한 번 읽었다. push/PR verify 두 job은 당시 in_progress였고 fmt/test 결과는 관측하지 못했다. 과거 source524의 fmt 실패/test skipped와 구분하며 전체 CI green을 주장하지 않는다. CURRENT_SOURCE_CI.json과 원시응답을 보존했다.

## 최종 게시·백업 identity

- 구현·결과 source commit: `d234243a79e4e8e611aaf4ac61949c5ef9111468`. 최종 metadata HEAD는 이 파일을 포함하는 commit이다.
- Archive: `REI_LRS_PARALLEL_C10_20261020.tar.xz`, 7,654,920bytes, SHA256 `388ef80e25fef7905e44fcc1aaf6179c6332b41fdf7c7e07233f51b805e608ac`. Drive `1yK1fsc_-ybJ59l8VYDvIARrpZtTIWbc5`, Dropbox `id:BSpOijBcT10AAAAAAD_aKw`.
- ACK: `REI_LRS_PARALLEL_C10_ACK_20261020.json`, 6,391bytes, SHA256 `05c4bd684818cbc65b89a3f4091cdfb0c87a6902117ea954d0ded60f1774539e`. Drive `19mpts1yDKBtp02K6qOpG9C_dolyfDt4H`, Dropbox `id:BSpOijBcT10AAAAAAD_aLQ`.
- Archive와 ACK 각각 양쪽 전체 GET/bytes/SHA256 일치. Archive343 regular files/manifest342개+self1개 PASS. Drive origin HTTP NOT_EXPOSED/materialization200, Dropbox HTTP200, 실제 회수 process exit0.
- archive는 기존 검증된 dependency/base 위에 repo_payload를 overlay하는 delta이며 단독 복원본이 아니다. 포장 시점 PENDING은 별도 ACK와 FINAL_PUBLICATION_ACK.json이 닫는다.
- 실제 source524의 NCP19/borrowedN2/originalV14 84 완료를 유지한다. 이번 V12/V13/SSPRK backlog는 NOT_RUN_BLOCKED_EXECUTION_ACCESS다.
