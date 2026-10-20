# 연구·구현 단계와 현재 실행 경계

이 표는 PhysMath Research Loop1.3.0의 단계 정의에 맞춰 root 계약과 실제 산출물을 연결한다. R단계의 COMPLETE는 독립 이력 병렬화라는 이번 범위의 완료이며 새로운 일반 물리 정리나 전체 NCP backlog의 수용을 뜻하지 않는다. C5–C8은 lower-tier 구현·실행, R6/C9는 구현하지 않은 독립 Astra, 최종 판정·게시·provider 백업은 root 소관이다. 기존 전체 검증을 새 필수 gate로 추가하지 않는다.

## R1–R10

| 단계 | 이번 수행 내용 | 현재 상태·근거 |
|---|---|---|
| R1 연구 목표·계약 | 독립 이력 process 병렬화 한 가지 최적화, 새 물리·solver·rate cache0 | COMPLETE — ROOT_CONTRACT_KO.md, intake |
| R2 문헌조사·기존 성과 재사용 | 기존 native/solver/저장 raw·분석/외부 문헌을 회수하고 완료된19/N2/original84를 제외 | COMPLETE — intake_root/LITERATURE_KO.md, review_intake/BACKLOG_REVIEW.json |
| R3 주장·전제 정합성 | V12 photon-free/V13/current seeded-disabled의 서로 다른 모델·설정, 측정 경계, byte identity와 과학 동등성 구분 | COMPLETE — ROOT_CONTRACT, backlog intake review |
| R4 발산적 탐색 | profile 비용과 공유 build를 고려하고 수치 source 변경 없는 독립 이력 queue 선택 | COMPLETE_SCOPED — root 선택·profile3 actual receipt; 다른 optimizer 추가하지 않음 |
| R5 구성적 유도 | block-diagonal 독립성/Lie bracket, total-H electron identity, W/L bounds와 shared-build 민감도 유도 | COMPLETE_SCOPED — ROOT_CONTRACT, stage-A theory/WOLFRAM_SYMBOLIC.json 및 WOLFRAM_PHYSICS.json |
| R6 독립 검증·심사 | backlog·유도·가정의 독립 심사 및 최종 코드와 실제 raw의 독립 C9 연계 | COMPLETE_SCOPED — backlog review, review/INDEPENDENT_REVIEW.json; build64 bounded repair도 review/ROOT_REPAIR_ADDENDUM에서 PASS/residual blocking0 |
| R7 판별·경량 계산 | 기호 검산, actual profile3, 대표 native shard2와9serial/parallel casepairs 비교 | COMPLETE_SCOPED — theory/profile/native_validation/scheduler_native_validation; 전체 backlog NCP NOT_RUN |
| R8 과학적 결과 판정 | 내부 수치 순서를 유지하는 process scheduling, local 재현성과 비용 관측의 범위 판정 | COMPLETE_SCOPED — root 계약과 실행 근거; NCP64 scaling·새 physics admission 없음 |
| R9 정식화·계산 연결 | 정확한 selector/restore closure, 자원 pool/DAG/원래 순서 merge·분석으로 독립성 조건 연결 | COMPLETE — ROOT_CONTRACT와 실행 가능한 CLI/명시적 inputs/outputs |
| R10 연구 정리·체크포인트 | 현재 근거·한계·다음 유한 실행과 source-bound package 보존 | COMPLETE_SCOPED — source50파일 Git readback, 최종 archive·ACK 양쪽 full GET PASS; FINAL_PUBLICATION_ACK.json |

stage-A의 R1–R9 COMPLETE 기록은 이번 유도·intake 범위의 역사적 snapshot으로 보존한다. 이 표는 그 이후 실제 코드·경량 실행과 최종 검토를 덧붙인 현재 인계이며 stage-A 원문을 소급 수정하지 않는다.

## C1–C10

