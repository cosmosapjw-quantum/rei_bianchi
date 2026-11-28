# BASS_HE B3: 선택형 RCX 원자 공급 경계와 충돌 없는 설치

날짜 2026-10-03. 판정:
`RCX_SOURCE_SELECTED_ATOMIC_EXPORT_AND_COINSTALLATION_VERIFIED__PHYSICAL_SOURCE_DISAGREEMENT_OPEN`.

## 1. 이번에 닫은 제한 단위

B2 handoff의 EOR_B3_RCX_SOURCE_CHOICE_AND_NONCOLLIDING_ATOMIC_EXPORT를 수행했다.
이미 있는 rate 평가기와 create-only 저장기를 byte동일하게새namespace로이관하고,
source선택·범위·원숫자·null moment를보존하는원자packet과CLI를 구현했다.
West광학reference와같은설치target에서공존하고실제호출되는것을검사했다.
이완료는RCX공급경계의기능완료이며 전체BASS_HE,I1–I4,physicalsourceaccuracy가아니다.

## 2. 회수한 실제 근거

부모B2 ZIP4,241,665bytes/SHA256 e045bbbad1e4429c81b034c8f86049a17302891bc3750be57e8fbab992f64c72의
CRC와60payloadsize/SHA를확인했다.새작업은별도root에두고부모를수정하지않았다.
원격HEAD처음읽기는70396fdc38fa64ede799d8a4929a203a422256d6이다.
source-rate코드는9e3d54bf13045b01b3d7a493db78fa3289d3da9d에서읽었다.

- ratecore:8113bytes,Gitblob c3f5cb56b7f5babcbead21694de31b57ca4ff992,
  SHA256 529ae325622718b48292c3b748a7850ccb315733b28bff930388f00915f2d217.
- writer:1003bytes,Gitblob 4738131e4f29cd1ee9b0fe3271f9e7f1cb4855b6,
  SHA256 3dd8d8080216d6e4448d66590e411afdab4b6a801abf37a1c1fad47754c3bd88.

DirectHTTP가DNS오류를냈지만GitHub도구의UTF8본문을회수해로컬bytes의GitblobSHA를대조했다.
새_rate.py/_io.py는이두파일과바이트동일하다.자료없음이나재작성으로대체하지않았다.

GM25 arXiv2511.21966v1AppendixB.3를web에서직접읽어근사식과상충문장을확인했다.
West원문은부모PDF와현재첨부근거를재사용한다.새rawGM25PDF다운로드/SHA는없다.
Liu의원자료나Bianchi물리모형을새로가져오거나변경하지않았다.

## 3. 물리적 공급내용과 한계

유일하게평가가능한등록rate는GM25_W82_RCX_CONSTANT_200_10000_K_V1다.
명시적공통T·상대drift0Maxwellian,200≤T/K≤10000,H1s및W82의4He-Hscope,
자발단광자과정에서문헌상수근사1.70E-13cm³/s=1.70E-19m³/s를평가한다.
기존원코드의출력을그대로사용하며새fit,source자동기본값,새질량변환은없다.
상수모델의dk/dT=0을물리기울기측정으로표시하지않는다.

종(HI,HII,HeI,HeII,HeIII,e)의계수는(-1,+1,0,+1,-1,0)k다.
소비기에서곱할밀도쌍은HI×HeIII이며이코드는밀도·유체진화를계산하지않는다.
단광자반응의광자수계수는k,자유전자순증분은0이다.
photonspectrum/meanphotonenergy/heat/recoil/inverserate/sourceUQ는null이다.
같은반응의rate/countview나대안source를두번더하는bundle을거부한다.

GM25는KF96와한자릿수이상차이를보고한다.acknowledge_source_conflict=true는
이를인지했다는입력일뿐상충이해결됐다는뜻이나production승인이아니다.
본노드에서KF96원수치계수와Westσ재적분은확인/수행하지않았다.
West의광학손실은별도reference로등록하며그에실제thermalrate권위를주지않는다.

## 4. 코드·설치 변화

