# 유한 열적 끝점 C6: 최초 fixture 실행 결과

2026-10-28 KST. cosmosapjw-quantum/rei_bianchi, research/rei-causal-prefix-consumer-20261027, Draft PR240.
실행 기준 HEAD: ebff569ac62792c182737e5f23c99e562768e5f2.
판정: PASS_SCOPED_C6_FIXTURE_IMPLEMENTATION. 전체 과학 수용은 NOT_ISSUED.

## 실제 실행

사용자가 C6 실행과 합리적인 범위의 자원 설정을 명시적으로 승인했다. 실행 전에 AUTHORIZATION.json과 세 소스의 identity를 고정했다. 현재 runtime의 Python3.13.5 탐침이 성공했다. 기존 mounted source에서 동일 byte의 세 파일만 staging했고 새로운 clone/worktree나 원래116파일 bundle 복원을 하지 않았다.

현재 게시된 계산 모듈, 수정된 실행기와 테스트를 그대로 한 번 실행했다. 27개 고유 unittest 메서드가 모두 통과했고 실패0,오류0,skip0,worker/outer exit0이었다. 수학·표현18,승인조건3,실패분류6개다. 수정0,재시도0,기존 suite replay0. 실행 후 세 소스의 SHA256/Git blob/크기가 실행 전 고정값과 일치했다. 이 확인은 source identity이고 테스트 결과를 대신하지 않는다. 테스트 원문의 red/green 실행 이력이 없으므로 TDD cycle 성공이라고 부르지 않는다.

명령:
`/opt/pyvenv/bin/python -B -S -m unittest discover -s /mnt/data/rei_thermal_c6_20261028/implementation -p test_finite_thermal.py -v`

이 worker는 승인된 run_once.py에서 실행됐고 전체 wrapper는 GNU time 및 별도 wait4 관측으로 계측됐다. 실제 authorization,STARTED,RESULT,stdout/stderr,외부time,observer원문은 백업 capsule 안의 RAW_EVIDENCE.json에 정확한 UTF-8 payload로 보존한다. Git에는 결과 요약,실제 외부 계측,테스트 stderr와 이 보고서를 게시한다. 두 보존 파일집합은 다르며 각각 명시한다. 각 payload에 원래 상대경로·bytes·SHA256이 있다. 새 결과 요약은 C6_RESULT.json이며 원래 raw 기록을 고쳐서 요약과 맞추지 않았다.

## 계측과 원장

|대상|실제 관측|
|---|---:|
|외부 명령 전체 terminal CPU|0.148771 s|
|외부 user / system|0.076178 / 0.072593 s|
|외부 wall|0.15305462700001726 s|
|worker terminal CPU|0.097287 s|
|supervisor 최종 직렬화 전 CPU|0.043720 s|
|unittest 자체 표시 시간|0.007 s|
|Linux maxrss 관측|17008 KiB|

외부 명령 CPU에는 GNU-time,Python supervisor와 waited worker의 시작·import·직렬화·종료가 포함된다. worker CPU를 여기에 다시 더하지 않는다. observer 자체의 직렬화 전 CPU0.021919 s와 준비·보존·커넥터·모델 비용은 이 외부 명령 수치 밖이다. maxrss는 프로세스 트리의 동시 총 메모리 사용량이 아니다. 짧은 단일 실행시간은 speedup 또는 반복 성능 benchmark가 아니다.

할당: 현재 사용자의 위임에 따라 이 C6의 recorded cumulative 임시 ceiling120 CPU s,단일시도30 CPU s,worker20,supervisor8,최종기록예약2,wall120 s,메모리512MiB,worker1을 실행 전 고정했다. 실제 관측된 해당 명령은 제한 안에서 종료됐다. 이 단계의 할당은 닫고 이전 정책 상태를 복원한다. 남는 예약을 새로운 source 실행·다음 노드에 자동 재사용하지 않는다.

역사적 planning15.929490885에 이번 외부 명령0.148771만 더한 부분 하한은16.078261885 CPU s다. 별도로 기록된 이전·이번 준비/metadata 비용과 미계측 비용은 여전히 존재하며 이 부분합에서 삭제되지 않는다. 준비 metadata prefix0.055215s,결과 정리 metadata prefix0.027211s 등은 관측구간이 다른 별도 기록이다. UNKNOWN_NOT_ZERO,표시 반올림과 미계측 tail을 유지하고 전체 대화·모든 과거 비용의 정확한 합계나 전체 cap PASS는 주장하지 않는다. presentation lower48.263016494/lastcap47,main595.225063/600 NO_MORE_IVPs는 그대로다. 이전 연구cap20/reserve3는 이 C6에 한해서 새 승인 할당으로 대체했고,기존 ZIPcap60/reserve8은 미승인·미실행이다.

## 확인된 수학–코드 대응

고정된 이상 caloric 법칙 U=cv*N*T,단일 온도,양의 N/U/cv 아래의 검증이다. Q와W는 공통 기준부피당 이미 적분된 기체 에너지와 일이다. cv=3*k_B/2는 단원자 source bridge의 가정이며 자연단위로 k_B를 생략하지 않는다.

