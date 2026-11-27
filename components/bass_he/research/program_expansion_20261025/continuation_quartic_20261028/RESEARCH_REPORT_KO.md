# BASS_HE QUARTIC12 연구 보고서
2026-10-28 · physmath-research-loop1.0.0 · R1–R10/C1–C10
정확한 source와 실제 전달 판정은 최종 외부 권위 문서 및 RESULT.json/STAGE_ACKS.json을 따른다. 이 문서는 과학 결과와 근거를 정리한다.

## 핵심 결과
고정 EXFOR 민감도 창을 만족하는 전체 비음수 짝대칭4차 각분포는330MeV에서도 존재한다. 같은 데이터에서 q(1)=0을 추가한 가족은 공집합이다.
두 결론은 서로 다른 조건을 판별한다. EXFOR11의 비음수 전역 Bernstein계수cone 안에서의 EMPTY는 그대로 유효하며, 이를 전체 양의4차 가족의 부재로 확대할 수 없다.
이번 새 범위의 최종 수용은 실제 비저자 최종 검토와 RESULT.json에서 결정한다. 완료수 표시는 시작11/16, 수용후12/16; 중앙28/88,HEdelta0다.

## 1. 최신 조사와 후속 선택
7개 관련repo의18terminal branch페이지에서1,438refs를 확인했다. 이전1,432와 비교해신규6/변경7/삭제0; 알려진EXFOR11게시2건외에외부11변경이다. 선택 owner본문16개는 Gitblob과 일치했다.
Dropbox dossier5,276unique/9terminalpages에서신규27/변경0/삭제0를 확인했다. 신규는EXFOR11단계+최종11개,CRpair-support9개,WUR12일곱개다.
Library오늘metadata329개/2terminalpages,신규·수정106개중프로젝트관련39개와 실제인계·receipt9개를 확인했다.
Drive는index954개와직접자식100개capped view,오늘관련metadata11개를 조사했다. ZIPindexinggap이 있어전체Driveholdings를 완전열람했다고 하지 않는다.
Root의targetedconversation-summary는성공했지만모든대화원문전수열람이아니다. 생성시점의빈providerACK배열과 실제POSTPUBLICATION외부ACK를 구분하여EXFOR11완료를보존했다.
CR의전자쌍support와WU의시간격자forcing은이번핵반응각분포연구와입력·관측량·증명의무가다르다. BASS18/20,REIthermal13/20,RECphysical0/313,VigilODEchemicalscoped20/20의조건부상태를섞지않았다.
분기된VigilODE중앙반환branch를canonicalHEAD로간주하거나전체merge하지않는다.
현재관측자료에는HE물리입력3개를닫을새payload가없었다. 조사한표면외의자료부재를증명하지않는다.
상세근거: SURVEY_SUMMARY_KO.md 및sources/SURVEY_GITHUB_KO.md,SURVEY_BACKUPS_KO.md.

## 2. 이론과 구현에서 바뀐 부분
f(mu)=q(mu²)=b0+b1mu²+b2mu⁴에서signed b를 허용하고q(z)>=0을전구간[0,1]에요구한다.
세nominalz의분리와Lagrange보간에서|b|<=(75,150,75)를유도해B160의포함상자를확정했다. 이는정규화나outcome에따라선택한추가가정이아니다.
부호가있는계수에는nominalangle midpoint오차eps=B(widthz+widthz²)/2를적용한다. 데이터를수축한내부부등식과확장한외부부등식이각각truefamily에대한포함을인증한다.
87deg의양의관측하한과도함수상계에서D=2b0+2b1/3+2b2/5>=49/4800000을증명했다.
고정N1/4/16에서cellBernstein양성은내부집합,gridnode양성은외부집합을준다. 중첩방향은inner증가/outer감소다. 영점을접하는경계다항식의유한inner완전성을주장하지않는다.
q(1)=0일때q=(1-z)[b0+(b0+b1)z]이며정확양성조건은b0>=0,2b0+b1>=0이다. 이2차원case는에너지당한번계산한다.
유리수정점전수열거와공유역행렬로12case를계산했다. signedmoment하한은concave,상한은convex이며양의분모가중Jensen으로필요한정점극값경계를증명했다.
내부정점은실제가능한분포의증인이다. 이를외부경계와합쳐최소값·최대값각각의bracket을제공한다.
알려진Bernstein포함/분할방법을이프로젝트의fullquartic가족에구체화한것이며보편적신규정리나문헌전수novelty를주장하지않는다. Garloff1993,Allen–Kirby2022,Harris–Parrilo2023의primarytext근거는sources/R2_PRIMARY_LITERATURE.md에있다.

