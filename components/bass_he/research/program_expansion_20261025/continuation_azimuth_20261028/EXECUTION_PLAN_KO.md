# R4/C4 — 판별 설계와 한정 실행 DAG

선택 알고리즘은 exact rational sector endpoint sweep이다. 전체2D cell grid는 같은 Boolean law를 확인하는 독립 manufactured oracle에 한정하고, Monte Carlo와 φ quadrature는 사용하지 않는다. 각 strip의 상수 mask→polar SetBounds→Bernstein integral→event/count/ratio 순서가 실제 계산 DAG다. fullazimuth→finiteazimuth의 변화만 새 검증한다.

## 단계 계약

| 단계 | 이론 산출물 | 코딩 산출물 | 게시/backup 위치 |
|---|---|---|---|
| S01 | R1 연구 범위 | C1 baseline/수용기준 | CONTRACT,DAG,LOOP |
| S02 | R2 source 재사용 | C2 식–코드 대응 | EVIDENCE_REUSE,preflight,EQUATION_CODE_MAP |
| S03 | R3 정의·전제 | C3 exactstrip/오차 설계 | THEORY,CODING_CONTRACT |
| S04 | R4 세 후보/표현 선택 | C4 자원·독립 분담 | EXECUTION_PLAN,precontractreview |
| S05 | R5 포함·대칭·ratio 유도 | C5 구현/독립정적검토 | source/tests/scripts,INPUTS,staticreview |
| S06 | R6 독립 확인 | C6 새 suite 실제검증 | 원로그/receipt/저장plot입력 |
| S07 | R7 Wolfram/판별예 | C7 physics 연결 | 상징결과/검증해석 |
| S08 | R8 과학·resource 판단 | C8 saved-onlyplot/수치근거 | 실제그림/receipt/해석 |
| S09 | R9 정식 범위 | C9 같은pass 실제결과검토 | RESULT,finalreview,DAG |
| S10 | R10 종료·재개 | C10 정확source/인계 | presnapshot,실제외부ACK는별도 |

각 S의 실제 source commit/tree 및 Drive·Dropbox ACK는 `/workspace/scratch/d444793afb2b/he09_checkpoints/Sxx_ACK.json`에 저장한다. Git 문서의 stage 완료는 그 work product를 뜻하며 아직 받지 않은 외부 ACK를 선행 주장하지 않는다. 마지막 외부4문서의 POSTPUBLICATION_EXTERNAL_DELIVERY가 실제 게시 후 권위다.

## 새 실행과 멈춤 기준

Validation은 reviewed S05 Local source를 정확히 pin하고 새22test methods를 한 suite invocation에서 실행한다. 원 expected값은 위 exactgeometry/analyticphysics와 독립 grid enumeration이다. Plot입력17rotation rows,4counterfactualcontrols,manual/default widths,3nativeenergyrows,timing을 같은 실행에서 저장한다. 과거 suite 실행0, 새 기하 비교에 필요한 이전 API함수 호출은 영향을 받는 의존성 검증으로 식별한다.

Validation wholeprocessCPU12s,wall40s,perprocessAS512MiB,singlethread; initialattempt1 + diagnosed targetedrepair reserve1. Plot wholeprocessCPU8s,wall20s,AS512MiB,attempt1, saveddataonly,scientificimports/calls0. 최초실행전에고정한새단위예산이며 과거failure와remaining을변경하지않는다. 실패기록은 create-only. 검증child가실행되지않은환경실패도wrapper invocations/cumulative비용에포함하고 실제scientificsuite횟수와구분한다. Wolfram evaluator1call/timeConstraint15s,actualremoteCPUunsupplied이면null.

Outer launcher는 run_bounded.py 전체수명과 waiteddescendants의CPU/wall을관측하고 자기bookkeepingCPU는별도기록한다. 자식CPU/AS cap이 parent+children aggregate의완전한선제차단이라고주장하지않는다. 후속외부metadata serialization/fsync는측정경계밖이다. Syntax/metadata preparation은science결과로계산하지않으며 준비시간은미측정으로둔다.

독립 reviewer는 같은pass1의 math→code→rawresults→기존PNG읽기로 이어간다. 사전F01원주비교assertion은기존places12에서수정하고닫는다. 새 수치오류가나오면원인과영향을특정해 controller판정후한정repair한다. 동일suite의정보없는반복은하지않는다. 허용된loop종료후새node는자동시작하지않는다.

## 물리·코드·그림 검토

물리: q_perp antipode, F(−μ), cm↔lab부호,fullcirclelimit,evenmeasure,J invariance,σ normalization,count/energy구별을검사한다. 코드: inputdomain,arcseam,unionoverlap,exactendpointmask,cacheidentity,manualδ/ratio/status를검사한다. 그림: rotation삼각형법칙,wrongmarginal/assignment/hitcontrols,3energyrows,actualwidth/bound를실제PNG에서읽는다. 정적proof와한정실행이각각지지하는범위를구분한다.

신규성과 strongno-go는주장하지않는다. 실험원정규화·실제φlaw/shape·flux·deposition의열린입력은선행계약을유지한다. 이번node통과시로컬9complete+1partial+3physicalopen/13,중앙28/88HEdelta0; 실제gate미통과시새nodepartial이며완료수는8/13으로남긴다.
