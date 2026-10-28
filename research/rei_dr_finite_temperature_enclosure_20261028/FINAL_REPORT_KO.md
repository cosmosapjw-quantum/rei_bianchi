# 연구 루프 결과와 실행 준비 인계

2026-10-28 UTC. 요청한 physmath-research-loop workflow1.0.0을 기준으로 수행했다. 현재 결과는 **방향미분 단위20/20 완료**, 다음 실제 DR 유한 온도 단위 **이론10/10 + 코딩 준비5/10 =15/20**다. 새로운 DR 수치/그림 실행은 NOT_RUN이다. 현재20/60 승인 한도는 별도 스레드의 새 실제 비용을 합친 뒤 소진되어, 남은 두 명령에는22/62의 구체적 추가 승인이 필요하다.

## 1. 완료한 방향미분 단위

PR244: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/244
완료 commit:17f86ce952eaeee265bf7b87d27d571321b629d3.
고정 과학 소스:9c2d0d286747d6e74f863a77c92f2f7cd03a3aa4.

R1–R10/C1–C10의20단계를 닫았다. 이번 승인 이후 C6–C10 원문, 한 차례 실제 A–G 실행, 저장 데이터만 이용한 한 차례 그림 생성, 독립 검토 원문과 실제 이중 ACK를 추가했다. 전체 이전 suite, 원천 생성기, IVP는 다시 실행하지 않았다. 새 과학 코드 수정이나 재시도도 없었다.

과학적 판별은 검사 개수와 구별한다. 열린 구간의 제조 기준값dT=11/6, 이동 절점에서 좌우 기울기에 따라 달라지는 방향미분, 허용된 끝점 방향, 좌표 공변성과 제공된 callback 합성 경로를 확인했다. 절점에서 양의 방향 정답1/3에 대해 단순 중앙 차분5/12는1/12만큼 다르다. A/B의 정확 유리수 오차는 raw JSON에 있고 C–G는 고정 테스트 원문과 실제 PASS 로그로 결속된 assertions다. C–G의 개별 raw scalar export가 있다고 주장하지 않는다.

실제 PNG를 root와 독립 reviewer가 읽었다. 수치 whole command0.132523+별도 supervisor prefix0.002303177=0.134826177CPU-s, 그림 whole1.851244+별도 prefix0.014470814=1.865714814CPU-s다. 내부 worker/plot-prefix는 다시 더하지 않았다. 공개된 runtime 원본30파일의 Git blob 일치와 최종 영수증 원문 일치를 다시 읽어 확인했다. C6–C10 각각의 원문 캡슐5개와 최종 post-ACK 캡슐은 두 provider의 실제 완료 ACK 및 별도 metadata readback을 받았다.

이 단위는 제공된 caloric graph와 callback의 조건부 방향미분이다. 실제 REI EOS/온도/전체 native25/radii를 새로 정한 결과가 아니다. 기존 finite_thermal 실제 native 검토와 F1 원문 교정,81-check와158-check의 별도C8 근거, 다른 atomic-storage20/20은 재실행·합산하지 않고 유지한다.

## 2. 최신 소스 조사와 그 한계

조사 창은10:37:59.205–10:55:37.738UTC다. 접근 가능한 repo metadata51개를 확인하고 관련15repo의 현재 branch refs를 끝 페이지까지 조사했다.41페이지 중15개는 명시적 빈 종료 페이지다. 관측한1,478refs/1,451tip 중1,462refs는 이전과 같고7개가 바뀌었으며9개가 추가됐다. 사라진 ref는0개다.1,435개의 불변 tip metadata를 재사용하고 새16개만 읽었다. 최근 ancestry16페이지의162개 고유 commit 및12개 최근 PR 기록을 확보했다. 본인PR244는 다른 owner의 새 과학 결과로 세지 않았다. 전체133개 read query와 원문/오류가 보존돼 있다.

그 뒤 실제 source-history head 변화 하나만 추가로 읽었다.10:59:17.109–10:59:34.478UTC의5개 query와3개 원문 blob이 PR246의 실제 완료 비용을 확인했다. 본 조사 원장은 변경하지 않고 late addendum으로 붙였다. 다시 전체 census를 반복하지 않았다.

주요 종합 결과는 다음과 같다.

