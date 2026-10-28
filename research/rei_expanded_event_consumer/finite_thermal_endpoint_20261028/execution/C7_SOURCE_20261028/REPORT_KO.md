# C7 실제 BASS 원자료: 유한 열적 끝점과 prescribed driver의 분리

2026-10-28 KST. cosmosapjw-quantum/rei_bianchi, research/rei-causal-prefix-consumer-20261027, Draft PR240.
기준 HEAD ded32cd6c3201a15d05c43472180f4f8689fad02.
판정 PASS_SCOPED_C7_REPRESENTED_SOURCE_CALORIC_VALIDATION. 독립 R6/C9 및 실제 수신자에 대한 과학적 수용은 NOT_ISSUED.

## 1. 이번에 닫은 실행 경로

고정 BASS205 원자료3554206bytes와11필드 literal packet8281bytes를 실제 consume_saved_source에 한 번 연결했다. Worker/외부명령 exit0,수정0,재시도0. 기존 C6의27개 fixture는 재실행하지 않았다. 계산 모듈/runner/tests 및 원자료의 실행 전후 SHA256/Git blob/크기가 일치한다. 입력→소스 bath→기체 Q/W→유한 caloric 끝점→정확한 num/den 직렬화의 성공 경로가 확인됐다.

생산 모듈을 import하지 않는 별도 saved-data 검사기에서45/45개 검사가 통과했다. 원자료에서 입자수·에너지를 다시 조립하고 저장된 출력과 비교했으며, Decimal100 경로의 온도도 같은 exact-rational 결과와 대조했다. 이 경로는 같은 작성자의 다른 산술 확인이며 독립 작성자 검토가 아니다. 전체 체크와 정확한 유리수는 evidence/SAVED_SOURCE_CHECKS.json,생산 출력은 attempt_01/stdout.txt에 보존한다.

원자료를 직접 HTTP로 받으려던 두 요청은 DNS 단계에서 실패했다. Python불가나 과학 실패가 아니다. 기존 Drive 원문4699240bytes를 원본 SHA256 d77ea863ad2730f6ef0be27a3f3a93c8b5c864f3d863b4b1b5950fd61a6ef63e와 대조한 뒤 필요한 입력 한 개만 추출했다. 기존116개 파일 전체 복원,소스 ZIP 생성,과거 백업 재생성은 하지 않았다. literal packet은 연결 도구 원문을 복사한 뒤 완전한8281bytes/SHA256/Git blob 일치를 확인했다.

## 2. 물리량과 조건부 caloric 사상

모든 입자수 N과 기체 에너지 U,Q,W는 같은 기준부피 V0당 값이다. 단일 온도·비상대론적 단원자 caloric 모형 U=cv*N*T,cv=3*k_B/2를 사용한다. k_B=1.380649e-23 J/K를 유지한다. Q는 이미 적분된 기체 사건 에너지이며 W는 이미 적분된 기하학적 일이다. 원자 결합/여기 저장량과 광자 에너지를 Q에 중복 가산하지 않는다.

열적 입자수는 H fine-stock 합+별도 저장 열적 전자+비활성 소스 He B=NH*fHe다. H-only 기여를 전체 gas energy의 분모로 사용하지 않는다. 사건 동안 DeltaB=0이어도 모수 방향의 deltaB=fHe*deltaNH+NH*deltafHe는 일반적으로0이 아니다.

D=Na+DeltaN>0,E=cv*Na*Ta+Q+W>0에서 T_rec=E/(cv*D). 별도 저장 끝점은 T_saved=Ub/(cv*Nb)다. r0=Ua-cv*Na*Ta,r_bal=Ub-Ua-Q-W,rE=r0+r_bal,rN=Nb-D를 원래 값 그대로 유지한다. 온도차는 정확히 (rE*D-E*rN)/(cv*D*(D+rN))다. 이 등식은 원자료의 표현된 숫자에 관한 것이지 물리 오차반경의 인증이 아니다.

## 3. 실제 수치 결과

다음은 표시용 반올림 값이며 보존된 num/den이 수치 authority다.