- 열이 양수여도 입자수 증가에 따라 T/Ta=3/4가 되는 fixture와,열이 음수여도 입자수 감소로7/4가 되는 fixture를 통과했다. 이는 실제 BASS 거래의 온도가 아니다.
- 독립 initial-EOS와 balance 잔차(r0=1,r_balance=2)를 보존하고 rE=3,rN=1에 따른 저장/재구성 온도차 -13/30을 두 표현으로 대조했다.
- 모든 입력 방향을 포함한 JVP는 미분된 caloric 항등식에 맞았고,R/b 정규화의 개별 항과 비율에서의 상쇄를 확인했다.
- inert-He를 포함한 count와 parameter tangent,별도 electron endpoint 잔차,비가중 구간의 R01 합성·미분 교차항을 확인했다.
- 선언된 직사각형 에너지/입자수 범위의 끝점과59/165의 exact discrepancy bound를 확인했다. 미공급 반경은None이며 물리 오차반경으로 승격하지 않는다.
- 원 JSON binary64,hex dyadic,saved MP-decimal의 차이,우발적 float 입력 거부,gas sector 선택과physical-null 출력을 확인했다.
- 실행 승인 조건과 실패 분류 함수는27개 suite 안의 순수 사례로 검증했다. 정상적인 supervisor/worker 종료 경로는 실제 실행됐다.

## 남은 검증과 과학적 해석

이번에는 실제 원자료3554206bytes를 성공적으로 consume_saved_source에 통과시키지 않았다. 전체11필드 packet의 성공적 결속 역시 실행하지 않았다. malformed bytes의 거부 테스트가 성공했다는 사실을 성공 경로의 통합 검증으로 바꾸지 않는다. 이 입력 경로는 다음 source-bound 검증의 구체적인 의무다.

timeout,메모리 고갈,fork 실패,외부 신호를 실제로 주입하지 않았다. 분류 함수에 대한 가상 관측값 검증은 운영체제 fault-injection과 다르다. 독립 비작성자 R6/C9도 NOT_RUN이며,이번 controller 실행을 별도 agent 검토로 표시하지 않는다. 단순 fixture PASS를 EOS/실제 수신자/전체 reionization solver 정확도로 확대하지 않는다. 새 CAS/IVP/provider/plot/ZIP 실행0이다. 그림이 필요한 새로운 연속 수치 campaign을 시작하지 않았고,PASS bar chart를 물리 검증으로 제시하지 않았다.

실제 REI bath/native25/temperature/physical radii는null,L4_ready=false,global_physical_completion=null. 기존 atomic-storage20/20의 scoped PASS와 이번 유한 thermal 단위는 별개다.

## 최신 조사와 재사용 결정

실행 전 작업HEAD/AGENTS/소스 identity를 확인했다. 더 넓은 연결 소스 조사는 같은 응답에서 이후 마무리했다. 무필터 branch-name pagination을7개 저장소에서 terminal null까지 조회했다:REI282,BASS302,HE112,CR190,REC162,WU159,Vigil221,총1428. 호출별 순차 live snapshot이므로 원자적 동일시각 snapshot은 아니다. 모든 branch 본문·모든 개인대화·모든 백업 bytes를 읽었다는 주장은 하지 않는다.

2026-10-28이후 updated 조건의7repo PR검색은12건을 반환했다. BASS217 signed Lyalpha dual-witness,fed29a0195ca9bec270971abe4ed60c7d23cff29의 인계 원문은18/20 및 비작성자R6/C9 미완료,경계 개선과 실제 correction/physical accuracy의 차이를 유지한다. BASS215 source-literal QSS와216 공간 polarized transport는 별도 모형이다. REC144 C10 recovery는 기존 결과의 보존과 미완 전달을 구분하고,REC143 background-jet/REC142 regularity는 physical tube/error를 제공하지 않는다. 이 PR 관측을 재현한 계산으로 세지 않았다.

중앙3d8bcdb79a7062459adaad9be6d7fe951f86a17a의CR_HE_EVENT_UNION 반환 앞부분을 직접 읽었다. 공급자R10/10+C10/10와central authority28/88,completion_effect0을 확인했다. 소유자의 사건합집합 완료는 우리 caloric bath나physical temperature 수용이 아니다. 그 예산은 이전되지 않는다. 현재 작업DAG33/88과중앙28/88,88IDs/17edges를 변경하지 않았다.

개인문맥 검색은 해당 단위의 다른 완료C6/독립검토 반환을 확립하지 못했으며 전체대화export가 아니다. 현재 사용자 명시 승인이 이번 실행 권한이다. 기존C5 delta의Drive1nKepsplcQoAzE33izYISVh2XC0xSC566 및Dropboxid:BSpOijBcT10AAAAAAEDJMg를 각57982bytes로 재조회했다. 원격원문 전체를 다시 내려받거나 과거capsule/ZIP을재생성하지 않았다. 이번에는새 물리문헌을도입할필요가없어SciSpace/Exa/Wolfram의새과학결과를주장하지않는다.

## 단계 종료

C6 fixture scope 완료:새 단위10/20에서11/20,R1-R5 5/10,C1-C6 6/10. 기존작업33/88,중앙28/88,원래노드증분0. 원문 계산코드·runner·tests·허용오차는수정하지않았다. 후속게시·백업은이번실행증거만새로보존하고실제ACK를별도handoff로결속한다.

다음 구체적인 의무는 고정된BASS 원자료와literal packet을 source-mode로 결속하는 통합 검증이다. 현재의fixture 승인·완료를 source-mode 실행기록으로 확장하지 않는다. 같은27개 테스트를 안심용으로 재실행하거나 C5/C6 허가를 다시 요청하는 절차를 만들지 않는다. 독립 검토와 physical admission은 별도 유지한다.