| 소스 | 실제 확보된 범위 | 이번 선택에 주는 의미 |
|---|---|---|
| PR237 ee6746ab… | native thermal point source와 온도JVP, Maxwellian 조건부 DR loss 및 Mao RR 선택 | 온도미분 자체가 전혀 없다는 넓은 이전 표현을 교정했다. 새 의무는 유한 온도 구간의 경계다. |
| PR241 41d2d92a… / VigilODE95 36104bfc… | 외부에서 제공된 고정 effective rates의 chemical polynomial/Jacobian/remainder | 실제 온도 의존 rate box와 전체 REI25 결합을 대신하지 않는다. |
| PR245 cc17c248… |17 thermal+2fast 외부 생성·흡수의 예시/QSS source-response | DR 온도 구간 인증과 별개다. 실제 새 비용과 닫힌 tail 예약은 합산했다. |
| PR246 ea805aef… | source-history/QSS 단위의 새 실행·전달·비용 원문 | 준비 상태였던 기록이 실제 완료로 변했다. 이 late debit 때문에 추가 실행을 보류했다. |
| REC146 | 점별 Fe=FH와 writer/query 대응 | 전체 coefficient box, inverse gain, physical tube를 제공하지 않는다. |
| BASS/HE/CR/WU 새 owner 결과 | 각각의 조건부 memory, angular, energy-support, forcing 결과 | 실제 열용량/thermal deposition/EOS, HD state 등 열린 입력을 닫은 결과로 통합하지 않았다. |

대화 검색은 연결된 검색 도구가 반환한 project 관련 lead를 실제 원문과 대조했다. 모든 대화의 열거 기능은 제공되지 않았으므로 모든 private transcript를 읽었다고 하지 않는다. 백업은 선택한 provider 목록에서 새 metadata122건을 확인했다. Dropbox의 관련 반환 페이지는 끝까지 읽었지만 Drive dossier는1,000개 제한과 continuation token 부재로 일부다. 새 큰 archive를 복원하지 않았으며 metadata 발견은 과학적 수용으로 세지 않았다.

새 evidence archive는251개 기존 근거 파일, 두 보존 설명과 manifest를 담은254-entry ZIP_STORED다.16,566,195bytes, SHA2564679cf87cc0e4c324b594bfc9d873d5e970c191f3368567aed12a6fe63eec5f7. 양쪽 실제 ACK와 크기 readback을 받았다. 이전11MB census archive는 정체성과 기존 ACK로 참조하여 다시 포장하지 않았다. 공개 원문 보고서는intake/census, 원자료 보존 영수증은별도delivery에 있다.

## 3. 선택한 다음 이론: 실제 signed DR 함수의 유한 구간 경계

PR247: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/247
새 단위:rei_dr_finite_temperature_enclosure_20261028.
최종 구현 과학 소스 pin:f43eaf9b16b98e1799f21a93b4555fe7d0ffaf9a.

PR237의 REC119와 PR241 아래 BASS 원천은 atomic_network.py, atomic_coefficients.json, atomic_model.json의 Git blob과SHA256이 각각 동일하다. 계수 SHA256은38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc다. 주변의 photo, density, clock, electron pool 모델까지 동일하다는 뜻은 아니다.

온도T는K이며 공통 runtime 정의역은100≤T≤10^6이다. 계수와s=Float64(1e-6),k=Float64(1.380649e-23)를 native JSON/float 변환 후의 정확한 binary64 실수 이미지로 고정한다. 선택한 함수는

$$
g_E(T)=T^{-3/2}e^{-E/T},\quad
\alpha(T)=s\sum_jc_jg_{E_j}(T),\quad
L(T)=ks\sum_jc_jE_jg_{E_j}(T).
$$

alpha의 단위는m³/s, L은J m³/s다. L은 선택된 전자 운동에너지 손실이며 결합에너지 저장고는 별개다. native 전체 연산 순서의 반올림 오차나 원자 적합 오차를 감싼다고 주장하지 않는다. DR 공식/단위의 primary source는 https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/ 이고 실제 계수·closure는 고정된 프로젝트 원문으로 결속했다.

| 초기 채널 | 실제 c 원문 | 실제 E/K 원문 |
|---|---|---|
| He+→He0 |0.001417,0.0002235,−2.185e−5|463300,553200,888700|
| Li+→Li0 |2.941e−5,6.068e−5,−7.753e−7|634500,702400,827100|
| Li2+→Li+ |0.0001451,0.005789,1.889e−5|852900,1056000,11700000|