|양|값|
|---|---:|
|초기 energy-based 온도 Ta|3003.751227277705910 K|
|초기 native driver 온도|3003.747832949155509 K|
|오른쪽 native driver 온도|3003.492794789281561 K|
|저장 끝점 caloric 온도|3003.417482286276822 K|
|사건 재구성 caloric 온도|3003.417482286276822 K|
|저장값-재구성값|-6.297256911088516e-67 K|
|caloric 끝점-right driver|-0.07531250300473922 K|
|초기 온도 상수/표현 차이|+0.003394328550400922 K|
|초기/최종 열적 입자수|3.064494708961487e8 / 3.064175142872488e8 per V0|
|비활성 He 입자수|1.989824298564396e7 per V0|
|사건 입자수 변화|-3.195660889985789e4 per V0|
|기체 사건 Q|-8.692142933008802e-16 J per V0|
|기하학적 일 W|-3.236594506618775e-15 J per V0|
|초기 EOS 잔차 r0|1.093445657377263e-81 J per V0|
|수지 잔차 r_bal|-8.2823e-81 J per V0|
|집계 잔차 rE|-7.188854342622737e-81 J per V0|
|입자수 잔차 rN|-5.132999999999936e-62 per V0|

저장/재구성 차이와 driver/caloric 차이는 다른 양이다. 전자는 표현된 에너지·입자수 잔차로 설명되는 약1e-67K의 차이다. 후자는 약0.0753K이며 prescribed 반응률 driver를 finite energy ledger가 내놓는 caloric 값과 동일시할 수 없음을 보여준다. 이는 이 모형에서 thermal feedback을 연결할 때 해결할 차이지, 여기서 모든 물리 heating의 누락이나 실제 우주의 온도 오차를 식별한 결과는 아니다. 원래 소스가 self-consistent thermal trajectory를 약속했다는 가정도 하지 않는다.

## 4. 부호를 보존한 직접 유도와 실제 값

오른쪽 native driver를 Td_b,왼쪽을 Td_a라 하자. 기존 사상에서 다음을 직접 얻는다.

T_saved-Td_b = Q/(cv*D)+W/(cv*D)-Ta*DeltaN/D
               +(Ta-Td_a)+(Td_a-Td_b)+(T_saved-T_rec).

첫 세 항은 실제 finite caloric 변화,네 번째는 초기 온도 상수/표현 연결,다섯 번째는 비교할 prescribed driver 변화의 음수,마지막은 보존한 끝점 표현 잔차다. 모두 K단위이며 정확한 유리수 합에서 잔차0을 얻었다.

|기여|K|
|---|---:|
|기체 사건 열|-0.1369741872869773|
|기하학적 일|-0.5100352186318024|
|열적 입자수 감소|+0.3132644144896919|
|초기 온도 관례|+0.003394328550400922|
|prescribed driver 변화의 음수|+0.2550381598739477|
|보존된 표현 잔차|-6.297256911088516e-67|
|합계|-0.07531250300473922|

WolframLanguageEvaluator의 단일20초 제한 호출은 위 분해식,저장/재구성 잔차식,전체 JVP의 세 유리식 잔차를 {0,0,0}으로 반환했다. 경고는 응답에 없었다. CAS는 해당 대수식의 corroboration이며 비작성자 R6/C9나 실제 bath 적격성 검토가 아니다. Remote CPU는 미계측이다.

같은 소스 에너지에 H-only 분모를 사용한 명시적 오연결 대조값은3211.999371310258K이며,올바른 bath 값보다6.944818369546268% 높다. 보존된 W를 다시 더하면3002.907447067645K로0.5100352186318024K 낮아진다. 이 두 대조는 별도 잘못된 계산식을 비교한 것이며 원자료나 수용된 생산 경로를 변경하지 않았다.

## 5. 이중 검토와 그림

수학·물리 검토: N,U의 공통 기준부피,기체/원자/광자 소유권,cv의 단위,양의 D/E/Nb/Ub,He와 전자의 count,초기EOS/구간수지 잔차 분리를 확인했다. 공통 R은 온도 비에서 상쇄되지만 개별 proper density에서 지우지 않았다. 실제physical radii는 작은 잔차로 채우지 않았다.

수학–코드 검토: 전체 성공 경로의 source hash와11개 decoder 값을 대조하고,raw-field 재조립과 exact identity,별도 Decimal100 산술을 확인했다. Decimal gap0E-96은 그 precision의 비교 결과이며 독립 정확도 theorem이 아니다. 새 검사코드는 source consumer를 import하거나 재실행하지 않는다.

TEMPERATURE_GAP_DECOMPOSITION.svg/PNG는 저장 결과의 위 부호 있는 기여를 그린 것이다. 시간 이력이나 확률구간을 가장하지 않는다. 음의 기체 열/일과 양의 입자수 효과가 상쇄되고 net가 음수임을 직접 읽었다. tiny residual은 caption에 수치로 남겼으며 축에서 보이지 않는다고0으로 바꾸지 않았다. 최초 그림 저장은 notebook과root 소유폴더의 쓰기권한 차이로 실패했다. 같은 메모리 figure를 notebook 소유경로에 저장했고,실제 이미지에서 축 근처 숫자 겹침을 발견해 x축 여백만 넓혔다. 데이터/소스 계산 재실행은0이다. 보존된 SVG는 최종 그림이며 PLOT_PROCESS.json에 실패와 복구를 기록한다.