## 3. 330MeV의 구성적 증인
정확한저장계수의표시값은b≈(0.140838303,-0.308117512,0.752692956)이다.
q의정확한전역최솟값은양수이며표시값qmin≈0.109306056,z≈0.204676761다.
동일다항식의이전foldedBernstein좌표는a≈(0.585413747,-0.611854653,0.996237097)여서a1<0이다.
따라서기존충분조건cone밖이지만전구간양수인실제데이터적합증인이존재한다.
N1inner는비어있어이증인을제공하지못하고,N4/N16에서같은증인이확인된다. inner공집합만으로배제해서는안된다.
정확한분수증인은evidence/validation/initial/SAVED_PLOT_DATA.json에있다. 위반올림계수를경계fits의대체입력으로쓰지않는다.

## 4. 수용확률
검출기의실험실cosine영역은fullazimuth하에서HEMISPHERES:A[0,1]/B[-1,0],CAPS:A[1/2,1]/B[-1,-1/2]다. 같은사건의두교차수용사건의합집합을쓴다.
아래는8소수자리로바깥방향반올림한외부포함경계다. 모든참된feasible분포를포함하며통계적신뢰구간이나실제생성률이아니다.

| EnergyMeV | Family | HEMISPHERES | CAPS |
|---:|---|---|---|
|213|FreeN16|[0.68262445,0.79669077]|[0.11121960,0.47234396]|
|258|FreeN16|[0.61837610,0.72996144]|[0.06067572,0.33548040]|
|330|FreeN16|[0.84269078,0.84492144]|[0.56910576,0.57480298]|
|213|Endpointzero|[0.68262445,0.74793761]|[0.11121960,0.20088783]|
|258|Endpointzero|[0.64371174,0.72996144]|[0.08848322,0.19563706]|
|330|Endpointzero|EMPTY_OUTER|EMPTY_OUTER|

258MeVN16의최소값bracket은HEMISPHERES[0.61837610,0.61855384],CAPS[0.06067572,0.06112028]이다. 남는유한경계폭을정확한극값으로지우지않는다.
213/330freeN4/N16에서극값bracket간격은대략10^-14수준이지만이는계산경계의정밀도이지물리정확도가아니다.
전체12case와N별bracket은INTERPRETATION_KO.md,OUTWARD_DISPLAY_BOUNDS.json,exactsavedJSON에있다.

## 5. 실제 검증과 자원
새primary1회,7controlPASS0FAIL,12case,132vertices(inner66/outer66),12nestedinclusions.
Exactinverse24,810;singular1,026;invertible23,784;RHScandidates71,691.
WholeCPU4.093938s/wall4.132060s/RSS17,812KiB;120/300capPASS.
Wolfram새평가1회:16literalzero+12literalTrue. remoteCPU/wall은미제공null이며시간제한20s와실제시간을혼동하지않는다.
saved-onlyplot1회:CPU2.569869s/wall2.621741s/RSS80,976KiB;10/30capPASS;scientificimports/calls0/0.
정확savedJSONsha=a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45.
실행sourceS05=2f66fbe31e6d52adb19f6701f58c14c67f6ac204,tree92f2941c65e890eab31adc3043e1cb169abf2e00.
새Python6개,CONTRACT,기존모듈5개를pin했다. 이전EXFOR11결과는hash를확인해읽기만했다.
비저자한pass가source→실제결과→CAS/PNG→최종과학판정→중앙metadata를이어심사한다. 같은시험의반복성공으로검증수를늘리지않는다.

## 6. 한계와 보존 상태
ERR-S창은민감도선택이다. covariance/jointconfidence가없고각도는nominal값이다. 다른에너지격자의totalcrosssection6개를결합·보간하지않는다.
실제편극/방위각법칙,photonflux/history,event/inclusive정규화,liquid-He투영,nonthermalbirth/deposition/thermalization을공급하지않는다.
따라서3physicalinputs는open이며global_physical_completion=null,L4=false,production=NOT_APPROVED,activation=false다.
population_rest_energy_witness가rest/binding의단독owner다. independent_binding_RHS/Gamma_thermal/Cv/species_heating/thermal_deposition=null,birth_pool=UNASSIGNED를유지한다.
HARMONIC10최초24PASS+1FAIL와targeted1PASS/reserve0,EXFOR11최초6PASS0FAIL,KINEMATIC08partial,PHOTON05plotCPU실패를보존했다.
S03즉시source조회불일치는actualref/parent/변경된2blob재조회로해결했고archive재생성/ref재시도/science재실행은0이다.
이번공집합은NG1–NG7심사범위의조건부모형배제이며강한전역no-go가아니다.
다음개선후보는258MeV극값경계또는실제물리입력소유자의새자료다. 새명시적요청전에는후속노드를시작하지않는다.