첫째, g'_E=g_E(E/T−3/2)/T이므로 최대 후보는 두 끝점과 내부의2E/3이다. 최소는 두 끝점 중 작은 값이다. 각 음수 계수는 구간 끝점의 순서를 뒤집어 곱하고 합한다. 여러 항의 극값이 같은T에서 난다고 가정하지 않는다.

둘째, 실제 signed 두 행에서E2≥E0이고c0>|c2|이므로

$$
c_0g_{E_0}+c_1g_{E_1}+c_2g_{E_2}
\ge(c_0-|c_2|)g_{E_0}+c_1g_{E_1}>0.
$$

손실에는c_jE_j를 같은 방식으로 쓴다. 정확한 decimal 원문 기준 양의 여유는 He+의 경우0.00139515 및637.078005, Li+의 경우0.0000286347 및18.01939437이다. 별도 원문 증명은u=2^-53의 binary64 변환 오차를 포함해도 부호가 바뀌지 않음을 보인다. 세 번째 행은 전항 양수다. 이로써 선택한 실제 함수의 strict support를 증명했다. 다만 low-T binary64 exp는0으로 underflow할 수 있고 이는 source에 채널이 없는 경우와 다르다.

음수 항을 지우면 alpha는s|c2|g_E2만큼, L은ks|c2|E2g_E2만큼 엄밀히 증가한다. 이것이 clipping이 실제 보존된 fit을 바꾼다는 구체적 반례다.

셋째,D=T d/dT,x=E/T이면

$$
Dg_E=(x-3/2)g_E,\quad D^2g_E=(x^2-4x+9/4)g_E.
$$

q2의 절댓값은x구간 두 끝점과 포함되는x=2만 검사하면 상계가 나온다. 각 커널 최대M_j와 이를Q_j라 하면B2=Σ|w_j|M_jQ_j는|D²F|의 균일 상계다. 따라서같은온도구간에속한T0와T0e^h에대하여

$$
|F(T_0e^h)-F(T_0)-DF(T_0)h|\le B_2h^2/2.
$$

양·음h모두 적분 나머지식으로 증명했다. 코드가 실제 enclosure를 만들 때는F0,DF0,h자체의 산술 구간도 포함한다. 조건부 energy identitykT(3alpha/2+Dalpha)는 직접DR loss식으로 정확히 환원된다. Mao 선택은RR만 바꾸므로 이DR범위는 기존closure를 바꾸지 않는다.

SciSpace는10개 discovery record를 반환했으며 중복을 합쳐 실제 읽은 새 primary paper는Mao/Kaastra/Badnell의관련정의와공식authorDR페이지다. Exa는그두원문을대조했다. Wolfram의단일제한검산은세차이식을모두0으로반환했다(관측kernelCPU0.00341s). 이는실제native독립검토를대체하지않는다.

## 4. 실제 독립 검토, 발견과 수정

실제 reviewer task ID는/root/current_repo_census다. Root가이론을작성했고/root/acquire_preserved_evidence가구현을작성했다. /root/finite_thermal_blind_reviewer는이단계에서소스/문헌intake와기계적포장을맡았다. 이름에blind가있어도이번DR검토는공유파일시스템과앞선census맥락이있으므로완전blind라고부르지않는다. 외부GitHub봇/부모역할극/CAS/Pythonprocess를native reviewer로대체하지않았다.

R6초기판정은11:04:18UTC PASS_SCOPED_INDEPENDENT_THEORY로고정됐으며, 코드/test원문검토전이다. 이론문서전체, positivity보충증명, 실제source5파일및정체성/예산원장을읽었다. D1–D5의수학적수정요구는없었다. 이후별도정적코드보고서는실제두문제를특정했다.

| 발견 | 구체적 경로/반례 | 최소 수정과 현재 판정 |
|---|---|---|
| F-ZERO |taylor('2:1',100,101,100,100)에서ln1의next±가subnormal이되어remainder계산의trap에걸리는소스경로|검증된동일끝점은h=[0,0],radius0,enclosure=f0반환. alpha/L두미실행control추가. CLOSED_STATIC.|
| F-FAMILY |내부leaf의setsid가외부sessionCPU감시와killpg에서벗어남|leaf를부모session에유지하고내부watchdog는단일PID종료. CLOSED_STATIC.|
| F-PLOT1 |표시문자열앞12자만잘라지수부가사라짐|.5E표기,정규화및개별signed-h축표기. CLOSED_STATIC;실제그림은없음.|