## 6. 실행과 비용

실제 source-mode 1회,새 saved-output 검사1회,정확한 분해 분석1회,CAS1회다. C6의27fixture,원 BASS provider,새 IVP/ODE,옛 과학 campaign,최종ZIP은0회다. 새 source 실행의 외부 terminal CPU는0.124835s(user0.085669/system0.039166),wall0.125188393s이다. Worker0.081005s는 이미 이 값에 포함된다. Supervisor prefix0.035586s와worker를 외부 inclusive CPU에 다시 더하지 않는다.

saved-check 명령은 GNU-time에서user0.01/system0.02/wall0.04s로 표시됐으며 반올림 계측이다. 그림의 첫 post-import clock부터 마지막 저장까지 notebook CPU prefix1.549246861s가 관측됐다. 시작 import/커넥터/모델/보존 및 기타 미계측 비용은 UNKNOWN_NOT_ZERO다. whole-session cap PASS는 주장하지 않는다.

현재 다음 연구 루프 실행 요청을 같은 단위의 C7 source integration 선택으로 해석하고,예전 닫힌 C6 잔여량이 아닌 새 bounded allocation을 기록했다. Primary30CPU(20worker+8supervisor+2record),wall120s,memory512MiB,단일시도. 이 단계 전체예약은source30+검사15+그림5+local보존10=60CPU,recorded cumulative ceiling120CPU다. 이미 지출된 planning 부분하한16.078261885와 모든 별도 과거비용은 보존한다. 여기에 이번 primary만 추가한 부분값은16.203096885이며 현재 전체합계가 아니다. 단계가 끝나면할당을닫고다음노드로이관하지않는다. 기존presentation lower48.263016494,main595.225063/600 NO_MORE_IVPs와다른owner예산은불변이다. ZIPcap60/reserve8은실행하지않았다.

## 7. 최신 연결 조사와 한계

현재7개관련저장소의최근PR검색과선택branch ref를다시읽었다. 2026-10-28T03:53:00Z이후PR검색은REI240만반환했으나,이를모든새commit의부재로해석하지않았다. 실제WU registry ref149d73a0...는새 R11의12/20,local21/38,primary완료/reference미완,15CASzeros와미해결경고를기록한다. 실제HDarray/namedphysicalconsumer/densityclock은미공급이다. 이결과나예산을우리source에이관하지않는다.

그외관측은BASSfed29a0195ca...,HEa73773a9e105...,CR729cb9516469...,REC5438f2a082f7...,Vigil7eb2dd0ffd...,중앙3d8bcdb79a70...이다. 원 frozen BASS205를대체하지않았다. 이전1428branch-name census는재사용한과거관측이며이번새전수조사라고표시하지않는다. 대화검색은해당단위후속완료를확립하지못했고stale C6-NOT_RUN 문서를현재C6완료기록대신쓰지않았다. Drive source-text 원본은전체SHA일치로회수했고관련backup검색은범위제한이있다. 전체branch본문·전체대화·모든backupbytes전수열람완료는아니다.

기존재결합문헌의근거를재사용했다. 공식HyRec arXiv서지(1011.3758v2,PRD83,043513)와Python Decimal문서는다시확인했으나원논문전체를새로검증했다고하지않는다. SciSpace/Exa신규문헌검색0,CAS평가1이다. 참고: https://arxiv.org/abs/1011.3758 ; https://docs.python.org/3/library/decimal.html .

## 8. 단계와 다음 의무

C7 source-representation validation 완료에따라R1-R5 5/10,C1-C7 7/10,합계12/20이다. 독립 R6/C9는미완료며same-author검사나CAS를대체로세지않는다. 기존atomic-storage20/20,작업33/88,중앙28/88,88IDs/17edges,증분0을보존한다. L4false/globalnull,실제REI bath/native25/temperature/physicalradii는null이다.

다음은C8의소스표현민감도·양의분모conditioning 검증이다. 정확한현재결과를재사용하고불필요한primary/27fixture 재실행을하지않는다. 현재모형의반올림표현/상수관례/원자료오차를물리오차와구별한다. C7/source모드승인과완료를다시묻는절차로되돌아가지않는다. 새검토자는고정R5,소스binding,실행근거를한번검토하고독립수용여부를판정한다. 원자료재생성,피드백추가,새fullsolver node는이번범위가아니다.
