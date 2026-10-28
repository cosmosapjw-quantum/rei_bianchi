# C5 실패 분류 수정: 실제 게시·이중백업 인계

2026-10-28 KST. repo cosmosapjw-quantum/rei_bianchi, branch research/rei-causal-prefix-consumer-20261027, Draft PR240.
기준 HEAD: 66878795aa14f79b32be0cd532c31b3a4a036985.
수정 소스 commit: 3ad98dd7e7a58bee047fc566cb36e41b1ea7df5f.
수정 소스 tree: d359fae6005cd4ba8e7a60adeba2d4abce95d522.
이 인계서는 위 source의 후속 Git-only metadata다. 자기 commit SHA를 미리 만들지 않는다.

## 결과와 완료 범위

상태 PATCH_AUTHORED_NOT_EXECUTION_VERIFIED. 기존 controller-direct C5 승인 아래 하나의 구체적 진단 결함을 수정했다. 테스트·실제 소스 평가·새 과학 실행은 승인하거나 수행하지 않았다. R1-R5 5/10,C1-C5 작성 5/10,합계10/20을 유지한다. 새 완료 단계0이며 R6 독립 검토,C6 실행,C9 과학 수용은 미완료다. 기존 atomic-storage20/20과 scoped PASS는 별도 유지한다.

원래 작업33/88,중앙28/88,88IDs/17edges,delta0,L4_ready=false,global_physical_completion=null. 중앙28/88은 이번에 읽은 CR owner-return의 명시적 count authority이며 전체 DAG 재계산 결과가 아니다. 실제 REI bath/native25/온도/physical radii는 null이다.

## 결함과 최소 수정

이전 runner는 stop_reason 존재 또는 usage 부재를 모두 RESOURCE_STOP_OR_OVERRUN으로 기록했다. 예컨대 예산 초과 없이 os.fork()가 OSError를 일으키는 조건에서도 이 분기로 간다. 이것은 원문 제어흐름으로 확인한 조건부 반례이며 실제 fault-injection 실행을 보고한 것이 아니다.

기존 runner 안에 순수 classify_outcome을 추가해 명시적 BudgetStop/관측된 초과,supervisor 실행 오류,사용자 interrupt,계측 누락,worker 신호,일반 nonzero exit를 분리했다. raw wait status,예외 type,종료 signal,개별 상한 관측을 보존한다. 미관측 child CPU와 그를 포함하는 합계는 null이지0이 아니다. SIGKILL 또는 timer-related signal만으로 원인을 단정하지 않는다. exit0도 과학 수용이 아니다.

run_once.py,test_finite_thermal.py,README.md만 변경하고 검토 노트 하나를 추가했다. 기존 수학/표현18개 및 승인3개 테스트는 그대로이며 새 분류 controls6개를 더해 총27개 작성,실행0이다. timer/limit/argv/단일시도/과학식/허용오차/입력 pin은 변경하지 않았다. cleanup의 모든 경우를 다루는 새 framework는 만들지 않았다.

finite_thermal.py는20532bytes,SHA2568482189fb3f7fd66d7b164517d0cce11431d315a5492ed3632643ff5100cf14d,Git blob880a074f793ba6bb3aa3e1d7958d8116eb239c0e로 유지한다. 새 source 비교에는 이 파일 변경이 없다. 이는 byte identity이며 새 수치 검증은 아니다.

## 실제 파일 identity

기준 경로 research/rei_expanded_event_consumer/finite_thermal_endpoint_20261028/.

|파일|bytes|SHA256|Git blob|
|---|---:|---|---|
|implementation/run_once.py|15122|14def6a0c42067e17a19cc638703c2b751ae82f28ba594171391458b577ebe68|3dd1b2428c41515139ecfe3e5c60ecc8988236f2|
|implementation/test_finite_thermal.py|15250|06aa8e39da065ecd495da30cd0294efaa07522420bcb6a6fe9bc3066ee113379|4c4948af09c2427c5d6f45eb1611db6b8f09c009|
|implementation/README.md|13173|99f1d2f9c08a3d20c9f9caf7f57f212e769b81b5c0981b598fe65d15b8a57528|cb493f7b22d6d650736863068d2d415ce7dc7202|
|review/C5_FAILURE_CLASSIFICATION_20261028.md|10379|b45e718e9aa37add50e17cae500b97d90ec5f4d5d3446ab1fd4fbb81489a1c07|16ee113380949e2af01527814ae3c150dd4f0bee|

실제 source ref 갱신은 expected_sha=66878795...와force=false로 성공했다. GitHub compare는3modified+1added,삭제0,다른파일변경0을 반환했다. 생성된 Git blob4개는 각각 로컬 원문 blob과 일치한다. CI나 실행 PASS를 근거로 쓰지 않았고 commit은[skip ci]다.

