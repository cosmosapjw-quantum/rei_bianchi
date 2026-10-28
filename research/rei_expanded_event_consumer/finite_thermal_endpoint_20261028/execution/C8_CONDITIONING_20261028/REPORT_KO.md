# C8: 저장 caloric 끝점의 표현 민감도와 조건수

2026-10-28 KST. Repository cosmosapjw-quantum/rei_bianchi, branch research/rei-causal-prefix-consumer-20261027, Draft PR240. 기준 HEAD는 7d1cf19e61c372ecda7964e50991685f006dc1ee이며 C7 증거 commit은 e086133df76bb27cf35e863ceade4e862de6f130이다.

판정: **PASS_SCOPED_C8_REPRESENTATION_AND_CONDITIONING**. 새 저장결과 수치 실험 1회, 81/81 검사, 실패0, 수정0, 재시도0. 이론5/10와 코딩8/10, 합계13/20이다. 원래 작업33/88, 중앙 승계관측28/88, 88IDs/17edges, 원래 노드 증분0을 보존한다. 이 문서의 직접 유도와 동일작성자 검산은 독립 R6/C9 완료가 아니다. 전체 물리적 수용은 NOT_ISSUED다.

## 1. 질문과 재사용한 근거

C7은 고정 BASS 거래에서 caloric 끝점과 prescribed driver의 차이 -0.075312503004739219596232 K 및 저장/재구성 끝점 표현 잔차 -6.2972569110885162919257e-67 K를 남겼다. C8의 질문은 이 두 차이가 숫자 표현과 산술 정밀도에 얼마나 민감한가, 그리고 양의 분모에서 어떤 조건수와 유한 섭동 경계가 필요한가다.

원래 3554206-byte BASS 원자료, provider, C7 consume_saved_source 및 C6의 27개 suite를 재실행하지 않았다. 첨부 C7 증거 capsule(212516bytes, SHA256 11628bb0754b76468c11b8f1d7f6b4f2bce45368555f9543dd2527bc04bf79b4)을 읽고 그 안의 attempt_01/stdout.txt(19293bytes, SHA256 2c9601a3a0baf66ce848b831b0695c600c69973f5372d05fa7045a4c99ec2948)의 정확한 분자/분모를 입력으로 사용했다. 원문과 기존 계산 모듈은 변경하지 않았다.

C7의 source pin은 BASS634c3046ffccc5d00f1ab7588b5834a6eb8053ad와 rawSHA256 a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac이다. C8이 실제로 읽은 것은 그 원자료의 저장된 C7 소비 결과이며, 새로운 provider solve가 아니다. C7의 45개 검산과 CAS3개는 기존 근거로 남기고 이번 새 검사 수에 합산하지 않는다.

## 2. 정의와 직접 유도

공통 기준부피 V0당 열적 입자수 D>0, 기체 병진에너지 E>0, 입자당 열용량 cv>0를 사용한다. T=E/(cv D)이며 단원자 source bridge에서는 cv=3k_B/2, k_B=1.380649e-23 J/K를 유지한다. 원자 저장에너지나 광자를 기체 열 Q에 더하지 않고 적분된 기하학적 일 W를 한 번만 적용하는 기존 계약은 바뀌지 않는다.

cv를 고정하고 u=deltaE/E, n=deltaD/D, u,n>-1이라 두면