F-ZERO/F-FAMILY는한번의범위고정author수정으로처리했다. 수정전bytes와해시,초기report,실제diff,수정후읽기및정체성검사를모두보존했다.7개preparedidentity가독립readback과일치한다. source-derived반례를실제실행에서관측한exception이라고쓰지않는다. 현재C9는STATIC_ONLY_NOT_RUNTIME_ACCEPTED이며완료수에넣지않는다.

## 5. 단계·게시·이중 ACK

R1–R10완료와C1–C5준비완료로15/20이다. C6/C7/C8 NOT_RUN, C9정적검토만완료, C10인계준비만완료다. 이번단위의실제완료15단계는각각Gitcommit과full원본evidencecapsule의Drive/Dropbox완료ACK및별도metadata읽기를받았다. 공개된최종원본101파일의Gitblob은f43eaf9b…에서모두일치했다. full캡슐은provider에보존하고그구성원본과원장은Git에게시했다. provider파일을다시다운로드하여원격hash를검증했다고하지않는다.

각stage의commit·capsuleSHA256·실제providerID·size는delivery/STAGE_DELIVERY_ACKS_FINAL.json에있다. 당시pending인ADMISSION/STAGE_LEDGER는보존하고이최종전달원장이실제ACK상태를덧붙인다. runtime상태를바꾸거나C10완료로승격하지않았다.

원래DAG는working33/88,central28/88,88IDs/17edges,delta0이다. 중앙pin66ef9a0147a0573b77e74e151dc280ba2bd4b64c와원래working505996e343f2638afcca05b70c12f1e8129e50d9에서확인했다. L4_ready=false,global_physical_completion=null,실제REI T/native25/physical radii=null을유지한다. 로컬연구단계의완료수를원래DAG완료수에더하지않는다.

## 6. 예산 상태와 남은 두 명령

공통상속PR243의17.295332885/54.561494494를한번만계상했다. 방향미분의실제새비용, PR245와PR246의서로겹치지않는새실행및닫힌tail예약을합쳤다. DR CAS는실제0.00341을포함하는총0.05예약을유지했다. 둘을다시더하지않았다. 세stage포장과새조사archive의관측CPU prefix합0.318182856은presentation에추가했다.

현재알려진비용과보존예약은planning21.004288062/presentation60.096621164CPU-s다(최종resume포장비용은관측되는경우별도후속영수증에추가). UNKNOWN_NOT_ZERO는없애지않고whole-sessionbudgetPASS를주장하지않는다. 현재20/60으로새수치/그림작업을시작할수없다. 이중백업등필수보존을마무리했으며새과학실행은보류했다.

요청하는증액은현재DR의C6–C10만완료하기위한절대누적planning22/presentation62다. 아직승인된값이아니다. 새수치예약은0.4+별도tail0.2,그림과renderer는1.5+별도tail0.3이다. 현시점기록에이를더하면21.604288062/61.896621164이며최종작은포장prefix는별도추가한다. 다른30/65승인,제안된main700을이전하지않는다. main595.225063/600 NO_MORE_IVPs는그대로다.

승인후sourcepin과새권한을기록하고아래첫명령을한번실행한다. 실제raw scalar/오차/exit/전체waitedcommandCPU를읽어독립runtime검토후둘째명령을한번실행한다. 둘째는저장JSON만읽고rate/test를다시돌리지않는다. 실제PNG를읽고C8/C9를판정한후C10의원문게시·이중ACK를완료한다.

~~~bash
python -B -S code/execute_bounded.py numerical --execute-authorized
python -B -S code/execute_bounded.py presentation --execute-authorized
~~~

자동retry/fallback/IVP/다음노드실행은없다. 실패시원자료와비용을보존하고원인에맞춰판단한다. 이론R1–R10,닫힌원감사,전체census와기존suite를안심용으로반복하지않는다. 이후RR/Mao와nb/H를포함한effective-ratebox가후속의존성이지만현재AUTO_NEXT_NODE=false다.