## 실제 이중백업 완료

파일: REI_FINITE_THERMAL_C5_CLASSIFICATION_PATCH_20261028_3ad98dd7e7a5.json.
형식: 새 UTF-8 JSON delta capsule,4payloads. ZIP 또는 원래 전체단위 백업이 아니다.
bytes57982.
SHA2560957f678be8a2d20ef13b02639de6ff04ff043bdc02f11906dccc950e7b3b24d.
Drive id1nKepsplcQoAzE33izYISVh2XC0xSC566: SUCCESS 및 별도 metadata size57982,modified2026-10-28T03:19:07.187Z.
Drive parent1phclg92jkhC5KgvnXhks8GbOFlya4qGe.
Dropbox id:BSpOijBcT10AAAAAAEDJMg: completed,size57982,modified2026-10-28T03:19:16Z.
Dropbox path /bianchi/research_backups/rei_bianchi/REI_FINITE_THERMAL_C5_CLASSIFICATION_PATCH_20261028_3ad98dd7e7a5.json.

양쪽 actual completion ACK가 있다. 새 원격 전체 bytes를 다시 내려받아 SHA를 확인한 것은 아니다. 원래 C5 capsule63289bytes/Drive1ZQ_3dkVwVNREA9CgwoIKXIsFxeB2QvSr/Dropboxid:BSpOijBcT10AAAAAAEDJFg는 metadata만 재확인했고 재생성하지 않았다. 기존116파일 bundle과source ZIP도 재생성하지 않았다. 본 post-ACK 인계서 자체의 이중백업은 주장하지 않는다.

## 새 공급자 관측과 재사용 한계

중앙 latest observed3d8bcdb79a7062459adaad9be6d7fe951f86a17a의 CR_HE_EVENT_UNION 반환은 공급자 자체20/20과central28/88,completion_effect0을 기록한다. Science406783036c26e71f3b85568adcfb5e163b012ab1,documents729cb95164697d8122b0a85ae6e403b57392e724. Actual exclusive measure,Ccross,EOS/온도,full native25는null이다. 같은pin HANDOFF_KO는preimage이므로 과거D/M=null을 최종상태로 읽지 않는다.

BASS restartf834101d...,HE307fee38...,REC5438f2a0...,WUc92e6378...,Vigil7eb2dd0...의 선택ref와 원문범위를 확인했다. 다른 공급자의 수용·계산·예산을 본 단위에 이관하지 않는다. 현 조사범위는7개선택lane,중앙ref,필요한producer/consumer원문,indexed대화검색,기존C5백업metadata다. 전체branch/대화전문/원격backupbytes전수조사완료는아니다. Native subagent/독립review는NOT_RUN이다.

## 실행·비용 경계

과학/테스트/CAS evaluator/실제source/IVP/provider/plot/원bundle복원/ZIP 실행0. 새runner/계산모듈import,syntax/AST/compile검사0. 동일문맥원문검토와source편집/해시/백업처리만했다.

현재metadata Python실행은PYTHON_PASS(Python3.13.5); C++는미탐침이며불가판정하지않았다. 별도timing표시(user/system/wall):edit0.02/0.02/0.04s;finalize0.01/0.02/0.04s;report-hash0.01/0.00/0.02s;capsule0.02/0.00/0.03s. 모두반올림표시이며모델/커넥터/원격/후속기록을포함한전체비용이아니다. 추가shell/read/hash/인계서작업과미계측tail은UNKNOWN_NOT_ZERO다.

planning historical15.929490885/lastcap16,presentation lower48.263016494/lastcap47,original10/30,main595.225063/600 NO_MORE_IVPs와이후별도기록비용을보존한다. 비용reset/transfer와전체cap준수주장없음. 연구cap20/reserve3 및ZIPcap60/reserve8은미승인이다. Controller-direct C5승인은유지되며다시요청하지않는다.

## 복사 가능한 다음 지시

현재HEAD/AGENTS와이인계서를읽고같은finite_thermal_endpoint_20261028단위를이어가라. 총10/20,작업33/88,중앙28/88,원88IDs/17edges,physicalnull을보존한다. C5를다시작성하거나같은조사를반복하지마라. 다음실행대상은수정된27메서드의최초C6 fixture suite다. 별도정량승인,최신3source hash,정확한argv와누적비용경계를고정한후한번만실행한다. 실제source소비는별도mode/승인이다. 실행실패원인과budget증거를섞지말고raw결과를보존하라. 이수정은runtime검증미완료이고독립R6/C9도미완료다. 새과학적승격이나자동재시도·다음노드시작은하지마라.