| 단계 | 이번 수행 내용 | 현재 상태·실제 근거 |
|---|---|---|
| C1 목표·기준 결과 | V12 144/V13 84/SSPRK3commands host 재현과 기존 기준 보존, 새 모델0 | COMPLETE — ROOT_CONTRACT, baseline source/pin/원본 example hash |
| C2 코드·수식·데이터 조사 | 기존 prepare/batch/profile/복원 chain, 원본 CSV·분석 경로/단위 확인 | COMPLETE — mechanical/source/runtime intake, 원본 hash inventory |
| C3 알고리즘·수치 설계 | history 내부 산술/순서 보존, selector-only 새 example과 typed output 비교 | COMPLETE — shards.py, selector reversal identity, source SHA; 새 tolerance0 |
| C4 DAG·병렬화 설계 | 246jobs/231native, exclusive CPU pool, memory admission, finite caps, resume/merge/receipt | COMPLETE — campaign.py/campaign_cli.py, ROOT_CONTRACT; 원격 실행 quota0/key absent 분리 |
| C5 구현 | source 복원→private build/test→backlog→exact merge→mechanical analysis의 한 명령 경로 | COMPLETE —12파일 구현; 현재 build64 repair manifest 참조 |
| C6 소프트웨어 검증 | 실제21tests PASS, native builds2성공/초기1실패 진단 후 private-target repair, build64 표적1test PASS | COMPLETE_SCOPED — validation/PYTHON_TEST_OUTCOME.json, native_validation, build64_repair/OUTCOME.json; 전체suite/native 반복 안함 |
| C7 물리·과학 검증 | V12/V13 같은 설정 대표 shard saved CSV576finite+24other 차이0, 기존3case의9non-timing pairs 차이0 | COMPLETE_SCOPED — SHARD_SAVED_OUTPUT_COMPARISON.json 및 scheduler raw; 전체 NCP backlog의 분석 수용은 PENDING |
| C8 정확도·성능 검증 | profile3, profile-off AB/BA/AB paired whole-phase, 실제 resume3reuse/native0, 자원 관측 | COMPLETE_SCOPED — local 중앙 ratio2.199360426; NCP64 가속/RSS감소/일반 solver속도 주장은 미발행 |
| C9 독립 코드 심사 | restore closure/dependent reuse/V12 reference findings CLOSED, blocking0 | PASS_SCOPED_RESOURCE_AWARE_ORCHESTRATION — review 원문; build64 repair 동일episode addendum PASS/residual blocking0 |
| C10 배포 판정·실행 인계 | 검증된 구현, 실행문·반환계약·남은 NCP 작업 전달 | COMPLETE_SCOPED — source commit/dual-provider archive·ACK full GET PASS; 최종 metadata는 enclosing commit |

## 실행과 보존의 별도 DAG

현재 구현은 source prepare3→build3→targeted-test3를 variant 순서로 수행하고, 그 뒤 독립 backlog231개를 자원 제한 queue에 배정한다. V12/V13 원래 key/step 순서 병합3건이 exact coverage를 통과한 뒤 분석3건이 수행된다. 실패·cap·admission 부족은 dependent 상태로 전파하고 과거 attempt를 보존한다.

게시·백업은 root의 실제 receipt로만 닫는다. 새 최종 publication commit=`d234243a79e4e8e611aaf4ac61949c5ef9111468`, 새 archive/Drive/Dropbox/dual-full-GET/ACK=`ARCHIVE_AND_ACK_DUAL_FULL_GET_PASS — FINAL_PUBLICATION_ACK.json`다. 실행·과학 승인·보존 완료는 서로 다른 상태다. 실제 전체 backlog NCP는 현재 NOT_RUN이며 이 표의 로컬 COMPLETE로 대체하지 않는다.

일반2차 source-on/uniform stiff/일반 양수성/Case B/full EoR/signed Bianchi/넓은 positive-CMB·비영 boundary/global certificate/완전 photon ledger는 기존 HOLD다. production은 NOT_ISSUED다.

## 최종 게시·백업 identity

- 구현·결과 source commit: `d234243a79e4e8e611aaf4ac61949c5ef9111468`. 최종 metadata HEAD는 이 파일을 포함하는 commit이다.
- Archive: `REI_LRS_PARALLEL_C10_20261020.tar.xz`, 7,654,920bytes, SHA256 `388ef80e25fef7905e44fcc1aaf6179c6332b41fdf7c7e07233f51b805e608ac`. Drive `1yK1fsc_-ybJ59l8VYDvIARrpZtTIWbc5`, Dropbox `id:BSpOijBcT10AAAAAAD_aKw`.
- ACK: `REI_LRS_PARALLEL_C10_ACK_20261020.json`, 6,391bytes, SHA256 `05c4bd684818cbc65b89a3f4091cdfb0c87a6902117ea954d0ded60f1774539e`. Drive `19mpts1yDKBtp02K6qOpG9C_dolyfDt4H`, Dropbox `id:BSpOijBcT10AAAAAAD_aLQ`.
- Archive와 ACK 각각 양쪽 전체 GET/bytes/SHA256 일치. Archive343 regular files/manifest342개+self1개 PASS. Drive origin HTTP NOT_EXPOSED/materialization200, Dropbox HTTP200, 실제 회수 process exit0.
- archive는 기존 검증된 dependency/base 위에 repo_payload를 overlay하는 delta이며 단독 복원본이 아니다. 포장 시점 PENDING은 별도 ACK와 FINAL_PUBLICATION_ACK.json이 닫는다.
- 실제 source524의 NCP19/borrowedN2/originalV14 84 완료를 유지한다. 이번 V12/V13/SSPRK backlog는 NOT_RUN_BLOCKED_EXECUTION_ACCESS다.
