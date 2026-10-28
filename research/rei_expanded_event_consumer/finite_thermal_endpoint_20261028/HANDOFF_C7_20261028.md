# C7 고정 원자료 통합 검증: 실제 결과·게시·백업 인계

2026-10-28 KST. cosmosapjw-quantum/rei_bianchi.
Branch: research/rei-causal-prefix-consumer-20261027. Draft PR240.
Base: ded32cd6c3201a15d05c43472180f4f8689fad02.
C7 evidence commit: e086133df76bb27cf35e863ceade4e862de6f130.
C7 evidence tree: 22f37d635c6bdb8484c349beda10ffd0b45d6119.
이 post-ACK 인계서의 containing commit은 현재 branch에서 확인한다.

## 결과와 수용 범위

PASS_SCOPED_C7_REPRESENTED_SOURCE_CALORIC_VALIDATION.
실제 fixed BASS 원자료와 11-field literal packet을 한 번 소비했다. Worker/외부 exit0, 수정0, 재시도0. 기존 C6 27fixture와 provider/IVP/old campaign 재실행0. 별도 saved-output checker45/45, 정확한 온도차 분해 합의 잔차0, Wolfram의 유리식3개 잔차0. 같은 작성자의 다른 산술 및 CAS이며 독립 R6/C9가 아니다.

현재 R1-R5 5/10, C1-C7 7/10, 합계12/20. 새 완료 단계는 C7 하나다. 기존 atomic-storage20/20은 별도다. 원래 작업33/88, 중앙 관측28/88, 88IDs/17edges, delta0. L4_ready=false, global_physical_completion=null. 실제 REI bath/temperature/native25/physical radii는 null이다. C8·독립 R6/C9·전체20/20은 미완료다.

## 핵심 실제 수치

단일 온도·비상대론적 단원자 source caloric 모형 U=cv*N*T,cv=3*k_B/2. N과U/Q/W는 공통 기준부피당 값이고 Q/W는 gas 소유의 이미 적분된 에너지다. He B=NH*fHe와 별도 저장 전자를 count에 포함한다.

저장 caloric 끝점:3003.417482286276822K.
Prescribed right driver:3003.492794789281561K.
Caloric-driver 차이:-0.07531250300473922K.
저장-사건재구성 차이:-6.297256911088516e-67K.
후자의 표현 잔차를 전자의 driver 불일치나 물리 오차반경과 혼동하지 마라.
초기 energy/native 관례 차이:+0.003394328550400922K.
H-only 분모 오연결은3211.999371310258K,6.944818369546268% 과대평가.
W 중복 적용은0.5100352186318024K 추가 냉각.
이는 잘못된 연결식의 대조이며 원자료·생산 경로의 변경이 아니다.

T_saved-Td_b = Q/(cv*D)+W/(cv*D)-Ta*DeltaN/D
 +(Ta-Td_a)+(Td_a-Td_b)+(T_saved-T_rec).
정확한 num/den과 원 출력은 capsule에 보존돼 있다. 표시값은 반올림이다. Prescribed rate-driver를 caloric 끝점이나 coupled REI 온도와 자동 동일시하지 마라.

## 입력·구현 정체성

BASS source commit634c3046ffccc5d00f1ab7588b5834a6eb8053ad.
Source path research/bass_b3h_qss_channel_completion_20261027/results/FINITE_CHANNEL_RESULT.json.
Source3554206bytes,SHA256a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac.
Literal packet8281bytes,SHA256b77aba9612584ffd74e2cdd951c0b9e2b573113bd7195c04d8cc857354cfe34f.
새 core/runner/test 변경0, 실행 전후 identity일치. C6에서 검증한 같은 구현을 사용했다.
원 source-text Drive1M2W7SEk-rqwJTvOr9PbLc6jMGNXpBPEu의4699240bytes를 전체SHA d77ea863ad2730f6ef0be27a3f3a93c8b5c864f3d863b4b1b5950fd61a6ef63e와 대조해 필요한 source 한 파일만 추출했다. 전체116파일 복원이나 옛bundle/ZIP 재생성은 하지 않았다.

## 읽기와 재현

