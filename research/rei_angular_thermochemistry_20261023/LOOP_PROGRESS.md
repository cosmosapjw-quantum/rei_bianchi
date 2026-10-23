# ANGTHERM01 단계별 진행·보존 기록

기준: physmath-research-loop intrinsic 1.0.0 / approved v0.2. 각 단계의 실제 내용으로 대응하며 번호를 새로 정의하지 않는다. 범위는 주어진 두 배경의 조건부 각도·열화학 유한 계다.

## 이론 R1–R10

| 단계 | 근거 | 상태 |
|---|---|---|
| R1 연구 위치·계약 | EXECUTION_CONTRACT.md, 기존 PR221/222 분기 관계 | 완료 |
| R2 근거·재사용 | inputs/source_indexes 두 조사 보고서, COPY_MANIFEST.json, vendor 원본 | 완료 |
| R3 주장·전제 정렬 | THEORY.md의 고정 배경·전자 동위원소 동일성·대칭·fit closure | 완료 |
| R4 가설·표현 탐색 | 21→9, 8방향→1그룹, optical-depth 좌표와 대조군 선택 | 완료 |
| R5 구성적 유도 | 고정 q 광자 사상, tensor·일, 사건별 보존, quotient와 Jacobian | 완료 |
| R6 독립 검증 | MATH_REVIEW.md, WOLFRAM_CHECK.md, 10개 algebra checks | 완료 |
| R7 판별 검증 | 10개 궤적과 같은 H/n의 방향/평균 적색편이 대조; Li threshold 해석 | 완료 |
| R8 결과 판정 | SCIENTIFIC_DECISION.md와 INDEPENDENT_REVIEW.md의 scoped PASS | 완료 |
| R9 정식 결과·코딩 연결 | REPORT_KO.md, THEORY.md, IMPLEMENTATION.md, RESULTS_OBSERVED.md | 완료 |
| R10 종료·재개 | HANDOFF_KO.md, DAG.json, 실제 commit/백업은 FINAL_DELIVERY.json | 과학 종료 완료; 전달 완료는 최종 receipt로 판정 |

## 코딩 C1–C10

| 단계 | 근거 | 상태 |
|---|---|---|
| C1 목표·baseline | PR221 73c5e00...와 exact donor pins; frozen tolerances | 완료 |
| C2 식–데이터–코드 | THEORY.md ↔ angular_model.py ↔ 원자 provider/배경 | 완료 |
| C3 수치 설계 | Radau, analytic J, threshold 분할, optical 좌표, 독립 full oracle | 완료 |
| C4 실행 DAG·자원 | finite cases/CPU·wall·메모리 계약, lower-tier 실행 분담 | 완료 |
| C5 구현 | code/ 및 보존된 입력에서 raw NPZ까지 | 완료 |
| C6 구현 검증 | pre-IVP checks, 빈 출력 구간·0-face·직렬화의 국소 수정 | 완료 |
| C7 과학 검증 | 사건 보존, 부호·기하·같은 배경 대조, raw-state 보존 확인 | 완료 |
| C8 수치·재현성 | full/tight 비교, M4/8/16, accepted nodes, 환경·명령·비용 | 완료; 연속 각도 오차 인증은 범위 밖 |
| C9 독립 검토 | 구현을 작성하지 않은 Astra의 INDEPENDENT_REVIEW.md | 완료, unresolved blocker 없음 |
| C10 판정·인계 | SCIENTIFIC_DECISION.md, REPRODUCE.md, HANDOFF_KO.md, FINAL_DELIVERY.json | 과학 판정 완료; 전달 완료는 최종 receipt로 판정 |

## DAG 순서와 단계별 보존 상태

| 체크포인트 | 완료 시점의 실질 산출물 | 보존/게시 근거 |
|---|---|---|
| S1 조사·출처·이론 계약 | remote 목록·읽은 소스·배경·정규화·식·유한 실행 계약 | PREPARED_DELIVERY.json: commit 00303ab..., Drive/Dropbox 8,014,567-byte archive 완료 |
| S2 구현·중간 계산 | 코드, 원래 실패, accepted-node continuation, 각 완료 궤적 | 각 구간 NPZ/JSON 및 batch 로그에 즉시 checkpoint; 기존 원자료 덮어쓰기 방지; 최종 archive에 모두 포함 |
| S3 10개 계산·검토·결과 | full/tight·angular·matched control, 7개 결과 그림, scoped admission | FINAL_RUN_RECEIPT.json 및 INDEPENDENT_REVIEW.md; 최종 과학 commit과 archive는 FINAL_DELIVERY.json |
| S4 전달 | 최종 소스·원자료·보고서·DAG·복사용 handoff | FINAL_DELIVERY.json에 원격 ref readback, Drive metadata, Dropbox completion 기록 |

각 연산마다 별도 원격 압축파일을 만들었다고 주장하지 않는다. S2의 매 계산 checkpoint는 로컬 원자료이며 S3/S4의 실제 게시·백업으로 전달한다. 준비 단계와 최종 단계의 원격 저장은 각각 별도 receipt로 확인한다.

## 완료율의 정의

과학 실행은 10/10개 완료, 허용 attempt는 중단 1개를 보수적으로 포함해 11/11개 사용했다. 이론·코딩 단계의 과학 의무는 완료했다. R10/C10의 전달 의무는 실제 최종 receipt가 complete일 때 완료로 해석한다. 전체 우주론 목표는 여러 열린 물리 closure를 포함하므로 이 10/10을 전체 연구 100%로 환산하지 않는다.
