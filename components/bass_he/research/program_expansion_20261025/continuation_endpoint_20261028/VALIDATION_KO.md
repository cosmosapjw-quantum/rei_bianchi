# R6/C6 — 실제 단일 campaign과 독립 검증

S05 source `501f4c5a5e5b14b0e05ff5d504578b5b9218caf7`, tree `54bbaf71c917c67f3c5d3b9dcda44e3eecb740c4`에서 실제 initial campaign을 한 번 실행했다. 실행 전 mandatory pin의9개 source파일과2개 입력 identity가 일치했다. root가 시행을 승인했고, 하위등급 구현자가 prescribed command를 실행했다. Requestedmodel=gpt-6.1-sol, observedruntime model=null이다.

## 실제 결과
`evidence/validation/initial/TEST_REPORT.json`: **8 PASS,0 FAIL**.
`READER_REPORT.json`: **PASS**,6polytopes/26vertices, candidate-search0, enumeration0, producer-import0.
`FINISH.json`:constructioncalls1,exit0. 전체과학구성을반복하지않았다. 동일campaign내실제결과reader호출과corrupt-certificatecontrols를추가construction으로세지않는다.

| Control group | 실제 결과 |
|---|---|
| Factorization/normalization/derivative identities | PASS |
| Positive quadratic with negative coefficient; negative case rejection | PASS |
| Three transformed basis intervals and all coefficient signs | PASS |
| Known threshold-moment examples | PASS |
| Cube/simplex exact vertices and singular rejection | PASS |
| Signed ratio and outward decimal conversion | PASS |
| Actual six certificates/nesting/witnesses/source binding | PASS |
| Corrupted certificate rejection | PASS |

Reader는producer를import하지않고candidate를찾거나정점을다시열거하지않는별도코드경로다. 두구현의저자는같은하위등급agent이며비저자과학심사는별도reviewer가담당한다. 정점목록완전성은유계polytope정리,실제producer의모든active-tripleloop,실행counts및code심사에의존한다. Reader만으로목록의완전성을증명했다고쓰지않는다.

## Exhaustion과비용
| N | Inner vertices | Outer vertices | Inner bases | Outer bases |
|---:|---:|---:|---:|---:|
|1|6|4|680|560|
|4|4|4|1771|969|
|16|4|4|16215|4495|

총24690activebases를새scope에서열거했다. 네nestedinclusion이모두PASS다. 모든inner증인은전구간r>=0와네창을통과했다. 이번실제outervertices도모두정확한rminimum>0를가졌다는것을저장했다. 이사실은고정된이번계수집합의결과다.

Whole runner+waitedchildrenCPU **2.020525s**, wall **1.9446278749965131s**, maxchildRSS **15752KiB**. LimitsCPU120s/wall300s/AS805306368bytes/threads1. Repairednamespace-aware runner의actualchildhost/localgroup411086/5를기록했고exit0/terminationreasonnull이다. RemoteWolframCPU/wall은이측정에포함하지않는다.

새science실패0, targetedscience repair0. 실행전F1의누락control보강과F2주석부호수정은사전코드교정이며actualfailure나repair실행으로세지않는다. 이전T13initialrunnerfailure및targetedrepair등모든선행이력은그대로보존한다.

## 판정 경로
독립검토는실제input/sourcepin,계약,원시결과,proof를읽어수행한다. 수용결정은review/ACTUAL_RESULT_REVIEW와후속최종review에연결한다. 이문서의실행PASS는최종외부게시·운송ACK를미리뜻하지않는다. 완료된campaign을재실행할이유는남아있지않다.