T'/T=(1+u)/(1+n),
(T'-T)/T=(u-n)/(1+n).

분모를 통분하면 선형항 u-n 뒤의 정확한 나머지는

R2 = n(n-u)/(1+n)

이다. |n|<1이면 |R2| <= |n|(|n|+|u|)/(1-|n|). 따라서 고정 방향 u=h*u0,n=h*n0에서 양의 분모 여유를 유지하는 한 나머지는 O(h^2)다. 이는 시간 적분법의 수렴 차수가 아니라 이 유한 대수적 사상의 국소 전개다.

각 좌표의 상대 섭동을 같은 infinity norm으로 제어하면 dlogT=dlogE-dlogD이므로 국소 상대 조건수는2다. cv를 독립적인 세 번째 입력으로 흔들면3이다. 공통 양의 배율 (E,D)->(sE,sD)는 정확히 상쇄한다. D의 단위나 크기만으로 상대 조건수가 발산한다고 말할 수 없으며, 절대 오차가 D에 비해 얼마나 큰지와 분모의 양의 여유를 구별해야 한다.

0<=rhoE,rhoN<1인 전체 상대오차 상자에서 T'/T는 분자에 증가, 분모에 감소하므로

[(1-rhoE)/(1+rhoN), (1+rhoE)/(1-rhoN)]

이 정확한 상이다. 최악의 상대 변화는 (rhoE+rhoN)/(1-rhoN)이고 u=+rhoE,n=-rhoN에서 달성된다. 선형 경계 rhoE+rhoN에 대한 증폭은 1/(1-rhoN)이다. 상관된 허용집합에 이 상자를 적용하면 enclosure는 유지되지만 sharpness는 일반적으로 사라진다. 모든 입력이 공통 배율을 공유하면 실제 온도 변화는0일 수 있다. 이 실험의 상자는 합성 섭동이며 실제 source/물리 오차반경을 새로 공급하지 않는다.

## 3. 실제 저장점의 조건수

| 대상과 입력 좌표 | 조건수 또는 여유 |
|---|---:|
| T(E,D), cv고정, 상대 infinity norm | 2 |
| T(E,D,cv), 독립 세 좌표 | 3 |
| E=cv*Na*Ta+Q+W의 합산 | 1.000430848797900889842747 |
| D=Na+deltaN의 합산 | 1.000208582130001227042723 |
| 온도 증분 분자 Q+W-cv*Ta*deltaN | 2.877268109093121182338700 |
| 저장 온도 minus right driver의 직접 뺄셈 | 79759.80132671409379722007 |
| 저장 minus 재구성 온도의 직접 뺄셈 | 9.538811976998153659903890e69 |
| 잔차 분자 rE*D-E*rN | 2.597908722411708146339351 |
| D/Na | 0.9998957198104914087954201 |
| E/(cv*Na*Ta) | 0.9997846219987260266724913 |

합산의 조건수는 각 독립 항 절댓값 합/합의 절댓값, 뺄셈의 조건수는 (|a|+|b|)/|a-b|다. 서로 다른 입력 좌표를 가진 조건수들을 같은 모형의 물리적 민감도로 동일시하지 않는다. 현재 온도 자체와 에너지/입자수 조립은 안정적이지만, 약3003K인 두 값을 빼서 약1e-67K 차이를 얻는 연산은 약70자리의 상쇄를 겪는다.

## 4. 정밀도 사다리: 직접 뺄셈과 잔차 전파

기존 R5 식을 그대로 쓴다. rE=Ub-E, rN=Nb-D일 때

Tb-T = (rE*D-E*rN)/(cv*D*(D+rN)).

Decimal ROUND_HALF_EVEN 정밀도16,24,32,48,64,70,80,100,120에서 저장된 정확한 유리수와 대조했다. 다음 상대오차의 분모는 비영인 정확한 저장 표현 잔차다.

| 유효 자리수 | 직접 계산한 차이 K | 직접 경로 상대오차 | 잔차식 상대오차 |
|---:|---|---:|---:|
|16|0E-12|1|3.63956e-16|
|24|0E-20|1|2.24024e-24|
|32|0E-28|1|2.03890e-32|
|48|0E-44|1|4.64138e-48|
|64|0E-60|1|1.53288e-64|
|70|-1e-66|0.587993|1.22259e-70|
|80|-6.297256912e-67|1.44743e-10|2.23593e-80|
|100|-6.29725691108851629192565410738e-67|8.68887e-31|8.40762e-101|
|120|약 -6.2972569110885162919256541073745283944950090296493e-67|1.14407e-50|5.84471e-120|

가장 중요한 전제는 rE,rN을 이미 정확한 저장 유리수에서 확보했다는 점이다. 원래 큰 에너지/입자수를 먼저 binary64로 반올림한 뒤 잔차를 새로 빼서 잃어버린 정보를 복구했다는 실험이 아니다. 잔차식은 보존된 작은 입력에 접근하는 다른 계산 경로다. 이 단서를 제거하면 낮은 정밀도로 원래의70자리 물리 정보를 생성한다는 잘못된 주장으로 바뀐다.

Binary64로 저장 중간값을 반올림한 온도는3003.417482286277K, 정확한 저장 온도에 대한 상대오차3.8067609922761155e-17이다. 정상 범위의 세 입력 반올림과 두 산술연산에 대한 gamma5=5u/(1-5u),u=2^-53=machine unit roundoff의 경계5.551115123125786e-16 안에 있다. 직접 끝점 차이는0이지만 보존된 잔차를 반올림해 쓰는 식은 -6.297256911088517e-67K, 상대오차9.722165508991066e-17을 준다. 이는 산술 정확도이며 물리 오차 보증이 아니다.

정확한 최종 온도의 표시용 반올림을6,12,16,24,48,70소수자리에서 따로 검사했고 각 half-ulp 경계를 만족했다. 최종 표시 반올림의 경계를 전체 연산 오차의 경계로 사용하지 않는다.

## 5. 디코더와 온도 상수 관례의 분리

기존 원 JSON숫자의 binary64 해석을 직접 exact-decimal 해석으로 바꾸는 반사실적 진단을 수행했다. 캐시된 H/전자 stocks와 Q/W는 고정하고 명시적 literal만 바꾸므로 이는 자기일관적인 새 provider 모형이 아니다.

모든 해당 literal을 바꿨을 때 재구성 온도 변화는 +1.4617995068338231e-13K, 저장 caloric 온도 변화는 -6.518952126342385e-15K였다. 각 NH,fHe,Tm-energy,EV의 영향과11개 field별 표현 차이를 원 결과에 보존했다. 현재0.0753K driver 차이를 이 디코딩 차이만으로 설명할 수는 없다.

별도로 source kBoltz와EV가 정하는 energy-temperature/native-K 배율은1.0000011300311275400297이다. 동일한 저장 기체 에너지를 유지하며 right driver만 같은 energy-temperature 관례로 옮기면 gap은 -0.07531250300473922K에서 -0.07870654335419331K로 바뀌고 부호가 유지된다. 이는 비교자 단위 관례 진단이지 온도 피드백이나 물리 상수의 새 추정이 아니다. 기존 원자료는 덮어쓰지 않았다.

## 6. 실행·코드 대응과 그림 검토

code/study.py가 고정 C7 capsule 및 그 안의 saved-output hash를 검사한 뒤 Fraction/Decimal로 위 식과 선택된 섭동을 평가한다. 생산 계산 모듈을 import하지 않는다. code/observe.py가 단일 child의 시작/import/계산/직렬화/종료를 포함하는 wait4 CPU를 기록했다. code/plot_c8.py는 저장 C8_RESULT.json만 읽는다.

81개의 이름이 서로 다른 검사:source-bound5,scope1,box-extrema10,sharp-bound10,domain5,correlated5,Taylor22,precision11,arithmetic3,counterfactual-binding3,display6. 이것은81개 독립 물리 주장이나81개 기존 unittest 메서드가 아니다. 모든 검사는 첫 실험에서 통과했고 허용기준을 수정하지 않았다. 기존 production code 변경0, primary source rerun0, 기존27fixture rerun0이다.

PRECISION_DEFECT 그림은 직접 뺄셈의 상쇄 plateau와 보존 잔차식의 정밀도 개선을 보여준다. POSITIVE_MARGIN 그림은 합성 상자의1/(1-rhoN) 증폭과 공통배율 상쇄의 구별을 보여준다. 두 그림을 직접 확인했으며 라벨/단위/범례/표시 경계가 맞고 자름이나 겹침을 발견하지 않았다. 첫 그림의 작은 오차를 실제 온도의 물리적 불확실성으로 읽지 말라는 주석과 둘째 그림의 synthetic 표기를 유지했다. 그림은 별개 PNG/SVG이고 데이터 생성 실험은 재실행하지 않았다. 출력 도구가 runpy의 globals사전을 추가 표시한 부수적 출력은 수치 결과나 추가 실행이 아니다.

## 7. 자원·재현성과 근거 수준

실제 명령은 /opt/pyvenv/bin/python -B -S code/study.py <pinned C7 capsule> <new result>이며 원래 절대 argv와 interpreter는 PROCESS.json에 있다. Python3.13.5 현재-turn 실행은 PYTHON_PASS, C++는 미탐침이다. Native subagent NOT_RUN, controller-direct 동일작성자 실험이다. 새 프로덕션 기능을 수정한 작업이 아니므로 red/green TDD cycle을 주장하지 않는다.

Child terminal CPU0.061126s=user0.048771+system0.012355,wall0.062064622s,exit0,attempt1,retry0,maxrss13948KiB였다. Observer CPU prefix0.027123939s는 별도이며 child에 이미 포함된 비용이 아니다. Plot post-import CPU1.377940414s도 별도이고 import/kernel비용은 포함하지 않는다. 이 단일 짧은 실행은 성능 향상 benchmark가 아니다.

현재 요청에 따른 새 C8 할당을 실행 전에 PREEXEC.json으로 고정했다:primary30CPU s/wall120s/memory512MiB/worker1,stage예약60CPU s(primary30+plot10+로컬보존20),recorded cumulative ceiling120CPU s. 이전 닫힌C6/C7 예약을 재사용하지 않았다. 현재 단계할당은 종료하며 미사용 예약을 다음 노드에 이관하지 않는다.

이월 partial planning16.203096885에 새 child0.061126만 더하면16.264222885CPU s다. 이전·현재 별도 기록과 미계측 metadata/observer/plot/import/connector/model비용은 여전히 추가되며 UNKNOWN_NOT_ZERO다. 전체 대화CPU나 전체cap준수를 주장하지 않는다. presentation lower48.263016494,main595.225063/600 NO_MORE_IVPs,ZIP미승인 상태와 과거 실패를 보존한다.

직접유도는 derived, 실험은 numerically checked/implementation-verified의 선언된 C8범위이며 non-author scientific admission은 미완료다. 새 CAS/SciSpace/Exa 과학 실행0,기존 문헌 근거재사용. Python3.13 Decimal 공식 문서는 정밀도·반올림·숫자변환 의미의 참고만 제공하며 이 코드의 정확성을 인증하지 않는다. NIST 직접상수URL 조회는 쿼리형식오류여서 새 상수확인근거로 채택하지 않았다. 여기서 k_B는 고정된 기존 SI계약이다.

## 8. 최신 조사·출처의 범위

현재7개 관련 저장소의 선택ref와 최근PR검색,해당단위 대화/파일검색,기존C7백업 정확한ID메타데이터를 조회했다. 작업HEAD7d1cf19e...와AGENTS blob6464cd96...는 그대로다. BASSfed29a01...,HEa73773a9...,CR729cb951...,REC5438f2a0...,Vigil7eb2dd0...의 선택ref도 이전관측과 같다. WU는c0b97999b928acb04a805bf3e5283af73aff9831로 진행됐으며 실제commit diff는R11자체20/20,DAG23/38,primary214/reference900와physical INPUT_PENDING/centraldelta0을 구별한다. 이 소유자의 결과를 재현한 것으로 세거나 우리물리bath·독립검토·예산으로 이관하지 않았다.

중앙ref3d8bcdb79a7062459adaad9be6d7fe951f86a17a는재확인됐고 이전명시적count authority28/88을승계한다. 전체DAG를새로세지않았다. 최근7repo PR색인검색은PR240만반환했으나 WU의직접ref변경이있으므로 검색부재를변경부재로판단하지않았다. 이전1428branch-name census는역사적근거이며이번전수조사라고재명명하지않는다. 모든branch본문·개인대화전문·backupbytes전수열람은아니다. 대화/Files검색은본단위의별도C8완료/독립review를확립하지못했고무관한결과를권위로쓰지않았다.

C7 Drive1Jl6k3Lh8Ky1_8VHS74eWw2DdkBBWMELP와Dropboxid:BSpOijBcT10AAAAAAEDJTw의metadata는212516bytes로재확인했다. 실제읽은첨부capsule의전체SHA와선택payload를확인했으며새원격whole-download를주장하지않는다. 기존C7/116파일/sourceZIP은재생성하지않는다.

## 9. 판정과 다음 의무

C8 scoped 완료로12/20에서13/20이다. 온도비율은선언된상대좌표에서잘조건화돼있고,아주작은표현차이는직접뺄셈에극도로민감하다. 기존Fraction/잔차보존경로가이미필요한정보를유지하므로생산코드수정은하지않는다. 실제물리radii,thermal-feedback수렴,fullsolver또는speedup은이번판정에포함되지않는다.

다음의무는R5와source-bath binding,C5–C8실행근거를대상으로하는한번의실제비작성자검토(R6/C9의열린질문통합)다. 동일작성자의재독/새CAS를독립검토로표시하지마라. C8을재실행하거나같은조사를반복하지않고현재증거를검토자에게넘긴다. 원래DAG및L4/global/physicalnull경계는유지한다.