기준 경로 research/rei_expanded_event_consumer/finite_thermal_endpoint_20261028/.
Git 실행 증거: execution/C7_SOURCE_20261028/REPORT_KO.md,C7_SUMMARY.json,EXTERNAL_PROCESS.json.
Full capsule에는 상세C7_RESULT,원 stdout/STARTED/RESULT/authorization,입력identity,checker와관측기/분해코드,45검사,정확한값,figure SVG/CAS원문 등33payload가 있다. Git의3파일과 capsule의33파일은 다른 보존집합이다.
고정 계산모듈과 큰 source 자체는 기존 Git/source-text백업을 재사용하며 capsule에 다시 넣지 않았다. Exact literal packet은 capsule에 포함한다. 원 실행을 재현하려면 immutable source와 세 implementation파일을 기존pin에서 결속하고 새 승인·출력경로를 사용한다. 이미 완료한 primary를 단순 확인용으로 반복하지 않는다.

## 실제 백업 완료

REI_FINITE_THERMAL_C7_EVIDENCE_20261028_e086133df76b.json
212516bytes,33UTF-8payloads.
SHA25611628bb0754b76468c11b8f1d7f6b4f2bce45368555f9543dd2527bc04bf79b4.
Drive1Jl6k3Lh8Ky1_8VHS74eWw2DdkBBWMELP:upload SUCCESS,별도metadata212516bytes.
Drive parent1phclg92jkhC5KgvnXhks8GbOFlya4qGe.
Dropboxid:BSpOijBcT10AAAAAAEDJTw:completed,212516bytes,modified2026-10-28T04:25:17Z.
Dropbox path /bianchi/research_backups/rei_bianchi/REI_FINITE_THERMAL_C7_EVIDENCE_20261028_e086133df76b.json.
Local33payload roundtrip/size/SHA일치. 새 원격백업 whole-download/hash는미수행이다. 원 source-text의 실제원문회수검증과 새백업metadata검증을구분한다. 본인계서는Git-only후속metadata이며 capsule을ACK때문에다시만들지않는다.

## 계측·실패 보존

Primary 외부명령 terminal CPU0.124835s=user0.085669+system0.039166,wall0.125188393s. Worker0.081005s는포함돼있으므로다시더하지않는다. Supervisorprefix0.035586s와observerprefix0.021229141s의범위를구분한다. Saved-check GNUtime표시user0.01/system0.02/wall0.04s는반올림값이다. Plotpost-importCPU prefix1.549246861s이며import/커넥터/모델/보존/기록tail은추가비용이다. Capsule생성prefix0.030428982s도별도관측이다. Exact전체대화CPU나whole-sessioncap PASS는주장하지않는다.

현재요청을다음source integration단계선택으로해석하고새boundedallocation을고정했다. Primary30CPU(20worker+8supervisor+2record),wall120s,512MiB. 단계전체예약60CPU(source30+검사15+그림5+local보존10),recorded cumulative ceiling120CPU. 이단계할당은닫고이전정책상태를복원하며잔여량을자동이관하지않는다. Historical planning부분하한16.078261885+이번primary0.124835=16.203096885는부분합뿐이다. 모든별도이전/현재비용과UNKNOWN_NOT_ZERO를보존한다. Presentation lower48.263016494,main595.225063/600 NO_MORE_IVPs,외부owner예산은불변이다. ZIP작업미실행.

직접HTTP DNS실패와plot저장PermissionError는보존했다. Input은Drive원문을통해복구했고,figure는같은메모리객체를notebook소유경로에저장해복구했다. 실제그림을읽고숫자여백만한번조정했다. 과학재실행0. 모든workflow시도가성공했다고표시하지마라. Current Python실행PASS,C++미탐침. Native subagent NOT_RUN.

## 최신 조사와 다음 단계

이번7repo선택ref/최근PR/변경WUcommit/정확한backup소스를확인했다. 이전1428branch-name census는역사적재사용이며현재전수본문조사로바꾸지않는다. 전체대화/모든backupbytes열람완료는아니다. WU149d73a0...의R11 12/20,local21/38과CAS경고는별도owner결과다. ActualHDarray/physicalconsumer/densityclock미공급을우리bath로채우지않았다. 중앙ref3d8bcdb79a7062459adaad9be6d7fe951f86a17a및28/88은유지했다.

다음은같은단위C8의소스표현민감도와양의분모conditioning검증이다. 먼저이인계서/보고서/정확한saved결과를읽고주장할오차종류와최소새계산범위를고정한다. 반올림·상수관례·원자료불확실성·물리오차를구분한다. 27fixture/primary를안심용으로반복하지않고C5/C6/C7승인완료를다시묻지않는다. 별도독립R6/C9는준비된근거를실제비작성자가한번검토하며CAS/동일작성자대조로대체하지않는다. 새fullsolver/feedback/원자료재생성/자동다음노드시작은하지않는다.