새배포명bass-he-atomic-export0.1.0,importbass_he_atomic_export.
원ratecore와writer는_private모듈로포함하고semantic/byteidentity를보존한다.
B2의bass-he-west82-reference0.2.0/importbass_he_west82는수정하지않는다.
새wheel둘의runtime파일교집합은없고legacybass_he_rcx패키지는포함하지않는다.
과거두bass_he_rcx배포물자체를고쳐서동시설치한것은아니다.

request11개필드를명시해야하며온도목록1–4096개,기본선택없음,알수없는필드거부다.
packet에는원source위치,선택된scope,codeidentity,fit/불확실성의미가함께들어간다.
validate_packet은selectedsupplier재생성비교다.물리증명·독립review·보안서명검증은아니다.
JSON중복키/비유한값/기존파일덮어쓰기/부정확한batch를거부하며유효batch만원자적create-only로저장한다.

## 5. 실제 검증

고유시험76개통과:45API와10CLI는실제실패를관측한후구현,21개는후속시험이다.
새기능source-suite와별도설치target에서각각76개를통과했다.반복을고유시험수에더하지않는다.
원core와출력비교는6개T×2단위×2quantity의24개dictparity이며모든필드가동일하다.
686원moment나기존743단면적,원60/49/43scientificsuite를재실행한것은아니다.

두로컬wheel을같은빈target에--no-index--no-deps로설치했다.실제import경로는모두그target내다.
NumPy/SciPy는호스트의기존설치를사용했다.원자rate-only모듈은표준라이브러리만필요하다.
동일process에서ratepacket을생성한뒤opticalmanufactured연산자한건(E/E0=1,l=0,Γ/E0=1e-18,
반경1,실수potential0)을호출하고ratepacket이변하지않는지검사했다.
그작은연산자는loss>0,physicalRCTnull을유지한다.새물리적He-Hσ를계산한것이아니다.

실패이력은보존했다.
- pytestasyncio자동로딩이Werror아래미설정eventloop경고로collection전에실패했다.
  동기시험에불필요한외부plugin자동로딩만꺼서재실행했고Werror는유지했다.
- CLItest의default_source오타를기존API의default_source_id로맞췄다.생산source를바꾸지않았다.
- 호스트sitecustomize가시작시NumPy를선로드해import독립성시험이실패했다.
  bareprocess에서도관측한후해당격리시험을-S로실행했다.공급코드의의존성변경은없다.

같은wheel/packet은봉인ZIP재현으로한번더검사하며최종결과는detachedARCHIVE_VALIDATION이소유한다.
고정밀새연산,새Fortranbuild,MPI,HPC성능측정,독립scientificreview는없다.
binary64/no-fast-math/no-reassociation/명시backend정책을보존했다.

## 6. 다음 과학작업과 NCP

다음단일node는EOR_B4_RCX_PRIMARY_COMPILATION_DISAGREEMENT_AUDIT다.
GM25가보고한KF96/AR85권고값차이의원coefficient·단위·전하상태·T영역·인용계보를회수해
수치적으로같은양을비교하는지판정한다.새packetwrapper를반복하는작업이아니다.
실제원숫자를찾으면별도sourceID로평가하고기존값을자동대체/합산하지않는다.
미회수라면모호함을유지하고접근실패를무한반복하지않는다.

지금NCP64는필요하지않다.원자자료조사·이경계의제품기능은여기서가능하다.
큰독립전자기저/E,R,b산란수렴/실제MPI·NUMA프로파일링시고정코드·입력·계약으로넘긴다.
actualrei_bianchiAPI통합시험은미수행이며Bianchi코드변경도없다.
원16DAGnode/requires와historicalgates를보존한다.
scientific_PROMOTE=HOLD,EOR_THEORY_GATE=NOT_SATISFIED,Eq55=NOT_RUN,
independent_review=NOT_RUN,production_default_change=NOT_AUTHORIZED.

## 7. 전달

보고서는봉인·원격쓰기전작성됐다.새archiveSHA/bytes,Gitcommit/tree,Drive/Dropbox/Library
objectID와성공여부는detachedDELIVERY_RECEIPT가확정한다.
공개Git은코드·시험·계약·수학·설명;privateZIP은부모archive와완전한입력/근거다.
새remote다운로드복원시험없이는RESTORE_VERIFIED를표시하지않는다.
