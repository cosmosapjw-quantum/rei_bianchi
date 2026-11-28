# 다음 HE 단위용 GitHub 조사

## 결과

EXFOR11 이후 완료된 HE 선행 단위 **QUARTIC12**를 발견했다. Source `research/he-quartic12-20261028`의 실제 ref는 `4c71acfa2b8721a0d0b8f9cec8814f75f1c55739`, tree는 `08e11c808d86cdf2a00ceb9feb3de43fc1bf3089`다. Commit 원문은 S10의 20개 산출물, local12/16 및 central28/88을 명시한다. Source 작성 시점 pending은 후속 실제 운송·중앙 게시와 구분한다. Root가 최신 source와 최종 패키지 원문을 별도로 복원·판정한다.

중앙 현재 ref `research/orchestration-sandbox-20261022`는 `7937ed4a842eb1ef6cec562a4224fb0add63d0d6`, tree `86f97b882caff8aa6022a97df185ee36a40da1ed`다. 부모는 인수인계에 있던 `8d6beee8724230f428211b105f9c3b1ec303c933`이며, commit 원문은 QUARTIC12 scoped return과 central28/88·HEdelta0을 명시한다.

## 실제 조사 범위

관련 7개 public repository의 branch 목록을 끝 페이지까지 실제로 읽었다. **1444 heads / 18 pages**이며 모든 마지막 페이지가 요청한100건보다 작아 해당 목록 종료를 확인했다. 이는 순차·병렬 page 요청으로 수집한 비원자적 스냅샷이다.

| 저장소 | heads | pages |
|---|---:|---:|
| BASS_HE | 114 | 2 |
| rei_bianchi | 283 | 3 |
| bass | 309 | 4 |
| bass_cr | 192 | 2 |
| WU088_HH | 159 | 2 |
| rec_bianchi | 163 | 2 |
| vigilode | 224 | 3 |
| 합계 | 1444 | 18 |

QUARTIC12 source에 보존된 이전 조사1438heads와 비교한 현재 총수의 차이는+6이다. 이전 전체 목록 바이트를 비교하지 않았으므로 added/deleted ref의 정확한 개수로 치환하지 않았다. Owner repository 목록은51개가 반환됐고, 별도 bianchi_phase_r/main1head를 관찰했다. 과제와 무관한 repository의 모든 branch/body를 조사했다고 표기하지 않는다. 전체 owner 원문에는 private repository metadata가 있어 공개 source payload에서 제외한다.

선택된 현재 계약·인계·결과 본문14개를 실제 읽었다. `SELECTED_READS.json`에 URL과 원시 응답 파일이 연결된다. 외부 unit의 검사 수는 owner 저장 결과이며 이 조사에서 과학·검사·CAS·plot을 재실행하지 않았다.

## 종합

| 소유자 / 실제 최신 조사 대상 | 관찰 결과 | HE 입력과 연결 |
|---|---|---|
| HE QUARTIC12 | S10 완료 source 발견,local12/16; 중앙 실제 다음 commit 발견 | 다음 연구의 선행 단위 갱신 |
| REI caloric branch | supplied 단조 piecewise-affine EOS inverse,6/6 검사와 independent PASS_SCOPED,기존 finite thermal20/20 reuse | 실제 EOS provider·recipient temperature·native25·physical radii null |
| REI source-bath addendum | source inert-He gas count 및 k_B T/eV convention,weighted-heat volume composition | 작성 시9/20를 이후 caloric 종료 상태와 구분;actual recipient bath null |
| CR pair support | 이론R1–R10/C1–C4 산출물 관찰,conditional4bin graph | 실제 graph/C/D/exclusive kernel/EOS null |
| CR energy-sum | 새 conditional E_a+E_b<=K support envelope 계약 | 실제K/kernel/C/D/outsidepartner/thermal state null |
| WU molecular R13 | R1/C1,2/20;science25/42;새 piecewise-affine nonaligned forcing | actualHDreactivearray 및 named consumer/density/clock INPUT_PENDING |
| REC thermal-path defect | saved313 reconstructed affine path의 component reference 계약 | physicalcoverage0/313,full defect/tube/radii null |
| BASS package integration | Python oracle integration PASS_SCOPED,science8/15 unchanged | 생산/nativeRust·독립모델심사 미완료;HE closure 입력 없음 |
| BASS anchored layer | 18/20,독립R6/C9NOT_RUN;동일재구성 조건부 경계 | actual error 측정false,physicalradii/global completion null |
| vigilode integrated polyalgorithm | exact-support 결과 및 prospective native coverage | native solver tests/benchmarks/profilesNOT_RUN,productionfalse |

BASS anchored-layer는 backup 조사자가 보고한2026-10-28T07:36:19Z 새 패키지에 대응하여 별도 최신 ref를 재확인했다. `research/bass-b3h-anchor-defect-20261028`는 `97a8c810e6e22c690c9e148b2bcc8313ca143d2e`이며 결과 파일에는20green methods/28primary/85reference,whole6.72651202785e-31m3 및 suffix6.71452244464e-31m3가 owner-reported로 저장돼 있다. 이 수치는 실제 물리 오차 측정값으로 승격하지 않았다.

현재 읽은 외부 자료에서 EXFOR event/inclusive normalization 및 liquid-He response, 실제 full angular/polarization law와 encounter flux/history, named birth/deposition/thermalization/global species binding을 해소하는 공급 입력은 관찰되지 않았다. Root가 제안한 TANGENT13의258MeV aperture tangent/dual certificate 후속 구성과 동일한 과학 단위도 선택된 계약에서 발견하지 못했다. 이 조사자는 새 tangent 방법을 유도하거나 구현하지 않아 후속 독립 R6/C9 검토의 비작성자 지위를 유지한다.

## 파일과 보존

- `CURRENT_BRANCH_CENSUS.json`: 공개 가능한7repo의 전branch/commit SHA 및 coverage.
- `SURVEY_GITHUB.json`: source identity,body별 판정,현재 조사 한계와 actions.
- `SELECTED_READS.json`: 실제 읽은14개 본문 위치.
- `*_pN.json`, `*_contract.json`, `*_handoff.json`, `*_result*.json`: 원시 응답.
- `inventory_51.json`: private metadata 포함 가능. 공개 source에 포함하지 않는다.

실제 remote mutation0,science0,test0,CAS0,plot0. 이전 완료 unit을 다시 실행하지 않았다. 최신 ref가 이후 변경되면 그 변경은 새 시점의 입력으로 확인한다.

